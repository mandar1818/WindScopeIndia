from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Date, ForeignKey, UniqueConstraint, Index, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class ForecastRecord(Base):
    __tablename__ = "forecast_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    geography_id = Column(Integer, ForeignKey("geographies.id", ondelete="CASCADE"), nullable=False)
    source_code = Column(String(20), ForeignKey("energy_sources.source_code"), nullable=False)
    forecast_type = Column(String(50), nullable=False)  # 'DAY_AHEAD_REMC', 'WEATHER_POWER_MODEL'
    publish_time = Column(DateTime, nullable=False)
    target_time = Column(DateTime, nullable=False)
    predicted_generation_mu = Column(Numeric(12, 3), nullable=True)
    predicted_generation_mw = Column(Numeric(10, 2), nullable=True)
    model_version = Column(String(50), nullable=False)
    is_eligible_under_cutoff = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    geography = relationship("Geography", back_populates="forecasts")
    energy_source = relationship("EnergySource", back_populates="forecasts")

    __table_args__ = (
        Index("idx_forecast_geo_target", "geography_id", "target_time"),
    )


class ForecastEvaluation(Base):
    __tablename__ = "forecast_evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    geography_id = Column(Integer, ForeignKey("geographies.id", ondelete="CASCADE"), nullable=False)
    source_code = Column(String(20), ForeignKey("energy_sources.source_code"), nullable=False)
    evaluation_date = Column(Date, nullable=False)
    model_name = Column(String(50), nullable=False)
    sample_count = Column(Integer, nullable=False)
    mae_mu = Column(Numeric(10, 3), nullable=False)
    rmse_mu = Column(Numeric(10, 3), nullable=False)
    wape_pct = Column(Numeric(6, 2), nullable=False)
    signed_bias_mu = Column(Numeric(10, 3), nullable=False)
    evaluation_timestamp = Column(DateTime, default=datetime.utcnow)

    geography = relationship("Geography", back_populates="evaluations")
    energy_source = relationship("EnergySource", back_populates="evaluations")

    __table_args__ = (
        UniqueConstraint("geography_id", "source_code", "evaluation_date", "model_name", name="uq_forecast_eval"),
        Index("idx_eval_geo_date", "geography_id", "evaluation_date"),
    )


class IngestionAuditLog(Base):
    __tablename__ = "ingestion_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_name = Column(String(100), nullable=False)
    source_url = Column(String(255), nullable=True)
    ingestion_status = Column(String(30), nullable=False)  # 'SUCCESS', 'PARTIAL', 'FAILED'
    records_processed = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    error_summary = Column(Text, nullable=True)
    execution_time_seconds = Column(Numeric(8, 2), nullable=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)

