style:
	poetry run black .

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --lifespan on
