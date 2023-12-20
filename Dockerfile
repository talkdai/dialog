FROM python:3.11-slim

ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_CACHE_DIR=on
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install poetry && \
  poetry config virtualenvs.create false && \
  poetry install --no-dev

COPY /src/ /app
COPY /etc/ /app


WORKDIR /app/src

ENTRYPOINT [ "/app/etc/run.sh" ]

