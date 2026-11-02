"""
National Reconciliation Engine & Validation Reporting.
Calculates State Sum, Published National Total, Absolute Variance, and Percentage Variance.
Assigns standardized reconciliation status codes and writes transparent audit manifests.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.reconciliation import NationalReconciliation


RECONCILIATION_STATUSES = {
    "MATCHES_VERIFIED_STATE_SUM",
    "UNVERIFIED_STATE_SUM",
    "INCOMPLETE_GEOGRAPHIC_COVERAGE",
    "FUEL_MAPPING_MISMATCH",
    "UNIT_MISMATCH",
    "DISCREPANCY_OUTSIDE_TOLERANCE",
    "NATIONAL_TOTAL_ONLY",
    "NOT_RECONCILED",
    # Legacy codes for backward compatibility
    "MATCHES_NATIONAL_SUM",
    "RECONCILED_WITH_EXPLANATION",
    "RECONCILIATION_FAILED",
}


def compute_reconciliation(
    published_total: float,
    state_sum: float,
    included_states_count: int,
    missing_states_count: int = 0,
    excluded_records_count: int = 0,
    tolerance_pct: float = 2.0,
    source_explanation: Optional[str] = None,
    dataset_classification: str = "OFFICIAL_SOURCE_UNVERIFIED",
    is_national_only: bool = False,
    fuel_matched: bool = True,
    unit_matched: bool = True,
) -> Dict[str, Any]:
    """
    Computes rigorous mathematical variance between published total and sum of state observations.
    Enforces staged verification: NEVER marks unverified records as MATCHES_VERIFIED_STATE_SUM.
    Separates mathematical variance from source verification and geographic coverage.
    """
    # 1. National Aggregate Only (no state observations published in document)
    if is_national_only or included_states_count == 0:
        return {
            "published_national_total_mu": round(published_total, 3),
            "state_sum_mu": None,
            "absolute_variance_mu": None,
            "percentage_variance": None,
            "included_states_count": 0,
            "missing_states_count": missing_states_count,
            "excluded_records_count": excluded_records_count,
            "reconciliation_status": "NATIONAL_TOTAL_ONLY",
            "mathematical_reconciliation": "NOT_APPLICABLE",
            "source_verification_status": dataset_classification,
            "geographic_coverage": "NATIONAL_AGGREGATE_ONLY",
            "fuel_mapping_validity": "VALID_FUEL_MAPPING" if fuel_matched else "MISMATCH",
            "unit_compatibility": "COMPATIBLE_UNITS" if unit_matched else "MISMATCH",
            "explanation": source_explanation or "Official publication contains All-India national aggregate only. No state-level breakdown was published in this source document to reconcile against.",
        }

    # 2. Incompatible Unit
    if not unit_matched:
        return {
            "published_national_total_mu": round(published_total, 3),
            "state_sum_mu": round(state_sum, 3),
            "absolute_variance_mu": round(abs(published_total - state_sum), 3),
            "percentage_variance": None,
            "included_states_count": included_states_count,
            "missing_states_count": missing_states_count,
            "excluded_records_count": excluded_records_count,
            "reconciliation_status": "UNIT_MISMATCH",
            "mathematical_reconciliation": "INCOMPATIBLE_UNITS",
            "source_verification_status": dataset_classification,
            "geographic_coverage": "PARTIAL_COVERAGE" if included_states_count < 36 else "COMPLETE_36_JURISDICTIONS",
            "fuel_mapping_validity": "VALID_FUEL_MAPPING" if fuel_matched else "MISMATCH",
            "unit_compatibility": "MISMATCH",
            "explanation": "Reported unit in state observations does not match national total unit.",
        }

    # 3. Incompatible Fuel Stream Mapping
    if not fuel_matched:
        return {
            "published_national_total_mu": round(published_total, 3),
            "state_sum_mu": round(state_sum, 3),
            "absolute_variance_mu": round(abs(published_total - state_sum), 3),
            "percentage_variance": None,
            "included_states_count": included_states_count,
            "missing_states_count": missing_states_count,
            "excluded_records_count": excluded_records_count,
            "reconciliation_status": "FUEL_MAPPING_MISMATCH",
            "mathematical_reconciliation": "INCOMPATIBLE_FUELS",
            "source_verification_status": dataset_classification,
            "geographic_coverage": "PARTIAL_COVERAGE" if included_states_count < 36 else "COMPLETE_36_JURISDICTIONS",
            "fuel_mapping_validity": "MISMATCH",
            "unit_compatibility": "COMPATIBLE_UNITS",
            "explanation": "Fuel stream category in state observations does not align with national aggregate classification.",
        }

    variance = round(published_total - state_sum, 3)
    abs_variance = abs(variance)
    pct_variance = round((abs_variance / published_total) * 100.0, 4) if published_total > 0 else 0.0

    coverage_status = "COMPLETE_36_JURISDICTIONS" if included_states_count >= 36 else "PARTIAL_COVERAGE"
    if pct_variance == 0.0:
        math_recon = "EXACT_MATCH"
    elif pct_variance <= tolerance_pct:
        math_recon = "WITHIN_TOLERANCE"
    else:
        math_recon = "OUTSIDE_TOLERANCE"

    # 4. Variance exceeds tolerance threshold
    if pct_variance > tolerance_pct:
        status = "DISCREPANCY_OUTSIDE_TOLERANCE"
        explanation = (
            f"State sum ({state_sum:.2f} MU) differs from published total ({published_total:.2f} MU) "
            f"by {variance:+.2f} MU ({pct_variance:.2f}%), exceeding statutory tolerance threshold ({tolerance_pct}%)."
        )
    # 5. State observations are NOT independently verified (cannot claim verified match)
    elif dataset_classification != "VERIFIED_OFFICIAL":
        status = "UNVERIFIED_STATE_SUM"
        if pct_variance == 0.0:
            explanation = (
                f"State sum ({state_sum:.2f} MU) exactly matches published national footer, "
                f"but observations originate from an unverified dataset ({dataset_classification}). Cannot be certified as verified official reconciliation."
            )
        else:
            explanation = (
                f"State sum ({state_sum:.2f} MU) reconciles with published national footer ({published_total:.2f} MU) "
                f"within {tolerance_pct}% tolerance (variance: {pct_variance:.2f}%, {variance:+.2f} MU), "
                f"but observations originate from an unverified dataset ({dataset_classification}). Cannot be certified as verified official reconciliation."
            )
    # 6. Incomplete geographic coverage (< 36 states and UTs)
    elif included_states_count < 36:
        status = "INCOMPLETE_GEOGRAPHIC_COVERAGE"
        explanation = f"Verified state observations cover only {included_states_count} of 36 required Indian States and UTs (variance: {pct_variance:.2f}%)."
    # 7. Fully reconciled and verified match
    else:
        status = "MATCHES_VERIFIED_STATE_SUM"
        explanation = source_explanation or f"Sum of independently verified official state observations matches published national total within statutory tolerance (variance: {pct_variance:.2f}%)."

    return {
        "published_national_total_mu": round(published_total, 3),
        "state_sum_mu": round(state_sum, 3),
        "absolute_variance_mu": abs_variance,
        "percentage_variance": pct_variance,
        "included_states_count": included_states_count,
        "missing_states_count": missing_states_count,
        "excluded_records_count": excluded_records_count,
        "reconciliation_status": status,
        "mathematical_reconciliation": math_recon,
        "source_verification_status": dataset_classification,
        "geographic_coverage": coverage_status,
        "fuel_mapping_validity": "VALID_FUEL_MAPPING",
        "unit_compatibility": "COMPATIBLE_UNITS",
        "explanation": explanation,
    }


def save_reconciliation_record(
    db: Session,
    source_file_id: int,
    reporting_year: int,
    reporting_month: int,
    source_code: str,
    recon_data: Dict[str, Any],
) -> NationalReconciliation:
    """
    Saves or updates a NationalReconciliation record in the database.
    """
    existing = (
        db.query(NationalReconciliation)
        .filter(
            NationalReconciliation.source_file_id == source_file_id,
            NationalReconciliation.reporting_year == reporting_year,
            NationalReconciliation.reporting_month == reporting_month,
            NationalReconciliation.source_code == source_code,
        )
        .first()
    )

    if existing:
        existing.published_national_total_mu = recon_data["published_national_total_mu"]
        existing.state_sum_mu = recon_data["state_sum_mu"]
        existing.absolute_variance_mu = recon_data["absolute_variance_mu"]
        existing.percentage_variance = recon_data["percentage_variance"]
        existing.included_states_count = recon_data["included_states_count"]
        existing.missing_states_count = recon_data["missing_states_count"]
        existing.excluded_records_count = recon_data["excluded_records_count"]
        existing.reconciliation_status = recon_data["reconciliation_status"]
        existing.mathematical_reconciliation = recon_data.get("mathematical_reconciliation", "NOT_APPLICABLE")
        existing.source_verification_status = recon_data.get("source_verification_status", "OFFICIAL_SOURCE_UNVERIFIED")
        existing.geographic_coverage = recon_data.get("geographic_coverage", "NATIONAL_AGGREGATE_ONLY")
        existing.fuel_mapping_validity = recon_data.get("fuel_mapping_validity", "VALID_FUEL_MAPPING")
        existing.unit_compatibility = recon_data.get("unit_compatibility", "COMPATIBLE_UNITS")
        existing.explanation = recon_data["explanation"]
        recon_obj = existing
    else:
        recon_obj = NationalReconciliation(
            source_file_id=source_file_id,
            reporting_year=reporting_year,
            reporting_month=reporting_month,
            source_code=source_code,
            published_national_total_mu=recon_data["published_national_total_mu"],
            state_sum_mu=recon_data["state_sum_mu"],
            absolute_variance_mu=recon_data["absolute_variance_mu"],
            percentage_variance=recon_data["percentage_variance"],
            included_states_count=recon_data["included_states_count"],
            missing_states_count=recon_data["missing_states_count"],
            excluded_records_count=recon_data["excluded_records_count"],
            reconciliation_status=recon_data["reconciliation_status"],
            mathematical_reconciliation=recon_data.get("mathematical_reconciliation", "NOT_APPLICABLE"),
            source_verification_status=recon_data.get("source_verification_status", "OFFICIAL_SOURCE_UNVERIFIED"),
            geographic_coverage=recon_data.get("geographic_coverage", "NATIONAL_AGGREGATE_ONLY"),
            fuel_mapping_validity=recon_data.get("fuel_mapping_validity", "VALID_FUEL_MAPPING"),
            unit_compatibility=recon_data.get("unit_compatibility", "COMPATIBLE_UNITS"),
            explanation=recon_data["explanation"],
        )
        db.add(recon_obj)

    db.commit()
    db.refresh(recon_obj)
    return recon_obj


def generate_validation_report_file(
    report_data: Dict[str, Any],
    reports_dir: Path,
) -> Path:
    """
    Writes a structured JSON and Markdown validation report to disk.
    """
    reports_dir.mkdir(parents=True, exist_ok=True)
    filename_base = report_data.get("filename", "validation_report").replace(".pdf", "")
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    json_path = reports_dir / f"{filename_base}_{timestamp_str}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, default=str)

    # Write Markdown summary
    md_path = reports_dir / f"{filename_base}_{timestamp_str}.md"
    reconciliations = report_data.get("reconciliations", [])

    recon_rows = []
    for r in reconciliations:
        recon_rows.append(
            f"| {r.get('source_code', 'ALL')} | {r.get('state_sum_mu', 0):.2f} | "
            f"{r.get('published_national_total_mu', 0):.2f} | {r.get('absolute_variance_mu', 0):.2f} | "
            f"{r.get('percentage_variance', 0):.2f}% | `{r.get('reconciliation_status', 'UNKNOWN')}` |"
        )
    recon_table = "\n".join(recon_rows) if recon_rows else "| No reconciliation rows recorded |"

    md_content = f"""# Validation Report: {report_data.get('filename')}

* **Document ID:** {report_data.get('source_file_id')}
* **Source Organization:** {report_data.get('source_org')}
* **Dataset Title:** {report_data.get('dataset_name')}
* **Reporting Period:** {report_data.get('reporting_period')}
* **Extraction Timestamp:** {report_data.get('timestamp')}
* **Parser Version:** {report_data.get('parser_version')}
* **SHA-256 Checksum:** `{report_data.get('sha256_hash')}`
* **Total Records Processed:** {report_data.get('records_processed')}
* **Verified Records Count:** {report_data.get('verified_records_count', 0)}
* **Pending Review Count:** {report_data.get('pending_review_count', 0)}

## National Reconciliation Summary

| Fuel | State Sum (MU) | Published Total (MU) | Abs Variance (MU) | Pct Variance | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
{recon_table}

## Verification Audit Notes
{report_data.get('audit_notes', 'All records audited against official PDF page extractions.')}
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return md_path

