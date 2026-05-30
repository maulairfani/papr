"""Step 5 verification: topics + daily-brief cron, end-to-end over the BFF.

Run inside the api container (talks to itself on :8000 and the agent on :2024):
    docker compose exec -T api python scripts/check_brief.py

Checks: topic CRUD, per-user isolation, subscribe creates a cron carrying the
right user_id context, "generate now" produces a /briefs/ file, unsubscribe
deletes the cron.
"""
from __future__ import annotations

import asyncio

import httpx
from langgraph_sdk import get_client

API = "http://localhost:8000"
AGENT = "http://agent:2024"


async def main() -> None:
    agent = get_client(url=AGENT)
    async with httpx.AsyncClient(base_url=API, timeout=180) as api:

        async def login(username: str) -> dict:
            r = await api.post("/auth/dev-login", json={"username": username})
            r.raise_for_status()
            return {"Authorization": f"Bearer {r.json()['token']}"}

        alice = await login("brief-alice")
        bob = await login("brief-bob")

        print("== topics ==")
        r = await api.post(
            "/topics",
            json={"name": "Diffusion Models", "query": "diffusion models image generation"},
            headers=alice,
        )
        print("alice add topic:", r.status_code, r.json())
        print("alice topics:", (await api.get("/topics", headers=alice)).json())
        print("bob topics (isolated):", (await api.get("/topics", headers=bob)).json())

        print("\n== subscribe ==")
        r = await api.post("/brief/subscribe", json={"hour": 6, "minute": 30}, headers=alice)
        print("subscribe:", r.status_code, r.json())
        cron_id = r.json()["cron_id"]
        print("alice subscription:", (await api.get("/brief/subscription", headers=alice)).json())
        print("bob subscription (isolated):", (await api.get("/brief/subscription", headers=bob)).json())

        crons = await agent.crons.search(limit=50)
        mine = next((c for c in crons if c.get("cron_id") == cron_id), None)
        print("cron present on agent:", mine is not None)
        if mine:
            print("  schedule:", mine.get("schedule"), "| metadata:", mine.get("metadata"))
            # Confirm the scheduled run will carry alice's user_id into context.
            payload = mine.get("payload") or {}
            ctx = payload.get("context") or mine.get("context")
            print("  carries context:", ctx)

        print("\n== generate now ==")
        r = await api.post("/brief/run-now", headers=alice)
        print("run-now:", r.status_code, r.json())
        brief = None
        for _ in range(60):
            await asyncio.sleep(3)
            files = (await api.get("/files", headers=alice)).json()["files"]
            briefs = [f for f in files if f["path"].startswith("/briefs/")]
            if briefs:
                brief = briefs[0]
                break
        print("brief file:", brief)
        if brief:
            content = (
                await api.get("/files/content", params={"path": brief["path"]}, headers=alice)
            ).json()["content"]
            print("--- brief (first 700 chars) ---\n" + content[:700])
        bob_briefs = [
            f for f in (await api.get("/files", headers=bob)).json()["files"]
            if f["path"].startswith("/briefs/")
        ]
        print("bob briefs (isolated):", bob_briefs)

        print("\n== unsubscribe ==")
        print("unsubscribe:", (await api.post("/brief/unsubscribe", headers=alice)).json())
        crons2 = await agent.crons.search(limit=50)
        print("cron deleted:", all(c.get("cron_id") != cron_id for c in crons2))
        print("subscription after:", (await api.get("/brief/subscription", headers=alice)).json())


if __name__ == "__main__":
    asyncio.run(main())
