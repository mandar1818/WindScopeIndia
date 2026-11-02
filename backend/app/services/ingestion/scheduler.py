"""
WindScope India — Automated Ingestion Scheduler & Freshness Monitor.
Manages idempotent batch ingestion jobs, SHA-256 duplicate prevention,
retry backoff, execution logging to ingestion_audit_logs, and source freshness metrics.
"""
import time
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.source_file import SourceFile
from app.models.forecast import IngestionAuditLog
from app.services.ingestion.adapters.cea_adapter import CEAAdapter
from app.services.ingestion.adapters.npp_adapter import NPPAdapter
from app.services.ingestion.adapters.mnre_adapter import MNREAdapter
from app.services.ingestion.adapters.grid_india_adapter import GridIndiaAdapter
from app.services.ingestion.pdf_archival import calculate_sha256
from app.services.ingestion.capacity_ingestion import parse_and_ingest_capacity_pdf
from app.services.ingestion.pdf_pipeline import run_pdf_ingestion_pipeline


class IngestionScheduler:
    def __init__(self, db: Session):
        self.db = db
        self.adapters = {
            "CEA": CEAAdapter(),
            "NPP": NPPAdapter(),
            "MNRE": MNREAdapter(),
            "GRID_INDIA": GridIndiaAdapter()
        }

    def get_source_freshness(self) -> Dict[str, Any]:
        """
        Calculates source data freshness across all statutory authorities.
        Returns last successful ingestion date, latest reporting month, and lag days.
        """
        latest_file = self.db.query(SourceFile).order_by(
            desc(SourceFile.reporting_year),
            desc(SourceFile.reporting_month)
        ).first()

        last_successful_log = self.db.query(IngestionAuditLog).filter(
            IngestionAuditLog.ingestion_status == "SUCCESS"
        ).order_by(desc(IngestionAuditLog.ingested_at)).first()

        today = date.today()

        if latest_file and latest_file.reporting_year and latest_file.reporting_month:
            latest_period_date = date(latest_file.reporting_year, latest_file.reporting_month, 1)
            # Estimate publication lag: days between period end and today
            lag_days = (today - latest_period_date).days
        else:
            latest_period_date = None
            lag_days = None

        return {
            "latest_reporting_period": f"{latest_file.reporting_year}-{latest_file.reporting_month:02d}" if latest_file and latest_file.reporting_month else "N/A",
            "latest_source_file": latest_file.filename if latest_file else "None",
            "latest_source_org": latest_file.source_org if latest_file else "None",
            "last_successful_ingestion_timestamp": last_successful_log.ingested_at.isoformat() if last_successful_log else None,
            "publication_lag_days": lag_days,
            "freshness_status": "CURRENT" if lag_days and lag_days <= 45 else "STALE"
        }

    def check_duplicate(self, file_path: Path) -> Optional[SourceFile]:
        """
        Calculates SHA-256 and checks if file has already been ingested.
        Guarantees strict idempotency without re-inserting records.
        """
        if not file_path.exists():
            return None
        file_hash = calculate_sha256(file_path)
        return self.db.query(SourceFile).filter(SourceFile.file_hash_sha256 == file_hash).first()

    def run_manual_ingestion(
        self,
        source_key: str,
        file_path: Path,
        reporting_year: int,
        reporting_month: Optional[int] = None,
        max_retries: int = 3,
        backoff_seconds: float = 1.0
    ) -> Dict[str, Any]:
        """
        Executes idempotent document ingestion with exponential retry backoff
        and comprehensive audit log recording.
        """
        start_time = time.time()
        adapter = self.adapters.get(source_key.upper())
        if not adapter:
            return {
                "status": "FAILED",
                "error": f"Unknown source authority: {source_key}. Valid: CEA, NPP, MNRE, GRID_INDIA"
            }

        # 1. Duplicate check via SHA-256
        existing_source = self.check_duplicate(file_path)
        if existing_source and existing_source.ingestion_status == "COMPLETED":
            return {
                "status": "ALREADY_INGESTED",
                "message": f"File {file_path.name} already ingested with SHA-256: {existing_source.file_hash_sha256}",
                "records_extracted": existing_source.records_extracted,
                "ingested_at": existing_source.created_at.isoformat() if existing_source.created_at else None
            }

        # 2. Execution with retry backoff
        attempt = 0
        last_error = None
        result = None

        while attempt < max_retries:
            attempt += 1
            try:
                # Dispatch based on document type
                if source_key.upper() == "NPP" and "capacity" in file_path.name.lower():
                    res = parse_and_ingest_capacity_pdf(
                        db=self.db,
                        pdf_path=file_path,
                        reporting_year=reporting_year,
                        reporting_month=reporting_month or 1,
                        allow_reprocessing=True
                    )
                    elapsed = round(time.time() - start_time, 2)
                    log_entry = IngestionAuditLog(
                        dataset_name=f"NPP Installed Capacity {reporting_year}-{reporting_month:02d}",
                        source_url="https://npp.gov.in/publishedReports",
                        ingestion_status=res["status"],
                        records_processed=res.get("records_count", 0),
                        records_inserted=res.get("records_count", 0),
                        execution_time_seconds=elapsed,
                        ingested_at=datetime.utcnow()
                    )
                    self.db.add(log_entry)
                    self.db.commit()
                    return {
                        "status": res["status"],
                        "records_count": res.get("records_count", 0),
                        "sha256": res.get("sha256"),
                        "execution_time_seconds": elapsed,
                        "attempts": attempt
                    }

                elif source_key.upper() == "CEA" and file_path.suffix.lower() == ".pdf":
                    res = run_pdf_ingestion_pipeline(
                        db=self.db,
                        source_url_or_path=str(file_path),
                        reporting_year=reporting_year,
                        reporting_month=reporting_month or 1,
                        is_remote_url=False,
                        allow_reprocessing=True
                    )
                    elapsed = round(time.time() - start_time, 2)
                    log_entry = IngestionAuditLog(
                        dataset_name=f"CEA Sub-Report 16 {reporting_year}-{reporting_month:02d}",
                        source_url="https://cea.nic.in/",
                        ingestion_status=res["status"],
                        records_processed=res.get("records_count", 0),
                        records_inserted=res.get("records_count", 0),
                        execution_time_seconds=elapsed,
                        ingested_at=datetime.utcnow()
                    )
                    self.db.add(log_entry)
                    self.db.commit()
                    return {
                        "status": res["status"],
                        "records_count": res.get("records_count", 0),
                        "sha256": res.get("sha256"),
                        "execution_time_seconds": elapsed,
                        "attempts": attempt
                    }
                else:
                    # Generic adapter parse
                    extract_res = adapter.parse_file(file_path, reporting_year, reporting_month)
                    elapsed = round(time.time() - start_time, 2)
                    log_entry = IngestionAuditLog(
                        dataset_name=f"{source_key} Extraction {file_path.name}",
                        source_url=f"https://{adapter.allowed_domains[0]}",
                        ingestion_status=extract_res.status,
                        records_processed=len(extract_res.extracted_records),
                        records_inserted=extract_res.accepted_records_count,
                        error_summary="; ".join(extract_res.errors) if extract_res.errors else None,
                        execution_time_seconds=elapsed,
                        ingested_at=datetime.utcnow()
                    )
                    self.db.add(log_entry)
                    self.db.commit()
                    return {
                        "status": extract_res.status,
                        "records_extracted": len(extract_res.extracted_records),
                        "accepted": extract_res.accepted_records_count,
                        "validation_summary": extract_res.validation_summary,
                        "execution_time_seconds": elapsed,
                        "attempts": attempt
                    }

            except Exception as exc:
                last_error = str(exc)
                time.sleep(backoff_seconds * (2 ** (attempt - 1)))

        elapsed = round(time.time() - start_time, 2)
        log_entry = IngestionAuditLog(
            dataset_name=f"{source_key} Failed Extraction {file_path.name}",
            ingestion_status="FAILED",
            error_summary=f"Exhausted {max_retries} attempts: {last_error}",
            execution_time_seconds=elapsed,
            ingested_at=datetime.utcnow()
        )
        self.db.add(log_entry)
        self.db.commit()

        return {
            "status": "FAILED",
            "error": last_error,
            "attempts": attempt,
            "execution_time_seconds": elapsed
        }
