"""Custom agent middleware for papr."""
from __future__ import annotations

from .current_date import inject_current_date
from .file_types import PapersFileTypeMiddleware

__all__ = ["PapersFileTypeMiddleware", "inject_current_date"]
