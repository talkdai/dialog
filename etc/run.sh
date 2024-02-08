#!/bin/bash

alembic upgrade head
python load_csv.py --path ${DIALOG_DATA_PATH}

if  [ -n "${TEST}" ]; then
    python -m unittest
    exit 0
fi

if [ -n "${DEBUG}" ]; then
    uvicorn main:app --host 0.0.0.0 --port ${PORT} --reload
else
    uvicorn main:app --host 0.0.0.0 --port ${PORT}
fi
