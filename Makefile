.PHONY: build up down venv install run


build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

venv:
	uv venv

install: venv
	uv sync --frozen --no-install-project --no-editable

run: install
	uv run worker.py
