#!/usr/bin/env bash
set -e

# Simple approach: start the app directly if DATABASE_URL is available
# Railway handles service connections automatically
if [ -n "$DATABASE_URL" ]; then
    echo "🔗 Found DATABASE_URL, starting application directly..."
    echo "🚀 Running database initialization..."
    python scripts/init-db.py
    echo "✅ Database initialization complete!"
    exec "$@"
fi

# Fallback for local development with individual env vars
export POSTGRES_HOST=${POSTGRES_HOST:-localhost}
export POSTGRES_PORT=${POSTGRES_PORT:-5432}
export POSTGRES_USER=${POSTGRES_USER:-marlin}
export POSTGRES_DB=${POSTGRES_DB:-marlin}

echo "🔗 Connecting to PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."

until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  echo "⏳ waiting for Postgres…"
  sleep 1
done

echo "🚀 Postgres is ready! Running database initialization..."
python scripts/init-db.py
echo "✅ Database initialization complete!"

exec "$@"
