# WindScope India — Database Migration Guide
## Step-by-Step Operator Runbook for PostgreSQL Provisioning, Alembic Execution & Production Data Seeding

**Document Version:** 1.0.0  
**Project:** WindScope India — Renewable Energy Intelligence Platform  
**Target Repository:** `D:\WindScopeUK`  
**Execution Date:** 01 November 2026  
**Auditor / Architecture Role:** Lead PostgreSQL Architect, DevOps Systems Engineer  

---

## 1. Overview & Objective

This runbook guides operators through provisioning an enterprise-grade PostgreSQL database (on Render, AWS RDS, Neon, or Supabase), executing Alembic schema migrations, and populating statutory renewable energy datasets.

WindScope India features a dual-dialect database architecture:
- **Local Development / Tests:** SQLite (`windscope_india.db`).
- **Production Staging & Cloud Deployments:** PostgreSQL 15+ via `psycopg2-binary`.

---

## 2. Prerequisites & Pre-Flight Checks

Before commencing database migrations:
1. Ensure Python 3.12+ and virtual environment are activated (`backend/.venv`).
2. Verify `psycopg2-binary` is installed:
   ```powershell
   & backend\.venv\Scripts\python.exe -c "import psycopg2; print(psycopg2.__version__)"
   # Output: 2.9.9
   ```
3. Provision a PostgreSQL 15+ instance with network access enabled.
4. Obtain the connection string in the format:
   `postgresql://username:password@hostname:port/database_name?sslmode=require`

---

## 3. Environment Variable Configuration

Create or update `.env` in the `backend/` directory or set environment variables in your cloud provider's dashboard:

```bash
# Database Connection URL (Mandatory for PostgreSQL)
DATABASE_URL=postgresql://windscope_user:SecurePassword123@dpg-xxxxxx.render.com/windscope_db

# Enforce TLS 1.3 / SSL Mode
DATABASE_SSL_REQUIRE=true
DATABASE_SSL_MODE=require

# Connection Pool Parameters (Optimized for 100+ concurrent analysts)
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=1800

# Application Environment & Security
APP_ENV=production
INGESTION_ADMIN_KEY=your-strong-production-api-key-here
```

> [!NOTE]
> If your cloud provider provisions the URL with legacy `postgres://`, `backend/app/core/database.py` automatically rewrites the prefix to `postgresql://` to maintain full compatibility with SQLAlchemy 2.x.

---

## 4. Executing Alembic Migrations

The database migration is managed via Alembic revision `af8f7710238a`.

### Step 4.1: Inspect Pending Migration Status
Run from the `backend/` directory:
```powershell
cd backend
& .venv\Scripts\alembic.exe current
```

### Step 4.2: Apply Schema Migration to Head
Execute the migration to provision all 13 relational tables, composite constraints, and indexes:
```powershell
& .venv\Scripts\alembic.exe upgrade head
```

Expected Output:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> af8f7710238a, Initial complete WindScope India schema
```

### Step 4.3: Verify Tables Created in PostgreSQL
Verify table provisioning using `psql` or database client:
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
```

Expected list of 13 tables:
1. `alembic_version`
2. `energy_sources`
3. `forecast_evaluations`
4. `forecast_records`
5. `generation_15min_blocks`
6. `generation_daily`
7. `generation_monthly`
8. `geographies`
9. `ingestion_audit_logs`
10. `installed_capacities`
11. `national_reconciliations`
12. `regions`
13. `source_files`
14. `weather_observations`

---

## 5. Production Data Seeding & Statutory Ingestion

Once the schema is established, populate the database using the idempotent ingestion pipeline:

### Step 5.1: Seed Core Geography, Regions & Demonstration Baseline
```powershell
$env:PYTHONPATH='backend'
& backend\.venv\Scripts\python.exe -m app.services.seed_data
```
This populates:
- 5 Regional Power Committees (NRPC, WRPC, SRPC, ERPC, NERPC)
- 36 States and Union Territories + National Aggregate entity
- 6 Energy Source streams (WIND, SOLAR, LARGE_HYDRO, SMALL_HYDRO, BIOMASS, OTHER_RE)
- Multi-year demonstration benchmark (2020–2026)

### Step 5.2: Ingest Official Installed Capacity Bulletins (NPP / CEA)
Ingest the official gazettes for June 2024 and September 2026:
```powershell
& backend\.venv\Scripts\python.exe -m app.services.ingestion.capacity_ingestion
```
Extracts and stores:
- June 30, 2024: 195.01 GW Clean RE (85.47 GW Solar, 46.66 GW Wind, 46.93 GW Large Hydro)
- September 30, 2026: 299.25 GW Clean RE (171.05 GW Solar, 59.20 GW Wind, 52.06 GW Large Hydro)

### Step 5.3: Ingest Official Generation Bulletins (CEA Sub-Report 1 & 16)
Ingest the official monthly generation reports:
```powershell
& backend\.venv\Scripts\python.exe -m app.services.ingestion.pdf_pipeline
```

### Step 5.4: Apply Forensic Provenance Audit
Run the observation classification auditor to verify zero unclassified records:
```powershell
& backend\.venv\Scripts\python.exe -c "from app.services.apply_phase2_final_remediation import run_remediation; run_remediation()"
```

---

## 6. Rollback & Disaster Recovery Procedures

### 6.1 Rolling Back Migration
If an issue occurs during schema deployment, revert the migration cleanly:
```powershell
# Revert to base (drops all tables cleanly)
& .venv\Scripts\alembic.exe downgrade base

# Or revert one step
& .venv\Scripts\alembic.exe downgrade -1
```

### 6.2 PostgreSQL Full Backup (`pg_dump`)
Prior to performing maintenance or upgrades in production:
```bash
pg_dump "$DATABASE_URL" \
  --format=custom \
  --no-owner \
  --no-privileges \
  --file=windscope_india_backup_$(date +%Y%m%d_%H%M%S).dump
```

### 6.3 Restoring from Backup (`pg_restore`)
```bash
pg_restore \
  --clean \
  --if-exists \
  --no-owner \
  --no-privileges \
  --dbname="$DATABASE_URL" \
  windscope_india_backup_20261101.dump
```

---

## 7. Troubleshooting Common Database Issues

| Symptom / Error | Root Cause | Operator Remediation |
| :--- | :--- | :--- |
| `psycopg2.OperationalError: SSL connection has been closed unexpectedly` | Cloud firewall closed idle TCP socket | Ensure `DATABASE_POOL_RECYCLE=1800` is active in `.env`. |
| `sqlalchemy.exc.TimeoutError: QueuePool limit exceeded` | Application connections not released back to pool | Verify that all database queries utilize `with get_db_context() as db:` or FastAPI dependency `db: Session = Depends(get_db)`. |
| `Can't load plugin: sqlalchemy.dialects:driver` | Default placeholder string in `alembic.ini` | Ensure `DATABASE_URL` is set in environment or `.env`; `backend/alembic/env.py` automatically substitutes the real connection string. |
| `DuplicateDocumentError` during ingestion | File with identical SHA-256 already ingested | Ingestion is strictly idempotent. To force re-extraction, pass `allow_reprocessing=True` to the adapter. |

