FROM ghcr.io/astral-sh/uv:python3.12-bookworm
WORKDIR /app

COPY pyproject.toml ./
# COPY uv.lock ./   # (optional if you have one)

RUN uv sync --frozen --no-dev || uv sync --no-dev

COPY . .

CMD ["uv", "run", "python", "src/homeharvest_mcp/server.py"]
