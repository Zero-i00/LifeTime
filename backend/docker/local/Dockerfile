FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ../../pyproject.toml ../../uv.lock ./

ENV UV_LINK_MODE=copy
ENV PYTHONPATH=/app

RUN uv sync --frozen

COPY ../../ .


RUN sed -i 's/\r$//' ./docker/local/entrypoint.sh && chmod +x ./docker/local/entrypoint.sh

ENTRYPOINT ["./docker/local/entrypoint.sh"]
