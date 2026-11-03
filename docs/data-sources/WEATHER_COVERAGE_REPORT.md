# WindScope India — Weather Coverage & Meteorological Intelligence Report

**Document Reference:** `WINDSCOPE_INDIA_WEATHER_COVERAGE_REPORT.md`  
**Date:** November 1, 2026  
**Provider:** Open-Meteo Historical Archive / ECMWF ERA5 Reanalysis  
**Primary Working Directory:** `D:\WindScopeIndia`  

---

## Executive Summary

This report documents the expansion and forensic validation of meteorological data within **WindScope India**. The database now maintains **12,096 genuine hourly meteorological observations** spanning all 36 Indian States and Union Territories across two representative seasonal regimes:
1. **June 1–7, 2024:** Onset of the Southwest Monsoon (high wind speeds in Gujarat/Tamil Nadu, convective cloud cover).
2. **December 1–7, 2024:** Winter high-pressure regime (moderate wind, stable high solar DNI across southern and western peninsulas, northern winter inversions).

---

## 1. Meteorological Parameters & Schema

Every observation is stored in `weather_observations` with full geographical and technical provenance:

| Parameter | Unit | Physical Significance | Primary Engine Usage |
| :--- | :--- | :--- | :--- |
| `wind_speed_100m_ms` | $\text{m/s}$ | Hub-height wind velocity for modern 2–3 MW utility wind turbines | Wind generation power curve estimation |
| `wind_speed_10m_ms` | $\text{m/s}$ | Standard surface anemometer measurement | Roughness extrapolation & surface drag validation |
| `wind_direction_deg` | Degrees ($^\circ$) | Hub-height wind direction ($0^\circ - 360^\circ$) | Wake loss modeling & directional shear |
| `solar_ghi_wm2` | $\text{W/m}^2$ | Global Horizontal Irradiance | Standard tilted-plane photovoltaic module conversion |
| `solar_dni_wm2` | $\text{W/m}^2$ | Direct Normal Irradiance | High-efficiency tracking & CSP potential estimation |
| `temperature_celsius` | $^\circ\text{C}$ | Ambient dry-bulb temperature | PV module temperature derating ($-0.35\%/^\circ\text{C}$ above $25^\circ\text{C}$) |
| `cloud_cover_pct` | $\%$ | Total cloud fraction | Diffuse irradiance attenuation |
| `precipitation_mm` | $\text{mm}$ | Hourly rainfall accumulation | PV soiling wash-off vs extreme storm cut-out |

---

## 2. Ingestion & Temporal Coverage Summary

### 2.1 Database Record Counts
* **Total Weather Observations:** **12,096** hourly records.
* **Geographical Scope:** 36 States and Union Territories (100% census/ISO coverage).
* **Idempotency & Deduplication:** Enforced through composite natural key `(geography_id, observation_time)`.
* **API Ingestion Performance:** 36 API requests pacing at 0.3s intervals completed with **0 failures and 0 dropped records**.

### 2.2 Temporal Batches
```
Batch 1: June 1, 2024 00:00 IST – June 7, 2024 23:00 IST (168 hours × 36 states = 6,048 records)
Batch 2: Dec 1, 2024 00:00 IST – Dec 7, 2024 23:00 IST (168 hours × 36 states = 6,048 records)
Total: 12,096 records
```

---

## 3. Provenance & Reanalysis Classification

Per Part 5.2 guidelines, all meteorological data is classified with explicit epistemological categories:

* **`REANALYSIS`:** Applied to all 12,096 records ingested via the Open-Meteo Historical Archive API. Reanalysis integrates historical ground observations, satellite radiances, and sounding balloons through ECMWF IFS data assimilation to produce physically consistent historical states.
* **`LIVE_FORECAST` / `LIVE_OBSERVATION`:** Reserved for real-time inference queries calling Open-Meteo's 7-day GFS/ECMWF operational numerical weather prediction (NWP) runs.
* **Separation Enforcement:** The backend API returns the `record_type` and `weather_model` in all payload responses so downstream analytics never mistake an ERA5 assimilated reanalysis point for an uncalibrated live forecast.

---

## 4. Centroid Limitations & Renewable Energy Zone (REZ) Roadmap

### 4.1 Physical Limitation of State Centroids
The current implementation samples weather at the geographic centroid of each State and Union Territory. While this provides uniform spatial coverage across the 36 jurisdictions, it introduces spatial representation bias:
* **Gujarat:** Centroid $(22.2587^\circ\text{N}, 71.1924^\circ\text{E})$ lies inland in Rajkot district, whereas the highest-capacity wind farms are situated along the coastal Gulf of Kutch (Mandvi, Jakhau) and Gulf of Khambhat.
* **Rajasthan:** Centroid $(27.0238^\circ\text{N}, 74.2179^\circ\text{E})$ lies in Nagaur district, whereas ultra-mega solar parks are clustered in the Thar Desert (Bhadla in Phalodi district, Fatehgarh in Jaisalmer).
* **Tamil Nadu:** Centroid $(11.1271^\circ\text{N}, 78.6569^\circ\text{E})$ lies near Tiruchirappalli, whereas the world-famous Muppandal wind corridor is located in the Palghat/Aralvaimozhi mountain passes in Kanyakumari/Tirunelveli.

### 4.2 Proposed REZ Park Coordinates
For Phase 8 and enterprise deployments, the architecture is designed to support high-density coordinate sampling at designated Renewable Energy Zones:

| Zone / Park | State | Latitude | Longitude | Primary Technology |
| :--- | :--- | :--- | :--- | :--- |
| **Bhadla Solar Park** | Rajasthan | $27.5385^\circ\text{N}$ | $71.9189^\circ\text{E}$ | Solar PV (2,245 MW) |
| **Khavda RE Park** | Gujarat | $23.8500^\circ\text{N}$ | $69.7500^\circ\text{E}$ | Hybrid Wind-Solar (30 GW target) |
| **Pavagada Solar Park** | Karnataka | $14.0950^\circ\text{N}$ | $77.2750^\circ\text{E}$ | Solar PV (2,050 MW) |
| **Muppandal Wind Complex** | Tamil Nadu | $8.2583^\circ\text{N}$ | $77.5458^\circ\text{E}$ | Wind Turbines (1,500 MW) |
| **Rewa Ultra Mega Solar** | Madhya Pradesh | $24.4820^\circ\text{N}$ | $81.5740^\circ\text{E}$ | Solar PV (750 MW) |
| **Ananthapuramu Solar Park** | Andhra Pradesh | $14.9750^\circ\text{N}$ | $77.4580^\circ\text{E}$ | Solar PV (1,500 MW) |

