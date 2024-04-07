#!/bin/bash
poetry install --sync
cd src && alembic upgrade head && cd ..
apt upgrade && apt update && apt install postgresql-client -y
