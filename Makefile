lint:
	poetry run black .

db-up:
	docker compose up db

run:
	poetry run uvicorn --app-dir src main:app --reload --host 0.0.0.0 --port 8000 --lifespan on --env-file .env

load-data:
	poetry run python src/load_csv.py --path $(path)
