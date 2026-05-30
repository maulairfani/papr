"""arXiv fetch tool.

A built-in tool (the MVP stand-in for an arXiv MCP source — see Docs/ROADMAP.md).
It only *fetches*; papr decides to persist the result to /papers/ using its own
filesystem tools. Keeping it fetch-only means the tool needs no store access and
swapping it for an MCP-sourced tool later is a drop-in change.
"""
from __future__ import annotations

import re

import arxiv
from langchain_core.tools import tool

# Matches a bare arXiv id like "1706.03762" or "2310.06825v2".
_ARXIV_ID = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")

# arXiv's export API throttles aggressively (HTTP 503); space requests out and
# retry rather than failing on the first transient error.
_client = arxiv.Client(page_size=10, delay_seconds=3.0, num_retries=5)


@tool
def fetch_arxiv(query: str, max_results: int = 1) -> str:
    """Fetch paper metadata and abstract from arXiv.

    `query` may be an arXiv id (e.g. "1706.03762") or a free-text search
    (e.g. "attention is all you need"). Returns Markdown with title, authors,
    abstract, categories, and links. To keep a paper, save the returned Markdown
    to /papers/<arxiv_id>.md before discussing it.
    """
    q = query.strip()
    search = (
        arxiv.Search(id_list=[q], max_results=max_results)
        if _ARXIV_ID.match(q)
        else arxiv.Search(query=q, max_results=max_results)
    )

    # Return a message instead of raising, so an upstream hiccup doesn't crash
    # the run — papr can relay it and the user can retry.
    try:
        results = list(_client.results(search))
    except arxiv.HTTPError as e:
        status = getattr(e, "status", "?")
        return (
            f"arXiv is temporarily unavailable (HTTP {status}) for query '{query}'. "
            "This is usually rate limiting or a brief outage — wait a moment and try again."
        )
    except Exception as e:  # noqa: BLE001 - upstream/library errors shouldn't break the agent
        return f"arXiv fetch failed for '{query}': {e}"

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
            f"- PDF: {r.pdf_url}\n\n"
            f"## Abstract\n\n{r.summary.strip()}\n"
        )
    return "\n\n---\n\n".join(blocks)
