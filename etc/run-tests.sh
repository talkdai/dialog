#!/bin/bash
set -e

cd /app/src/
poetry install --only dev
poetry run alembic upgrade head
exec poetry run pytest --cov=. --cov-config=.coveragerc . -vvv