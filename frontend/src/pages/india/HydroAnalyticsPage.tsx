import React, { useEffect, useState } from 'react';
import {
  Droplets,
  TrendingUp,
  MapPin,
  Calendar,
  ShieldCheck,
  Zap,
  Award,
  Layers,
  Activity,
} from 'lucide-react';
import { IndiaSourceAnalytics } from '../../types/india';
import { indiaApi } from '../../services/indiaApi';
import { MetricCard } from '../../components/common/MetricCard';
import { Skeleton, CardSkeleton } from '../../components/common/Skeleton';
import { ErrorAlert } from '../../components/common/ErrorAlert';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

export const HydroAnalyticsPage: React.FC = () => {
  const [largeHydro, setLargeHydro] = useState<IndiaSourceAnalytics | null>(null);
  const [smallHydro, setSmallHydro] = useState<IndiaSourceAnalytics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [hydroView, setHydroView] = useState<'ALL' | 'LARGE' | 'SMALL'>('ALL');

  const fetchHydroData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [lh, sh] = await Promise.all([
        indiaApi.getSourceAnalytics('LARGE_HYDRO'),
        indiaApi.getSourceAnalytics('SMALL_HYDRO'),
      ]);
      setLargeHydro(lh);
      setSmallHydro(sh);
    } catch (err: any) {
      setError(err?.message || 'Failed to load hydroelectric analytics from CEA service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHydroData();
  }, []);

  if (loading && (!largeHydro || !smallHydro)) {
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

  if (error && !largeHydro) {
    return <ErrorAlert title="Hydro Analytics Error" message={error} onRetry={fetchHydroData} />;
  }

  const largeGen = largeHydro?.annual_generation_2025_mu || 0;
  const smallGen = smallHydro?.annual_generation_2025_mu || 0;
  const totalHydroGen = largeGen + smallGen;

  const largeCap = largeHydro?.state_leaderboard.reduce((a, s) => a + s.capacity_mw, 0) || 0;
  const smallCap = smallHydro?.state_leaderboard.reduce((a, s) => a + s.capacity_mw, 0) || 0;
  const totalHydroCap = largeCap + smallCap;

  const activeLeaders = hydroView === 'SMALL'
    ? smallHydro?.state_leaderboard || []
    : largeHydro?.state_leaderboard || [];

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-semibold text-nature-text">
              Hydroelectric Energy Sector Intelligence
            </h1>
            <span className="px-2 py-0.5 rounded-full bg-sky-50 text-sky-800 border border-sky-200 text-[10px] font-mono font-medium flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-sky-800" />
              Hydro Fleet Model &bull; Ministry of Power Framework
            </span>
          </div>
          <p className="text-xs text-nature-muted">
            Tracking Himalayan river runoff, reservoir storage replenishment, run-of-river generation, and small hydro capacity under statutory guidelines.
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex rounded-md border border-nature-border bg-nature-bg p-0.5">
          <button
            onClick={() => setHydroView('ALL')}
            className={`px-2.5 py-1 text-xs rounded transition-colors ${
              hydroView === 'ALL'
                ? 'bg-nature-forest text-white font-medium shadow-xs'
                : 'text-nature-muted hover:text-nature-text'
            }`}
          >
            Combined Hydro
          </button>
          <button
            onClick={() => setHydroView('LARGE')}
            className={`px-2.5 py-1 text-xs rounded transition-colors ${
              hydroView === 'LARGE'
                ? 'bg-nature-forest text-white font-medium shadow-xs'
                : 'text-nature-muted hover:text-nature-text'
            }`}
          >
            Large (&gt;25MW)
          </button>
          <button
            onClick={() => setHydroView('SMALL')}
            className={`px-2.5 py-1 text-xs rounded transition-colors ${
              hydroView === 'SMALL'
                ? 'bg-nature-forest text-white font-medium shadow-xs'
                : 'text-nature-muted hover:text-nature-text'
            }`}
          >
            Small (&le;25MW)
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          title="Total Hydro Outturn"
          value={`${totalHydroGen.toLocaleString(undefined, { maximumFractionDigits: 0 })} MU`}
          subtitle="Annual 2025 model outturn (Large + Small)"
          icon={<Droplets className="w-4 h-4 text-[#5689B5]" />}
          trend="neutral"
        />
        <MetricCard
          title="Installed Hydro Fleet"
          value={`${(totalHydroCap / 1000).toFixed(2)} GW`}
          subtitle={`Large: ${(largeCap / 1000).toFixed(1)} GW | Small: ${(smallCap / 1000).toFixed(1)} GW`}
          icon={<Zap className="w-4 h-4 text-nature-forest" />}
          trend="neutral"
        />
        <MetricCard
          title="Monsoon Runoff Multiplier"
          value="3.2x Surge"
          subtitle="July–September vs January baseline"
          icon={<TrendingUp className="w-4 h-4 text-nature-actual" />}
          trend="positive"
        />
        <MetricCard
          title="Key Hydro Geography"
          value="Himalayan States"
          subtitle="HP, UK, J&amp;K, Sikkim &amp; Arunachal"
          icon={<MapPin className="w-4 h-4 text-[#5689B5]" />}
          trend="neutral"
        />
      </div>

      {/* Seasonality Chart & Hydro Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Seasonality Curve */}
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-nature-border pb-2.5">
            <div>
              <h2 className="text-sm font-semibold text-nature-text">
                Hydrological Seasonality &amp; Runoff Inflow
              </h2>
              <p className="text-[11px] text-nature-muted">
                Precipitation and snowmelt drive intense seasonal generation spikes in July–September.
              </p>
            </div>
            <span className="text-[10px] font-mono text-sky-800 bg-sky-50 px-2 py-0.5 rounded border border-sky-200">
              Peak: July–September
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={largeHydro?.seasonality_curve || []} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E1E8DF" vertical={false} />
                <XAxis dataKey="month_name" tick={{ fontSize: 11, fill: '#748078' }} tickLine={false} />
                <YAxis
                  yAxisId="gen"
                  tick={{ fontSize: 11, fill: '#748078' }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                />
                <YAxis
                  yAxisId="cuf"
                  orientation="right"
                  tick={{ fontSize: 11, fill: '#748078' }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip
                  formatter={(value: any, name: any) => [
                    name === 'Large Hydro Gen' ? `${Number(value).toLocaleString()} MU` : `${Number(value).toFixed(1)}%`,
                    name,
                  ]}
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderColor: '#E1E8DF',
                    borderRadius: '6px',
                    fontSize: '11px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Line
                  yAxisId="gen"
                  type="monotone"
                  dataKey="generation_mu"
                  name="Large Hydro Gen"
                  stroke="#5689B5"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#5689B5' }}
                />
                <Line
                  yAxisId="cuf"
                  type="monotone"
                  dataKey="average_cuf_pct"
                  name="Plant Load Factor (%)"
                  stroke="#26966B"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={{ r: 2, fill: '#26966B' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* State Hydro Leaderboard */}
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-nature-border pb-2.5">
            <div>
              <h2 className="text-sm font-semibold text-nature-text">
                Leading Hydroelectric Generating States
              </h2>
              <p className="text-[11px] text-nature-muted">
                {hydroView === 'SMALL' ? 'Small Hydro (<=25MW)' : 'Large Hydro (>25MW)'} generation outturn (MU).
              </p>
            </div>
            <span className="text-[11px] font-mono text-sky-800 bg-sky-50 px-2 py-0.5 rounded">
              MU Outturn
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={activeLeaders.slice(0, 8)}
                layout="vertical"
                margin={{ top: 10, right: 20, left: 20, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#E1E8DF" horizontal={false} />
                <XAxis
                  type="number"
                  tick={{ fontSize: 11, fill: '#748078' }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                />
                <YAxis
                  dataKey="name"
                  type="category"
                  tick={{ fontSize: 11, fill: '#26332C' }}
                  tickLine={false}
                  width={110}
                />
                <Tooltip
                  formatter={(value: any) => [`${Number(value).toLocaleString()} MU`, 'Generation']}
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderColor: '#E1E8DF',
                    borderRadius: '6px',
                    fontSize: '11px',
                  }}
                />
                <Bar dataKey="generation_mu" fill="#5689B5" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Hydro Basin Ledger */}
      <div className="rounded-lg border border-nature-border bg-white shadow-sm overflow-hidden">
        <div className="p-4 border-b border-nature-border flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-nature-text">
              Hydroelectric Fleet &amp; River Basin Registry
            </h3>
            <p className="text-[11px] text-nature-muted">
              Installed capacity and river basin systems according to CEA National Hydro Inventory.
            </p>
          </div>
          <span className="text-xs text-nature-muted font-mono">
            {activeLeaders.length} Jurisdictions
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-nature-bg border-b border-nature-border text-nature-muted font-medium">
                <th className="py-2.5 px-3">Rank</th>
                <th className="py-2.5 px-3">State</th>
                <th className="py-2.5 px-3">Region</th>
                <th className="py-2.5 px-3 text-right">Generation (MU)</th>
                <th className="py-2.5 px-3 text-right">National Share</th>
                <th className="py-2.5 px-3 text-right">Installed Fleet (MW)</th>
                <th className="py-2.5 px-3 text-center">Primary River Basin</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-nature-border">
              {activeLeaders.map((s) => (
                <tr key={s.code} className="hover:bg-nature-bg/60 transition-colors">
                  <td className="py-2.5 px-3 font-mono font-medium text-nature-muted">#{s.rank}</td>
                  <td className="py-2.5 px-3 font-semibold text-nature-text">{s.name}</td>
                  <td className="py-2.5 px-3">
                    <span className="px-1.5 py-0.5 rounded font-mono text-[10px] bg-nature-bg border border-nature-border">
                      {s.region_code}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono font-medium text-[#5689B5]">
                    {s.generation_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono font-medium">
                    {s.share_pct.toFixed(1)}%
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono font-semibold">
                    {s.capacity_mw.toLocaleString()} MW
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <span className="text-[10px] text-sky-800 font-medium">
                      {s.code === 'IN-HP' && 'Satluj / Beas / Ravi'}
                      {s.code === 'IN-UT' && 'Bhagirathi / Alaknanda (Ganga)'}
                      {s.code === 'IN-JK' && 'Chenab / Jhelum Basin'}
                      {s.code === 'IN-SK' && 'Teesta River System'}
                      {s.code === 'IN-KL' && 'Periyar / Idamalayar'}
                      {s.code === 'IN-KA' && 'Sharavathi / Kalinadi'}
                      {s.code === 'IN-MH' && 'Koyna Hydro Project'}
                      {s.code === 'IN-AP' && 'Krishna / Srisailam Basin'}
                      {s.code === 'IN-AR' && 'Kameng / Subansiri Basin'}
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

