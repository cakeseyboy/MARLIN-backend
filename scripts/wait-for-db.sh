#!/usr/bin/env bash
set -e

until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  echo "⏳ waiting for Postgres…"
  sleep 1
done

echo "�� Postgres is ready! Initializing database..."
python scripts/init-db.py
echo "✅ Database initialization complete!"

exec "$@" 