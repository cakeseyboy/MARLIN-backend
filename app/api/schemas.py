from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any


class WeatherStationIn(BaseModel):
    code: str = Field(..., min_length=3, max_length=5)
    name: str
    lat: float
    lon: float
    timezone: str
    coastal_distance_km: float


class WeatherStationOut(WeatherStationIn):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TmaxCalcIn(BaseModel):
    station_id: int
    cli_forecast: float
    method: str
    confidence: float
    raw_payload: Any


class TmaxCalcOut(TmaxCalcIn):
    id: int
    observed_high: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
