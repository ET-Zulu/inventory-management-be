# Inventory Backend - Docker Setup Guide

## Quick Start

### Using Docker Compose

1. **Build the images:**
   ```bash
   docker-compose build
   # or
   make docker-build
   ```

2. **Start the services:**
   ```bash
   docker-compose up -d
   # or
   make docker-up
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f app
   # or
   make docker-logs
   ```

4. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Useful Docker Commands

**Stop containers:**
```bash
docker-compose down
# or
make docker-down
```

**Clean up (remove volumes):**
```bash
docker-compose down -v
# or
make docker-clean
```

**Run migrations:**
```bash
docker-compose exec app alembic upgrade head
# or
make docker-migrate
```

**Access app shell:**
```bash
docker-compose exec app /bin/bash
# or
make docker-shell
```

### Environment Variables

Default Docker environment variables are defined in `.env`:
- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
- `APP_NAME`: Application name
- `APP_VERSION`: API version
- `API_V1_PREFIX`: API prefix

You can modify these in the `.env` file or `docker-compose.yml`.

### Database

- **Service**: `postgres:15-alpine`
- **Port**: 5432 (forwarded to host)
- **Volume**: `postgres_data` (persisted)

### Local Development (without Docker)

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start the app:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

```
inventory_backend/
├── app/
│   ├── main.py
│   ├── api/
│   ├── db/
│   ├── model/
│   ├── core/
│   └── ...
├── alembic/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── .dockerignore
```

## Troubleshooting

**Port already in use:**
```bash
# Change port in docker-compose.yml or kill the process
lsof -i :8000  # Find process using port 8000
kill -9 <PID>
```

**Database connection failed:**
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check logs: `docker-compose logs db`
- Verify DATABASE_URL in `.env`

**Migrations not running:**
```bash
docker-compose exec app alembic upgrade head
```
