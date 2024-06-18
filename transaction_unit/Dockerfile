FROM python:3.12.4-bookworm

ARG PERF ID

ENV YOUR_ENV=${YOUR_ENV} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    # Poetry's install location:
    POETRY_HOME='/usr/local'


RUN curl -sSL https://install.python-poetry.org | python3 -
RUN mkdir /app && adduser app && chown -R app /app
WORKDIR /app

COPY pyproject.toml .
RUN poetry install --only=main --no-interaction --no-ansi

ADD transaction_unit/ transaction_unit/

ENV APP_TMP_DATA=/tmp PYTHONPATH=/app
USER app
ENTRYPOINT poetry run python transaction_unit/main.py $PERF $ID
