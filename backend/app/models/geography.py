from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Region(Base):
    __tablename__ = "regions"

    region_code = Column(String(10), primary_key=True)  # 'NR', 'WR', 'SR', 'ER', 'NER'
    name = Column(String(100), nullable=False)
    headquarters = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)

    geographies = relationship("Geography", back_populates="region")


class Geography(Base):
    __tablename__ = "geographies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False, index=True)  # ISO e.g. 'IN-MH', 'IN-TN', 'IN-DL'
    name = Column(String(100), nullable=False, index=True)              # 'Maharashtra', 'Tamil Nadu'
    entity_type = Column(String(20), nullable=False)                    # 'STATE' or 'UNION_TERRITORY'
    region_code = Column(String(10), ForeignKey("regions.region_code"), nullable=False)
    capital = Column(String(100), nullable=False)
    latitude = Column(Numeric(8, 4), nullable=False)
    longitude = Column(Numeric(8, 4), nullable=False)
    geojson_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    region = relationship("Region", back_populates="geographies")
    capacities = relationship("InstalledCapacity", back_populates="geography", cascade="all, delete-orphan")
    monthly_generations = relationship("GenerationMonthly", back_populates="geography", cascade="all, delete-orphan")
    daily_generations = relationship("GenerationDaily", back_populates="geography", cascade="all, delete-orphan")
    daily_operational_metrics = relationship("DailyOperationalMetrics", back_populates="geography", cascade="all, delete-orphan")
    block_generations = relationship("Generation15MinBlock", back_populates="geography", cascade="all, delete-orphan")
    weather_observations = relationship("WeatherObservation", back_populates="geography", cascade="all, delete-orphan")
    forecasts = relationship("ForecastRecord", back_populates="geography", cascade="all, delete-orphan")
    evaluations = relationship("ForecastEvaluation", back_populates="geography", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_geo_code_type", "code", "entity_type"),
    )

