# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Conventions

- **Language:** Always respond, write code, and write code comments in **English**.
- Keep comments focused on *why*, not *what*, and match the surrounding code's style.

## What is papr

**papr** is an open-source AI agent that helps users *understand* research papers — not just
summarize them, but guide, take notes, and track topics the user is following over time.

**Status:** In development. Steps 0–6 done — agent + per-user store; the web stack (React SPA,
FastAPI BFF, agent) in Docker with auth → chat → files and per-user isolation; paper ingestion
(upload plus a built-in arXiv fetch tool); store-backed, user-creatable skills (native
progressive disclosure); topics + a native-cron **daily brief** (subscribe creates a per-user
cron carrying `user_id` in run context; "generate now" fires the same trigger immediately);
and a dedicated **MCP server** (FastMCP) exposing each user's store to external clients via a
per-user PAT. The FastAPI BFF is structured domain-modular (`routers/` thin adapters →
`services/` business logic + store access → `core/` auth/client). Only deploy (Step 7) remains.
All verified end-to-end. See `Docs/ROADMAP.md`.

## Architecture mental model

The **per-user store is the single source of truth.** Every other component is just a "head"
that reads/writes the same files — papers, notes, topics, briefs, AND skills are all files in
the store, so they show up in the web UI, are readable by the agent, and are exposed over MCP
with no extra logic.

```text
              STORAGE (per-user, LangGraph Store)
              papers/  notes/  topics/  skills/  briefs/
                          |
   papr agent  --  React + FastAPI  --  MCP server  --  Cron jobs
   (deepagents)   (web UI / BFF)       (external)       (daily brief)
```

## Planned components

- **Agent (`papr`)** — LangChain `deepagents` (`create_deep_agent`: planning/todos, subagents,
  filesystem tools, skills). Use a **CompositeBackend**: default `StateBackend` for ephemeral
  scratch (todos, offloaded tool results) + `StoreBackend` routes for persistent paths
  (`/papers/`, `/notes/`, `/topics/`, `/skills/`, `/briefs/`). A **`namespace` factory keyed on
  `user_id` from run context (`rt.context`, deepagents >= 0.5.2)** isolates each user's files — FastAPI injects it for web runs, the
  assistant/cron config carries it for scheduled runs. `read_file` reads PDFs natively
  (deepagents >= 0.5.0), so papr reads uploaded papers without a separate parser.
- **Storage** — a LangGraph `BaseStore` (Postgres/Redis; auto-provisioned on LangSmith
  Deployment). Stores binary files (PDFs). Do NOT use `FilesystemBackend`/`LocalShellBackend`
  in a deployed agent — they touch the host directly.
- **Skills — live in the user's store, user-creatable.** Skills follow the Agent Skills standard
  (a directory per skill with a `SKILL.md`: frontmatter + instructions, optional resources) and
  use progressive disclosure (agent reads frontmatter at run startup, loads full content on
  demand). They live under `/skills/` in the per-user store, so users (and papr itself) create
  and edit them via the web UI; new/edited skills are picked up on the next run. papr ships a few
  starter skills (Feynman/ELI5, structured summary, methodology breakdown, analogies, critique),
  seeded into a new user's `/skills/` on first login.
  *(Confirmed: `skills=["/skills/"]` loads per-user skills through the StoreBackend route — the
  SkillsMiddleware reads via backend APIs and `create_deep_agent` passes it our CompositeBackend.)*
- **Web app — React SPA + FastAPI backend-for-frontend (BFF).** React: chat, file browser, notes
  viewer, topics page, skills editor. FastAPI: authenticates the user → `user_id`; proxies/streams
  runs to the Agent Server, **injecting `configurable.user_id` server-side** (clients can't spoof
  it → secure per-user isolation); serves Store reads (file browser) scoped to the user; handles
  uploads; manages cron lifecycle; mints MCP tokens.
- **MCP server (`Mcp/`, FastMCP)** — exposes the user's store to external MCP clients (Claude
  Desktop, Cursor) over streamable HTTP. Same per-user namespace. Auth: per-user bearer token
  (PAT) for MVP; OAuth 2.1 later. *(Resolved: the Agent Server's built-in `/mcp` exposes only the
  papr assistant as an "invoke the agent" tool — no `resources/list`, unauthenticated — so it
  cannot browse files. We run a dedicated FastMCP server: `JWTVerifier` validates the HS256 PAT
  with the shared secret; the token's `sub` scopes every store read; tools `list_files`/`read_file`.
  The API mints the PAT at `POST /mcp/token` carrying `aud`/`iss`, so a web session token isn't
  accepted on the MCP surface.)*
- **Cron / scheduler** — daily brief on followed topics (native LangGraph crons; see Decided).
  *(Resolved: a cron created with `context={"user_id": ...}` carries that into `rt.context`, so the
  namespace factory isolates scheduled runs to the right store — verified.)*

## Paper sources

- **User upload** → stored under `/papers/`.
- **Agent-fetched** → papr acts as an MCP *client* to external sources (arXiv, Hugging Face).
  arXiv is public (no auth); Hugging Face may need a token (app-level for MVP).

## Auth has three distinct surfaces

1. **Web user <-> agent** — managed auth via FastAPI → `user_id` injected into run config → namespace.
2. **External MCP client <-> papr MCP server** — per-user bearer token for MVP, OAuth 2.1 later.
3. **papr <-> upstream paper MCPs** — app-level/anonymous tokens (arXiv none, HF optional).

## Decided

- **No execution sandbox** — storage-only backend.
- **Stack: React SPA + FastAPI BFF + one LangSmith Deployment (Agent Server)** as the shared
  runtime — hosts the agent, auto-provisions the Store, runs cron jobs, exposes MCP endpoints.
- **Containerized from the start** — each service (`Agent/`, `Api/`, `Web/`) ships a dev
  `Dockerfile`; a root `docker-compose.yml` runs the local stack.
- **Skills live in the per-user store under `/skills/` and are user-creatable** (Agent Skills standard).
- **Daily brief = native LangGraph cron jobs** (`client.crons.create`). Per-user scheduling via a
  per-user assistant (configured instance carrying `user_id`) + a cron created on subscribe and
  deleted on unsubscribe. The `namespace` factory reads `user_id` from run config so interactive
  AND cron runs isolate to the right store.
  - Cron `input` is STATIC → "what's new" logic lives in the agent; it reads `/topics/`, fetches
    new papers, and writes the brief to `/briefs/YYYY-MM-DD.md` (shows in web UI + MCP). Delivery
    (email) is a tool the agent calls.
  - Schedules are UTC (convert per-user local time, e.g. WIB). Delete unused crons — each run bills the LLM.

## Still open (don't re-litigate without revisiting)

1. **Paper source for daily brief** — MVP ships **arXiv only** (reuses `fetch_arxiv`). Multi-source
   (Semantic Scholar/OpenAlex) is a later enhancement, not blocking.
2. **Auth specifics** — MVP MCP auth is a **per-user PAT** (HS256 JWT with `aud=papr-mcp`/`iss=papr`,
   minted at `POST /mcp/token`, shared `PAPR_JWT_SECRET` between api+mcp); OAuth 2.1 later. Web auth
   is still the dev JWT — pick a real provider at deploy (Step 7).
3. **Email delivery for the brief** — `send_email` is a best-effort SMTP tool; sends only when
   `SMTP_*` env is set, otherwise reports "not configured" (the `/briefs/` file is the real artifact).
   Pick a provider/credentials at deploy.

*(Resolved during build: `skills=` resolves through the StoreBackend; a cron carries `user_id` via
`context=`; the built-in `/mcp` can't browse files so we run a dedicated FastMCP server.)*

## Suggested build order (de-risk heavy parts last)

Core agent + store → React/FastAPI chat + file browser → upload + arXiv fetch → skills (store-backed)
→ topics + cron brief → MCP server → deploy. See `Docs/ROADMAP.md` for the detailed plan.
