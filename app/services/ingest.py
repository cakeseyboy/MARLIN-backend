from datetime import datetime, timezone
from typing import Dict, Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather import WeatherStation, WeatherForecast
from app.services.ingest_guard import should_run

OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&hourly=temperature_2m"
    "&timezone=UTC"
)


async def fetch_forecast(client: httpx.AsyncClient, station: WeatherStation) -> Any:
    """Fetch weather forecast data from Open-Meteo API for a station."""
    url = OPEN_METEO_URL.format(lat=station.lat, lon=station.lon)
    r = await client.get(url, timeout=20.0)
    r.raise_for_status()
    return r.json()


async def ingest_open_meteo_for_station(db: AsyncSession, station_code: str) -> None:
    """Ingest Open-Meteo data for a specific station."""
    # Get the station
    stmt = select(WeatherStation).where(WeatherStation.code == station_code.upper())
    result = await db.execute(stmt)
    station = result.scalar_one_or_none()
    
    if not station:
        print(f"Station {station_code} not found")
        return
    
    # Fetch and store data
    async with httpx.AsyncClient(http2=True) as client:
        try:
            data = await fetch_forecast(client, station)
            wf = WeatherForecast(
                station_id=station.id,
                source="OpenMeteo",
                forecast_time=datetime.now(timezone.utc),
                valid_time=datetime.now(timezone.utc),
                temperature=0.0,  # Will be populated from data processing
                raw_data=data,
            )
            db.add(wf)
            await db.commit()
            print(f"Stored Open-Meteo data for {station_code}")
        except Exception as e:
            print(f"Error ingesting Open-Meteo data for {station_code}: {e}")


async def fetch_forecast_single(code: str) -> None:
    """Fetch forecast for a single station with guard protection."""
    if not should_run(f"model-{code}"):
        return
    
    from app.db.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        await ingest_open_meteo_for_station(db, code)


async def ingest_all(db: AsyncSession) -> None:
    """Ingest weather data for all stations from Open-Meteo."""
    # Get all stations
    res = await db.execute(select(WeatherStation))
    stations = list(res.scalars().all())

    if not stations:
        return

    # Fetch data for all stations
    async with httpx.AsyncClient(http2=True) as client:
        for station in stations:
            try:
                data = await fetch_forecast(client, station)
                wf = WeatherForecast(
                    station_id=station.id,
                    source="OpenMeteo",
                    forecast_time=datetime.now(timezone.utc),
                    valid_time=datetime.now(timezone.utc),
                    temperature=0.0,  # Will be populated from data processing
                    raw_data=data,
                )
                db.add(wf)
            except Exception as e:
                # Log error but continue with other stations
                print(f"Error ingesting data for station {station.code}: {e}")
                continue

    await db.commit()
