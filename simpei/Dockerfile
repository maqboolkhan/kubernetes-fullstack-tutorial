# Multi-stage build for production FastAPI service
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-install-project --no-dev

# Production stage
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app
# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv
COPY src/ /app/src/

# Create data directory for SQLite database with proper permissions
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

USER appuser

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV SQLALCHEMY_DATABASE_URL="sqlite:///./data/todos.db"

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.simpei.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
