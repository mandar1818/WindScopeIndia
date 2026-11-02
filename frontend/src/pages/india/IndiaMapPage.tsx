import React, { useEffect, useState } from 'react';
import { IndiaMapItem, IndiaStateProfile, GridRegionCode } from '../../types/india';
import { indiaApi } from '../../services/indiaApi';
import { IndiaInteractiveMap } from '../../components/india/IndiaInteractiveMap';
import { Skeleton } from '../../components/common/Skeleton';
import { ErrorAlert } from '../../components/common/ErrorAlert';
import { X, ArrowRight, ShieldCheck, Info, BarChart3, Wind, Sun, Droplets } from 'lucide-react';

export const IndiaMapPage: React.FC = () => {
  const [mapData, setMapData] = useState<IndiaMapItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [metric, setMetric] = useState<'generation' | 'capacity'>('generation');
  const [selectedSource, setSelectedSource] = useState<string | undefined>(undefined);
  const [selectedRegion, setSelectedRegion] = useState<GridRegionCode | undefined>(undefined);
  const [selectedYear, setSelectedYear] = useState<number>(2026);
  const [selectedMonth, setSelectedMonth] = useState<number | null>(1);

  // Selected State Detail Drawer
  const [selectedStateCode, setSelectedStateCode] = useState<string | null>('IN-GJ');
  const [stateProfile, setStateProfile] = useState<IndiaStateProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState<boolean>(false);

  // Comparison State
  const [comparisonStateCode, setComparisonStateCode] = useState<string | null>('IN-TN');
  const [comparisonProfile, setComparisonProfile] = useState<IndiaStateProfile | null>(null);

  const fetchMapData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await indiaApi.getMapData(metric, selectedSource, selectedYear, selectedMonth);
      setMapData(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load map data from CEA analytics service.');
    } finally {
      setLoading(false);
    }
  };

  const fetchStateProfile = async (code: string, isComparison: boolean = false) => {
    if (!isComparison) setProfileLoading(true);
    try {
      const prof = await indiaApi.getStateProfile(code);
      if (isComparison) {
        setComparisonProfile(prof);
      } else {
        setStateProfile(prof);
      }
    } catch (e) {
      console.warn('Failed to load state profile:', e);
    } finally {
      if (!isComparison) setProfileLoading(false);
    }
  };

  useEffect(() => {
    fetchMapData();
  }, [metric, selectedSource, selectedRegion, selectedYear, selectedMonth]);

  useEffect(() => {
    if (selectedStateCode) {
      fetchStateProfile(selectedStateCode, false);
    }
  }, [selectedStateCode]);

  useEffect(() => {
    if (comparisonStateCode) {
      fetchStateProfile(comparisonStateCode, true);
    }
  }, [comparisonStateCode]);

  return (
    <div className="space-y-4">
      {/* Page Title & Scope Ribbon */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold text-nature-text">
            Interactive India Renewable Energy Map
          </h1>
          <p className="text-xs text-nature-muted font-sans">
            Vector choropleth coverage across all 28 Indian States and 8 Union Territories with calibrated demonstration outturns.
          </p>
        </div>

        {/* Global Year & Month Filter */}
        <div className="flex items-center space-x-2 text-xs">
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="rounded-md border border-nature-border bg-white px-2.5 py-1 text-nature-text font-medium"
          >
            {[2026, 2025, 2024, 2023, 2022, 2021, 2020].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>

          <select
            value={selectedMonth === null ? 'ALL' : String(selectedMonth)}
            onChange={(e) => setSelectedMonth(e.target.value === 'ALL' ? null : Number(e.target.value))}
            className="rounded-md border border-nature-border bg-white px-2.5 py-1 text-nature-text font-medium"
          >
            <option value="ALL">Full Year</option>
            <option value="1">January</option>
            <option value="4">April</option>
            <option value="7">July (Monsoon)</option>
            <option value="10">October</option>
          </select>
        </div>
      </div>

      {error && <ErrorAlert title="Map Data Ingestion Error" message={error} onRetry={fetchMapData} />}

      {/* Main Map & Side Details Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Vector Map Container (2 cols) */}
        <div className="lg:col-span-2">
          {loading && mapData.length === 0 ? (
            <Skeleton className="h-[620px] w-full" />
          ) : (
            <IndiaInteractiveMap
              data={mapData}
              metric={metric}
              selectedSource={selectedSource}
              selectedStateCode={selectedStateCode || undefined}
              onSelectState={(code) => setSelectedStateCode(code)}
              onMetricChange={setMetric}
              onSourceChange={setSelectedSource}
              onRegionChange={setSelectedRegion}
              selectedRegion={selectedRegion}
            />
          )}
        </div>

        {/* Side Details & Comparison Drawer (1 col) */}
        <div className="space-y-4">
          {/* Primary Selected State Card */}
          {stateProfile ? (
            <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-nature-border">
                <div>
                  <h3 className="text-sm font-semibold text-nature-text font-sans">{stateProfile.name}</h3>
                  <span className="text-[10px] text-nature-muted font-mono">
                    {stateProfile.code} &bull; Capital: {stateProfile.capital} &bull; {stateProfile.region_code} Grid
                  </span>
                </div>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-50 text-nature-forest border border-emerald-200 font-mono font-medium">
                  {stateProfile.entity_type}
                </span>
              </div>

              {/* Total Capacity Metric */}
              <div className="p-2.5 rounded-md bg-nature-bg border border-nature-border flex justify-between items-center">
                <span className="text-xs text-nature-muted font-sans">Total RE Capacity:</span>
                <span className="text-sm font-semibold font-mono text-nature-forest tabular-nums">
                  {stateProfile.total_capacity_mw.toLocaleString()} MW
                </span>
              </div>

              {/* Technology Capacity Breakdown */}
              <div className="space-y-1.5 text-xs">
                <span className="text-[11px] font-semibold text-nature-text font-sans block">
                  Installed Fleet Breakdown (MW):
                </span>
                <div className="space-y-1 font-mono text-[11px]">
                  <div className="flex justify-between p-1.5 rounded bg-nature-bg/70">
                    <span className="flex items-center gap-1.5 text-nature-text font-sans">
                      <Sun className="w-3.5 h-3.5 text-nature-risk" /> Solar Power:
                    </span>
                    <span className="font-semibold tabular-nums">
                      {(stateProfile.capacity_breakdown['SOLAR'] || 0).toLocaleString()} MW
                    </span>
                  </div>

                  <div className="flex justify-between p-1.5 rounded bg-nature-bg/70">
                    <span className="flex items-center gap-1.5 text-nature-text font-sans">
                      <Wind className="w-3.5 h-3.5 text-nature-actual" /> Wind Power:
                    </span>
                    <span className="font-semibold tabular-nums">
                      {stateProfile.has_wind
                        ? `${(stateProfile.capacity_breakdown['WIND'] || 0).toLocaleString()} MW`
                        : '0.0 MW (No Fleet)'}
                    </span>
                  </div>

                  <div className="flex justify-between p-1.5 rounded bg-nature-bg/70">
                    <span className="flex items-center gap-1.5 text-nature-text font-sans">
                      <Droplets className="w-3.5 h-3.5 text-nature-forecast" /> Large Hydro:
                    </span>
                    <span className="font-semibold tabular-nums">
                      {(stateProfile.capacity_breakdown['LARGE_HYDRO'] || 0).toLocaleString()} MW
                    </span>
                  </div>

                  <div className="flex justify-between p-1.5 rounded bg-nature-bg/70">
                    <span className="flex items-center gap-1.5 text-nature-text font-sans">
                      <BarChart3 className="w-3.5 h-3.5 text-nature-forest" /> Small Hydro:
                    </span>
                    <span className="font-semibold tabular-nums">
                      {(stateProfile.capacity_breakdown['SMALL_HYDRO'] || 0).toLocaleString()} MW
                    </span>
                  </div>
                </div>
              </div>

              {/* Quick Comparison Selector */}
              <div className="pt-2 border-t border-nature-border space-y-2">
                <span className="text-xs font-semibold text-nature-text font-sans block">
                  Compare with another State / UT:
                </span>
                <select
                  value={comparisonStateCode || ''}
                  onChange={(e) => setComparisonStateCode(e.target.value)}
                  className="w-full text-xs rounded-md border border-nature-border bg-white px-2.5 py-1.5 text-nature-text focus:outline-none focus:ring-1 focus:ring-nature-forest font-medium"
                >
                  {mapData.map((d) => (
                    <option key={d.code} value={d.code}>
                      {d.name} ({d.code})
                    </option>
                  ))}
                </select>

                {comparisonProfile && (
                  <div className="p-2.5 rounded-md bg-nature-bg border border-nature-border text-xs space-y-1">
                    <div className="flex justify-between font-sans">
                      <span className="font-semibold text-nature-text">{comparisonProfile.name}:</span>
                      <span className="font-mono text-nature-forest font-semibold">
                        {comparisonProfile.total_capacity_mw.toLocaleString()} MW
                      </span>
                    </div>
                    <div className="flex justify-between text-[11px] text-nature-muted font-mono">
                      <span>Solar: {(comparisonProfile.capacity_breakdown['SOLAR'] || 0).toLocaleString()} MW</span>
                      <span>Wind: {(comparisonProfile.capacity_breakdown['WIND'] || 0).toLocaleString()} MW</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="rounded-lg border border-nature-border bg-white p-6 text-center text-xs text-nature-muted">
              Select a state on the map to inspect its renewable fleet profile.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

