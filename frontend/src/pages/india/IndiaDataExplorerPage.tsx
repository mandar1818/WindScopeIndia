import React, { useEffect, useState } from 'react';
import {
  Database,
  Download,
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  FileSpreadsheet,
} from 'lucide-react';
import { IndiaExplorerResponse, ExplorerRecord } from '../../types/india';
import { indiaApi } from '../../services/indiaApi';
import { Skeleton, CardSkeleton } from '../../components/common/Skeleton';
import { ErrorAlert } from '../../components/common/ErrorAlert';

export const IndiaDataExplorerPage: React.FC = () => {
  const [data, setData] = useState<IndiaExplorerResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(25);
  const [selectedState, setSelectedState] = useState<string>('');
  const [selectedSource, setSelectedSource] = useState<string>('');
  const [selectedYear, setSelectedYear] = useState<string>('');
  const [selectedClassification, setSelectedClassification] = useState<string>('');

  const fetchExplorerData = async () => {
    setLoading(true);
    setError(null);
    try {
      const stateParam = selectedState || undefined;
      const sourceParam = selectedSource || undefined;
      const yearParam = selectedYear ? Number(selectedYear) : undefined;
      const classParam = selectedClassification || undefined;
      const res = await indiaApi.getExplorer(page, pageSize, stateParam, sourceParam, yearParam, classParam);
      setData(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to query tabular data explorer.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExplorerData();
  }, [page, pageSize, selectedState, selectedSource, selectedYear, selectedClassification]);

  const handleFilterChange = (setter: React.Dispatch<React.SetStateAction<string>>) => (e: React.ChangeEvent<HTMLSelectElement>) => {
    setter(e.target.value);
    setPage(1); // Reset to first page
  };

  const csvUrl = indiaApi.getExportCsvUrl(
    selectedState || undefined,
    selectedSource || undefined,
    selectedYear ? Number(selectedYear) : undefined,
    selectedClassification || undefined
  );

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="rounded-lg border border-nature-border bg-white p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-semibold text-nature-text">
              National Renewable Energy Data Explorer &amp; Ledger
            </h1>
            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-nature-forest border border-emerald-200 text-[10px] font-mono font-medium flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-nature-forest" />
              18,213 Model Observations &bull; Demo
            </span>
          </div>
          <p className="text-xs text-nature-muted">
            Granular exploration of monthly state-level generation outturns, target benchmarks, and plant capacity utilization factors (2020–2026).
          </p>
        </div>

        {/* Export CSV Button */}
        <div>
          <a
            href={csvUrl}
            target="_blank"
            rel="noopener noreferrer"
            download
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-nature-forest text-white text-xs font-medium hover:bg-nature-forest-dark transition-colors shadow-xs"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV Dataset</span>
          </a>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="rounded-lg border border-nature-border bg-white p-3.5 shadow-sm flex flex-wrap items-center gap-3 text-xs">
        <div className="flex items-center space-x-1.5">
          <Filter className="w-3.5 h-3.5 text-nature-muted" />
          <span className="font-medium text-nature-muted">Filters:</span>
        </div>

        {/* State Dropdown */}
        <div className="flex items-center space-x-1">
          <select
            value={selectedState}
            onChange={handleFilterChange(setSelectedState)}
            className="px-2.5 py-1 rounded-md border border-nature-border bg-nature-bg text-nature-text text-xs focus:outline-hidden focus:ring-1 focus:ring-nature-forest"
          >
            <option value="">All States &amp; UTs (36)</option>
            <option value="IN-GJ">Gujarat</option>
            <option value="IN-RJ">Rajasthan</option>
            <option value="IN-TN">Tamil Nadu</option>
            <option value="IN-KA">Karnataka</option>
            <option value="IN-MH">Maharashtra</option>
            <option value="IN-AP">Andhra Pradesh</option>
            <option value="IN-MP">Madhya Pradesh</option>
            <option value="IN-HP">Himachal Pradesh</option>
            <option value="IN-UT">Uttarakhand</option>
            <option value="IN-UP">Uttar Pradesh</option>
            <option value="IN-BR">Bihar</option>
            <option value="IN-WB">West Bengal</option>
          </select>
        </div>

        {/* Fuel Dropdown */}
        <div className="flex items-center space-x-1">
          <select
            value={selectedSource}
            onChange={handleFilterChange(setSelectedSource)}
            className="px-2.5 py-1 rounded-md border border-nature-border bg-nature-bg text-nature-text text-xs focus:outline-hidden focus:ring-1 focus:ring-nature-forest"
          >
            <option value="">All Fuel Streams</option>
            <option value="SOLAR">Solar PV</option>
            <option value="WIND">Wind Energy</option>
            <option value="LARGE_HYDRO">Large Hydro (&gt;25MW)</option>
            <option value="SMALL_HYDRO">Small Hydro (&le;25MW)</option>
            <option value="BIOMASS">Biomass &amp; Bagasse</option>
            <option value="OTHER_RE">Other RE (Waste to Energy)</option>
          </select>
        </div>

        {/* Year Dropdown */}
        <div className="flex items-center space-x-1">
          <select
            value={selectedYear}
            onChange={handleFilterChange(setSelectedYear)}
            className="px-2.5 py-1 rounded-md border border-nature-border bg-nature-bg text-nature-text text-xs focus:outline-hidden focus:ring-1 focus:ring-nature-forest"
          >
            <option value="">All Years (2020–2026)</option>
            <option value="2026">2026 (Partial Jan)</option>
            <option value="2025">2025</option>
            <option value="2024">2024</option>
            <option value="2023">2023</option>
            <option value="2022">2022</option>
            <option value="2021">2021</option>
            <option value="2020">2020</option>
          </select>
        </div>

        {/* Dataset Classification Dropdown */}
        <div className="flex items-center space-x-1">
          <select
            value={selectedClassification}
            onChange={handleFilterChange(setSelectedClassification)}
            className="px-2.5 py-1 rounded-md border border-nature-border bg-nature-bg text-nature-text text-xs focus:outline-hidden focus:ring-1 focus:ring-nature-forest font-medium"
          >
            <option value="">All Datasets (Official &amp; Demo)</option>
            <option value="VERIFIED_OFFICIAL">Verified Official Gazette (CEA PDF)</option>
            <option value="OFFICIAL_SOURCE_UNVERIFIED">Unverified Source Model (Awaiting Gazette)</option>
            <option value="DEMONSTRATION">Demonstration Benchmark (2020-2026)</option>
          </select>
        </div>

        <div className="ml-auto text-nature-muted font-mono text-[11px]">
          Showing {data?.records.length || 0} of {data?.total_records.toLocaleString() || 0} rows
        </div>
      </div>

      {/* Main Table */}
      {loading && !data ? (
        <Skeleton className="h-96 w-full" />
      ) : error ? (
        <ErrorAlert title="Data Query Error" message={error} onRetry={fetchExplorerData} />
      ) : (
        <div className="rounded-lg border border-nature-border bg-white shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-nature-bg border-b border-nature-border text-nature-muted font-medium">
                  <th className="py-2.5 px-3">State / UT</th>
                  <th className="py-2.5 px-3">Region</th>
                  <th className="py-2.5 px-3">Energy Stream</th>
                  <th className="py-2.5 px-3">Period</th>
                  <th className="py-2.5 px-3 text-right">Generation (MU)</th>
                  <th className="py-2.5 px-3 text-right">Target (MU)</th>
                  <th className="py-2.5 px-3 text-right">CUF (%)</th>
                  <th className="py-2.5 px-3 text-center">Dataset</th>
                  <th className="py-2.5 px-3 text-center">Observation Status</th>
                  <th className="py-2.5 px-3 text-center">Source Document</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-nature-border font-mono">
                {data?.records.map((r) => (
                  <tr key={r.id} className="hover:bg-nature-bg/60 transition-colors">
                    <td className="py-2.5 px-3 font-sans font-medium text-nature-text">
                      <div className="flex items-center space-x-1.5">
                        <span className="font-mono text-[10px] text-nature-muted">{r.state_code}</span>
                        <span>{r.state_name}</span>
                      </div>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="px-1 py-0.5 rounded text-[10px] bg-nature-bg border border-nature-border">
                        {r.region_code}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-sans">
                      <span
                        className={`text-[11px] font-medium ${
                          r.source_code === 'SOLAR'
                            ? 'text-[#D49A42]'
                            : r.source_code === 'WIND'
                            ? 'text-[#26966B]'
                            : r.source_code.includes('HYDRO')
                            ? 'text-[#5689B5]'
                            : 'text-[#8A5D3B]'
                        }`}
                      >
                        {r.source_code.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-nature-text font-medium">{r.period}</td>
                    <td className="py-2.5 px-3 text-right font-semibold text-nature-text">
                      {r.generation_mu !== null ? r.generation_mu.toFixed(3) : (
                        <span className="text-amber-700 italic">MISSING</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-right text-nature-muted">
                      {r.target_mu !== null && r.target_mu > 0 ? r.target_mu.toFixed(3) : '-'}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      {r.cuf_pct !== null && r.cuf_pct > 0 ? (
                        <span className="text-nature-text">{r.cuf_pct.toFixed(1)}%</span>
                      ) : (
                        <span className="text-nature-muted">0.0%</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      {r.dataset_classification === 'VERIFIED_OFFICIAL' || r.dataset_classification === 'OFFICIAL_REPORTED' ? (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-sans font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
                          VERIFIED
                        </span>
                      ) : r.dataset_classification === 'OFFICIAL_SOURCE_UNVERIFIED' ? (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-sans font-medium bg-blue-50 text-blue-800 border border-blue-200">
                          UNVERIFIED
                        </span>
                      ) : (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-sans bg-amber-50 text-amber-800 border border-amber-200">
                          DEMO
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-nature-bg border border-nature-border text-nature-text">
                        {r.observation_status || 'REPORTED_VALUE'}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-sans bg-emerald-50 text-nature-forest border border-emerald-200">
                        {r.original_filename || r.source_provenance}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          <div className="p-3 border-t border-nature-border bg-[#FAFCF9] flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2">
              <span className="text-nature-muted">Rows per page:</span>
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setPage(1);
                }}
                className="px-2 py-0.5 rounded border border-nature-border bg-white text-xs font-mono"
              >
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-nature-muted font-mono">
                Page {data?.page} of {data?.total_pages || 1}
              </span>
              <div className="flex space-x-1">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="p-1 rounded border border-nature-border bg-white hover:bg-nature-bg disabled:opacity-40 disabled:cursor-not-allowed text-nature-text"
                  title="Previous Page"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  disabled={page >= (data?.total_pages || 1)}
                  onClick={() => setPage((p) => p + 1)}
                  className="p-1 rounded border border-nature-border bg-white hover:bg-nature-bg disabled:opacity-40 disabled:cursor-not-allowed text-nature-text"
                  title="Next Page"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

