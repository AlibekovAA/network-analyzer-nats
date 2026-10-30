FROM python:3.13-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.11.28 /uv /bin/uv

WORKDIR /app

LABEL maintainer="aslan.alibekov.2017@mail.ru"
LABEL version="0.1.0"
LABEL description="Python FastAPI NATS Application"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

FROM base AS production

COPY app app/

RUN mypy app/

ENV PYTHONPATH=/app
ENV TZ=Europe/Moscow

HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
