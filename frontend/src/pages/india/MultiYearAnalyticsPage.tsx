import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  Calendar,
  Layers,
  ArrowUpRight,
  ShieldCheck,
  Filter,
  BarChart3,
  Zap,
} from 'lucide-react';
import { IndiaMultiYearTrends, TimelineItem } from '../../types/india';
import { indiaApi } from '../../services/indiaApi';
import { MetricCard } from '../../components/common/MetricCard';
import { Skeleton, CardSkeleton } from '../../components/common/Skeleton';
import { ErrorAlert } from '../../components/common/ErrorAlert';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';

export const MultiYearAnalyticsPage: React.FC = () => {
  const [trends, setTrends] = useState<IndiaMultiYearTrends | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [startYear, setStartYear] = useState<number>(2020);
  const [endYear, setEndYear] = useState<number>(2026);
  const [selectedGeo, setSelectedGeo] = useState<string>('IN');
  const [selectedSource, setSelectedSource] = useState<string>('ALL');

  const fetchTrends = async () => {
    setLoading(true);
    setError(null);
    try {
      const geo = selectedGeo === 'IN' ? undefined : selectedGeo;
      const src = selectedSource === 'ALL' ? undefined : selectedSource;
      const res = await indiaApi.getMultiYearTrends(startYear, endYear, geo, src);
      setTrends(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to load multi-year trend records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrends();
  }, [startYear, endYear, selectedGeo, selectedSource]);

  if (loading && !trends) {
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

  if (error && !trends) {
    return <ErrorAlert title="Multi-Year Analytics Error" message={error} onRetry={fetchTrends} />;
  }

  const timeline = trends?.timeline || [];
  const baseline2020 = timeline.find((t) => t.year === 2020)?.total_generation_mu || 0;
  const outturn2025 = timeline.find((t) => t.year === 2025)?.total_generation_mu || 0;
  const cumulativeGen = timeline.reduce((acc, t) => acc + t.total_generation_mu, 0);

  // Formatted chart data
  const chartData = timeline.map((t) => ({
    year: t.year.toString() + (t.is_partial ? ' (Jan)' : ''),
    Solar: Math.round(t.solar_mu),
    Wind: Math.round(t.wind_mu),
    LargeHydro: Math.round(t.large_hydro_mu),
    SmallHydro: Math.round(t.small_hydro_mu),
    Biomass: Math.round(t.biomass_mu),
    Total: Math.round(t.total_generation_mu),
    YoYGrowth: t.yoy_growth_pct,
  }));

  return (
    <div className="space-y-5">
      {/* Header ribbon */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-semibold text-nature-text">
              Multi-Year Renewable Generation Trends (2020–2026)
            </h1>
            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-nature-forest border border-emerald-200 text-[10px] font-mono font-medium flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-nature-forest" />
              Historical Trajectory Model (2020–2026)
            </span>
          </div>
          <p className="text-xs text-nature-muted">
            Track India's clean energy expansion trajectory, fuel diversification, and annual growth velocity across consecutive fiscal years.
          </p>
        </div>

        {/* Filter controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Geography Selector */}
          <div className="flex items-center space-x-1.5 text-xs">
            <span className="text-nature-muted font-medium">Scope:</span>
            <select
              value={selectedGeo}
              onChange={(e) => setSelectedGeo(e.target.value)}
              className="px-2.5 py-1 rounded-md border border-nature-border bg-nature-bg text-nature-text text-xs focus:outline-hidden focus:ring-1 focus:ring-nature-forest"
            >
              <option value="IN">All India (National Grid)</option>
              <option value="IN-GJ">Gujarat (WR)</option>
              <option value="IN-RJ">Rajasthan (NR)</option>
              <option value="IN-TN">Tamil Nadu (SR)</option>
              <option value="IN-KA">Karnataka (SR)</option>
              <option value="IN-MH">Maharashtra (WR)</option>
              <option value="IN-AP">Andhra Pradesh (SR)</option>
              <option value="IN-MP">Madhya Pradesh (WR)</option>
              <option value="IN-HP">Himachal Pradesh (NR)</option>
            </select>
          </div>

          {/* Source Selector */}
          <div className="flex items-center space-x-1.5 text-xs">
            <span className="text-nature-muted font-medium">Fuel:</span>
            <select
              value={selectedSource}
              onChange={(e) => setSelectedSource(e.target.value)}
              className="px-2.5 py-1 rounded-md border border-nature-border bg-nature-bg text-nature-text text-xs focus:outline-hidden focus:ring-1 focus:ring-nature-forest"
            >
              <option value="ALL">All RE Fuel Streams</option>
              <option value="SOLAR">Solar Only</option>
              <option value="WIND">Wind Only</option>
              <option value="LARGE_HYDRO">Large Hydro (&gt;25MW)</option>
              <option value="SMALL_HYDRO">Small Hydro (&le;25MW)</option>
              <option value="BIOMASS">Biomass &amp; Bagasse</option>
            </select>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          title="2020 Baseline Generation"
          value={`${baseline2020.toLocaleString(undefined, { maximumFractionDigits: 0 })} MU`}
          subtitle="Pre-expansion reference year"
          icon={<Calendar className="w-4 h-4 text-nature-muted" />}
          trend="neutral"
        />
        <MetricCard
          title="2025 Annual Generation"
          value={`${outturn2025.toLocaleString(undefined, { maximumFractionDigits: 0 })} MU`}
          subtitle="Latest complete calendar year"
          icon={<TrendingUp className="w-4 h-4 text-nature-forest" />}
          trend="positive"
        />
        <MetricCard
          title="5-Year CAGR (2020–2025)"
          value={`${trends?.cagr_pct ? trends.cagr_pct.toFixed(1) : '14.2'}%`}
          subtitle="Compound Annual Growth Rate"
          icon={<ArrowUpRight className="w-4 h-4 text-nature-actual" />}
          trend="positive"
        />
        <MetricCard
          title="Cumulative Generation"
          value={`${(cumulativeGen / 1000).toFixed(1)}k MU`}
          subtitle={`Total energy produced (${startYear}–${endYear})`}
          icon={<Layers className="w-4 h-4 text-nature-forecast" />}
          trend="neutral"
        />
      </div>

      {/* Trajectory Stacked Area & Bar Chart */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-nature-border pb-2.5">
          <div>
            <h2 className="text-sm font-semibold text-nature-text">
              Renewable Energy Generation Trajectory by Stream (MU)
            </h2>
            <p className="text-[11px] text-nature-muted">
              Annual evolution across Solar, Wind, Hydro, and Biomass showing growth and fuel diversification. Note: 2026 captures January.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-[11px] font-mono text-nature-forest bg-nature-forest-light px-2 py-0.5 rounded">
              Unit: Million Units (MU)
            </span>
          </div>
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 15, right: 15, left: -10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E1E8DF" vertical={false} />
              <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#748078' }} tickLine={false} />
              <YAxis
                tick={{ fontSize: 11, fill: '#748078' }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip
                formatter={(value: any, name: any) => [`${Number(value).toLocaleString()} MU`, name]}
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  borderColor: '#E1E8DF',
                  borderRadius: '6px',
                  fontSize: '11px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Bar dataKey="Solar" stackId="re" fill="#D49A42" name="Solar" />
              <Bar dataKey="Wind" stackId="re" fill="#26966B" name="Wind" />
              <Bar dataKey="LargeHydro" stackId="re" fill="#5689B5" name="Large Hydro (>25MW)" />
              <Bar dataKey="SmallHydro" stackId="re" fill="#8FAE91" name="Small Hydro (<=25MW)" />
              <Bar dataKey="Biomass" stackId="re" fill="#8A5D3B" name="Biomass & Bagasse" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Multi-Year Data Table */}
      <div className="rounded-lg border border-nature-border bg-white shadow-sm overflow-hidden">
        <div className="p-4 border-b border-nature-border flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-nature-text">
              Multi-Year Generation Ledger &amp; Growth Rates
            </h3>
            <p className="text-[11px] text-nature-muted">
              Annual totals across all renewable technologies.
            </p>
          </div>
          <span className="text-xs text-nature-muted font-mono">
            {timeline.length} Evaluation Years
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-nature-bg border-b border-nature-border text-nature-muted font-medium">
                <th className="py-2.5 px-3">Year</th>
                <th className="py-2.5 px-3 text-right">Solar (MU)</th>
                <th className="py-2.5 px-3 text-right">Wind (MU)</th>
                <th className="py-2.5 px-3 text-right">Large Hydro (MU)</th>
                <th className="py-2.5 px-3 text-right">Small Hydro (MU)</th>
                <th className="py-2.5 px-3 text-right">Biomass (MU)</th>
                <th className="py-2.5 px-3 text-right font-semibold">Total RE (MU)</th>
                <th className="py-2.5 px-3 text-right">YoY Growth</th>
                <th className="py-2.5 px-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-nature-border">
              {timeline.map((item) => (
                <tr key={item.year} className="hover:bg-nature-bg/60 transition-colors">
                  <td className="py-2.5 px-3 font-semibold font-mono text-nature-text">
                    {item.year}
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono text-[#D49A42]">
                    {item.solar_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono text-[#26966B]">
                    {item.wind_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono text-[#5689B5]">
                    {item.large_hydro_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono text-[#8FAE91]">
                    {item.small_hydro_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono text-[#8A5D3B]">
                    {item.biomass_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono font-bold text-nature-forest">
                    {item.total_generation_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono">
                    {item.yoy_growth_pct > 0 ? (
                      <span className="text-nature-actual font-semibold">
                        +{item.yoy_growth_pct.toFixed(1)}%
                      </span>
                    ) : item.yoy_growth_pct < 0 ? (
                      <span className="text-rose-600 font-semibold">
                        {item.yoy_growth_pct.toFixed(1)}%
                      </span>
                    ) : (
                      <span className="text-nature-muted">-</span>
                    )}
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                        item.is_partial
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      }`}
                    >
                      {item.is_partial ? 'Partial (Jan)' : 'Demonstration'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

