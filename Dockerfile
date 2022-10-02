FROM python:3.9 AS dev_build

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.1.12 \
  POETRY_CACHE_DIR="/var/cache/pypoetry" \
  PATH="$PATH:/root/.local/bin"

RUN apt update \
  # Installing `poetry` package manager:
  # https://github.com/python-poetry/poetry
  && curl -sSL 'https://install.python-poetry.org' | python - \
  && poetry --version

WORKDIR /root/app
COPY ./pyproject.toml ./poetry.lock /root/app/


RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-dev -vvv \
  && rm -rf $POETRY_CACHE_DIR

ENV PYTHONPATH=/root/app

COPY ./ /root/app

CMD ["poetry", "run", "python3", "bereal_telegram/run.py"]