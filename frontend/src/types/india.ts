export type GridRegionCode = 'NR' | 'WR' | 'SR' | 'ER' | 'NER';

export type EnergySourceCode =
  | 'WIND'
  | 'SOLAR'
  | 'LARGE_HYDRO'
  | 'SMALL_HYDRO'
  | 'BIOMASS'
  | 'OTHER_RE';

export interface SourceBreakdownItem {
  source_code: EnergySourceCode;
  display_name: string;
  generation_mu: number;
  capacity_mw: number;
  share_pct: number;
}

export interface TopStateItem {
  code: string;
  name: string;
  region_code: GridRegionCode;
  generation_mu: number;
  share_of_national_pct: number;
}

export interface IndiaNationalOverview {
  evaluation_year: number;
  evaluation_month: number | null;
  dataset_classification?: string;
  is_verified_official?: boolean;
  is_official_reported?: boolean;
  is_official_source_unverified?: boolean;
  total_generation_mu: number;
  total_capacity_gw: number;
  total_capacity_mw: number;
  yoy_growth_pct: number;
  source_breakdown: SourceBreakdownItem[];
  top_states: TopStateItem[];
  timestamp_ist: string;
  statutory_source: string;
}

export interface IndiaMapItem {
  code: string;
  name: string;
  entity_type: 'STATE' | 'UNION_TERRITORY';
  region_code: GridRegionCode;
  geojson_id: string;
  latitude: number;
  longitude: number;
  total_generation_mu: number;
  total_capacity_mw: number;
  solar_mu: number;
  wind_mu: number;
  hydro_mu: number;
  biomass_mu: number;
  other_mu: number;
  solar_capacity_mw: number;
  wind_capacity_mw: number;
  has_wind: boolean;
  value: number;
}

export interface IndiaStateItem {
  code: string;
  name: string;
  entity_type: 'STATE' | 'UNION_TERRITORY';
  region_code: GridRegionCode;
  capital: string;
  latitude: number;
  longitude: number;
  total_capacity_mw: number;
  total_re_capacity_mw?: number;
  wind_capacity_mw: number;
  solar_capacity_mw: number;
  hydro_capacity_mw?: number;
  has_wind: boolean;
  has_commercial_wind?: boolean;
}

export interface MonthlySeriesItem {
  year: number;
  month: number;
  period: string;
  source_code: EnergySourceCode;
  generation_mu: number;
  cuf_pct: number;
}

export interface SeasonalityItem {
  month: number;
  month_name: string;
  avg_wind_mu: number;
  avg_solar_mu: number;
  avg_hydro_mu: number;
}

export interface DailyPointItem {
  date: string;
  source_code: EnergySourceCode;
  generation_mu: number;
  peak_mw: number;
}

export interface IndiaStateProfile {
  code: string;
  name: string;
  entity_type: 'STATE' | 'UNION_TERRITORY';
  region_code: GridRegionCode;
  capital: string;
  latitude: number;
  longitude: number;
  total_capacity_mw: number;
  capacity_breakdown: Record<string, number>;
  has_wind: boolean;
  monthly_series: MonthlySeriesItem[];
  seasonality: SeasonalityItem[];
  daily_january_2026: DailyPointItem[];
  statutory_source: string;
}

export interface TimelineItem {
  year: number;
  is_partial: boolean;
  total_generation_mu: number;
  solar_mu: number;
  wind_mu: number;
  large_hydro_mu: number;
  small_hydro_mu: number;
  biomass_mu: number;
  other_mu: number;
  yoy_growth_pct: number;
}

export interface IndiaMultiYearTrends {
  start_year: number;
  end_year: number;
  geo_code: string;
  source_code: string;
  timeline: TimelineItem[];
  cagr_pct: number;
}

export interface StateLeaderItem {
  rank: number;
  code: string;
  name: string;
  region_code: GridRegionCode;
  generation_mu: number;
  capacity_mw: number;
  share_pct: number;
}

export interface SourceSeasonalityItem {
  month: number;
  month_name: string;
  generation_mu: number;
  average_cuf_pct: number;
}

export interface IndiaSourceAnalytics {
  source_code: EnergySourceCode;
  display_name: string;
  unit: string;
  annual_generation_2025_mu: number;
  state_leaderboard: StateLeaderItem[];
  seasonality_curve: SourceSeasonalityItem[];
}

export interface IndiaRegionalComparison {
  region_code: GridRegionCode;
  name: string;
  headquarters: string;
  total_generation_mu: number;
  total_capacity_mw: number;
  wind_mu: number;
  solar_mu: number;
  hydro_mu: number;
  wind_share_pct: number;
  solar_share_pct: number;
  hydro_share_pct: number;
}

export interface ForecastingBlockItem {
  block_number: number;
  timestamp: string;
  actual_mw: number;
  scheduled_mw: number;
  deviation_mw: number;
  is_overforecast: boolean;
  energy_deviation_mwh: number;
}

export interface IndiaForecastingData {
  state_code: string;
  state_name: string;
  delivery_date: string;
  time_block_count: number;
  mae_mw: number;
  rmse_mw: number;
  wape_pct: number;
  signed_bias_mw: number;
  bias_direction: string;
  dataset_classification?: string;
  features_data_source?: string;
  actuals_data_source?: string;
  missing_data_explanation?: string;
  evaluation_notice?: string;
  blocks: ForecastingBlockItem[];
}

export interface WeatherObservationPoint {
  time: string;
  wind_speed_10m_ms?: number | null;
  wind_speed_100m_ms?: number | null;
  wind_direction_deg?: number | null;
  solar_ghi_wm2?: number | null;
  solar_dni_wm2?: number | null;
  temperature_c?: number | null;
  cloud_cover_pct?: number | null;
  precipitation_mm?: number | null;
  type?: string;
}

export interface IndiaWeatherIntelligence {
  state_code: string;
  year: number;
  correlation_status?: string;
  correlation_status_description?: string;
  hub_height_wind_correlation: number | null;
  solar_ghi_correlation: number | null;
  matched_sample_size_n?: number;
  wind_sample_size_n?: number;
  solar_sample_size_n?: number;
  weather_observations_count?: number;
  sample_size_n?: number;
  correlation_disclaimer?: string;
  monsoon_intensity_index: string;
  average_wind_speed_100m_ms: number;
  average_solar_ghi_wm2: number;
  seasonal_summary: string;
  dataset_classification?: string;
  is_official_observation?: boolean;
  data_provenance?: string;
  provider_metadata?: {
    provider: string;
    model?: string;
    spatial_resolution?: string;
    elevation_model?: string;
    units?: Record<string, string>;
    disclaimer?: string;
  };
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  series?: WeatherObservationPoint[];
  disclaimer?: string;
}

export interface ReportingMatrixItem {
  code: string;
  name: string;
  entity_type: 'STATE' | 'UNION_TERRITORY';
  region_code: GridRegionCode;
  available_months: number;
  expected_months: number;
  completeness_pct: number;
  has_wind_capacity: boolean;
  wind_capacity_mw: number;
  reporting_status: string;
}

export interface IngestionAuditLogItem {
  dataset_name: string;
  status: string;
  records_processed: number;
  execution_seconds: number;
  timestamp: string;
}

export interface SourceFileItem {
  id: number;
  filename: string;
  source_org: string;
  dataset_title: string;
  document_format?: string;
  publication_date?: string;
  source_url: string;
  reporting_year: number;
  reporting_month: number | null;
  file_hash_sha256: string;
  file_size_bytes: number;
  records_extracted: number;
  ingestion_status: string;
  parser_version?: string;
  download_timestamp: string | null;
}

export interface NationalReconciliationItem {
  id: number;
  source_file_id: number;
  source_file_name: string;
  reporting_year: number;
  reporting_month: number;
  period: string;
  source_code: string;
  published_national_total_mu: number;
  state_sum_mu: number | null;
  absolute_variance_mu: number | null;
  percentage_variance: number | null;
  included_states_count: number;
  missing_states_count: number;
  excluded_records_count: number;
  reconciliation_status: string;
  mathematical_reconciliation?: string;
  source_verification_status?: string;
  geographic_coverage?: string;
  fuel_mapping_validity?: string;
  unit_compatibility?: string;
  explanation?: string;
  created_at: string;
}

export interface CoveragePeriodItem {
  year: number;
  month: number;
  period_label: string;
  coverage_status: string;
  verified_records_count: number;
  unverified_records_count: number;
  demonstration_records_count: number;
  source_files: Array<{
    id: number;
    filename: string;
    format: string;
    source_org: string;
    status: string;
    sha256: string;
  }>;
  reconciliation_summary: string;
}

export interface CoverageInventory {
  summary: {
    verified_official_periods: number;
    unverified_source_periods: number;
    demonstration_only_periods: number;
    total_verified_records: number;
    total_unverified_records: number;
    total_demonstration_records: number;
  };
  inventory: CoveragePeriodItem[];
}

export interface IndiaDataQuality {
  total_geographies: number;
  verified_geographies: number;
  official_records_count?: number;
  unverified_source_count?: number;
  verified_official_count?: number;
  demonstration_records_count?: number;
  total_records_count?: number;
  reconciliations_count?: number;
  matched_reconciliations_count?: number;
  source_files_count?: number;
  source_files?: SourceFileItem[];
  reporting_matrix: ReportingMatrixItem[];
  latest_ingestion_logs: IngestionAuditLogItem[];
}

export interface ExplorerRecord {
  id: number;
  state_code: string;
  state_name: string;
  region_code: GridRegionCode;
  source_code: EnergySourceCode;
  year: number;
  month: number;
  period: string;
  generation_mu: number | null;
  target_mu: number | null;
  cuf_pct: number | null;
  dataset_classification?: string;
  source_org?: string;
  dataset_name?: string;
  original_filename?: string;
  sha256_checksum?: string;
  publication_date?: string;
  original_state_label?: string;
  normalized_geography_code?: string;
  original_fuel_label?: string;
  original_reported_value?: string;
  original_unit?: string;
  normalized_unit?: string;
  pdf_page_number?: number;
  table_heading?: string;
  parser_version?: string;
  validation_status?: string;
  observation_status?: string;
  source_provenance: string;
}

export interface IndiaExplorerResponse {
  page: number;
  page_size: number;
  total_records: number;
  total_pages: number;
  records: ExplorerRecord[];
}

export interface CapacitySummaryGW {
  solar_gw: number;
  wind_gw: number;
  large_hydro_gw: number;
  small_hydro_gw: number;
  biomass_gw: number;
  total_res_gw: number;
  clean_re_gw: number;
  nuclear_gw: number;
  total_non_fossil_gw: number;
  thermal_gw: number;
  grand_total_gw: number;
}

export interface Target500GWTracker {
  target_year: number;
  target_capacity_gw: number;
  target_scope: string;
  statutory_basis: string;
  current_achieved_gw: number;
  progress_percentage: number;
  remaining_capacity_gw: number;
  required_annual_addition_gw: number;
  clean_re_share_of_total_pct: number;
  non_fossil_share_of_total_pct: number;
}

export interface HistoricalCapacityTrajectoryItem {
  effective_date: string;
  solar_gw: number;
  wind_gw: number;
  large_hydro_gw: number;
  small_hydro_gw: number;
  biomass_gw: number;
  total_res_gw: number;
  clean_re_gw: number;
  nuclear_gw: number;
  thermal_gw: number;
}

export interface CapacityAnalyticsResponse {
  effective_date: string;
  is_verified_official: boolean;
  dataset_classification: string;
  statutory_source: string;
  source_provenance: string;
  summary_gw: CapacitySummaryGW;
  summary_mw: Record<string, number>;
  target_500gw_tracker: Target500GWTracker;
  historical_trajectory: HistoricalCapacityTrajectoryItem[];
  disclaimer: string;
}


