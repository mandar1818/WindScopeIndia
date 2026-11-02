"""
Grid-India (formerly POSOCO) Source Adapter.
Official Source Domain: grid-india.in

Official Public Data Channels:
1. Daily Power Supply Position (PSP) Reports:
   - Portal: https://grid-india.in/reports/daily-reports/
   - API: https://webapi.grid-india.in/api/v1/file
   - CDN Base: https://webcdn.grid-india.in/
   - Frequency: Daily (Day D published on Day D+1)
   - Scope: All-India and Regional energy met (MU), peak demand met (MW),
     renewable generation (Solar, Wind, Hydro), frequency profile.
   - Access Method: Public HTTPS GET (PDF/Excel bulletins).

2. Real-Time Renewable Energy Management Centre (REMC) 15-Minute Telemetry:
   - Scope: 96 15-minute scheduled vs actual generation, frequency, deviations.
   - Access Method: Enterprise REST / WAMS API.
   - Authentication: Requires NLDC/RLDC enterprise credentials, token exchange, and IP whitelisting.
   - Status: BLOCKED (Requires REMC portal enterprise credentials; cannot be accessed publicly).
"""
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.services.ingestion.adapters.base import BaseSourceAdapter, ExtractionResult
from app.services.ingestion.pdf_validator import validate_pdf_file


class GridIndiaAdapter(BaseSourceAdapter):
    def __init__(self):
        super().__init__(
            source_org="Grid Controller of India Limited (Grid-India)",
            allowed_domains=["grid-india.in", "posoco.in"]
        )

    def parse_file(self, file_path: Path, reporting_year: int = 2024, reporting_month: Optional[int] = None) -> ExtractionResult:
        """
        Parses official Grid-India Daily PSP PDF bulletin:
        Extracts All-India and Regional daily generation (Solar, Wind, Hydro)
        and Energy Met (MU) from Page 2 (Table A: Power Supply Position at All India and Regional level).
        """
        if not file_path.exists():
            return ExtractionResult(
                status="FAILED",
                errors=[f"File not found: {file_path}"]
            )

        suffix = file_path.suffix.lower()
        if suffix != ".pdf":
            return ExtractionResult(
                status="FAILED",
                errors=[f"Unsupported Grid-India document format: {suffix}. Only official PDF PSP reports supported."]
            )

        val = validate_pdf_file(file_path)
        if not val["is_valid"]:
            return ExtractionResult(status="FAILED", errors=[f"Invalid Grid-India PDF: {val.get('error')}"])

        import pdfplumber

        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) < 2:
                return ExtractionResult(status="FAILED", errors=["Invalid Grid-India PSP bulletin: Expected at least 2 pages."])

            # Extract reporting date
            p1_text = pdf.pages[0].extract_text() or ""
            p2_text = pdf.pages[1].extract_text() or ""

            date_match = re.search(r'for the date\s+(\d{1,2}\.\d{1,2}\.\d{4})', p1_text)
            if not date_match:
                date_match = re.search(r'Date\s*:\s*(\d{1,2}\.\d{1,2}\.\d{4})', p1_text)

            if date_match:
                date_str = date_match.group(1)
                report_date = datetime.strptime(date_str, "%d.%m.%Y").date()
            else:
                fn_match = re.search(r'(\d{4})_(\d{2})_(\d{2})', file_path.name)
                if fn_match:
                    report_date = datetime.strptime(f"{fn_match.group(1)}-{fn_match.group(2)}-{fn_match.group(3)}", "%Y-%m-%d").date()
                else:
                    report_date = datetime(reporting_year, reporting_month or 6, 1).date()

            regions = ["NR", "WR", "SR", "ER", "NER", "TOTAL"]
            extracted_records = []

            # Patterns for Page 2 Table A
            fuel_patterns = {
                "HYDRO": r"Hydro Gen\s*\(MU\)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)",
                "WIND": r"Wind Gen\s*\(MU\)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)",
                "SOLAR": r"Solar Gen\s*\(MU\)\*?\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)",
                "ENERGY_MET": r"Energy Met\s*\(MU\)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)"
            }

            for fuel_code, pat in fuel_patterns.items():
                m = re.search(pat, p2_text, re.IGNORECASE)
                if m:
                    vals = m.groups()
                    for reg, val_str in zip(regions, vals):
                        if val_str not in ["-", "--", ""]:
                            try:
                                val = float(val_str)
                                extracted_records.append({
                                    "delivery_date": str(report_date),
                                    "region_code": reg,
                                    "source_code": fuel_code,
                                    "generation_mu": val,
                                    "raw_value": val_str,
                                    "unit": "MU",
                                    "page_number": 2,
                                    "document_name": file_path.name
                                })
                            except ValueError:
                                pass

        if not extracted_records:
            return ExtractionResult(
                status="FAILED",
                errors=["Failed to extract Table A power supply position metrics from Page 2."]
            )

        # Compute reconciliation for Solar, Wind, Hydro
        reconciliation_notes = []
        for fuel_code in ["HYDRO", "WIND", "SOLAR", "ENERGY_MET"]:
            regional_sum = sum(r["generation_mu"] for r in extracted_records if r["source_code"] == fuel_code and r["region_code"] != "TOTAL")
            total_rec = next((r["generation_mu"] for r in extracted_records if r["source_code"] == fuel_code and r["region_code"] == "TOTAL"), None)
            if total_rec is not None:
                diff = abs(round(regional_sum - total_rec, 2))
                reconciliation_notes.append(f"{fuel_code}: Regional Sum={round(regional_sum, 2)}, Reported Total={total_rec}, Diff={diff} MU")

        summary = (
            f"Successfully parsed Grid-India Daily PSP ({file_path.name}) for {report_date}. "
            f"Extracted {len(extracted_records)} observations across regions (NR, WR, SR, ER, NER) and National TOTAL. "
            f"Reconciliation: {'; '.join(reconciliation_notes)}"
        )

        return ExtractionResult(
            status="SUCCESS",
            extracted_records=extracted_records,
            accepted_records_count=len(extracted_records),
            validation_summary=summary
        )

    def fetch_live_15min_telemetry(self) -> Dict[str, Any]:
        """
        Stub for live REMC 15-minute telemetry.
        Honest assessment: Requires NLDC/RLDC enterprise credentials.
        Returns BLOCKED status per project rules.
        """
        return {
            "status": "BLOCKED",
            "reason": "Live Grid-India 15-minute operational telemetry requires enterprise REMC/WAMS credentials, IP whitelisting, and secure VPN access to RLDC dispatch centers. Public endpoints do not expose raw real-time SCADA feeds.",
            "source_authority": "Grid Controller of India Limited",
            "portal_url": "https://grid-india.in/",
            "remedy": "Configure GRID_INDIA_REMC_CLIENT_ID and GRID_INDIA_REMC_CLIENT_SECRET when enterprise access is provisioned."
        }
