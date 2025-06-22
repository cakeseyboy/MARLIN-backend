FROM python:3.11-slim

# Install PostgreSQL client for pg_isready
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic
COPY scripts/wait-for-db.sh ./scripts/wait-for-db.sh
RUN chmod +x ./scripts/wait-for-db.sh

CMD ["bash", "-c", "./scripts/wait-for-db.sh && uvicorn app.main:app --host 0.0.0.0 --port 8000"] 