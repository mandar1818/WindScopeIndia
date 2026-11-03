# WindScope India — Production Deployment Guide
## Complete Runbook for Render (Backend & PostgreSQL) and Vercel (Frontend)

**Document Version:** 1.0.0  
**Project:** WindScope India — Renewable Energy Intelligence Platform  
**Target Repository:** `D:\WindScopeIndia`  
**Execution Date:** 01 November 2026  
**Auditor / Architecture Role:** Lead DevOps & Cloud Infrastructure Engineer  

---

## 1. System Architecture Overview

WindScope India is deployed across a decoupled, cloud-native architecture:

```mermaid
flowchart LR
    Client["Client Browser<br/>(Desktop / Mobile)"] -->|HTTPS / WSS| Vercel["Vercel CDN Edge<br/>React 18 + Vite SPA<br/>(windscope-india.vercel.app)"]
    Vercel -->|REST API Requests<br/>/api/v1/*| Render["Render Web Service<br/>FastAPI + Uvicorn (Python 3.12)<br/>(windscope-india-backend.onrender.com)"]
    Render -->|Encrypted Pool / TLS 1.3| DB["Render Managed PostgreSQL 15+<br/>(13 Relational Tables)"]
    Render -.->|Statutory Reports| Gov["Official Portals<br/>(CEA, NPP, MNRE, Grid-India)"]
```

---

## 2. Backend Deployment to Render

### 2.1 Service Specifications
- **Service Type:** Web Service (Native Python 3.12 or Docker)
- **Region:** Frankfurt (EU Central) or Singapore (Asia East) for low-latency routing to India.
- **Instance Type:** Standard (0.5 CPU, 512 MB RAM) or Pro for high concurrency.
- **Root Directory:** `backend`

### 2.2 Build & Start Commands
- **Build Command:**
  ```bash
  pip install --upgrade pip && pip install -r requirements.txt && alembic upgrade head
  ```
- **Start Command:**
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2 --timeout-keep-alive 30
  ```

### 2.3 Required Environment Variables
Configure the following in the Render Dashboard under **Environment**:

| Variable Name | Example Value | Description |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.12.10` | Enforces modern Python runtime. |
| `DATABASE_URL` | `postgresql://user:pass@host/db?sslmode=require` | Internal/External connection string. |
| `DATABASE_SSL_REQUIRE`| `true` | Enforces TLS encrypted communication. |
| `DATABASE_POOL_SIZE` | `10` | Persistent connection pool size per worker. |
| `DATABASE_MAX_OVERFLOW`| `20` | Maximum burst connections under heavy load. |
| `DATABASE_POOL_RECYCLE`| `1800` | Recycles connections after 30 minutes. |
| `APP_ENV` | `production` | Enables production security controls. |
| `INGESTION_ADMIN_KEY` | `strong-random-uuid-key` | Protects `/api/v1/india/ingestion/trigger`. |
| `CORS_ORIGINS` | `https://windscope-india.vercel.app,http://localhost:5173` | Allowed frontend client origins. |

### 2.4 Health Check & Zero-Downtime Probes
- **Health Check Path:** `/health`
- **Interval:** 30 seconds
- **Timeout:** 5 seconds
- Render guarantees zero-downtime rolling deploys: the new container must respond HTTP 200 on `/health` before traffic cuts over.

---

## 3. Frontend Deployment to Vercel

### 3.1 Project Configuration
- **Framework Preset:** Vite
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Node.js Version:** `20.x` or `22.x`

### 3.2 Required Environment Variables
Configure in Vercel Project Settings under **Environment Variables**:

| Variable Name | Value | Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `https://windscope-india-backend.onrender.com` | Base URL of deployed FastAPI backend. |

### 3.3 SPA Routing Configuration (`frontend/vercel.json`)
To prevent HTTP 404 on deep links (e.g. `/india/map`, `/india/state/IN-GJ`), ensure `frontend/vercel.json` includes SPA rewrites:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

---

## 4. Post-Deployment Verification Runbook

Immediately following deployment, execute these smoke test queries:

### Step 4.1: Verify Backend Root & Health Check
```bash
curl -f https://windscope-india-backend.onrender.com/health
```
Expected Response:
```json
{
  "status": "healthy",
  "service": "WindScope India — Renewable Energy Intelligence Platform",
  "platform_jurisdiction": "India (28 States & 8 Union Territories)",
  "market_timezone": "Asia/Kolkata (IST)"
}
```

### Step 4.2: Verify National Overview Endpoint
```bash
curl -f "https://windscope-india-backend.onrender.com/api/v1/india/overview?year=2026&month=1"
```
Expected Response: HTTP 200 with `total_generation_mu > 0`, `source_breakdown` (6 items), `top_states` (5 items).

### Step 4.3: Verify Grid Status Endpoint
```bash
curl -f https://windscope-india-backend.onrender.com/api/v1/india/grid/status
```
Expected Response: HTTP 200 with `grid_regions` (5 items) and `frequency_band_hz` ("49.90 - 50.05 Hz").

### Step 4.4: Verify Ingestion Key Protection
```bash
curl -s -o /dev/null -w "%{http_code}" -X POST https://windscope-india-backend.onrender.com/api/v1/india/ingestion/trigger -H "Content-Type: application/json" -d '{"source_key":"CEA","file_path":"test","reporting_year":2024}'
```
Expected Response: `401` Unauthorized.

---

## 5. Security & Disaster Recovery Checklist

- [x] HTTPS enforced across all endpoints with TLS 1.3.
- [x] Automated database backups enabled on Render (daily snapshots retained).
- [x] Ingestion admin key stored exclusively in cloud environment variables.
- [x] Database connection pooling configured with automatic 30-minute recycling.
- [x] Dedicated 14 India frontend modules verified functioning.

