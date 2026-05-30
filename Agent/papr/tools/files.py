"""Filesystem tools beyond what deepagents ships.

deepagents provides ls/read_file/write_file/edit_file/glob/grep but no delete or
move/rename, so papr can't reorganize files on its own. These tools fill that gap
by operating straight on the per-user store (the same store the filesystem tools
are backed by).
"""
from __future__ import annotations

from typing import Any

from langchain_core.tools import tool
from langgraph.runtime import get_runtime


def _store_and_user(rt: Any):
    # Lazy import: papr.agent imports this module, so a top-level import would
    # create a cycle. By call time the agent module is fully loaded.
    from ..agent import _user_id

    return getattr(rt, "store", None), _user_id(rt)


def _split(path: str) -> tuple[str, str]:
    """`/papers/a/b.md` -> ("papers", "/a/b.md"). Raises ValueError on a bad path."""
    from ..agent import PERSISTENT_FOLDERS

    parts = ("/" + path.strip("/")).split("/", 2)
    folder = parts[1] if len(parts) > 1 else ""
    if folder not in PERSISTENT_FOLDERS:
        raise ValueError(f"path must be under {list(PERSISTENT_FOLDERS)} — got '{path}'")
    key = "/" + (parts[2] if len(parts) > 2 else "")
    if key == "/":
        raise ValueError(f"'{path}' points to a folder, not a file")
    return folder, key


@tool
async def delete_file(file_path: str) -> str:
    """Delete a file from the user's workspace. This cannot be undone.

    `file_path` is an absolute path like `/papers/old.md` or
    `/briefs/specs/diffusion.md`. Use it to remove a paper, note, brief, spec, or
    skill the user no longer wants. Only delete when the user clearly asks to.
    """
    rt = get_runtime()
    store, user_id = _store_and_user(rt)
    if store is None:
        return "No store is available to delete the file."
    try:
        folder, key = _split(file_path)
    except ValueError as e:
        return str(e)

    namespace = (user_id, "papr", folder)
    if await store.aget(namespace, key) is None:
        return f"No file at {file_path}."
    await store.adelete(namespace, key)
    return f"Deleted {file_path}."


@tool
async def move_file(source: str, destination: str) -> str:
    """Move or rename a file in the user's workspace.

    Both are absolute paths, e.g. rename `/papers/old.md` -> `/papers/new.md`, or
    move `/papers/x.md` -> `/papers/archive/x.md`. The file's contents are kept; an
    existing file at `destination` is overwritten.
    """
    rt = get_runtime()
    store, user_id = _store_and_user(rt)
    if store is None:
        return "No store is available to move the file."
    try:
        src_folder, src_key = _split(source)
        dst_folder, dst_key = _split(destination)
    except ValueError as e:
        return str(e)
    if (src_folder, src_key) == (dst_folder, dst_key):
        return "Source and destination are the same."

    item = await store.aget((user_id, "papr", src_folder), src_key)
    if item is None:
        return f"No file at {source}."
    await store.aput((user_id, "papr", dst_folder), dst_key, item.value)
    await store.adelete((user_id, "papr", src_folder), src_key)
    return f"Moved {source} -> {destination}."
