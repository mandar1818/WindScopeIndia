from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Date, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class EnergySource(Base):
    __tablename__ = "energy_sources"

    source_code = Column(String(20), primary_key=True)  # 'WIND', 'SOLAR', 'LARGE_HYDRO', 'SMALL_HYDRO', 'BIOMASS', 'OTHER_RE'
    display_name = Column(String(100), nullable=False)
    unit = Column(String(20), default="MU")              # Million Units
    is_variable_re = Column(Boolean, default=False)

    capacities = relationship("InstalledCapacity", back_populates="energy_source")
    monthly_generations = relationship("GenerationMonthly", back_populates="energy_source")
    daily_generations = relationship("GenerationDaily", back_populates="energy_source")
    block_generations = relationship("Generation15MinBlock", back_populates="energy_source")
    forecasts = relationship("ForecastRecord", back_populates="energy_source")
    evaluations = relationship("ForecastEvaluation", back_populates="energy_source")


class InstalledCapacity(Base):
    __tablename__ = "installed_capacity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    geography_id = Column(Integer, ForeignKey("geographies.id", ondelete="CASCADE"), nullable=False)
    source_code = Column(String(20), ForeignKey("energy_sources.source_code"), nullable=False)
    effective_date = Column(Date, nullable=False)
    capacity_mw = Column(Numeric(12, 2), nullable=False)
    source_provenance = Column(String(100), nullable=False, default="CEA Monthly Executive Summary")
    created_at = Column(DateTime, default=datetime.utcnow)

    geography = relationship("Geography", back_populates="capacities")
    energy_source = relationship("EnergySource", back_populates="capacities")

    __table_args__ = (
        UniqueConstraint("geography_id", "source_code", "effective_date", name="uq_capacity_geo_source_date"),
        Index("idx_installed_capacity_geo_date", "geography_id", "effective_date"),
    )

