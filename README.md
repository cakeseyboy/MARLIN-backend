# MARLIN Backend (FastAPI)

Self-contained service that exposes MARLIN's weather-trading logic via a REST/JSON interface.  
Stack: **FastAPI + SQLAlchemy + Postgres**. Deployable on Fly.io.

## Quick start

### Option 1: Docker Compose (Recommended)
```bash
# 1. configure env
cp .env.sample .env              # adjust creds if needed

# 2. spin up stack
docker compose up --build

# 3. hit the API
curl http://localhost:8000/health   # → {"status":"ok"}
```

### Option 2: Local Development
```bash
cp .env.sample .env      # configure creds
pip install -r requirements.txt
uvicorn app.main:app --reload
``` 