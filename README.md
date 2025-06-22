# MARLIN Backend (FastAPI)

Self-contained service that exposes MARLIN's weather-trading logic via a REST/JSON interface.  
Stack: **FastAPI + SQLAlchemy + Postgres**. Deployable on Fly.io.

## Quick start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
``` 