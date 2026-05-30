"""MCP: mint a per-user personal access token (PAT) for external MCP clients.

The user pastes the returned token + url into Claude Desktop / Cursor; the papr
MCP server verifies the PAT and scopes all reads to this user.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from .. import config
from ..core.auth import current_user, mint_mcp_token

router = APIRouter()


@router.post("/mcp/token")
def mcp_token(user_id: str = Depends(current_user)) -> dict:
    return {"token": mint_mcp_token(user_id), "url": config.MCP_PUBLIC_URL}
