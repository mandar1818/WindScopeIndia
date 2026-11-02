"""
Historical Data Coverage Service.
Audits and aggregates actual data coverage across 2020–2026,
strictly distinguishing verified official data, unverified source models, and demonstration baselines.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.generation import GenerationMonthly
from app.models.source_file import SourceFile
from app.models.reconciliation import NationalReconciliation


class CoverageService:
    def __init__(self, db: Session):
        self.db = db

    def get_coverage_inventory(self) -> Dict[str, Any]:
        """
        Builds a comprehensive inventory of monthly coverage across 2020–2026.
        """
        # Query record counts grouped by year, month, dataset_classification
        counts_query = (
            self.db.query(
                GenerationMonthly.year,
                GenerationMonthly.month,
                GenerationMonthly.dataset_classification,
                func.count(GenerationMonthly.id).label("total_records"),
                func.count(func.nullif(GenerationMonthly.generation_mu, None)).label("valid_obs_count"),
                func.count(func.nullif(GenerationMonthly.observation_status != "MISSING_OBSERVATION", False)).label("non_missing_count"),
            )
            .group_by(
                GenerationMonthly.year,
                GenerationMonthly.month,
                GenerationMonthly.dataset_classification,
            )
            .all()
        )

        counts_map: Dict[tuple, Dict[str, int]] = {}
        for row in counts_query:
            key = (row.year, row.month, row.dataset_classification)
            counts_map[key] = {
                "total": row.total_records,
                "valid": row.valid_obs_count,
            }

        # Query source files
        files = self.db.query(SourceFile).all()
        files_by_period: Dict[tuple, List[Dict[str, Any]]] = {}
        for f in files:
            if f.reporting_month:
                key = (f.reporting_year, f.reporting_month)
                if key not in files_by_period:
                    files_by_period[key] = []
                files_by_period[key].append({
                    "id": f.id,
                    "filename": f.filename,
                    "format": f.document_format,
                    "source_org": f.source_org,
                    "status": f.ingestion_status,
                    "sha256": f.file_hash_sha256,
                })

        # Query reconciliations
        reconciliations = self.db.query(NationalReconciliation).all()
        recons_by_period: Dict[tuple, List[str]] = {}
        for r in reconciliations:
            key = (r.reporting_year, r.reporting_month)
            if key not in recons_by_period:
                recons_by_period[key] = []
            recons_by_period[key].append(r.reconciliation_status)

        # Build year-by-year inventory for 2020 to 2026
        inventory: List[Dict[str, Any]] = []
        overall_stats = {
            "verified_official_periods": 0,
            "unverified_source_periods": 0,
            "demonstration_only_periods": 0,
            "total_verified_records": 0,
            "total_unverified_records": 0,
            "total_demonstration_records": 0,
        }

        for yr in range(2020, 2027):
            months_in_year = 12 if yr < 2026 else 1  # 2026 has Jan
            for mo in range(1, months_in_year + 1):
                v_count = counts_map.get((yr, mo, "VERIFIED_OFFICIAL"), {}).get("total", 0)
                u_count = counts_map.get((yr, mo, "OFFICIAL_SOURCE_UNVERIFIED"), {}).get("total", 0)
                d_count = counts_map.get((yr, mo, "DEMONSTRATION"), {}).get("total", 0)

                overall_stats["total_verified_records"] += v_count
                overall_stats["total_unverified_records"] += u_count
                overall_stats["total_demonstration_records"] += d_count

                period_files = files_by_period.get((yr, mo), [])
                period_recons = recons_by_period.get((yr, mo), [])

                if v_count > 0:
                    coverage_status = "VERIFIED_OFFICIAL"
                    overall_stats["verified_official_periods"] += 1
                elif u_count > 0:
                    coverage_status = "OFFICIAL_SOURCE_UNVERIFIED"
                    overall_stats["unverified_source_periods"] += 1
                elif d_count > 0:
                    coverage_status = "DEMONSTRATION_ONLY"
                    overall_stats["demonstration_only_periods"] += 1
                else:
                    coverage_status = "NO_COVERAGE"

                recon_summary = "N/A"
                if period_recons:
                    if all(s in ["MATCHES_VERIFIED_STATE_SUM", "MATCHES_NATIONAL_SUM"] for s in period_recons):
                        recon_summary = "ALL_VERIFIED_MATCH"
                    elif any(s == "NATIONAL_TOTAL_ONLY" for s in period_recons):
                        recon_summary = "NATIONAL_AGGREGATE_ONLY"
                    elif all(s in ["UNVERIFIED_STATE_SUM", "MATCHES_VERIFIED_STATE_SUM"] for s in period_recons):
                        recon_summary = "WITHIN_TOLERANCE_UNVERIFIED"
                    elif any(s == "DISCREPANCY_OUTSIDE_TOLERANCE" for s in period_recons):
                        recon_summary = "DISCREPANCIES_OUTSIDE_TOLERANCE"
                    else:
                        recon_summary = "RECONCILED_WITH_EXPLANATION"

                inventory.append({
                    "year": yr,
                    "month": mo,
                    "period_label": f"{yr}-{mo:02d}",
                    "coverage_status": coverage_status,
                    "verified_records_count": v_count,
                    "unverified_records_count": u_count,
                    "demonstration_records_count": d_count,
                    "source_files": period_files,
                    "reconciliation_summary": recon_summary,
                })

        return {
            "summary": overall_stats,
            "inventory": inventory,
        }

