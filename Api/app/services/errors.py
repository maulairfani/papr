"""Domain errors raised by services, mapped to HTTP status codes in app.main.

Services raise these instead of importing FastAPI, so business logic stays free
of transport concerns and the routers stay thin.
"""
from __future__ import annotations


class Invalid(Exception):
    """Bad input — mapped to HTTP 400."""


class NotFound(Exception):
    """Missing resource — mapped to HTTP 404."""
