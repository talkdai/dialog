FROM python:3.11-slim as dependencies

WORKDIR /dependencies

COPY ["pyproject.toml", "poetry.lock", "/dependencies/"]

RUN pip install poetry && \
  poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=100 \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_NO_CACHE_DIR=on \
  PYTHONFAULTHANDLER=1 \
  PYTHONHASHSEED=random \
  PYTHONUNBUFFERED=1

COPY --from=dependencies /dependencies/requirements.txt ./requirements.txt
COPY ./app .
RUN chmod +x /app/run.sh

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
