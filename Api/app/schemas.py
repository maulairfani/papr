"""Shared request models for the papr API.

Centralized so routers don't redefine the same shapes and the wire contract lives
in one place.
"""
from __future__ import annotations

from pydantic import BaseModel


class LoginBody(BaseModel):
    username: str


class ChatBody(BaseModel):
    message: str
    thread_id: str | None = None


class SkillBody(BaseModel):
    name: str
    content: str


class TopicBody(BaseModel):
    name: str
    query: str | None = None


class SubscribeBody(BaseModel):
    # Daily delivery time in UTC. The UI labels it as UTC explicitly.
    hour: int = 6
    minute: int = 0
