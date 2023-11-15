style:
	poetry run black .

run:
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --lifespan on

load_data:
	poetry run python src/load_csv.py --path data/buser.csv
