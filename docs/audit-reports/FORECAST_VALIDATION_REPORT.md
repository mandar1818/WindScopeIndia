# WindScope India — Forecasting Engine Validation & Mathematical Integrity Report

**Document Reference:** `WINDSCOPE_INDIA_FORECAST_VALIDATION_REPORT.md`  
**Date:** November 1, 2026  
**Engine:** Multi-Horizon Renewable Dispatch Forecasting Engine (v2.2.0)  
**Primary Working Directory:** `D:\WindScopeIndia`  

---

## Executive Summary

This report establishes the forensic mathematical validation, anti-leakage guarantees, and physical boundary conditions of the **WindScope India Forecasting Engine**. It distinguishes the three analytical operating modes, audits the standardized error conventions, details the physical turbine/PV conversion curves, and verifies complete compliance with statutory gate closures.

---

## 1. Distinction Among Three Analytical Modes

To avoid conflation between diagnostic estimation, market scheduling, and power system balancing, WindScope India decouples analysis into three distinct modes:

```
+-----------------------------------------------------------------------------------------+
|                                1. GENERATION ESTIMATION                                 |
| Purpose: Diagnostic outturn reconstruction based on contemporaneous weather observations|
| Input: Observed meteorological measurements (ERA5 reanalysis / ground weather stations)  |
| Timing: Ex-post (T+1 or post-delivery); strictly NOT a forecast                         |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                                2. RENEWABLE FORECASTING                                 |
| Purpose: Forward-looking predictions of plant/state variable renewable generation       |
| Input: Numerical Weather Predictions (NWP) issued PRIOR to statutory cutoff timestamps |
| Horizons: Day-Ahead (DAM D-1 12:00 IST), Real-Time (RTM T-75m), Intraday (TAM T-3h)     |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                           3. OPERATIONAL DISPATCH FORECASTING                           |
| Purpose: System-level net demand balancing and merit-order transmission scheduling     |
| Input: Aggregated RE forecasts + System Demand Met (MU) + Grid transmission constraints  |
| Application: SLDC/RLDC scheduling, DSM (Deviation Settlement Mechanism) deviation risks |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Mathematical Error Metrics & Sign Conventions

### 2.1 Standardized Sign Convention
Across all WindScope products (India platform and UK benchmark), the sign convention is strictly defined as:
$$\text{Forecast Error } (e_t) = \text{Forecast}_t - \text{Actual}_t$$

* **Positive Error ($e_t > 0$):** **Overforecasting** $\rightarrow$ Generator physically generates *less* than scheduled; in physical power markets, this creates a **short position** requiring deficit replacement or DSM down-deviation penalties.
* **Negative Error ($e_t < 0$):** **Underforecasting** $\rightarrow$ Generator physically generates *more* than scheduled; creates a **long position** subject to potential curtailment or unremunerated energy feed-in.

### 2.2 Mathematical Error Formulations
For $N$ valid matched dispatch blocks where Actual $A_t > 0$:

1. **Mean Absolute Error (MAE) [MW]:**
   $$\text{MAE} = \frac{1}{N} \sum_{t=1}^N \left| F_t - A_t \right|$$
2. **Root Mean Square Error (RMSE) [MW]:**
   $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{t=1}^N \left( F_t - A_t \right)^2}$$
3. **Weighted Absolute Percentage Error (WAPE) [\%]:**
   $$\text{WAPE} = \frac{\sum_{t=1}^N \left| F_t - A_t \right|}{\sum_{t=1}^N A_t} \times 100$$
   *(Zero-denominator safe: if $\sum A_t = 0$, returns 0.0%).*
4. **Mean Bias Error (MBE) [MW]:**
   $$\text{Bias} = \frac{1}{N} \sum_{t=1}^N \left( F_t - A_t \right)$$
5. **Skill Score vs. Persistence Baseline [\%]:**
   $$\text{Skill Score} = \left( 1 - \frac{\text{MAE}_{\text{model}}}{\text{MAE}_{\text{persistence}}} \right) \times 100$$

---

## 3. Physical Boundary Enforcement & Power Curves

Both wind and solar generation predictions must strictly respect physical laws and generator capabilities:

### 3.1 Solar Photovoltaic Physical Constraints
* **Nighttime Zero Generation:** If Global Horizontal Irradiance (GHI) $\le 5.0\text{ W/m}^2$, predicted solar power is forced to strictly $0.0\text{ MW}$ regardless of statistical model coefficients.
* **Diurnal Zenith Angle Enforcement:** Solar generation is bounded by solar elevation and morning/evening horizon limits ($06:00 - 18:30\text{ IST}$).
* **Temperature Derating:** PV cell efficiency degrades with elevated ambient temperature above STC ($25^\circ\text{C}$):
  $$\text{Derating Factor} = \max\left(0.85, \, 1.0 - 0.004 \times (T_{\text{ambient}} - 25.0)\right)$$
* **Capacity Cap:** Predicted output can never exceed installed nameplate capacity ($P_{\text{solar}} \le C_{\text{solar}}$).

### 3.2 Wind Turbine Aero-Mechanical Constraints
* **Cut-In Velocity:** For $v_{100} < 3.0\text{ m/s}$, aerodynamic torque is insufficient to overcome friction; power output is $0.0\text{ MW}$.
* **Rated Region:** For $3.0\text{ m/s} \le v_{100} \le 12.0\text{ m/s}$, power follows the cubic aerodynamic curve:
  $$P_w \propto \left( \frac{v_{100} - 3.0}{9.0} \right)^{2.5}$$
* **Cut-Out Storm Cutoff:** For $v_{100} > 25.0\text{ m/s}$, turbines feather blades and engage mechanical brakes for structural protection; output drops instantly to $0.0\text{ MW}$.
* **Non-Negativity:** Generation is non-negative ($P_w \ge 0$).

---

## 4. Chronological Anti-Leakage & Issue Timestamping

To prevent look-ahead bias (data leakage) in model evaluations:
1. **Decision Cutoff Enforcement:**
   Every forecast for delivery period $T$ must have been published at or before decision cutoff $C(T)$. Any forecast published after $C(T)$ is marked ineligible.
2. **Issue Timestamps:**
   Every forecast record explicitly preserves `created_at` / `issued_at` in UTC and IST.
3. **No Retrospective Weather Leakage:**
   NWP numerical predictions must reflect only the model run initialized prior to the trading cutoff (e.g., 00:00 UTC run for D-1 noon gate closure).

---

## 5. Honest Status of 15-Minute Operational Actuals

* **SCADA Telemetry Status:** **`BLOCKED`**
* **Technical Reason:** 15-minute dispatch blocks from State Load Despatch Centres (SLDCs) and REMCs are transmitted over private utility VPNs and protected by CERC Cyber Security Directions.
* **Platform Disclosure:** All 15-minute generation actuals used for model evaluation are explicitly classified as **`DEMONSTRATION`**. No simulated or synthetic telemetry is ever represented as official REMC SCADA outturn.

