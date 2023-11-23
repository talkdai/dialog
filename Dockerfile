FROM python:3.11-slim

ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_CACHE_DIR=on
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random
ENV PYTHONUNBUFFERED=1

COPY . /app

WORKDIR /app

RUN pip install poetry && \
  poetry config virtualenvs.create false && \
  poetry install --no-dev

WORKDIR /app/src

CMD [ "/app/etc/run.sh" ]

