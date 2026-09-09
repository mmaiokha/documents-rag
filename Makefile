api-dev:
	uv run --project api fastapi dev api/src/main.py

api-start:
	uv run --project api fastapi run api/src/main.py

migrate:
	cd api && uv run alembic upgrade head

migration:
	cd api && uv run alembic revision --autogenerate -m "$(name)"

infra-setup:
	uv run --project infra infra/src/main.py

worker:
	uv run --project worker worker/src/main.py