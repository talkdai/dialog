#!/bin/bash
set -e

poetry run alembic upgrade head
exec poetry run pytest --cov=. --cov-config=.coveragerc . -vvv --timeout 10