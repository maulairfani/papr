"""Prompt text for the papr agent, kept as editable files (one .md per prompt).

Keeping prompts out of the Python source makes them easy to read, diff, and edit
without touching code. Add new prompts as `.md` files in this package and expose
them here.
"""
from __future__ import annotations

from pathlib import Path

_DIR = Path(__file__).parent


def load(name: str) -> str:
    """Read a prompt file from this package by name (e.g. 'system_prompt.md')."""
    return (_DIR / name).read_text(encoding="utf-8").strip()


SYSTEM_PROMPT = load("system_prompt.md")
