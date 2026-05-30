"""Assembles the papr deep agent graph (and its filesystem backend).

`build_agent()` is the single factory; `agent` is the instance referenced by
`langgraph.json`. In production the store and checkpointer are left unset so the
Agent Server (and `langgraph dev`) provision them at runtime — locally in memory,
in production a real backing store. Tests pass an explicit in-memory store.

## Filesystem backend

The per-user store is papr's single source of truth. Each persistent top-level
folder (papers, topics, skills, briefs, memories) routes to its own StoreBackend
namespace; everything else (agent scratch: todos, offloaded tool results) stays
ephemeral in thread state. `/papers/` is the user's whole research workspace —
papers AND notes live there together, organized however they like (nested
subfolders welcome). `/memories/AGENTS.md` is papr's always-loaded, per-user
profile of the reader (deepagents `memory=`), which papr updates as it learns.

Why a namespace *per folder*: CompositeBackend strips the matched route prefix
before delegating, so a single shared StoreBackend would map /papers/x.md and
/topics/x.md to the same key ("/x.md") and collide. Per-folder namespaces keep
them apart and make the store easy to browse: (user_id, "papr", folder).

Isolation is enforced by keying every namespace on `user_id` from run context
(`rt.context`), set server-side — never chosen by the client.
"""
from __future__ import annotations

from typing import Any, Callable

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

from .config import PAPR_MODEL
from .context import PaprContext
from .middleware import PapersFileTypeMiddleware, inject_current_date
from .prompts import SYSTEM_PROMPT
from .tools.arxiv import download_arxiv, search_arxiv

# Persistent top-level folders, each isolated in its own store namespace.
# /papers/ holds both papers and notes (the user's research workspace);
# /memories/ holds papr's per-user AGENTS.md profile (loaded every run).
PERSISTENT_FOLDERS: tuple[str, ...] = ("papers", "topics", "skills", "briefs", "memories")

# Used when no authenticated user is present (local `langgraph dev` runs).
_DEV_USER = "local-dev"


def _user_id(rt: Any) -> str:
    """Read `user_id` from run context, with a dev fallback.

    Imported lazily by `tools/arxiv.py` (which writes PDFs straight to the store)
    to avoid an import cycle with this module.
    """
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


def build_agent(store=None):
    """Build the papr deep agent.

    Pass `store` only outside the Agent Server (e.g. tests); the server
    provisions one otherwise. `context_schema` makes `user_id` available to the
    backend's namespace factory via `rt.context`.
    """
    return create_deep_agent(
        model=PAPR_MODEL,
        system_prompt=SYSTEM_PROMPT,
        tools=[search_arxiv, download_arxiv],
        backend=make_backend(),
        context_schema=PaprContext,
        # Enforce the /papers/ workspace rule (.md/.pdf only); inject today's date
        # into the system prompt so papr knows "today" without a tool round-trip.
        middleware=[PapersFileTypeMiddleware(), inject_current_date],
        # Skills live in the per-user store; the SkillsMiddleware loads them
        # through our CompositeBackend's /skills/ route (progressive disclosure).
        skills=["/skills/"],
        # Per-user memory: an always-loaded AGENTS.md profile of the reader,
        # routed to the persistent /memories/ namespace. Read-write by default,
        # so papr updates it (via edit_file) as it learns about the user.
        memory=["/memories/AGENTS.md"],
        store=store,
    )


agent = build_agent()
