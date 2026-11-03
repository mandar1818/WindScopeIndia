# WindScope India — Backend Service

FastAPI REST API and data ingestion service powering the **WindScope India Renewable Energy Intelligence Platform**.

---

## Architecture & Technology Stack

- **API Framework:** [FastAPI 0.110](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **Runtime:** Python 3.12
- **ORM & Migrations:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) + [Alembic 1.20](https://alembic.sqlalchemy.org/)
- **Data Engines:** [Pandas 2.2](https://pandas.pydata.org/), [NumPy 1.26](https://numpy.org/), [pdfplumber](https://github.com/jsvine/pdfplumber)
- **Database Support:** SQLite (development / standalone) & PostgreSQL 15+ (production target)
- **Testing:** [Pytest 8.1](https://docs.pytest.org/) + `pytest-asyncio`

---

## Directory Layout

```
backend/
├── alembic/                # Database migration scripts and environment
│   └── versions/           # Migration revisions (af8f7710238a, b12984cf5102, c34891ef9012)
├── app/
│   ├── api/v1/             # REST endpoints (/india/*, /health)
│   ├── core/               # Configuration (Pydantic BaseSettings), logging, DB session
│   ├── models/             # SQLAlchemy ORM declarations (generation, geography, weather, etc.)
│   └── services/           # Ingestion pipelines, analytics engine, forecasting, market rules
├── data/
│   └── raw/                # Statutory CEA and Grid-India source bulletins and datasets
└── tests/                  # Pytest test suite (67 test cases)
```

---

## Local Setup & Execution

### 1. Environment Setup
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
```

### 2. Database Migrations
```bash
alembic upgrade head
```

### 3. Running the Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Probe: `http://localhost:8000/health`

### 4. Running Tests
```bash
.venv\Scripts\python.exe -m pytest tests -v
```
Runs the 67-case test suite covering mathematical formulas, CERC market rules, ingestion adapters, and API endpoints.
