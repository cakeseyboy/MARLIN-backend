from datetime import datetime, timezone, date
from typing import Optional

from playwright.async_api import async_playwright
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather import WeatherStation, WeatherForecast, WethrHigh
from app.services.ingest_guard import should_run
from app.services import strategy


async def fetch_wethr_high(station_code: str) -> Optional[float]:
    """Fetch the high temperature from wethr.net for a given station."""
    url = f"https://wethr.net/{station_code.lower()}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            
            # Wait for the page to load and try to find temperature data
            # This is a placeholder implementation - actual scraping logic would go here
            # For now, return a mock temperature for testing
            await page.wait_for_timeout(1000)
            
            # TODO: Implement actual temperature scraping logic
            # Example: high_temp_element = await page.query_selector('.high-temp')
            # if high_temp_element:
            #     temp_text = await high_temp_element.text_content()
            #     return float(temp_text.strip('°F'))
            
            # Mock temperature for testing (random value between 70-100°F)
            import random
            return round(random.uniform(70.0, 100.0), 1)
            
        except Exception as e:
            print(f"Error scraping wethr.net for {station_code}: {e}")
            return None
        finally:
            await browser.close()


async def store_wethr_data(db: AsyncSession, station_code: str, high_temp: float) -> None:
    """Store wethr.net data in the database."""
    # Get the station
    stmt = select(WeatherStation).where(WeatherStation.code == station_code.upper())
    result = await db.execute(stmt)
    station = result.scalar_one_or_none()
    
    if not station:
        print(f"Station {station_code} not found")
        return
    
    # Store the data
    wf = WeatherForecast(
        station_id=station.id,
        source="Wethr",
        forecast_time=datetime.now(timezone.utc),
        valid_time=datetime.now(timezone.utc),
        temperature=high_temp,
        raw_data={"high_temperature": high_temp, "source": "wethr.net"},
    )
    db.add(wf)
    await db.commit()
    print(f"Stored Wethr data for {station_code}: {high_temp}°F")


async def fetch_and_store_single(code: str) -> None:
    """Fetch and store wethr data for a single station with guard protection and strategy engine."""
    if not should_run(f"wethr-{code}"):
        return
    
    from app.db.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            high_temp = await fetch_wethr_high(code)
            if high_temp is None:
                print(f"No temperature data scraped for {code}")
                return
            
            # Get the station
            stmt = select(WeatherStation).where(WeatherStation.code == code.upper())
            result = await db.execute(stmt)
            station = result.scalar_one_or_none()
            
            if not station:
                print(f"Station {code} not found")
                return
            
            # Create WethrHigh record
            wethr_high_record = WethrHigh(
                station_id=station.id,
                date_iso=date.today().isoformat(),
                wethr_high=high_temp,
                scraped_at=datetime.now(timezone.utc),
            )
            db.add(wethr_high_record)
            
            # Run strategy engine
            await strategy.run_for_station(db, station, high_temp)
            
            # Commit all changes
            await db.commit()
            print(f"Processed Wethr data and strategy for {code}: {high_temp}°F")
            
        except Exception as e:
            print(f"Error in fetch_and_store_single for {code}: {e}")
            await db.rollback() 