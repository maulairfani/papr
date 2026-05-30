# papr

An open-source AI agent that helps you *understand* research papers — guiding you
through them, taking notes, and tracking topics you follow over time.

> Status: early development. See [Docs/ROADMAP.md](Docs/ROADMAP.md) for the plan
> and [CLAUDE.md](CLAUDE.md) for the architecture.

## Structure

| Path | What |
| --- | --- |
| `Agent/` | The papr deep agent (Python, `deepagents`) — runs on the LangGraph Agent Server. |
| `Api/` | FastAPI backend-for-frontend bridging the web app and the agent. |
| `Web/` | React + Vite single-page app. |
| `Skills/` | Starter explanation skills (Agent Skills standard). |
| `Docs/` | Project docs, including the roadmap. |

## Local development

Everything is containerized:

```bash
cp Agent/.env.example Agent/.env   # add your OPENAI_API_KEY
cp Api/.env.example Api/.env
docker compose up --build
```

- Agent (LangGraph dev server): `http://localhost:2024`
- API (FastAPI health): `http://localhost:8000/health`
- Web (Vite): `http://localhost:5173`
