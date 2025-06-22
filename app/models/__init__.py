from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import all models to ensure they're registered with the Base
from app.models.weather import WeatherStation, TmaxCalculation, WeatherForecast 