from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    geography_id = Column(Integer, ForeignKey("geographies.id", ondelete="CASCADE"), nullable=False)
    observation_time = Column(DateTime, nullable=False)
    wind_speed_10m_ms = Column(Numeric(6, 2), nullable=True)   # Wind speed at 10m height (m/s)
    wind_speed_100m_ms = Column(Numeric(6, 2), nullable=True)  # Wind speed at hub height (m/s)
    wind_direction_deg = Column(Numeric(5, 1), nullable=True)  # Wind direction (degrees)
    solar_ghi_wm2 = Column(Numeric(7, 2), nullable=True)       # Global Horizontal Irradiance (W/m2)
    solar_dni_wm2 = Column(Numeric(7, 2), nullable=True)       # Direct Normal Irradiance (W/m2)
    temperature_celsius = Column(Numeric(5, 2), nullable=True) # Temperature (Celsius)
    cloud_cover_pct = Column(Numeric(5, 2), nullable=True)     # Cloud cover (%)
    precipitation_mm = Column(Numeric(6, 2), nullable=True)    # Precipitation (mm)
    latitude = Column(Numeric(8, 4), nullable=True)            # Latitude of observation
    longitude = Column(Numeric(8, 4), nullable=True)           # Longitude of observation
    weather_model = Column(String(50), nullable=True, default="ECMWF ERA5")
    record_type = Column(String(30), nullable=True, default="REANALYSIS")  # REANALYSIS, HISTORICAL_OBSERVATION, FORECAST
    weather_source = Column(String(50), default="ERA5 / Open-Meteo")
    retrieval_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    geography = relationship("Geography", back_populates="weather_observations")

    __table_args__ = (
        UniqueConstraint("geography_id", "observation_time", name="uq_weather_geo_time"),
        Index("idx_weather_geo_time", "geography_id", "observation_time"),
    )
