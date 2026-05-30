"""First-login seeding: copy starter skills + AGENTS.md into a new user's store.

Idempotent — only writes when the user has none yet. Seed sources ship inside the
image at /app/seed-skills and /app/seed-memory (Api/seed-skills, Api/seed-memory).
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..core.agent_client import agent_client

SEED_SKILLS = Path("/app/seed-skills")
SEED_MEMORY = Path("/app/seed-memory")


def _fv(content: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {"content": content, "encoding": "utf-8", "created_at": now, "modified_at": now}


async def seed_user(user_id: str) -> dict:
    """Seed starter skills + AGENTS.md if absent. Returns counts written."""
    client = agent_client()
    seeded = {"skills": 0, "memory": 0}

    skills = await client.store.search_items([user_id, "papr", "skills"], limit=1)
    if not skills["items"] and SEED_SKILLS.is_dir():
        for sub in sorted(SEED_SKILLS.iterdir()):
            skill_md = sub / "SKILL.md"
            if sub.is_dir() and skill_md.is_file():
                await client.store.put_item(
                    [user_id, "papr", "skills"],
                    key=f"/{sub.name}/SKILL.md",
                    value=_fv(skill_md.read_text("utf-8")),
                )
                seeded["skills"] += 1

    memories = await client.store.search_items([user_id, "papr", "memories"], limit=1)
    agents_md = SEED_MEMORY / "AGENTS.md"
    if not memories["items"] and agents_md.is_file():
        await client.store.put_item(
            [user_id, "papr", "memories"], key="/AGENTS.md", value=_fv(agents_md.read_text("utf-8"))
        )
        seeded["memory"] = 1

    return seeded
