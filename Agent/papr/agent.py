"""Assembles the papr deep agent graph.

`build_agent()` is the single factory; `agent` is the instance referenced by
`langgraph.json`. In production the store and checkpointer are left unset so the
Agent Server (and `langgraph dev`) provision them at runtime — locally in memory,
in production a real backing store. Tests pass an explicit in-memory store.
"""
from __future__ import annotations

from deepagents import create_deep_agent

from .backend import make_backend
from .config import PAPR_MODEL
from .context import PaprContext
from .middleware import PapersFileTypeMiddleware
from .prompts import SYSTEM_PROMPT
from .tools.arxiv import download_arxiv, search_arxiv
from .tools.brief import current_date


def build_agent(store=None):
    """Build the papr deep agent.

    Pass `store` only outside the Agent Server (e.g. tests); the server
    provisions one otherwise. `context_schema` makes `user_id` available to the
    backend's namespace factory via `rt.context`.
    """
    return create_deep_agent(
        model=PAPR_MODEL,
        system_prompt=SYSTEM_PROMPT,
        tools=[search_arxiv, download_arxiv, current_date],
        backend=make_backend(),
        context_schema=PaprContext,
        # Enforce the /papers/ workspace rule (only .md and .pdf) on papr's writes.
        middleware=[PapersFileTypeMiddleware()],
        # Skills live in the per-user store; the SkillsMiddleware loads them
        # through our CompositeBackend's /skills/ route (progressive disclosure).
        skills=["/skills/"],
        store=store,
    )


agent = build_agent()
