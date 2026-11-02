import pytest
from app.services.india_analytics_service import IndiaAnalyticsService
from app.services.weather_service import WeatherService
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestCUFAnalytics:
    """Rigorous mathematical tests for Capacity Utilization Factor (CUF %) calculations."""

    def test_cuf_standard_monthly_calculation(self):
        # 150 MU generation from 1,000 MW capacity in a 30-day month (April: 720 hours)
        # Theoretical MWh = 1,000 MW * 720 h = 720,000 MWh
        # Actual MWh = 150 MU * 1,000 = 150,000 MWh
        # Expected CUF = 150,000 / 720,000 * 100 = 20.833...% -> 20.83%
        res = IndiaAnalyticsService.calculate_cuf(
            generation_mu=150.0,
            capacity_mw=1000.0,
            year=2024,
            month=4
        )
        assert res["status"] == "CALCULATED"
        assert res["cuf_pct"] == 20.83
        assert res["period_hours"] == 720.0
        assert res["is_physically_bounded"] is True

    def test_cuf_leap_year_february_handling(self):
        # February 2024 is a leap year (29 days = 696 hours)
        res_leap = IndiaAnalyticsService.calculate_cuf(
            generation_mu=100.0,
            capacity_mw=1000.0,
            year=2024,
            month=2
        )
        assert res_leap["period_hours"] == 29 * 24.0  # 696 hours
        # CUF = (100 * 1000) / (1000 * 696) * 100 = 14.3678...% -> 14.37%
        assert res_leap["cuf_pct"] == 14.37

        # February 2023 is a non-leap year (28 days = 672 hours)
        res_non_leap = IndiaAnalyticsService.calculate_cuf(
            generation_mu=100.0,
            capacity_mw=1000.0,
            year=2023,
            month=2
        )
        assert res_non_leap["period_hours"] == 28 * 24.0  # 672 hours
        # CUF = (100 * 1000) / (1000 * 672) * 100 = 14.8809...% -> 14.88%
        assert res_non_leap["cuf_pct"] == 14.88

    def test_cuf_zero_generation_distinguished(self):
        # Operational plant with 0.0 reported generation has 0.0% CUF as a distinct reported zero state
        res = IndiaAnalyticsService.calculate_cuf(
            generation_mu=0.0,
            capacity_mw=500.0,
            year=2024,
            month=6
        )
        assert res["status"] == "REPORTED_ZERO_GENERATION"
        assert res["cuf_pct"] == 0.0
        assert res["actual_mwh"] == 0.0
        assert res["is_physically_bounded"] is True

    def test_cuf_missing_generation_handled_safely(self):
        # Missing generation (None) must never produce 0.0%; it returns MISSING_OBSERVATION
        res = IndiaAnalyticsService.calculate_cuf(
            generation_mu=None,
            capacity_mw=500.0,
            year=2024,
            month=6
        )
        assert res["status"] == "MISSING_OBSERVATION"
        assert res["cuf_pct"] is None

    def test_cuf_missing_or_zero_capacity_handled_safely(self):
        # Missing capacity (None) or 0 MW returns INVALID_OR_MISSING_CAPACITY
        res_none = IndiaAnalyticsService.calculate_cuf(
            generation_mu=50.0,
            capacity_mw=None,
            year=2024,
            month=6
        )
        assert res_none["status"] == "INVALID_OR_MISSING_CAPACITY"
        assert res_none["cuf_pct"] is None

        res_zero = IndiaAnalyticsService.calculate_cuf(
            generation_mu=50.0,
            capacity_mw=0.0,
            year=2024,
            month=6
        )
        assert res_zero["status"] == "INVALID_OR_MISSING_CAPACITY"
        assert res_zero["cuf_pct"] is None

    def test_cuf_unclamped_implausible_value_flagged(self):
        # Physically implausible: generation exceeds 100% capacity (e.g. 800 MU from 1,000 MW in 720h = 111.11%)
        # Must NOT be silently clamped to 100.0%
        res = IndiaAnalyticsService.calculate_cuf(
            generation_mu=800.0,
            capacity_mw=1000.0,
            year=2024,
            month=4
        )
        assert res["status"] == "DATA_QUALITY_WARNING_IMPLAUSIBLE"
        assert res["cuf_pct"] == 111.11  # Exact unclamped value preserved!
        assert res["is_physically_bounded"] is False
        assert "exceeds theoretical 100.0%" in res["data_quality_warning"]

    def test_cuf_units_and_reporting_periods(self):
        # Verify units reporting
        res = IndiaAnalyticsService.calculate_cuf(
            generation_mu=100.0,
            capacity_mw=500.0,
            year=2024,
            month=1
        )
        assert res["units"]["generation"] == "MU"
        assert res["units"]["capacity"] == "MW"
        assert res["units"]["period_hours"] == "hours"
        assert res["period_hours"] == 31 * 24.0


class TestRenewableAccountingFourMeasures:
    """Verifies all four distinct CERC & NLDC renewable accounting measures."""

    def test_june_1_2024_all_four_measures(self):
        response = client.get("/api/v1/india/grid/operational-metrics?delivery_date=2024-06-01")
        assert response.status_code == 200
        data = response.json()
        total_row = next(r for r in data["regional_breakdown"] if r["geography_code"] == "IN-TOTAL")

        # Ground figures
        assert total_row["energy_met_mu"] == 5290.0
        assert total_row["solar_generation_mu"] == 398.0
        assert total_row["wind_generation_mu"] == 371.0
        assert total_row["hydro_generation_mu"] == 501.0

        measures = total_row["accounting_measures"]

        # Measure A: Variable Renewable Energy (VRE)
        # (371 + 398) / 5290 * 100 = 769 / 5290 * 100 = 14.54%
        assert measures["measure_a_variable_re"]["numerator_mu"] == 769.0
        assert measures["measure_a_variable_re"]["penetration_pct"] == 14.54

        # Measure B: RE Excluding Large Hydro (Wind + Solar + Biomass & Others)
        # (371 + 398 + 35) / 5290 * 100 = 804 / 5290 * 100 = 15.20%
        assert measures["measure_b_re_excl_large_hydro"]["numerator_mu"] == 804.0
        assert measures["measure_b_re_excl_large_hydro"]["penetration_pct"] == 15.20

        # Measure C: Total RE Including Large Hydro
        # (804 + 501) / 5290 * 100 = 1305 / 5290 * 100 = 24.67%
        assert measures["measure_c_total_re_incl_large_hydro"]["numerator_mu"] == 1305.0
        assert measures["measure_c_total_re_incl_large_hydro"]["penetration_pct"] == 24.67

        # Measure D: Non-Fossil Share of Gross Generation
        # (501 + 145 + 804) / 5706 * 100 = 1450 / 5706 * 100 = 25.41%
        assert measures["measure_d_non_fossil_gross"]["numerator_mu"] == 1450.0
        assert measures["measure_d_non_fossil_gross"]["denominator_gross_generation_mu"] == 5706.0
        assert measures["measure_d_non_fossil_gross"]["share_pct"] == 25.41

    def test_rez_parks_catalog_endpoint(self):
        response = client.get("/api/v1/india/weather/rez-parks")
        assert response.status_code == 200
        parks = response.json()
        assert len(parks) >= 6

        # Check key flagship parks
        park_codes = [p["code"] for p in parks]
        assert "REZ-BHADLA" in park_codes
        assert "REZ-KHAVDA" in park_codes
        assert "REZ-PAVAGADA" in park_codes
        assert "REZ-MUPPANDAL" in park_codes

        bhadla = next(p for p in parks if p["code"] == "REZ-BHADLA")
        assert bhadla["state_code"] == "IN-RJ"
        assert bhadla["capacity_mw"] == 2245.0
        assert 27.0 < bhadla["latitude"] < 28.0
        assert 71.0 < bhadla["longitude"] < 72.0


class TestWeatherGenerationCorrelation:
    """Verifies that weather-generation correlation uses genuinely matched observations and excludes demonstration data."""

    def test_weather_correlation_insufficient_data_status(self):
        # Querying weather for a state where verified generation observations do not match the weather range
        response = client.get("/api/v1/india/weather?state_code=IN-GJ&year=2024")
        assert response.status_code == 200
        data = response.json()

        assert data["correlation_status"] == "INSUFFICIENT_DATA"
        assert data["matched_sample_size_n"] == 0
        assert data["hub_height_wind_correlation"] is None
        assert data["solar_ghi_correlation"] is None
        # Total weather records count must NOT be confused with matched sample size
        assert data["weather_observations_count"] > 0
        assert data["matched_sample_size_n"] != data["weather_observations_count"]

    def test_weather_correlation_excludes_demonstration_generation(self):
        # Even if demonstration generation exists in the DB for Jan 2026, correlation engine must ignore it
        response = client.get("/api/v1/india/weather?state_code=IN-GJ&year=2026")
        assert response.status_code == 200
        data = response.json()

        # Must return INSUFFICIENT_DATA because demonstration data is quarantined
        assert data["correlation_status"] == "INSUFFICIENT_DATA"
        assert data["matched_sample_size_n"] == 0
        assert data["hub_height_wind_correlation"] is None
        assert data["solar_ghi_correlation"] is None

