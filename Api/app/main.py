"""papr API — FastAPI backend-for-frontend (BFF).

Bridges the React app and the LangGraph Agent Server. Endpoints live in
`app/routers/` (one thin module per domain) and delegate to `app/services/` for
all business logic and store access. Cross-cutting infra (auth, the agent-server
client) is in `app/core/`. This file builds the app, applies CORS, maps domain
errors to HTTP status, and wires the routers together.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import config
from .routers import auth, chat, files, health, mcp, papers, skills, topics
from .services.errors import Invalid, NotFound


def create_app() -> FastAPI:
    app = FastAPI(title="papr API", version="0.0.1")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.WEB_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Map service-layer domain errors to HTTP status, so routers stay thin and
    # services never import FastAPI.
    @app.exception_handler(Invalid)
    async def _on_invalid(_: Request, exc: Invalid) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(NotFound)
    async def _on_not_found(_: Request, exc: NotFound) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    for module in (auth, chat, files, papers, skills, topics, mcp, health):
        app.include_router(module.router)
    return app


app = create_app()
