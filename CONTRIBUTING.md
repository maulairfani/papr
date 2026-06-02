# Contributing to papr

Thanks for your interest in papr! This guide covers how to set up a dev
environment, the conventions we follow, and how to propose changes.

By contributing, you agree that your contributions are licensed under the
project's [AGPL-3.0](LICENSE) license.

## Development setup

See the [Quickstart](README.md#quickstart) in the README. In short:

```bash
echo "OPENAI_API_KEY=sk-..." > Agent/.env
docker compose up -d          # agent (:2024) + BFF (:8000)
cd Web && npm install && npm run dev   # web (:5173)
```

The three services:

- **`Agent/`** — Python, [deepagents](https://github.com/langchain-ai/deepagents) on the LangGraph dev server. Runs in Docker; edit and it hot-reloads (restart the container to pick up new tools/middleware).
- **`Api/`** — Python, FastAPI. Runs in Docker with `--reload`.
- **`Web/`** — TypeScript, React + Vite. Run locally with `npm run dev`.

## Conventions

- **Language:** code, comments, and docs in **English**. Comments explain _why_, not _what_.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/) — e.g.
  `feat(agent): add move_file tool`, `fix(web): wrap long tool args`, `docs: ...`.
- **Branches:** short, descriptive (`feat/briefs-ui`, `fix/chat-overflow`).
- **Scope:** keep PRs focused; one logical change per PR.

## Code style

- **Python:** type hints, `from __future__ import annotations`, small focused
  modules (routers → services → core in the BFF). Keep secrets out of code.
- **TypeScript:** `strict` mode; prefer small single-responsibility modules
  (`api/`, `hooks/`, `workspace/`, and one component per file).

## Before you open a PR

Make sure the relevant service still builds:

```bash
# Web
cd Web && npm run build        # tsc + vite build

# Api / Agent (import check)
docker compose exec api python -c "import app.main"
docker compose exec agent python -c "from papr.agent import agent"
```

## Pull requests

1. Fork and create a branch.
2. Make your change with a clear commit history.
3. Open a PR describing **what** and **why**; link any related issue.
4. CI must pass and at least one maintainer review is required.

## Reporting bugs / requesting features

Use the issue templates. For security vulnerabilities, please **do not** open a
public issue — report it privately to the maintainer instead.
