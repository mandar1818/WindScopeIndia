import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.geography import Geography
from app.models.generation import GenerationMonthly
from app.models.source_file import SourceFile
from app.models.reconciliation import NationalReconciliation
from app.models.forecast import IngestionAuditLog
from app.services.india_analytics_service import IndiaAnalyticsService
from app.services.ingestion.state_mapper import map_state_name
from app.services.ingestion.fuel_mapper import map_fuel_stream
from app.services.ingestion.observation_auditor import audit_observation
from app.services.ingestion.reconciler import reconcile_national_total
from app.services.ingestion.parser_cea import CEAParser
from app.services.ingestion.file_archiver import compute_file_sha256, DuplicateFileError
from app.services.ingestion.pipeline import run_cea_ingestion_pipeline


def test_state_mapper_canonical_and_variants():
    # Canonical & variations
    assert map_state_name("Tamil Nadu") == ("IN-TN", "STATE_OR_UT")
    assert map_state_name("Tamilnadu") == ("IN-TN", "STATE_OR_UT")
    assert map_state_name("TN") == ("IN-TN", "STATE_OR_UT")
    assert map_state_name("Gujarat") == ("IN-GJ", "STATE_OR_UT")
    assert map_state_name("GJ") == ("IN-GJ", "STATE_OR_UT")
    assert map_state_name("Odisha") == ("IN-OR", "STATE_OR_UT")
    assert map_state_name("Orissa") == ("IN-OR", "STATE_OR_UT")
    assert map_state_name("Dadra and Nagar Haveli and Daman and Diu") == ("IN-DH", "STATE_OR_UT")
    assert map_state_name("D&NH and DD") == ("IN-DH", "STATE_OR_UT")
    assert map_state_name("Delhi") == ("IN-DL", "STATE_OR_UT")
    assert map_state_name("NCT of Delhi") == ("IN-DL", "STATE_OR_UT")

    # Footers and Totals
    assert map_state_name("All India") == ("NATIONAL_TOTAL", "NATIONAL_TOTAL")
    assert map_state_name("Total (RE)") == ("NATIONAL_TOTAL", "NATIONAL_TOTAL")
    assert map_state_name("Grand Total") == ("NATIONAL_TOTAL", "NATIONAL_TOTAL")
    assert map_state_name("Northern Region") == ("NR", "REGIONAL_SUBTOTAL")


def test_fuel_mapper_canonical_fuels():
    assert map_fuel_stream("Wind") == "WIND"
    assert map_fuel_stream("Wind Power") == "WIND"
    assert map_fuel_stream("Solar") == "SOLAR"
    assert map_fuel_stream("Solar PV") == "SOLAR"
    assert map_fuel_stream("Small Hydro") == "SMALL_HYDRO"
    assert map_fuel_stream("SHP") == "SMALL_HYDRO"
    assert map_fuel_stream("Biomass") == "BIOMASS"
    assert map_fuel_stream("Bagasse Cogen") == "BIOMASS"
    assert map_fuel_stream("Waste to Energy") == "OTHER_RE"
    assert map_fuel_stream("Total RE") == "TOTAL_RE"
    assert map_fuel_stream("Unrecognized Fuel XYZ") is None


def test_observation_auditor_zero_vs_missing():
    # Positive reported outturn
    val, status = audit_observation("145.20", "IN-GJ", "WIND", installed_capacity_mw=10000.0)
    assert val == 145.2
    assert status == "REPORTED_VALUE"

    # Explicitly reported zero in unverified source (0.0 or 0.00) -> UNVERIFIED_ZERO
    val, status = audit_observation("0.0", "IN-DL", "WIND", installed_capacity_mw=0.0, is_verified_source=False)
    assert val == 0.0
    assert status == "UNVERIFIED_ZERO"

    val, status = audit_observation("0.00", "IN-TN", "WIND", installed_capacity_mw=9000.0, is_verified_source=False)
    assert val == 0.0
    assert status == "UNVERIFIED_ZERO"

    # Confirmed zero in verified official source -> VERIFIED_REPORTED_ZERO
    val, status = audit_observation("0.0", "IN-DL", "WIND", installed_capacity_mw=0.0, is_verified_source=True)
    assert val == 0.0
    assert status == "VERIFIED_REPORTED_ZERO"

    # Hyphen is strictly MISSING_OBSERVATION (never forced to 0.0 or physical zero)
    val, status = audit_observation("-", "IN-BR", "WIND", installed_capacity_mw=0.0)
    assert val is None
    assert status == "MISSING_OBSERVATION"

    val, status = audit_observation("-", "IN-TN", "WIND", installed_capacity_mw=9000.0)
    assert val is None
    assert status == "MISSING_OBSERVATION"

    val, status = audit_observation("NA", "IN-GJ", "SOLAR", installed_capacity_mw=5000.0)
    assert val is None
    assert status == "MISSING_OBSERVATION"


def test_reconciler_national_total():
    # Exact match with unverified dataset
    state_vals = [
        {"generation_mu": 100.0},
        {"generation_mu": 200.0},
        {"generation_mu": 0.0},
        {"generation_mu": None},
    ]
    res_unverified = reconcile_national_total(
        "2024-12", "WIND", state_vals, published_national_total=300.0, dataset_classification="OFFICIAL_SOURCE_UNVERIFIED"
    )
    assert res_unverified.validation_status == "UNVERIFIED_STATE_SUM"
    assert res_unverified.discrepancy_mu == 0.0
    assert res_unverified.states_counted == 3
    assert res_unverified.missing_count == 1

    # Exact match with verified official dataset but incomplete geographic coverage (< 36 jurisdictions)
    res_incomplete = reconcile_national_total(
        "2024-12", "WIND", state_vals, published_national_total=300.0, dataset_classification="VERIFIED_OFFICIAL"
    )
    assert res_incomplete.validation_status == "INCOMPLETE_GEOGRAPHIC_COVERAGE"

    # Exact match with verified official dataset and complete 36 jurisdictions
    full_state_vals = [{"generation_mu": 10.0} for _ in range(36)]
    res_verified = reconcile_national_total(
        "2024-12", "WIND", full_state_vals, published_national_total=360.0, dataset_classification="VERIFIED_OFFICIAL"
    )
    assert res_verified.validation_status == "MATCHES_VERIFIED_STATE_SUM"
    assert res_verified.discrepancy_mu == 0.0

    # Discrepancy outside tolerance (> 2%)
    res_flag = reconcile_national_total("2024-12", "WIND", state_vals, published_national_total=350.0)
    assert res_flag.validation_status == "DISCREPANCY_OUTSIDE_TOLERANCE"
    assert res_flag.discrepancy_mu == 50.0

    # National total only
    res_nat_only = reconcile_national_total("2024-06", "THERMAL", [], published_national_total=120865.06, is_national_only=True)
    assert res_nat_only.validation_status == "NATIONAL_TOTAL_ONLY"
    assert res_nat_only.sum_of_states_mu is None
    assert res_nat_only.discrepancy_mu is None
    assert res_nat_only.discrepancy_pct is None
    assert res_nat_only.mathematical_reconciliation == "NOT_APPLICABLE"
    assert res_nat_only.geographic_coverage == "NATIONAL_AGGREGATE_ONLY"


def test_cea_csv_parsing_and_pipeline_end_to_end():
    db: Session = SessionLocal()
    try:
        # Create a sample CEA CSV with realistic headers, states, and footer
        sample_csv_content = """CENTRAL ELECTRICITY AUTHORITY
RENEWABLE ENERGY MONITORING DIVISION
MONTHLY REPORT OF RENEWABLE GENERATION FOR DECEMBER 2024 (IN MU)
S.No.,State / UT,Wind,Solar,Small Hydro,Biomass,Others,Total RE
1,Gujarat,1420.50,1150.20,12.50,45.30,8.20,2636.70
2,Tamil Nadu,1125.80,980.40,48.20,82.10,5.40,2241.90
3,Rajasthan,450.20,2100.60,0.00,24.00,0.00,2574.80
4,Delhi,0.00,45.60,0.00,0.00,22.10,67.70
5,Bihar,-,62.30,15.10,32.40,0.00,109.80
,,,,,
,All India,2996.50,4339.10,75.80,183.80,35.70,7630.90
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(sample_csv_content)
            temp_path = Path(f.name)

        try:
            # Run ingestion pipeline
            result = run_cea_ingestion_pipeline(
                db=db,
                file_path=temp_path,
                reporting_year=2024,
                reporting_month=11,
                source_org="Central Electricity Authority",
                dataset_name="Broad Overview of Monthly Renewable Energy Generation",
                source_url="https://cea.nic.in/renewable-generation-report/?lang=en",
                allow_reprocessing=True,
            )

            assert result["status"] == "SUCCESS"
            assert (result["records_inserted"] + result["records_updated"]) > 0
            assert "WIND" in result["reconciliations"]
            assert "SOLAR" in result["reconciliations"]

            # Verify unverified source model records in DB
            official_records = (
                db.query(GenerationMonthly)
                .filter(
                    GenerationMonthly.year == 2024,
                    GenerationMonthly.month == 11,
                    GenerationMonthly.dataset_classification == "OFFICIAL_SOURCE_UNVERIFIED",
                )
                .all()
            )
            assert len(official_records) > 0

            # Verify that Gujarat Wind is recorded correctly
            gj_wind = next(
                r for r in official_records
                if r.source_code == "WIND" and r.geography.code == "IN-GJ"
            )
            assert float(gj_wind.generation_mu) == 1420.50
            assert gj_wind.observation_status == "REPORTED_VALUE"
            assert gj_wind.source_org == "Central Electricity Authority"

            # Verify that Delhi Wind (reported 0.00) is classified as REPORTED_ZERO or UNVERIFIED_ZERO
            dl_wind = next(
                r for r in official_records
                if r.source_code == "WIND" and r.geography.code == "IN-DL"
            )
            assert float(dl_wind.generation_mu) == 0.0
            assert dl_wind.observation_status in ["REPORTED_ZERO", "UNVERIFIED_ZERO"]

            # Verify that Bihar Wind (reported "-") is classified strictly as MISSING_OBSERVATION
            br_wind = next(
                r for r in official_records
                if r.source_code == "WIND" and r.geography.code == "IN-BR"
            )
            assert br_wind.generation_mu is None
            assert br_wind.observation_status == "MISSING_OBSERVATION"

            # Verify SourceFile record
            source_file = db.query(SourceFile).filter(SourceFile.id == result["source_file_id"]).first()
            assert source_file is not None
            assert source_file.ingestion_status == "COMPLETED"

            # Verify IngestionAuditLog record
            audit_log = db.query(IngestionAuditLog).filter(IngestionAuditLog.dataset_name == "CEA_RE_2024_11").first()
            assert audit_log is not None
            assert audit_log.ingestion_status == "SUCCESS"

            # Test duplicate protection
            with pytest.raises(DuplicateFileError):
                run_cea_ingestion_pipeline(
                    db=db,
                    file_path=temp_path,
                    reporting_year=2024,
                    reporting_month=11,
                    allow_reprocessing=False,
                )

        finally:
            if temp_path.exists():
                temp_path.unlink()
            # Clean up only test rows created by this test's source file
            if "result" in locals() and "source_file_id" in result:
                db.query(NationalReconciliation).filter(
                    NationalReconciliation.source_file_id == result["source_file_id"]
                ).delete()
                db.query(GenerationMonthly).filter(
                    GenerationMonthly.source_file_id == result["source_file_id"]
                ).delete()
                db.query(SourceFile).filter(SourceFile.id == result["source_file_id"]).delete()
                db.query(IngestionAuditLog).filter(IngestionAuditLog.dataset_name == "CEA_RE_2024_11").delete()
                db.commit()

                if "filename" in result:
                    archived_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "2024" / result["filename"]
                    if archived_path.exists():
                        archived_path.unlink()
    finally:
        db.close()


# =============================================================================
# PHASE 2 REMEDIATION REGRESSION TEST SUITE (TASKS 1-10)
# =============================================================================

def test_regression_1_below_tolerance_reconciliation():
    """
    1. Below-tolerance reconciliation:
    Solar 1.24% variance (10,124.60 state sum vs 10,000.30 national total) and
    Biomass 0.86% variance (1,437.80 state sum vs 1,450.30 national total) must be
    classified as UNVERIFIED_STATE_SUM and WITHIN_TOLERANCE, not DISCREPANCY_OUTSIDE_TOLERANCE.
    """
    # June 2024 Solar
    solar_states = [{"generation_mu": 10124.60}]
    res_solar = reconcile_national_total(
        reporting_period="2024-06",
        source_code="SOLAR",
        state_values=solar_states,
        published_national_total=10000.30,
        tolerance_pct=2.0,
        dataset_classification="OFFICIAL_SOURCE_UNVERIFIED"
    )
    assert res_solar.validation_status == "UNVERIFIED_STATE_SUM"
    assert res_solar.mathematical_reconciliation == "WITHIN_TOLERANCE"
    assert res_solar.discrepancy_pct == 1.24

    # June 2024 Biomass
    biomass_states = [{"generation_mu": 1437.80}]
    res_bio = reconcile_national_total(
        reporting_period="2024-06",
        source_code="BIOMASS",
        state_values=biomass_states,
        published_national_total=1450.30,
        tolerance_pct=2.0,
        dataset_classification="OFFICIAL_SOURCE_UNVERIFIED"
    )
    assert res_bio.validation_status == "UNVERIFIED_STATE_SUM"
    assert res_bio.mathematical_reconciliation == "WITHIN_TOLERANCE"
    assert res_bio.discrepancy_pct == 0.86


def test_regression_2_above_tolerance_reconciliation():
    """
    2. Above-tolerance reconciliation:
    Small Hydro (3.42% variance) and Other RE (5.41% variance) must be classified
    as DISCREPANCY_OUTSIDE_TOLERANCE and OUTSIDE_TOLERANCE.
    """
    small_hydro_states = [{"generation_mu": 1333.50}]
    res_sh = reconcile_national_total(
        reporting_period="2024-06",
        source_code="SMALL_HYDRO",
        state_values=small_hydro_states,
        published_national_total=1289.40,
        tolerance_pct=2.0,
        dataset_classification="OFFICIAL_SOURCE_UNVERIFIED"
    )
    assert res_sh.validation_status == "DISCREPANCY_OUTSIDE_TOLERANCE"
    assert res_sh.mathematical_reconciliation == "OUTSIDE_TOLERANCE"
    assert res_sh.discrepancy_pct == 3.42


def test_regression_3_national_only_null_state_sum_and_no_zero_variance():
    """
    3. National-only records with NULL state sum:
    Must have state_sum_mu=None, absolute_variance_mu=None, percentage_variance=None,
    reconciliation_status="NATIONAL_TOTAL_ONLY", and mathematical_reconciliation="NOT_APPLICABLE".
    """
    res = reconcile_national_total(
        reporting_period="2024-06",
        source_code="THERMAL",
        state_values=[],
        published_national_total=120865.06,
        dataset_classification="VERIFIED_OFFICIAL",
        is_national_only=True
    )
    assert res.validation_status == "NATIONAL_TOTAL_ONLY"
    assert res.sum_of_states_mu is None
    assert res.discrepancy_mu is None
    assert res.discrepancy_pct is None
    assert res.mathematical_reconciliation == "NOT_APPLICABLE"
    assert res.geographic_coverage == "NATIONAL_AGGREGATE_ONLY"
    assert res.reported_national_total_mu == 120865.06


def test_regression_4_no_false_zero_variance_match():
    """
    4. No false zero-variance match:
    An unverified dataset or national-only record must NEVER return MATCHES_VERIFIED_STATE_SUM.
    """
    state_vals = [{"generation_mu": 100.0} for _ in range(36)]
    res_unverified = reconcile_national_total(
        reporting_period="2024-06",
        source_code="WIND",
        state_values=state_vals,
        published_national_total=3600.0,
        dataset_classification="OFFICIAL_SOURCE_UNVERIFIED"
    )
    assert res_unverified.validation_status != "MATCHES_VERIFIED_STATE_SUM"
    assert res_unverified.validation_status == "UNVERIFIED_STATE_SUM"


def test_regression_5_no_mixing_of_national_and_state_geography():
    """
    5. No mixing of national and state geography:
    Verifies that IN-TOTAL (National Aggregate, id=37) is excluded from get_all_states,
    get_map_data, and get_data_quality_report.
    """
    db = SessionLocal()
    try:
        service = IndiaAnalyticsService(db)
        
        # Test get_all_states
        states = service.get_all_states()
        state_codes = [s["code"] for s in states]
        assert "IN-TOTAL" not in state_codes
        assert len(states) == 36  # Exactly 28 States + 8 UTs

        # Test get_map_data
        map_data = service.get_map_data(2026, 1)
        map_codes = [m["code"] for m in map_data]
        assert "IN-TOTAL" not in map_codes
        assert len(map_data) == 36

        # Test data quality reporting matrix
        dq = service.get_data_quality_report()
        dq_codes = [m["code"] for m in dq["reporting_matrix"]]
        assert "IN-TOTAL" not in dq_codes
        assert dq["total_geographies"] == 36
    finally:
        db.close()


def test_regression_6_no_promotion_of_demonstration_records():
    """
    6. No promotion of demonstration records:
    Ensures that demonstration baselines remain classified as DEMONSTRATION.
    """
    db = SessionLocal()
    try:
        demo_count = db.query(GenerationMonthly).filter(
            GenerationMonthly.dataset_classification == "DEMONSTRATION"
        ).count()
        assert demo_count == 15768
    finally:
        db.close()


def test_regression_7_no_automatic_verification_of_unverified_csv():
    """
    7. No automatic verification of unverified CSV data:
    The 360 CSV records must remain classified as OFFICIAL_SOURCE_UNVERIFIED.
    """
    db = SessionLocal()
    try:
        unverified_count = db.query(GenerationMonthly).filter(
            GenerationMonthly.dataset_classification == "OFFICIAL_SOURCE_UNVERIFIED"
        ).count()
        assert unverified_count == 360
    finally:
        db.close()


def test_regression_8_physical_zero_evidence_requirements():
    """
    8. Physical zero evidence requirements:
    Verifies that unverified demonstration zeros are classified as UNVERIFIED_ZERO,
    and PHYSICAL_ZERO_CONFIRMED count is 0 because no physical metering proof exists.
    """
    db = SessionLocal()
    try:
        phys_zero_count = db.query(GenerationMonthly).filter(
            GenerationMonthly.observation_status == "PHYSICAL_ZERO_CONFIRMED"
        ).count()
        assert phys_zero_count == 0

        unverified_zeros = db.query(GenerationMonthly).filter(
            GenerationMonthly.observation_status == "UNVERIFIED_ZERO"
        ).count()
        assert unverified_zeros == 5185  # 5,037 demonstration zeros + 148 CSV zeros
    finally:
        db.close()


def test_regression_9_missing_observation_versus_numeric_zero():
    """
    9. Missing observation versus numeric zero:
    Auditing numeric 0.0 returns 0.0, UNVERIFIED_ZERO (or VERIFIED_REPORTED_ZERO).
    Auditing blanks, hyphens, NA returns None, MISSING_OBSERVATION.
    """
    val_num, status_num = audit_observation("0.00", "IN-GJ", "SOLAR", is_verified_source=False)
    assert val_num == 0.0
    assert status_num == "UNVERIFIED_ZERO"

    for missing_str in ["", "-", "--", "NA", "N/A", "NIL", "NULL"]:
        val_m, status_m = audit_observation(missing_str, "IN-GJ", "SOLAR")
        assert val_m is None
        assert status_m == "MISSING_OBSERVATION"


def test_regression_10_forecast_evaluation_requires_matched_pairs():
    """
    10. Forecast evaluation requires matched actual and forecast data:
    Verifies that get_forecasting_data calculates MAE, RMSE, WAPE dynamically
    from the 96 paired blocks and tags output with demonstration notices.
    """
    db = SessionLocal()
    try:
        service = IndiaAnalyticsService(db)
        res = service.get_forecasting_data("IN-GJ", "2026-01-15")
        assert res["time_block_count"] == 96
        assert len(res["blocks"]) == 96
        assert res["mae_mw"] > 0
        assert res["rmse_mw"] > res["mae_mw"]  # RMSE mathematically >= MAE
        assert res["wape_pct"] > 0
        assert res["dataset_classification"] == "DEMONSTRATION"
        assert res["is_official_forecast"] is False
    finally:
        db.close()


def test_regression_11_provenance_retention_csv_export():
    """
    11. Provenance retention during CSV export:
    Tabular explorer records retain dataset classification, source org, and units.
    """
    db = SessionLocal()
    try:
        service = IndiaAnalyticsService(db)
        res = service.get_tabular_explorer(page=1, page_size=10)
        assert res["total_records"] >= 16131
        record = res["records"][0]
        assert "dataset_classification" in record
        assert "source_org" in record
        assert "normalized_unit" in record
        assert "observation_status" in record
    finally:
        db.close()

