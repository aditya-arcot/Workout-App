.PHONY: dev test check_migrations manual_migration auto_migration run_migrations

dev:
	uv run fastapi dev app/main.py --port 8080

test:
	uv run pytest -v

check_migrations:
	uv run alembic check

manual_migration:
	@test -n "$(msg)" || (echo "ERROR: msg is required"; exit 1)
	uv run alembic revision -m "$(msg)"

auto_migration:
	@test -n "$(msg)" || (echo "ERROR: msg is required"; exit 1)
	uv run alembic revision --autogenerate -m "$(msg)"

run_migrations:
	uv run alembic upgrade head
