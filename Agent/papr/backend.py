"""Filesystem backend for the papr deep agent.

The per-user store is papr's single source of truth. Each persistent top-level
folder (papers, topics, skills, briefs) routes to its own StoreBackend namespace;
everything else (agent scratch: todos, offloaded tool results) stays ephemeral in
thread state. `/papers/` is the user's whole research workspace — papers AND notes
live there together, organized however they like (nested subfolders welcome).

Why a namespace *per folder*: CompositeBackend strips the matched route prefix
before delegating, so a single shared StoreBackend would map /papers/x.md and
/topics/x.md to the same key ("/x.md") and collide. Per-folder namespaces keep
them apart and make the store easy to browse: (user_id, "papr", folder).

Isolation is enforced by keying every namespace on `user_id` from run context
(`rt.context`), set server-side — never chosen by the client.
"""
from __future__ import annotations

from typing import Any, Callable

from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

# Persistent top-level folders, each isolated in its own store namespace.
# /papers/ holds both papers and notes (the user's research workspace).
PERSISTENT_FOLDERS: tuple[str, ...] = ("papers", "topics", "skills", "briefs")

# Used when no authenticated user is present (local `langgraph dev` runs).
_DEV_USER = "local-dev"


def _user_id(rt: Any) -> str:
    """Read `user_id` from run context, with a dev fallback."""
    context = getattr(rt, "context", None)
    if isinstance(context, dict):
        return context.get("user_id") or _DEV_USER
    return getattr(context, "user_id", None) or _DEV_USER


def _namespace_for(folder: str) -> Callable[[Any], tuple[str, ...]]:
    """Build a namespace factory for one folder: (user_id, "papr", folder)."""

    def factory(rt: Any) -> tuple[str, ...]:
        return (_user_id(rt), "papr", folder)

    return factory


def make_backend() -> CompositeBackend:
    """Composite filesystem: ephemeral by default, persistent per user + folder."""
    routes = {
        f"/{folder}/": StoreBackend(namespace=_namespace_for(folder))
        for folder in PERSISTENT_FOLDERS
    }
    return CompositeBackend(default=StateBackend(), routes=routes)
