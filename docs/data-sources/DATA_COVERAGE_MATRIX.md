# WindScope India — Data Coverage Matrix
## Historical Multi-Year Inventory, Provenance Classification & Observation Audit

**Document Version:** 1.0.0  
**Project:** WindScope India — Renewable Energy Intelligence Platform  
**Target Repository:** `D:\WindScopeIndia`  
**Execution Date:** 01 November 2026  
**Auditor / Architecture Role:** Lead Data Quality Auditor, Senior Data Engineer  

---

## 1. Executive Summary

This Data Coverage Matrix provides an exhaustive inventory of all 16,134 monthly generation records, 1,528 installed capacity records, and 10 national reconciliation audits currently held in the WindScope India platform.

Every record is cataloged with strict adherence to data provenance:
- **`VERIFIED_OFFICIAL`:** Directly extracted from original statutory PDF gazettes and publications (CEA OPM Sub-Reports 1 & 16, NPP Installed Capacity Bulletins).
- **`OFFICIAL_SOURCE_UNVERIFIED`:** Extracted from intermediate CSV extractions (CEA REMD June 2024 and December 2024) quarantined from official status.
- **`DEMONSTRATION`:** Synthetic multi-year benchmark records clearly flagged with UI notices to enable offline modeling and frontend testing across 2020–2026.

---

## 2. Platform Summary Metrics

| Metric Dimension | Record Count | Notes / Provenance Standard |
| :--- | :--- | :--- |
| **Total Monthly Generation Records** | **16,134** | Covers 2020–2026 across 36 States/UTs and 6 fuel types |
| — `DEMONSTRATION` Records | 15,768 | Calibrated multi-year synthetic baseline |
| — `OFFICIAL_SOURCE_UNVERIFIED` Records | 360 | June 2024 (180 records) + Dec 2024 (180 records) |
| — `VERIFIED_OFFICIAL` Records | 6 | CEA Sub-Report 1 (June 2024: 3, Sept 2026: 3) |
| **Total Installed Capacity Records** | **1,528** | State-level and national capacity by technology |
| — `VERIFIED_OFFICIAL` Capacity Records | 16 | NPP Capacity Bulletins (June 2024 & Sept 2026) |
| — `DEMONSTRATION` Capacity Records | 1,512 | Historical capacity progression (2020–2026) |
| **Total Registered Source Files** | **8** | 4 Official CEA/NPP PDFs + 2 Ingested CSVs + 2 Capacity PDFs |
| **National Reconciliation Audits** | **10** | Standardized sum-of-states vs national total checks |
| **Geographic Entities Covered** | **36** | 28 States + 8 Union Territories + National Aggregate |
| **Renewable Fuel Types Monitored** | **6** | Wind, Solar, Large Hydro, Small Hydro, Biomass, Other RE |

---

## 3. Observation Status Breakdown

Under the strict observation auditor (`backend/app/services/ingestion/observation_auditor.py`), every data cell is classified into a statistical observation status:

| Observation Status | Record Count | Description & Provenance Grounding |
| :--- | :--- | :--- |
| `REPORTED_VALUE` | **10,949** | Positive reported generation outturn ($>0.0$ MU). |
| `UNVERIFIED_ZERO` | **5,185** | Explicit numeric 0.00 in unverified records (5,037 demonstration zeros + 148 CSV zeros). |
| `VERIFIED_REPORTED_ZERO` | **0** | Verified official numeric zero confirmed in published gazettes. |
| `PHYSICAL_ZERO_CONFIRMED` | **0** | **Strictly 0.** Never claimed without physical revenue-grade metering certificates. |
| `MISSING_OBSERVATION` | **0** | Missing, blank, or hyphenated cells (represented as NULL in database). |
| **Total Generation Slices** | **16,134** | Sum of all audited observation statuses |

---

## 4. Multi-Year Coverage Matrix (2020–2026)

| Evaluation Period | Reporting Months | Fuel Coverage | Geographic Scope | Primary Classification | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2020** | Jan – Dec (12) | Wind, Solar, Large Hydro, Small Hydro, Biomass, Other RE | 28 States + 8 UTs | `DEMONSTRATION` | Calibrated Baseline |
| **2021** | Jan – Dec (12) | Wind, Solar, Large Hydro, Small Hydro, Biomass, Other RE | 28 States + 8 UTs | `DEMONSTRATION` | Calibrated Baseline |
| **2022** | Jan – Dec (12) | Wind, Solar, Large Hydro, Small Hydro, Biomass, Other RE | 28 States + 8 UTs | `DEMONSTRATION` | Calibrated Baseline |
| **2023** | Jan – Dec (12) | Wind, Solar, Large Hydro, Small Hydro, Biomass, Other RE | 28 States + 8 UTs | `DEMONSTRATION` | Calibrated Baseline |
| **2024 (H1 - June)** | June 2024 | Wind, Solar, Large Hydro, Small Hydro, Biomass, Other RE | 28 States + 8 UTs | `VERIFIED_OFFICIAL` + `OFFICIAL_SOURCE_UNVERIFIED` | CEA Sub-Report 1 & NPP Capacity Verified; CSV Quarantined |
| **2024 (Other Months)**| Jan–May, Jul–Dec | Wind, Solar, Large Hydro, Small Hydro, Biomass, Other RE | 28 States + 8 UTs | `DEMONSTRATION` (Dec CSV quarantined) | Demonstrative baseline |
| **2025** | Jan – Dec (12) | Wind, Solar, Large Hydro, Small Hydro, Biomass, Other RE | 28 States + 8 UTs | `DEMONSTRATION` | Calibrated Baseline |
| **2026 (Sept)** | Sept 2026 | Large Hydro, Thermal, Nuclear, Solar, Wind | 28 States + 8 UTs | `VERIFIED_OFFICIAL` + `DEMONSTRATION` | CEA Sub-Report 1 & NPP Capacity Verified |
| **2026 (Other Months)**| Jan–Aug, Oct–Dec | Wind, Solar, Large Hydro, Small Hydro, Biomass, Other RE | 28 States + 8 UTs | `DEMONSTRATION` | Evaluated benchmark scope |

---

## 5. National Reconciliation Audit Matrix

The platform executes national sum reconciliation audits to verify whether sum-of-states aggregates reconcile with published All-India headline totals:

| Period | Energy Source | Published Total (MU) | State Sum (MU) | Abs Variance (MU) | Variance (%) | Reconciliation Status | Source Reference |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2024-06** | Large Hydro | 13,445.69 | 13,445.69 | 0.00 | 0.00% | `VERIFIED_ZERO_VARIANCE` | CEA Sub-Report 1, Page 3 |
| **2024-06** | Wind | 14,812.34 | 14,812.34 | 0.00 | 0.00% | `VERIFIED_ZERO_VARIANCE` | CEA Sub-Report 16, Table 2 |
| **2024-06** | Small Hydro | 810.15 | 810.15 | 0.00 | 0.00% | `VERIFIED_ZERO_VARIANCE` | CEA Sub-Report 16, Table 4 |
| **2024-06** | Solar | 10,250.00 | 10,122.80 | 127.20 | -1.24% | `UNVERIFIED_STATE_SUM` | CEA REMD CSV Discrepancy |
| **2024-06** | Biomass | 350.00 | 347.00 | 3.00 | -0.86% | `UNVERIFIED_STATE_SUM` | CEA REMD CSV Discrepancy |
| **2024-06** | Thermal | 115,200.00 | NULL | NULL | NULL | `NATIONAL_TOTAL_ONLY` | CEA Sub-Report 1 (No state sum) |
| **2024-06** | Nuclear | 4,120.00 | NULL | NULL | NULL | `NATIONAL_TOTAL_ONLY` | CEA Sub-Report 1 (No state sum) |
| **2024-12** | Biomass | 380.00 | 374.10 | 5.90 | -1.55% | `UNVERIFIED_STATE_SUM` | CEA REMD CSV Discrepancy |
| **2026-09** | Large Hydro | 14,920.40 | 14,920.40 | 0.00 | 0.00% | `VERIFIED_ZERO_VARIANCE` | CEA Sub-Report 1, Page 3 |
| **2026-09** | Clean RE Total| 29,480.00 | 29,480.00 | 0.00 | 0.00% | `VERIFIED_ZERO_VARIANCE` | NPP Executive Summary |

---

## 6. Official Source Documents Registry

| ID | Filename | Source Authority | Reporting Period | SHA-256 Checksum (Prefix) | Extraction Status | Records Extracted |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `2024_06_capacity1-2024-06.pdf` | NPP / CEA | 2024-06-30 | `63b827cb6b5f...` | `COMPLETED` | 8 |
| 2 | `2026_09_capacity1-2026-09.pdf` | NPP / CEA | 2026-09-30 | `a4959db87cc4...` | `COMPLETED` | 8 |
| 3 | `2024_06_CEA_RE_Monthly_June_2024.csv` | CEA REMD | 2024-06 | `2467b7f14ad1...` | `UNVERIFIED_SOURCE` | 180 |
| 4 | `2024_12_CEA_RE_Monthly_December_2024.csv` | CEA REMD | 2024-12 | `365113a10521...` | `UNVERIFIED_SOURCE` | 180 |
| 5 | `2024_06_18_col_act-16_2024-JUN.pdf` | CEA OPM | 2024-06 | `5a7bb91845eb...` | `COMPLETED` | Station-Level |
| 6 | `2024_06_18_col_act-1_2024-JUN.pdf` | CEA OPM | 2024-06 | `02909f2ea700...` | `COMPLETED` | 3 |
| 7 | `2026_09_18_col_act-16_2026-SEP.pdf` | CEA OPM | 2026-09 | `30a845946399...` | `COMPLETED` | Station-Level |
| 8 | `2026_09_18_col_act-1_2026-SEP.pdf` | CEA OPM | 2026-09 | `6d2a71fef4d8...` | `COMPLETED` | 3 |

---

## 7. Geographic Entities Monitored (36 States & UTs)

1. **Northern Region (NRPC):** Delhi (`IN-DL`), Haryana (`IN-HR`), Himachal Pradesh (`IN-HP`), Jammu and Kashmir (`IN-JK`), Ladakh (`IN-LA`), Punjab (`IN-PB`), Rajasthan (`IN-RJ`), Uttar Pradesh (`IN-UP`), Uttarakhand (`IN-UT`), Chandigarh (`IN-CH`).
2. **Western Region (WRPC):** Gujarat (`IN-GJ`), Maharashtra (`IN-MH`), Madhya Pradesh (`IN-MP`), Chhattisgarh (`IN-CT`), Goa (`IN-GA`), Dadra and Nagar Haveli and Daman and Diu (`IN-DH`).
3. **Southern Region (SRPC):** Andhra Pradesh (`IN-AP`), Karnataka (`IN-KA`), Kerala (`IN-KL`), Tamil Nadu (`IN-TN`), Telangana (`IN-TG`), Puducherry (`IN-PY`), Lakshadweep (`IN-LD`), Andaman and Nicobar Islands (`IN-AN`).
4. **Eastern Region (ERPC):** Bihar (`IN-BR`), Jharkhand (`IN-JH`), Odisha (`IN-OR`), West Bengal (`IN-WB`), Sikkim (`IN-SK`).
5. **North-Eastern Region (NERPC):** Assam (`IN-AS`), Arunachal Pradesh (`IN-AR`), Manipur (`IN-MN`), Meghalaya (`IN-ML`), Mizoram (`IN-MZ`), Nagaland (`IN-NL`), Tripura (`IN-TR`).

All entities are verified with zero data loss or unassigned national aggregates.

