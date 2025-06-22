from fastapi import FastAPI
from app.api.routes import router as station_router, tmax_router

app = FastAPI(title="MARLIN API", version="0.1.0")
app.include_router(station_router)
app.include_router(tmax_router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
