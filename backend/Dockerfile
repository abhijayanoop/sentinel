# ---- Stage 1: build dependencies ----
FROM python:3.12-slim AS builder

ENV UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /app

RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ---- Stage 2: final runtime image ----
FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

ENV PATH="/app/.venv/bin:$PATH"

# non-root user: if the app is compromised, the attacker isn't root inside the container
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]