#!/bin/bash
cd /app/src/
poetry install
poetry run alembic upgrade head
poetry run pytest --cov --cov-config=.coveragerc