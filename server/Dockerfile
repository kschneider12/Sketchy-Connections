# syntax=docker/dockerfile:1.7
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
COPY client/pyproject.toml client/pyproject.toml
COPY server/pyproject.toml server/pyproject.toml
COPY shared/pyproject.toml shared/pyproject.toml

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --package sketchy-server --no-install-workspace

COPY server ./server
COPY shared ./shared

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --package sketchy-server

EXPOSE 8000

CMD ["uv", "run", "--package", "sketchy-server", "uvicorn", "sketchy_server.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
