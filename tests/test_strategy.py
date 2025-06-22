import pytest
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models import Base, WeatherStation, WeatherForecast, TmaxCalculation
from app.services.strategy import _scoring, run_for_station


@pytest.mark.parametrize("delta,expected", [
    (-3.2, (0.95, 3.0)),
    (3.2, (0.95, 3.0)),
    (-2.1, (0.85, 2.0)),
    (2.1, (0.85, 2.0)),
    (-1.2, (0.70, 1.0)),
    (1.2, (0.70, 1.0)),
    (-0.4, (0.50, 0.5)),
    (0.4, (0.50, 0.5)),
    (0.0, (0.50, 0.5)),
])
def test_scoring(delta, expected):
    """Test the scoring function with various delta values."""
    assert _scoring(delta) == expected


@pytest.mark.asyncio
async def test_strategy_engine_integration():
    """Test the strategy engine with a mock database."""
    # Create in-memory test database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as db:
        # Create test station
        station = WeatherStation(
            code="KTEST",
            name="Test Airport",
            lat=30.0,
            lon=-97.0,
            timezone="America/Chicago",
            coastal_distance_km=100.0
        )
        db.add(station)
        await db.flush()  # Get the station ID
        
        # Create test forecast
        forecast = WeatherForecast(
            station_id=station.id,
            source="OpenMeteo",
            forecast_time=datetime.now(timezone.utc),
            valid_time=datetime.now(timezone.utc),
            temperature=85.0,
            raw_data={
                "hourly": {
                    "temperature_2m": [80.0, 82.0, 84.0, 85.0]
                }
            }
        )
        db.add(forecast)
        await db.commit()
        
        # Run strategy engine
        wethr_high = 82.0  # 3 degree difference from model (85.0)
        await run_for_station(db, station, wethr_high)
        await db.commit()
        
        # Check results using ORM query
        result = await db.execute(
            select(TmaxCalculation).where(TmaxCalculation.station_id == station.id)
        )
        tmax_calc = result.scalar_one_or_none()
        
        assert tmax_calc is not None
        assert tmax_calc.cli_forecast == 85.0
        assert tmax_calc.confidence == 0.95  # 3 degree delta
        assert tmax_calc.size == 3.0
        assert tmax_calc.method == "MARLIN_v1"
        assert tmax_calc.raw_payload["delta"] == 3.0
        assert tmax_calc.raw_payload["station_code"] == "KTEST"


@pytest.mark.asyncio
async def test_strategy_no_forecast():
    """Test strategy engine when no forecast is available."""
    # Create in-memory test database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as db:
        # Create test station without any forecasts
        station = WeatherStation(
            code="KTEST2",
            name="Test Airport 2",
            lat=30.0,
            lon=-97.0,
            timezone="America/Chicago",
            coastal_distance_km=100.0
        )
        db.add(station)
        await db.flush()
        await db.commit()
        
        # Run strategy engine
        wethr_high = 82.0
        await run_for_station(db, station, wethr_high)
        await db.commit()
        
        # Check that no tmax_calculation was created using ORM query
        result = await db.execute(
            select(func.count(TmaxCalculation.id)).where(TmaxCalculation.station_id == station.id)
        )
        count = result.scalar()
        assert count == 0 