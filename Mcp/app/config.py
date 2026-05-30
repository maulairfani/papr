"""MCP server configuration, sourced from environment (Mcp/.env for local runs).

The JWT settings MUST match the API's PAT minting (same secret/issuer/audience),
so a token the API mints for a user is accepted here.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# LangGraph Agent Server (holds the per-user store). In docker: http://agent:2024.
AGENT_URL = os.environ.get("AGENT_URL", "http://localhost:2024")

# Shared secret for verifying per-user PATs. MUST equal the API's PAPR_JWT_SECRET.
JWT_SECRET = os.environ.get("PAPR_JWT_SECRET", "dev-insecure-secret-change-me")
JWT_ALGORITHM = "HS256"
MCP_ISSUER = os.environ.get("PAPR_MCP_ISSUER", "papr")
MCP_AUDIENCE = os.environ.get("PAPR_MCP_AUDIENCE", "papr-mcp")

# Path the streamable-HTTP transport is served at (clients connect to host:9000/mcp).
MCP_PATH = os.environ.get("PAPR_MCP_PATH", "/mcp")

# Must match the agent's persistent folders (Agent/papr/backend.py).
PERSISTENT_FOLDERS = ("papers", "notes", "topics", "skills", "briefs")
