import React from 'react';
import {
  BookOpen,
  Scale,
  Calculator,
  ShieldCheck,
  FileText,
  Layers,
  Database,
  Building,
  CheckCircle2,
} from 'lucide-react';

export const IndiaMethodologyPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="rounded-lg border border-nature-border bg-white p-5 shadow-sm space-y-2">
        <div className="flex items-center space-x-2">
          <BookOpen className="w-5 h-5 text-nature-forest" />
          <h1 className="text-xl font-bold text-nature-text">
            Technical Methodology &amp; Statutory Standards
          </h1>
        </div>
        <p className="text-xs text-nature-muted leading-relaxed">
          Comprehensive documentation of regulatory frameworks, unit conventions, mathematical formulas, and data provenance governing the WindScope India platform.
        </p>
      </div>

      {/* 1. Statutory Framework */}
      <div className="rounded-lg border border-nature-border bg-white p-5 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-nature-border pb-3">
          <Scale className="w-4 h-4 text-nature-forest" />
          <h2 className="text-sm font-semibold text-nature-text">
            1. Statutory &amp; Regulatory Framework
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="p-3 rounded border border-nature-border bg-nature-bg/40 space-y-1.5">
            <span className="font-semibold text-nature-forest block">
              Central Electricity Authority (CEA)
            </span>
            <p className="text-nature-muted leading-relaxed">
              Established under Section 70 of the Electricity Act, 2003. CEA serves as the statutory authority mandated under Section 73 to collect, compile, and publish national electricity generation, transmission, and capacity statistics across all Indian states and Union Territories.
            </p>
          </div>

          <div className="p-3 rounded border border-nature-border bg-nature-bg/40 space-y-1.5">
            <span className="font-semibold text-nature-forest block">
              CERC Indian Electricity Grid Code (IEGC) 2023
            </span>
            <p className="text-nature-muted leading-relaxed">
              Central Electricity Regulatory Commission (CERC) regulations mandate 96 intraday 15-minute time-blocks for scheduling, dispatch, and Deviation Settlement Mechanism (DSM) tracking of renewable energy feeding the Inter-State Transmission System (ISTS).
            </p>
          </div>

          <div className="p-3 rounded border border-nature-border bg-nature-bg/40 space-y-1.5">
            <span className="font-semibold text-nature-forest block">
              Renewable Energy Management Centres (REMC)
            </span>
            <p className="text-nature-muted leading-relaxed">
              Specialized grid monitoring centers deployed across SLDCs, RLDCs, and NLDC to perform automated day-ahead and intraday forecasting for wind and solar plants, ensuring grid stability in high-RE penetration zones.
            </p>
          </div>

          <div className="p-3 rounded border border-nature-border bg-nature-bg/40 space-y-1.5">
            <span className="font-semibold text-nature-forest block">
              Ministry of Power Hydro Reclassification (March 2019)
            </span>
            <p className="text-nature-muted leading-relaxed">
              Under Government of India Order No. 23/03/2016-R&amp;R, Large Hydroelectric Projects (&gt;25 MW) are recognized as Renewable Energy sources, participating in Renewable Purchase Obligations (Hydro Purchase Obligation - HPO).
            </p>
          </div>
        </div>
      </div>

      {/* 2. Standard Units and Conversions */}
      <div className="rounded-lg border border-nature-border bg-white p-5 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-nature-border pb-3">
          <Layers className="w-4 h-4 text-nature-forest" />
          <h2 className="text-sm font-semibold text-nature-text">
            2. Standard Units &amp; Mathematical Conversions
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded border border-nature-border bg-white space-y-1">
            <span className="font-semibold text-nature-text block">Million Units (MU)</span>
            <p className="text-[11px] text-nature-muted">
              Primary generation unit in Indian utility reporting.
            </p>
            <div className="font-mono text-[11px] text-nature-forest bg-nature-forest-light p-1.5 rounded mt-1">
              1 MU = 1 GWh = 1,000 MWh = 10⁶ kWh
            </div>
          </div>

          <div className="p-3 rounded border border-nature-border bg-white space-y-1">
            <span className="font-semibold text-nature-text block">Capacity (MW &amp; GW)</span>
            <p className="text-[11px] text-nature-muted">
              Nameplate peak capacity at standard test conditions.
            </p>
            <div className="font-mono text-[11px] text-nature-forest bg-nature-forest-light p-1.5 rounded mt-1">
              1 GW = 1,000 MW = 1,000,000 kW
            </div>
          </div>

          <div className="p-3 rounded border border-nature-border bg-white space-y-1">
            <span className="font-semibold text-nature-text block">15-Minute Time Block Energy</span>
            <p className="text-[11px] text-nature-muted">
              Energy delivered across 15-minute grid interval.
            </p>
            <div className="font-mono text-[11px] text-nature-forest bg-nature-forest-light p-1.5 rounded mt-1">
              Energy (MWh) = Power (MW) × 0.25 h
            </div>
          </div>
        </div>
      </div>

      {/* 3. Mathematical Error & Performance Formulas */}
      <div className="rounded-lg border border-nature-border bg-white p-5 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-nature-border pb-3">
          <Calculator className="w-4 h-4 text-nature-forest" />
          <h2 className="text-sm font-semibold text-nature-text">
            3. Quantitative Analytics &amp; Accuracy Formulations
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {/* CUF */}
          <div className="p-3.5 rounded border border-nature-border bg-nature-bg/30 space-y-2">
            <span className="font-semibold text-nature-text block">
              Capacity Utilization Factor (CUF %)
            </span>
            <p className="text-nature-muted leading-relaxed">
              Ratio of the actual energy generated over a given period to the maximum possible energy output if operated continuously at rated peak capacity.
            </p>
            <div className="font-mono text-xs bg-white p-2 rounded border border-nature-border text-nature-text text-center">
              CUF (%) = [ Generation (MWh) / ( Capacity (MW) × Hours in Period ) ] × 100
            </div>
          </div>

          {/* WAPE */}
          <div className="p-3.5 rounded border border-nature-border bg-nature-bg/30 space-y-2">
            <span className="font-semibold text-nature-text block">
              Weighted Absolute Percentage Error (WAPE %)
            </span>
            <p className="text-nature-muted leading-relaxed">
              Primary normalized metric used by REMCs to measure day-ahead forecasting accuracy without distortion from near-zero night generation.
            </p>
            <div className="font-mono text-xs bg-white p-2 rounded border border-nature-border text-nature-text text-center">
              WAPE (%) = [ Σ |Actual_t - Forecast_t| / Σ Actual_t ] × 100
            </div>
          </div>

          {/* MAE & RMSE */}
          <div className="p-3.5 rounded border border-nature-border bg-nature-bg/30 space-y-2">
            <span className="font-semibold text-nature-text block">
              Mean Absolute Error (MAE) &amp; Root Mean Squared Error (RMSE)
            </span>
            <p className="text-nature-muted leading-relaxed">
              MAE represents average linear deviation; RMSE applies quadratic penalty to penalize large scheduling errors that risk grid frequency limits.
            </p>
            <div className="font-mono text-xs bg-white p-2 rounded border border-nature-border text-nature-text text-center">
              MAE = (1/N) Σ |Actual - Forecast| &bull; RMSE = √[ (1/N) Σ (Actual - Forecast)² ]
            </div>
          </div>

          {/* Signed Bias */}
          <div className="p-3.5 rounded border border-nature-border bg-nature-bg/30 space-y-2">
            <span className="font-semibold text-nature-text block">
              Signed Forecast Bias (MW)
            </span>
            <p className="text-nature-muted leading-relaxed">
              Measures directional tendency of forecasting algorithms. Positive bias indicates systematic over-forecasting (leading to shortfall and DSM penalties).
            </p>
            <div className="font-mono text-xs bg-white p-2 rounded border border-nature-border text-nature-text text-center">
              Bias = (1/N) Σ (Forecast_t - Actual_t)
            </div>
          </div>
        </div>
      </div>

      {/* 4. Renewable Energy Accounting Framework */}
      <div className="rounded-lg border border-nature-border bg-white p-5 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-nature-border pb-3">
          <Layers className="w-4 h-4 text-nature-forest" />
          <h2 className="text-sm font-semibold text-nature-text">
            4. Statutory Renewable Energy &amp; Non-Fossil Accounting Framework
          </h2>
        </div>

        <p className="text-xs text-nature-muted leading-relaxed">
          In compliance with CERC reporting standards and Ministry of Power mandates, WindScope India defines and calculates four distinct renewable and clean energy metrics based on Grid Controller of India Limited (NLDC PSP Table A and Table G):
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="p-3 rounded border border-nature-border bg-amber-50/50 space-y-1.5">
            <span className="font-semibold text-amber-950 block">
              Measure A: Variable Renewable Energy (VRE)
            </span>
            <div className="font-mono text-[11px] text-amber-900 bg-white p-1 rounded border border-amber-200">
              Formula: (Wind + Solar) / Demand Met × 100
            </div>
            <p className="text-amber-800 text-[11px]">
              Illustrative Benchmark (June 1, 2024): (371 + 398) / 5,290 × 100 = <strong>14.54%</strong>. Measures intermittent generation that directly influences grid ramp rate and reserves.
            </p>
          </div>

          <div className="p-3 rounded border border-nature-border bg-emerald-50/50 space-y-1.5">
            <span className="font-semibold text-emerald-950 block">
              Measure B: Renewable Energy Excluding Large Hydro
            </span>
            <div className="font-mono text-[11px] text-emerald-900 bg-white p-1 rounded border border-emerald-200">
              Formula: (Wind + Solar + Biomass &amp; Others) / Demand Met × 100
            </div>
            <p className="text-emerald-800 text-[11px]">
              Illustrative Benchmark (June 1, 2024): (371 + 398 + 35) / 5,290 × 100 = 804 / 5,290 × 100 = <strong>15.20%</strong>. Corresponds to the official RES category in Table G.
            </p>
          </div>

          <div className="p-3 rounded border border-nature-border bg-emerald-50/70 space-y-1.5">
            <span className="font-semibold text-emerald-950 block">
              Measure C: Total Renewable Energy Including Large Hydro
            </span>
            <div className="font-mono text-[11px] text-emerald-900 bg-white p-1 rounded border border-emerald-300">
              Formula: (Wind + Solar + Biomass &amp; Others + Hydro) / Demand Met × 100
            </div>
            <p className="text-emerald-800 text-[11px]">
              Illustrative Benchmark (June 1, 2024): (804 + 501) / 5,290 × 100 = 1,305 / 5,290 × 100 = <strong>24.67%</strong>. Reflects Ministry of Power Order (March 2019) recognizing large hydro as renewable.
            </p>
          </div>

          <div className="p-3 rounded border border-nature-border bg-blue-50/50 space-y-1.5">
            <span className="font-semibold text-blue-950 block">
              Measure D: Non-Fossil Share of Gross Generation
            </span>
            <div className="font-mono text-[11px] text-blue-900 bg-white p-1 rounded border border-blue-200">
              Formula: (Hydro + Nuclear + RES) / Gross Generation × 100
            </div>
            <p className="text-blue-800 text-[11px]">
              Illustrative Benchmark (June 1, 2024): (501 + 145 + 804) / 5,706 × 100 = 1,450 / 5,706 × 100 = <strong>25.41%</strong>. Measures total clean electricity output including civil nuclear power.
            </p>
          </div>
        </div>

        <div className="p-2.5 rounded bg-nature-bg border border-nature-border text-[11px] text-nature-muted leading-relaxed">
          <strong className="text-nature-text">Double-Counting Prevention Audit:</strong> In Grid-India NLDC Table G, the RES category (804 MU) is composed of Wind (371 MU) + Solar (398 MU) + Biomass &amp; Others (35 MU). Hydro (501 MU) and Nuclear (145 MU) are reported in independent rows. Hydro is never added twice; zero double counting exists in the analytical engine.
        </div>
      </div>

      {/* 5. Data Provenance & Model Demonstration Disclosures */}
      <div className="rounded-lg border border-emerald-200 bg-emerald-50/40 p-5 shadow-sm space-y-3">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-nature-forest" />
          <h3 className="text-sm font-semibold text-nature-forest">
            5. Data Provenance &amp; Demonstration Model Disclosures
          </h3>
        </div>
        <p className="text-xs text-nature-text leading-relaxed">
          WindScope India operates under an explicit data integrity and transparent provenance policy:
        </p>
        <ul className="space-y-1.5 text-xs text-nature-text/90 list-disc list-inside">
          <li>
            <strong>Demonstration Dataset Classification:</strong> The multi-year time-series (2020–2026), intraday 15-minute scheduling blocks, and meteorological correlations represent a calibrated demonstration model developed to evaluate CERC IEGC forecasting metrics, rather than live government API feeds.
          </li>
          <li>
            <strong>Physical Zero-Fleet Jurisdictions:</strong> Non-wind states (e.g. Bihar, Assam, Delhi, Uttar Pradesh, Punjab) feature strictly 0.0 MW installed wind turbine capacity and 0.000 MU generation based on NIWE commercial wind density thresholds. These confirmed physical zeros are distinguished from missing observations.
          </li>
          <li>
            <strong>Distinction of Data States:</strong> The platform distinguishes confirmed zero generation, missing observations, not applicable resources, and demonstration model projections.
          </li>
          <li>
            <strong>Preserved UK Benchmark:</strong> The existing January 2026 UK offshore/onshore wind Day-Ahead forecasting evaluation is permanently archived in Git tag <code className="font-mono bg-white px-1 py-0.5 rounded border border-emerald-300">uk-benchmark-v1.0</code> and accessible via the benchmark viewer.
          </li>
        </ul>
      </div>
    </div>
  );
};

