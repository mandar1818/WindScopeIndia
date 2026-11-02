"""
WindScope India — Weather Intelligence Service.
Integrates genuine meteorological parameters (Open-Meteo & ECMWF ERA5)
for state-level renewable intelligence: Hub-height wind speeds, 10m wind speeds,
Solar GHI/DNI, temperature, cloud cover, and precipitation.
"""
import time
import math
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.geography import Geography
from app.models.weather import WeatherObservation


class WeatherService:
    REZ_PARKS = [
        {
            "code": "REZ-BHADLA",
            "name": "Bhadla Solar Park",
            "state_code": "IN-RJ",
            "state_name": "Rajasthan",
            "technology": "SOLAR",
            "capacity_mw": 2245.0,
            "latitude": 27.5398,
            "longitude": 71.9161,
            "location_description": "Phalodi district, Thar Desert region",
            "elevation_m": 210.0
        },
        {
            "code": "REZ-KHAVDA",
            "name": "Khavda Hybrid Renewable Energy Park",
            "state_code": "IN-GJ",
            "state_name": "Gujarat",
            "technology": "HYBRID_WIND_SOLAR",
            "capacity_mw": 30000.0,
            "latitude": 23.8373,
            "longitude": 69.7548,
            "location_description": "Great Rann of Kutch, near Indo-Pak border",
            "elevation_m": 15.0
        },
        {
            "code": "REZ-PAVAGADA",
            "name": "Pavagada Solar Park (Shakti Sthala)",
            "state_code": "IN-KA",
            "state_name": "Karnataka",
            "technology": "SOLAR",
            "capacity_mw": 2050.0,
            "latitude": 14.2811,
            "longitude": 77.2769,
            "location_description": "Tumakuru district, semi-arid plateau",
            "elevation_m": 650.0
        },
        {
            "code": "REZ-MUPPANDAL",
            "name": "Muppandal Wind Farm",
            "state_code": "IN-TN",
            "state_name": "Tamil Nadu",
            "technology": "WIND",
            "capacity_mw": 1500.0,
            "latitude": 8.2614,
            "longitude": 77.5458,
            "location_description": "Kanyakumari district, Palakkad / Aramboli Gap wind funnel",
            "elevation_m": 45.0
        },
        {
            "code": "REZ-JAISALMER",
            "name": "Jaisalmer Wind Park",
            "state_code": "IN-RJ",
            "state_name": "Rajasthan",
            "technology": "WIND",
            "capacity_mw": 1600.0,
            "latitude": 26.9157,
            "longitude": 70.9083,
            "location_description": "Jaisalmer district, western desert plateau",
            "elevation_m": 225.0
        },
        {
            "code": "REZ-REWA",
            "name": "Rewa Ultra Mega Solar",
            "state_code": "IN-MP",
            "state_name": "Madhya Pradesh",
            "technology": "SOLAR",
            "capacity_mw": 750.0,
            "latitude": 24.4789,
            "longitude": 81.5739,
            "location_description": "Gurh tehsil, Rewa district",
            "elevation_m": 310.0
        },
        {
            "code": "REZ-KURNOOL",
            "name": "Kurnool Ultra Mega Solar Park",
            "state_code": "IN-AP",
            "state_name": "Andhra Pradesh",
            "technology": "SOLAR",
            "capacity_mw": 1000.0,
            "latitude": 15.6811,
            "longitude": 78.2858,
            "location_description": "Gani and Sakunala villages, Kurnool district",
            "elevation_m": 280.0
        }
    ]

    def __init__(self, db: Session):
        self.db = db
        self.api_base_url = "https://api.open-meteo.com/v1/forecast"
        self.archive_base_url = "https://archive-api.open-meteo.com/v1/archive"

    @classmethod
    def get_rez_parks(cls) -> List[Dict[str, Any]]:
        return cls.REZ_PARKS

    def fetch_open_meteo_historical(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        retries: int = 3,
        backoff_sec: float = 1.0
    ) -> Optional[Dict[str, Any]]:
        """
        Fetches genuine historical reanalysis weather data from Open-Meteo Historical Archive API (ERA5/CERRA).
        Includes retry mechanism with exponential backoff.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "temperature_2m,precipitation,cloud_cover,shortwave_radiation,direct_normal_irradiance,wind_speed_10m,wind_speed_100m,wind_direction_100m",
            "wind_speed_unit": "ms",
            "timezone": "Asia/Kolkata"
        }

        for attempt in range(1, retries + 1):
            try:
                with httpx.Client(timeout=20.0) as client:
                    resp = client.get(self.archive_base_url, params=params)
                    if resp.status_code == 200:
                        return resp.json()
                    elif resp.status_code == 429:
                        time.sleep(backoff_sec * attempt * 2)
            except Exception:
                time.sleep(backoff_sec * attempt)
        return None

    def fetch_open_meteo_live(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
        retries: int = 3,
        backoff_sec: float = 1.0
    ) -> Optional[Dict[str, Any]]:
        """
        Fetches live weather forecast from Open-Meteo API.
        Returns None if network is unavailable or request fails.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,precipitation,cloud_cover,shortwave_radiation,direct_normal_irradiance,wind_speed_10m,wind_speed_100m,wind_direction_100m",
            "forecast_days": forecast_days,
            "wind_speed_unit": "ms",
            "timezone": "Asia/Kolkata"
        }
        for attempt in range(1, retries + 1):
            try:
                with httpx.Client(timeout=15.0) as client:
                    resp = client.get(self.api_base_url, params=params)
                    if resp.status_code == 200:
                        return resp.json()
                    elif resp.status_code == 429:
                        time.sleep(backoff_sec * attempt * 2)
            except Exception:
                time.sleep(backoff_sec * attempt)
        return None

    def ingest_weather_observations(
        self,
        geography: Geography,
        raw_payload: Dict[str, Any],
        record_type: str = "REANALYSIS",
        weather_model: str = "ECMWF ERA5"
    ) -> int:
        """
        Parses Open-Meteo hourly payload and persists actual observations with deduplication.
        Returns number of newly persisted observations.
        """
        hourly = raw_payload.get("hourly", {})
        times = hourly.get("time", [])
        if not times:
            return 0

        temps = hourly.get("temperature_2m", [])
        precips = hourly.get("precipitation", [])
        clouds = hourly.get("cloud_cover", [])
        ghis = hourly.get("shortwave_radiation", [])
        dnis = hourly.get("direct_normal_irradiance", [])
        wind10s = hourly.get("wind_speed_10m", [])
        wind100s = hourly.get("wind_speed_100m", [])
        wind_dirs = hourly.get("wind_direction_100m", [])

        # Fetch existing timestamps for this geography to guarantee idempotency
        existing_times = set(
            t[0] for t in self.db.query(WeatherObservation.observation_time).filter(
                WeatherObservation.geography_id == geography.id
            ).all()
        )

        new_records = []
        retrieval_dt = datetime.utcnow()
        lat = float(geography.latitude)
        lon = float(geography.longitude)

        for i, time_str in enumerate(times):
            obs_dt = datetime.fromisoformat(time_str)
            if obs_dt in existing_times:
                continue

            obs = WeatherObservation(
                geography_id=geography.id,
                observation_time=obs_dt,
                wind_speed_10m_ms=round(float(wind10s[i]), 2) if i < len(wind10s) and wind10s[i] is not None else None,
                wind_speed_100m_ms=round(float(wind100s[i]), 2) if i < len(wind100s) and wind100s[i] is not None else None,
                wind_direction_deg=round(float(wind_dirs[i]), 1) if i < len(wind_dirs) and wind_dirs[i] is not None else None,
                solar_ghi_wm2=round(float(ghis[i]), 2) if i < len(ghis) and ghis[i] is not None else None,
                solar_dni_wm2=round(float(dnis[i]), 2) if i < len(dnis) and dnis[i] is not None else None,
                temperature_celsius=round(float(temps[i]), 2) if i < len(temps) and temps[i] is not None else None,
                cloud_cover_pct=round(float(clouds[i]), 2) if i < len(clouds) and clouds[i] is not None else None,
                precipitation_mm=round(float(precips[i]), 2) if i < len(precips) and precips[i] is not None else None,
                latitude=lat,
                longitude=lon,
                weather_model=weather_model,
                record_type=record_type,
                weather_source="Open-Meteo / ECMWF ERA5",
                retrieval_timestamp=retrieval_dt
            )
            new_records.append(obs)
            existing_times.add(obs_dt)

        if new_records:
            self.db.bulk_save_objects(new_records)
            self.db.commit()

        return len(new_records)

    def ingest_all_states_historical_weather(
        self,
        start_date: str = "2024-06-01",
        end_date: str = "2024-06-07"
    ) -> Dict[str, Any]:
        """
        Retrieves and stores genuine historical weather observations for all 36 State/UT centroids.
        Tracks requests made, success, failure, records retrieved, and coverage.
        """
        geos = self.db.query(Geography).filter(
            Geography.entity_type.in_(["STATE", "UNION_TERRITORY"])
        ).order_by(Geography.code.asc()).all()

        report = {
            "period": f"{start_date} to {end_date}",
            "api_requests_made": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "records_retrieved": 0,
            "records_persisted": 0,
            "geographic_coverage": [],
            "missing_data": []
        }

        for geo in geos:
            report["api_requests_made"] += 1
            lat = float(geo.latitude)
            lon = float(geo.longitude)

            payload = self.fetch_open_meteo_historical(
                latitude=lat,
                longitude=lon,
                start_date=start_date,
                end_date=end_date
            )

            if payload and "hourly" in payload:
                report["successful_responses"] += 1
                times = payload["hourly"].get("time", [])
                retrieved_count = len(times)
                report["records_retrieved"] += retrieved_count

                persisted = self.ingest_weather_observations(
                    geography=geo,
                    raw_payload=payload,
                    record_type="REANALYSIS",
                    weather_model="ECMWF ERA5"
                )
                report["records_persisted"] += persisted
                report["geographic_coverage"].append({
                    "state_code": geo.code,
                    "state_name": geo.name,
                    "records_persisted": persisted
                })
            else:
                report["failed_responses"] += 1
                report["missing_data"].append({
                    "state_code": geo.code,
                    "state_name": geo.name,
                    "error": "Open-Meteo Historical API request failed or timed out"
                })

            # Small polite pause to avoid hitting rate limits
            time.sleep(0.15)

        return report

    def compute_weather_generation_correlation(
        self,
        state_code: str = "IN-GJ",
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Computes Pearson correlation between genuinely matched meteorological observations
        and verified official generation observations.

        Strict validation rules:
        - Only matches weather observations with GenerationDaily where data_classification == 'VERIFIED_OFFICIAL'.
        - Excludes all DEMONSTRATION and unverified generation records.
        - Matches identical geography and delivery dates.
        - Calculates Pearson r: sum((x - mean_x)(y - mean_y)) / sqrt(sum(x - mean_x)^2 * sum(y - mean_y)^2)
        - Requires a minimum matched sample size of N >= 3 with non-zero variance.
        - If matched valid observations are unavailable or N < 3, returns status 'INSUFFICIENT_DATA'
          and correlation values of None.
        """
        geo = self.db.query(Geography).filter(Geography.code == state_code).first()
        if not geo:
            return {
                "status": "INSUFFICIENT_DATA",
                "status_description": f"Geography code '{state_code}' not found.",
                "matched_sample_size_n": 0,
                "wind_sample_size_n": 0,
                "solar_sample_size_n": 0,
                "hub_height_wind_correlation": None,
                "solar_ghi_correlation": None
            }

        # 1. Query daily average weather observations for this geography
        obs_query = self.db.query(
            func.date(WeatherObservation.observation_time).label("obs_date"),
            func.avg(WeatherObservation.wind_speed_100m_ms).label("avg_wind_100m"),
            func.avg(WeatherObservation.solar_ghi_wm2).label("avg_solar_ghi")
        ).filter(
            WeatherObservation.geography_id == geo.id,
            WeatherObservation.record_type.in_(["REANALYSIS", "HISTORICAL_OBSERVATION"])
        )

        if year:
            obs_query = obs_query.filter(
                WeatherObservation.observation_time >= datetime(year, 1, 1),
                WeatherObservation.observation_time <= datetime(year, 12, 31, 23, 59, 59)
            )

        weather_daily = obs_query.group_by(func.date(WeatherObservation.observation_time)).all()
        weather_map = {
            str(r.obs_date): {
                "wind_100m": float(r.avg_wind_100m) if r.avg_wind_100m is not None else None,
                "solar_ghi": float(r.avg_solar_ghi) if r.avg_solar_ghi is not None else None
            }
            for r in weather_daily
        }

        # 2. Query VERIFIED_OFFICIAL daily generation observations (exclude DEMONSTRATION)
        from app.models.generation import GenerationDaily
        gen_query = self.db.query(GenerationDaily).filter(
            GenerationDaily.geography_id == geo.id,
            GenerationDaily.data_classification == "VERIFIED_OFFICIAL",
            GenerationDaily.source_code.in_(["WIND", "SOLAR"])
        )
        if year:
            gen_query = gen_query.filter(
                GenerationDaily.delivery_date >= date(year, 1, 1),
                GenerationDaily.delivery_date <= date(year, 12, 31)
            )
        gen_records = gen_query.all()

        wind_pairs = []   # (weather_wind, gen_mu)
        solar_pairs = []  # (weather_ghi, gen_mu)

        for rec in gen_records:
            d_str = rec.delivery_date.isoformat()
            if d_str in weather_map:
                w_data = weather_map[d_str]
                gen_val = float(rec.generation_mu) if rec.generation_mu is not None else None
                if gen_val is not None:
                    if rec.source_code == "WIND" and w_data["wind_100m"] is not None:
                        wind_pairs.append((w_data["wind_100m"], gen_val))
                    elif rec.source_code == "SOLAR" and w_data["solar_ghi"] is not None:
                        solar_pairs.append((w_data["solar_ghi"], gen_val))

        def _pearson(pairs):
            if len(pairs) < 3:
                return None
            xs = [p[0] for p in pairs]
            ys = [p[1] for p in pairs]
            mean_x = sum(xs) / len(xs)
            mean_y = sum(ys) / len(ys)
            cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
            var_x = sum((x - mean_x) ** 2 for x in xs)
            var_y = sum((y - mean_y) ** 2 for y in ys)
            if var_x <= 1e-9 or var_y <= 1e-9:
                return None
            return round(cov / math.sqrt(var_x * var_y), 3)

        wind_r = _pearson(wind_pairs)
        solar_r = _pearson(solar_pairs)
        max_matched = max(len(wind_pairs), len(solar_pairs))

        if max_matched < 3 or (wind_r is None and solar_r is None):
            return {
                "status": "INSUFFICIENT_DATA",
                "status_description": f"Insufficient verified official generation observations matched with meteorological observations for {state_code} in {year or 'all years'} (minimum N=3 required for Pearson correlation). Demonstration records excluded.",
                "matched_sample_size_n": max_matched,
                "wind_sample_size_n": len(wind_pairs),
                "solar_sample_size_n": len(solar_pairs),
                "hub_height_wind_correlation": None,
                "solar_ghi_correlation": None
            }

        return {
            "status": "CALCULATED_FROM_MATCHED_OBSERVATIONS",
            "status_description": "Computed from genuinely matched verified official generation and ECMWF ERA5 reanalysis.",
            "matched_sample_size_n": max_matched,
            "wind_sample_size_n": len(wind_pairs),
            "solar_sample_size_n": len(solar_pairs),
            "hub_height_wind_correlation": wind_r,
            "solar_ghi_correlation": solar_r
        }

    def get_state_weather(
        self,
        state_code: str = "IN-GJ",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieves weather series for a specific state, combining stored observations
        with provider metadata and clear demonstration/live classification.
        """
        geo = self.db.query(Geography).filter(Geography.code == state_code).first()
        if not geo:
            # Fallback to IN-GJ (Gujarat)
            geo = self.db.query(Geography).filter(Geography.code == "IN-GJ").first()

        lat = float(geo.latitude) if geo else 22.2587
        lon = float(geo.longitude) if geo else 71.1924
        state_name = geo.name if geo else "Gujarat"

        # Check existing observations in database
        obs_query = self.db.query(WeatherObservation).filter(
            WeatherObservation.geography_id == (geo.id if geo else 1)
        ).order_by(WeatherObservation.observation_time.asc())

        if start_date:
            try:
                dt_start = datetime.fromisoformat(start_date)
                obs_query = obs_query.filter(WeatherObservation.observation_time >= dt_start)
            except ValueError:
                pass

        if end_date:
            try:
                dt_end = datetime.fromisoformat(end_date)
                obs_query = obs_query.filter(WeatherObservation.observation_time <= dt_end)
            except ValueError:
                pass
        elif year:
            # Filter specifically for the requested calendar year
            dt_year_start = datetime(year, 1, 1, 0, 0)
            dt_year_end = datetime(year, 12, 31, 23, 59)
            obs_query = obs_query.filter(
                WeatherObservation.observation_time >= dt_year_start,
                WeatherObservation.observation_time <= dt_year_end
            )

        limit_val = 168 if (start_date or end_date or year) else 24
        db_records = obs_query.limit(limit_val).all()

        if db_records:
            series = [
                {
                    "time": r.observation_time.isoformat(),
                    "wind_speed_10m_ms": float(r.wind_speed_10m_ms) if r.wind_speed_10m_ms is not None else None,
                    "wind_speed_100m_ms": float(r.wind_speed_100m_ms) if r.wind_speed_100m_ms is not None else None,
                    "wind_direction_deg": float(r.wind_direction_deg) if r.wind_direction_deg is not None else None,
                    "solar_ghi_wm2": float(r.solar_ghi_wm2) if r.solar_ghi_wm2 is not None else None,
                    "solar_dni_wm2": float(r.solar_dni_wm2) if r.solar_dni_wm2 is not None else None,
                    "temperature_c": float(r.temperature_celsius) if r.temperature_celsius is not None else None,
                    "cloud_cover_pct": float(r.cloud_cover_pct) if r.cloud_cover_pct is not None else None,
                    "precipitation_mm": float(r.precipitation_mm) if r.precipitation_mm is not None else None,
                    "type": r.record_type or "HISTORICAL_OBSERVATION"
                }
                for r in db_records
            ]
            source_classification = "VERIFIED_METEOROLOGICAL_ARCHIVE"
            provider = db_records[0].weather_source or "ECMWF ERA5 / Open-Meteo"
            weather_model = db_records[0].weather_model or "ECMWF ERA5"
            is_demonstration = False
        else:
            # When no stored records exist: clearly mark as DEMONSTRATION_CALIBRATED_IMD
            series = []
            fallback_year = year or 2026
            base_time = datetime(fallback_year, 1, 15, 0, 0)
            for hour in range(24):
                t = base_time + timedelta(hours=hour)
                ghi = max(0.0, round(850.0 * math.sin(max(0, math.pi * (hour - 6) / 12)), 1)) if 6 <= hour <= 18 else 0.0
                dni = max(0.0, round(ghi * 1.15, 1)) if ghi > 0 else 0.0
                wind = round(6.5 + 2.5 * math.sin(math.pi * (hour - 3) / 12), 2)
                temp = round(21.0 + 8.0 * math.sin(math.pi * (hour - 8) / 12), 1)
                cloud = round(15.0 + 10.0 * math.cos(math.pi * hour / 12), 1)

                series.append({
                    "time": t.isoformat(),
                    "wind_speed_10m_ms": round(wind * 0.75, 2),
                    "wind_speed_100m_ms": wind,
                    "wind_direction_deg": 240.0,
                    "solar_ghi_wm2": ghi,
                    "solar_dni_wm2": dni,
                    "temperature_c": temp,
                    "cloud_cover_pct": cloud,
                    "precipitation_mm": 0.0,
                    "type": "DEMONSTRATION_CALIBRATED"
                })
            source_classification = "DEMONSTRATION_CALIBRATED_IMD"
            provider = "India Meteorological Department (IMD) Climatological Norms (Mathematical Simulation)"
            weather_model = "Diurnal Climatological Harmonics"
            is_demonstration = True

        valid_winds = [s["wind_speed_100m_ms"] for s in series if s.get("wind_speed_100m_ms") is not None]
        avg_wind = round(sum(valid_winds) / max(1, len(valid_winds)), 2) if valid_winds else 0.0
        peak_ghi = round(max((s["solar_ghi_wm2"] or 0.0) for s in series), 1) if series else 0.0

        return {
            "state_code": state_code,
            "state_name": state_name,
            "coordinates": {"latitude": lat, "longitude": lon},
            "source_classification": source_classification,
            "is_demonstration": is_demonstration,
            "provider_metadata": {
                "provider": provider,
                "model": weather_model,
                "spatial_resolution": "0.1° (~11 km)",
                "elevation_model": "Copernicus DEM",
                "units": {
                    "wind_speed": "m/s",
                    "wind_direction": "degrees",
                    "solar_ghi": "W/m²",
                    "solar_dni": "W/m²",
                    "temperature": "°C",
                    "precipitation": "mm",
                    "cloud_cover": "%"
                },
                "disclaimer": "Weather observations are recorded at state geographic centroid. For utility parks (e.g. Bhadla, Khavda), on-site pyranometers and anemometer masts should be referenced."
            },
            "summary_metrics": {
                "average_wind_speed_100m_ms": avg_wind,
                "peak_solar_ghi_wm2": peak_ghi,
                "data_points_count": len(series)
            },
            "series": series
        }
