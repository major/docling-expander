.PHONY: test lint typecheck all db-up db-down db-logs chunk-content cleanup-workers

test:
	uv run pytest

lint:
	uv run pre-commit run --all-files

typecheck:
	uv run pyright src/codex

db-up:
	podman compose -f src/codex/postgres-compose.yml up -d

db-down:
	podman compose -f src/codex/postgres-compose.yml down

db-logs:
	podman compose -f src/codex/postgres-compose.yml logs -f db

chunk-content:
	uv run codex chunk

cleanup-workers:
	uv run codex cleanup-workers

all: lint test typecheck
