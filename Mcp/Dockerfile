# Development image for the papr MCP server (FastMCP over streamable HTTP).
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-cache-dir -e .

EXPOSE 9000

# uvicorn runs the FastMCP ASGI app (its lifespan sets up the session manager).
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "9000"]
