# Docker Production Deployment

This guide details how to deploy SnapSplit using Docker Compose for a production-ready environment.

## Architecture

The system is composed of the following containerized services:

- **Frontend (Nginx)**: Serves the React SPA and proxies API requests.
- **Backend (FastAPI)**: Runs the application logic (gunicorn/uvicorn).
- **PostgreSQL**: Primary database for persistent data.
- **Redis**: Message broker for Celery and caching.
- **Celery Worker**: Processes background tasks (e.g., OCR bill scanning).

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux) installed and running.
- Git cloned repository.

## Quick Start

1. **Verify Environment Variables**
   Ensure `.env.prod` exists and contains correct secrets.
   ```bash
   # .env.prod should be in the root directory
   JWT_SECRET_KEY=...
   DATABASE_URL=postgresql+psycopg2://...
   GROQ_API_KEY=...
   ```

2. **Build and Start**
   Run the following command in the project root:
   ```bash
   docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
   ```

3. **Verify Deployment**
   - Access the application at `http://localhost`.
   - Backend API is accessible internally via Nginx at `/api`.
   - Check logs: `docker compose -f docker-compose.prod.yml logs -f`.

## Scaling Workers

To handle higher load for AI processing, scale the Celery workers:
```bash
docker compose -f docker-compose.prod.yml up -d --scale celery-worker=3
```

## Troubleshooting

- **Database Connection Failed**: Ensure the `postgres` service is healthy before the backend starts (managed by `healthcheck` in compose file).
- **OCR Not Working**: Verify `tesseract-ocr` is installed in the worker container (exec into it and run `tesseract --version`).
- **WebSockets Failed**: Ensure Nginx config properly upgrades headers for `/ws` endpoint.
- **Docker Daemon Error**: If you see "error during connect", ensure Docker Desktop is running.
