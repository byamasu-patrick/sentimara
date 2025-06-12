run:
	uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2 --reload

# Generate a new migration with automatic detection of changes
migration-generate:
	alembic revision --autogenerate -m "$(message)"

# Apply all pending migrations
migration-upgrade:
	alembic upgrade head

# Downgrade to the previous migration
migration-downgrade:
	alembic downgrade -1

# Show current migration version
migration-current:
	alembic current

# Show migration history
migration-history:
	alembic history --verbose

# Show migration history
migration-history:
	alembic history --verbose
