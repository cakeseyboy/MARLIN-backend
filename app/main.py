from contextlib import asynccontextmanager
from typing import AsyncGenerator

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.api.routes import router
from app.core.schedule_loader import load_station_times
from app.services.ingest import fetch_forecast_single
from app.services.wethr import fetch_and_store_single

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan with scheduler."""
    # Initialize database
    try:
        from app.models import Base
        from app.core.settings import get_settings
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        settings = get_settings()
        engine = create_async_engine(settings.database_url)
        
        async with engine.begin() as conn:
            print("🗄️  Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("🔄 Application will continue, database will be retried on first request")
    
    # Load station timing configuration
    station_times = load_station_times()
    
    # Schedule jobs for each station
    for code, times in station_times.items():
        pre_dsm, post_dsm, pre_cli, post_cli = times
        
        # Schedule model fetches (pre_dsm and pre_cli)
        for t in (pre_dsm, pre_cli):
            h, m = map(int, t.split(":"))
            scheduler.add_job(
                fetch_forecast_single,
                "cron",
                hour=h, minute=m, timezone="UTC",
                args=[code], name=f"{code}-model-{t}",
                misfire_grace_time=180, coalesce=True,
            )
        
        # Schedule wethr scrapes (post_dsm and post_cli)
        for t in (post_dsm, post_cli):
            h, m = map(int, t.split(":"))
            scheduler.add_job(
                fetch_and_store_single,
                "cron",
                hour=h, minute=m, timezone="UTC",
                args=[code], name=f"{code}-wethr-{t}",
                misfire_grace_time=180, coalesce=True,
            )
    
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="MARLIN Weather API",
    description="Weather trading backend with FastAPI + SQLAlchemy + Postgres",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
