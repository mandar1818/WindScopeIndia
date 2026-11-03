# WindScope India — API Reference Specification
## Comprehensive OpenAPI REST Reference for WindScope India Platform

**Document Version:** 2.0.0  
**Project:** WindScope India — Renewable Energy Intelligence Platform  
**Target Repository:** `D:\WindScopeIndia`  
**Execution Date:** 03 November 2026  
**Architecture Role:** Lead API Architect & Backend Systems Engineer  

---

## 1. Overview & Base URLs

WindScope India provides a high-throughput, OpenAPI 3.0-compliant RESTful API built with FastAPI. All endpoints return standard JSON payloads (or UTF-8 CSV streams for data exports).

- **Production API Base URL:** `https://windscope-india-backend.onrender.com`
- **Local Development Base URL:** `http://localhost:8000`
- **Interactive Swagger Documentation:** `/docs`
- **Alternative ReDoc Documentation:** `/redoc`
- **OpenAPI Schema Specification:** `/openapi.json`

---

## 2. Authentication & Security Headers

| Authentication Mechanism | Scope | Description |
| :--- | :--- | :--- |
| **Public Access** | Read-only endpoints (`GET`) | Open to browser frontends and analytic clients without authentication. |
| **X-API-KEY Header** | `POST /api/v1/india/ingestion/trigger` | Required administrative token for triggering document ingestion jobs. |

---

## 3. WindScope India Endpoints (`/api/v1/india`)

### 3.1 `GET /api/v1/india/overview`
**Description:** Retrieves all-India headline numbers: Total RE generation (MU), Installed Capacity (GW), fuel source breakdown, top 5 generating states, and YoY growth. Supports dataset switching.

**Parameters:**
- `year` (*integer, optional, default: 2026*): Target evaluation year (2020–2026).
- `month` (*integer, optional, default: 1*): Calendar month (1–12) or null for annual aggregate.
- `dataset_type` (*string, optional*): `'VERIFIED_OFFICIAL'`, `'OFFICIAL_SOURCE_UNVERIFIED'`, `'DEMONSTRATION'`, or null for auto-select.

**Response (200 OK):**
```json
{
  "evaluation_year": 2026,
  "evaluation_month": 1,
  "total_generation_mu": 33402.48,
  "total_capacity_gw": 204.73,
  "yoy_growth_pct": 14.8,
  "dataset_classification": "DEMONSTRATION",
  "is_official_reported": false,
  "source_breakdown": [
    { "source_code": "SOLAR", "name": "Solar", "generation_mu": 12850.2, "percentage": 38.5 },
    { "source_code": "WIND", "name": "Wind", "generation_mu": 10420.5, "percentage": 31.2 },
    { "source_code": "LARGE_HYDRO", "name": "Large Hydro", "generation_mu": 7100.0, "percentage": 21.3 }
  ],
  "top_states": [
    { "state_code": "IN-GJ", "state_name": "Gujarat", "generation_mu": 6120.4, "capacity_mw": 31200.0 },
    { "state_code": "IN-RJ", "state_name": "Rajasthan", "generation_mu": 5840.1, "capacity_mw": 29800.0 }
  ]
}
```

---

### 3.2 `GET /api/v1/india/map-data`
**Description:** Returns state-by-state geo-spatial metrics for the Interactive Choropleth Map across all 28 States and 8 Union Territories.

**Parameters:**
- `metric` (*string, default: "generation"*): `"generation"` (MU) or `"capacity"` (MW).
- `source` (*string, optional*): Filter by fuel: `"SOLAR"`, `"WIND"`, `"LARGE_HYDRO"`, etc.
- `year` (*integer, default: 2026*): Target year.
- `month` (*integer, optional, default: 1*): Target month.
- `dataset_type` (*string, optional*): Dataset classification filter.

**Response (200 OK):** Array of 36 state records (`code`, `name`, `total_generation_mu`, `total_capacity_mw`, `has_wind`, `has_solar`, `dominant_source`).

---

### 3.3 `GET /api/v1/india/states`
**Description:** Returns directory of all 36 Indian States and Union Territories with metadata and regional power committee assignments.

**Parameters:**
- `region_code` (*string, optional*): Filter by region (`NRPC`, `WRPC`, `SRPC`, `ERPC`, `NERPC`).
- `has_wind` (*boolean, optional*): Filter states with commercial wind generation.
- `has_solar` (*boolean, optional*): Filter states with utility solar generation.

---

### 3.4 `GET /api/v1/india/states/{state_code}`
**Description:** Returns detailed single-state operational profile, including monthly generation trends, capacity breakdown, monsoon impact, and historical trajectory.

**Parameters:**
- `state_code` (*path, string, required*): ISO 3166-2 code (e.g. `IN-GJ`, `IN-TN`, `IN-RJ`).
- `year` (*query, integer, default: 2026*): Evaluation year.

---

### 3.5 `GET /api/v1/india/multi-year`
**Description:** Returns multi-year monthly generation time series (2020–2026), compound annual growth rates (CAGR), and seasonal monsoon analysis.

**Parameters:**
- `start_year` (*integer, default: 2020*): Starting year for evaluation window.
- `end_year` (*integer, default: 2026*): Ending year for evaluation window.
- `geo_code` (*string, optional*): Filter by state/UT code (e.g. `IN-GJ`) or null for all-India aggregate.
- `source_code` (*string, optional*): Filter by energy source code (`WIND`, `SOLAR`, `LARGE_HYDRO`, etc.).

---

### 3.6 `GET /api/v1/india/sources/{source_code}`
**Description:** Deep dive into specific generation technology: Solar, Wind, Large Hydro, Small Hydro, Biomass, or Other RE.

**Parameters:**
- `source_code` (*path, string, required*): `WIND`, `SOLAR`, `LARGE_HYDRO`, `SMALL_HYDRO`, `BIOMASS`, `OTHER_RE`.
- `year` (*query, integer, default: 2026*)

---

### 3.7 `GET /api/v1/india/regional`
**Description:** Comparative analytics across India's 5 Regional Power Committees (Northern, Western, Southern, Eastern, North-Eastern).

**Parameters:**
- `year` (*integer, default: 2026*)
- `month` (*integer, optional, default: 1*)

---

### 3.8 `GET /api/v1/india/capacity`
**Description:** Returns verified statutory installed capacity gazettes and the 500 GW by 2030 Non-Fossil Target Progress Tracker.

**Parameters:**
- `effective_date` (*string, optional*): Gazetted effective date (`2026-09-30`, `2024-06-30`) or null for latest.

**Response (200 OK):**
```json
{
  "effective_date": "2026-09-30",
  "publication_date": "19/10/2026",
  "dataset_classification": "VERIFIED_OFFICIAL",
  "summary_gw": {
    "solar_gw": 171.05,
    "wind_gw": 59.20,
    "large_hydro_gw": 52.06,
    "small_hydro_gw": 5.12,
    "biomass_gw": 11.82,
    "clean_re_gw": 299.25,
    "nuclear_gw": 8.78,
    "total_non_fossil_gw": 308.03,
    "total_installed_capacity_gw": 472.18
  },
  "target_500gw_tracker": {
    "target_capacity_gw": 500.0,
    "current_achieved_gw": 308.03,
    "progress_percentage": 61.61,
    "remaining_capacity_gw": 191.97,
    "required_annual_addition_gw": 45.17
  }
}
```

---

### 3.9 `GET /api/v1/india/forecasting`
**Description:** Generates 96 15-minute dispatch blocks day-ahead renewable forecasts with standardized error metrics.

**Parameters:**
- `state_code` (*string, default: "IN-GJ"*): State code.
- `date_str` (*string, default: "2026-01-15"*): Target date (YYYY-MM-DD).
- `model_name` (*string, default: "GRADIENT_BOOSTING_TS"*): Forecast model from registry.
- `source_code` (*string, default: "SOLAR"*): `SOLAR` or `WIND`.

**Response (200 OK):** Includes `metrics` (`mae_mw`, `rmse_mw`, `wape_pct`, `mean_bias_mw`, `sign_convention`: "Forecast - Actual"), `model_metadata`, and 96 dispatch `blocks`.

---

### 3.10 `GET /api/v1/india/weather`
**Description:** Atmospheric observations and correlations from Open-Meteo & IMD climatological models.

**Parameters:**
- `state_code` (*string, default: "IN-GJ"*)
- `year` (*integer, default: 2025*)

**Response (200 OK):** Returns `coordinates`, `average_wind_speed_100m_ms`, `average_solar_ghi_wm2`, `data_provenance`, and 24-hour hourly series.

---

### 3.11 `GET /api/v1/india/grid/status`
**Description:** Operational status of Grid Controller of India Limited telemetry feeds and IEGC operating frequency band.

**Response (200 OK):**
```json
{
  "operational_status": "MONITORED_DEMONSTRATION",
  "telemetry_integration": {
    "status": "BLOCKED",
    "reason": "Enterprise REMC SCADA network boundaries require statutory CERC authorization."
  },
  "frequency_band_hz": {
    "nominal": 50.00,
    "iegc_operating_band": "49.90 - 50.05 Hz",
    "standard": "Indian Electricity Grid Code (IEGC 2023)"
  },
  "grid_regions": [
    { "region_code": "NRPC", "name": "Northern Regional Power Committee", "monitored_states_count": 10 },
    { "region_code": "WRPC", "name": "Western Regional Power Committee", "monitored_states_count": 6 },
    { "region_code": "SRPC", "name": "Southern Regional Power Committee", "monitored_states_count": 8 },
    { "region_code": "ERPC", "name": "Eastern Regional Power Committee", "monitored_states_count": 5 },
    { "region_code": "NERPC", "name": "North-Eastern Regional Power Committee", "monitored_states_count": 7 }
  ]
}
```

---

### 3.12 `GET /api/v1/india/ingestion/freshness`
**Description:** Source data freshness, latest ingested file, and publication lag days across statutory authorities.

**Response (200 OK):**
```json
{
  "latest_reporting_period": "2026-09",
  "latest_source_file": "2026_09_capacity1-2026-09.pdf",
  "latest_source_org": "NPP / CEA",
  "publication_lag_days": 32,
  "freshness_status": "CURRENT"
}
```

---

### 3.13 `POST /api/v1/india/ingestion/trigger`
**Description:** Triggers automated document ingestion pipeline. Protected by administrative API key.

**Headers:**
- `X-API-KEY` (*string, required*): Ingestion administrative key.

**Request Body (JSON):**
```json
{
  "source_key": "CEA",
  "file_path": "backend/data/raw/cea/2024/2024_06_18_col_act-1_2024-JUN.pdf",
  "reporting_year": 2024,
  "reporting_month": 6
}
```

**Status Codes:**
- `200 OK`: Job executed successfully.
- `401 Unauthorized`: Missing or invalid `X-API-KEY`.
- `409 Conflict`: File with identical SHA-256 already ingested.
- `422 Unprocessable Entity`: Invalid request payload.

---

### 3.14 `GET /api/v1/india/source-files`
**Description:** Lists all ingested statutory PDF and CSV documents, SHA-256 checksums, and extraction audit counts.

---

### 3.15 `GET /api/v1/india/reconciliations`
**Description:** Lists national reconciliation records comparing published All-India totals against bottom-up sum-of-states.

---

### 3.16 `GET /api/v1/india/coverage`
**Description:** Multi-year data coverage inventory matrix (2020–2026) across all 36 States/UTs.

---

### 3.17 `GET /api/v1/india/data-quality`
**Description:** Data quality metrics: provenance classifications, observation statuses, and physical zero audit integrity.

---

### 3.18 `GET /api/v1/india/explorer`
**Description:** Paginated, multi-filter tabular data explorer for regulatory reporting and auditing.

**Parameters:**
- `page` (*integer, default: 1*)
- `page_size` (*integer, default: 50, max: 500*)
- `state_code` (*string, optional*)
- `source_code` (*string, optional*)
- `year` (*integer, optional*)
- `dataset_classification` (*string, optional*)

---

### 3.19 `GET /api/v1/india/export/csv`
**Description:** Exports filtered generation outturns as a standardized UTF-8 CSV stream.


