"""papr BFF — FastAPI app factory.

Thin routers -> services (logic + store) -> core (auth, agent client). The BFF is
stateless: all data lives in the agent's per-user store; this process holds none.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .routers import auth, briefs, chat, files, health
from .services.errors import Invalid, NotFound


def create_app() -> FastAPI:
    app = FastAPI(title="papr API", version="0.0.1")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Invalid)
    async def _on_invalid(_, exc: Invalid):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(NotFound)
    async def _on_not_found(_, exc: NotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    for module in (health, auth, files, chat, briefs):
        app.include_router(module.router)

    return app


app = create_app()
