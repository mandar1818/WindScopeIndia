"""
CEA Renewable Generation Tabular Parser.
Parses CSV and Excel (.xlsx) reports published by the Central Electricity Authority.
Extracts state-wise monthly generation for Wind, Solar, Hydro, Biomass, and Other RE.
"""

import csv
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from app.services.ingestion.state_mapper import map_state_name
from app.services.ingestion.fuel_mapper import map_fuel_stream
from app.services.ingestion.observation_auditor import audit_observation
from app.services.ingestion.reconciler import reconcile_national_total, ReconciliationResult


class CEAParseError(Exception):
    """Raised when parsing a CEA document fails."""
    pass


class CEAParser:
    """Parser for CEA monthly state-wise renewable generation reports."""

    def __init__(self, capacity_lookup: Optional[Dict[Tuple[str, str], float]] = None):
        """
        capacity_lookup: Optional dict of (state_iso_code, fuel_code) -> capacity_mw
        """
        self.capacity_lookup = capacity_lookup or {}

    def _read_csv_robust(self, filepath: Path) -> pd.DataFrame:
        """Reads CSV file safely even if title lines have irregular field counts."""
        encodings = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
        raw_rows = []
        for enc in encodings:
            try:
                with open(filepath, "r", encoding=enc, errors="replace") as f:
                    reader = csv.reader(f)
                    raw_rows = [row for row in reader]
                break
            except Exception:
                continue

        if not raw_rows:
            return pd.DataFrame()

        max_cols = max(len(r) for r in raw_rows)
        padded_rows = [r + [None] * (max_cols - len(r)) for r in raw_rows]
        return pd.DataFrame(padded_rows)

    def parse_file(
        self,
        filepath: Path,
        reporting_year: int,
        reporting_month: int,
        source_org: str = "Central Electricity Authority",
        dataset_name: str = "Broad Overview of Monthly Renewable Energy Generation",
        source_url: str = "https://cea.nic.in/renewable-generation-report/?lang=en",
    ) -> Dict[str, Any]:
        """
        Parses a CEA CSV or XLSX file and returns parsed records, national reconciliation,
        and audit metadata.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Read file as dataframe
        if filepath.suffix.lower() == ".csv":
            df = self._read_csv_robust(filepath)
        elif filepath.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(filepath, header=None)
        else:
            raise CEAParseError(f"Unsupported file format: {filepath.suffix}")

        # 1. Locate header row
        header_row_idx, state_col_idx, fuel_columns = self._detect_headers(df)
        if header_row_idx is None or state_col_idx is None or not fuel_columns:
            raise CEAParseError(
                f"Could not automatically detect valid state and fuel columns in {filepath.name}."
            )

        # 2. Extract state rows and national footer
        raw_state_rows: List[Dict[str, Any]] = []
        national_totals: Dict[str, float] = {}

        for row_idx in range(header_row_idx + 1, len(df)):
            row = df.iloc[row_idx]
            cell_val = row[state_col_idx]
            if pd.isna(cell_val):
                continue

            name_id, category = map_state_name(str(cell_val))

            if category == "NATIONAL_TOTAL":
                for col_idx, fuel_code in fuel_columns.items():
                    val = row[col_idx]
                    if not pd.isna(val):
                        try:
                            clean_val = float(str(val).replace(",", "").strip())
                            national_totals[fuel_code] = clean_val
                        except ValueError:
                            pass
            elif category == "STATE_OR_UT":
                # Valid Indian State / UT row
                state_data = {
                    "state_code": name_id,
                    "state_raw_name": str(cell_val).strip(),
                    "row_idx": row_idx,
                    "fuels": {}
                }
                for col_idx, fuel_code in fuel_columns.items():
                    state_data["fuels"][fuel_code] = row[col_idx]
                raw_state_rows.append(state_data)
            # We ignore REGIONAL_SUBTOTAL rows to prevent double counting

        # 3. Process observations & perform reconciliation
        normalized_records: List[Dict[str, Any]] = []
        reconciliation_by_fuel: Dict[str, ReconciliationResult] = {}
        period_str = f"{reporting_year}-{reporting_month:02d}"

        # Group by fuel stream to reconcile
        for col_idx, fuel_code in fuel_columns.items():
            if fuel_code == "TOTAL_RE":
                continue

            state_fuel_values = []
            for state_row in raw_state_rows:
                state_code = state_row["state_code"]
                raw_fuel_val = state_row["fuels"].get(fuel_code)
                cap_mw = self.capacity_lookup.get((state_code, fuel_code))
                gen_mu, obs_status = audit_observation(
                    raw_fuel_val, state_code, fuel_code, installed_capacity_mw=cap_mw
                )
                state_fuel_values.append({
                    "state_code": state_code,
                    "generation_mu": gen_mu,
                    "observation_status": obs_status,
                })

            # Reconcile this fuel
            reported_total = national_totals.get(fuel_code)
            recon = reconcile_national_total(
                reporting_period=period_str,
                source_code=fuel_code,
                state_values=state_fuel_values,
                published_national_total=reported_total,
            )
            reconciliation_by_fuel[fuel_code] = recon

            # Build normalized records for this fuel
            for item in state_fuel_values:
                normalized_records.append({
                    "state_code": item["state_code"],
                    "source_code": fuel_code,
                    "year": reporting_year,
                    "month": reporting_month,
                    "generation_mu": item["generation_mu"],
                    "target_mu": None,
                    "capacity_utilization_factor_pct": None,
                    "dataset_classification": "OFFICIAL_REPORTED",
                    "observation_status": item["observation_status"],
                    "validation_status": recon.validation_status,
                    "source_org": source_org,
                    "dataset_name": dataset_name,
                    "source_url": source_url,
                    "original_filename": filepath.name,
                    "unit_conversion_applied": "DIRECT_MU",
                })

        return {
            "source_filename": filepath.name,
            "reporting_year": reporting_year,
            "reporting_month": reporting_month,
            "records_count": len(normalized_records),
            "records": normalized_records,
            "reconciliations": {k: v.model_dump() for k, v in reconciliation_by_fuel.items()},
            "national_totals_found": national_totals,
        }

    def _detect_headers(self, df: pd.DataFrame) -> Tuple[Optional[int], Optional[int], Dict[int, str]]:
        """
        Scans top 15 rows of dataframe to locate the table header row,
        identifying the state name column and columns for energy fuels.
        """
        for r_idx in range(min(15, len(df))):
            row = df.iloc[r_idx]
            state_col = None
            fuel_cols: Dict[int, str] = {}

            for c_idx, cell in enumerate(row):
                if pd.isna(cell):
                    continue
                cell_text = str(cell).strip()
                cell_lower = cell_text.lower()

                # Check state column label
                if any(k in cell_lower for k in ["state", "state/ut", "name of state", "states/uts", "region/state"]):
                    state_col = c_idx
                else:
                    mapped_fuel = map_fuel_stream(cell_text)
                    if mapped_fuel:
                        fuel_cols[c_idx] = mapped_fuel

            if state_col is not None and len(fuel_cols) >= 1:
                return r_idx, state_col, fuel_cols

        return None, None, {}
