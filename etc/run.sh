#!/bin/bash
set -e

poetry run alembic upgrade head
[[ -z "${DIALOG_LOADCSV_CLEARDB}" ]] || CLEARDB_COMMAND=--cleardb
[[ -z "${DIALOG_LOADCSV_EMBED_COLUMNS}" ]] || EMBED_COLUMNS="--embed-columns ${DIALOG_LOADCSV_EMBED_COLUMNS}"
poetry run python load_csv.py --path ${DIALOG_DATA_PATH} ${CLEARDB_COMMAND} ${EMBED_COLUMNS}

/app/etc/install-plugins.sh

if  [ -n "${TEST}" ]; then
    python -m unittest
    exit 0
fi

if [ -n "${DEBUG}" ]; then
    exec poetry run uvicorn main:app --host 0.0.0.0 --port ${PORT} --reload
else
    exec poetry run uvicorn main:app --host 0.0.0.0 --port ${PORT}
fi
