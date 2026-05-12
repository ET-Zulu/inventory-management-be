.PHONY: help docker-build docker-up docker-down docker-logs docker-shell docker-migrate docker-seed

help:
	@echo "Available commands:"
	@echo "  make docker-build    - Build Docker images"
	@echo "  make docker-up       - Start Docker containers"
	@echo "  make docker-down     - Stop Docker containers"
	@echo "  make docker-logs     - View Docker logs"
	@echo "  make docker-shell    - Open shell in app container"
	@echo "  make docker-migrate  - Run database migrations"
	@echo "  make docker-clean    - Remove Docker containers and volumes"

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f app

docker-shell:
	docker-compose exec app /bin/bash

docker-migrate:
	docker-compose exec app alembic upgrade head

docker-clean:
	docker-compose down -v

local-install:
	pip install -r requirements.txt

local-run:
	uvicorn app.main:app --reload

local-migrate:
	alembic upgrade head
