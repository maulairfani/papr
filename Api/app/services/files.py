"""File-browser service: list and read the user's files from the store."""
from __future__ import annotations

from .. import config
from . import store
from .errors import Invalid, NotFound


async def list_files(user_id: str) -> list[dict]:
    files: list[dict] = []
    for folder in config.PERSISTENT_FOLDERS:
        resp = await store.search(user_id, folder)
        for item in resp.get("items", []):
            value = item.get("value") or {}
            files.append(
                {
                    "path": f"/{folder}{item.get('key', '')}",
                    "modified_at": value.get("modified_at"),
                }
            )
    return files


async def read_file(user_id: str, path: str) -> str:
    trimmed = path.strip("/")
    if "/" not in trimmed:
        raise Invalid("path must be /<folder>/<file>")
    folder, rest = trimmed.split("/", 1)
    if folder not in config.PERSISTENT_FOLDERS:
        raise NotFound("unknown folder")
    item = await store.get(user_id, folder, f"/{rest}")
    if not item:
        raise NotFound("file not found")
    return (item.get("value") or {}).get("content", "")
