import React, { useEffect, useState } from 'react';
import {
  Layers,
  MapPin,
  TrendingUp,
  Wind,
  Sun,
  Droplets,
  Zap,
  ShieldCheck,
  Building,
  BarChart3,
  Calendar,
} from 'lucide-react';
import { IndiaRegionalComparison } from '../../types/india';
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
  Legend,
  CartesianGrid,
  Cell,
} from 'recharts';

export const RegionalComparisonPage: React.FC = () => {
  const [data, setData] = useState<IndiaRegionalComparison[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedYear, setSelectedYear] = useState<number>(2025);
  const [activeRegion, setActiveRegion] = useState<string | null>(null);

  const fetchRegionalData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await indiaApi.getRegionalComparison(selectedYear);
      setData(res);
      if (res.length > 0 && !activeRegion) {
        setActiveRegion(res[0].region_code);
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load regional grid comparison data from CEA analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRegionalData();
  }, [selectedYear]);

  if (loading && data.length === 0) {
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

  if (error && data.length === 0) {
    return <ErrorAlert title="Regional Data Loading Error" message={error} onRetry={fetchRegionalData} />;
  }

  const totalNationalGen = data.reduce((acc, r) => acc + r.total_generation_mu, 0);
  const totalNationalCap = data.reduce((acc, r) => acc + r.total_capacity_mw, 0);
  const topRegionByGen = [...data].sort((a, b) => b.total_generation_mu - a.total_generation_mu)[0];
  const topRegionByCap = [...data].sort((a, b) => b.total_capacity_mw - a.total_capacity_mw)[0];

  // Chart data preparation
  const chartData = data.map((r) => ({
    region: r.name,
    code: r.region_code,
    Solar: Math.round(r.solar_mu),
    Wind: Math.round(r.wind_mu),
    Hydro: Math.round(r.hydro_mu),
    Total: Math.round(r.total_generation_mu),
    CapacityGW: Number((r.total_capacity_mw / 1000).toFixed(1)),
  }));

  const selectedRegionData = data.find((r) => r.region_code === activeRegion) || data[0];

  return (
    <div className="space-y-5">
      {/* Scope Header */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-semibold text-nature-text">
              Five Regional Grid Councils Comparison
            </h1>
            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-nature-forest border border-emerald-200 text-[10px] font-mono font-medium flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-nature-forest" />
              5 Regional Grids &bull; Calibrated Model
            </span>
          </div>
          <p className="text-xs text-nature-muted">
            Evaluation of renewable energy generation, capacity deployment, and technology outturns across India's five regional grids (NR, WR, SR, ER, NER).
          </p>
        </div>

        {/* Year Filter */}
        <div className="flex items-center space-x-2">
          <Calendar className="w-3.5 h-3.5 text-nature-muted" />
          <span className="text-xs font-medium text-nature-muted">Annual Scope:</span>
          <div className="flex rounded-md border border-nature-border bg-nature-bg p-0.5">
            {[2022, 2023, 2024, 2025, 2026].map((yr) => (
              <button
                key={yr}
                onClick={() => setSelectedYear(yr)}
                className={`px-2.5 py-1 text-xs rounded transition-colors ${
                  selectedYear === yr
                    ? 'bg-nature-forest text-white font-medium shadow-xs'
                    : 'text-nature-muted hover:text-nature-text'
                }`}
              >
                {yr}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* National Grid Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          title="National RE Generation"
          value={`${totalNationalGen.toLocaleString(undefined, { maximumFractionDigits: 0 })} MU`}
          subtitle={`Sum of 5 Regional Grids (${selectedYear})`}
          icon={<Zap className="w-4 h-4 text-nature-forest" />}
          trend="neutral"
        />
        <MetricCard
          title="Total Installed Capacity"
          value={`${(totalNationalCap / 1000).toFixed(1)} GW`}
          subtitle={`${totalNationalCap.toLocaleString()} MW grid connected`}
          icon={<Layers className="w-4 h-4 text-nature-forecast" />}
          trend="neutral"
        />
        <MetricCard
          title="Leading Generation Grid"
          value={topRegionByGen ? `${topRegionByGen.name}` : '-'}
          subtitle={topRegionByGen ? `${topRegionByGen.total_generation_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })} MU (${((topRegionByGen.total_generation_mu / (totalNationalGen || 1)) * 100).toFixed(1)}%)` : ''}
          icon={<TrendingUp className="w-4 h-4 text-nature-actual" />}
          trend="positive"
        />
        <MetricCard
          title="Leading Capacity Grid"
          value={topRegionByCap ? `${topRegionByCap.name}` : '-'}
          subtitle={topRegionByCap ? `${(topRegionByCap.total_capacity_mw / 1000).toFixed(1)} GW capacity installed` : ''}
          icon={<Building className="w-4 h-4 text-[#D49A42]" />}
          trend="neutral"
        />
      </div>

      {/* Grid Generation by Source Stacked Bar Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-nature-border pb-2.5">
            <div>
              <h2 className="text-sm font-semibold text-nature-text">
                Regional Renewable Generation Mix ({selectedYear})
              </h2>
              <p className="text-[11px] text-nature-muted">
                Million Units (MU) by primary generation stream: Solar, Wind, and Hydro.
              </p>
            </div>
            <span className="text-[11px] font-mono text-nature-forest bg-nature-forest-light px-2 py-0.5 rounded">
              Unit: Million Units (MU)
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E1E8DF" vertical={false} />
                <XAxis dataKey="code" tick={{ fontSize: 11, fill: '#748078' }} tickLine={false} />
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
                <Bar dataKey="Solar" stackId="a" fill="#D49A42" />
                <Bar dataKey="Wind" stackId="a" fill="#26966B" />
                <Bar dataKey="Hydro" stackId="a" fill="#5689B5" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Selected Regional Deep-Dive Card */}
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between border-b border-nature-border pb-2.5">
              <h3 className="text-sm font-semibold text-nature-text">
                Regional Profile
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-nature-bg border border-nature-border text-nature-text">
                {selectedRegionData?.region_code} Grid
              </span>
            </div>

            <div className="mt-3 space-y-3">
              <div>
                <span className="text-[10px] uppercase font-semibold text-nature-muted tracking-wider">
                  Regional Council
                </span>
                <p className="text-base font-semibold text-nature-text">{selectedRegionData?.name}</p>
                <div className="flex items-center space-x-1.5 text-xs text-nature-muted mt-0.5">
                  <MapPin className="w-3.5 h-3.5 text-nature-muted" />
                  <span>HQ: {selectedRegionData?.headquarters}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-nature-border">
                <div className="p-2.5 rounded bg-nature-bg/60 border border-nature-border">
                  <span className="text-[10px] text-nature-muted block">Total Generation</span>
                  <span className="text-sm font-semibold text-nature-text">
                    {selectedRegionData?.total_generation_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })} MU
                  </span>
                </div>
                <div className="p-2.5 rounded bg-nature-bg/60 border border-nature-border">
                  <span className="text-[10px] text-nature-muted block">Installed Capacity</span>
                  <span className="text-sm font-semibold text-nature-text">
                    {(selectedRegionData?.total_capacity_mw / 1000).toFixed(1)} GW
                  </span>
                </div>
              </div>

              {/* Fuel share breakdown */}
              <div className="space-y-2 pt-2">
                <div className="text-[11px] font-medium text-nature-text flex justify-between">
                  <span className="flex items-center gap-1.5"><Sun className="w-3 h-3 text-[#D49A42]" /> Solar Share</span>
                  <span className="font-mono">{selectedRegionData?.solar_share_pct.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5">
                  <div
                    className="bg-[#D49A42] h-1.5 rounded-full"
                    style={{ width: `${Math.min(selectedRegionData?.solar_share_pct || 0, 100)}%` }}
                  />
                </div>

                <div className="text-[11px] font-medium text-nature-text flex justify-between">
                  <span className="flex items-center gap-1.5"><Wind className="w-3 h-3 text-[#26966B]" /> Wind Share</span>
                  <span className="font-mono">{selectedRegionData?.wind_share_pct.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5">
                  <div
                    className="bg-[#26966B] h-1.5 rounded-full"
                    style={{ width: `${Math.min(selectedRegionData?.wind_share_pct || 0, 100)}%` }}
                  />
                </div>

                <div className="text-[11px] font-medium text-nature-text flex justify-between">
                  <span className="flex items-center gap-1.5"><Droplets className="w-3 h-3 text-[#5689B5]" /> Hydro Share</span>
                  <span className="font-mono">{selectedRegionData?.hydro_share_pct.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5">
                  <div
                    className="bg-[#5689B5] h-1.5 rounded-full"
                    style={{ width: `${Math.min(selectedRegionData?.hydro_share_pct || 0, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="p-2.5 rounded bg-amber-50/60 border border-amber-200/60 text-[11px] text-[#8C611C]">
            <span className="font-semibold block">Grid Characteristics:</span>
            {selectedRegionData?.region_code === 'SR' && 'High renewable penetration with strong seasonal wind during SW monsoon and year-round solar generation.'}
            {selectedRegionData?.region_code === 'WR' && 'Heavy industrial load center with major wind capacity in Gujarat/Maharashtra and huge solar parks in Kutch.'}
            {selectedRegionData?.region_code === 'NR' && 'Solar leader anchored by Rajasthan Thar Desert parks alongside massive Himalayan hydro in HP & Uttarakhand.'}
            {selectedRegionData?.region_code === 'ER' && 'Thermal-dominant base grid transitioning to solar and pumped hydro storage assets.'}
            {selectedRegionData?.region_code === 'NER' && 'Precipitation-rich Himalayan river basins with vast untapped run-of-river hydro potential.'}
          </div>
        </div>
      </div>

      {/* Full 5-Region Comparison Table */}
      <div className="rounded-lg border border-nature-border bg-white shadow-sm overflow-hidden">
        <div className="p-4 border-b border-nature-border flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-nature-text">
              Five Regional Grids Comprehensive Matrix
            </h3>
            <p className="text-[11px] text-nature-muted">
              Click a row to focus on that regional grid profile.
            </p>
          </div>
          <span className="text-xs text-nature-muted font-mono">
            {data.length} Grids Analyzed
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-nature-bg border-b border-nature-border text-nature-muted font-medium">
                <th className="py-2.5 px-3">Region</th>
                <th className="py-2.5 px-3">HQ / RLDC</th>
                <th className="py-2.5 px-3 text-right">Total Gen (MU)</th>
                <th className="py-2.5 px-3 text-right">National Share</th>
                <th className="py-2.5 px-3 text-right">Solar (MU)</th>
                <th className="py-2.5 px-3 text-right">Wind (MU)</th>
                <th className="py-2.5 px-3 text-right">Hydro (MU)</th>
                <th className="py-2.5 px-3 text-right">Installed Cap (GW)</th>
                <th className="py-2.5 px-3 text-center">Focus</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-nature-border">
              {data.map((r) => {
                const isSelected = activeRegion === r.region_code;
                const natShare = ((r.total_generation_mu / (totalNationalGen || 1)) * 100).toFixed(1);
                return (
                  <tr
                    key={r.region_code}
                    onClick={() => setActiveRegion(r.region_code)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-nature-forest-light/60 font-medium text-nature-forest'
                        : 'hover:bg-nature-bg/60 text-nature-text'
                    }`}
                  >
                    <td className="py-2.5 px-3">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-[11px] font-semibold px-1.5 py-0.5 rounded bg-nature-bg border border-nature-border">
                          {r.region_code}
                        </span>
                        <span>{r.name}</span>
                      </div>
                    </td>
                    <td className="py-2.5 px-3 text-nature-muted font-mono">{r.headquarters}</td>
                    <td className="py-2.5 px-3 text-right font-mono font-medium">
                      {r.total_generation_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-nature-muted">
                      {natShare}%
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-[#D49A42]">
                      {r.solar_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-[#26966B]">
                      {r.wind_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono text-[#5689B5]">
                      {r.hydro_mu.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="py-2.5 px-3 text-right font-mono font-semibold">
                      {(r.total_capacity_mw / 1000).toFixed(2)}
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setActiveRegion(r.region_code);
                        }}
                        className={`px-2 py-0.5 rounded text-[10px] font-medium transition-colors ${
                          isSelected
                            ? 'bg-nature-forest text-white'
                            : 'bg-white border border-nature-border text-nature-muted hover:text-nature-text'
                        }`}
                      >
                        {isSelected ? 'Active' : 'Select'}
                      </button>
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

