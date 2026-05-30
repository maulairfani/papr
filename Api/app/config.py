"""API configuration, sourced from environment (Api/.env for local runs)."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load Api/.env regardless of the process working directory.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# LangGraph Agent Server URL. Local dev: localhost:2024; in docker: http://agent:2024.
AGENT_URL = os.environ.get("AGENT_URL", "http://localhost:2024")

# Dev auth secret. MUST be overridden in production.
JWT_SECRET = os.environ.get("PAPR_JWT_SECRET", "dev-insecure-secret-change-me")
JWT_ALGORITHM = "HS256"

# Allowed browser origins for CORS (the Vite dev server).
WEB_ORIGINS = os.environ.get(
    "PAPR_WEB_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

# Must match the agent's persistent folders (Agent/papr/backend.py).
PERSISTENT_FOLDERS = ("papers", "notes", "topics", "skills", "briefs")

# The graph name registered in Agent/langgraph.json.
ASSISTANT_ID = "papr"

# Static trigger sent to papr to produce a daily brief — identical for the cron
# job and the "generate now" button, so both paths exercise the same agent logic.
# The "what's new" reasoning lives in the agent (it reads /topics/), per CLAUDE.md.
BRIEF_TRIGGER = (
    "It's time for the daily brief. Generate today's brief now: follow the "
    "daily-brief steps and save it to /briefs/<today>.md."
)

# MCP personal access token (PAT) settings. issuer/audience MUST match the MCP
# server's verifier (Mcp/app/config.py) so a PAT minted here is accepted there.
MCP_ISSUER = os.environ.get("PAPR_MCP_ISSUER", "papr")
MCP_AUDIENCE = os.environ.get("PAPR_MCP_AUDIENCE", "papr-mcp")
MCP_PAT_DAYS = int(os.environ.get("PAPR_MCP_PAT_DAYS", "365"))
# Public URL of the MCP endpoint the user pastes into their MCP client.
# Host 9100 maps to the mcp container's 9000 (see docker-compose.yml).
MCP_PUBLIC_URL = os.environ.get("PAPR_MCP_URL", "http://localhost:9100/mcp")
