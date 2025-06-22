#!/usr/bin/env bash
set -e

# Wait for database with timeout
TRIES=30
until pg_isready -d "$DATABASE_URL" -q || [ $TRIES -eq 0 ]; do
  echo "⏳ waiting for Postgres…"
  sleep 2
  TRIES=$((TRIES-1))
done

if [ $TRIES -eq 0 ]; then
  echo "❌ Database connection timeout"
  exit 1
fi

echo "🚀 Postgres is ready!"
