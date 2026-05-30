"""Seed a new user's /skills/ namespace with starter skills.

Starter skills live in SEED_SKILLS_DIR (the repo's Skills/ folder, mounted into
the container). On a user's first login we copy any starter skills into their
per-user store, giving papr a baseline library that users can then edit. Seeding
is skipped if the user already has skills, so edits/deletes are never clobbered.
"""
from __future__ import annotations

import os
from pathlib import Path

from . import store

SEED_SKILLS_DIR = Path(os.environ.get("SEED_SKILLS_DIR", "/app/seed-skills"))


def _load_seed_skills() -> dict[str, str]:
    """Read starter skills from disk once at import: {skill_name: SKILL.md text}."""
    skills: dict[str, str] = {}
    if not SEED_SKILLS_DIR.is_dir():
        return skills
    for sub in sorted(SEED_SKILLS_DIR.iterdir()):
        skill_md = sub / "SKILL.md"
        if sub.is_dir() and skill_md.is_file():
            skills[sub.name] = skill_md.read_text(encoding="utf-8")
    return skills


_SEED_SKILLS = _load_seed_skills()


async def seed_skills_for(user_id: str) -> None:
    """Write starter skills into the user's store, but only if they have none."""
    if not _SEED_SKILLS:
        return
    existing = await store.search(user_id, "skills", limit=1)
    if existing.get("items"):
        return  # already seeded / user has their own skills — don't overwrite

    for name, content in _SEED_SKILLS.items():
        await store.put(user_id, "skills", f"/{name}/SKILL.md", store.file_value(content))
