"""Generic file CRUD over the agent's per-user store.

Everything in papr is a file in the store, so this one service covers papers,
skills, briefs (specs + outputs) and memory. A full path is `/<folder>/<rest>`,
which maps to store namespace `(user_id, "papr", folder)` with key `/<rest>`.

The BFF writes to the store directly (bypassing the agent's filesystem
middleware), so the per-folder content policy (papers = .md/.pdf, else .md) is
enforced here too.
"""
from __future__ import annotations

import base64
import os
from datetime import datetime, timezone

from ..config import settings
from ..core.agent_client import agent_client
from .errors import Invalid, NotFound


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ns(user_id: str, folder: str) -> list[str]:
    return [user_id, "papr", folder]


def _ext(name: str) -> str:
    return os.path.splitext(name)[1].lower()


def _safe_name(filename: str) -> str:
    return filename.replace("\\", "/").split("/")[-1].strip() or "upload"


def _allowed_ext(folder: str) -> set[str]:
    return {".md", ".pdf"} if folder == "papers" else {".md"}


def _split_path(path: str) -> tuple[str, str]:
    """`/papers/a/b.md` -> ("papers", "/a/b.md")."""
    parts = ("/" + path.strip("/")).split("/", 2)
    folder = parts[1] if len(parts) > 1 else ""
    if not folder or folder not in settings.persistent_folders:
        raise Invalid(f"path must start with one of {list(settings.persistent_folders)}")
    key = "/" + (parts[2] if len(parts) > 2 else "")
    if key == "/":
        raise Invalid("path must point to a file, not a folder")
    return folder, key


async def _get_value(user_id: str, folder: str, key: str) -> dict:
    try:
        item = await agent_client().store.get_item(_ns(user_id, folder), key=key)
    except Exception:  # noqa: BLE001 - missing item surfaces as 404 from the store
        raise NotFound(f"no file at /{folder}{key}")
    value = (item or {}).get("value")
    if value is None:
        raise NotFound(f"no file at /{folder}{key}")
    return value


# --- tree -----------------------------------------------------------------

async def tree(user_id: str) -> list[dict]:
    """Nested file tree across all persistent folders (folders first, then files)."""
    root: dict = {}
    client = agent_client()
    for folder in settings.persistent_folders:
        result = await client.store.search_items(_ns(user_id, folder), limit=1000)
        for item in result["items"]:
            key = item["key"]
            key = key if key.startswith("/") else "/" + key
            _insert(root, f"/{folder}{key}".strip("/").split("/"))
    return _to_nodes(root, "")


def _insert(node: dict, parts: list[str]) -> None:
    if not parts:
        return
    head, *rest = parts
    _insert(node.setdefault(head, {}), rest)


def _to_nodes(node: dict, prefix: str) -> list[dict]:
    # Folders (non-empty dict) before files; each group alphabetical.
    names = sorted(node, key=lambda n: (not node[n], n.lower()))
    out: list[dict] = []
    for name in names:
        path = f"{prefix}/{name}"
        children = node[name]
        if children:
            out.append(
                {"name": name, "path": path, "type": "folder", "children": _to_nodes(children, path)}
            )
        else:
            out.append({"name": name, "path": path, "type": "file"})
    return out


# --- read / write / delete ------------------------------------------------

async def read(user_id: str, path: str) -> dict:
    folder, key = _split_path(path)
    value = await _get_value(user_id, folder, key)
    return {
        "path": path,
        "content": value.get("content", ""),
        "encoding": value.get("encoding", "utf-8"),
        "modified_at": value.get("modified_at"),
    }


async def raw_bytes(user_id: str, path: str) -> tuple[bytes, str]:
    folder, key = _split_path(path)
    value = await _get_value(user_id, folder, key)
    content = value.get("content", "")
    if value.get("encoding") == "base64":
        data = base64.b64decode(content)
    else:
        data = content.encode("utf-8")
    media = "application/pdf" if path.lower().endswith(".pdf") else "text/plain; charset=utf-8"
    return data, media


async def write(user_id: str, path: str, content: str, encoding: str = "utf-8") -> dict:
    folder, key = _split_path(path)
    ext = _ext(key)
    if ext not in _allowed_ext(folder):
        raise Invalid(f"/{folder}/ allows {sorted(_allowed_ext(folder))}, got '{ext or '(none)'}'")
    if encoding not in ("utf-8", "base64"):
        raise Invalid("encoding must be 'utf-8' or 'base64'")

    created = _now()
    try:  # preserve created_at on overwrite
        existing = await agent_client().store.get_item(_ns(user_id, folder), key=key)
        if existing and existing.get("value"):
            created = existing["value"].get("created_at", created)
    except Exception:  # noqa: BLE001 - new file
        pass

    value = {"content": content, "encoding": encoding, "created_at": created, "modified_at": _now()}
    await agent_client().store.put_item(_ns(user_id, folder), key=key, value=value)
    return {"path": path, "encoding": encoding, "modified_at": value["modified_at"]}


async def delete(user_id: str, path: str) -> None:
    folder, key = _split_path(path)
    await agent_client().store.delete_item(_ns(user_id, folder), key=key)


async def upload(user_id: str, filename: str, data: bytes) -> dict:
    """Store an uploaded .md/.pdf under /papers/."""
    ext = _ext(filename)
    if ext not in {".md", ".pdf"}:
        raise Invalid("only .md and .pdf uploads are allowed")
    if ext == ".pdf":
        content, encoding = base64.b64encode(data).decode("ascii"), "base64"
    else:
        content, encoding = data.decode("utf-8"), "utf-8"
    return await write(user_id, f"/papers/{_safe_name(filename)}", content, encoding)
