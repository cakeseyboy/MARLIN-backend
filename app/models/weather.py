from sqlalchemy import String, Float, Integer, JSON, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.models import Base


class WeatherStation(Base):
    __tablename__ = "weather_stations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(5), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(32))
    coastal_distance_km: Mapped[float] = mapped_column(Float)


class TmaxCalculation(Base):
    __tablename__ = "tmax_calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(Integer)
    cli_forecast: Mapped[float] = mapped_column(Float)
    observed_high: Mapped[float] = mapped_column(Float, nullable=True)
    method: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column(Float)
    raw_payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(16))  # HRRR, GFS, etc.
    run_timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    data: Mapped[dict] = mapped_column(JSON) 