.PHONY: install lint format test coverage run docker-up docker-down logs

install:
	python -m venv .venv
	.venv\Scripts\pip install -e .[dev]

lint:
	.venv\Scripts\ruff check .
	.venv\Scripts\mypy app

format:
	.venv\Scripts\black .
	.venv\Scripts\ruff check --fix .

test:
	.venv\Scripts\pytest tests

coverage:
	.venv\Scripts\pytest --cov=app --cov-report=html tests

run:
	.venv\Scripts\uvicorn app.main:app --reload

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

logs:
	docker-compose logs -f
