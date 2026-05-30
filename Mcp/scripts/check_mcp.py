"""Step 6 verification: the papr MCP server, end-to-end with a real PAT.

Run inside the mcp container (reaches the API at :8000 and itself at :9000):
    docker compose exec -T mcp python scripts/check_mcp.py

Checks: PAT minting, MCP tools/list, list_files + read_file scoped to the token's
user, and that a bad / missing token is rejected.
"""
from __future__ import annotations

import asyncio

import httpx
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

API = "http://api:8000"
MCP_URL = "http://localhost:9000/mcp"


def _data(result):
    # CallToolResult: FastMCP wraps non-object returns as {"result": value} in
    # structured_content — plain JSON, unlike `.data` (deserialized model objects).
    sc = getattr(result, "structured_content", None)
    if isinstance(sc, dict) and "result" in sc:
        return sc["result"]
    if sc is not None:
        return sc
    return getattr(result, "data", None)


async def main() -> None:
    # 1) Mint a PAT for a user that has some files (skills are seeded on login).
    async with httpx.AsyncClient(base_url=API, timeout=30) as api:
        tok = (await api.post("/auth/dev-login", json={"username": "mcp-user"})).json()["token"]
        h = {"Authorization": f"Bearer {tok}"}
        await api.post("/topics", json={"name": "Mechanistic Interpretability"}, headers=h)
        pat_resp = (await api.post("/mcp/token", headers=h)).json()
    pat = pat_resp["token"]
    print("PAT url:", pat_resp["url"], "| token length:", len(pat))

    # 2) Connect to the MCP server with the PAT and exercise the tools.
    transport = StreamableHttpTransport(MCP_URL, headers={"Authorization": f"Bearer {pat}"})
    async with Client(transport) as client:
        tools = await client.list_tools()
        print("tools:", [t.name for t in tools])

        files = _data(await client.call_tool("list_files", {})) or []
        print("list_files count:", len(files))
        for f in files[:6]:
            print("  -", f["path"])

        target = next((f["path"] for f in files if str(f["path"]).endswith("SKILL.md")), None)
        if target:
            content = _data(await client.call_tool("read_file", {"path": target}))
            print(f"read_file {target} (first 160):", str(content)[:160].replace("\n", " "))

        topics = _data(await client.call_tool("list_files", {"folder": "topics"})) or []
        print("topics folder ->", [f["path"] for f in topics])

    # 3) Negative: a bad token and a missing token must both be rejected.
    for label, headers in [("bad token", {"Authorization": "Bearer not-a-real-token"}), ("no token", {})]:
        t = StreamableHttpTransport(MCP_URL, headers=headers)
        try:
            async with Client(t) as c:
                await c.list_tools()
            print(f"{label}: ACCEPTED (WRONG)")
        except Exception as e:  # noqa: BLE001
            print(f"{label}: rejected ({type(e).__name__})")


if __name__ == "__main__":
    asyncio.run(main())
