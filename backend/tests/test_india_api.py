import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_india_overview_endpoint():
    response = client.get("/api/v1/india/overview?year=2026&month=1")
    assert response.status_code == 200
    data = response.json()
    assert data["evaluation_year"] == 2026
    assert data["evaluation_month"] == 1
    assert data["total_generation_mu"] > 0
    assert data["total_capacity_gw"] > 100.0
    assert len(data["source_breakdown"]) == 6
    assert len(data["top_states"]) == 5
    assert data["top_states"][0]["generation_mu"] > 0


def test_india_map_data_endpoint():
    response = client.get("/api/v1/india/map-data?metric=generation&year=2026&month=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 36  # 28 States + 8 UTs
    first = data[0]
    assert "code" in first
    assert "name" in first
    assert "total_generation_mu" in first
    assert "total_capacity_mw" in first
    assert "has_wind" in first


def test_india_states_directory_and_filter():
    # All 36
    res_all = client.get("/api/v1/india/states")
    assert res_all.status_code == 200
    all_states = res_all.json()
    assert len(all_states) == 36

    # Verify 28 States and 8 Union Territories
    states = [s for s in all_states if s["entity_type"] == "STATE"]
    uts = [s for s in all_states if s["entity_type"] == "UNION_TERRITORY"]
    assert len(states) == 28
    assert len(uts) == 8

    # Schema integrity check
    for item in all_states:
        assert "code" in item
        assert "name" in item
        assert "entity_type" in item
        assert "region_code" in item
        assert "capital" in item
        assert "total_capacity_mw" in item
        assert "total_re_capacity_mw" in item
        assert "wind_capacity_mw" in item
        assert "solar_capacity_mw" in item
        assert "has_wind" in item
        assert isinstance(item["has_wind"], bool)
        assert item["total_capacity_mw"] >= 0.0

    # Only wind states
    res_wind = client.get("/api/v1/india/states?has_wind=true")
    assert res_wind.status_code == 200
    wind_states = res_wind.json()
    wind_codes = [s["code"] for s in wind_states]
    assert "IN-GJ" in wind_codes
    assert "IN-TN" in wind_codes
    assert "IN-RJ" in wind_codes
    # Non-wind states must strictly NOT be in wind states list
    assert "IN-BR" not in wind_codes  # Bihar has zero wind
    assert "IN-AS" not in wind_codes  # Assam has zero wind


def test_india_state_profile_integrity():
    # Test Gujarat (High Wind + Solar)
    res_gj = client.get("/api/v1/india/states/IN-GJ")
    assert res_gj.status_code == 200
    data_gj = res_gj.json()
    assert data_gj["has_wind"] is True
    assert data_gj["capacity_breakdown"]["WIND"] > 10000.0
    assert len(data_gj["monthly_series"]) > 0

    # Test Bihar (Zero Wind, Solar & Biomass only)
    res_br = client.get("/api/v1/india/states/IN-BR")
    assert res_br.status_code == 200
    data_br = res_br.json()
    assert data_br["has_wind"] is False
    assert data_br["capacity_breakdown"]["WIND"] == 0.0


def test_india_multi_year_trends():
    response = client.get("/api/v1/india/multi-year?start_year=2020&end_year=2026")
    assert response.status_code == 200
    data = response.json()
    assert len(data["timeline"]) == 7  # 2020 to 2026
    years = [t["year"] for t in data["timeline"]]
    assert 2020 in years
    assert 2025 in years
    assert 2026 in years


def test_india_source_analytics():
    response = client.get("/api/v1/india/sources/WIND")
    assert response.status_code == 200
    data = response.json()
    assert data["source_code"] == "WIND"
    assert len(data["state_leaderboard"]) > 0
    assert len(data["seasonality_curve"]) == 12


def test_india_regional_comparison():
    response = client.get("/api/v1/india/regional?year=2025")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5  # NR, WR, SR, ER, NER
    regions = [r["region_code"] for r in data]
    assert "WR" in regions
    assert "SR" in regions
    assert "NR" in regions


def test_india_forecasting_blocks_and_metrics():
    response = client.get("/api/v1/india/forecasting?state_code=IN-GJ&date_str=2026-01-15")
    assert response.status_code == 200
    data = response.json()
    assert data["time_block_count"] == 96  # 96 15-minute blocks
    assert data["mae_mw"] >= 0.0
    assert data["rmse_mw"] >= data["mae_mw"]
    assert data["wape_pct"] >= 0.0
    assert len(data["blocks"]) == 96


def test_india_data_quality_report():
    response = client.get("/api/v1/india/data-quality")
    assert response.status_code == 200
    data = response.json()
    assert data["total_geographies"] == 36
    assert data["verified_geographies"] == 36
    assert len(data["reporting_matrix"]) == 36


def test_india_csv_export():
    response = client.get("/api/v1/india/export/csv?year=2025")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment; filename=" in response.headers["content-disposition"]
    lines = response.text.strip().split("\n")
    assert len(lines) > 10  # Header + rows
    assert "State Code,State Name,Grid Region" in lines[0]


def test_india_overview_dataset_classification_official():
    # Query 2024-06 where CEA unverified source model data is ingested
    response = client.get("/api/v1/india/overview?year=2024&month=6&dataset_type=OFFICIAL")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_classification"] == "OFFICIAL_SOURCE_UNVERIFIED"
    assert data["is_official_reported"] is False
    assert data["is_official_source_unverified"] is True
    assert data["total_generation_mu"] > 10000.0  # June is high monsoon generation month
    assert "CEA Unverified Source Model" in data["statutory_source"]


def test_india_source_files_endpoint():
    response = client.get("/api/v1/india/source-files")
    assert response.status_code == 200
    files = response.json()
    assert len(files) >= 2  # June 2024 and Dec 2024
    for f in files:
        assert f["ingestion_status"] in ["UNVERIFIED_SOURCE", "COMPLETED", "SUCCESS"]
        assert len(f["file_hash_sha256"]) == 64
        assert f["records_extracted"] >= 0


def test_india_explorer_dataset_filter():
    response = client.get("/api/v1/india/explorer?dataset_classification=OFFICIAL_SOURCE_UNVERIFIED&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] >= 360
    assert len(data["records"]) == 10
    for r in data["records"]:
        assert r["dataset_classification"] == "OFFICIAL_SOURCE_UNVERIFIED"
        assert "Central Electricity Authority" in r["source_org"]
        assert r["observation_status"] in ["REPORTED_VALUE", "REPORTED_ZERO", "UNVERIFIED_ZERO", "VERIFIED_REPORTED_ZERO", "MISSING_OBSERVATION", "NOT_APPLICABLE"]


def test_india_reconciliations_endpoint():
    response = client.get("/api/v1/india/reconciliations")
    assert response.status_code == 200
    recons = response.json()
    assert len(recons) >= 10
    for r in recons:
        assert "published_national_total_mu" in r
        assert "state_sum_mu" in r
        assert "reconciliation_status" in r
        assert "mathematical_reconciliation" in r
        assert "source_verification_status" in r
        assert "geographic_coverage" in r
        assert r["reconciliation_status"] in [
            "MATCHES_VERIFIED_STATE_SUM",
            "UNVERIFIED_STATE_SUM",
            "INCOMPLETE_GEOGRAPHIC_COVERAGE",
            "FUEL_MAPPING_MISMATCH",
            "UNIT_MISMATCH",
            "DISCREPANCY_OUTSIDE_TOLERANCE",
            "NATIONAL_TOTAL_ONLY",
            "NOT_RECONCILED",
            "MATCHES_NATIONAL_SUM",
            "RECONCILED_WITH_EXPLANATION",
            "RECONCILIATION_FAILED",
        ]


def test_india_coverage_endpoint():
    response = client.get("/api/v1/india/coverage")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "inventory" in data
    assert len(data["inventory"]) >= 73  # 2020-2026 months
    assert data["summary"]["total_demonstration_records"] >= 15000


def test_india_capacity_endpoint():
    # 1. Test default latest capacity report (September 30, 2026)
    response_default = client.get("/api/v1/india/capacity")
    assert response_default.status_code == 200
    data_default = response_default.json()
    assert data_default["effective_date"] == "2026-09-30"
    assert data_default["publication_date"] == "19/10/2026"
    assert data_default["is_verified_official"] is True
    assert data_default["dataset_classification"] == "VERIFIED_OFFICIAL"
    assert "summary_gw" in data_default
    assert data_default["summary_gw"]["solar_gw"] == 171.05
    assert data_default["summary_gw"]["wind_gw"] == 59.20
    assert data_default["summary_gw"]["large_hydro_gw"] == 52.06
    assert data_default["summary_gw"]["clean_re_gw"] == 299.25
    assert data_default["summary_gw"]["nuclear_gw"] == 8.78
    assert data_default["summary_gw"]["total_non_fossil_gw"] == 308.03
    assert "target_500gw_tracker" in data_default
    assert data_default["target_500gw_tracker"]["target_capacity_gw"] == 500.0
    assert data_default["target_500gw_tracker"]["current_achieved_gw"] == 308.03
    assert data_default["target_500gw_tracker"]["progress_percentage"] == 61.61
    assert data_default["target_500gw_tracker"]["remaining_capacity_gw"] == 191.97
    assert data_default["target_500gw_tracker"]["years_remaining"] == 4.25
    assert data_default["target_500gw_tracker"]["required_annual_addition_gw"] == 45.17

    # 2. Test explicit historical capacity report (June 30, 2024)
    response_2024 = client.get("/api/v1/india/capacity?effective_date=2024-06-30")
    assert response_2024.status_code == 200
    data_2024 = response_2024.json()
    assert data_2024["effective_date"] == "2024-06-30"
    assert data_2024["publication_date"] == "18/07/2024"
    assert data_2024["is_verified_official"] is True
    assert data_2024["dataset_classification"] == "VERIFIED_OFFICIAL"
    assert "summary_gw" in data_2024
    assert data_2024["summary_gw"]["solar_gw"] == 85.47
    assert data_2024["summary_gw"]["wind_gw"] == 46.66
    assert data_2024["summary_gw"]["clean_re_gw"] == 195.01
    assert data_2024["summary_gw"]["nuclear_gw"] == 8.18
    assert data_2024["summary_gw"]["total_non_fossil_gw"] == 203.19
    assert data_2024["target_500gw_tracker"]["target_capacity_gw"] == 500.0
    assert data_2024["target_500gw_tracker"]["progress_percentage"] == 40.64
    assert len(data_2024["historical_trajectory"]) > 0


def test_india_weather_endpoint():
    response = client.get("/api/v1/india/weather?state_code=IN-GJ&year=2025")
    assert response.status_code == 200
    data = response.json()
    assert data["state_code"] == "IN-GJ"
    assert data["year"] == 2025
    assert "IMD" in data["data_provenance"] or "Open-Meteo" in data["data_provenance"]
    assert "coordinates" in data
    assert "series" in data
    assert len(data["series"]) == 24  # 24 hourly intervals
    assert data["average_wind_speed_100m_ms"] > 0


def test_india_forecasting_engine_endpoint():
    response = client.get("/api/v1/india/forecasting?state_code=IN-TN&date_str=2026-01-15&model_name=GRADIENT_BOOSTING_TS&source_code=WIND")
    assert response.status_code == 200
    data = response.json()
    assert data["state_code"] == "IN-TN"
    assert "Gradient" in data["model_metadata"]["name"]
    assert "metrics" in data
    assert "mae_mw" in data["metrics"]
    assert "rmse_mw" in data["metrics"]
    assert "wape_pct" in data["metrics"]
    assert "mean_bias_mw" in data["metrics"]
    assert "Forecast - Actual" in data["metrics"]["sign_convention"]
    assert len(data["blocks"]) == 96


def test_india_grid_status_endpoint():
    response = client.get("/api/v1/india/grid/status")
    assert response.status_code == 200
    data = response.json()
    assert "operational_status" in data
    assert data["frequency_band_hz"]["iegc_operating_band"] == "49.90 - 50.05 Hz"
    assert "grid_regions" in data
    assert len(data["grid_regions"]) == 5
    assert "database_daily_operational_count" in data
    assert data["database_daily_operational_count"] >= 18


def test_india_grid_operational_metrics_endpoint():
    response = client.get("/api/v1/india/grid/operational-metrics?delivery_date=2024-06-01")
    assert response.status_code == 200
    data = response.json()
    assert data["delivery_date"] == "2024-06-01"
    assert data["records_count"] == 6
    assert "regional_breakdown" in data
    for item in data["regional_breakdown"]:
        assert item["energy_met_mu"] > 0
        assert item["re_generation_mu"] >= 0
        assert item["re_penetration_pct"] >= 0
        assert item["data_classification"] == "VERIFIED_OFFICIAL"

    # Verify All-India TOTAL row (Extracted from official NLDC PSP Table A)
    total_row = next(r for r in data["regional_breakdown"] if r["geography_code"] == "IN-TOTAL")
    assert total_row["energy_met_mu"] == 5290.0
    assert total_row["solar_generation_mu"] == 398.0
    assert total_row["wind_generation_mu"] == 371.0
    assert total_row["hydro_generation_mu"] == 501.0
    assert total_row["re_generation_excl_hydro_mu"] == 769.0
    assert total_row["re_penetration_excl_hydro_pct"] == 14.54
    assert total_row["re_generation_incl_hydro_mu"] == 1270.0
    assert total_row["re_penetration_incl_hydro_pct"] == 24.01
    assert "accounting_measures" in total_row
    measures = total_row["accounting_measures"]
    assert measures["measure_a_variable_re"]["penetration_pct"] == 14.54
    assert measures["measure_b_re_excl_large_hydro"]["penetration_pct"] == 15.20
    assert measures["measure_c_total_re_incl_large_hydro"]["penetration_pct"] == 24.67
    assert measures["measure_d_non_fossil_gross"]["share_pct"] == 25.41
    assert measures["measure_3_non_fossil"]["share_pct"] == 25.41

    # Verify ER and NER wind are accurately classified as NOT_REPORTED_IN_SOURCE
    er_row = next(r for r in data["regional_breakdown"] if r["geography_code"] == "IN-ER")
    assert er_row["wind_generation_mu"] is None
    assert er_row["wind_status"] == "NOT_REPORTED_IN_SOURCE"

    ner_row = next(r for r in data["regional_breakdown"] if r["geography_code"] == "IN-NER")
    assert ner_row["wind_generation_mu"] is None
    assert ner_row["wind_status"] == "NOT_REPORTED_IN_SOURCE"


def test_india_ingestion_freshness_endpoint():
    response = client.get("/api/v1/india/ingestion/freshness")
    assert response.status_code == 200
    data = response.json()
    assert "latest_source_file" in data
    assert "publication_lag_days" in data
    assert "freshness_status" in data


def test_india_ingestion_trigger_security():
    payload = {"source_key": "CEA", "file_path": "dummy.pdf", "reporting_year": 2024}
    # Unauthorized request without key rejected with 401
    resp_unauth = client.post("/api/v1/india/ingestion/trigger", json=payload)
    assert resp_unauth.status_code == 401

    # Invalid key rejected with 401
    resp_bad = client.post("/api/v1/india/ingestion/trigger", json=payload, headers={"X-API-KEY": "wrong-key"})
    assert resp_bad.status_code == 401




