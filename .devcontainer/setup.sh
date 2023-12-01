#!/bin/bash
git config --global safe.directory /workspaces

poetry install --no-root --all-extras --sync
source /workspaces/.venv/bin/activate
cd src && alembic upgrade head && cd ..
