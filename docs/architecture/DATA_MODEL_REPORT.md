# WindScope India — Data Model & Ontological Architecture Report

**Document Reference:** `WINDSCOPE_INDIA_DATA_MODEL_REPORT.md`  
**Date:** November 1, 2026  
**Status:** Completed & Certified  
**Primary Working Directory:** `D:\WindScopeIndia`  

---

## Executive Summary

This report documents the structural correction of the **WindScope India** data model, decoupling operational power system demand measurements from renewable generation fuel technologies. It formalizes the database schema, verifies the canonical geographic hierarchy, details the applied Alembic migration (`c34891ef9012`), and guarantees strict epistemological separation across all ten standardized data classifications.

---

## 1. Problem Statement: Conflation of Demand and Generation

In early prototype iterations, total electrical demand met (`DEMAND_MET`) from Grid-India Daily PSP reports was stored in `generation_daily` using `energy_sources.source_code = 'DEMAND_MET'`.

### Why This Was Defective:
1. **Ontological Conflation:** Electrical demand met is an operational grid consumption metric, whereas wind, solar, and hydro are generator fuel technologies.
2. **Distorted RE Penetration:** Querying `SUM(generation_mu)` over `generation_daily` double-counted energy by adding consumer demand to electricity generated.
3. **Database Integrity Violation:** Energy sources had non-generating categories marked with `is_renewable = False`, violating domain semantics.

---

## 2. Structural Architecture & Schema Correction

### 2.1 The New Operational Demand Table: `daily_operational_metrics`
A dedicated table was created via Alembic revision `c34891ef9012`:

```sql
CREATE TABLE daily_operational_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    geography_id INTEGER NOT NULL REFERENCES geographies(id) ON DELETE CASCADE,
    delivery_date DATE NOT NULL,
    energy_met_mu NUMERIC(12, 3) NOT NULL,
    peak_demand_met_mw NUMERIC(12, 2) NULL,
    peak_shortage_mw NUMERIC(12, 2) NULL,
    energy_shortage_mu NUMERIC(12, 3) NULL,
    source_file_id INTEGER NULL REFERENCES source_files(id) ON DELETE SET NULL,
    source_provenance VARCHAR(100) NOT NULL DEFAULT 'Grid Controller of India Limited (NLDC Daily PSP)',
    data_classification VARCHAR(50) NOT NULL DEFAULT 'VERIFIED_OFFICIAL',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_daily_operational_metrics UNIQUE (geography_id, delivery_date)
);

CREATE INDEX idx_daily_operational_geo_date ON daily_operational_metrics(geography_id, delivery_date);
```

### 2.2 Purification of `energy_sources`
`DEMAND_MET` was purged from `energy_sources`. The table now contains strictly the 9 canonical electricity generation fuels:
* **Renewable Fuels (`is_variable_re = True`):** `WIND`, `SOLAR`
* **Non-Variable Renewable & Clean Fuels:** `LARGE_HYDRO`, `SMALL_HYDRO`, `BIOMASS`, `OTHER_RE`
* **Conventional / Baseload Generation:** `THERMAL`, `NUCLEAR`, `HYDRO`

### 2.3 Upgraded `generation_daily` Schema
`generation_daily` now possesses explicit provenance and classification attributes:
* `source_file_id`: Foreign key link to `source_files.id`
* `data_classification`: Standardized as `VERIFIED_OFFICIAL` for official Grid-India PSP records.

---

## 3. Canonical Geographic Hierarchy

All spatial operations reference the central `geographies` table (`42` canonical entries):

```
National Level (1 Entity)
└── IN-TOTAL: All India (National Aggregate)

Regional Grid Level (5 Entities)
├── IN-NR:  Northern Regional Load Despatch Centre (NRLDC, New Delhi)
├── IN-WR:  Western Regional Load Despatch Centre (WRLDC, Mumbai)
├── IN-SR:  Southern Regional Load Despatch Centre (SRLDC, Bengaluru)
├── IN-ER:  Eastern Regional Load Despatch Centre (ERLDC, Kolkata)
└── IN-NER: North Eastern Regional Load Despatch Centre (NERLDC, Shillong)

State & Union Territory Level (36 Entities)
├── 28 States: IN-AP, IN-AR, IN-AS, IN-BR, IN-CT, IN-GA, IN-GJ, IN-HR, IN-HP, IN-JH,
│              IN-KA, IN-KL, IN-MP, IN-MH, IN-MN, IN-ML, IN-MZ, IN-NL, IN-OR, IN-PB,
│              IN-RJ, IN-SK, IN-TN, IN-TG, IN-TR, IN-UP, IN-UT, IN-WB
└── 8 Union Territories: IN-AN, IN-CH, IN-DH, IN-DL, IN-JK, IN-LA, IN-LD, IN-PY
```

---

## 4. Standardized Data Classifications

Every record across all tables adheres to one of the ten standardized classifications:

| Classification | Meaning & Standard | Typical Table Usage |
| :--- | :--- | :--- |
| `VERIFIED_OFFICIAL` | Digitally authenticated against primary government PDF gazette | `generation_monthly`, `generation_daily`, `daily_operational_metrics`, `installed_capacity` |
| `OFFICIAL_SOURCE_UNVERIFIED` | Extracted from government portals/CSVs without matched primary PDF | Ingested CEA CSV reports |
| `VERIFIED_METEOROLOGICAL_ARCHIVE` | Historical meteorological ground truth from verified scientific archives | `weather_observations` |
| `REANALYSIS` | ECMWF ERA5 state reconstruction via IFS numerical assimilation | `weather_observations` (12,096 records) |
| `MODEL_GENERATED` | Deterministic algorithmic projection or machine learning inference | `forecast_records` |
| `DEMONSTRATION` | Calibrated synthetic data clearly disclosed to prevent false official claims | Historical multi-year baselines, 15-min simulated SCADA actuals |
| `UNVERIFIED_ZERO` | Numeric zero present in dataset without secondary evidence of plant outage | `generation_monthly` missing state entries |
| `VERIFIED_REPORTED_ZERO` | Numeric zero backed by physical non-existence or verified zero capacity | `Wind in Eastern Region` |
| `MISSING` | Delivery interval with absent telemetry or unsubmitted generation report | Null data blocks |
| `BLOCKED` | Data stream restricted by statutory, enterprise, or security boundaries | Live REMC 15-min SCADA, unprovisioned live PostgreSQL |

