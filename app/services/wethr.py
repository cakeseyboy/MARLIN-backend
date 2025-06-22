from datetime import datetime, timezone
from typing import Optional

from playwright.async_api import async_playwright
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather import WeatherStation, WeatherForecast
from app.services.ingest_guard import should_run


async def fetch_wethr_high(station_code: str) -> Optional[float]:
    """Fetch the high temperature from wethr.net for a given station."""
    url = f"https://wethr.net/{station_code.lower()}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            
            # Wait for the page to load and try to find temperature data
            # This is a placeholder - actual selectors would need to be determined
            # by inspecting the wethr.net site structure
            await page.wait_for_timeout(2000)
            
            # Example selector - would need to be updated based on actual site
            temp_element = await page.query_selector(".temperature-high")
            if temp_element:
                temp_text = await temp_element.text_content()
                if temp_text:
                    # Extract numeric value from temperature string
                    import re
                    match = re.search(r'(\d+\.?\d*)', temp_text)
                    if match:
                        return float(match.group(1))
            
            return None
        except Exception as e:
            print(f"Error fetching wethr data for {station_code}: {e}")
            return None
        finally:
            await browser.close()


async def fetch_and_store_single(code: str) -> None:
    """Fetch and store wethr data for a single station with guard protection."""
    if not should_run(f"wethr-{code}"):
        return
    
    from app.db.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        # Get the station
        stmt = select(WeatherStation).where(WeatherStation.code == code.upper())
        result = await db.execute(stmt)
        station = result.scalar_one_or_none()
        
        if not station:
            print(f"Station {code} not found")
            return
        
        # Fetch wethr data
        high_temp = await fetch_wethr_high(code)
        
        if high_temp is not None:
            # Store as a forecast record with wethr source
            wf = WeatherForecast(
                station_id=station.id,
                source="Wethr",
                forecast_time=datetime.now(timezone.utc),
                valid_time=datetime.now(timezone.utc),
                temperature=high_temp,
                raw_data={"wethr_high": high_temp, "scraped_at": datetime.now(timezone.utc).isoformat()},
            )
            db.add(wf)
            await db.commit()
            print(f"Stored wethr high temp {high_temp}°F for {code}")
        else:
            print(f"Failed to fetch wethr data for {code}") 