# papr

> An open-source AI agent that helps you **understand** research papers — not just summarize them.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-in%20development-orange.svg)](#status)

papr reads papers _with_ you: it explains intuition, takes durable notes, fetches
related work from arXiv, and tracks the topics you follow over time with a daily
brief. Everything papr knows — papers, notes, skills, briefs, and its memory of
you — lives as plain files in **your** per-user store, so it shows up in the web
app, is readable by the agent, and is exposed over MCP with no extra glue.

## Why papr

Most "chat with your PDF" tools summarize and forget. papr is built around a
different idea: a persistent, per-user **workspace** that the agent and the UI
share. That makes papr good at the things summarizers aren't — building up notes
on a paper, remembering your background so explanations meet you at your level,
and following a research area across weeks.

## Architecture

The **per-user store is the single source of truth.** Every other component is a
"head" that reads/writes the same files.

```text
                 STORAGE  (per-user, LangGraph Store)
                 papers/  skills/  briefs/  memories/
                              |
   papr agent  --  React SPA + FastAPI BFF  --  MCP server  --  Cron
   (deepagents)        (web UI / API)          (external)    (daily brief)
```

| Component | Path | What it is |
| --- | --- | --- |
| **Agent** | [`Agent/`](Agent/) | A LangChain [deepagents](https://github.com/langchain-ai/deepagents) agent: planning, filesystem tools, skills, and a per-user `StoreBackend`. Tools: arXiv search/download, file delete/move, injected current date. |
| **BFF** | [`Api/`](Api/) | A **stateless** FastAPI backend-for-frontend over the agent's store: file CRUD, chat SSE (streams the agent's activity + tokens), brief cron, first-login seeding. No database of its own. |
| **Web** | [`Web/`](Web/) | A React + Vite + Tailwind SPA: a three-pane workspace (file explorer / editor for PDF & Markdown / chat with a live activity trace). |
| **MCP** | _planned_ | A dedicated FastMCP server exposing each user's store to external clients (Claude Desktop, Cursor) via a per-user token. Shelved during the rebuild. |

Per-user isolation is enforced server-side: the BFF authenticates the user to a
`user_id` and injects it into every agent run and store access — clients never
choose it.

## Quickstart

**Prerequisites:** Docker + Docker Compose, Node 20+, and an OpenAI API key.

```bash
# 1. Agent secrets (gitignored)
echo "OPENAI_API_KEY=sk-..." > Agent/.env

# 2. Start the agent + BFF (LangGraph server on :2024, API on :8000)
docker compose up -d

# 3. Start the web app
cd Web && npm install && npm run dev
```

Open **http://localhost:5173**. The dev build auto-logs-in a local user and seeds
starter skills + a memory profile on first login.

> If host port `8000` is taken, set `PAPR_API_PORT` in a root `.env` and point the
> web app at it with `VITE_API_URL` in `Web/.env.local`.

## Project structure

```text
Agent/   deepagents agent — tools, skills, per-user store backend
Api/     FastAPI BFF (stateless) + seed-skills/ + seed-memory/ (starter content)
Web/     React SPA (Vite + Tailwind) — sidebar / editor / chat
Docs/    design notes & roadmap
```

## Status

**In development.** The agent, BFF, and web app are wired end-to-end; remaining
work includes in-editor save, uploads, a briefs UI, and bringing the MCP server
back.

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0) — see
[LICENSE](LICENSE). In short: you may use, modify, and distribute papr, but if you
run a modified version as a network service, you must offer its users the source.
