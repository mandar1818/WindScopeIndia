from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime, Date,
    ForeignKey, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base


# ============================================================================
# SQLAlchemy ORM Models (India Multi-Year Platform)
# ============================================================================

class GenerationMonthly(Base):
    __tablename__ = "generation_monthly"

    id = Column(Integer, primary_key=True, autoincrement=True)
    geography_id = Column(Integer, ForeignKey("geographies.id", ondelete="CASCADE"), nullable=False)
    source_code = Column(String(20), ForeignKey("energy_sources.source_code"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    generation_mu = Column(Numeric(12, 3), nullable=True)  # Million Units (None for MISSING_OBSERVATION)
    target_mu = Column(Numeric(12, 3), nullable=True)       # CEA Target
    capacity_utilization_factor_pct = Column(Numeric(6, 2), nullable=True) # CUF %
    source_provenance = Column(String(100), nullable=False, default="CEA Monthly RE Report")
    is_verified = Column(Boolean, default=True)

    # Phase 2: Provenance & Classification
    dataset_classification = Column(
        String(50),
        nullable=False,
        default="DEMONSTRATION",
        server_default="DEMONSTRATION",
        index=True
    )
    source_file_id = Column(Integer, ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True, index=True)
    source_org = Column(String(100), nullable=True)
    dataset_name = Column(String(255), nullable=True)
    source_url = Column(String(512), nullable=True)
    original_filename = Column(String(255), nullable=True)
    sha256_checksum = Column(String(64), nullable=True, index=True)
    publication_date = Column(String(50), nullable=True)
    download_timestamp = Column(DateTime, nullable=True)
    extraction_timestamp = Column(DateTime, nullable=True)
    processing_timestamp = Column(DateTime, nullable=True)
    parser_version = Column(String(50), nullable=True, default="1.0.0")

    # Record-Level Provenance & Staged Validation
    original_state_label = Column(String(100), nullable=True)
    normalized_geography_code = Column(String(20), nullable=True, index=True)
    original_fuel_label = Column(String(100), nullable=True)
    original_reported_value = Column(String(50), nullable=True)
    original_unit = Column(String(50), nullable=True, default="MU")
    normalized_unit = Column(String(20), nullable=False, default="MU", server_default="MU")
    unit_conversion_applied = Column(String(100), nullable=True, default="DIRECT_MU")
    pdf_page_number = Column(Integer, nullable=True)
    table_heading = Column(String(255), nullable=True)

    validation_status = Column(String(50), nullable=False, default="UNAUDITED", server_default="UNAUDITED")
    observation_status = Column(String(50), nullable=False, default="REPORTED_VALUE", server_default="REPORTED_VALUE")
    created_at = Column(DateTime, default=datetime.utcnow)

    geography = relationship("Geography", back_populates="monthly_generations")
    energy_source = relationship("EnergySource", back_populates="monthly_generations")
    source_file = relationship("SourceFile", back_populates="monthly_generations")

    __table_args__ = (
        CheckConstraint("month >= 1 AND month <= 12", name="chk_month_range"),
        UniqueConstraint("geography_id", "source_code", "year", "month", "dataset_classification", name="uq_gen_monthly_record"),
        Index("idx_gen_monthly_geo_year", "geography_id", "year", "month"),
        Index("idx_gen_monthly_source_year", "source_code", "year", "month"),
        Index("idx_gen_monthly_dataset", "dataset_classification", "year", "month"),
    )


class GenerationDaily(Base):
    __tablename__ = "generation_daily"

    id = Column(Integer, primary_key=True, autoincrement=True)
    geography_id = Column(Integer, ForeignKey("geographies.id", ondelete="CASCADE"), nullable=False)
    source_code = Column(String(20), ForeignKey("energy_sources.source_code"), nullable=False)
    delivery_date = Column(Date, nullable=False)
    generation_mu = Column(Numeric(12, 3), nullable=False)  # Million Units
    peak_generation_mw = Column(Numeric(12, 2), nullable=True)
    source_file_id = Column(Integer, ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True, index=True)
    source_provenance = Column(String(100), nullable=False, default="CEA Daily RE Report / NPP")
    data_classification = Column(String(50), nullable=False, default="VERIFIED_OFFICIAL", server_default="VERIFIED_OFFICIAL")
    created_at = Column(DateTime, default=datetime.utcnow)

    geography = relationship("Geography", back_populates="daily_generations")
    energy_source = relationship("EnergySource", back_populates="daily_generations")
    source_file = relationship("SourceFile")

    __table_args__ = (
        UniqueConstraint("geography_id", "source_code", "delivery_date", name="uq_gen_daily_record"),
        Index("idx_gen_daily_geo_date", "geography_id", "delivery_date"),
    )


class DailyOperationalMetrics(Base):
    """
    Dedicated operational measurement abstraction for grid power supply position (PSP).
    Captures operational electrical demand (energy met, peak demand, shortages)
    as distinct from energy generation fuel technologies.
    """
    __tablename__ = "daily_operational_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    geography_id = Column(Integer, ForeignKey("geographies.id", ondelete="CASCADE"), nullable=False)
    delivery_date = Column(Date, nullable=False)
    energy_met_mu = Column(Numeric(12, 3), nullable=False)  # Total system demand met in MU
    peak_demand_met_mw = Column(Numeric(12, 2), nullable=True) # Peak demand met in MW
    peak_shortage_mw = Column(Numeric(12, 2), nullable=True)   # Maximum shortage MW
    energy_shortage_mu = Column(Numeric(12, 3), nullable=True) # Unserved energy in MU
    source_file_id = Column(Integer, ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True, index=True)
    source_provenance = Column(String(100), nullable=False, default="Grid Controller of India Limited (NLDC Daily PSP)")
    data_classification = Column(String(50), nullable=False, default="VERIFIED_OFFICIAL", server_default="VERIFIED_OFFICIAL")
    created_at = Column(DateTime, default=datetime.utcnow)

    geography = relationship("Geography", back_populates="daily_operational_metrics")
    source_file = relationship("SourceFile")

    __table_args__ = (
        UniqueConstraint("geography_id", "delivery_date", name="uq_daily_operational_metrics"),
        Index("idx_daily_operational_geo_date", "geography_id", "delivery_date"),
    )


class Generation15MinBlock(Base):
    __tablename__ = "generation_15min_blocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    geography_id = Column(Integer, ForeignKey("geographies.id", ondelete="CASCADE"), nullable=False)
    source_code = Column(String(20), ForeignKey("energy_sources.source_code"), nullable=False)
    block_timestamp = Column(DateTime, nullable=False)
    block_number = Column(Integer, nullable=False)          # 1 to 96
    actual_generation_mw = Column(Numeric(10, 2), nullable=True)
    scheduled_generation_mw = Column(Numeric(10, 2), nullable=True)
    deviation_mw = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    geography = relationship("Geography", back_populates="block_generations")
    energy_source = relationship("EnergySource", back_populates="block_generations")

    __table_args__ = (
        CheckConstraint("block_number >= 1 AND block_number <= 96", name="chk_block_range"),
        UniqueConstraint("geography_id", "source_code", "block_timestamp", name="uq_gen_15min_block"),
        Index("idx_gen_15min_geo_time", "geography_id", "block_timestamp"),
    )
