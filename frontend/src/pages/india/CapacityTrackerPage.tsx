import React, { useEffect, useState } from 'react';
import {
  Target,
  Layers,
  TrendingUp,
  Award,
  Zap,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sun,
  Wind,
  Droplets,
  Flame,
} from 'lucide-react';
import { IndiaNationalOverview, IndiaStateItem, CapacityAnalyticsResponse } from '../../types/india';
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
  CartesianGrid,
  Cell,
  Legend,
} from 'recharts';

export const CapacityTrackerPage: React.FC = () => {
  const [overview, setOverview] = useState<IndiaNationalOverview | null>(null);
  const [states, setStates] = useState<IndiaStateItem[]>([]);
  const [capacityData, setCapacityData] = useState<CapacityAnalyticsResponse | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>('2026-09-30');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const TARGET_2030_GW = 500; // India's COP26 500 GW non-fossil target

  const fetchData = async (targetDate: string = selectedDate) => {
    setLoading(true);
    setError(null);
    try {
      const [ov, st, cap] = await Promise.all([
        indiaApi.getOverview(2026, 1),
        indiaApi.getStates(),
        indiaApi.getCapacityAnalytics(targetDate).catch(() => null),
      ]);
      setOverview(ov);
      setStates(st);
      if (cap) setCapacityData(cap);
    } catch (err: any) {
      setError(err?.message || 'Failed to load capacity tracker data.');
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (newDate: string) => {
    setSelectedDate(newDate);
    fetchData(newDate);
  };

  useEffect(() => {
    fetchData('2026-09-30');
  }, []);

  if (loading && !overview) {
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

  if (error && !overview) {
    return <ErrorAlert title="Capacity Tracker Error" message={error} onRetry={fetchData} />;
  }

  const pureReCapGW = capacityData?.summary_gw.clean_re_gw ?? (overview?.total_capacity_gw || 195.0);
  const nuclearCapGW = capacityData?.summary_gw.nuclear_gw ?? 8.18; // CEA Sub-Report 1 Statutory Benchmark (8,180 MW operational nuclear fleet)
  const totalNonFossilGW = capacityData?.summary_gw.total_non_fossil_gw ?? (pureReCapGW + nuclearCapGW);
  const nonFossilProgressPct = capacityData?.target_500gw_tracker.progress_percentage ?? ((totalNonFossilGW / TARGET_2030_GW) * 100);
  const reProgressPct = (pureReCapGW / TARGET_2030_GW) * 100;
  const nuclearProgressPct = (nuclearCapGW / TARGET_2030_GW) * 100;
  const deficitGW = capacityData?.target_500gw_tracker.remaining_capacity_gw ?? (TARGET_2030_GW - totalNonFossilGW);
  const requiredAnnualAdditionGW = capacityData?.target_500gw_tracker.required_annual_addition_gw ?? (deficitGW / 5.5);

  const sourceStreams = capacityData ? [
    { source_code: 'SOLAR', display_name: 'Solar Power', capacity_mw: capacityData.summary_mw.solar_mw },
    { source_code: 'WIND', display_name: 'Wind Energy', capacity_mw: capacityData.summary_mw.wind_mw },
    { source_code: 'LARGE_HYDRO', display_name: 'Large Hydro (>25 MW)', capacity_mw: capacityData.summary_mw.large_hydro_mw },
    { source_code: 'SMALL_HYDRO', display_name: 'Small Hydro (<=25 MW)', capacity_mw: capacityData.summary_mw.small_hydro_mw },
    { source_code: 'BIOMASS', display_name: 'Biomass & Bio-power', capacity_mw: capacityData.summary_mw.biomass_mw },
    { source_code: 'NUCLEAR', display_name: 'Nuclear Fleet', capacity_mw: capacityData.summary_mw.nuclear_mw },
  ] : (overview?.source_breakdown || []);
  const streamTotalMW = capacityData?.summary_mw.grand_total_mw || (overview?.total_capacity_mw || 1);

  // State leaderboard sorted by total capacity
  const sortedStates = [...states].sort((a, b) => b.total_capacity_mw - a.total_capacity_mw);
  const top10States = sortedStates.slice(0, 10).map((s) => ({
    name: s.name,
    code: s.code,
    SolarMW: s.solar_capacity_mw,
    WindMW: s.wind_capacity_mw,
    OtherMW: Math.max(0, s.total_capacity_mw - s.solar_capacity_mw - s.wind_capacity_mw),
    TotalGW: Number((s.total_capacity_mw / 1000).toFixed(1)),
  }));

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-semibold text-nature-text">
              National Non-Fossil Capacity &amp; 500 GW Target Tracker
            </h1>
            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-nature-forest border border-emerald-200 text-[10px] font-mono font-medium flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-nature-forest" />
              Target Benchmark &bull; 2030 Horizon
            </span>
          </div>
          <p className="text-xs text-nature-muted">
            Tracking national trajectory toward India's COP26 Panchamrit commitment (500 GW non-fossil capacity by 2030).
            Reporting baseline:{' '}
            <strong className="text-nature-text">
              {selectedDate === '2026-09-30'
                ? '30 September 2026 (Latest Verified Gazette)'
                : '30 June 2024 (Mid-Year 2024 Gazette)'}
            </strong>{' '}
            &bull; Published:{' '}
            <strong className="text-nature-text">
              {selectedDate === '2026-09-30' ? '19/10/2026' : '18/07/2024'}
            </strong>{' '}
            via National Power Portal.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-nature-muted font-medium">Reporting Gazette:</span>
            <select
              value={selectedDate}
              onChange={(e) => handleDateChange(e.target.value)}
              className="text-xs font-mono bg-white border border-nature-border rounded px-2.5 py-1 text-nature-text font-medium shadow-sm focus:outline-none focus:ring-1 focus:ring-nature-forest"
            >
              <option value="2026-09-30">30 Sep 2026 (Latest Verified Gazette)</option>
              <option value="2024-06-30">30 Jun 2024 (Mid-Year 2024 Gazette)</option>
            </select>
          </div>
          <span className="text-xs font-mono text-nature-forest bg-nature-forest-light px-2.5 py-1 rounded border border-nature-border">
            Target Year: 2030 Horizon
          </span>
        </div>
      </div>

      {/* Target Progress Bar Banner */}
      <div className="rounded-lg border border-nature-border bg-white p-5 shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-semibold text-nature-text">
                500 GW Non-Fossil Electricity Target (COP26 Commitment)
              </span>
              <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                {nonFossilProgressPct.toFixed(1)}% Achieved (Total Non-Fossil)
              </span>
            </div>
            <p className="text-xs text-nature-muted mt-0.5">
              Total Non-Fossil: <strong className="text-nature-text">{totalNonFossilGW.toFixed(1)} GW</strong> (RE: {pureReCapGW.toFixed(1)} GW + Nuclear: {nuclearCapGW.toFixed(2)} GW) of 500.0 GW target &bull; Balance to commission: <strong className="text-nature-text">{deficitGW.toFixed(1)} GW</strong>
            </p>
          </div>

          <div className="text-right">
            <span className="text-xs text-nature-muted">Required Additions Pace:</span>
            <div className="text-sm font-bold font-mono text-nature-forest">
              ~{requiredAnnualAdditionGW.toFixed(1)} GW / year
            </div>
          </div>
        </div>

        {/* Multi-segment progress visual */}
        <div className="w-full bg-slate-100 rounded-full h-4 overflow-hidden flex border border-nature-border">
          <div
            className="bg-emerald-600 h-full"
            style={{ width: `${Math.min(reProgressPct, 100)}%` }}
            title={`Renewable Energy Fleet: ${pureReCapGW.toFixed(1)} GW (${reProgressPct.toFixed(1)}%)`}
          />
          <div
            className="bg-indigo-600 h-full"
            style={{ width: `${Math.min(nuclearProgressPct, 100)}%` }}
            title={`Operational Nuclear Fleet: ${nuclearCapGW.toFixed(2)} GW (${nuclearProgressPct.toFixed(1)}%)`}
          />
          <div
            className="bg-amber-50 h-full border-l border-amber-300"
            style={{ width: `${Math.max(0, 100 - nonFossilProgressPct)}%` }}
            title={`Deficit to 2030: ${deficitGW.toFixed(1)} GW (${(100 - nonFossilProgressPct).toFixed(1)}%)`}
          />
        </div>

        <div className="flex flex-wrap items-center justify-between text-[11px] font-mono text-nature-muted pt-1 gap-2">
          <span>0 GW (Baseline)</span>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1 text-emerald-800">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-600 inline-block" />
              RE Fleet: {pureReCapGW.toFixed(1)} GW ({reProgressPct.toFixed(1)}%)
            </span>
            <span className="flex items-center gap-1 text-indigo-800">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-600 inline-block" />
              Nuclear Fleet: {nuclearCapGW.toFixed(2)} GW ({nuclearProgressPct.toFixed(1)}%)
            </span>
            <span className="font-semibold text-nature-forest">Total: {totalNonFossilGW.toFixed(1)} GW ({nonFossilProgressPct.toFixed(1)}%)</span>
          </div>
          <span>Target: 500.0 GW (2030)</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          title="Total Non-Fossil Fleet"
          value={`${totalNonFossilGW.toFixed(1)} GW`}
          subtitle={`${nonFossilProgressPct.toFixed(1)}% of 500 GW target`}
          icon={<Zap className="w-4 h-4 text-nature-forest" />}
          trend="positive"
        />
        <MetricCard
          title="Renewable Energy Fleet"
          value={`${pureReCapGW.toFixed(1)} GW`}
          subtitle={`${(capacityData?.summary_mw.clean_re_mw ?? overview?.total_capacity_mw ?? 0).toLocaleString()} MW (Solar, Wind, Hydro, Bio)`}
          icon={<Layers className="w-4 h-4 text-emerald-600" />}
          trend="positive"
        />
        <MetricCard
          title="Operational Nuclear Fleet"
          value={`${nuclearCapGW.toFixed(2)} GW`}
          subtitle={selectedDate === '2026-09-30' ? '8,780 MW across CEA-monitored fleet' : '8,180 MW across 22 CEA-monitored units'}
          icon={<ShieldCheck className="w-4 h-4 text-indigo-600" />}
          trend="neutral"
        />
        <MetricCard
          title="Target Deficit (to 2030)"
          value={`${deficitGW.toFixed(1)} GW`}
          subtitle={`Required additions pace: ~${requiredAnnualAdditionGW.toFixed(1)} GW/yr`}
          icon={<AlertTriangle className="w-4 h-4 text-[#D49A42]" />}
          trend="neutral"
        />
      </div>

      {/* Technology Breakdown & State Leaderboard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Source Breakdown Table */}
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="border-b border-nature-border pb-2.5">
            <h2 className="text-sm font-semibold text-nature-text">
              Capacity by Energy Stream
            </h2>
            <p className="text-[11px] text-nature-muted">
              Installed capacity breakdown across official CEA fuel classes.
            </p>
          </div>

          <div className="space-y-3">
            {sourceStreams.map((src) => {
              const capGW = (src.capacity_mw / 1000).toFixed(2);
              const capShare = ((src.capacity_mw / streamTotalMW) * 100).toFixed(1);
              return (
                <div key={src.source_code} className="p-2.5 rounded border border-nature-border bg-nature-bg/40 space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-nature-text flex items-center gap-1.5">
                      {src.source_code === 'SOLAR' && <Sun className="w-3.5 h-3.5 text-[#D49A42]" />}
                      {src.source_code === 'WIND' && <Wind className="w-3.5 h-3.5 text-[#26966B]" />}
                      {src.source_code === 'LARGE_HYDRO' && <Droplets className="w-3.5 h-3.5 text-[#5689B5]" />}
                      {src.source_code === 'SMALL_HYDRO' && <Droplets className="w-3.5 h-3.5 text-[#8FAE91]" />}
                      {src.source_code === 'BIOMASS' && <Flame className="w-3.5 h-3.5 text-[#8A5D3B]" />}
                      {src.source_code === 'NUCLEAR' && <ShieldCheck className="w-3.5 h-3.5 text-indigo-600" />}
                      {src.display_name}
                    </span>
                    <span className="font-mono font-semibold text-nature-text">{capGW} GW</span>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-nature-muted">
                    <span>{src.capacity_mw.toLocaleString()} MW</span>
                    <span className="font-mono">{capShare}% of fleet</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-1">
                    <div
                      className="bg-nature-forest h-1 rounded-full"
                      style={{ width: `${Math.min(Number(capShare), 100)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* State Capacity Leaderboard Stacked Bar Chart */}
        <div className="lg:col-span-2 rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-nature-border pb-2.5">
            <div>
              <h2 className="text-sm font-semibold text-nature-text">
                Top 10 States Installed Capacity Leaderboard
              </h2>
              <p className="text-[11px] text-nature-muted">
                Installed capacity (MW) stacked by Solar, Wind, and Other RE.
              </p>
            </div>
            <span className="text-[11px] font-mono text-nature-forest bg-nature-forest-light px-2 py-0.5 rounded">
              Unit: MW
            </span>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={top10States}
                margin={{ top: 10, right: 10, left: 10, bottom: 25 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#E1E8DF" vertical={false} />
                <XAxis dataKey="code" tick={{ fontSize: 11, fill: '#748078' }} tickLine={false} />
                <YAxis
                  tick={{ fontSize: 11, fill: '#748078' }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  formatter={(value: any, name: any) => [`${Number(value).toLocaleString()} MW`, name]}
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderColor: '#E1E8DF',
                    borderRadius: '6px',
                    fontSize: '11px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="SolarMW" stackId="a" fill="#D49A42" name="Solar (MW)" />
                <Bar dataKey="WindMW" stackId="a" fill="#26966B" name="Wind (MW)" />
                <Bar dataKey="OtherMW" stackId="a" fill="#5689B5" name="Hydro & Other (MW)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Statutory Provenance Banner */}
      <div className="rounded-lg border border-nature-border bg-emerald-50/60 p-4 text-xs space-y-1">
        <div className="flex items-center gap-2 font-semibold text-nature-forest">
          <ShieldCheck className="w-4 h-4 text-nature-forest" />
          <span>Statutory Provenance &amp; Target Methodology</span>
        </div>
        <p className="text-nature-muted text-[11px] leading-relaxed">
          <strong>Official Gazette:</strong> {capacityData?.statutory_source || 'Central Electricity Authority (CEA) All-India Installed Capacity Gazette'} &bull;{' '}
          <strong>Source File:</strong> {capacityData?.source_provenance || 'capacity1-2024-06.pdf'} &bull;{' '}
          <strong>Scope:</strong> Non-fossil capacity under COP26 encompasses Solar ({capacityData?.summary_gw.solar_gw ?? 85.5} GW), Wind ({capacityData?.summary_gw.wind_gw ?? 46.7} GW), Large Hydro ({capacityData?.summary_gw.large_hydro_gw ?? 46.9} GW), Small Hydro ({capacityData?.summary_gw.small_hydro_gw ?? 5.0} GW), Biomass/Bio-Power ({capacityData?.summary_gw.biomass_gw ?? 10.9} GW), and Nuclear ({capacityData?.summary_gw.nuclear_gw ?? 8.18} GW).
        </p>
      </div>
    </div>
  );
};

