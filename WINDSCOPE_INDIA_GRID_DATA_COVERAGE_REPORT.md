# WindScope India — Grid Data Coverage Report

**Document Reference:** `WINDSCOPE_INDIA_GRID_DATA_COVERAGE_REPORT.md`  
**Date:** November 1, 2026  
**Source Authority:** Grid Controller of India Limited (formerly POSOCO) / National Load Despatch Centre (NLDC)  
**Primary Working Directory:** `D:\WindScopeIndia`  

---

## Executive Summary

This report delivers a forensic audit of the daily operational grid data coverage within **WindScope India**, validating the ingestion of official Power Supply Position (PSP) bulletins, resolving the 22-record extraction structure, detailing the structural separation between operational demand and renewable generation, and confirming the honest `BLOCKED` status of private 15-minute SCADA telemetry.

---

## 1. Grid-India Institutional Architecture & Data Streams

Under the *Electricity Act 2003* and the *Indian Electricity Grid Code (IEGC 2023)*, Grid Controller of India Limited operates the National Load Despatch Centre (NLDC) and five Regional Load Despatch Centres (RLDCs: NRLDC, WRLDC, SRLDC, ERLDC, NERLDC).

### 1.1 Official Data Streams
1. **Daily Power Supply Position (PSP) Bulletins (Public):**
   * **Domain:** `https://grid-india.in/reports/daily-reports/`
   * **Cadence:** Daily (Day $D$ published on $D+1$ by 09:00 IST).
   * **Scope:** All-India and 5 Regional totals for Energy Met (MU), Peak Demand Met (MW), Shortage (MW), and Renewable Generation outturn (Solar, Wind, Hydro).
   * **Integration Status:** `ACTIVE_VERIFIED`. Ingested via `GridIndiaAdapter` with SHA-256 deduplication and PDF table extraction.
2. **REMC 15-Minute SCADA Telemetry (Enterprise/Restricted):**
   * **Scope:** 96 intraday 15-minute time blocks of active power dispatch, solar/wind schedules, actuals, frequency, and Area Control Error (ACE).
   * **Access Method:** WAMS / Enterprise REST API over secure National Knowledge Network / PowerGrid MPLS VPN.
   * **Integration Status:** **`BLOCKED`** (Strict compliance with Project Rule 1 & Integrity Mandate: No fabrication of enterprise SCADA; clear statutory disclosure).

---

## 2. Ingested Daily PSP Bulletins & Verification

Three primary official Grid-India PSP bulletins are archived on disk, verified, and ingested:

| Bulletin Name | Delivery Date | File Size | SHA-256 Checksum (Prefix) | Extracted Records | Ingestion Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `2024_06_01_NLDC_PSP.pdf` | `2024-06-01` | 442,128 bytes | `7cc16a86aaec0ec5...` | 22 records | `SUCCESS` / `VERIFIED` |
| `2024_06_02_NLDC_PSP.pdf` | `2024-06-02` | 440,789 bytes | `eb45479cb256bca9...` | 22 records | `SUCCESS` / `VERIFIED` |
| `2026_10_31_NLDC_PSP.pdf` | `2026-10-31` | 448,512 bytes | `0689b7b9f5d60f4d...` | 22 records | `SUCCESS` / `VERIFIED` |

---

## 3. Forensic Investigation: 22 Records vs 24 Combinations Mystery

A persistent question during preliminary ingestion audits was why Page 2, Table A (*Power Supply Position at All India and Regional level*) consistently yielded **22 records** instead of the anticipated $4 \times 6 = 24$ records (4 metrics $\times$ 6 geographic entities).

### 3.1 Table A Grid Matrix Structure
Table A evaluates 6 columns:
* **NR:** Northern Region
* **WR:** Western Region
* **SR:** Southern Region
* **ER:** Eastern Region
* **NER:** North Eastern Region
* **TOTAL:** All-India National Aggregate

Against 4 reported operational rows:
1. `Hydro Gen (MU)`
2. `Wind Gen (MU)`
3. `Solar Gen (MU)`
4. `Energy Met (MU)`

### 3.2 Physical Ground Truth
Direct forensic extraction from the primary PDFs reveals:
```
Table A Lines (e.g. 2024-06-01):
Hydro Gen (MU)   326    49    57    31    37    501    (6 numeric values)
Wind Gen (MU)     43   202   126     -     -    371    (4 numeric values, 2 hyphens)
Solar Gen (MU)* 180.60 92.30 120.91  2.98  1.02 398.81   (6 numeric values)
Energy Met (MU) 1785  1629  1226   595    56   5290    (6 numeric values)
```

* **The 2 Missing Combinations:** `Wind Generation in Eastern Region (ER)` and `Wind Generation in North Eastern Region (NER)`.
* **Root Cause:** Commercial utility-scale grid-connected wind installations in India are concentrated exclusively in the windy states of the Western and Southern regions (Gujarat, Maharashtra, Rajasthan, Tamil Nadu, Karnataka, Andhra Pradesh, Madhya Pradesh). Neither the Eastern Region nor the North Eastern Region possesses commercial wind farms connected to the inter-state transmission system.
* **Official NLDC Representation:** The official NLDC report authors print `-` (hyphen) for ER and NER wind generation. The adapter correctly rejects non-numeric entries (`-`), extracting:
  $$6 (\text{Hydro}) + 4 (\text{Wind}) + 6 (\text{Solar}) + 6 (\text{Energy Met}) = 22 \text{ records}$$
* **Conclusion:** The extraction of 22 records is **physically and statistically 100% accurate**, exactly mirroring the real Indian grid topology and the primary government bulletin.

---

## 4. Data Model Decoupling & Operational Demand Architecture

In accordance with Part 3 requirements, operational demand measurements have been separated from electricity generation fuels:

### 4.1 Structural Changes
1. **`DEMAND_MET` Removed from `energy_sources`:**
   * Demand met is an electrical grid load measurement, not a fuel or generator technology.
   * Treating demand met as a generation source skewed total generation figures and corrupted clean RE penetration percentages.
2. **Dedicated Table `daily_operational_metrics`:**
   * Schema:
     * `id`: Primary key
     * `geography_id`: Foreign key to `geographies.id` (covering `IN-TOTAL` and 5 regions)
     * `delivery_date`: Date of delivery
     * `energy_met_mu`: Total system energy met (MU)
     * `peak_demand_met_mw`: Peak demand met (MW)
     * `peak_shortage_mw`: Peak demand shortage (MW)
     * `energy_shortage_mu`: Unserved energy (MU)
     * `source_file_id`: Foreign key to `source_files.id`
     * `data_classification`: Standardized as `VERIFIED_OFFICIAL`
     * `source_provenance`: `Grid Controller of India Limited (NLDC Daily PSP)`
3. **True Renewable Energy Penetration Formula:**
   $$\text{RE Penetration } (\%) = \frac{\sum \text{RE Generation (Solar + Wind + Hydro) } [\text{MU}]}{\text{Total Energy Met } [\text{MU}]} \times 100$$
   On `2024-06-01`, All-India Energy Met was **5,290.0 MU**, with RE generation (Solar 398.81 + Wind 371.0 + Hydro 501.0 = 1,270.81 MU), yielding a clean, source-backed RE penetration of **24.02%**.

---

## 5. Live Grid Telemetry Gap Assessment

| Dimension | Public PSP Reporting | REMC Live SCADA Telemetry |
| :--- | :--- | :--- |
| **Cadence** | Daily ($D+1$) | 15-minute blocks (96 blocks/day) |
| **Protocol** | HTTPS PDF / Excel download | WAMS / REST / IEC 60870-5-104 |
| **Authentication** | Publicly accessible | Enterprise NLDC/RLDC Credentials + VPN |
| **WindScope India Status** | **ACTIVE & INGESTED** | **BLOCKED (Statutory disclosure)** |
| **Remedy Required** | Maintained automated scraper | NLDC REMC API partner credentials |

WindScope India enforces zero tolerance for simulated data masquerading as official live SCADA. All 15-minute dispatch blocks are tagged transparently as `DEMONSTRATION` until enterprise credentials can be configured.

