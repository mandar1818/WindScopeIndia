# WindScope India

### Renewable Energy Intelligence & Forecasting Platform

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript 5.4](https://img.shields.io/badge/TypeScript-5.4-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS 3.4](https://img.shields.io/badge/TailwindCSS-3.4-38BDF8.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Alembic 1.20](https://img.shields.io/badge/Alembic-1.20-red.svg)](https://alembic.sqlalchemy.org/)
[![Jurisdiction](https://img.shields.io/badge/Jurisdiction-India_(28_States_&_8_UTs)-245B45.svg)](#)
[![Timezone](https://img.shields.io/badge/Grid_Timezone-Asia/Kolkata_(IST)-orange.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Project Introduction

**WindScope India** is an enterprise-grade renewable energy intelligence, analytics, and operational forecasting platform engineered specifically for the Indian power sector. The platform synthesizes statutory generation records from the Central Electricity Authority (CEA), operational demand and grid telemetry from Grid Controller of India Limited (Grid-India NLDC), installed capacity inventories from the National Power Portal (NPP), and atmospheric reanalysis models from ECMWF ERA5 and Open-Meteo.

Designed for energy analysts, grid operators, traders, and policymakers, WindScope India delivers multi-year generation analysis, technology-specific deep dives, regional electrical grid comparisons, and 15-minute intraday dispatch schedules governed strictly by statutory Indian electricity market rules.

---

## 2. Problem Statement

India possesses one of the world's most rapidly expanding renewable energy grids, targeting 500 GW of non-fossil capacity by 2030. However, renewable market data remains fragmented across disparate government bodies, static monthly PDF gazettes, legacy state portals, and unstandardized formats:

1. **Information Asymmetry:** CEA monthly reports, NLDC daily bulletins, and state-level renewable accounting follow different reporting calendars, units, and categorization methodologies.
2. **Lookahead Bias in Forecasting:** Machine learning benchmarks frequently leak future operational information across gate closures, violating CERC Deviation Settlement Mechanism (DSM) operating conditions.
3. **Misleading Accounting:** Conventional platforms often confound Variable Renewable Energy (VRE: Wind + Solar) with Large Hydro or conflate missing telemetry with zero generation.
4. **Lack of Granular Provenance:** Analysts frequently cannot trace aggregate data back to official government source files, PDF page numbers, or cryptographic checksums.

---

## 3. Project Objectives

- **Unified National Intelligence:** Provide comprehensive, all-India coverage across all 28 States and 8 Union Territories spanning 5 regional electrical grid councils.
- **Multi-Source Reconciliation:** Ingest and normalize statutory records from official CEA monthly reports, Grid-India daily bulletins, and NPP capacity gazettes with SHA-256 provenance tracking.
- **Statutory Market Rule Enforcement:** Implement strict mathematical anti-leakage filters adhering to CERC (Power Market Regulations) 2021 and CERC (Indian Electricity Grid Code) 2023 trading gate closures.
- **Multi-Measure Renewable Accounting:** Accurately compute all four distinct renewable energy metrics used across Indian regulatory proceedings.
- **Transparent Provenance & Zero Fabrication:** Maintain strict segregation between verified government observations (`VERIFIED_OFFICIAL`), unverified filings (`OFFICIAL_SOURCE_UNVERIFIED`), and synthetic baselines (`DEMONSTRATION`).

---

## 4. Main Capabilities

- **National Overview Dashboard:** High-level metrics, national generation outturns, monthly fuel contributions, and capacity trajectories.
- **Interactive India Choropleth Map:** High-precision SVG visualization covering all 36 States and Union Territories with state detail drawers and grid overlays.
- **Granular State & UT Explorer:** Multi-year generation curves, monthly seasonality profiles, and technology mix analysis for each jurisdiction.
- **Regional Grid Council Analytics:** Comparative performance analysis across the 5 synchronous electrical regions (NR, WR, SR, ER, NER).
- **Multi-Year Trend Analysis (2020–2026):** Longitudinal generation tracking, annual growth rates (YoY), and seasonal surge detection.
- **Technology Deep Dives:** Dedicated operational modules for Wind, Solar Photovoltaic, and Hydroelectric generation.
- **Capacity & 500 GW Target Tracker:** Tracking installed renewable capacity against India's COP26 2030 target of 500 GW non-fossil capacity.
- **Forecasting & REMC Accuracy:** 96-block 15-minute intraday schedules, day-ahead forecasts, outturn comparisons, and error metrics (MAE, RMSE, WAPE).
- **Atmospheric Weather Intelligence:** Centroid hub-height 100m wind velocity, Global Horizontal Irradiance (GHI), temperature, and empirical weather-to-generation correlation matrices.
- **Searchable Ledger & CSV Export:** Filtered tabular data explorer across 18,213 records with standards-compliant UTF-8 CSV streaming export.
- **Data Quality & Provenance Matrix:** Audit logs, source file registers, checksums, and national sum reconciliation variances.

---

## 5. Renewable Energy Categories

The platform analyzes six standardized fuel and technology classifications:

1. **Wind Energy (`WIND`):** Onshore utility fleet, hub-height 100m wind speeds, and southwest monsoon generation surges (May–September).
2. **Solar Photovoltaic (`SOLAR`):** Ground-mounted solar parks, rooftop installations, daytime generation profiles, and GHI solar irradiance.
3. **Large Hydroelectric (`LARGE_HYDRO`):** Conventional reservoirs and run-of-the-river plants (>25 MW) under CEA monitoring.
4. **Small Hydroelectric (`SMALL_HYDRO`):** Sub-25 MW mini and micro hydroelectric projects governed under MNRE mandate.
5. **Biomass, Bagasse & Cogeneration (`BIOMASS`):** Agro-residue power and bagasse cogeneration units.
6. **Other Renewable Energy / Waste-to-Energy (`OTHER_RE`):** Municipal solid waste, industrial waste-to-energy, and emerging technologies.

---

## 6. Geographic Coverage

WindScope India covers 100% of India's electrical and administrative jurisdiction:

```
+---------------------------------------------------------------------------------------------------+
|                           INDIA ELECTRICAL JURISDICTION (5 REGIONS)                               |
+---------------------------------------------------------------------------------------------------+
|  Northern Region (NR)   |  Western Region (WR)    |  Southern Region (SR)   |  Eastern / NER      |
|  - Delhi, Haryana       |  - Gujarat, Maharashtra |  - Tamil Nadu, Karnataka|  - West Bengal,     |
|  - Punjab, Rajasthan    |  - Madhya Pradesh       |  - Andhra Pradesh       |    Odisha, Bihar    |
|  - UP, Uttarakhand      |  - Chhattisgarh, Goa    |  - Telangana, Kerala    |  - Assam, Sikkim    |
|  - HP, J&K, Ladakh      |  - DNH & DD             |  - Puducherry, Lakshadw.|  - All 7 NE States  |
+---------------------------------------------------------------------------------------------------+
```

- **28 States:** Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat, Haryana, Himachal Pradesh, Jharkhand, Karnataka, Kerala, Madhya Pradesh, Maharashtra, Manipur, Meghalaya, Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura, Uttar Pradesh, Uttarakhand, West Bengal.
- **8 Union Territories:** Andaman and Nicobar Islands, Chandigarh, Dadra and Nagar Haveli and Daman and Diu, Delhi (NCT), Jammu and Kashmir, Ladakh, Lakshadweep, Puducherry.
- **5 Regional Grid Councils:** Northern Region (NR), Western Region (WR), Southern Region (SR), Eastern Region (ER), North Eastern Region (NER).

---

## 7. Historical Analytics & Statutory Accounting

WindScope India enforces exact mathematical definitions for the four official renewable energy accounting measures utilized across CEA, CERC, and Grid-India proceedings:

| Measure | Metric Designation | Mathematical Formulation | Regulatory Context |
| :--- | :--- | :--- | :--- |
| **Measure A** | **Variable Renewable Energy (VRE %)** | $\frac{\text{Wind (MU)} + \text{Solar (MU)}}{\text{Total Energy Met (MU)}} \times 100$ | Grid balancing and intermittency tracking |
| **Measure B** | **RE Excluding Large Hydro (%)** | $\frac{\text{Wind} + \text{Solar} + \text{Small Hydro} + \text{Biomass}}{\text{Total Energy Met (MU)}} \times 100$ | Traditional MNRE renewable target accounting |
| **Measure C** | **Total Renewable Energy (%)** | $\frac{\text{Wind} + \text{Solar} + \text{Small Hydro} + \text{Biomass} + \text{Large Hydro}}{\text{Total Energy Met (MU)}} \times 100$ | Comprehensive green power share |
| **Measure D** | **Non-Fossil Share of Generation (%)** | $\frac{\text{Hydro} + \text{Nuclear} + \text{RES (Wind+Solar+Bio)}}{\text{Gross National Generation (MU)}} \times 100$ | COP26 non-fossil generation commitment |

*Capacity Utilization Factor (CUF %)* calculations explicitly account for leap-year calendar days (696 hours in February 2024 vs 672 in standard years) and preserve unclamped data-quality warnings if reported figures exceed theoretical 100% availability.

---

## 8. Electricity Grid Intelligence & Market Rules

WindScope India models statutory wholesale market segments under CERC (Power Market Regulations) 2021 and CERC (Indian Electricity Grid Code) 2023:

```
+---------------------------------------------------------------------------------------------------+
|                              STATUTORY POWER MARKET GATE CLOSURES                                 |
+---------------------------------------------------------------------------------------------------+
|  Market Segment       | Authority & Regulation      | Gate Closure (IST)      | Delivery Horizon  |
+-----------------------+-----------------------------+-------------------------+-------------------+
|  Day-Ahead (DAM)      | CERC PMR 2021 Reg 6         | 12:00 PM (Noon) on D-1  | Day D (96 blocks) |
|  Green Day-Ahead      | CERC Order 447/MP/2019      | 12:00 PM (Noon) on D-1  | Day D (96 blocks) |
|  Real-Time (RTM)      | CERC IEGC 2023 Reg 45(4)    | T - 75 minutes          | 15-minute block   |
|  Term-Ahead (TAM)     | Power Exchange Rules        | T - 3 hours             | Intraday blocks   |
+---------------------------------------------------------------------------------------------------+
```

- **Anti-Leakage Guarantee:** Any forecast record published after gate closure is disqualified from day-ahead evaluations, eliminating lookahead bias.
- **Operational Grid Telemetry:** Monitors daily All-India and Regional energy met (MU), peak demand met (MW), frequency bands (nominal 50.00 Hz, iegc band 49.90–50.05 Hz), and inter-regional exchanges.

---

## 9. Weather Intelligence & REZ Zones

- **Atmospheric Variables:** 100m hub-height wind speed (m/s), surface temperature (°C), Global Horizontal Irradiance ($GHI$, $\text{W/m}^2$), Direct Normal Irradiance ($DNI$), and cloud cover (%).
- **Reanalysis Sources:** High-resolution ECMWF ERA5 reanalysis and Open-Meteo meteorological models.
- **Renewable Energy Zone (REZ) Catalog:** Precise geographical coordinates and installed capacities for major green energy complexes:
  - Bhadla Solar Park (Rajasthan — 2,245 MW)
  - Khavda Renewable Energy Park (Gujarat — 30,000 MW planned)
  - Pavagada Solar Park (Karnataka — 2,050 MW)
  - Kurnool Ultra Mega Solar Park (Andhra Pradesh — 1,000 MW)
  - Muppandal Wind Farm (Tamil Nadu — 1,500 MW)
  - Jaisalmer Wind Park (Rajasthan — 1,064 MW)

---

## 10. Machine Learning Forecasting

The platform features a modular forecasting engine designed for Renewable Energy Management Centres (REMC):

- **Model Registry:** Gradient Boosted Decision Trees (`GRADIENT_BOOSTING_TS`), Persistence / Naive Baseline (`PERSISTENCE_NAIVE`), and Climatological Seasonal Baselines.
- **Dispatch Granularity:** 96 intraday 15-minute settlement blocks per delivery day.
- **Error Formulations:**
  - Mean Absolute Error (MAE): $\frac{1}{N}\sum |F_t - A_t|$
  - Root Mean Squared Error (RMSE): $\sqrt{\frac{1}{N}\sum (F_t - A_t)^2}$
  - Weighted Absolute Percentage Error (WAPE %): $\frac{\sum |F_t - A_t|}{\sum A_t} \times 100$
  - Deviation Settlement Mechanism (DSM) Error Bands: CERC tolerance bands ($\pm 10\%$ / $\pm 15\%$).

*Note: All model-generated forecasts are research and analytical simulations. They do not constitute official Grid-India or REMC operational schedules.*

---

## 11. Technology Stack

### Backend
- **Language:** Python 3.12
- **Web Framework:** FastAPI 0.110.1 (ASGI)
- **Server:** Uvicorn 0.29.0
- **Database ORM:** SQLAlchemy 2.1.6
- **Database Migrations:** Alembic 1.20.1
- **Data Science:** Pandas 2.2.2, NumPy 1.26.4
- **Document Extraction:** pdfplumber 0.11.0, PyPDF 6.0.0, openpyxl 3.1.2
- **Testing:** Pytest 8.1.1, pytest-asyncio 0.23.6

### Frontend
- **Language:** TypeScript 5.4.5
- **Library:** React 18.3.1 (Single-Page Application)
- **Build Tool:** Vite 5.3.1
- **Styling:** Tailwind CSS 3.4.4
- **Visualization:** Recharts 2.12.7 + SVG Interactive Choropleth Map
- **Icons:** Lucide React 0.395.0
- **Testing:** Vitest 1.6.0, React Testing Library 15.0.7, jsdom 24.1.0

### Database & Infrastructure
- **Development Database:** SQLite (standalone file-based database: `windscope_india.db`)
- **Production Target Database:** PostgreSQL 15+ (via `psycopg2-binary 2.9.9` with connection pooling)
- **Hosting Blueprint:** Render (`render.yaml` web service) & Vercel (`vercel.json` SPA configuration)

---

## 12. System Architecture

```
+---------------------------------------------------------------------------------------------------+
|                         WINDSCOPE INDIA — SYSTEM ARCHITECTURE                                     |
+---------------------------------------------------------------------------------------------------+
|  Statutory Ingestion Engine    |  Relational Storage Engine           |  Analytics & Forecasting  |
|  - CEA Monthly OPM PDF/CSVs    |  - Canonical Geographies (42)        |  - Capacity Utilization   |
|  - Grid-India Daily PSP PDFs   |  - Generation Monthly (16,134 rows)  |  - 4 Statutory RE Measures|
|  - NPP Installed Capacity      |  - Weather Observations (12,096 rows)|  - 96-Block REMC Forecasts|
|  - Open-Meteo / ERA5 Reanalysis|  - Daily Operational Demand Met      |  - CERC Gate Closures     |
|  - Cryptographic SHA-256 Logs  |  - Source File Audits & Reconcile    |  - DSM Error Bands        |
+---------------------------------------------------------------------------------------------------+
|                                 REST API GATEWAY (FastAPI)                                        |
|  /api/v1/india/overview  /api/v1/india/map-data  /api/v1/india/states  /api/v1/india/forecasting   |
|  /api/v1/india/weather   /api/v1/india/capacity  /api/v1/india/grid    /api/v1/india/data-quality  |
+---------------------------------------------------------------------------------------------------+
|                              REACT 18 + TYPESCRIPT FRONTEND                                       |
|  14 Dedicated Modules • Responsive Shell • Natural Palette (#245B45 / #8FAE91 / #F5F7F2)          |
+---------------------------------------------------------------------------------------------------+
```

---

## 13. Project Directory Structure

```
WindScopeIndia/
├── .github/
│   ├── workflows/ci.yml                # Automated CI workflow (Pytest, Vitest, Build)
│   └── ISSUE_TEMPLATE/                 # Issue templates (Bug Report, Feature Request)
├── backend/
│   ├── alembic/                        # Alembic migration environment
│   │   └── versions/                   # Versioned migration revisions
│   ├── app/
│   │   ├── api/v1/                     # FastAPI route handlers (/india/*, /health)
│   │   ├── core/                       # App settings, logging, database engine session
│   │   ├── models/                     # SQLAlchemy declarative models
│   │   └── services/                   # Business logic, analytics, weather, ingestion
│   ├── data/
│   │   └── raw/                        # Statutory CEA & Grid-India bulletins and datasets
│   ├── tests/                          # 67-case Pytest automated test suite
│   ├── requirements.txt                # Pinned Python dependencies
│   └── README.md                       # Backend specific documentation
├── frontend/
│   ├── public/                         # Public static assets
│   ├── src/
│   │   ├── components/                 # Reusable UI widgets, layout shell, interactive map
│   │   ├── pages/india/                # 14 dedicated analytical views
│   │   ├── services/                   # API clients and response mappers
│   │   ├── types/                      # TypeScript domain definitions
│   │   ├── App.tsx                     # Main layout shell and route selector
│   │   └── main.tsx                    # React application bootstrap
│   ├── package.json                    # Frontend package dependencies & scripts
│   ├── vite.config.ts                  # Vite configuration & proxy definitions
│   └── README.md                       # Frontend specific documentation
├── docs/
│   ├── api/                            # REST API reference specifications
│   ├── architecture/                   # Data model, migration guides, design system
│   ├── audit-reports/                  # Independent verification and deployment audits
│   ├── data-sources/                   # Coverage matrices, weather, grid telemetry specs
│   └── MASTER_INDEX.md                 # Complete documentation catalog
├── .env.example                        # Template environment variables
├── .gitignore                          # Git exclusion rules
├── CONTRIBUTING.md                     # Contribution guidelines and ground rules
├── docker-compose.yml                  # Local container orchestration
├── LICENSE                             # MIT License
├── README.md                           # Master repository documentation
├── render.yaml                         # Render blueprint specification
└── vercel.json                         # Vercel SPA build and rewrite rules
```

---

## 14. Data Sources and Provenance

Every dataset ingested into WindScope India preserves complete provenance:

1. **Central Electricity Authority (CEA):** Monthly Operation Performance Monitoring (OPM) bulletins and generation tables under Section 73(i) of the Electricity Act 2003.
2. **Grid Controller of India Limited (Grid-India NLDC):** Daily Power Supply Position (PSP) bulletins published by the National Load Despatch Centre.
3. **National Power Portal (NPP):** Official installed capacity gazettes and technology breakdowns.
4. **Open-Meteo & ECMWF ERA5:** Atmospheric reanalysis observations licensed under CC BY 4.0.

---

## 15. Data Reliability Classifications

To ensure academic and regulatory rigor, records are strictly tagged:

- `VERIFIED_OFFICIAL`: Ingested directly from official government reports (CEA, Grid-India, NPP) with cryptographic SHA-256 source file checksums, page numbers, and reconciliation records.
- `OFFICIAL_SOURCE_UNVERIFIED`: Extracted from provisional reports or bulletins pending final statutory annual reconciliation.
- `DEMONSTRATION`: Synthetic baseline records utilized strictly for UI rendering or algorithm prototyping when statutory historical feeds are unavailable.

> **Data Integrity Principle:** Missing observations (`null`) are strictly distinguished from zero generation (`0.0`). Zero generation represents an operational non-generating state (e.g. non-wind states or solar at night), while missing telemetry represents data unavailability.

---

## 16. Installation Instructions

### Prerequisites
- Python 3.12 or higher
- Node.js 18 or higher with npm
- Git

Clone the repository:
```bash
git clone https://github.com/mandar1818/WindScopeIndia.git
cd WindScopeIndia
```

---

## 17. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend server will start at `http://localhost:8000`. Interactive docs are available at `/docs` and `/redoc`.

---

## 18. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

The application frontend will be available at `http://localhost:5173`.

---

## 19. Environment Variable Configuration

Copy the example environment template:
```bash
cp .env.example .env
```

Key environment variables:
```ini
# Database (SQLite by default, PostgreSQL for production)
DATABASE_URL=sqlite:///./windscope_india.db

# Application Configuration
APP_ENV=development
DEBUG=false
PORT=8000
API_V1_PREFIX=/api/v1
TIMEZONE_IST=Asia/Kolkata
MARKET_TIMEZONE=Asia/Kolkata

# Security (Required for triggering document ingestion)
INGESTION_ADMIN_KEY=dev_admin_secret_key_change_in_prod

# CORS Allowed Origins
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

---

## 20. Database Configuration

The application features dual-engine database support via SQLAlchemy:

- **Local Development (Default):** Pre-seeded SQLite database (`backend/windscope_india.db`) containing 16,134 monthly generation records, 12,096 weather observations, and canonical Indian geographical definitions.
- **Production PostgreSQL:** Supported via `psycopg2-binary` with configurable connection pooling (`DATABASE_POOL_SIZE=10`, `DATABASE_MAX_OVERFLOW=20`, `DATABASE_POOL_RECYCLE=1800`, SSL mode support).

To apply migrations on PostgreSQL:
```bash
export DATABASE_URL="postgresql://user:password@hostname:5432/dbname"
alembic upgrade head
```

---

## 21. Running Tests

### Backend Automated Tests
```bash
cd backend
.venv\Scripts\python.exe -m pytest tests -v
```
**Results:** **66 passed, 1 skipped** (PostgreSQL container test skipped when local PG daemon is offline).

### Frontend Component & Navigation Tests
```bash
cd frontend
npm test
```
**Results:** **4 test files passed, 7 tests passed** (`ErrorAlert`, `MetricCard`, `IndiaNavigation`, `IndiaInteractiveMap`).

---

## 22. Production Build Instructions

To compile and verify the frontend production build:
```bash
cd frontend
npm run build
```
Executes TypeScript compilation (`tsc`) and Vite bundling. Output is generated in `frontend/dist/`.

---

## 23. Deployment Configuration & Status

The project includes pre-configured deployment manifests:

- **Render Backend Blueprint (`render.yaml`):** Defines the `windscope-india-backend` web service running Python 3.12 with Uvicorn and `/health` probes.
- **Vercel Frontend Configuration (`vercel.json`):** Defines build command `cd frontend && npm install && npm run build`, output directory `frontend/dist`, and API proxy rewrites to Render.

### Deployment Status Audit (as of 2026-11-03)

| Component | Status | Verification Detail |
| :--- | :--- | :--- |
| **GitHub** | **VERIFIED** | Active repository at `mandar1818/WindScopeIndia`, branch `main` in sync. |
| **Vercel** | **CONFIGURED TARGET** | Manifest configured; live domain `windscope-india.vercel.app` requires dashboard deployment activation. |
| **Render** | **CONFIGURED TARGET** | Blueprint configured; live domain `windscope-india-backend.onrender.com` requires service activation. |
| **PostgreSQL** | **CONFIGURED TARGET** | Migration scripts verified; requires managed PostgreSQL instance connection. |

*Links to configured deployment targets:*
- Frontend: `https://windscope-india.vercel.app`
- Backend API: `https://windscope-india-backend.onrender.com`

---

## 24. API Documentation

Detailed endpoint documentation is available in [`docs/api/API_REFERENCE.md`](docs/api/API_REFERENCE.md).

Key REST endpoints:

- `GET /health` — Service health and operational indicators.
- `GET /api/v1/india/overview` — National generation outturn, capacity, and monthly summary.
- `GET /api/v1/india/map-data` — State-level metrics for SVG choropleth rendering.
- `GET /api/v1/india/states` — Directory of all 28 States and 8 Union Territories.
- `GET /api/v1/india/states/{state_code}` — Granular state profile and historical trends.
- `GET /api/v1/india/multi-year` — Multi-year generation trends and YoY comparisons (2020–2026).
- `GET /api/v1/india/sources/{source_code}` — Deep dive into Wind, Solar, or Hydro generation.
- `GET /api/v1/india/regional` — Regional comparison across NR, WR, SR, ER, and NER grids.
- `GET /api/v1/india/capacity` — Installed capacity metrics and 2030 target progress.
- `GET /api/v1/india/forecasting` — 96-block intraday REMC schedules and accuracy bounds.
- `GET /api/v1/india/weather` — Atmospheric observations, wind speeds, GHI, and correlations.
- `GET /api/v1/india/grid/status` — Grid Controller of India operational indicators.
- `GET /api/v1/india/grid/operational-metrics` — Daily demand met and 4 renewable accounting measures.
- `GET /api/v1/india/data-quality` — 36/36 jurisdictional completeness report and audit log.
- `GET /api/v1/india/explorer` — Paginated tabular ledger with filtering.
- `GET /api/v1/india/export/csv` — UTF-8 streaming CSV download.

---

## 25. Known Limitations

1. **REMC Real-Time Telemetry:** Live 15-minute SCADA telemetry from Renewable Energy Management Centres requires enterprise RLDC access credentials and VPN whitelisting; public access relies on statutory daily PSP bulletins.
2. **Centroid Meteorological Resolution:** State-level weather data uses geographic centroids; microclimate variations in mountainous regions (e.g. Ladakh, Himachal Pradesh) are subject to smoothing.
3. **Historical Ingestion Lags:** Government CEA monthly OPM bulletins operate with an official statutory publishing lag of 45–60 days.

---

## 26. Future Scope

- **Inter-Regional Flow Optimization:** Integration of dynamic ATC/TTC (Available Transfer Capability) inter-regional transfer data from NLDC.
- **Battery Energy Storage (BESS) Tracking:** Dedicated module for utility-scale battery storage and pumped storage hydro (PSP) operational dispatch.
- **Rooftop Solar Disaggregation:** High-resolution separation of rooftop solar PV outturn from utility-scale transmission-connected solar parks.
- **Automated Crawler for Daily PSP:** Scheduled cron jobs for automatic daily PDF bulletin retrieval from Grid-India.

---

## 27. Contribution Guidelines

Contributions are welcome! Please review [`CONTRIBUTING.md`](CONTRIBUTING.md) for details on code style, testing requirements, and the strict non-fabrication data policy.

---

## 28. License Information

This project is licensed under the [MIT License](LICENSE).

Statutory public data citations:
- Central Electricity Authority (CEA), Ministry of Power, Government of India.
- Grid Controller of India Limited (Grid-India NLDC).
- National Power Portal (NPP), Central Electricity Authority.
- Open-Meteo Weather API & ECMWF ERA5 reanalysis (licensed under CC BY 4.0).
