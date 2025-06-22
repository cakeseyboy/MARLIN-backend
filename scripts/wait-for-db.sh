#!/usr/bin/env bash
set -e

# Extract connection details from DATABASE_URL if available
if [ -n "$DATABASE_URL" ]; then
    # Parse DATABASE_URL (format: postgres://user:pass@host:port/db)
    export POSTGRES_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    export POSTGRES_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    export POSTGRES_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    export POSTGRES_DB=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
fi

# Default values if not set
export POSTGRES_HOST=${POSTGRES_HOST:-localhost}
export POSTGRES_PORT=${POSTGRES_PORT:-5432}
export POSTGRES_USER=${POSTGRES_USER:-marlin}
export POSTGRES_DB=${POSTGRES_DB:-marlin}

echo "🔗 Connecting to PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."

until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  echo "⏳ waiting for Postgres…"
  echo ": - no response"
  sleep 1
done

echo "🚀 Postgres is ready! Running database initialization..."
python scripts/init-db.py
echo "✅ Database initialization complete!"

exec "$@"
