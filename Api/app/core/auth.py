"""Dev authentication.

The whole point of the BFF auth boundary: `user_id` is derived from a token the
server signed, never from a client-supplied field. So a client cannot read or
write another user's files. Swap `dev_login` for real auth (OAuth/OIDC) later;
the rest of the app only depends on `current_user`.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .. import config

_bearer = HTTPBearer(auto_error=True)


def mint_token(user_id: str) -> str:
    return jwt.encode({"sub": user_id}, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def mint_mcp_token(user_id: str) -> str:
    """Mint a long-lived per-user PAT for external MCP clients.

    Carries an audience/issuer so the MCP server accepts it while rejecting an
    ordinary web session token (which has neither).
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iss": config.MCP_ISSUER,
        "aud": config.MCP_AUDIENCE,
        "scope": "papr:read",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=config.MCP_PAT_DAYS)).timestamp()),
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def current_user(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
    """Resolve the authenticated user_id from the Bearer token."""
    try:
        payload = jwt.decode(
            creds.credentials, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "token has no subject")
    return user_id
