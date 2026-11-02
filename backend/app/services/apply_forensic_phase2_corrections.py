"""
Forensic Phase 2 Corrections Script.
1. Ensures THERMAL, NUCLEAR, and HYDRO are registered in energy_sources.
2. Creates canonical IN-TOTAL national geography record.
3. Migrates verified official records to IN-TOTAL with full gazette provenance.
4. Standardizes and recalculates all reconciliation records using truthful taxonomy:
   - NATIONAL_TOTAL_ONLY for PDF gazette national aggregate.
   - UNVERIFIED_STATE_SUM and DISCREPANCY_OUTSIDE_TOLERANCE for unverified CSV files.
5. Cleans up test reconciliation rows.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.geography import Geography
from app.models.energy import EnergySource
from app.models.generation import GenerationMonthly
from app.models.source_file import SourceFile
from app.models.reconciliation import NationalReconciliation


def run_corrections():
    db = SessionLocal()
    try:
        print("=== STEP 0: Ensuring EnergySource has THERMAL, NUCLEAR, and HYDRO ===")
        sources_to_ensure = [
            ("THERMAL", "Thermal Power (Coal, Gas, Lignite, Diesel)", False),
            ("NUCLEAR", "Nuclear Power Fleet", False),
            ("HYDRO", "Conventional Hydro Generation (Utility-Scale)", False),
        ]
        for code, name, is_vre in sources_to_ensure:
            existing = db.query(EnergySource).filter(EnergySource.source_code == code).first()
            if not existing:
                es = EnergySource(source_code=code, display_name=name, unit="MU", is_variable_re=is_vre)
                db.add(es)
                print(f"Created EnergySource: {code}")
            else:
                print(f"EnergySource {code} already exists")
        db.commit()

        print("\n=== STEP 1: Ensuring IN-TOTAL National Geography exists ===")
        national_geo = db.query(Geography).filter(Geography.code == "IN-TOTAL").first()
        if not national_geo:
            national_geo = Geography(
                code="IN-TOTAL",
                name="All India (National Aggregate)",
                entity_type="NATIONAL",
                region_code="NR",
                capital="New Delhi",
                latitude=28.6139,
                longitude=77.2090,
                geojson_id="IND",
                is_active=True,
            )
            db.add(national_geo)
            db.commit()
            db.refresh(national_geo)
            print(f"Created IN-TOTAL geography with ID: {national_geo.id}")
        else:
            print(f"Found existing IN-TOTAL geography with ID: {national_geo.id}")

        print("\n=== STEP 2: Moving VERIFIED_OFFICIAL records to IN-TOTAL ===")
        verified_records = (
            db.query(GenerationMonthly)
            .filter(GenerationMonthly.dataset_classification == "VERIFIED_OFFICIAL")
            .all()
        )
        print(f"Found {len(verified_records)} VERIFIED_OFFICIAL records to update")

        table_heading_gazette = "1. SUMMARY-ALL INDIA AN OVERVIEW"
        for r in verified_records:
            r.geography_id = national_geo.id
            r.normalized_geography_code = "IN-TOTAL"
            r.original_state_label = "ALL INDIA"
            r.pdf_page_number = 1
            r.table_heading = table_heading_gazette
            r.original_unit = "GWH"
            r.normalized_unit = "MU"
            r.unit_conversion_applied = "1_GWH_EQUALS_1_MU"
            r.validation_status = "VERIFIED_OFFICIAL"
            r.observation_status = "REPORTED_VALUE"
            print(f"Updated record ID {r.id}: {r.source_code} ({r.generation_mu} MU) mapped to IN-TOTAL (ID {national_geo.id})")

        db.commit()

        print("\n=== STEP 3: Cleaning up leaked test reconciliation records ===")
        deleted_count = db.query(NationalReconciliation).filter(
            NationalReconciliation.reporting_month == 11
        ).delete()
        print(f"Deleted {deleted_count} test reconciliation records (month 11)")
        db.commit()

        print("\n=== STEP 4: Standardizing National Reconciliation Records ===")
        sf_june_csv = db.query(SourceFile).filter(SourceFile.reporting_year == 2024, SourceFile.reporting_month == 6, SourceFile.filename.like("%.csv")).first()
        sf_dec_csv = db.query(SourceFile).filter(SourceFile.reporting_year == 2024, SourceFile.reporting_month == 12, SourceFile.filename.like("%.csv")).first()
        sf_pdf = db.query(SourceFile).filter(SourceFile.reporting_year == 2024, SourceFile.reporting_month == 6, SourceFile.filename.like("%.pdf")).first()

        # June 2024 unverified CSV recalculations
        june_recons = [
            ("WIND", 11448.50, 11448.50, 0.0, 0.0, 36, "UNVERIFIED_STATE_SUM", "Sum of state observations (11,448.50 MU) equals published footer in unverified CSV. Cannot be certified as verified official reconciliation until original state gazettes are cryptographically verified."),
            ("SOLAR", 10000.30, 10124.60, 124.30, 1.243, 36, "DISCREPANCY_OUTSIDE_TOLERANCE", "State sum (10,124.60 MU) exceeds published national total (10,000.30 MU) by +124.30 MU (+1.24%) in unverified CSV."),
            ("SMALL_HYDRO", 1289.40, 1333.50, 44.10, 3.420, 36, "DISCREPANCY_OUTSIDE_TOLERANCE", "State sum (1,333.50 MU) exceeds published national total (1,289.40 MU) by +44.10 MU (+3.42%) in unverified CSV."),
            ("BIOMASS", 1450.30, 1437.80, 12.50, 0.862, 36, "DISCREPANCY_OUTSIDE_TOLERANCE", "State sum (1,437.80 MU) is less than published national total (1,450.30 MU) by -12.50 MU (-0.86%) in unverified CSV."),
            ("OTHER_RE", 114.80, 114.80, 0.0, 0.0, 36, "UNVERIFIED_STATE_SUM", "Sum of state observations (114.80 MU) equals published footer in unverified CSV. Cannot be certified as verified official reconciliation until original state gazettes are cryptographically verified."),
        ]

        if sf_june_csv:
            for sc, pub, st_sum, abs_v, pct_v, st_cnt, stat, expl in june_recons:
                rec = db.query(NationalReconciliation).filter(
                    NationalReconciliation.source_file_id == sf_june_csv.id,
                    NationalReconciliation.source_code == sc,
                    NationalReconciliation.reporting_year == 2024,
                    NationalReconciliation.reporting_month == 6,
                ).first()
                if rec:
                    rec.published_national_total_mu = pub
                    rec.state_sum_mu = st_sum
                    rec.absolute_variance_mu = abs_v
                    rec.percentage_variance = pct_v
                    rec.included_states_count = st_cnt
                    rec.reconciliation_status = stat
                    rec.explanation = expl
                else:
                    rec = NationalReconciliation(
                        source_file_id=sf_june_csv.id,
                        reporting_year=2024,
                        reporting_month=6,
                        source_code=sc,
                        published_national_total_mu=pub,
                        state_sum_mu=st_sum,
                        absolute_variance_mu=abs_v,
                        percentage_variance=pct_v,
                        included_states_count=st_cnt,
                        missing_states_count=0,
                        excluded_records_count=0,
                        reconciliation_status=stat,
                        explanation=expl,
                    )
                    db.add(rec)
                print(f"Updated June 2024 CSV recon: {sc} -> {stat}")

        # Dec 2024 unverified CSV recalculations
        dec_recons = [
            ("WIND", 2106.90, 2106.90, 0.0, 0.0, 36, "UNVERIFIED_STATE_SUM", "Sum of state observations (2,106.90 MU) equals published footer in unverified CSV. Cannot be certified as verified official reconciliation until original state gazettes are cryptographically verified."),
            ("SOLAR", 11840.40, 11391.00, 449.40, 3.796, 36, "DISCREPANCY_OUTSIDE_TOLERANCE", "State sum (11,391.00 MU) is less than published national total (11,840.40 MU) by -449.40 MU (-3.80%) in unverified CSV."),
            ("SMALL_HYDRO", 513.70, 533.20, 19.50, 3.796, 36, "DISCREPANCY_OUTSIDE_TOLERANCE", "State sum (533.20 MU) exceeds published national total (513.70 MU) by +19.50 MU (+3.80%) in unverified CSV."),
            ("BIOMASS", 2443.30, 2405.50, 37.80, 1.547, 36, "DISCREPANCY_OUTSIDE_TOLERANCE", "State sum (2,405.50 MU) is less than published national total (2,443.30 MU) by -37.80 MU (-1.55%) in unverified CSV."),
            ("OTHER_RE", 147.90, 139.90, 8.00, 5.409, 36, "DISCREPANCY_OUTSIDE_TOLERANCE", "State sum (139.90 MU) is less than published national total (147.90 MU) by -8.00 MU (-5.41%) in unverified CSV."),
        ]

        if sf_dec_csv:
            for sc, pub, st_sum, abs_v, pct_v, st_cnt, stat, expl in dec_recons:
                rec = db.query(NationalReconciliation).filter(
                    NationalReconciliation.source_file_id == sf_dec_csv.id,
                    NationalReconciliation.source_code == sc,
                    NationalReconciliation.reporting_year == 2024,
                    NationalReconciliation.reporting_month == 12,
                ).first()
                if rec:
                    rec.published_national_total_mu = pub
                    rec.state_sum_mu = st_sum
                    rec.absolute_variance_mu = abs_v
                    rec.percentage_variance = pct_v
                    rec.included_states_count = st_cnt
                    rec.reconciliation_status = stat
                    rec.explanation = expl
                else:
                    rec = NationalReconciliation(
                        source_file_id=sf_dec_csv.id,
                        reporting_year=2024,
                        reporting_month=12,
                        source_code=sc,
                        published_national_total_mu=pub,
                        state_sum_mu=st_sum,
                        absolute_variance_mu=abs_v,
                        percentage_variance=pct_v,
                        included_states_count=st_cnt,
                        missing_states_count=0,
                        excluded_records_count=0,
                        reconciliation_status=stat,
                        explanation=expl,
                    )
                    db.add(rec)
                print(f"Updated Dec 2024 CSV recon: {sc} -> {stat}")

        # June 2024 Verified Official PDF Gazettes (SourceFile ID 14 or sf_pdf)
        if sf_pdf:
            pdf_recons = [
                ("HYDRO", 14212.67, 0.0, 0.0, 0.0, 0, "NATIONAL_TOTAL_ONLY", "Source document (CEA 18-Column Actual Gazette) reports All-India national totals only. No state-level breakdown was published in this document to reconcile against."),
                ("NUCLEAR", 4217.61, 0.0, 0.0, 0.0, 0, "NATIONAL_TOTAL_ONLY", "Source document (CEA 18-Column Actual Gazette) reports All-India national totals only. No state-level breakdown was published in this document to reconcile against."),
                ("THERMAL", 120865.06, 0.0, 0.0, 0.0, 0, "NATIONAL_TOTAL_ONLY", "Source document (CEA 18-Column Actual Gazette) reports All-India national totals only. No state-level breakdown was published in this document to reconcile against."),
            ]
            for sc, pub, st_sum, abs_v, pct_v, st_cnt, stat, expl in pdf_recons:
                rec = db.query(NationalReconciliation).filter(
                    NationalReconciliation.source_file_id == sf_pdf.id,
                    NationalReconciliation.source_code == sc,
                    NationalReconciliation.reporting_year == 2024,
                    NationalReconciliation.reporting_month == 6,
                ).first()
                if rec:
                    rec.published_national_total_mu = pub
                    rec.state_sum_mu = st_sum
                    rec.absolute_variance_mu = abs_v
                    rec.percentage_variance = pct_v
                    rec.included_states_count = st_cnt
                    rec.reconciliation_status = stat
                    rec.explanation = expl
                else:
                    rec = NationalReconciliation(
                        source_file_id=sf_pdf.id,
                        reporting_year=2024,
                        reporting_month=6,
                        source_code=sc,
                        published_national_total_mu=pub,
                        state_sum_mu=st_sum,
                        absolute_variance_mu=abs_v,
                        percentage_variance=pct_v,
                        included_states_count=st_cnt,
                        missing_states_count=0,
                        excluded_records_count=0,
                        reconciliation_status=stat,
                        explanation=expl,
                    )
                    db.add(rec)
                print(f"Updated June 2024 PDF recon: {sc} -> {stat}")

        db.commit()
        print("\nAll forensic corrections committed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    run_corrections()
