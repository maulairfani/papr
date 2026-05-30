"""papr MCP server.

Exposes each user's papr store (papers, notes, topics, skills, briefs) to external
MCP clients (Claude Desktop, Cursor) over streamable HTTP. Auth is a per-user
bearer token (PAT) minted by the API and verified here with the shared secret; the
token's `sub` claim is the user_id, which scopes every store read — so a client
can only ever see its own files.
"""
from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token

from . import config, store

# Verify HS256 PATs signed with the shared secret. `public_key` accepts the
# symmetric secret for HMAC algorithms. issuer/audience pin the token to papr's
# MCP surface, so an ordinary web session token (no audience) is not accepted.
verifier = JWTVerifier(
    public_key=config.JWT_SECRET,
    algorithm=config.JWT_ALGORITHM,
    issuer=config.MCP_ISSUER,
    audience=config.MCP_AUDIENCE,
)

mcp = FastMCP(
    name="papr",
    instructions=(
        "Browse your papr research workspace: papers you've saved, notes papr "
        "wrote, topics you follow, your explanation skills, and daily briefs."
    ),
    auth=verifier,
)


def _user_id() -> str:
    """The authenticated user_id, from the PAT's `sub` claim."""
    token = get_access_token()
    claims = getattr(token, "claims", None) or {}
    user_id = claims.get("sub") or getattr(token, "client_id", None)
    if not user_id:
        raise ValueError("token is missing a subject (sub) claim")
    return user_id


@mcp.tool
async def list_files(folder: str | None = None) -> list[dict]:
    """List your papr files.

    Optional `folder` narrows to one of: papers, notes, topics, skills, briefs.
    Returns each file's path and last-modified time.
    """
    return await store.list_files(_user_id(), folder)


@mcp.tool
async def read_file(path: str) -> str:
    """Read one papr file by path.

    Example paths: '/papers/1706.03762.md', '/notes/transformers.md',
    '/briefs/2026-05-30.md'.
    """
    return await store.read_file(_user_id(), path)


# ASGI app for uvicorn; serves the streamable-HTTP transport at config.MCP_PATH.
app = mcp.http_app(path=config.MCP_PATH)
