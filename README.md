# MARLIN Backend (FastAPI)

[![CI](https://github.com/yourusername/MARLIN-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/MARLIN-backend/actions/workflows/ci.yml)

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

## API Usage

### Create a weather station
```bash
curl -X POST localhost:8000/stations/ \
  -H 'Content-Type: application/json' \
  -d '{"code":"KLAX","name":"Los Angeles Intl","lat":33.94,"lon":-118.40,"timezone":"America/Los_Angeles","coastal_distance_km":3.4}'
```

### List all stations
```bash
curl localhost:8000/stations/
```

### Get a specific station
```bash
curl localhost:8000/stations/{station_id}
```

### Create a temperature calculation
```bash
curl -X POST localhost:8000/stations/tmax/ \
  -H 'Content-Type: application/json' \
  -d '{"station_id":1,"cli_forecast":78.5,"method":"MARLIN_v1","confidence":0.85,"raw_payload":{"model":"GFS","temp":78.5}}'
```

### Manual data ingestion
```bash
# Trigger data ingestion for a specific station
curl -X POST localhost:8000/stations/ingest/KLAX
```

## Development

### Install development dependencies
```bash
pip install -r requirements-dev.txt
```

### Code quality tools
```bash
# Format code
black .

# Type check
mypy app

# Run tests
pytest
```

### CI Pipeline
Every PR is automatically checked with:
- **Black** for code formatting
- **MyPy** for type checking
- **Pytest** for running the test suite

## Data Ingestion

The application automatically ingests weather data from Open-Meteo every hour at HH:15 UTC for all registered weather stations. Data is stored in the `weather_forecasts` table with full JSON payload preservation.

### Automatic ingestion
- **Schedule**: Every hour at 15 minutes past the hour (UTC)
- **Source**: Open-Meteo API
- **Data**: Hourly temperature forecasts with full API response

### Manual ingestion
Use the `/stations/ingest/{station_code}` endpoint to trigger data collection for a specific station on demand.

## Testing

```bash
# Run tests with Docker Compose
docker compose exec api pytest

# Or run tests locally
source venv/bin/activate
pytest
``` 