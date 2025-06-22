# MARLIN Backend (FastAPI)

[![CI](https://github.com/yourusername/MARLIN-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/MARLIN-backend/actions/workflows/ci.yml)

Weather-trading application backend built with FastAPI, SQLAlchemy, and PostgreSQL. Exposes weather trading logic via REST/JSON interface.

## Features

- **FastAPI**: High-performance async web framework
- **SQLAlchemy 2.0**: Modern async ORM with type safety
- **PostgreSQL**: Robust database with JSON support
- **Alembic**: Database migrations
- **Docker Compose**: Development environment
- **Automated Data Ingestion**: Station-specific scheduling for weather data
- **Strategy Engine**: Automated trading signal generation
- **Comprehensive Testing**: Async test suite with CI/CD

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

## Strategy Engine

Every time a Wethr "High" temperature is scraped, the strategy engine automatically:

1. **Pulls latest model forecast** temperature for the station
2. **Calculates delta** between model and Wethr high
3. **Maps delta to confidence & position size** using scoring tiers:
   - `|Δ| ≥ 3°F`: confidence=0.95, size=3.0
   - `|Δ| ≥ 2°F`: confidence=0.85, size=2.0  
   - `|Δ| ≥ 1°F`: confidence=0.70, size=1.0
   - `|Δ| < 1°F`: confidence=0.50, size=0.5
4. **Creates trading signal** in `tmax_calculations` table

### Example Strategy Output
```json
{
  "station_id": 3,
  "cli_forecast": 92.6,
  "observed_high": null,
  "method": "MARLIN_v1",
  "confidence": 0.95,
  "size": 3.0,
  "raw_payload": {
    "delta": 3.6,
    "model_temp": 92.6,
    "wethr_high": 89.0,
    "station_code": "KMIA"
  }
}
```

The strategy engine runs automatically during post-DSM and post-CLI Wethr scrapes, generating live trade signals ready for MARLIN consumption.

## Data Ingestion

The system automatically ingests weather data using station-specific timing windows optimized for DSM (Decision Support Matrix) and CLI (Command Line Interface) operations.

### Station-Specific Scheduling

Each weather station has four daily ingestion windows defined in `config/ingest_schedule.yml`:

- **pre_dsm**: Model data fetch before DSM window
- **post_dsm**: Wethr scrape after DSM window  
- **pre_cli**: Model data fetch before CLI window
- **post_cli**: Wethr scrape after CLI window

Example for Austin (KAUS):
```yaml
KAUS:
  pre_dsm: "21:07"    # 9:07 PM UTC - fetch models
  post_dsm: "21:19"   # 9:19 PM UTC - scrape wethr
  pre_cli: "06:07"    # 6:07 AM UTC - fetch models  
  post_cli: "06:19"   # 6:19 AM UTC - scrape wethr
```

### Adjusting Ingest Windows

Edit `config/ingest_schedule.yml` and restart the stack. Times are UTC; keep them quoted (`"22:12"`). Guard logic ensures we never hit a source more than once every 30 minutes.

### Data Sources

1. **Open-Meteo API**: Numerical weather models (HRRR, GFS, ECMWF)
2. **Wethr.net**: Scraped temperature data via Playwright

### Manual Data Ingestion

Trigger ingestion for specific stations:

```bash
# Ingest Open-Meteo data for Austin
curl -X POST "http://localhost:8000/stations/ingest/KAUS"

# Response: {"status": "queued"}
```

## Testing

```bash
# Run tests with Docker Compose
docker compose exec api pytest

# Or run tests locally
source venv/bin/activate
pytest
``` 