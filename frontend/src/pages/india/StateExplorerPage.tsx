import React, { useEffect, useState } from 'react';
import { IndiaStateItem, IndiaStateProfile, GridRegionCode } from '../../types/india';
import { indiaApi } from '../../services/indiaApi';
import { Search, MapPin, Wind, Sun, ArrowRight, ShieldCheck, Filter } from 'lucide-react';
import { Skeleton } from '../../components/common/Skeleton';
import { ErrorAlert } from '../../components/common/ErrorAlert';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';

export const StateExplorerPage: React.FC = () => {
  const [states, setStates] = useState<IndiaStateItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedRegion, setSelectedRegion] = useState<string>('ALL');
  const [windFilter, setWindFilter] = useState<string>('ALL'); // 'ALL' | 'WIND_ONLY' | 'NON_WIND'
  const [typeFilter, setTypeFilter] = useState<string>('ALL'); // 'ALL' | 'STATE' | 'UNION_TERRITORY'

  // Selected State Detail Modal / Side view
  const [activeStateCode, setActiveStateCode] = useState<string>('IN-GJ');
  const [stateProfile, setStateProfile] = useState<IndiaStateProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState<boolean>(false);

  const fetchStates = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await indiaApi.getStates();
      setStates(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load state directory from CEA registry.');
    } finally {
      setLoading(false);
    }
  };

  const fetchProfile = async (code: string) => {
    setProfileLoading(true);
    try {
      const p = await indiaApi.getStateProfile(code);
      setStateProfile(p);
    } catch (e) {
      console.warn('Failed to load profile:', e);
    } finally {
      setProfileLoading(false);
    }
  };

  useEffect(() => {
    fetchStates();
  }, []);

  useEffect(() => {
    if (activeStateCode) {
      fetchProfile(activeStateCode);
    }
  }, [activeStateCode]);

  const filteredStates = states.filter((st) => {
    const matchesSearch =
      st.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      st.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      st.capital.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesRegion = selectedRegion === 'ALL' || st.region_code === selectedRegion;
    const matchesType = typeFilter === 'ALL' || st.entity_type === typeFilter;
    const matchesWind =
      windFilter === 'ALL' ||
      (windFilter === 'WIND_ONLY' && st.has_wind) ||
      (windFilter === 'NON_WIND' && !st.has_wind);

    return matchesSearch && matchesRegion && matchesType && matchesWind;
  });

  return (
    <div className="space-y-4">
      {/* Page Title */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold text-nature-text">
            State &amp; Union Territory Intelligence Explorer
          </h1>
          <p className="text-xs text-nature-muted font-sans">
            Benchmark profiles for all 28 Indian States and 8 Union Territories calibrated to CEA parameters (Demonstration Data).
          </p>
        </div>

        <span className="text-xs font-mono px-2.5 py-1 rounded bg-nature-bg text-nature-forest border border-nature-border font-medium">
          Showing {filteredStates.length} of 36 Geographies
        </span>
      </div>

      {error && <ErrorAlert title="State Directory Error" message={error} onRetry={fetchStates} />}

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        {/* Search Input */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-nature-muted absolute left-3 top-3 pointer-events-none" />
          <input
            type="text"
            placeholder="Search state, UT, capital or code..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-xs rounded-md border border-nature-border bg-white pl-9 pr-3 py-2 text-nature-text placeholder:text-nature-muted/60 focus:outline-none focus:ring-1 focus:ring-nature-forest"
          />
        </div>

        {/* Region Filter */}
        <select
          value={selectedRegion}
          onChange={(e) => setSelectedRegion(e.target.value)}
          className="text-xs rounded-md border border-nature-border bg-white px-3 py-2 text-nature-text focus:outline-none focus:ring-1 focus:ring-nature-forest font-medium"
        >
          <option value="ALL">All Grid Regions</option>
          <option value="NR">Northern Region (NR)</option>
          <option value="WR">Western Region (WR)</option>
          <option value="SR">Southern Region (SR)</option>
          <option value="ER">Eastern Region (ER)</option>
          <option value="NER">North Eastern Region (NER)</option>
        </select>

        {/* Type Filter */}
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="text-xs rounded-md border border-nature-border bg-white px-3 py-2 text-nature-text focus:outline-none focus:ring-1 focus:ring-nature-forest font-medium"
        >
          <option value="ALL">All Entity Types</option>
          <option value="STATE">28 States</option>
          <option value="UNION_TERRITORY">8 Union Territories</option>
        </select>

        {/* Wind Presence Filter */}
        <select
          value={windFilter}
          onChange={(e) => setWindFilter(e.target.value)}
          className="text-xs rounded-md border border-nature-border bg-white px-3 py-2 text-nature-text focus:outline-none focus:ring-1 focus:ring-nature-forest font-medium"
        >
          <option value="ALL">All Fleet Types</option>
          <option value="WIND_ONLY">States with Active Wind Fleet</option>
          <option value="NON_WIND">Non-Wind Geographies (0.0 MW)</option>
        </select>
      </div>

      {/* Main Grid: Directory List & Deep Dive Profile */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left State Cards (2 cols) */}
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[720px] overflow-y-auto pr-1">
          {loading && states.length === 0 ? (
            Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-28 w-full" />)
          ) : (
            filteredStates.map((st) => {
              const isSelected = activeStateCode === st.code;
              return (
                <div
                  key={st.code}
                  onClick={() => setActiveStateCode(st.code)}
                  className={`p-3.5 rounded-lg border transition-all cursor-pointer shadow-xs ${
                    isSelected
                      ? 'border-nature-forest bg-emerald-50/40 ring-1 ring-nature-forest'
                      : 'border-nature-border bg-white hover:border-nature-forest/40'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="text-xs font-semibold text-nature-text font-sans">{st.name}</h4>
                      <span className="text-[10px] text-nature-muted font-mono">
                        {st.capital} &bull; {st.region_code} Region
                      </span>
                    </div>
                    <span className="font-mono text-[10px] font-semibold px-1.5 py-0.5 rounded bg-nature-bg border border-nature-border text-nature-forest">
                      {st.code}
                    </span>
                  </div>

                  <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] font-mono border-t border-nature-border/60 pt-2">
                    <div>
                      <span className="text-[10px] text-nature-muted block font-sans">Total Capacity</span>
                      <strong className="text-nature-text">{st.total_capacity_mw.toLocaleString()} MW</strong>
                    </div>
                    <div>
                      <span className="text-[10px] text-nature-muted block font-sans">Wind Fleet</span>
                      <strong className={st.has_wind ? 'text-nature-actual' : 'text-nature-muted'}>
                        {st.has_wind ? `${st.wind_capacity_mw.toLocaleString()} MW` : '0.0 MW'}
                      </strong>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Active State Deep Dive Profile */}
        <div className="space-y-3">
          {stateProfile ? (
            <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3 sticky top-4">
              <div className="flex items-center justify-between pb-2 border-b border-nature-border">
                <div>
                  <h3 className="text-sm font-semibold text-nature-text">{stateProfile.name}</h3>
                  <span className="text-[10px] text-nature-muted font-mono">
                    {stateProfile.entity_type} &bull; {stateProfile.region_code} Grid &bull; Lat {stateProfile.latitude.toFixed(2)}&deg;
                  </span>
                </div>
                <span className="px-2 py-0.5 rounded bg-emerald-50 text-nature-forest text-xs font-mono font-semibold border border-emerald-200">
                  {stateProfile.code}
                </span>
              </div>

              {/* Capacity Breakdown */}
              <div className="space-y-1.5">
                <span className="text-xs font-semibold text-nature-text block">Installed Capacity Mix (MW):</span>
                <div className="grid grid-cols-2 gap-1.5 text-xs font-mono">
                  {Object.entries(stateProfile.capacity_breakdown).map(([src, mw]) => (
                    <div key={src} className="p-2 rounded bg-nature-bg border border-nature-border">
                      <span className="text-[10px] text-nature-muted block truncate font-sans">
                        {src.replace('_', ' ')}
                      </span>
                      <span className="font-semibold text-nature-text tabular-nums">{mw.toLocaleString()} MW</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Monthly Seasonality Curve */}
              <div className="space-y-1 pt-2 border-t border-nature-border">
                <span className="text-xs font-semibold text-nature-text block">
                  Monthly Seasonality (Average MU):
                </span>
                <div className="h-40">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={stateProfile.seasonality} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                      <XAxis dataKey="month_name" tick={{ fontSize: 10, fill: '#748078' }} />
                      <YAxis tick={{ fontSize: 10, fill: '#748078' }} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#FFFFFF',
                          borderColor: '#E1E8DF',
                          fontSize: '11px',
                          borderRadius: '6px',
                        }}
                      />
                      <Line type="monotone" dataKey="avg_solar_mu" stroke="#D49A42" strokeWidth={2} dot={false} name="Solar (MU)" />
                      {stateProfile.has_wind && (
                        <Line type="monotone" dataKey="avg_wind_mu" stroke="#26966B" strokeWidth={2} dot={false} name="Wind (MU)" />
                      )}
                      <Line type="monotone" dataKey="avg_hydro_mu" stroke="#5689B5" strokeWidth={1.5} dot={false} name="Hydro (MU)" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Methodology & Data Note */}
              <div className="text-[10px] text-nature-muted font-sans pt-1 border-t border-nature-border">
                Calibrated Demonstration Profile &bull; CEA Benchmark Parameters
              </div>
            </div>
          ) : (
            <div className="rounded-lg border border-nature-border bg-white p-6 text-center text-xs text-nature-muted">
              Select any state or Union Territory to inspect its monthly historical series and seasonality profile.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

