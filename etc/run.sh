#!/bin/bash

python load_csv.py --path ${DIALOG_DATA_PATH}
uvicorn main:app --host 0.0.0.0 --port ${PORT}
