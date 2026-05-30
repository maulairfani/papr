# Development image for the papr agent. Runs the local LangGraph Agent Server
# (`langgraph dev`). Production builds use `langgraph build` (see Docs/ROADMAP.md).
FROM python:3.12-slim

WORKDIR /app

# Copy metadata + source, then install the package and the dev CLI.
COPY pyproject.toml ./
COPY papr ./papr
RUN pip install --no-cache-dir -e ".[dev]"

EXPOSE 2024

# --host 0.0.0.0 so the dev server is reachable from outside the container.
# --no-reload: the mounted volume + in-memory store's own persistence writes would
# otherwise trigger watchfiles reloads that fragment runs and wipe the store.
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "2024", "--no-reload"]
