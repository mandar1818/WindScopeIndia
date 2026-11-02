from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class NationalReconciliation(Base):
    """
    Stores reconciliation calculations comparing state-level aggregated observations
    against the published national total in official source documents.
    """
    __tablename__ = "national_reconciliations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_file_id = Column(Integer, ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False, index=True)
    reporting_year = Column(Integer, nullable=False, index=True)
    reporting_month = Column(Integer, nullable=False, index=True)
    source_code = Column(String(20), ForeignKey("energy_sources.source_code"), nullable=False)
    
    published_national_total_mu = Column(Numeric(12, 3), nullable=False)
    state_sum_mu = Column(Numeric(12, 3), nullable=True)
    absolute_variance_mu = Column(Numeric(12, 3), nullable=True)
    percentage_variance = Column(Numeric(8, 4), nullable=True)
    
    included_states_count = Column(Integer, nullable=False, default=0)
    missing_states_count = Column(Integer, nullable=False, default=0)
    excluded_records_count = Column(Integer, nullable=False, default=0)
    
    # Standardized 8 reconciliation statuses:
    # MATCHES_VERIFIED_STATE_SUM, UNVERIFIED_STATE_SUM, INCOMPLETE_GEOGRAPHIC_COVERAGE,
    # FUEL_MAPPING_MISMATCH, UNIT_MISMATCH, DISCREPANCY_OUTSIDE_TOLERANCE, NATIONAL_TOTAL_ONLY, NOT_RECONCILED
    reconciliation_status = Column(String(50), nullable=False, default="NOT_RECONCILED")
    
    # Separated orthogonal dimensions (never conflate mathematical variance with verification):
    mathematical_reconciliation = Column(String(50), nullable=False, default="NOT_APPLICABLE")
    source_verification_status = Column(String(50), nullable=False, default="OFFICIAL_SOURCE_UNVERIFIED")
    geographic_coverage = Column(String(50), nullable=False, default="NATIONAL_AGGREGATE_ONLY")
    fuel_mapping_validity = Column(String(50), nullable=False, default="VALID_FUEL_MAPPING")
    unit_compatibility = Column(String(50), nullable=False, default="COMPATIBLE_UNITS")
    
    explanation = Column(String(1000), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    source_file = relationship("SourceFile", back_populates="reconciliations")
    energy_source = relationship("EnergySource")

    __table_args__ = (
        Index("idx_reconciliation_period", "reporting_year", "reporting_month"),
        Index("idx_reconciliation_fuel", "source_code", "reporting_year", "reporting_month"),
    )

