from __future__ import annotations
import math
from datetime import datetime, timezone, date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather import (
    WeatherStation,
    WeatherForecast,
    WethrHigh,
    TmaxCalculation,
)


async def _latest_model_temp(db: AsyncSession, station_id: int) -> float | None:
    """Get the latest model temperature forecast for a station."""
    stmt = (
        select(WeatherForecast)
        .where(WeatherForecast.station_id == station_id)
        .order_by(WeatherForecast.forecast_time.desc())
        .limit(1)
    )
    wf = (await db.execute(stmt)).scalar_one_or_none()
    if not wf:
        return None
    
    # If raw_data contains hourly temperature array, get the last value
    if wf.raw_data and "hourly" in wf.raw_data and "temperature_2m" in wf.raw_data["hourly"]:
        temps = wf.raw_data["hourly"]["temperature_2m"]
        if temps and len(temps) > 0:
            return float(temps[-1])
    
    # Fallback to the temperature field
    return wf.temperature


def _scoring(delta: float) -> tuple[float, float]:
    """Return (confidence, size) based on |delta|."""
    ad = abs(delta)
    if ad >= 3:
        return 0.95, 3.0
    if ad >= 2:
        return 0.85, 2.0
    if ad >= 1:
        return 0.70, 1.0
    return 0.50, 0.5


async def run_for_station(db: AsyncSession, station: WeatherStation, wethr_high: float) -> None:
    """Run strategy calculation for a station after receiving a Wethr high temperature."""
    model_temp = await _latest_model_temp(db, station.id)
    if model_temp is None:
        print(f"No model temperature found for station {station.code}")
        return
    
    delta = model_temp - wethr_high
    conf, size = _scoring(delta)

    tmax_calc = TmaxCalculation(
        station_id=station.id,
        cli_forecast=model_temp,
        observed_high=None,  # Will be filled in later when actual observed data is available
        method="MARLIN_v1",
        confidence=conf,
        size=size,
        raw_payload={
            "delta": delta,
            "model_temp": model_temp,
            "wethr_high": wethr_high,
            "station_code": station.code,
        },
        created_at=datetime.now(timezone.utc),
    )
    
    db.add(tmax_calc)
    print(f"Strategy signal for {station.code}: delta={delta:.1f}, confidence={conf}, size={size}") 