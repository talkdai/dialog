#!/bin/bash
set -e

poetry run alembic upgrade head
[[ -z "${DIALOG_LOADCSV_CLEARDB}" ]] || CLEARDB_COMMAND=--cleardb
[[ -z "${DIALOG_LOADCSV_EMBED_COLUMNS}" ]] || EMBED_COLUMNS="--embed-columns ${DIALOG_LOADCSV_EMBED_COLUMNS}"
poetry run python load_csv.py --path ${DIALOG_DATA_PATH} ${CLEARDB_COMMAND} ${EMBED_COLUMNS}

/app/etc/install-plugins.sh

if  [ -n "${TEST}" ]; then
    python -m unittest
    exit $?
fi

WORKERS=${WORKERS:-1}

if [ -n "${DEBUG}" ]; then
    exec poetry run gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT} main:app --workers ${WORKERS} --reload
else
    exec poetry run gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT} main:app --workers ${WORKERS}
fi
