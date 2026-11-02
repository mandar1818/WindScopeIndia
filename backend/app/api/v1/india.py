"""
WindScope India — API v1 Router
Provides all REST endpoints for India Overview, Interactive Map, State & UT Explorer,
Multi-Year Trends, Source-Specific Analytics, Forecasting, Regional Comparison, and Data Quality.
"""
import io
import csv
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, Header, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.services.india_analytics_service import IndiaAnalyticsService
from app.services.coverage_service import CoverageService
from app.services.weather_service import WeatherService
from app.services.forecasting_engine import ForecastingEngine, ModelRegistry
from app.services.grid_india_service import GridIndiaService
from app.services.ingestion.scheduler import IngestionScheduler
from app.services.india_market_rules import INDIA_MARKET_RULES, IndiaMarketProduct

router = APIRouter(prefix="/india", tags=["WindScope India"])


@router.get("/overview", summary="National Renewable Energy Overview")
def get_national_overview(
    year: int = Query(2026, description="Target evaluation year (2020-2026)"),
    month: Optional[int] = Query(1, description="Calendar month (1-12) or null for full year"),
    dataset_type: Optional[str] = Query(None, description="'OFFICIAL', 'DEMONSTRATION', or null for auto-select"),
    db: Session = Depends(get_db)
):
    service = IndiaAnalyticsService(db)
    return service.get_national_overview(year=year, month=month, dataset_type=dataset_type)


@router.get("/map-data", summary="Interactive India Choropleth Map Data")
def get_map_data(
    metric: str = Query("generation", description="'generation' (MU) or 'capacity' (MW)"),
    source: Optional[str] = Query(None, description="'WIND', 'SOLAR', 'LARGE_HYDRO', etc."),
    year: int = Query(2026, description="Target year"),
    month: Optional[int] = Query(1, description="Target month or null for annual"),
    dataset_type: Optional[str] = Query(None, description="'OFFICIAL', 'DEMONSTRATION', or null for auto-select"),
    db: Session = Depends(get_db)
):
    service = IndiaAnalyticsService(db)
    return service.get_map_data(metric=metric, source=source, year=year, month=month, dataset_type=dataset_type)


@router.get("/states", summary="List All 28 States & 8 Union Territories")
def list_states(
    region: Optional[str] = Query(None, description="Grid region code: 'NR', 'WR', 'SR', 'ER', 'NER'"),
    has_wind: Optional[bool] = Query(None, description="Filter states with active wind generation"),
    db: Session = Depends(get_db)
):
    service = IndiaAnalyticsService(db)
    return service.get_all_states(region=region, has_wind=has_wind)


@router.get("/states/{state_code}", summary="Detailed State & UT Profile")
def get_state_profile(
    state_code: str,
    start_year: int = Query(2020, description="Start year"),
    end_year: int = Query(2026, description="End year"),
    db: Session = Depends(get_db)
):
    service = IndiaAnalyticsService(db)
    profile = service.get_state_profile(state_code=state_code, start_year=start_year, end_year=end_year)
    if not profile:
        raise HTTPException(status_code=404, detail=f"State with code '{state_code}' not found")
    return profile


@router.get("/trends", include_in_schema=False)
@router.get("/multi-year", summary="Multi-Year Generation Trends & YoY Growth (2020-2026)")
def get_multi_year_trends(
    start_year: int = Query(2020, description="Start year"),
    end_year: int = Query(2026, description="End year"),
    geo_code: Optional[str] = Query(None, description="State/UT code or null for All-India"),
    source_code: Optional[str] = Query(None, description="Energy source code or null for all sources"),
    db: Session = Depends(get_db)
):
    service = IndiaAnalyticsService(db)
    return service.get_multi_year_trends(
        start_year=start_year,
        end_year=end_year,
        geo_code=geo_code,
        source_code=source_code
    )


@router.get("/sources/{source_code}", summary="Source-Specific Deep Dive (Wind, Solar, Hydro)")
def get_source_analytics(
    source_code: str,
    db: Session = Depends(get_db)
):
    service = IndiaAnalyticsService(db)
    return service.get_source_analytics(source_code=source_code.upper())


@router.get("/regional", summary="Regional Comparison (5 Electrical Grid Councils)")
def get_regional_comparison(
    year: int = Query(2025, description="Evaluation year"),
    db: Session = Depends(get_db)
):
    service = IndiaAnalyticsService(db)
    return service.get_regional_comparison(year=year)


@router.get("/capacity", summary="Installed Capacity Benchmarks, Growth & 2030 Target Tracker")
def get_capacity_analytics(
    effective_date: Optional[str] = Query(None, description="Effective date for capacity gazette (YYYY-MM-DD) or null for latest verified"),
    db: Session = Depends(get_db)
):
    service = IndiaAnalyticsService(db)
    return service.get_capacity_analytics(target_date_str=effective_date)


@router.get("/forecasting", summary="15-Minute Intraday Schedules & Accuracy Metrics")
def get_forecasting_data(
    state_code: str = Query("IN-GJ", description="State code with active REMC scheduling"),
    date_str: str = Query("2026-01-15", description="Evaluation date (YYYY-MM-DD)"),
    model_name: str = Query("GRADIENT_BOOSTING_TS", description="Model name from registry"),
    source_code: str = Query("SOLAR", description="Energy source code (SOLAR or WIND)"),
    db: Session = Depends(get_db)
):
    engine = ForecastingEngine(db)
    return engine.generate_day_ahead_forecast(
        state_code=state_code,
        source_code=source_code,
        model_name=model_name,
        target_date=date_str
    )


@router.get("/market-rules", summary="Statutory Indian Power Market Timelines & Gate Closures")
def get_india_market_rules():
    """
    Returns statutory market product timelines and gate closure rules governed under
    CERC (Power Market) Regulations 2021, CERC (IEGC) 2023, and Power Exchange operating rules.
    """
    return {
        "jurisdiction": "Central Electricity Regulatory Commission (CERC)",
        "grid_operator": "Grid Controller of India Limited (NLDC / RLDCs)",
        "market_timezone": "Asia/Kolkata (IST)",
        "products": INDIA_MARKET_RULES
    }


@router.get("/weather", summary="Atmospheric Observations & Correlations")
def get_weather_intelligence(
    state_code: str = Query("IN-GJ", description="State code"),
    year: int = Query(2024, description="Year"),
    db: Session = Depends(get_db)
):
    service = WeatherService(db)
    res = service.get_state_weather(state_code=state_code, year=year)
    corr = service.compute_weather_generation_correlation(state_code=state_code, year=year)

    return {
        "state_code": state_code,
        "year": year,
        "correlation_status": corr["status"],
        "correlation_status_description": corr["status_description"],
        "hub_height_wind_correlation": corr["hub_height_wind_correlation"],
        "solar_ghi_correlation": corr["solar_ghi_correlation"],
        "matched_sample_size_n": corr["matched_sample_size_n"],
        "wind_sample_size_n": corr["wind_sample_size_n"],
        "solar_sample_size_n": corr["solar_sample_size_n"],
        "weather_observations_count": len(res["series"]),
        "correlation_disclaimer": "Statistical correlation indicates co-movement but does not establish physical causality. Auxiliary consumption, transmission bottlenecks, scheduled outages, and dynamic grid curtailment influence realized generation outturn.",
        "monsoon_intensity_index": "STRONG_SOUTHWEST",
        "average_wind_speed_100m_ms": res["summary_metrics"]["average_wind_speed_100m_ms"],
        "average_solar_ghi_wm2": res["summary_metrics"]["peak_solar_ghi_wm2"],
        "seasonal_summary": "Simulated climatological baseline: Peak wind speeds observed June-August (8.5-12.0 m/s); peak solar irradiance March-May (650-780 W/m²)." if res["is_demonstration"] else "Verified ECMWF ERA5 reanalysis: High-resolution surface and boundary layer observations.",
        "dataset_classification": res["source_classification"],
        "is_official_observation": res["source_classification"] == "VERIFIED_METEOROLOGICAL_ARCHIVE",
        "data_provenance": res["provider_metadata"]["provider"],
        "provider_metadata": res["provider_metadata"],
        "coordinates": res["coordinates"],
        "series": res["series"],
        "disclaimer": res["provider_metadata"]["disclaimer"]
    }


@router.get("/weather/rez-parks", summary="Renewable Energy Zone (REZ) Park Coordinates & Catalog")
def get_rez_parks_catalog():
    """
    Returns high-precision geographical coordinates, installed capacities, and technology
    classifications for major Indian Renewable Energy Zone (REZ) parks (Bhadla, Khavda, Pavagada, Muppandal, etc.).
    """
    return WeatherService.get_rez_parks()


@router.get("/grid/status", summary="Grid Controller of India Operational & Telemetry Status")
def get_grid_operational_status(db: Session = Depends(get_db)):
    service = GridIndiaService(db)
    return service.get_grid_operational_summary()


@router.get("/grid/operational-metrics", summary="Daily Operational Demand & RE Penetration Metrics")
def get_grid_operational_metrics(
    delivery_date: Optional[str] = Query(None, description="Delivery date (YYYY-MM-DD)"),
    region: Optional[str] = Query(None, description="Region code: NR, WR, SR, ER, NER, TOTAL"),
    db: Session = Depends(get_db)
):
    from datetime import date
    parsed_date = date.fromisoformat(delivery_date) if delivery_date else None
    service = GridIndiaService(db)
    return service.get_daily_operational_metrics(delivery_date=parsed_date, region_code=region)


@router.get("/ingestion/freshness", summary="Statutory Source Data Freshness & Lag Metrics")
def get_ingestion_freshness(db: Session = Depends(get_db)):
    scheduler = IngestionScheduler(db)
    return scheduler.get_source_freshness()


class TriggerIngestionRequest(BaseModel):
    source_key: str = Field(..., description="Source authority: CEA, NPP, MNRE, GRID_INDIA")
    file_path: str = Field(..., description="Path to source file on disk")
    reporting_year: int
    reporting_month: Optional[int] = None


@router.post("/ingestion/trigger", summary="Trigger Automated Document Ingestion Job")
def trigger_ingestion_job(
    payload: TriggerIngestionRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-KEY"),
    db: Session = Depends(get_db)
):
    if not x_api_key or x_api_key != settings.INGESTION_ADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing X-API-KEY header."
        )
    scheduler = IngestionScheduler(db)
    target_path = Path(payload.file_path)
    return scheduler.run_manual_ingestion(
        source_key=payload.source_key,
        file_path=target_path,
        reporting_year=payload.reporting_year,
        reporting_month=payload.reporting_month
    )


@router.get("/source-files", summary="List Ingested Official Source Files")
def get_source_files(db: Session = Depends(get_db)):
    service = IndiaAnalyticsService(db)
    return service.get_source_files()


@router.get("/reconciliations", summary="National Sum Reconciliation Audits")
def get_reconciliations(
    year: Optional[int] = Query(None, description="Filter by reporting year"),
    month: Optional[int] = Query(None, description="Filter by reporting month"),
    source_code: Optional[str] = Query(None, description="Filter by fuel source code"),
    db: Session = Depends(get_db)
):
    service = IndiaAnalyticsService(db)
    return service.get_reconciliations(year=year, month=month, source_code=source_code)


@router.get("/coverage", summary="Historical Multi-Year Data Coverage Inventory (2020-2026)")
def get_coverage_inventory(db: Session = Depends(get_db)):
    service = CoverageService(db)
    return service.get_coverage_inventory()


@router.get("/data-quality", summary="Data Quality, Provenance & Completeness Matrix")
def get_data_quality_report(db: Session = Depends(get_db)):
    service = IndiaAnalyticsService(db)
    return service.get_data_quality_report()


@router.get("/explorer", summary="Paginated Tabular Data Explorer")
def get_tabular_explorer(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=10, le=500, description="Page size"),
    state_code: Optional[str] = Query(None, description="State code filter"),
    source_code: Optional[str] = Query(None, description="Energy source filter"),
    year: Optional[int] = Query(None, description="Year filter"),
    dataset_classification: Optional[str] = Query(None, description="Filter: VERIFIED_OFFICIAL, OFFICIAL_SOURCE_UNVERIFIED, DEMONSTRATION"),
    db: Session = Depends(get_db)
):
    service = IndiaAnalyticsService(db)
    return service.get_tabular_explorer(
        page=page,
        page_size=page_size,
        state_code=state_code,
        source_code=source_code,
        year=year,
        dataset_classification=dataset_classification
    )


@router.get("/export/csv", summary="Export Generation Records as Standards-Compliant CSV")
def export_csv(
    state_code: Optional[str] = Query(None),
    source_code: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    dataset_classification: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = IndiaAnalyticsService(db)
    result = service.get_tabular_explorer(
        page=1,
        page_size=20000,
        state_code=state_code,
        source_code=source_code,
        year=year,
        dataset_classification=dataset_classification
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "State Code", "State Name", "Grid Region", "Fuel Source",
        "Year", "Month", "Period", "Generation (MU)", "Target (MU)",
        "Capacity Utilization Factor (%)", "Dataset Classification",
        "Observation Status", "Validation Status", "SHA-256 Checksum",
        "Original State Label", "Original Fuel Label", "Original Reported Value",
        "Original Unit", "Normalized Unit", "PDF Page Number", "Table Heading",
        "Parser Version", "Source Organization", "Original Filename", "Data Provenance"
    ])

    for r in result["records"]:
        writer.writerow([
            r["state_code"], r["state_name"], r["region_code"], r["source_code"],
            r["year"], r["month"], r["period"], r["generation_mu"], r["target_mu"],
            r["cuf_pct"], r["dataset_classification"], r["observation_status"],
            r["validation_status"], r.get("sha256_checksum", ""),
            r.get("original_state_label", ""), r.get("original_fuel_label", ""),
            r.get("original_reported_value", ""), r.get("original_unit", "MU"),
            r.get("normalized_unit", "MU"), r.get("pdf_page_number", ""),
            r.get("table_heading", ""), r.get("parser_version", ""),
            r["source_org"], r["original_filename"], r["source_provenance"]
        ])

    output.seek(0)
    filename = f"windscope_india_generation_{year or 'all'}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

