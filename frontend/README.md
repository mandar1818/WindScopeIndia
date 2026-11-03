# WindScope India — Frontend Application

React 18 + TypeScript SPA powering the institutional analytics, interactive maps, and forecasting dashboards for the **WindScope India Renewable Energy Intelligence Platform**.

---

## Architecture & Technology Stack

- **Framework:** [React 18](https://react.dev/) + [TypeScript 5.4](https://www.typescriptlang.org/)
- **Bundler:** [Vite 5.3](https://vitejs.dev/) with route-level code splitting (`React.lazy` & `Suspense`)
- **Styling:** [Tailwind CSS 3.4](https://tailwindcss.com/) with custom institutional nature palette
- **Data Visualization:** [Recharts 2.12](https://recharts.org/) + SVG Interactive Choropleth Map
- **Icons:** [Lucide React](https://lucide.dev/)
- **Testing:** [Vitest 1.6](https://vitest.dev/) + [React Testing Library](https://testing-library.com/)

---

## 14 Dedicated Analytical Modules

1. **National Overview (`/india-overview`):** Top-level generation outturn, capacity, and fuel shares.
2. **Interactive India Map (`/india-map`):** SVG choropleth mapping all 28 States & 8 Union Territories.
3. **State & UT Explorer (`/india-states`):** Granular jurisdictional profiles, multi-year curves, and seasonality.
4. **Regional Comparison (`/india-regional`):** NR, WR, SR, ER, and NER regional grid council breakdowns.
5. **Multi-Year Analytics (`/india-multi-year`):** 2020–2026 trajectory tracking and YoY growth analysis.
6. **Wind Energy Analytics (`/india-wind`):** Wind generation surges, monsoon profiles, and non-wind disclosures.
7. **Solar Photovoltaic (`/india-solar`):** Solar park generation, insolation profiles, and seasonal peaks.
8. **Hydroelectric Energy (`/india-hydro`):** Large Hydro (>25 MW) and Small Hydro (≤25 MW) metrics.
9. **Capacity & 500 GW Target Tracker (`/india-capacity`):** Progress toward India's 2030 renewable targets.
10. **Forecasting & REMC Accuracy (`/india-forecasting`):** 96 intraday 15-minute dispatch blocks and DSM bands.
11. **Weather Intelligence (`/india-weather`):** Hub-height wind speeds, GHI solar irradiance, and ERA5 correlations.
12. **Data Explorer & Ledger (`/india-explorer`):** Searchable, paginated tabular ledger across 18,213 records with CSV export.
13. **Data Quality & Provenance (`/india-data-quality`):** 36/36 jurisdictional completeness and verification tagging.
14. **Technical Methodology (`/india-methodology`):** Statutory regulations (CERC IEGC 2023), formulas, and unit standards.

---

## Local Development & Build

### Prerequisites
- Node.js 18+ and npm

### Installation
```bash
npm install
```

### Development Server
```bash
npm run dev
```
Runs the Vite development server with HMR at `http://localhost:5173`.

### Running Tests
```bash
npm test
```
Executes Vitest component and navigation test suites.

### Production Build
```bash
npm run build
```
Type-checks with `tsc` and compiles optimized production bundles into `frontend/dist/`.
