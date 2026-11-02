import React, { useEffect, useState } from 'react';
import {
  Sun,
  TrendingUp,
  MapPin,
  Calendar,
  ShieldCheck,
  Zap,
  Award,
  Layers,
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

export const SolarAnalyticsPage: React.FC = () => {
  const [data, setData] = useState<IndiaSourceAnalytics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSolarData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await indiaApi.getSourceAnalytics('SOLAR');
      setData(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to load solar energy analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSolarData();
  }, []);

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
    return <ErrorAlert title="Solar Analytics Loading Error" message={error} onRetry={fetchSolarData} />;
  }

  const leaders = data?.state_leaderboard || [];
  const topSolarLeader = leaders[0];
  const totalSolarGen = data?.annual_generation_2025_mu || 0;
  const totalSolarCap = leaders.reduce((acc, s) => acc + s.capacity_mw, 0);

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-semibold text-nature-text">
              Solar Photovoltaic (PV) Sector Intelligence
            </h1>
            <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-[10px] font-mono font-medium flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-amber-800" />
              Solar PV Fleet Model &bull; Benchmark
            </span>
          </div>
          <p className="text-xs text-nature-muted">
            Intelligence on India's utility-scale solar parks, rooftop installations, Global Horizontal Irradiance (GHI) regimes, and spring outturn peaks.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono text-amber-800 bg-amber-50 px-2.5 py-1 rounded border border-amber-200">
            Annual Scope: 2025 Model Outturn
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          title="Total Solar Generation"
          value={`${totalSolarGen.toLocaleString(undefined, { maximumFractionDigits: 0 })} MU`}
          subtitle="Annual 2025 model outturn"
          icon={<Sun className="w-4 h-4 text-[#D49A42]" />}
          trend="neutral"
        />
        <MetricCard
          title="Installed Solar Capacity"
          value={`${(totalSolarCap / 1000).toFixed(2)} GW`}
          subtitle={`${totalSolarCap.toLocaleString()} MW grid connected`}
          icon={<Zap className="w-4 h-4 text-nature-forest" />}
          trend="positive"
        />
        <MetricCard
          title="Leading Solar State"
          value={topSolarLeader ? topSolarLeader.name : '-'}
          subtitle={topSolarLeader ? `${topSolarLeader.generation_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })} MU (${topSolarLeader.share_pct.toFixed(1)}% share)` : ''}
          icon={<Award className="w-4 h-4 text-[#D49A42]" />}
          trend="positive"
        />
        <MetricCard
          title="Ultra-Mega Parks Hub"
          value="Bhadla &amp; Pavagada"
          subtitle="World's largest contiguous solar clusters"
          icon={<Layers className="w-4 h-4 text-nature-forecast" />}
          trend="neutral"
        />
      </div>

      {/* Charts Grid: Seasonality Spring Peak & Leaderboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Seasonality Curve (Spring peak, monsoon cloud dip) */}
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-nature-border pb-2.5">
            <div>
              <h2 className="text-sm font-semibold text-nature-text">
                Seasonal Solar Generation Curve
              </h2>
              <p className="text-[11px] text-nature-muted">
                Pre-monsoon spring insolation peak (March–May) vs cloud-cover moderation (July–August).
              </p>
            </div>
            <span className="text-[10px] font-mono text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
              Peak: March–May
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data?.seasonality_curve || []} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
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
                    name === 'Generation' ? `${Number(value).toLocaleString()} MU` : `${Number(value).toFixed(1)}%`,
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
                  name="Generation"
                  stroke="#D49A42"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#D49A42' }}
                />
                <Line
                  yAxisId="cuf"
                  type="monotone"
                  dataKey="average_cuf_pct"
                  name="Average CUF (%)"
                  stroke="#26966B"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={{ r: 2, fill: '#26966B' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* State Capacity & Generation Leaderboard */}
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-nature-border pb-2.5">
            <div>
              <h2 className="text-sm font-semibold text-nature-text">
                Top Solar Producing States (2025)
              </h2>
              <p className="text-[11px] text-nature-muted">
                Generation in Million Units (MU) by leading states.
              </p>
            </div>
            <span className="text-[11px] font-mono text-amber-800 bg-amber-50 px-2 py-0.5 rounded">
              MU Outturn
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={leaders.slice(0, 8)}
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
                  width={90}
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
                <Bar dataKey="generation_mu" fill="#D49A42" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Solar Leaderboard Matrix */}
      <div className="rounded-lg border border-nature-border bg-white shadow-sm overflow-hidden">
        <div className="p-4 border-b border-nature-border flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-nature-text">
              State Solar Outturn &amp; Plant Capacity Matrix
            </h3>
            <p className="text-[11px] text-nature-muted">
              Capacity Utilization Factors (CUF) and flagship solar parks.
            </p>
          </div>
          <span className="text-xs text-nature-muted font-mono">
            {leaders.length} Jurisdictions
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
                <th className="py-2.5 px-3 text-right">Installed Solar (MW)</th>
                <th className="py-2.5 px-3 text-right">Implied Annual CUF</th>
                <th className="py-2.5 px-3 text-center">Anchor Park</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-nature-border">
              {leaders.map((s) => {
                const cuf = s.capacity_mw > 0 ? ((s.generation_mu * 1000) / (s.capacity_mw * 8760)) * 100 : 0;
                return (
                  <tr key={s.code} className="hover:bg-nature-bg/60 transition-colors">
                    <td className="py-2.5 px-3 font-mono font-medium text-nature-muted">#{s.rank}</td>
                    <td className="py-2.5 px-3 font-semibold text-nature-text">{s.name}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-1.5 py-0.5 rounded font-mono text-[10px] bg-nature-bg border border-nature-border">
                        {s.region_code}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono font-medium text-[#D49A42]">
                      {s.generation_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono font-medium">
                      {s.share_pct.toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono font-semibold">
                      {s.capacity_mw.toLocaleString()} MW
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-nature-muted">
                      {cuf.toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <span className="text-[10px] text-amber-800 font-medium">
                        {s.code === 'IN-RJ' && 'Bhadla (2,245 MW)'}
                        {s.code === 'IN-GJ' && 'Khavda Renewable Park'}
                        {s.code === 'IN-KA' && 'Pavagada Solar Park (2,050 MW)'}
                        {s.code === 'IN-TN' && 'Kamuthi Solar Power (648 MW)'}
                        {s.code === 'IN-AP' && 'Kurnool Ultra Solar (1,000 MW)'}
                        {s.code === 'IN-MH' && 'Shirdi & Sakri Projects'}
                        {s.code === 'IN-MP' && 'Rewa Ultra Mega Solar (750 MW)'}
                        {s.code === 'IN-UP' && 'Jalaun & Bundelkhand Parks'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

