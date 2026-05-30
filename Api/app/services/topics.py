"""Topic service: CRUD over the user's /topics/ files.

Topics are Markdown files with `name`/`query` frontmatter; the agent reads them
directly to drive the daily brief.
"""
from __future__ import annotations

import re

from . import store
from .errors import Invalid

_SLUG = re.compile(r"[^a-z0-9]+")


def _slugify(name: str) -> str:
    return _SLUG.sub("-", name.strip().lower()).strip("-")[:64]


def _parse(content: str) -> dict[str, str]:
    """Pull `name`/`query` out of a topic file's YAML-ish frontmatter."""
    meta: dict[str, str] = {}
    if content.startswith("---"):
        _, _, rest = content.partition("\n")
        body, _, _ = rest.partition("\n---")
        for line in body.splitlines():
            key, sep, value = line.partition(":")
            if sep:
                meta[key.strip()] = value.strip()
    return meta


def _file(name: str, query: str) -> str:
    return f"---\nname: {name}\nquery: {query}\n---\n\nFollowing **{name}** — daily brief searches arXiv for: {query}\n"


async def list_topics(user_id: str) -> list[dict]:
    resp = await store.search(user_id, "topics")
    topics = []
    for item in resp.get("items", []):
        slug = item.get("key", "").strip("/").removesuffix(".md")
        value = item.get("value") or {}
        meta = _parse(value.get("content", ""))
        topics.append(
            {
                "slug": slug,
                "name": meta.get("name", slug),
                "query": meta.get("query", slug),
                "modified_at": value.get("modified_at"),
            }
        )
    topics.sort(key=lambda t: t["name"].lower())
    return topics


async def add_topic(user_id: str, name: str, query: str | None) -> dict:
    name = name.strip()
    if not name:
        raise Invalid("topic name required")
    slug = _slugify(name)
    if not slug:
        raise Invalid("topic name must contain letters or digits")
    query = (query or name).strip()
    await store.put(user_id, "topics", f"/{slug}.md", store.file_value(_file(name, query)))
    return {"slug": slug, "name": name, "query": query}


async def delete_topic(user_id: str, slug: str) -> str:
    await store.delete(user_id, "topics", f"/{slug}.md")
    return slug
