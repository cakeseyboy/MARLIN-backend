from datetime import datetime, date
from typing import Dict, Any

from sqlalchemy import Integer, String, Float, ForeignKey, func, JSON, Date
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class WeatherStation(Base):
    __tablename__ = "weather_stations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(50))
    coastal_distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=func.now()
    )

    # Relationships
    tmax_calculations = relationship("TmaxCalculation", back_populates="station")
    forecasts = relationship("WeatherForecast", back_populates="station")
    wethr_highs = relationship("WethrHigh", back_populates="station")


class TmaxCalculation(Base):
    __tablename__ = "tmax_calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("weather_stations.id"))
    cli_forecast: Mapped[float] = mapped_column(Float)
    observed_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    method: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[float] = mapped_column(Float)
    size: Mapped[float] = mapped_column(Float, default=0)
    raw_payload: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=func.now()
    )

    # Relationships
    station = relationship("WeatherStation", back_populates="tmax_calculations")


class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("weather_stations.id"))
    source: Mapped[str] = mapped_column(String(20))  # HRRR, GFS, etc.
    forecast_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    valid_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    temperature: Mapped[float] = mapped_column(Float)
    raw_data: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=func.now()
    )

    # Relationships
    station = relationship("WeatherStation", back_populates="forecasts")


class WethrHigh(Base):
    __tablename__ = "wethr_highs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("weather_stations.id"))
    date_iso: Mapped[str] = mapped_column(String(10))  # YYYY-MM-DD format
    wethr_high: Mapped[float] = mapped_column(Float)
    scraped_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    # Relationships
    station = relationship("WeatherStation", back_populates="wethr_highs")
