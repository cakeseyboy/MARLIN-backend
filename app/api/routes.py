from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.weather import WeatherStation, TmaxCalculation
from app.api.schemas import (
    WeatherStationIn,
    WeatherStationOut,
    TmaxCalcIn,
    TmaxCalcOut,
)

router = APIRouter(prefix="/stations", tags=["stations"])


@router.post("/", response_model=WeatherStationOut, status_code=201)
async def create_station(
    station: WeatherStationIn, db: AsyncSession = Depends(get_db)
) -> WeatherStation:
    obj = WeatherStation(**station.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("/", response_model=List[WeatherStationOut])
async def list_stations(db: AsyncSession = Depends(get_db)) -> List[WeatherStation]:
    res = await db.execute(select(WeatherStation))
    return list(res.scalars().all())


@router.get("/{station_id}", response_model=WeatherStationOut)
async def get_station(
    station_id: int, db: AsyncSession = Depends(get_db)
) -> WeatherStation:
    obj = await db.get(WeatherStation, station_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Station not found")
    return obj


# --- tmax sub-router ---
tmax_router = APIRouter(prefix="/tmax", tags=["tmax"])


@tmax_router.post("/", response_model=TmaxCalcOut, status_code=201)
async def create_tmax(
    calc: TmaxCalcIn, db: AsyncSession = Depends(get_db)
) -> TmaxCalculation:
    obj = TmaxCalculation(**calc.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@tmax_router.get("/station/{station_id}", response_model=List[TmaxCalcOut])
async def list_tmax_for_station(
    station_id: int, db: AsyncSession = Depends(get_db)
) -> List[TmaxCalculation]:
    res = await db.execute(
        select(TmaxCalculation).where(TmaxCalculation.station_id == station_id)
    )
    return list(res.scalars().all())
