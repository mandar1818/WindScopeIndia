import React, { useEffect, useState } from 'react';
import {
  Zap,
  Wind,
  Sun,
  Droplets,
  TrendingUp,
  MapPin,
  ArrowRight,
  ShieldCheck,
  Building2,
  Calendar,
} from 'lucide-react';
import { IndiaNationalOverview } from '../../types/india';
import { indiaApi } from '../../services/indiaApi';
import { MetricCard } from '../../components/common/MetricCard';
import { Skeleton, CardSkeleton } from '../../components/common/Skeleton';
import { ErrorAlert } from '../../components/common/ErrorAlert';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';

interface IndiaOverviewPageProps {
  onNavigate: (tabId: string) => void;
}

export const IndiaOverviewPage: React.FC<IndiaOverviewPageProps> = ({ onNavigate }) => {
  const [data, setData] = useState<IndiaNationalOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedYear, setSelectedYear] = useState<number>(2026);
  const [selectedMonth, setSelectedMonth] = useState<number | null>(1);
  const [datasetType, setDatasetType] = useState<
    'VERIFIED_OFFICIAL' | 'OFFICIAL_SOURCE_UNVERIFIED' | 'DEMONSTRATION' | undefined
  >(undefined);
  const [activeMeasure, setActiveMeasure] = useState<
    'vre' | 're_excl_hydro' | 'total_re_incl_hydro' | 'non_fossil'
  >('total_re_incl_hydro');

  const fetchOverview = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await indiaApi.getOverview(selectedYear, selectedMonth, datasetType);
      setData(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to load national overview from Central Electricity Authority backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, [selectedYear, selectedMonth, datasetType]);

  if (loading && !data) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (error && !data) {
    return <ErrorAlert title="National Overview Ingestion Error" message={error} onRetry={fetchOverview} />;
  }

  const solarData = data?.source_breakdown.find((s) => s.source_code === 'SOLAR');
  const windData = data?.source_breakdown.find((s) => s.source_code === 'WIND');
  const hydroData = data?.source_breakdown.find((s) => s.source_code === 'LARGE_HYDRO');

  const fuelColors: Record<string, string> = {
    SOLAR: '#D49A42',       // Solar amber
    WIND: '#26966B',        // Wind green
    LARGE_HYDRO: '#5689B5', // Hydro blue
    SMALL_HYDRO: '#8FAE91', // Small hydro sage
    BIOMASS: '#8A5D3B',     // Biomass earth
    OTHER_RE: '#748078',    // Other neutral
  };

  return (
    <div className="space-y-5">
      {/* Header & Evaluation Scope Ribbon */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-semibold text-nature-text">
              National Renewable Energy Intelligence Dashboard
            </h1>
            {data?.is_verified_official ? (
              <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 text-[10px] font-mono font-medium flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-emerald-700" />
                Verified Official (CEA Gazette)
              </span>
            ) : data?.is_official_source_unverified ? (
              <span className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200 text-[10px] font-mono font-medium flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-blue-700" />
                Unverified Source Model (Awaiting Official Gazette)
              </span>
            ) : (
              <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-[10px] font-mono font-medium flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-amber-700" />
                Benchmark Model (Demo)
              </span>
            )}
          </div>
          <p className="text-xs text-nature-muted font-sans">
            Authoritative all-India power generation metrics across all 28 States, 8 Union Territories, and 5 Regional Grids.
          </p>
        </div>

        {/* Temporal & Dataset Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Dataset Type Selector */}
          <div className="flex items-center rounded-md border border-nature-border bg-nature-bg p-0.5 text-xs">
            <button
              type="button"
              onClick={() => setDatasetType(undefined)}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                !datasetType ? 'bg-white text-nature-forest shadow-xs' : 'text-nature-muted hover:text-nature-text'
              }`}
            >
              Auto
            </button>
            <button
              type="button"
              onClick={() => setDatasetType('VERIFIED_OFFICIAL')}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                datasetType === 'VERIFIED_OFFICIAL' ? 'bg-white text-nature-forest shadow-xs' : 'text-nature-muted hover:text-nature-text'
              }`}
            >
              Verified Official
            </button>
            <button
              type="button"
              onClick={() => setDatasetType('OFFICIAL_SOURCE_UNVERIFIED')}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                datasetType === 'OFFICIAL_SOURCE_UNVERIFIED' ? 'bg-white text-nature-forest shadow-xs' : 'text-nature-muted hover:text-nature-text'
              }`}
            >
              Unverified Source
            </button>
            <button
              type="button"
              onClick={() => setDatasetType('DEMONSTRATION')}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                datasetType === 'DEMONSTRATION' ? 'bg-white text-nature-forest shadow-xs' : 'text-nature-muted hover:text-nature-text'
              }`}
            >
              Demo Model
            </button>
          </div>

          <div className="flex items-center space-x-1.5 text-xs text-nature-muted font-sans">
            <Calendar className="w-3.5 h-3.5 text-nature-forest" />
            <span>Horizon:</span>
          </div>

          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="text-xs rounded-md border border-nature-border bg-white px-2.5 py-1.5 text-nature-text focus:outline-none focus:ring-1 focus:ring-nature-forest font-medium"
          >
            {[2026, 2025, 2024, 2023, 2022, 2021, 2020].map((y) => (
              <option key={y} value={y}>
                {y} {y === 2024 ? '(Audited Ingested Period)' : y === 2026 ? '(Benchmark Model)' : ''}
              </option>
            ))}
          </select>

          <select
            value={selectedMonth === null ? 'ALL' : String(selectedMonth)}
            onChange={(e) => setSelectedMonth(e.target.value === 'ALL' ? null : Number(e.target.value))}
            className="text-xs rounded-md border border-nature-border bg-white px-2.5 py-1.5 text-nature-text focus:outline-none focus:ring-1 focus:ring-nature-forest font-medium"
          >
            <option value="ALL">Full Year (Cumulative)</option>
            {selectedYear === 2026 ? (
              <option value="1">January 2026</option>
            ) : (
              [
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
              ].map((m, idx) => (
                <option key={idx + 1} value={idx + 1}>
                  {m} {selectedYear === 2024 && (idx + 1 === 6 || idx + 1 === 12) ? '★ Official' : ''}
                </option>
              ))
            )}
          </select>
        </div>
      </div>

      {/* Primary KPI Ribbon (5 Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <MetricCard
          title="Total RE Generation"
          value={data?.total_generation_mu.toLocaleString() ?? '—'}
          unit="MU"
          subtitle={selectedMonth ? `Month ${selectedMonth} outturn` : 'Annual generation'}
          highlight="actual"
          tooltipText="1 Million Unit (MU) = 1 GWh = 1,000,000 kWh net generation."
        />
        <MetricCard
          title="Total Installed Capacity"
          value={data?.total_capacity_gw.toLocaleString() ?? '—'}
          unit="GW"
          subtitle={`${data?.total_capacity_mw.toLocaleString()} MW capacity`}
          highlight="primary"
          tooltipText="Aggregate grid-connected non-fossil capacity."
        />
        <MetricCard
          title="Solar Generation"
          value={solarData?.generation_mu.toLocaleString() ?? '—'}
          unit="MU"
          subtitle={`${solarData?.share_pct ?? 0}% of RE mix`}
          highlight="risk"
          tooltipText="Solar PV and ground-mounted utility scale generation."
        />
        <MetricCard
          title="Wind Generation"
          value={windData?.generation_mu.toLocaleString() ?? '—'}
          unit="MU"
          subtitle={`${windData?.share_pct ?? 0}% of RE mix`}
          highlight="actual"
          tooltipText="Transmission-connected wind turbine outturns."
        />
        <MetricCard
          title="YoY Generation Growth"
          value={data?.yoy_growth_pct ? `+${data.yoy_growth_pct}%` : '—'}
          unit="YoY"
          subtitle="Relative to prior year"
          highlight="forecast"
          tooltipText="Annualized outturn volume expansion rate."
        />
      </div>

      {/* Renewable Energy & Non-Fossil Accounting Section (Grid-India NLDC PSP Table A & G) */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-nature-border gap-2">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-semibold text-nature-text">
                Renewable Energy &amp; Non-Fossil Generation Accounting
              </h2>
              <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 text-[10px] font-mono font-medium flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-emerald-700" />
                NLDC PSP Table A &amp; G &bull; June 1, 2024
              </span>
            </div>
            <p className="text-xs text-nature-muted font-sans mt-0.5">
              Four distinct statutory accounting definitions for renewable and non-fossil generation under Indian grid operations.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-1 bg-nature-bg p-1 rounded-md border border-nature-border text-xs">
            <button
              type="button"
              onClick={() => setActiveMeasure('vre')}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                activeMeasure === 'vre'
                  ? 'bg-white text-nature-forest shadow-xs font-semibold'
                  : 'text-nature-muted hover:text-nature-text'
              }`}
            >
              A. Variable RE (14.54%)
            </button>
            <button
              type="button"
              onClick={() => setActiveMeasure('re_excl_hydro')}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                activeMeasure === 're_excl_hydro'
                  ? 'bg-white text-nature-forest shadow-xs font-semibold'
                  : 'text-nature-muted hover:text-nature-text'
              }`}
            >
              B. RE Excl. Hydro (15.20%)
            </button>
            <button
              type="button"
              onClick={() => setActiveMeasure('total_re_incl_hydro')}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                activeMeasure === 'total_re_incl_hydro'
                  ? 'bg-white text-nature-forest shadow-xs font-semibold'
                  : 'text-nature-muted hover:text-nature-text'
              }`}
            >
              C. Total RE Incl. Hydro (24.67%)
            </button>
            <button
              type="button"
              onClick={() => setActiveMeasure('non_fossil')}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                activeMeasure === 'non_fossil'
                  ? 'bg-white text-nature-forest shadow-xs font-semibold'
                  : 'text-nature-muted hover:text-nature-text'
              }`}
            >
              D. Non-Fossil Gross (25.41%)
            </button>
          </div>
        </div>

        {/* Dynamic Accounting Detail Card */}
        {activeMeasure === 'vre' && (
          <div className="rounded-md border border-amber-200 bg-amber-50/50 p-3.5 space-y-2 text-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="space-y-0.5">
                <span className="font-semibold text-amber-950 font-sans">
                  Measure A: Variable Renewable Energy (VRE) — Intermittent Wind &amp; Solar PV
                </span>
                <p className="text-[11px] text-amber-800">
                  Formula: (Wind + Solar) / Demand Met × 100. Measures short-term variable generation requiring flexible balancing.
                </p>
              </div>
              <div className="text-right sm:border-l sm:border-amber-200 sm:pl-4 shrink-0 font-mono">
                <span className="text-xl font-bold text-amber-900">14.54%</span>
                <span className="block text-[10px] text-amber-700">769.00 MU / 5,290.00 MU</span>
              </div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-amber-200/60 font-mono text-[11px]">
              <div><span className="text-amber-800 font-sans">Numerator:</span> 769.00 MU (Solar 398 + Wind 371)</div>
              <div><span className="text-amber-800 font-sans">Denominator:</span> 5,290.00 MU (Energy Met)</div>
              <div><span className="text-amber-800 font-sans">Included Fuels:</span> Solar PV, Wind</div>
              <div><span className="text-amber-800 font-sans">Source:</span> NLDC Daily PSP Table A</div>
            </div>
          </div>
        )}

        {activeMeasure === 're_excl_hydro' && (
          <div className="rounded-md border border-emerald-200 bg-emerald-50/50 p-3.5 space-y-2 text-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="space-y-0.5">
                <span className="font-semibold text-emerald-950 font-sans">
                  Measure B: Renewable Energy Excluding Large Hydro — (Pre-2019 MNRE RES Category)
                </span>
                <p className="text-[11px] text-emerald-800">
                  Formula: (Wind + Solar + Biomass and Others) / Demand Met × 100. Matches the official RES category in Table G.
                </p>
              </div>
              <div className="text-right sm:border-l sm:border-emerald-200 sm:pl-4 shrink-0 font-mono">
                <span className="text-xl font-bold text-emerald-900">15.20%</span>
                <span className="block text-[10px] text-emerald-700">804.00 MU / 5,290.00 MU</span>
              </div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-emerald-200/60 font-mono text-[11px]">
              <div><span className="text-emerald-800 font-sans">Numerator:</span> 804.00 MU (Solar 398 + Wind 371 + Biomass 35)</div>
              <div><span className="text-emerald-800 font-sans">Denominator:</span> 5,290.00 MU (Energy Met)</div>
              <div><span className="text-emerald-800 font-sans">Included Fuels:</span> Solar, Wind, Biomass &amp; Others</div>
              <div><span className="text-emerald-800 font-sans">Source:</span> NLDC Daily PSP Table A &amp; G</div>
            </div>
          </div>
        )}

        {activeMeasure === 'total_re_incl_hydro' && (
          <div className="rounded-md border border-emerald-300 bg-emerald-50/70 p-3.5 space-y-2 text-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="space-y-0.5">
                <span className="font-semibold text-emerald-950 font-sans">
                  Measure C: Total Renewable Energy Including Large Hydro — (MoP Order March 8, 2019)
                </span>
                <p className="text-[11px] text-emerald-800">
                  Formula: (Wind + Solar + Biomass and Others + Hydro) / Demand Met × 100. Encompasses all renewable assets under national policy.
                </p>
              </div>
              <div className="text-right sm:border-l sm:border-emerald-300 sm:pl-4 shrink-0 font-mono">
                <span className="text-xl font-bold text-emerald-900">24.67%</span>
                <span className="block text-[10px] text-emerald-700">1,305.00 MU / 5,290.00 MU</span>
              </div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-emerald-300/60 font-mono text-[11px]">
              <div><span className="text-emerald-800 font-sans">Numerator:</span> 1,305.00 MU (RES 804 + Hydro 501)</div>
              <div><span className="text-emerald-800 font-sans">Denominator:</span> 5,290.00 MU (Energy Met)</div>
              <div><span className="text-emerald-800 font-sans">Included Fuels:</span> Solar, Wind, Biomass, Large Hydro</div>
              <div><span className="text-emerald-800 font-sans">Source:</span> NLDC Daily PSP Table A &amp; G</div>
            </div>
            <div className="pt-1 text-[11px] text-emerald-900/80 font-sans">
              *Note: Table A (reporting only Solar, Wind, and Hydro) outturn is 1,270.00 MU (24.01%). Table G includes Biomass &amp; Others (+35 MU) yielding 1,305.00 MU (24.67%).
            </div>
          </div>
        )}

        {activeMeasure === 'non_fossil' && (
          <div className="rounded-md border border-blue-200 bg-blue-50/50 p-3.5 space-y-2 text-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="space-y-0.5">
                <span className="font-semibold text-blue-950 font-sans">
                  Measure D: Share of Non-Fossil Fuel Generation (Gross Generation Basis) — NLDC PSP Table G
                </span>
                <p className="text-[11px] text-blue-800">
                  Formula: (Hydro + Nuclear + RES) / Gross Generation × 100. National non-fossil electricity output including nuclear power.
                </p>
              </div>
              <div className="text-right sm:border-l sm:border-blue-200 sm:pl-4 shrink-0 font-mono">
                <span className="text-xl font-bold text-blue-900">25.41%</span>
                <span className="block text-[10px] text-blue-700">1,450.00 MU / 5,706.00 MU</span>
              </div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-blue-200/60 font-mono text-[11px]">
              <div><span className="text-blue-800 font-sans">Numerator:</span> 1,450.00 MU (Hydro 501 + Nuclear 145 + RES 804)</div>
              <div><span className="text-blue-800 font-sans">Denominator:</span> 5,706.00 MU (Gross Generation)</div>
              <div><span className="text-blue-800 font-sans">Included Fuels:</span> Hydro, Nuclear, RES (Solar, Wind, Biomass)</div>
              <div><span className="text-blue-800 font-sans">Source:</span> NLDC Daily PSP Table G</div>
            </div>
            <div className="pt-1 text-[11px] text-blue-900/80 font-sans">
              *Double-counting audit: In Table G, RES (804 MU) = Wind (371 MU) + Solar (398 MU) + Biomass &amp; Others (35 MU). Hydro (501 MU) and Nuclear (145 MU) are reported in separate rows. Zero double counting.
            </div>
          </div>
        )}

        {/* Regional Breakdown Subtable */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-nature-border bg-nature-bg/60 text-nature-muted font-mono text-[11px]">
                <th className="py-2 px-3">Regional Grid</th>
                <th className="py-2 px-3 text-right">Energy Met (MU)</th>
                <th className="py-2 px-3 text-right">Hydro (MU)</th>
                <th className="py-2 px-3 text-right">Wind (MU)</th>
                <th className="py-2 px-3 text-right">Solar (MU)</th>
                <th className="py-2 px-3 text-right">RE Total (MU)</th>
                <th className="py-2 px-3 text-right">VRE % (Excl. Hydro)</th>
                <th className="py-2 px-3 text-right">RE % (Incl. Hydro)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-nature-border font-mono text-[11px]">
              <tr className="hover:bg-nature-bg/30">
                <td className="py-2 px-3 font-semibold text-nature-text font-sans">Northern Region (NR)</td>
                <td className="py-2 px-3 text-right">1,785.0</td>
                <td className="py-2 px-3 text-right">326.0</td>
                <td className="py-2 px-3 text-right">43.0</td>
                <td className="py-2 px-3 text-right">180.60</td>
                <td className="py-2 px-3 text-right font-semibold">549.60</td>
                <td className="py-2 px-3 text-right text-amber-800 font-medium">12.53%</td>
                <td className="py-2 px-3 text-right text-nature-forest font-semibold">30.79%</td>
              </tr>
              <tr className="hover:bg-nature-bg/30">
                <td className="py-2 px-3 font-semibold text-nature-text font-sans">Western Region (WR)</td>
                <td className="py-2 px-3 text-right">1,629.0</td>
                <td className="py-2 px-3 text-right">49.0</td>
                <td className="py-2 px-3 text-right">202.0</td>
                <td className="py-2 px-3 text-right">92.30</td>
                <td className="py-2 px-3 text-right font-semibold">343.30</td>
                <td className="py-2 px-3 text-right text-amber-800 font-medium">18.07%</td>
                <td className="py-2 px-3 text-right text-nature-forest font-semibold">21.07%</td>
              </tr>
              <tr className="hover:bg-nature-bg/30">
                <td className="py-2 px-3 font-semibold text-nature-text font-sans">Southern Region (SR)</td>
                <td className="py-2 px-3 text-right">1,226.0</td>
                <td className="py-2 px-3 text-right">57.0</td>
                <td className="py-2 px-3 text-right">126.0</td>
                <td className="py-2 px-3 text-right">120.91</td>
                <td className="py-2 px-3 text-right font-semibold">303.91</td>
                <td className="py-2 px-3 text-right text-amber-800 font-medium">20.14%</td>
                <td className="py-2 px-3 text-right text-nature-forest font-semibold">24.79%</td>
              </tr>
              <tr className="hover:bg-nature-bg/30">
                <td className="py-2 px-3 font-semibold text-nature-text font-sans">
                  Eastern Region (ER) <span className="text-[10px] text-nature-muted font-normal font-mono">(NOT_REPORTED_IN_SOURCE)</span>
                </td>
                <td className="py-2 px-3 text-right">595.0</td>
                <td className="py-2 px-3 text-right">31.0</td>
                <td className="py-2 px-3 text-right text-nature-muted font-medium">-</td>
                <td className="py-2 px-3 text-right">2.98</td>
                <td className="py-2 px-3 text-right font-semibold">33.98</td>
                <td className="py-2 px-3 text-right text-amber-800 font-medium">0.50%</td>
                <td className="py-2 px-3 text-right text-nature-forest font-semibold">5.71%</td>
              </tr>
              <tr className="hover:bg-nature-bg/30">
                <td className="py-2 px-3 font-semibold text-nature-text font-sans">
                  North Eastern Region (NER) <span className="text-[10px] text-nature-muted font-normal font-mono">(NOT_REPORTED_IN_SOURCE)</span>
                </td>
                <td className="py-2 px-3 text-right">56.0</td>
                <td className="py-2 px-3 text-right">37.0</td>
                <td className="py-2 px-3 text-right text-nature-muted font-medium">-</td>
                <td className="py-2 px-3 text-right">1.02</td>
                <td className="py-2 px-3 text-right font-semibold">38.02</td>
                <td className="py-2 px-3 text-right text-amber-800 font-medium">1.82%</td>
                <td className="py-2 px-3 text-right text-nature-forest font-semibold">67.89%</td>
              </tr>
              <tr className="bg-nature-bg/60 font-bold border-t-2 border-nature-border">
                <td className="py-2 px-3 font-semibold text-nature-forest font-sans">All-India Total (ISTS)</td>
                <td className="py-2 px-3 text-right">5,290.0</td>
                <td className="py-2 px-3 text-right">501.0</td>
                <td className="py-2 px-3 text-right">371.0</td>
                <td className="py-2 px-3 text-right">398.0</td>
                <td className="py-2 px-3 text-right text-nature-forest">1,270.0</td>
                <td className="py-2 px-3 text-right text-amber-900 font-bold">14.54%</td>
                <td className="py-2 px-3 text-right text-nature-forest font-bold">24.01%</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="text-[11px] text-nature-muted font-sans flex items-center justify-between border-t border-nature-border pt-2">
          <span>
            *Note: Official NLDC PSP Table A prints &quot;-&quot; for ER and NER wind generation. Classified strictly as NOT_REPORTED_IN_SOURCE rather than assumed zero. Total solar is rounded to 398 MU in the official gazette (sum of regional rows is 397.81 MU).
          </span>
          <span className="font-mono text-emerald-800 font-medium shrink-0 ml-2">VERIFIED_OFFICIAL</span>
        </div>
      </div>

      {/* Charts Grid: Fuel Source Breakdown & Top States Leaderboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* RE Source Mix Breakdown */}
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-nature-border">
            <div>
              <h3 className="text-sm font-semibold text-nature-text">
                Renewable Generation by Fuel Source
              </h3>
              <p className="text-xs text-nature-muted">
                {data?.is_verified_official
                  ? 'Official Central Electricity Authority (CEA) monthly gazette outturn'
                  : 'Calibrated parameter breakdown across utility-scale non-fossil generation'}
              </p>
            </div>
            <span className="font-mono text-xs text-nature-muted font-medium">MU Outturn</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data?.source_breakdown}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
              >
                <XAxis
                  type="number"
                  tick={{ fontSize: 11, fill: '#748078' }}
                  tickFormatter={(v) => `${(v / 1000).toFixed(1)}k`}
                />
                <YAxis
                  type="category"
                  dataKey="display_name"
                  tick={{ fontSize: 11, fill: '#26332C' }}
                  width={110}
                />
                <Tooltip
                  formatter={(val: number) => [`${val.toLocaleString()} MU`, 'Generation']}
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderColor: '#E1E8DF',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="generation_mu" radius={[0, 4, 4, 0]}>
                  {data?.source_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={fuelColors[entry.source_code] || '#245B45'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Source Share Grid */}
          <div className="grid grid-cols-3 gap-2 pt-2 border-t border-nature-border text-xs">
            {data?.source_breakdown.slice(0, 3).map((s) => (
              <div key={s.source_code} className="p-2 rounded bg-nature-bg border border-nature-border">
                <span className="text-[10px] text-nature-muted block truncate">{s.display_name}</span>
                <span className="font-semibold text-nature-text font-mono tabular-nums">{s.share_pct}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top 5 Generating States Leaderboard */}
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-nature-border">
            <div>
              <h3 className="text-sm font-semibold text-nature-text">
                Top State Renewable Producers
              </h3>
              <p className="text-xs text-nature-muted">
                Leading states by generation volume and national market share
              </p>
            </div>
            <button
              onClick={() => onNavigate('map')}
              className="inline-flex items-center space-x-1 text-xs text-nature-forest hover:underline font-medium"
            >
              <span>Explore Map</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2">
            {data?.top_states.map((st, idx) => (
              <div
                key={st.code}
                onClick={() => onNavigate('states')}
                className="p-3 rounded-md border border-nature-border bg-nature-bg hover:bg-white hover:border-nature-forest/40 transition-colors flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center space-x-3">
                  <span className="w-6 h-6 rounded-full bg-white border border-nature-border flex items-center justify-center font-mono text-xs font-semibold text-nature-forest">
                    {idx + 1}
                  </span>
                  <div>
                    <h4 className="text-xs font-semibold text-nature-text font-sans">{st.name}</h4>
                    <span className="text-[10px] text-nature-muted font-mono">
                      {st.code} &bull; {st.region_code} Region
                    </span>
                  </div>
                </div>

                <div className="text-right font-mono">
                  <span className="text-xs font-semibold text-nature-text block tabular-nums">
                    {st.generation_mu.toLocaleString()} MU
                  </span>
                  <span className="text-[10px] text-nature-muted">
                    {st.share_of_national_pct}% of national
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Quick Action Bar */}
          <div className="pt-2 border-t border-nature-border flex justify-between items-center text-xs text-nature-muted font-sans">
            <span>All 28 States and 8 Union Territories monitored.</span>
            <button
              onClick={() => onNavigate('states')}
              className="text-nature-forest font-medium hover:underline inline-flex items-center gap-1"
            >
              <span>View All 36 Entities</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Quick Access Operational Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div
          onClick={() => onNavigate('map')}
          className="rounded-lg border border-nature-border bg-white p-4 shadow-sm hover:border-nature-forest/40 transition-colors cursor-pointer space-y-1.5"
        >
          <div className="flex items-center space-x-2 text-nature-forest">
            <MapPin className="w-4 h-4" />
            <h4 className="text-xs font-semibold text-nature-text">Interactive India Map</h4>
          </div>
          <p className="text-xs text-nature-muted font-sans">
            Inspect choropleth generation and capacity heatmaps across all 36 Indian states and UTs.
          </p>
        </div>

        <div
          onClick={() => onNavigate('multi-year')}
          className="rounded-lg border border-nature-border bg-white p-4 shadow-sm hover:border-nature-forest/40 transition-colors cursor-pointer space-y-1.5"
        >
          <div className="flex items-center space-x-2 text-nature-forecast">
            <TrendingUp className="w-4 h-4" />
            <h4 className="text-xs font-semibold text-nature-text">Multi-Year Analytics</h4>
          </div>
          <p className="text-xs text-nature-muted font-sans">
            Explore 6-year generation trends (2020–2026), compound growth rates, and monsoon seasonality.
          </p>
        </div>

        <div
          onClick={() => onNavigate('forecasting')}
          className="rounded-lg border border-nature-border bg-white p-4 shadow-sm hover:border-nature-forest/40 transition-colors cursor-pointer space-y-1.5"
        >
          <div className="flex items-center space-x-2 text-nature-risk">
            <Zap className="w-4 h-4" />
            <h4 className="text-xs font-semibold text-nature-text">15-Min Forecasting Lab</h4>
          </div>
          <p className="text-xs text-nature-muted font-sans">
            Analyze 96 daily time blocks, REMC schedules, MAE, RMSE, and balancing deviations.
          </p>
        </div>
      </div>
    </div>
  );
};

