# WindScope India — Deployment & Operations Manual

**Document Reference:** `WINDSCOPE_INDIA_DEPLOYMENT_OPERATIONS_MANUAL.md`  
**Date:** November 1, 2026  
**Status:** Certified Operational Runbook  
**Primary Working Directory:** `D:\WindScopeIndia`  

---

## Executive Summary

This operations manual details production deployment, environment configuration, administrative security, database maintenance, and scheduled statutory ingestion procedures for **WindScope India**. It serves as the definitive reference for DevOps engineers, data engineers, and system administrators operating the platform.

---

## 1. System Architecture & Deployment Topology

WindScope India is architected as a decoupled, cloud-native full-stack platform:

```
[ Clients / Web Browsers ]
            │
            ▼ (HTTPS / DNS: windscope-india.vercel.app)
┌────────────────────────────────────────────────────────┐
│             Vercel Frontend Edge Network               │
│  React 18 + Vite 5 + Tailwind CSS SPA                 │
└────────────────────────────────────────────────────────┘
            │
            ▼ (REST API / JSON / HTTPS)
┌────────────────────────────────────────────────────────┐
│             Render Web Service Container               │
│  FastAPI (Python 3.12) + Uvicorn ASGI Server          │
│  - Endpoint Router: /api/v1/india/*                    │
│  - Preserved Benchmark: /api/v1/* (UK Elexon)          │
│  - Ingestion Engine & Schedulers                       │
└────────────────────────────────────────────────────────┘
            │
            ▼ (SQLAlchemy Pool / PostgreSQL 15+ / SQLite)
┌────────────────────────────────────────────────────────┐
│           Production Relational Database               │
│  - Canonical Geographies (42)                          │
│  - Generation Monthly (16,134 records)                 │
│  - Weather Observations (12,096 records)               │
│  - Daily Operational Metrics (Demand Met)              │
│  - Source Files & Checksums (SHA-256)                  │
└────────────────────────────────────────────────────────┘
```

---

## 2. Environment Variables & Secret Configuration

Production environments are configured via `.env` (derived from `.env.example`). No sensitive credentials are committed to source control:

| Variable Name | Required | Default / Example | Purpose |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Yes | `sqlite:///./windscope_india.db` | Connection string (PostgreSQL in production) |
| `DATABASE_POOL_SIZE` | No | `10` | SQLAlchemy persistent connection pool size |
| `DATABASE_MAX_OVERFLOW`| No | `20` | Maximum burst connections beyond pool size |
| `DATABASE_POOL_RECYCLE`| No | `1800` | Socket recycle interval in seconds (30 min) |
| `APP_ENV` | Yes | `production` | Environment mode (`development`, `production`) |
| `DEBUG` | Yes | `false` | Disables verbose tracebacks in production |
| `INGESTION_ADMIN_KEY` | Yes | `<secure-uuid-token>` | Secret key for triggering manual document ingestion |
| `CORS_ORIGINS` | Yes | `["https://windscope-india.vercel.app"]` | Allowed CORS origins for browser security |
| `TIMEZONE_IST` | No | `Asia/Kolkata` | Standard Indian Market operational timezone |
| `MARKET_TIMEZONE` | No | `Asia/Kolkata` | Standard Indian Market operational timezone |

---

## 3. Operational Runbooks & Administration

### 3.1 Ingestion Triggering & Security
Automated document ingestion endpoints are protected by `X-API-KEY` header authentication:

```bash
# Trigger Ingestion of a newly published CEA Monthly Report
curl -X POST https://windscope-india-backend.onrender.com/api/v1/india/ingestion/trigger \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $INGESTION_ADMIN_KEY" \
  -d '{
    "source_key": "CEA",
    "file_path": "backend/data/raw/cea/2026_10_RE_Monthly.pdf",
    "reporting_year": 2026,
    "reporting_month": 10
  }'
```

*Unauthorized requests without the matching `X-API-KEY` return `401 Unauthorized`.*

### 3.2 Scheduled Weather Intelligence Refresh
Weather observations are updated periodically using the `WeatherService` batch pipeline:
```bash
# Ingest 7-day reanalysis batch across all 36 state centroids
python backend/expand_weather_coverage.py
```
*Built-in pacing (0.3s sleep between requests) prevents Open-Meteo HTTP 429 rate-limiting.*

### 3.3 Database Backup & Restore Procedures
1. **Pre-Deployment Backup:**
   ```bash
   cp backend/windscope_india.db backend/windscope_india_backup_$(date +%Y%m%d_%H%M%S).db
   ```
2. **PostgreSQL Dump (Production):**
   ```bash
   pg_dump $DATABASE_URL --format=custom --file=windscope_backup_$(date +%Y%m%d).dump
   ```
3. **Database Migration Deployment:**
   ```bash
   cd backend
   alembic upgrade head
   ```

---

## 4. Health Checks & Monitoring

* **Liveness & Readiness Probe:** `GET /health`
  * Returns JSON payload verifying application uptime, current active database dialect, and system memory state.
* **Source Lag & Freshness Metric:** `GET /api/v1/india/ingestion/freshness`
  * Returns publication lag in days and flags whether statutory CEA reports are overdue.

