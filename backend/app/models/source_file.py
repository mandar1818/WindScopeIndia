from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class SourceFile(Base):
    __tablename__ = "source_files"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(512), nullable=False)
    file_hash_sha256 = Column(String(64), nullable=False, index=True)
    file_size_bytes = Column(Integer, nullable=False)
    document_format = Column(String(20), nullable=False, default="CSV")  # PDF, CSV, XLS
    publication_date = Column(String(50), nullable=True)                 # Official publication date if stated
    source_org = Column(String(100), nullable=False)
    dataset_title = Column(String(255), nullable=False)
    source_url = Column(String(512), nullable=False)
    reporting_year = Column(Integer, nullable=False, index=True)
    reporting_month = Column(Integer, nullable=True, index=True)
    download_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    parser_version = Column(String(50), nullable=True, default="1.0.0")
    ingestion_status = Column(String(50), nullable=False, default="PENDING")
    records_extracted = Column(Integer, nullable=False, default=0)
    validation_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    monthly_generations = relationship("GenerationMonthly", back_populates="source_file")
    reconciliations = relationship("NationalReconciliation", back_populates="source_file", cascade="all, delete-orphan")
