"""Dev auth: mint a JWT for a user_id and resolve it back on each request.

This is the web<->agent surface from CLAUDE.md: the BFF authenticates the user to
a `user_id`, which it then injects into agent runs and store access server-side so
each user is isolated. A real provider replaces dev-login at deploy time.
"""
from __future__ import annotations

import time

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import settings


def mint_token(user_id: str) -> str:
    now = int(time.time())
    payload = {"sub": user_id, "iat": now, "exp": now + settings.jwt_ttl_days * 86400}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def user_from_token(token: str) -> str:
    """Decode a bearer token to its `user_id`. Used by the dependency below and by
    endpoints that take the token via query string (e.g. an <iframe> PDF src)."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing subject")
    return user_id


_bearer = HTTPBearer(auto_error=True)


def current_user(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
    """FastAPI dependency → the authenticated `user_id`. Never client-supplied."""
    return user_from_token(creds.credentials)
