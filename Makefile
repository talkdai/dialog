lint:
	poetry run black .

db-up:
	docker compose up db

run:
	poetry run uvicorn --app-dir src main:app --reload --host 0.0.0.0 --port 8000 --lifespan on --env-file .env

# make load-data path="data/2023-12-02.csv"
load-data:
	poetry run python src/load_csv.py --path $(path)

test-build:
	docker compose -f docker-compose.test.yml run --rm --build dialog

test:
	docker compose -f docker-compose.test.yml run --rm dialog