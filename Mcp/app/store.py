"""Read-only, user-scoped access to the papr store.

Mirrors the API's store namespace shape (user_id, "papr", <folder>) but exposes
only reads — external MCP clients browse the user's files, they don't mutate them.
"""
from __future__ import annotations

from langgraph_sdk import get_client

from . import config

_store = get_client(url=config.AGENT_URL).store


def _ns(user_id: str, folder: str) -> list[str]:
    return [user_id, "papr", folder]


async def list_files(user_id: str, folder: str | None = None) -> list[dict]:
    folders = [folder] if folder else list(config.PERSISTENT_FOLDERS)
    out: list[dict] = []
    for f in folders:
        if f not in config.PERSISTENT_FOLDERS:
            raise ValueError(f"unknown folder: {f}")
        resp = await _store.search_items(_ns(user_id, f), limit=200)
        for item in resp.get("items", []):
            value = item.get("value") or {}
            out.append(
                {"path": f"/{f}{item.get('key', '')}", "modified_at": value.get("modified_at")}
            )
    return out


async def read_file(user_id: str, path: str) -> str:
    trimmed = path.strip("/")
    if "/" not in trimmed:
        raise ValueError("path must be /<folder>/<file>")
    folder, rest = trimmed.split("/", 1)
    if folder not in config.PERSISTENT_FOLDERS:
        raise ValueError(f"unknown folder: {folder}")
    item = await _store.get_item(_ns(user_id, folder), key=f"/{rest}")
    if not item:
        raise ValueError("file not found")
    return (item.get("value") or {}).get("content", "")
