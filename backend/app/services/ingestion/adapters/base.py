"""
WindScope India — Unified Ingestion Framework Base Adapter.
Defines the standard contract for all statutory data source adapters:
Central Electricity Authority (CEA), National Power Portal (NPP),
Ministry of New and Renewable Energy (MNRE), and Grid-India.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field


class IngestionJobMetadata(BaseModel):
    source_org: str = Field(..., description="Sponsoring statutory authority")
    dataset_name: str = Field(..., description="Canonical dataset identifier")
    source_url: str = Field(..., description="Official portal download URL")
    original_filename: str = Field(..., description="Basename of downloaded asset")
    document_format: str = Field(..., description="PDF, CSV, XLSX, JSON")
    reporting_year: int
    reporting_month: Optional[int] = None
    publication_date: Optional[str] = None
    download_timestamp: datetime = Field(default_factory=datetime.utcnow)
    sha256_checksum: str
    file_size_bytes: int
    parser_version: str = "2.0.0"


class ExtractionResult(BaseModel):
    status: str  # SUCCESS, FAILED, PARTIAL, ALREADY_INGESTED
    extracted_records: List[Dict[str, Any]] = []
    accepted_records_count: int = 0
    rejected_records_count: int = 0
    validation_summary: str = ""
    errors: List[str] = []


class BaseSourceAdapter(ABC):
    """Abstract base class for all statutory energy data adapters."""

    def __init__(self, source_org: str, allowed_domains: List[str]):
        self.source_org = source_org
        self.allowed_domains = allowed_domains

    def validate_url_domain(self, url: str) -> bool:
        """Enforces domain whitelisting to prevent unauthorized destinations."""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        # Strip port if present
        domain = domain.split(":")[0]
        return any(domain == ad or domain.endswith("." + ad) for ad in self.allowed_domains)

    @abstractmethod
    def parse_file(self, file_path: Path, reporting_year: int, reporting_month: Optional[int]) -> ExtractionResult:
        """Parses local document into structured observations."""
        pass

