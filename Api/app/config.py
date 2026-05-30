"""BFF configuration via pydantic-settings (environment / Api/.env)."""
from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings. Env names keep the historical PAPR_* spelling via aliases."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LangGraph Agent Server URL (docker: http://agent:2024; local: localhost:2024).
    agent_url: str = Field("http://localhost:2024", validation_alias="AGENT_URL")
    # The graph/assistant registered in Agent/langgraph.json.
    assistant_id: str = "papr"

    # Dev auth secret. MUST be overridden in production.
    jwt_secret: str = Field("dev-insecure-secret-change-me", validation_alias="PAPR_JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_ttl_days: int = 7

    # Comma-separated browser origins for CORS (the Vite dev server, 5173/5174).
    web_origins: str = Field(
        "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174",
        validation_alias="PAPR_WEB_ORIGINS",
    )

    # Persistent store folders — MUST match the agent (Agent/papr/agent.py).
    # `notes` merged into `papers`; `topics` dropped; `memories` added.
    persistent_folders: tuple[str, ...] = ("papers", "skills", "briefs", "memories")

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.web_origins.split(",") if o.strip()]


settings = Settings()
