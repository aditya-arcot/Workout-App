### base
FROM ghcr.io/astral-sh/uv:python3.14-alpine AS base

WORKDIR /src

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_TOOL_BIN_DIR=/usr/local/bin

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY app ./app
COPY alembic.ini pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/src/.venv/bin:$PATH"


### dev
FROM base AS dev

EXPOSE 8000

CMD ["fastapi", "run", "--reload", "app/main.py"]


### prod
FROM base AS prod

EXPOSE 8000

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
