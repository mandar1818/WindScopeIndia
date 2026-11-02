import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  AreaChart,
  Area,
} from 'recharts';
import {
  Target,
  Clock,
  ShieldCheck,
  TrendingUp,
  AlertCircle,
  Calendar,
  Zap,
  Activity,
  Layers,
} from 'lucide-react';
import { IndiaForecastingData } from '../../types/india';
import { indiaApi } from '../../services/indiaApi';
import { MetricCard } from '../../components/common/MetricCard';
import { Skeleton, CardSkeleton } from '../../components/common/Skeleton';
import { ErrorAlert } from '../../components/common/ErrorAlert';

export const IndiaForecastingPage: React.FC = () => {
  const [data, setData] = useState<IndiaForecastingData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedState, setSelectedState] = useState<string>('IN-GJ');
  const [selectedDate, setSelectedDate] = useState<string>('2026-01-15');

  const fetchForecast = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await indiaApi.getForecastingData(selectedState, selectedDate);
      setData(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to load intraday 15-minute forecasting data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, [selectedState, selectedDate]);

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
    return <ErrorAlert title="Forecasting Service Error" message={error} onRetry={fetchForecast} />;
  }

  const blocks = data?.blocks || [];

  // Chart data for 96 blocks
  const chartData = blocks.map((b) => ({
    block: `B${b.block_number}`,
    time: b.timestamp.includes('T') ? b.timestamp.split('T')[1].substring(0, 5) : b.timestamp,
    Actual: Math.round(b.actual_mw),
    Scheduled: Math.round(b.scheduled_mw),
    Deviation: Math.round(b.deviation_mw),
  }));

  const totalActualMWh = blocks.reduce((a, b) => a + b.actual_mw * 0.25, 0);
  const totalScheduledMWh = blocks.reduce((a, b) => a + b.scheduled_mw * 0.25, 0);
  const totalImbalanceMWh = blocks.reduce((a, b) => a + b.energy_deviation_mwh, 0);

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-semibold text-nature-text">
              Intraday 15-Minute Forecasting &amp; REMC Accuracy
            </h1>
            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-nature-forest border border-emerald-200 text-[10px] font-mono font-medium flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-nature-forest" />
              Simulated IEGC 96 Time-Blocks &bull; Demo Schedule
            </span>
          </div>
          <p className="text-xs text-nature-muted">
            Demonstration Day-Ahead schedule vs simulated outturn across standard 15-minute operational intervals (CERC IEGC framework).
          </p>
        </div>

        {/* State and Date Selector */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center space-x-1.5 text-xs">
            <span className="text-nature-muted font-medium">REMC State:</span>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="px-2.5 py-1 rounded-md border border-nature-border bg-nature-bg text-nature-text text-xs focus:outline-hidden focus:ring-1 focus:ring-nature-forest"
            >
              <option value="IN-GJ">Gujarat (SLDC Gotri)</option>
              <option value="IN-TN">Tamil Nadu (SLDC Chennai)</option>
              <option value="IN-RJ">Rajasthan (SLDC Heerapura)</option>
              <option value="IN-KA">Karnataka (SLDC Bengaluru)</option>
              <option value="IN-MH">Maharashtra (SLDC Kalwa)</option>
            </select>
          </div>

          <div className="flex items-center space-x-1.5 text-xs">
            <Calendar className="w-3.5 h-3.5 text-nature-muted" />
            <input
              type="date"
              value={selectedDate}
              min="2026-01-01"
              max="2026-01-31"
              onChange={(e) => setSelectedDate(e.target.value)}
              className="px-2 py-1 rounded-md border border-nature-border bg-nature-bg text-nature-text text-xs focus:outline-hidden focus:ring-1 focus:ring-nature-forest font-mono"
            />
          </div>
        </div>
      </div>

      {/* Demonstration Data Disclaimer Banner */}
      <div className="rounded-md border border-amber-200 bg-amber-50/70 p-3 text-xs text-amber-900 flex flex-col md:flex-row md:items-start justify-between gap-3">
        <div className="flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
          <div className="space-y-1">
            <p className="font-semibold text-amber-950">Demonstration Dispatch &amp; Forecast Evaluation Model</p>
            <p className="text-[11px] text-amber-800 leading-relaxed">
              {data?.missing_data_explanation ||
                'The 96 intraday time-blocks and error metrics (MAE, RMSE, WAPE, Signed Bias) are evaluated over baseline demonstration dispatches. Official SLDC/REMC operational SCADA telemetry is NOT ACCESSIBLE IN CURRENT ENVIRONMENT — AUTHORIZATION OR ACCESS REQUIRED.'}
            </p>
          </div>
        </div>

        <div className="border-t md:border-t-0 md:border-l border-amber-200 pt-2 md:pt-0 md:pl-3 space-y-1 text-[11px] font-mono shrink-0">
          <div><span className="text-amber-800 font-semibold">Features:</span> {data?.features_data_source || 'ECMWF ERA5 / Harmonics'}</div>
          <div><span className="text-amber-800 font-semibold">Actuals:</span> DEMONSTRATION ACTUALS (REMC SCADA NOT ACCESSIBLE IN CURRENT ENVIRONMENT)</div>
          <div><span className="text-amber-800 font-semibold">Statutory Cutoff:</span> 12:00 PM (Noon) IST (D-1)</div>
        </div>
      </div>

      {/* Accuracy Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          title="Mean Absolute Error (MAE)"
          value={`${data?.mae_mw ? data.mae_mw.toFixed(1) : '-'} MW`}
          subtitle="Average block forecast error magnitude"
          icon={<Target className="w-4 h-4 text-nature-forest" />}
          trend="neutral"
        />
        <MetricCard
          title="Root Mean Squared Error (RMSE)"
          value={`${data?.rmse_mw ? data.rmse_mw.toFixed(1) : '-'} MW`}
          subtitle="Quadratic penalty on large deviations"
          icon={<Activity className="w-4 h-4 text-nature-forecast" />}
          trend="neutral"
        />
        <MetricCard
          title="Weighted Absolute Error (WAPE)"
          value={`${data?.wape_pct ? data.wape_pct.toFixed(2) : '-'}%`}
          subtitle="Normalized by total actual generation"
          icon={<TrendingUp className="w-4 h-4 text-nature-actual" />}
          trend="positive"
        />
        <MetricCard
          title="Signed Forecast Bias"
          value={`${data?.signed_bias_mw !== undefined ? (data.signed_bias_mw > 0 ? `+${data.signed_bias_mw.toFixed(1)}` : data.signed_bias_mw.toFixed(1)) : '-'} MW`}
          subtitle={`Direction: ${data?.bias_direction || 'Neutral'}`}
          icon={<AlertCircle className="w-4 h-4 text-[#D49A42]" />}
          trend="neutral"
        />
      </div>

      {/* 96-Block Actual vs Scheduled Main Chart */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-nature-border pb-2.5">
          <div>
            <h2 className="text-sm font-semibold text-nature-text">
              Day-Ahead Scheduled vs Actual Generation (96 Time Blocks)
            </h2>
            <p className="text-[11px] text-nature-muted">
              {data?.state_name} &bull; Delivery Date: <span className="font-mono">{data?.delivery_date}</span> &bull; 15-Minute Settlement Granularity
            </p>
          </div>
          <div className="flex items-center space-x-3 text-xs font-mono">
            <span className="text-nature-muted">
              Total Actual: <strong className="text-nature-text">{Math.round(totalActualMWh).toLocaleString()} MWh</strong>
            </span>
            <span className="text-nature-muted">
              Imbalance: <strong className={totalImbalanceMWh >= 0 ? 'text-nature-actual' : 'text-rose-600'}>
                {totalImbalanceMWh >= 0 ? `+${Math.round(totalImbalanceMWh)}` : Math.round(totalImbalanceMWh)} MWh
              </strong>
            </span>
          </div>
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 15, right: 15, left: -10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E1E8DF" vertical={false} />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 10, fill: '#748078' }}
                tickLine={false}
                interval={7}
              />
              <YAxis
                tick={{ fontSize: 11, fill: '#748078' }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => `${v} MW`}
              />
              <Tooltip
                formatter={(value: any, name: any) => [`${Number(value).toLocaleString()} MW`, name]}
                labelFormatter={(label, payload) => {
                  const item = payload[0]?.payload;
                  return item ? `${item.block} (${item.time} IST)` : label;
                }}
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  borderColor: '#E1E8DF',
                  borderRadius: '6px',
                  fontSize: '11px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Line
                type="monotone"
                dataKey="Actual"
                stroke="#26966B"
                strokeWidth={2.5}
                dot={false}
                name="Actual Outturn (MW)"
              />
              <Line
                type="monotone"
                dataKey="Scheduled"
                stroke="#5689B5"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={false}
                name="REMC Day-Ahead Schedule (MW)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Demonstration Data Disclaimer Banner */}
      <div className="rounded-md border border-amber-200 bg-amber-50/70 p-3 text-xs text-amber-900 flex flex-col md:flex-row md:items-start justify-between gap-3">
        <div className="flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
          <div className="space-y-1">
            <p className="font-semibold text-amber-950">Demonstration Dispatch &amp; Forecast Evaluation Model</p>
            <p className="text-[11px] text-amber-800 leading-relaxed">
              {data?.missing_data_explanation ||
                'The 96 intraday time-blocks and error metrics (MAE, RMSE, WAPE, Signed Bias) are evaluated over baseline demonstration dispatches. Official SLDC/REMC operational SCADA telemetry is NOT ACCESSIBLE IN CURRENT ENVIRONMENT — AUTHORIZATION OR ACCESS REQUIRED.'}
            </p>
          </div>
        </div>

        <div className="border-t md:border-t-0 md:border-l border-amber-200 pt-2 md:pt-0 md:pl-3 space-y-1 text-[11px] font-mono shrink-0">
          <div><span className="text-amber-800 font-semibold">Features:</span> {data?.features_data_source || 'ECMWF ERA5 / Harmonics'}</div>
          <div><span className="text-amber-800 font-semibold">Actuals:</span> DEMONSTRATION ACTUALS (REMC SCADA NOT ACCESSIBLE IN CURRENT ENVIRONMENT)</div>
          <div><span className="text-amber-800 font-semibold">Statutory Cutoff:</span> 12:00 PM (Noon) IST (D-1)</div>
        </div>
      </div>

      {/* Deviation Area Chart (Block Deviation) */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm space-y-3">
        <div className="border-b border-nature-border pb-2.5">
          <h3 className="text-sm font-semibold text-nature-text">
            Deviation Spectrum (Actual minus Scheduled)
          </h3>
          <p className="text-[11px] text-nature-muted">
            Positive values denote surplus generation; negative values denote shortfall triggering Deviation Settlement Mechanism (DSM) exposure.
          </p>
        </div>

        <div className="h-48 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 15, left: -10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E1E8DF" vertical={false} />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 10, fill: '#748078' }}
                tickLine={false}
                interval={7}
              />
              <YAxis
                tick={{ fontSize: 11, fill: '#748078' }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => `${v} MW`}
              />
              <Tooltip
                formatter={(value: any) => [`${Number(value).toLocaleString()} MW`, 'Deviation']}
                labelFormatter={(label, payload) => {
                  const item = payload[0]?.payload;
                  return item ? `${item.block} (${item.time} IST)` : label;
                }}
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  borderColor: '#E1E8DF',
                  borderRadius: '6px',
                  fontSize: '11px',
                }}
              />
              <Area
                type="monotone"
                dataKey="Deviation"
                stroke="#D49A42"
                fill="#D49A42"
                fillOpacity={0.2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

