import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from app.models.source_file import SourceFile


class DuplicateFileError(Exception):
    """Raised when an identical source file has already been archived and ingested."""
    pass


def compute_file_sha256(filepath: Path) -> str:
    """Calculates the SHA-256 hash of a file on disk."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def archive_source_file(
    db: Session,
    source_file_path: Path,
    source_org: str,
    dataset_title: str,
    source_url: str,
    reporting_year: int,
    reporting_month: Optional[int] = None,
    allow_reprocessing: bool = False,
) -> SourceFile:
    """
    Validates, computes SHA-256 checksum, copies file into the raw archive storage,
    and registers an entry in the source_files database table.
    """
    source_file_path = Path(source_file_path)
    if not source_file_path.exists():
        raise FileNotFoundError(f"Source file does not exist: {source_file_path}")

    file_hash = compute_file_sha256(source_file_path)
    file_size = source_file_path.stat().st_size

    # Check for duplicate
    existing = db.query(SourceFile).filter(SourceFile.file_hash_sha256 == file_hash).first()
    if existing:
        if not allow_reprocessing and existing.ingestion_status == "COMPLETED":
            raise DuplicateFileError(
                f"File '{source_file_path.name}' with hash {file_hash[:8]}... "
                f"was already ingested on {existing.created_at} (SourceFile id={existing.id})."
            )
        return existing

    # Define target archive path: backend/data/raw/{year}/
    raw_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw" / str(reporting_year)
    raw_dir.mkdir(parents=True, exist_ok=True)

    archived_filename = f"{reporting_year}_{reporting_month:02d}_{source_file_path.name}" if reporting_month else f"{reporting_year}_{source_file_path.name}"
    target_path = raw_dir / archived_filename

    # Copy raw file untouched to archive directory
    if source_file_path.resolve() != target_path.resolve():
        shutil.copy2(source_file_path, target_path)

    # Persist SourceFile record
    source_record = SourceFile(
        filename=archived_filename,
        file_path=str(target_path.as_posix()),
        file_hash_sha256=file_hash,
        file_size_bytes=file_size,
        source_org=source_org,
        dataset_title=dataset_title,
        source_url=source_url,
        reporting_year=reporting_year,
        reporting_month=reporting_month,
        download_timestamp=datetime.utcnow(),
        ingestion_status="PENDING",
        records_extracted=0,
    )
    db.add(source_record)
    db.commit()
    db.refresh(source_record)
    return source_record

