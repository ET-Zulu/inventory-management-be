.PHONY: help local-install local-run local-migrate

help:
	@echo "Available commands:"
	@echo "  make local-install   - Install Python dependencies"
	@echo "  make local-run       - Start the FastAPI app locally"
	@echo "  make local-migrate   - Run database migrations locally"

local-install:
	pip install -r requirements.txt

local-run:
	uvicorn app.main:app --reload

local-migrate:
	alembic upgrade head
