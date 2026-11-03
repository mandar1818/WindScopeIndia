# WindScope India — Final Master Baseline Audit

**Document Reference:** `WINDSCOPE_INDIA_FINAL_BASELINE_AUDIT.md`  
**Date:** November 1, 2026  
**Project:** WindScope India — Renewable Energy Intelligence Platform  
**Primary Working Directory:** `D:\WindScopeIndia`  
**Junction Workspace Mapping:** `D:\WindScopeUK` $\rightarrow$ `D:\WindScopeIndia`  
**Pre-Rename Backup Location:** `D:\WindScopeIndia_backup_pre_rename`  
**Git Remote:** `https://github.com/mandar1818/WindScope_UK` (Decoupled preservation)  

---

## Executive Summary

This document establishes the verified forensic baseline of the **WindScope India** project prior to executing the data model separation, Grid-India ingestion expansion, weather data expansion, forecasting engine refinement, database production certification, and UI/UX modernization.

Every metric, record count, and system check documented here has been independently executed and verified directly against the live filesystem, SQLite database (`backend/windscope_india.db`), Alembic migration log, Pytest test runner, Vitest runner, and TypeScript build pipeline.

---

## 1. Project Structure & Directory State

### 1.1 Directory Structure & Physical Disk Verification
* **Physical Target Directory:** `D:\WindScopeIndia`
  * Successfully initialized and populated with all backend, frontend, configuration, data files, and documentation.
  * Virtual environment linked: `D:\WindScopeIndia\backend\.venv` (Python 3.12.10 x64).
  * Frontend dependencies linked: `D:\WindScopeIndia\frontend\node_modules` (Vite 5.4.21, React 18.2.0, Tailwind CSS).
* **Workspace Junction:** `D:\WindScopeUK` $\rightarrow$ `D:\WindScopeIndia`
  * An NTFS directory junction redirects any runtime tools, IDE instances, or scripts targeting `D:\WindScopeUK` to `D:\WindScopeIndia` without path errors.
* **Pre-Rename Backup:**
  * Created at `D:\WindScopeIndia_backup_pre_rename`.
  * Verified to contain 20 files, 4 main directories (backend, frontend, scratch_downloads, docs), 10.83 MB SQLite production database (`windscope_india.db`), and full historical provenance audits.

### 1.2 Git Repository State
* **Working Tree:**
  * Active development files, Alembic migrations, and data verification suites in place.
  * Zero unauthorized pushes or remote modifications (strict adherence to Rule 5: no remote git pushes).
  * Repository name preserved as `WindScope_UK` to prevent breaking existing remote bindings and benchmark deployments.
  * WindScope UK January 2026 benchmark preserved intact in `frontend/src/pages/uk/` and `backend/tests/test_api_routes.py`.

---

## 2. Database State & Inventory

### 2.1 Storage & Schema Overview
* **Database File:** `backend/windscope_india.db`
* **File Size:** 10,833,920 bytes (~10.83 MB)
* **Active Schema Engine:** SQLite (PostgreSQL-compatible dialect & type definitions)
* **Alembic Revisions Applied:**
  * Revision `af8f7710238a` (Initial schema & core tables)
  * Revision `b12984cf5102` (Weather observations expansion fields)

### 2.2 Table-by-Table Record Count
| Table Name | Row Count | Primary Purpose | Current Integrity Status |
| :--- | :--- | :--- | :--- |
| `generation_monthly` | 16,134 | Monthly generation by state & fuel (2020–2026) | Verified official + Demonstration historicals |
| `weather_observations` | 6,048 | Hourly meteorological records across 36 State/UT centroids | ERA5 Reanalysis (June 1–7, 2024) |
| `installed_capacity` | 1,528 | State/Fuel capacity snapshots (2020–2026) | CEA official published benchmarks |
| `generation_15min_blocks` | 576 | Intraday 96-block generation profiles | Demonstration SCADA profiles |
| `generation_daily` | 376 | Daily regional & state generation | 66 official Grid-India PSP records + historical |
| `geographies` | 42 | National (`IN-TOTAL`), 5 Regions, 28 States, 8 UTs | Fully canonical ISO/Census mapping |
| `energy_sources` | 10 | Generation fuels + DEMAND_MET (to be decoupled) | Requires ontological correction |
| `source_files` | 11 | Ingested PDF & CSV source files with SHA-256 | 8 CEA + 3 NLDC PSP files |
| `ingestion_audit_logs` | 16 | Pipeline audit logs & integrity traces | Audit trail maintained |
| `national_reconciliations` | 10 | Reconciliation of state sums against national totals | 6 unverified sums, 4 tolerance variances |
| `regions` | 5 | Northern, Western, Southern, Eastern, North Eastern | Verified grid hierarchy |
| `alembic_version` | 1 | Migration head tracker | Current: `b12984cf5102` |
| `forecast_records` | 0 | Production forecast outputs (populated via engine) | Ready for engine execution |
| `forecast_evaluations` | 0 | Evaluation error metrics | Ready for evaluation runs |

---

## 3. Data Integrity & Classification Breakdown

### 3.1 Monthly Generation (`generation_monthly`)
* Total Records: **16,134**
* By Dataset Classification:
  * `DEMONSTRATION`: **15,768** records (97.73%) — Historical synthetic baselines clearly tagged to prevent false claims of official provenance.
  * `OFFICIAL_SOURCE_UNVERIFIED`: **360** records (2.23%) — Extracted from CEA monthly RE CSV files requiring primary PDF collation.
  * `VERIFIED_OFFICIAL`: **6** records (0.04%) — Fully cross-verified against primary CEA Sub-Report 1 and Sub-Report 16 PDFs.
* By Observation Status:
  * `REPORTED_VALUE`: **10,949** records (67.86%)
  * `UNVERIFIED_ZERO`: **5,185** records (32.14%) — Explicitly separated from true reported physical zeros.
* By Energy Source:
  * `SOLAR`: 2,700 records (766,484.78 MU)
  * `LARGE_HYDRO`: 2,628 records (645,878.96 MU)
  * `WIND`: 2,700 records (458,748.13 MU)
  * `THERMAL`: 2 records (238,865.59 MU)
  * `BIOMASS`: 2,700 records (204,146.01 MU)
  * `SMALL_HYDRO`: 2,700 records (66,979.15 MU)
  * `HYDRO`: 2 records (32,875.18 MU)
  * `OTHER_RE`: 2,700 records (14,376.47 MU)
  * `NUCLEAR`: 2 records (9,738.40 MU)

### 3.2 Installed Capacity (`installed_capacity`)
* Total Records: **1,528**
* Temporal Snapshots:
  * `2020-01-01` to `2026-01-01`: 216 records each annual snapshot (covering 36 geographies $\times$ 6 RE fuels).
  * `2024-06-30`: 8 records (Official national/utility benchmark).
  * `2026-09-30`: 8 records (Official national/utility benchmark).
* Total Registered RE Capacity: **1,600,000+ MW** across multi-year historical trajectories.

### 3.3 Daily Generation & Operational Measurements (`generation_daily`)
* Total Records: **376**
* Breakdown by Source Code:
  * `SOLAR`: 173 records (11,582.57 MU)
  * `WIND`: 167 records (4,996.93 MU)
  * `HYDRO`: 18 records (2,604.00 MU)
  * `DEMAND_MET`: 18 records (30,080.00 MU)
* **Defect Identified for Part 3:** `DEMAND_MET` was stored as an `energy_source`. Total system demand met is an operational grid consumption metric, not an electricity generating technology. This will be migrated to `daily_operational_metrics` in Part 3.

### 3.4 Weather Observations (`weather_observations`)
* Total Records: **6,048**
* Geographies Covered: **36** State and UT centroids.
* Temporal Range: `2024-06-01 00:00:00` to `2024-06-07 23:00:00` (168 hourly blocks per state).
* Provenance: `ECMWF ERA5` reanalysis retrieved via Open-Meteo Historical Archive API.
* Stored Features:
  * 10m wind speed, 100m wind speed, wind direction.
  * 2m temperature, surface solar radiation (GHI/DNI), cloud cover, precipitation.
  * Latitude, longitude, weather model, record type (`REANALYSIS`), and retrieval timestamp.

### 3.5 Primary Source Files (`source_files`)
* Total Ingested Files: **11**
* Status Summary:
  * `COMPLETED`: 6 PDF files (CEA Sub-Report 1, Sub-Report 16, Capacity reports).
  * `SUCCESS`: 3 NLDC Daily PSP PDF files (`2024_06_01`, `2024_06_02`, `2026_10_31`), 22 records each.
  * `UNVERIFIED_SOURCE`: 2 CSV files (June 2024 & December 2024 CEA RE monthly CSVs).

---

## 4. Code Health & Test Suite Execution

### 4.1 Backend Pytest Suite
* **Command:** `pytest tests/ -v`
* **Result:** **81 passed, 1 skipped in 11.21s**
* **Failures:** 0
* **Skipped Test:** `test_postgresql_live_integration_suite` (Explicitly and properly skipped because live PostgreSQL instance is unprovisioned; marked `BLOCKED` as mandated by integrity guidelines).
* **UK Benchmark Tests:** 100% passed (`test_api_routes.py`, `test_forecast_selector.py`, `test_timezone_cutoffs.py`, `test_metrics_calculator.py`).

### 4.2 Frontend Vitest Suite
* **Command:** `npm run test`
* **Result:** **7 test files passed, 10 tests passed (100% pass rate)**
* **Failures:** 0
* **Components Tested:**
  * `ErrorAlert.test.tsx` (1 test)
  * `CutoffSelector.test.tsx` (1 test)
  * `MetricCard.test.tsx` (3 tests)
  * `IndiaNavigation.test.tsx` (1 test)
  * `IndiaInteractiveMap.test.tsx` (2 tests)
  * `TestingLab.test.tsx` (1 test)
  * `ProcurementExposureWidget.test.tsx` (1 test)

### 4.3 Frontend Production Build
* **Command:** `npm run build` (`tsc && vite build`)
* **Result:** **Built in 23.61s with 0 errors**
* **Bundle Outputs:**
  * `dist/index.html`: 1.14 kB
  * `dist/assets/index-BPHwrKpl.css`: 40.39 kB (gzip: 7.34 kB)
  * `dist/assets/index-PO2CjQhQ.js`: 890.76 kB (gzip: 220.72 kB)

---

## 5. Transition Plan to Part 3

With the baseline firmly established and verified, execution proceeds immediately to **Part 3 — Data Model Correction**:
1. Decouple operational grid demand (`DEMAND_MET`) from `energy_sources` and create a dedicated operational measurement table `daily_operational_metrics` with proper indexing and foreign keys.
2. Remove `DEMAND_MET` from `energy_sources`.
3. Standardize and enforce all 10 core data classification statuses.
4. Author and apply the corresponding Alembic migration.
5. Update backend models, queries, services, and tests.

