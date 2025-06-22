from contextlib import asynccontextmanager
from typing import AsyncGenerator

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from fastapi import FastAPI

from app.api.routes import router as station_router
from app.db.database import get_db
from app.services.ingest import ingest_all

# Global scheduler instance
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan - start/stop scheduler."""
    # Start scheduler
    scheduler.add_job(
        ingest_all_wrapper,
        "cron",
        minute="15",  # every hour at HH:15 UTC
        misfire_grace_time=180,
    )
    scheduler.start()
    yield
    # Stop scheduler
    scheduler.shutdown()


async def ingest_all_wrapper() -> None:
    """Wrapper to provide database session to ingest_all."""
    from app.db.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await ingest_all(session)


app = FastAPI(title="MARLIN API", version="0.1.0", lifespan=lifespan)

app.include_router(station_router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
