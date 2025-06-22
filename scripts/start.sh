#!/bin/bash
set -e

echo "Starting MARLIN backend..."

# Wait for database
./scripts/wait-for-db.sh

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 