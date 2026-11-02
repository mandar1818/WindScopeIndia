"""
PDF Archival & Directory Management.
Preserves official source documents immutably under structured raw directories:
backend/data/raw/cea/{year}/
backend/data/processed/cea/{year}/
backend/data/validation_reports/
backend/data/manifests/
"""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.source_file import SourceFile


class DuplicateDocumentError(Exception):
    pass


def get_base_data_dir() -> Path:
    """Returns the backend data directory."""
    # Location: backend/data
    backend_dir = Path(__file__).resolve().parent.parent.parent.parent
    data_dir = backend_dir / "data"
    return data_dir


def ensure_archive_directories(reporting_year: int) -> Dict[str, Path]:
    """Ensures all archival and reporting directories exist."""
    base_dir = get_base_data_dir()
    dirs = {
        "raw_cea": base_dir / "raw" / "cea" / str(reporting_year),
        "processed_cea": base_dir / "processed" / "cea" / str(reporting_year),
        "validation_reports": base_dir / "validation_reports",
        "manifests": base_dir / "manifests",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def calculate_sha256(file_path: Path) -> str:
    """Calculates SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def archive_official_pdf(
    db: Session,
    source_pdf_path: Path,
    reporting_year: int,
    reporting_month: Optional[int],
    source_org: str,
    dataset_title: str,
    source_url: str,
    publication_date: Optional[str] = None,
    allow_reprocessing: bool = False,
    parser_version: str = "1.0.0",
) -> SourceFile:
    """
    Archives a PDF file into the permanent raw directory and creates or retrieves
    the SourceFile record in the database.
    """
    source_path = Path(source_pdf_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Source PDF does not exist: {source_path}")

    # Compute checksum
    file_hash = calculate_sha256(source_path)
    file_size = source_path.stat().st_size

    # Check for duplicate document in database
    existing_file = db.query(SourceFile).filter(SourceFile.file_hash_sha256 == file_hash).first()
    if existing_file:
        if not allow_reprocessing:
            raise DuplicateDocumentError(
                f"Document already archived with identical SHA-256 hash {file_hash}: "
                f"ID={existing_file.id}, Filename={existing_file.filename}"
            )
        return existing_file

    # Ensure archive directory
    dirs = ensure_archive_directories(reporting_year)
    month_prefix = f"{reporting_month:02d}_" if reporting_month else ""
    archive_filename = f"{reporting_year}_{month_prefix}{source_path.name}"
    dest_path = dirs["raw_cea"] / archive_filename

    # If file exists on disk with same hash, keep it; else copy
    if not dest_path.exists():
        shutil.copy2(source_path, dest_path)

    # Create SourceFile record
    source_file_rec = SourceFile(
        filename=archive_filename,
        file_path=str(dest_path.resolve()),
        file_hash_sha256=file_hash,
        file_size_bytes=file_size,
        document_format="PDF",
        publication_date=publication_date,
        source_org=source_org,
        dataset_title=dataset_title,
        source_url=source_url,
        reporting_year=reporting_year,
        reporting_month=reporting_month,
        download_timestamp=datetime.utcnow(),
        parser_version=parser_version,
        ingestion_status="ARCHIVED",
        records_extracted=0,
    )
    db.add(source_file_rec)
    db.commit()
    db.refresh(source_file_rec)
    return source_file_rec

