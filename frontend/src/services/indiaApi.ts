import {
  IndiaNationalOverview,
  IndiaMapItem,
  IndiaStateItem,
  IndiaStateProfile,
  IndiaMultiYearTrends,
  IndiaSourceAnalytics,
  IndiaRegionalComparison,
  IndiaForecastingData,
  IndiaWeatherIntelligence,
  IndiaDataQuality,
  IndiaExplorerResponse,
  SourceFileItem,
  NationalReconciliationItem,
  CoverageInventory,
  CapacityAnalyticsResponse,
} from '../types/india';

const getApiBaseUrl = (): string => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '');
  }
  if (import.meta.env.PROD) {
    return 'https://windscope-india-backend.onrender.com';
  }
  return '';
};

const API_BASE = getApiBaseUrl();

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errMsg = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const body = await res.json();
      if (body.detail) {
        errMsg = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
      } else if (body.message) {
        errMsg = body.message;
      }
    } catch {
      // Non-json response
    }
    throw new ApiError(res.status, errMsg);
  }
  return res.json();
}

export const indiaApi = {
  async getHealth(): Promise<{
    status: string;
    service: string;
    timestamp_utc: string;
    platform_jurisdiction: string;
    market_timezone: string;
  }> {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },
  async getOverview(
    year: number = 2026,
    month: number | null = 1,
    datasetType?: 'VERIFIED_OFFICIAL' | 'OFFICIAL_SOURCE_UNVERIFIED' | 'DEMONSTRATION' | 'OFFICIAL'
  ): Promise<IndiaNationalOverview> {
    const params = new URLSearchParams({ year: String(year) });
    if (month !== null) {
      params.append('month', String(month));
    }
    if (datasetType) {
      params.append('dataset_type', datasetType);
    }
    const res = await fetch(`${API_BASE}/api/v1/india/overview?${params.toString()}`);
    return handleResponse<IndiaNationalOverview>(res);
  },

  async getMapData(
    metric: 'generation' | 'capacity' = 'generation',
    source?: string,
    year: number = 2026,
    month: number | null = 1,
    datasetType?: 'VERIFIED_OFFICIAL' | 'OFFICIAL_SOURCE_UNVERIFIED' | 'DEMONSTRATION' | 'OFFICIAL'
  ): Promise<IndiaMapItem[]> {
    const params = new URLSearchParams({ metric, year: String(year) });
    if (source) params.append('source', source);
    if (month !== null) params.append('month', String(month));
    if (datasetType) params.append('dataset_type', datasetType);
    const res = await fetch(`${API_BASE}/api/v1/india/map-data?${params.toString()}`);
    return handleResponse<IndiaMapItem[]>(res);
  },

  async getStates(region?: string, hasWind?: boolean): Promise<IndiaStateItem[]> {
    const params = new URLSearchParams();
    if (region) params.append('region', region);
    if (hasWind !== undefined) params.append('has_wind', String(hasWind));
    const qs = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/api/v1/india/states${qs}`);
    return handleResponse<IndiaStateItem[]>(res);
  },

  async getStateProfile(stateCode: string, startYear: number = 2020, endYear: number = 2026): Promise<IndiaStateProfile> {
    const params = new URLSearchParams({
      start_year: String(startYear),
      end_year: String(endYear),
    });
    const res = await fetch(`${API_BASE}/api/v1/india/states/${stateCode}?${params.toString()}`);
    return handleResponse<IndiaStateProfile>(res);
  },

  async getMultiYearTrends(
    startYear: number = 2020,
    endYear: number = 2026,
    geoCode?: string,
    sourceCode?: string
  ): Promise<IndiaMultiYearTrends> {
    const params = new URLSearchParams({
      start_year: String(startYear),
      end_year: String(endYear),
    });
    if (geoCode) params.append('geo_code', geoCode);
    if (sourceCode) params.append('source_code', sourceCode);
    const res = await fetch(`${API_BASE}/api/v1/india/multi-year?${params.toString()}`);
    return handleResponse<IndiaMultiYearTrends>(res);
  },

  async getSourceAnalytics(sourceCode: string): Promise<IndiaSourceAnalytics> {
    const res = await fetch(`${API_BASE}/api/v1/india/sources/${sourceCode}`);
    return handleResponse<IndiaSourceAnalytics>(res);
  },

  async getRegionalComparison(year: number = 2025): Promise<IndiaRegionalComparison[]> {
    const res = await fetch(`${API_BASE}/api/v1/india/regional?year=${year}`);
    return handleResponse<IndiaRegionalComparison[]>(res);
  },

  async getForecastingData(stateCode: string = 'IN-GJ', dateStr: string = '2026-01-15'): Promise<IndiaForecastingData> {
    const params = new URLSearchParams({
      state_code: stateCode,
      date_str: dateStr,
    });
    const res = await fetch(`${API_BASE}/api/v1/india/forecasting?${params.toString()}`);
    return handleResponse<IndiaForecastingData>(res);
  },

  async getWeatherIntelligence(stateCode: string = 'IN-GJ', year: number = 2025): Promise<IndiaWeatherIntelligence> {
    const params = new URLSearchParams({
      state_code: stateCode,
      year: String(year),
    });
    const res = await fetch(`${API_BASE}/api/v1/india/weather?${params.toString()}`);
    return handleResponse<IndiaWeatherIntelligence>(res);
  },

  async getDataQuality(): Promise<IndiaDataQuality> {
    const res = await fetch(`${API_BASE}/api/v1/india/data-quality`);
    return handleResponse<IndiaDataQuality>(res);
  },

  async getOperationalMetrics(deliveryDate: string = '2024-06-01', region?: string): Promise<any> {
    const params = new URLSearchParams({ delivery_date: deliveryDate });
    if (region) params.append('region', region);
    const res = await fetch(`${API_BASE}/api/v1/india/grid/operational-metrics?${params.toString()}`);
    return handleResponse<any>(res);
  },

  async getSourceFiles(): Promise<SourceFileItem[]> {
    const res = await fetch(`${API_BASE}/api/v1/india/source-files`);
    return handleResponse<SourceFileItem[]>(res);
  },

  async getReconciliations(year?: number, month?: number, sourceCode?: string): Promise<NationalReconciliationItem[]> {
    const params = new URLSearchParams();
    if (year) params.append('year', String(year));
    if (month) params.append('month', String(month));
    if (sourceCode) params.append('source_code', sourceCode);
    const qs = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/api/v1/india/reconciliations${qs}`);
    return handleResponse<NationalReconciliationItem[]>(res);
  },

  async getCoverageInventory(): Promise<CoverageInventory> {
    const res = await fetch(`${API_BASE}/api/v1/india/coverage`);
    return handleResponse<CoverageInventory>(res);
  },

  async getExplorer(
    page: number = 1,
    pageSize: number = 50,
    stateCode?: string,
    sourceCode?: string,
    year?: number,
    datasetClassification?: string
  ): Promise<IndiaExplorerResponse> {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
    });
    if (stateCode) params.append('state_code', stateCode);
    if (sourceCode) params.append('source_code', sourceCode);
    if (year) params.append('year', String(year));
    if (datasetClassification) params.append('dataset_classification', datasetClassification);
    const res = await fetch(`${API_BASE}/api/v1/india/explorer?${params.toString()}`);
    return handleResponse<IndiaExplorerResponse>(res);
  },

  getExportCsvUrl(stateCode?: string, sourceCode?: string, year?: number, datasetClassification?: string): string {
    const params = new URLSearchParams();
    if (stateCode) params.append('state_code', stateCode);
    if (sourceCode) params.append('source_code', sourceCode);
    if (year) params.append('year', String(year));
    if (datasetClassification) params.append('dataset_classification', datasetClassification);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return `${API_BASE}/api/v1/india/export/csv${qs}`;
  },

  async getCapacityAnalytics(effectiveDate: string = '2024-06-30'): Promise<CapacityAnalyticsResponse> {
    const params = new URLSearchParams({ effective_date: effectiveDate });
    const res = await fetch(`${API_BASE}/api/v1/india/capacity?${params.toString()}`);
    return handleResponse<CapacityAnalyticsResponse>(res);
  },
};
