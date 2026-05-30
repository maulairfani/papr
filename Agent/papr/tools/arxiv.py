"""arXiv tools: search and download.

Two separate tools, by design:
- `search_arxiv` only *finds* papers and returns their metadata for papr to
  present. It never saves anything — saving waits for the user's say-so.
- `download_arxiv` saves a paper's PDF into the user's /papers/ workspace. papr
  should call it only when the user asks to download/save a paper.
"""
from __future__ import annotations

import base64
import re
from datetime import datetime, timezone

import arxiv
import httpx
from langchain_core.tools import tool
from langgraph.runtime import get_runtime

from ..backend import _user_id

# Matches a bare new-style arXiv id like "1706.03762" or "2310.06825v2".
_ARXIV_ID = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")

# arXiv's export API throttles aggressively (HTTP 503); space requests out and
# retry rather than failing on the first transient error.
_client = arxiv.Client(page_size=10, delay_seconds=3.0, num_retries=5)

_UA = "papr/0.1 (research understanding assistant)"


def _clean_arxiv_id(raw: str) -> str:
    """Normalize an id or arXiv URL to a bare id (e.g. '1706.03762v2')."""
    s = raw.strip()
    s = re.sub(r"(?i)^arxiv:", "", s)
    if "/" in s:  # a URL like https://arxiv.org/abs/1706.03762
        s = s.rstrip("/").split("/")[-1]
    s = re.sub(r"(?i)\.pdf$", "", s)
    return s.strip()


@tool
def search_arxiv(query: str, max_results: int = 5) -> str:
    """Search arXiv and return matching papers (title, id, authors, abstract, links).

    `query` may be free text (e.g. "attention is all you need") or an arXiv id
    (e.g. "1706.03762"). This only searches — it does NOT save anything. Present
    the results to the user; download a paper only if they ask.
    """
    q = query.strip()
    search = (
        arxiv.Search(id_list=[_clean_arxiv_id(q)], max_results=max_results)
        if _ARXIV_ID.match(_clean_arxiv_id(q))
        else arxiv.Search(query=q, max_results=max_results)
    )

    # Return a message instead of raising, so an upstream hiccup doesn't crash the run.
    try:
        results = list(_client.results(search))
    except arxiv.HTTPError as e:
        status = getattr(e, "status", "?")
        return (
            f"arXiv is temporarily unavailable (HTTP {status}) for query '{query}'. "
            "This is usually rate limiting or a brief outage — wait a moment and try again."
        )
    except Exception as e:  # noqa: BLE001 - upstream/library errors shouldn't break the agent
        return f"arXiv search failed for '{query}': {e}"

    if not results:
        return f"No arXiv results for: {query}"

    blocks = []
    for r in results:
        authors = ", ".join(a.name for a in r.authors)
        blocks.append(
            f"# {r.title}\n\n"
            f"- arXiv: {r.get_short_id()}\n"
            f"- Authors: {authors}\n"
            f"- Published: {r.published.date()}\n"
            f"- Categories: {', '.join(r.categories)}\n"
            f"- Abstract page: {r.entry_id}\n\n"
            f"## Abstract\n\n{r.summary.strip()}\n"
        )
    return "\n\n---\n\n".join(blocks)


@tool
async def download_arxiv(arxiv_id: str) -> str:
    """Download an arXiv paper's PDF into the user's /papers/ workspace.

    Use ONLY when the user asks to save/download a paper. `arxiv_id` is the id
    (e.g. "1706.03762" or "2310.06825v2"); an arXiv URL is accepted too. Saves to
    /papers/<id>.pdf, which the user can then open and you can read.
    """
    aid = _clean_arxiv_id(arxiv_id)
    if not aid:
        return f"'{arxiv_id}' is not a usable arXiv id."

    rt = get_runtime()
    store = getattr(rt, "store", None)
    if store is None:
        return "No store is available to save the paper."
    user_id = _user_id(rt)

    url = f"https://arxiv.org/pdf/{aid}.pdf"
    try:
        async with httpx.AsyncClient(
            timeout=60.0, follow_redirects=True, headers={"User-Agent": _UA}
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except Exception as e:  # noqa: BLE001 - network/library errors shouldn't break the run
        return f"Failed to download arXiv {aid}: {e}"

    if "pdf" not in resp.headers.get("content-type", "").lower():
        return f"arXiv {aid} did not return a PDF — double-check the id."

    data = resp.content
    now = datetime.now(timezone.utc).isoformat()
    await store.aput(
        (user_id, "papr", "papers"),
        f"/{aid}.pdf",
        {"content": base64.b64encode(data).decode("ascii"), "encoding": "base64",
         "created_at": now, "modified_at": now},
    )
    return f"Saved arXiv {aid} to /papers/{aid}.pdf ({len(data) // 1024} KB). You can open it from /papers/ and I can read it."
