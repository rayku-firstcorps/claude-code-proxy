FROM ghcr.io/astral-sh/uv:bookworm-slim

ARG PYTHON_VERSION=3.13.9

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON=${PYTHON_VERSION}

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
RUN uv sync --locked --no-dev --python "${UV_PYTHON}"

CMD ["/app/.venv/bin/python", "start_proxy.py"]
