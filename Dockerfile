FROM python:3.11-slim-buster AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    VIRTUAL_ENV=/venv \
    PATH="/venv/bin:${PATH}"

FROM base AS build

ARG POETRY_VERSION=1.8.3

RUN set -eux; \
    python -m pip install "poetry==${POETRY_VERSION}"; \
    python -m venv /venv

COPY ./poetry.lock ./poetry.lock
COPY ./pyproject.toml ./pyproject.toml

RUN poetry install --no-root --only=main

COPY app /app

FROM base

COPY --from=build /venv /venv
COPY --from=build /app /app
COPY ./run.sh /run.sh

EXPOSE 8000

RUN chmod +x /run.sh

CMD ["/run.sh"]
