"""Data-access helpers over the per-user LangGraph store.

Every persistent file lives under the namespace (user_id, "papr", <folder>). These
helpers centralize that shape and the deepagents `FileData` envelope so the
higher-level services never construct namespaces or value dicts by hand.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..core.agent_client import client


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ns(user_id: str, folder: str) -> list[str]:
    return [user_id, "papr", folder]


def file_value(content: str, encoding: str = "utf-8") -> dict[str, Any]:
    """Wrap text/binary in the deepagents FileData shape the agent expects."""
    now = now_iso()
    return {"content": content, "encoding": encoding, "created_at": now, "modified_at": now}


async def search(user_id: str, folder: str, limit: int = 200) -> dict:
    return await client.store.search_items(_ns(user_id, folder), limit=limit)


async def get(user_id: str, folder: str, key: str) -> dict | None:
    return await client.store.get_item(_ns(user_id, folder), key=key)


async def put(user_id: str, folder: str, key: str, value: dict[str, Any]) -> None:
    await client.store.put_item(_ns(user_id, folder), key=key, value=value)


async def delete(user_id: str, folder: str, key: str) -> None:
    await client.store.delete_item(_ns(user_id, folder), key=key)
