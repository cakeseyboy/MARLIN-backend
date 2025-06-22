#!/bin/bash
set -e

echo "🚀 Starting MARLIN backend..."
echo "📊 Port: ${PORT:-8000}"
echo "🗄️  Database: ${DATABASE_URL:0:30}..."

# Wait for database
echo "⏳ Waiting for database..."
TRIES=30
until pg_isready -d "$DATABASE_URL" -q || [ $TRIES -eq 0 ]; do
  echo "   Waiting for Postgres... ($TRIES tries left)"
  sleep 2
  TRIES=$((TRIES-1))
done

if [ $TRIES -eq 0 ]; then
  echo "❌ Database connection timeout after 60 seconds"
  exit 1
fi

echo "✅ Database is ready!"

# Run migrations (don't fail if migrations fail)
echo "🔄 Running database migrations..."
if alembic upgrade head; then
    echo "✅ Migrations complete!"
else
    echo "⚠️  Warning: Migrations failed, but continuing startup..."
fi

# Start the application
echo "🌐 Starting FastAPI application on 0.0.0.0:${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 