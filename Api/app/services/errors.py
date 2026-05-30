"""Domain exceptions, mapped to HTTP status by handlers in main.py."""
from __future__ import annotations


class Invalid(Exception):
    """Bad input from the client (-> 400)."""


class NotFound(Exception):
    """A requested resource does not exist (-> 404)."""
