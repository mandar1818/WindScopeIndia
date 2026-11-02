import React, { useEffect, useState } from 'react';
import {
  Wind,
  TrendingUp,
  MapPin,
  Calendar,
  AlertCircle,
  ShieldCheck,
  Zap,
  Info,
  Award,
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
  Cell,
  Legend,
} from 'recharts';

export const WindAnalyticsPage: React.FC = () => {
  const [data, setData] = useState<IndiaSourceAnalytics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWindData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await indiaApi.getSourceAnalytics('WIND');
      setData(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to load wind energy analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWindData();
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
    return <ErrorAlert title="Wind Analytics Loading Error" message={error} onRetry={fetchWindData} />;
  }

  const leaders = data?.state_leaderboard || [];
  const topWindLeader = leaders[0];
  const totalWindGen = data?.annual_generation_2025_mu || 0;
  const totalWindCap = leaders.reduce((acc, s) => acc + s.capacity_mw, 0);

  // High-wind states vs Non-wind states count
  const activeWindStates = leaders.filter((s) => s.capacity_mw > 0);
  const nonWindStates = [
    { code: 'IN-BR', name: 'Bihar', reason: 'Wind power density < 200 W/m² (Sub-commercial resource)' },
    { code: 'IN-UP', name: 'Uttar Pradesh', reason: 'Inland Gangetic plains with low mean wind speeds' },
    { code: 'IN-AS', name: 'Assam', reason: 'North-Eastern river basin topography with low wind velocity' },
    { code: 'IN-DL', name: 'Delhi', reason: 'High-density urban territory without utility land availability' },
    { code: 'IN-WB', name: 'West Bengal', reason: 'Limited Class III coastal pockets; zero commercial wind fleet' },
    { code: 'IN-PB', name: 'Punjab', reason: 'Sub-threshold mean annual wind speeds at 100m–120m hub height' },
  ];

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-semibold text-nature-text">
              Wind Energy Sector Intelligence
            </h1>
            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-nature-forest border border-emerald-200 text-[10px] font-mono font-medium flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-nature-forest" />
              Calibrated Wind Model &bull; NIWE Benchmark
            </span>
          </div>
          <p className="text-xs text-nature-muted">
            Analysis of India's onshore wind turbine fleet, monsoon surge seasonality (June–September), coastal wind corridors, and geographic concentration.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono text-nature-forest bg-nature-forest-light px-2.5 py-1 rounded border border-nature-border">
            Annual Scope: 2025 Model Outturn
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          title="Total Wind Generation"
          value={`${totalWindGen.toLocaleString(undefined, { maximumFractionDigits: 0 })} MU`}
          subtitle="Annual 2025 model outturn"
          icon={<Wind className="w-4 h-4 text-[#26966B]" />}
          trend="neutral"
        />
        <MetricCard
          title="Installed Wind Fleet"
          value={`${(totalWindCap / 1000).toFixed(2)} GW`}
          subtitle={`${totalWindCap.toLocaleString()} MW across commercial states`}
          icon={<Zap className="w-4 h-4 text-nature-forest" />}
          trend="positive"
        />
        <MetricCard
          title="Leading Wind State"
          value={topWindLeader ? topWindLeader.name : '-'}
          subtitle={topWindLeader ? `${topWindLeader.generation_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })} MU (${topWindLeader.share_pct.toFixed(1)}% share)` : ''}
          icon={<Award className="w-4 h-4 text-[#D49A42]" />}
          trend="positive"
        />
        <MetricCard
          title="Active Wind States"
          value={`${activeWindStates.length} of 36`}
          subtitle="Strictly 8 commercial wind coastal/arid states"
          icon={<MapPin className="w-4 h-4 text-nature-forecast" />}
          trend="neutral"
        />
      </div>

      {/* Charts Grid: Seasonality Monsoon Surge & Leaderboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Seasonality Curve (Monsoon surge) */}
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-nature-border pb-2.5">
            <div>
              <h2 className="text-sm font-semibold text-nature-text">
                Seasonal Wind Outturn Profile (Monsoon Surge)
              </h2>
              <p className="text-[11px] text-nature-muted">
                South-West monsoon brings ~65% of annual wind generation between June and September.
              </p>
            </div>
            <span className="text-[10px] font-mono text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              Peak CUF: ~38%
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
                  stroke="#26966B"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#26966B' }}
                />
                <Line
                  yAxisId="cuf"
                  type="monotone"
                  dataKey="average_cuf_pct"
                  name="Average CUF (%)"
                  stroke="#D49A42"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={{ r: 2, fill: '#D49A42' }}
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
                State Wind Generation Leaderboard (2025)
              </h2>
              <p className="text-[11px] text-nature-muted">
                Generation in Million Units (MU) by leading states.
              </p>
            </div>
            <span className="text-[11px] font-mono text-nature-forest bg-nature-forest-light px-2 py-0.5 rounded">
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
                <Bar dataKey="generation_mu" fill="#26966B" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* State-by-State Wind Fleet Table */}
      <div className="rounded-lg border border-nature-border bg-white shadow-sm overflow-hidden">
        <div className="p-4 border-b border-nature-border flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-nature-text">
              Active Wind Turbine Capacity &amp; Generation Matrix
            </h3>
            <p className="text-[11px] text-nature-muted">
              States with commercial grid-connected wind assets evaluated against CEA benchmarks.
            </p>
          </div>
          <span className="text-xs text-nature-muted font-mono">
            {leaders.length} Wind Jurisdictions
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
                <th className="py-2.5 px-3 text-right">Implied Annual CUF</th>
                <th className="py-2.5 px-3 text-center">Corridor</th>
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
                    <td className="py-2.5 px-3 text-right font-mono font-medium text-[#26966B]">
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
                      <span className="text-[10px] text-nature-forest font-medium">
                        {s.code === 'IN-GJ' && 'Kutch / Saurashtra'}
                        {s.code === 'IN-TN' && 'Muppandal / Palghat'}
                        {s.code === 'IN-RJ' && 'Jaisalmer Desert'}
                        {s.code === 'IN-KA' && 'Chitradurga / Gadag'}
                        {s.code === 'IN-MH' && 'Satara / Sangli'}
                        {s.code === 'IN-AP' && 'Anantapur / Kurnool'}
                        {s.code === 'IN-MP' && 'Dewas / Ratlam'}
                        {s.code === 'IN-KL' && 'Kanjikode Pass'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Non-Wind States Disclosure Box */}
      <div className="rounded-lg border border-amber-200 bg-amber-50/50 p-4 shadow-sm space-y-2.5">
        <div className="flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-[#D49A42]" />
          <h4 className="text-xs font-semibold text-[#8C611C]">
            Physical Zero-Wind States &amp; Fleet Disclosures
          </h4>
        </div>
        <p className="text-[11px] text-[#8C611C]/90 leading-relaxed">
          In accordance with National Institute of Wind Energy (NIWE) wind resource assessments and CEA regional data, states located in sub-threshold wind regimes feature <strong>strictly 0.0 MW commercial wind turbine capacity and 0.000 MU generation</strong>. These physical zero-fleet jurisdictions are explicitly distinguished from missing or unreported observations.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 pt-2">
          {nonWindStates.map((st) => (
            <div key={st.code} className="p-2 rounded bg-white border border-amber-200/80 text-xs space-y-0.5">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-nature-text">{st.name}</span>
                <span className="font-mono text-[10px] text-nature-muted bg-nature-bg px-1 rounded">0.0 MW</span>
              </div>
              <p className="text-[10px] text-nature-muted leading-tight">{st.reason}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

