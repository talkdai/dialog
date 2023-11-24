lint:
	poetry run black .

db:
	docker compose up db

run:
	poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000 --lifespan on --env-file ../.env

load-data:
	poetry run python load_csv.py --path $(path)