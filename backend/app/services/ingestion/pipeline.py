"""
End-to-End Renewable Energy Data Ingestion Pipeline.
Orchestrates raw file validation, hashing, archiving, tabular parsing,
state and fuel stream canonicalization, observation auditing,
national reconciliation, and persistent database storage.
"""

import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.models.geography import Geography
from app.models.energy import InstalledCapacity
from app.models.generation import GenerationMonthly
from app.models.source_file import SourceFile
from app.models.reconciliation import NationalReconciliation
from app.models.forecast import IngestionAuditLog
from app.services.ingestion.file_archiver import archive_source_file, DuplicateFileError
from app.services.ingestion.parser_cea import CEAParser, CEAParseError


class IngestionPipelineError(Exception):
    pass


def run_cea_ingestion_pipeline(
    db: Session,
    file_path: Path,
    reporting_year: int,
    reporting_month: int,
    source_org: str = "Central Electricity Authority",
    dataset_name: str = "Broad Overview of Monthly Renewable Energy Generation",
    source_url: str = "https://cea.nic.in/renewable-generation-report/?lang=en",
    allow_reprocessing: bool = False,
    dataset_classification: str = "OFFICIAL_SOURCE_UNVERIFIED",
    is_verified: bool = False,
) -> Dict[str, Any]:
    """
    Executes the ingestion pipeline on a CEA monthly report file.
    """
    start_time = time.time()
    file_path = Path(file_path)

    # 1. Archive file & ensure registration in source_files
    source_file = archive_source_file(
        db=db,
        source_file_path=file_path,
        source_org=source_org,
        dataset_title=dataset_name,
        source_url=source_url,
        reporting_year=reporting_year,
        reporting_month=reporting_month,
        allow_reprocessing=allow_reprocessing,
    )

    try:
        # 2. Build capacity lookup table from database
        capacities = (
            db.query(InstalledCapacity, Geography.code)
            .join(Geography, Geography.id == InstalledCapacity.geography_id)
            .filter(InstalledCapacity.effective_date <= f"{reporting_year}-12-31")
            .all()
        )
        cap_lookup: Dict[tuple, float] = {}
        for cap, geo_code in capacities:
            key = (geo_code, cap.source_code)
            cap_lookup[key] = float(cap.capacity_mw)

        # 3. Parse CEA document
        parser = CEAParser(capacity_lookup=cap_lookup)
        parse_result = parser.parse_file(
            filepath=Path(source_file.file_path),
            reporting_year=reporting_year,
            reporting_month=reporting_month,
            source_org=source_org,
            dataset_name=dataset_name,
            source_url=source_url,
        )

        # 4. Map Geography ISO codes to database IDs
        all_geos = db.query(Geography.id, Geography.code, Geography.name).all()
        geo_map = {g.code: g.id for g in all_geos}
        geo_names = {g.code: g.name for g in all_geos}

        # 5. Insert / Upsert into GenerationMonthly
        records_inserted = 0
        records_updated = 0
        now = datetime.utcnow()

        for rec in parse_result["records"]:
            geo_code = rec["state_code"]
            geo_id = geo_map.get(geo_code)
            if not geo_id:
                continue

            state_name = geo_names.get(geo_code, geo_code)
            raw_str = str(rec["generation_mu"]) if rec["generation_mu"] is not None else "-"

            existing_record = (
                db.query(GenerationMonthly)
                .filter(
                    GenerationMonthly.geography_id == geo_id,
                    GenerationMonthly.source_code == rec["source_code"],
                    GenerationMonthly.year == rec["year"],
                    GenerationMonthly.month == rec["month"],
                    GenerationMonthly.dataset_classification == dataset_classification,
                )
                .first()
            )

            obs_status = rec.get("observation_status")
            if not obs_status:
                if rec["generation_mu"] is None:
                    obs_status = "MISSING_OBSERVATION"
                elif rec["generation_mu"] == 0.0:
                    obs_status = "VERIFIED_REPORTED_ZERO" if is_verified else "UNVERIFIED_ZERO"
                else:
                    obs_status = "REPORTED_VALUE"

            val_status = rec.get("validation_status")
            if not val_status:
                val_status = "PENDING_REVIEW" if rec["generation_mu"] and rec["generation_mu"] > 0 else "VALIDATION_FAILED"

            if existing_record:
                existing_record.generation_mu = rec["generation_mu"]
                existing_record.source_file_id = source_file.id
                existing_record.source_org = rec["source_org"]
                existing_record.dataset_name = rec["dataset_name"]
                existing_record.source_url = rec["source_url"]
                existing_record.original_filename = rec["original_filename"]
                existing_record.sha256_checksum = source_file.file_hash_sha256
                existing_record.download_timestamp = source_file.download_timestamp
                existing_record.processing_timestamp = now
                existing_record.extraction_timestamp = now
                existing_record.original_state_label = state_name
                existing_record.normalized_geography_code = geo_code
                existing_record.original_fuel_label = rec["source_code"]
                existing_record.original_reported_value = raw_str
                existing_record.original_unit = "MU"
                existing_record.normalized_unit = "MU"
                existing_record.unit_conversion_applied = rec["unit_conversion_applied"]
                existing_record.table_heading = dataset_name
                existing_record.parser_version = "1.0.0"
                existing_record.validation_status = val_status
                existing_record.observation_status = obs_status
                existing_record.is_verified = is_verified
                records_updated += 1
            else:
                new_record = GenerationMonthly(
                    geography_id=geo_id,
                    source_code=rec["source_code"],
                    year=rec["year"],
                    month=rec["month"],
                    generation_mu=rec["generation_mu"],
                    target_mu=None,
                    capacity_utilization_factor_pct=None,
                    source_provenance=f"CEA Ingestion ({source_file.filename})",
                    is_verified=is_verified,
                    dataset_classification=dataset_classification,
                    source_file_id=source_file.id,
                    source_org=rec["source_org"],
                    dataset_name=rec["dataset_name"],
                    source_url=rec["source_url"],
                    original_filename=rec["original_filename"],
                    sha256_checksum=source_file.file_hash_sha256,
                    download_timestamp=source_file.download_timestamp,
                    processing_timestamp=now,
                    extraction_timestamp=now,
                    parser_version="1.0.0",
                    original_state_label=state_name,
                    normalized_geography_code=geo_code,
                    original_fuel_label=rec["source_code"],
                    original_reported_value=raw_str,
                    original_unit="MU",
                    normalized_unit="MU",
                    table_heading=dataset_name,
                    unit_conversion_applied=rec["unit_conversion_applied"],
                    validation_status=val_status,
                    observation_status=obs_status,
                )
                db.add(new_record)
                records_inserted += 1

        # 6. Save reconciliations into national_reconciliations
        recon_data = parse_result.get("reconciliations", {})
        recon_items = recon_data.values() if isinstance(recon_data, dict) else recon_data

        for recon in recon_items:
            sc = recon.get("source_code")
            pub_tot = recon.get("reported_national_total_mu") if recon.get("reported_national_total_mu") is not None else recon.get("published_total", 0.0)
            if pub_tot is None:
                pub_tot = 0.0
            st_sum = recon.get("sum_of_states_mu") if recon.get("sum_of_states_mu") is not None else recon.get("sum_of_states", 0.0)
            abs_var = recon.get("discrepancy_mu") if recon.get("discrepancy_mu") is not None else recon.get("absolute_variance", 0.0)
            pct_var = recon.get("discrepancy_pct") if recon.get("discrepancy_pct") is not None else recon.get("percentage_variance", 0.0)
            st_count = recon.get("states_counted") if recon.get("states_counted") is not None else recon.get("state_count", 0)
            pct_float = float(pct_var) if pct_var is not None else 0.0
            if st_count == 0:
                status = "NATIONAL_TOTAL_ONLY"
                explanation = "Source document reports national aggregate only. No state-level breakdown in document to reconcile against."
            elif abs(pct_float) > 0.05:
                status = "DISCREPANCY_OUTSIDE_TOLERANCE"
                explanation = f"State sum ({st_sum:.2f} MU) differs from published total ({pub_tot:.2f} MU) by {abs_var:+.2f} MU ({pct_var}%)."
            elif dataset_classification != "VERIFIED_OFFICIAL":
                status = "UNVERIFIED_STATE_SUM"
                explanation = f"State sum matches published national footer, but source document is unverified ({dataset_classification})."
            elif st_count < 36:
                status = "INCOMPLETE_GEOGRAPHIC_COVERAGE"
                explanation = f"Verified state observations cover only {st_count} of 36 required Indian States and UTs."
            else:
                status = "MATCHES_VERIFIED_STATE_SUM"
                explanation = "Sum of independently verified official state observations matches published national total."

            existing_recon = db.query(NationalReconciliation).filter(
                NationalReconciliation.source_file_id == source_file.id,
                NationalReconciliation.source_code == sc,
                NationalReconciliation.reporting_year == reporting_year,
                NationalReconciliation.reporting_month == reporting_month,
            ).first()

            if existing_recon:
                existing_recon.published_national_total_mu = pub_tot
                existing_recon.state_sum_mu = st_sum
                existing_recon.absolute_variance_mu = abs_var
                existing_recon.percentage_variance = pct_var
                existing_recon.included_states_count = st_count
                existing_recon.reconciliation_status = status
                existing_recon.explanation = explanation
            else:
                new_recon = NationalReconciliation(
                    source_file_id=source_file.id,
                    reporting_year=reporting_year,
                    reporting_month=reporting_month,
                    source_code=sc,
                    published_national_total_mu=pub_tot,
                    state_sum_mu=st_sum,
                    absolute_variance_mu=abs_var,
                    percentage_variance=pct_var,
                    included_states_count=st_count,
                    missing_states_count=0,
                    excluded_records_count=0,
                    reconciliation_status=status,
                    explanation=explanation,
                )
                db.add(new_recon)

        # 7. Update SourceFile status
        total_extracted = records_inserted + records_updated
        source_file.records_extracted = total_extracted
        source_file.ingestion_status = "COMPLETED"

        # 8. Record Ingestion Audit Log
        exec_duration = round(time.time() - start_time, 2)
        audit_log = IngestionAuditLog(
            dataset_name=f"CEA_RE_{reporting_year}_{reporting_month:02d}",
            source_url=source_url,
            ingestion_status="SUCCESS",
            records_processed=len(parse_result["records"]),
            records_inserted=records_inserted,
            records_updated=records_updated,
            error_summary=json.dumps({
                "reconciliations": parse_result["reconciliations"],
                "national_totals": parse_result["national_totals_found"],
            }),
            execution_time_seconds=exec_duration,
            ingested_at=now,
        )
        db.add(audit_log)
        db.commit()

        return {
            "status": "SUCCESS",
            "source_file_id": source_file.id,
            "filename": source_file.filename,
            "reporting_period": f"{reporting_year}-{reporting_month:02d}",
            "records_processed": len(parse_result["records"]),
            "records_inserted": records_inserted,
            "records_updated": records_updated,
            "reconciliations": parse_result["reconciliations"],
            "national_totals": parse_result["national_totals_found"],
            "execution_time_seconds": exec_duration,
        }

    except Exception as e:
        db.rollback()
        source_file.ingestion_status = "FAILED"
        db.commit()
        raise IngestionPipelineError(f"Ingestion pipeline failed for {file_path.name}: {str(e)}") from e
