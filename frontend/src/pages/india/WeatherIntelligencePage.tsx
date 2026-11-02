import React, { useEffect, useState } from 'react';
import {
  CloudSun,
  Wind,
  Sun,
  Droplets,
  Compass,
  ShieldCheck,
  TrendingUp,
  Activity,
  Layers,
  Calendar,
  Thermometer,
  AlertTriangle,
  MapPin,
  Clock,
  Database,
  Info,
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { IndiaWeatherIntelligence } from '../../types/india';
import { indiaApi } from '../../services/indiaApi';
import { MetricCard } from '../../components/common/MetricCard';
import { Skeleton, CardSkeleton } from '../../components/common/Skeleton';
import { ErrorAlert } from '../../components/common/ErrorAlert';

export const WeatherIntelligencePage: React.FC = () => {
  const [data, setData] = useState<IndiaWeatherIntelligence | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedState, setSelectedState] = useState<string>('IN-GJ');
  const [selectedYear, setSelectedYear] = useState<number>(2024);

  const fetchWeather = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await indiaApi.getWeatherIntelligence(selectedState, selectedYear);
      setData(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to load meteorological intelligence.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeather();
  }, [selectedState, selectedYear]);

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
    return <ErrorAlert title="Meteorological Ingestion Error" message={error} onRetry={fetchWeather} />;
  }

  const isVerified = data?.is_official_observation === true;
  const series = data?.series || [];

  // Prepare chart series (24 or 168 hourly points)
  const chartData = series.map((s, idx) => {
    const timeLabel = s.time.includes('T') ? s.time.split('T')[1].substring(0, 5) : `H${idx + 1}`;
    return {
      time: timeLabel,
      wind_100m: s.wind_speed_100m_ms !== null && s.wind_speed_100m_ms !== undefined ? Number(s.wind_speed_100m_ms) : null,
      wind_10m: s.wind_speed_10m_ms !== null && s.wind_speed_10m_ms !== undefined ? Number(s.wind_speed_10m_ms) : null,
      solar_ghi: s.solar_ghi_wm2 !== null && s.solar_ghi_wm2 !== undefined ? Number(s.solar_ghi_wm2) : null,
      temp_c: s.temperature_c !== null && s.temperature_c !== undefined ? Number(s.temperature_c) : null,
      type: s.type || 'OBSERVATION',
    };
  });

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-semibold text-nature-text">
              Renewable Meteorological &amp; Weather Intelligence
            </h1>
            {isVerified ? (
              <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300 text-[10px] font-mono font-medium flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-emerald-600" />
                ECMWF ERA5 Reanalysis &bull; Verified
              </span>
            ) : (
              <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-300 text-[10px] font-mono font-medium flex items-center gap-1">
                <AlertTriangle className="w-3 h-3 text-amber-600" />
                Demonstration Simulation &bull; Synthetic
              </span>
            )}
          </div>
          <p className="text-xs text-nature-muted">
            State-level meteorological telemetry: 100m hub-height boundary layer wind speeds, Global Horizontal Irradiance (GHI), Direct Normal Irradiance (DNI), and surface temperatures.
          </p>
        </div>

        {/* State and Year Filter */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center space-x-1.5 text-xs">
            <span className="text-nature-muted font-medium">State:</span>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="px-2.5 py-1 rounded-md border border-nature-border bg-nature-bg text-nature-text text-xs focus:outline-hidden focus:ring-1 focus:ring-nature-forest"
            >
              <option value="IN-GJ">Gujarat (Kutch / Saurashtra)</option>
              <option value="IN-TN">Tamil Nadu (Muppandal)</option>
              <option value="IN-RJ">Rajasthan (Thar Desert)</option>
              <option value="IN-KA">Karnataka (Pavagada / Chitradurga)</option>
              <option value="IN-MH">Maharashtra (Western Ghats)</option>
              <option value="IN-AP">Andhra Pradesh (Rayalaseema)</option>
              <option value="IN-MP">Madhya Pradesh (Malwa)</option>
              <option value="IN-UP">Uttar Pradesh</option>
            </select>
          </div>

          <div className="flex items-center space-x-1.5 text-xs">
            <Calendar className="w-3.5 h-3.5 text-nature-muted" />
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="px-2 py-1 rounded-md border border-nature-border bg-nature-bg text-nature-text text-xs focus:outline-hidden focus:ring-1 focus:ring-nature-forest font-mono"
            >
              <option value={2024}>2024 (Verified Ingested Period)</option>
              <option value={2025}>2025</option>
              <option value={2026}>2026</option>
            </select>
          </div>
        </div>
      </div>

      {/* Provenance & Metadata Card */}
      <div className={`rounded-md border p-3 text-xs flex flex-col md:flex-row md:items-center justify-between gap-3 ${
        isVerified ? 'border-emerald-200 bg-emerald-50/60 text-emerald-950' : 'border-amber-200 bg-amber-50/70 text-amber-950'
      }`}>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Database className={`w-4 h-4 ${isVerified ? 'text-emerald-700' : 'text-amber-700'}`} />
            <span className="font-semibold text-xs">
              {isVerified ? 'Official Meteorological Archive (Open-Meteo / ECMWF ERA5)' : 'Demonstration Fallback Simulation (Diurnal Harmonics)'}
            </span>
          </div>
          <p className="text-[11px] leading-relaxed opacity-90">
            {isVerified
              ? 'Atmospheric observations retrieved from Copernicus ECMWF ERA5 Reanalysis archive via Open-Meteo API. Historical observations stored at 0.1° spatial resolution for state centroid.'
              : 'Warning: No stored historical automated weather station records exist for this state and year. A mathematical diurnal simulation calibrated to coordinates is displayed.'}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-[11px] font-mono shrink-0">
          {data?.coordinates && (
            <div className="flex items-center gap-1">
              <MapPin className="w-3 h-3 text-nature-muted" />
              <span>{data.coordinates.latitude.toFixed(2)}°N, {data.coordinates.longitude.toFixed(2)}°E</span>
            </div>
          )}
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3 text-nature-muted" />
            <span>Reporting: {series.length} Hourly Points</span>
          </div>
          <div className="flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-nature-muted" />
            <span>Status: {data?.dataset_classification || 'UNVERIFIED'}</span>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          title="Average Hub Wind Speed"
          value={`${data?.average_wind_speed_100m_ms ? data.average_wind_speed_100m_ms.toFixed(1) : '-'} m/s`}
          subtitle="At 100m turbine hub height"
          icon={<Wind className="w-4 h-4 text-[#26966B]" />}
          trend="neutral"
        />
        <MetricCard
          title="Peak Solar GHI"
          value={`${data?.average_solar_ghi_wm2 ? Math.round(data.average_solar_ghi_wm2) : '-'} W/m²`}
          subtitle="Global Horizontal Irradiance"
          icon={<Sun className="w-4 h-4 text-[#D49A42]" />}
          trend="neutral"
        />
        <MetricCard
          title="Wind Correlation (r)"
          value={data?.hub_height_wind_correlation != null ? data.hub_height_wind_correlation.toFixed(2) : 'N/A'}
          subtitle={data?.matched_sample_size_n != null && data.matched_sample_size_n > 0 ? `Hub speed vs gen (N=${data.matched_sample_size_n})` : 'Insufficient matched data (N=0)'}
          icon={<TrendingUp className="w-4 h-4 text-nature-actual" />}
          trend="neutral"
        />
        <MetricCard
          title="Solar Correlation (r)"
          value={data?.solar_ghi_correlation != null ? data.solar_ghi_correlation.toFixed(2) : 'N/A'}
          subtitle={data?.matched_sample_size_n != null && data.matched_sample_size_n > 0 ? `GHI vs PV outturn (N=${data.matched_sample_size_n})` : 'Insufficient matched data (N=0)'}
          icon={<Activity className="w-4 h-4 text-nature-forecast" />}
          trend="neutral"
        />
      </div>

      {/* Correlation Data Status Alert if Insufficient Data */}
      {data?.correlation_status === 'INSUFFICIENT_DATA' && (
        <div className="rounded-md border border-sky-200 bg-sky-50/70 p-2.5 text-xs text-sky-900 flex items-start gap-2">
          <Info className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />
          <p className="text-[11px] leading-relaxed">
            <strong className="font-semibold">Correlation Data Status:</strong> {data.correlation_status_description || 'Insufficient verified official generation observations matched with meteorological observations for this jurisdiction. Demonstration generation is excluded from verified analytics.'}
          </p>
        </div>
      )}

      {/* Scientific Causation Disclaimer */}
      <div className="rounded-md border border-amber-200 bg-amber-50/70 p-2.5 text-xs text-amber-900 flex items-start gap-2">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <p className="text-[11px] leading-relaxed">
          <strong className="font-semibold">Methodological Notice:</strong> Correlation is not causation. Statistical correlation (<span className="font-mono">r</span>) measures linear co-movement between atmospheric parameters and generation outturn, but does not imply direct physical causality. Realized grid injection is modulated by regional curtailment orders, transmission bottlenecks, scheduled inverter/turbine outages, and auxiliary consumption.
        </p>
      </div>

      {/* Hourly Meteorological Profile Chart */}
      {chartData.length > 0 && (
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-nature-border pb-2.5">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-nature-forest" />
              <h3 className="text-sm font-semibold text-nature-text">
                Diurnal Atmospheric Profile ({isVerified ? 'ECMWF ERA5 Observations' : 'Simulated Diurnal Harmonics'})
              </h3>
            </div>
            <span className="text-[11px] text-nature-muted font-mono">
              Primary Axis: Wind Speed (m/s) &bull; Secondary Axis: Solar GHI (W/m²)
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#666' }} />
                <YAxis yAxisId="left" tick={{ fontSize: 10, fill: '#26966B' }} unit=" m/s" domain={[0, 'auto']} />
                <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: '#D49A42' }} unit=" W/m²" domain={[0, 'auto']} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#fff', borderColor: '#e2e8f0', fontSize: '11px', borderRadius: '6px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Area
                  yAxisId="right"
                  type="monotone"
                  dataKey="solar_ghi"
                  name="Solar GHI (W/m²)"
                  fill="#FDF6EC"
                  stroke="#D49A42"
                  strokeWidth={2}
                />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="wind_100m"
                  name="Wind Speed @ 100m (m/s)"
                  stroke="#26966B"
                  strokeWidth={2.5}
                  dot={false}
                />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="wind_10m"
                  name="Wind Speed @ 10m (m/s)"
                  stroke="#5689B5"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  dot={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Weather Dynamics Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Monsoon Intensity Index Card */}
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 border-b border-nature-border pb-2.5">
            <Droplets className="w-4 h-4 text-[#5689B5]" />
            <h3 className="text-sm font-semibold text-nature-text">Monsoon Dynamics</h3>
          </div>

          <div className="p-3 rounded bg-nature-bg border border-nature-border space-y-1">
            <span className="text-[10px] uppercase font-semibold text-nature-muted tracking-wider">
              Monsoon Classification
            </span>
            <p className="text-sm font-bold text-nature-forest">
              {data?.monsoon_intensity_index || 'Normal South-West Monsoon Regime'}
            </p>
          </div>

          <p className="text-xs text-nature-muted leading-relaxed">
            The South-West monsoon acts as a reciprocal regulator: it accelerates onshore turbine generation across western and southern corridors while depressing solar PV generation via dense cumulonimbus cloud covers and rainfall attenuation.
          </p>
        </div>

        {/* Boundary Layer Wind Profile */}
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 border-b border-nature-border pb-2.5">
            <Compass className="w-4 h-4 text-[#26966B]" />
            <h3 className="text-sm font-semibold text-nature-text">Boundary Layer &amp; Wind Shear</h3>
          </div>

          <div className="space-y-2 text-xs text-nature-text">
            <div className="flex justify-between py-1 border-b border-nature-border/60">
              <span className="text-nature-muted">Hub Height Standard</span>
              <span className="font-mono font-medium">100m – 120m AGL</span>
            </div>
            <div className="flex justify-between py-1 border-b border-nature-border/60">
              <span className="text-nature-muted">Wind Shear Exponent (α)</span>
              <span className="font-mono font-medium">0.14 – 0.22</span>
            </div>
            <div className="flex justify-between py-1 border-b border-nature-border/60">
              <span className="text-nature-muted">Weibull Shape Factor (k)</span>
              <span className="font-mono font-medium">2.1 – 2.4</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-nature-muted">Prevailing Direction</span>
              <span className="font-mono font-medium">SW (215°–245°)</span>
            </div>
          </div>
        </div>

        {/* Solar Radiation Spectrum */}
        <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 border-b border-nature-border pb-2.5">
            <Thermometer className="w-4 h-4 text-[#D49A42]" />
            <h3 className="text-sm font-semibold text-nature-text">Solar Irradiance Profile</h3>
          </div>

          <div className="space-y-2 text-xs text-nature-text">
            <div className="flex justify-between py-1 border-b border-nature-border/60">
              <span className="text-nature-muted">Annual DHI Average</span>
              <span className="font-mono font-medium">650 – 750 kWh/m²</span>
            </div>
            <div className="flex justify-between py-1 border-b border-nature-border/60">
              <span className="text-nature-muted">Direct Normal Irradiance (DNI)</span>
              <span className="font-mono font-medium">1,850 – 2,100 kWh/m²</span>
            </div>
            <div className="flex justify-between py-1 border-b border-nature-border/60">
              <span className="text-nature-muted">Summer Temperature Derating</span>
              <span className="font-mono font-medium">-0.35% / °C &gt; 25°C</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-nature-muted">Peak Insolation Window</span>
              <span className="font-mono font-medium">11:00 – 14:00 IST</span>
            </div>
          </div>
        </div>
      </div>

      {/* Seasonal Synthesis Callout */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-2">
        <h4 className="text-xs font-semibold text-nature-text flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5 text-nature-forest" />
          Regional Meteorological Summary
        </h4>
        <p className="text-xs text-nature-muted leading-relaxed">
          {data?.seasonal_summary ||
            'Strong South-West monsoon winds prevail from June through September with peak wind speeds exceeding 8.5 m/s, yielding maximum wind CUF. Solar irradiance reaches annual maximum in March-April (~220 W/m² GHI average) prior to onset of summer dust and monsoon cloud coverage.'}
        </p>
      </div>
    </div>
  );
};
