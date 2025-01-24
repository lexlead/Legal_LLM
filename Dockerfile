FROM python:3.11-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y g++ build-essential && rm -rf /var/lib/apt/lists/*


WORKDIR /app


ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ARG UV_EXTRA_INDEX_URL


COPY uv.lock /app/


RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    UV_EXTRA_INDEX_URL=${UV_EXTRA_INDEX_URL} \
    uv sync --frozen --no-install-project --no-editable

COPY streamlit_app /app
COPY core /app
COPY rag /app
COPY app.py /app/app.py

EXPOSE 8080

CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
