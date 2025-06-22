FROM python:3.11-slim

# Install PostgreSQL client for pg_isready
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY config ./config
COPY alembic.ini .
COPY alembic ./alembic
COPY scripts/wait-for-db.sh ./scripts/wait-for-db.sh
COPY scripts/init-db.py ./scripts/init-db.py
RUN chmod +x ./scripts/wait-for-db.sh

CMD bash scripts/wait-for-db.sh uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 