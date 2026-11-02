# WindScope India — Renewable Energy Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178c6.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![Alembic](https://img.shields.io/badge/Alembic-1.13-red.svg)](https://alembic.sqlalchemy.org/)
[![Jurisdiction](https://img.shields.io/badge/Jurisdiction-India_(28_States_&_8_UTs)-forest.svg)](#)
[![Timezone](https://img.shields.io/badge/Grid_Timezone-Asia/Kolkata_(IST)-orange.svg)](#)

**WindScope India** is an enterprise-grade renewable energy intelligence, analytics, and operational forecasting platform engineered for the Indian electricity sector. The platform synthesizes statutory generation records from the Central Electricity Authority (CEA), real-time operational telemetry and demand data from Grid Controller of India Limited (Grid-India NLDC), capacity inventories from the National Power Portal (NPP), and atmospheric reanalysis models (Open-Meteo & ERA5).

---

## 1. Platform Architecture & Scope

```
+---------------------------------------------------------------------------------------------------+
|                  WINDSCOPE INDIA — RENEWABLE ENERGY INTELLIGENCE PLATFORM                         |
+---------------------------------------------------------------------------------------------------+
|  Statutory Ingestion Pipeline  |  PostgreSQL / SQLite Storage Engine  |  Analytics & Forecasting  |
|  - CEA Monthly OPM Reports     |  - 28 States & 8 Union Territories   |  - Capacity Utilization   |
|  - Grid-India NLDC Daily PSP   |  - 5 Regional Grid Councils          |  - 4 RE Accounting Metrics|
|  - NPP Installed Capacity      |  - 18,213 Normalized Observations    |  - 96-Block REMC Forecasts|
|  - ERA5 / Open-Meteo Reanalysis|  - Statutory Audit Logs & Reconcile  |  - CERC Market Timelines  |
+---------------------------------------------------------------------------------------------------+
|                                  REST API GATEWAY (FastAPI)                                       |
|  /api/v1/india/overview  /api/v1/india/map-data  /api/v1/india/states  /api/v1/india/forecasting  |
|  /api/v1/india/weather   /api/v1/india/capacity  /api/v1/india/grid    /api/v1/india/data-quality |
+---------------------------------------------------------------------------------------------------+
|                           REACT 18 + TYPESCRIPT RESPONSIVE FRONTEND                               |
|  14 Dynamic Modules • Natural Green Theme (#245B45 / #8FAE91 / #F5F7F2) • Zero Lookahead Leakage  |
+---------------------------------------------------------------------------------------------------+
```

### Complete Geographic Coverage
- **28 States:** Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat, Haryana, Himachal Pradesh, Jharkhand, Karnataka, Kerala, Madhya Pradesh, Maharashtra, Manipur, Meghalaya, Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura, Uttar Pradesh, Uttarakhand, West Bengal.
- **8 Union Territories:** Andaman and Nicobar Islands, Chandigarh, Dadra and Nagar Haveli and Daman and Diu, Delhi (NCT), Jammu and Kashmir, Ladakh, Lakshadweep, Puducherry.
- **5 Electrical Grid Councils:** Northern Region (NR), Western Region (WR), Southern Region (SR), Eastern Region (ER), North Eastern Region (NER).

### Energy Technologies Analyzed
- **Wind Energy:** Onshore fleet, hub-height 100m wind velocity correlation, monsoon generation surges.
- **Solar Photovoltaic:** Ground-mount utility solar parks, Rooftop Solar, Global Horizontal Irradiance (GHI).
- **Large Hydroelectric:** Conventional reservoirs and run-of-the-river (>25 MW).
- **Small Hydroelectric:** Sub-25 MW projects under MNRE mandate.
- **Biomass, Bagasse & Waste-to-Energy:** Agro-residue cogeneration and municipal solid waste.

---

## 2. Interactive Application Modules

The application frontend delivers 14 dedicated, high-performance analytical views:

1. **National Overview (`/india-overview`):** High-level aggregate metrics, national generation outturn, capacity trajectory, and monthly fuel contributions.
2. **Interactive India Map (`/india-map`):** Interactive choropleth map supporting technology filtering, regional grid council overlays, and state-level detail drawers.
3. **State & UT Explorer (`/india-states`):** Granular profiles for all 36 administrative entities, multi-year generation curves, monthly seasonality profiles, and technology mix.
4. **Regional Grid Comparison (`/india-regional`):** Inter-regional comparison across NR, WR, SR, ER, and NER grids, evaluating regional renewable penetration and demand.
5. **Multi-Year Analytics (`/india-multi-year`):** 2020–2026 trajectory tracking, annual growth rates (YoY), and compound expansion across solar and wind sectors.
6. **Wind Energy Sector (`/india-wind`):** Deep dive into Indian wind power, seasonal monsoon generation profiles (May–September), and non-wind state disclosures.
7. **Solar Photovoltaic Sector (`/india-solar`):** Deep dive into solar parks (Bhadla, Pavagada, Kurnool), springtime outturn peaks (March–May), and daytime insolation patterns.
8. **Hydroelectric Energy (`/india-hydro`):** Large Hydro and Small Hydro operational characteristics, Himalayan snowmelt and monsoon inflows, and firm capacity contributions.
9. **Capacity & 500 GW Target Tracker (`/india-capacity`):** Monitoring progress toward India's COP26 non-fossil installed capacity goal of 500 GW by 2030, required addition run-rates, and technology trajectories.
10. **Forecasting & REMC Accuracy (`/india-forecasting`):** 96 intraday 15-minute dispatch blocks, Renewable Energy Management Centre (REMC) Day-Ahead schedules, outturn comparisons, and Deviation Settlement Mechanism (DSM) error bands.
11. **Atmospheric Weather Intelligence (`/india-weather`):** Hub-height 100m wind speeds, solar irradiance, surface temperatures, and empirical weather-to-generation correlation matrices.
12. **Data Explorer & Ledger (`/india-explorer`):** Searchable, paginated tabular explorer across 18,213 normalized observations with provenance indicators and standards-compliant CSV export.
13. **Data Quality & Provenance Matrix (`/india-data-quality`):** 36/36 jurisdictional completeness matrix, official source file records, national sum reconciliation audits, and data classification tagging.
14. **Technical Methodology (`/india-methodology`):** Regulatory documentation, Section 73(i) statutory authority, CERC IEGC rules, mathematical error formulations, and unit standardization (MW, MU, MWh).

---

## 3. Statutory Market Rules & Gate Closures

WindScope India enforces exact statutory market timing rules defined by the Central Electricity Regulatory Commission (CERC) under the Indian Electricity Grid Code (IEGC) 2023 and Power Market Regulations (PMR) 2021:

| Market Product | Authority & Regulation | Bidding Gate Closure (IST) | Delivery Horizon | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **Day-Ahead Market (DAM)** | CERC PMR 2021 Reg 6 / Power Exchanges | **12:00 PM (Noon) on D-1** | Day D (00:00 - 24:00 IST) | COMPLETED |
| **Green Day-Ahead Market (GDAM)** | CERC PMR 2021 / CERC Order 447/MP/2019 | **12:00 PM (Noon) on D-1** | Day D (00:00 - 24:00 IST) | COMPLETED |
| **Real-Time Market (RTM)** | CERC IEGC 2023 Reg 45(4) / RTM Regs | **T - 75 minutes** | Specified 15-min block | COMPLETED |
| **Term-Ahead Intraday (TAM)** | Power Exchange Business Rules (IEX/PXIL/HPX) | **T - 3 hours** | Specified intraday block | COMPLETED |

Anti-leakage eligibility validation ensures that forecasts published after gate closure are strictly disqualified from day-ahead evaluations, preventing look-ahead contamination.

---

## 4. Statutory Renewable Accounting Measures

The platform provides explicit computation of all four distinct renewable energy measures used across Indian regulatory proceedings:

- **Measure A — Variable Renewable Energy (VRE) Penetration (%):**
  $$\text{VRE \%} = \frac{\text{Wind Generation (MU)} + \text{Solar Generation (MU)}}{\text{Total Energy Met (MU)}} \times 100$$
- **Measure B — RE Excluding Large Hydro (%):**
  $$\text{RE (Excl. LH) \%} = \frac{\text{Wind} + \text{Solar} + \text{Small Hydro} + \text{Biomass}}{\text{Total Energy Met (MU)}} \times 100$$
- **Measure C — Total Renewable Energy Including Large Hydro (%):**
  $$\text{Total RE \%} = \frac{\text{Total Renewable Generation including Large Hydro (MU)}}{\text{Total Energy Met (MU)}} \times 100$$
- **Measure D — Non-Fossil Share of Gross Generation (%):**
  $$\text{Non-Fossil Share \%} = \frac{\text{Hydro} + \text{Nuclear} + \text{Wind} + \text{Solar} + \text{Other RE (MU)}}{\text{Gross National Generation (MU)}} \times 100$$

---

## 5. Technology Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, NumPy, Pandas, Requests.
- **Frontend:** React 18, TypeScript 5.4, Vite 5.3, Tailwind CSS 3.4, Lucide React Icons, Recharts 2.12.
- **Database:** SQLite (development / standalone), PostgreSQL (production target via psycopg2-binary).
- **Timezone Architecture:** `Asia/Kolkata` (Indian Standard Time, UTC+05:30) uniformly enforced.
- **Design System:** Restrained nature palette — Deep Forest Green (`#245B45`), Sage Accent (`#8FAE91`), Pale Natural Background (`#F5F7F2`), Slate Text (`#26332C`).

---

## 6. Local Setup & Execution Guide

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Git

### 1. Backend Setup
```bash
cd D:\WindScopeIndia\backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate   # On Windows (PowerShell: .venv\Scripts\Activate.ps1)

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations (SQLite or PostgreSQL)
alembic upgrade head

# Launch the FastAPI backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API documentation is interactively accessible at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Endpoint: `http://localhost:8000/health`

### 2. Frontend Setup
```bash
cd D:\WindScopeIndia\frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
The application will be available at `http://localhost:5173`.

---

## 7. Verification & Test Suite

### Backend Regression Tests
Run the comprehensive 67-case backend test suite:
```bash
cd D:\WindScopeIndia\backend
.venv\Scripts\python.exe -m pytest tests -v
```
Expected result: **66 passed, 1 skipped** (PostgreSQL live container test skipped when local PG daemon is offline).

### Frontend Component & Navigation Tests
Run the Vitest test suite:
```bash
cd D:\WindScopeIndia\frontend
npm test
```
Expected result: **4 test files passed, 7 tests passed**.

### Production Frontend Build
Verify TypeScript compilation and chunk bundling:
```bash
cd D:\WindScopeIndia\frontend
npm run build
```
Expected result: **0 errors, clean output in `frontend/dist/`**.

---

## 8. Data Integrity & Provenance Principles

1. **Strict Source Attribution:** Every record preserves its originating authority (CEA, Grid-India, NPP, Open-Meteo), statutory legal reference, and ingestion timestamp.
2. **Separation of Verified and Demonstration Data:** Official government observations are classified as `VERIFIED_OFFICIAL`; synthetic or simulated data points are explicitly flagged as `DEMONSTRATION` and never mixed silently in statutory analytics.
3. **Accurate Semantics for Non-Reporting:** Zero generation is distinguished from missing observations (`MISSING_OBSERVATION`). Non-wind states are reported as non-generating rather than omitted.
4. **Physical Sanity Bounds:** Capacity Utilization Factor (CUF %) formulas account for exact leap-year month lengths and flag implausible values (>100%) as data-quality warnings rather than silently clamping.

---

## 9. License & Statutory Citations

- Electricity Act 2003, Section 73(i) (Central Electricity Authority).
- CERC Indian Electricity Grid Code (IEGC) Regulations, 2023.
- CERC Power Market Regulations (PMR), 2021.
- Grid Controller of India Limited (National Load Despatch Centre Daily Operational Bulletins).
- Open-Meteo API (Weather and ERA5 atmospheric reanalysis under CC BY 4.0).
