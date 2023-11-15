FROM python:3.11-slim as dependencies

WORKDIR /dependencies

COPY ["pyproject.toml", "poetry.lock", "/dependencies/"]

RUN pip install poetry && \
  poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim

ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_CACHE_DIR=on
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random
ENV PYTHONUNBUFFERED=1

COPY . /app

WORKDIR /app/src
COPY --from=dependencies /dependencies/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "/app/etc/run.sh" ]
