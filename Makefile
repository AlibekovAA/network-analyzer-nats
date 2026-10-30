.PHONY: sync lint lint-python lint-go up restart stop clean

sync:
	cd python_app && uv sync --frozen

lint: lint-python lint-go

lint-python:
	cd python_app && uv run --frozen ruff check app
	cd python_app && uv run --frozen python -m mypy app

lint-go:
	cd go_app && go vet ./...

up:
	docker compose up --build -d

restart:
	docker compose restart

stop:
	docker compose stop

clean:
	docker compose down --remove-orphans
