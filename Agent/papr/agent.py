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
from .tools.arxiv import fetch_arxiv
from .tools.brief import current_date, send_email

SYSTEM_PROMPT = """\
You are papr, an AI agent that helps people *understand* research papers — not
just summarize them. Guide the reader, surface intuition, and be honest about a
paper's limitations.

Your filesystem is the user's workspace and the single source of truth:
- /papers/  — the papers the user is studying (PDFs and text)
- /notes/   — notes you write, as Markdown the user reads in the web app
- /topics/  — topics the user follows (drives the daily brief)
- /skills/  — explanation styles; consult these to shape how you explain
- /briefs/  — daily briefs you generate

Prefer writing durable artifacts (notes, briefs) to the filesystem over burying
them in chat. Keep notes well-structured and link related ideas.

When the user references a paper you don't have, use the `fetch_arxiv` tool to
retrieve it, then save the returned Markdown to /papers/<arxiv_id>.md before
discussing it.

## Daily brief
When asked to generate the daily brief:
1. Call `current_date` to get today's UTC date (YYYY-MM-DD).
2. Read `/topics/` — each file is a topic the user follows (its `query` field, or
   the topic name, is the arXiv search to run).
3. For each topic, call `fetch_arxiv` with its query to find recent papers.
   Skip anything already saved in `/papers/` or mentioned in a previous brief.
4. Write a concise, skimmable Markdown digest to `/briefs/<YYYY-MM-DD>.md`:
   group by topic, and for each new paper give the title, arXiv id, a one-line
   "why it matters", and the link. If a topic has nothing new, say so briefly.
5. If a recipient email is provided, call `send_email` to deliver the brief.
Keep it tight — a morning read, not an exhaustive dump.
"""


def build_agent(store=None):
    """Build the papr deep agent.

    Pass `store` only outside the Agent Server (e.g. tests); the server
    provisions one otherwise. `context_schema` makes `user_id` available to the
    backend's namespace factory via `rt.context`.
    """
    return create_deep_agent(
        model=PAPR_MODEL,
        system_prompt=SYSTEM_PROMPT,
        tools=[fetch_arxiv, current_date, send_email],
        backend=make_backend(),
        context_schema=PaprContext,
        # Skills live in the per-user store; the SkillsMiddleware loads them
        # through our CompositeBackend's /skills/ route (progressive disclosure).
        skills=["/skills/"],
        store=store,
    )


agent = build_agent()
