# WindScope India — Market Rules & Statutory Gate Closure Audit

**Document Reference:** `WINDSCOPE_INDIA_MARKET_RULES_AUDIT.md`  
**Date:** November 1, 2026  
**Statutory Authorities:** Central Electricity Regulatory Commission (CERC) / Grid Controller of India Limited / Elexon (UK)  
**Primary Working Directory:** `D:\WindScopeIndia`  

---

## Executive Summary

This audit establishes the primary statutory foundation for Indian power market trading timelines and gate closures implemented in `backend/app/services/india_market_rules.py`. It verifies the mathematical anti-leakage filters applied to trading horizons (DAM, G-DAM, RTM, TAM) and proves the strict, decoupled preservation of the original **WindScope UK** January 2026 benchmark.

---

## 1. Statutory Framework for Indian Power Markets

Indian wholesale power market segments operate under regulations issued by the Central Electricity Regulatory Commission (CERC) under Sections 66 and 178 of the *Electricity Act, 2003*:

### 1.1 Primary Regulatory Instruments
1. **CERC (Power Market) Regulations, 2021 (PMR 2021):**
   * *Notification:* No. L-1/257/2020/CERC, dated February 15, 2021 (effective August 15, 2021).
   * *Mandate:* Governs power exchange trading, contracts, collective transactions, price coupling, and market clearing rules.
2. **CERC (Open Access in inter-State Transmission) (Sixth Amendment) Regulations, 2019:**
   * *Notification:* Effective June 1, 2020.
   * *Mandate:* Introduced the Real-Time Market (RTM) framework for half-hourly auction clearing.
3. **CERC (Indian Electricity Grid Code) Regulations, 2023 (IEGC 2023):**
   * *Notification:* Effective October 1, 2023.
   * *Mandate:* Codes for unit commitment, day-ahead scheduling, intra-day revision boundaries, and tertiary reserves.
4. **CERC (Deviation Settlement Mechanism and Related Matters) Regulations, 2022:**
   * *Mandate:* Commercial penalties and incentive structures for physical deviation from scheduled generation/drawal.

---

## 2. Product-by-Product Gate Closure Rules

| Product | Statutory Citation | Bidding Window | Gate Closure Cutoff | Delivery Granularity |
| :--- | :--- | :--- | :--- | :--- |
| **Day-Ahead Market (DAM)** | CERC PMR 2021, Regulation 6; IEX Business Rules Chapter 3 | 10:00 to 12:00 IST on Day $D-1$ | **12:00 PM (Noon) IST on $D-1$** | 96 15-minute blocks (00:00 – 24:00 IST) |
| **Green Day-Ahead Market (G-DAM)** | CERC Order in Petition No. 447/MP/2019; PMR 2021 | 10:00 to 12:00 IST on Day $D-1$ | **12:00 PM (Noon) IST on $D-1$** | 96 15-minute blocks (Solar & Non-Solar) |
| **Real-Time Market (RTM)** | CERC OA Regulations 2019; CERC Order 10/SM/2020 | 48 sessions/day (opens $T-105$m, closes $T-75$m) | **$T - 75$ minutes prior to delivery** | 2 15-minute blocks per half-hour session |
| **Term-Ahead Intraday (TAM)** | CERC PMR 2021, Schedule II; PXIL/IEX Rules | Continuous 24x7 trading up to $T-3$h | **$T - 3$ hours prior to delivery** | Hourly and 15-minute bilateral contracts |

### 2.1 Anti-Leakage Implementation
Under `is_forecast_eligible_under_india_market()`:
```python
cutoff_time = calculate_india_market_cutoff(delivery_time, product)
return forecast_publish_time <= cutoff_time
```
Any forecast with publication timestamp $> \text{cutoff}$ is mathematically excluded, guaranteeing that evaluations replicate the exact operational information set available to a trader at gate closure.

---

## 3. Decoupled Preservation of the WindScope UK Benchmark

Per Non-Negotiable Rule 2, the **WindScope UK** January 2026 benchmark is preserved with 100% architectural and statutory independence:

| Dimension | WindScope India | WindScope UK Benchmark |
| :--- | :--- | :--- |
| **Governing Code** | CERC IEGC 2023 / PMR 2021 | Balancing and Settlement Code (BSC), Section Q |
| **System Operator** | Grid Controller of India Limited (NLDC) | National Grid ESO (NESO) |
| **Market Data Provider**| Power Exchanges (IEX, PXIL, HPX) / NLDC | Elexon BMRS / Insights Solution API |
| **Timezone** | `Asia/Kolkata` (UTC+05:30) | `Europe/London` (UTC+00:00 / BST UTC+01:00) |
| **Day-Ahead Gate Closure**| 12:00 PM (Noon) IST on $D-1$ | 11:00 London Time on $D-1$ |
| **Intraday Gate Closure** | $T - 75$ min (RTM) / $T - 3$ hours (TAM) | $T - 1$ hour prior to each 30-min Settlement Period |
| **Delivery Granularity** | 96 15-minute blocks / day | 48 30-minute settlement periods (50 on clock-change) |
| **Service Module** | `app/services/india_market_rules.py` | `app/services/forecast_selector.py` |
| **Regression Suite** | `tests/test_india_market_cutoffs.py` | `tests/test_forecast_selector.py`, `test_api_routes.py` |

### 3.2 Regression Verification
* The UK benchmark test suite executes in `tests/test_api_routes.py` and `tests/test_forecast_selector.py` verifying all January 2026 Elexon mocked outturns.
* The two modules do not share global state, databases, or timezone conversions.

