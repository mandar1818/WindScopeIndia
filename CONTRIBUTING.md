# Contributing to WindScope India

Thank you for your interest in contributing to **WindScope India — Renewable Energy Intelligence Platform**! We welcome contributions that enhance our analytics, improve statutory data pipelines, or expand test coverage.

---

## Code of Conduct & Ground Rules

1. **Data Integrity Above All:** We do not fabricate, simulate without labeling, or manipulate statutory generation datasets. Official government observations must retain exact provenance and checksums. Synthetic data must always be tagged `DEMONSTRATION`.
2. **Strict Non-Zero Interpretation:** Missing observations (`null`) must never be silently converted to `0.0`.
3. **Statutory Anti-Leakage:** Any forecasting evaluations must enforce CERC gate closures (DAM/GDAM at 12:00 IST on D-1, RTM at T-75m) to prevent look-ahead bias.
4. **Design Consistency:** All UI components must adhere to the institutional natural palette (Deep Forest `#245B45`, Sage `#8FAE91`, Soft Pale `#F5F7F2`).

---

## Development Workflow

### 1. Fork and Clone
```bash
git clone https://github.com/mandar1818/WindScopeIndia.git
cd WindScopeIndia
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
pytest tests -v
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm test
npm run build
npm run dev
```

### 4. Commits and Pull Requests
- Create a feature branch: `git checkout -b feature/your-feature-name`
- Follow conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- Ensure all backend tests (`pytest tests -v`) and frontend tests (`npm test` and `npm run build`) pass before opening a PR.
