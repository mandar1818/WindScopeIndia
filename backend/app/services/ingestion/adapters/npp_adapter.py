"""
NPP Source Adapter.
Handles official National Power Portal (npp.gov.in) publications:
1. All-India Installed Capacity of Power Stations (capacity1-YYYY-MM.pdf)
2. Daily operational bulletins and executive generation summaries
"""
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.services.ingestion.adapters.base import BaseSourceAdapter, ExtractionResult
from app.services.ingestion.pdf_validator import validate_pdf_file


class NPPAdapter(BaseSourceAdapter):
    def __init__(self):
        super().__init__(
            source_org="National Power Portal",
            allowed_domains=["npp.gov.in"]
        )

    def parse_file(self, file_path: Path, reporting_year: int, reporting_month: Optional[int]) -> ExtractionResult:
        if not file_path.exists():
            return ExtractionResult(
                status="FAILED",
                errors=[f"File not found: {file_path}"]
            )

        suffix = file_path.suffix.lower()
        if suffix != ".pdf":
            return ExtractionResult(
                status="FAILED",
                errors=[f"Unsupported NPP format: {suffix}. Only official PDF bulletins supported."]
            )

        val = validate_pdf_file(file_path)
        if not val["is_valid"]:
            return ExtractionResult(
                status="FAILED",
                errors=[f"Invalid PDF: {val.get('error')}"]
            )

        # For capacity reports, parse structured RES breakdown and All-India summary
        import re
        import pdfplumber

        with pdfplumber.open(file_path) as pdf:
            if not pdf.pages:
                return ExtractionResult(status="FAILED", errors=["Empty PDF"])
            text = pdf.pages[0].extract_text() or ""

        # Extract numeric tokens
        all_india_match = re.search(
            r"Total\s+of\s+ALL\s+INDIA\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)",
            text,
            re.IGNORECASE
        )
        res_line_match = re.search(
            r"(?:Waste\s+to\s+Energy|Congen|Cogen)\s*\n\s*([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)",
            text,
            re.IGNORECASE
        )

        if not all_india_match or not res_line_match:
            return ExtractionResult(
                status="FAILED",
                errors=["Failed to parse NPP capacity layout matching canonical table schema."]
            )

        records = [
            {"source_code": "THERMAL", "capacity_mw": float(all_india_match.group(5))},
            {"source_code": "LARGE_HYDRO", "capacity_mw": float(all_india_match.group(6))},
            {"source_code": "NUCLEAR", "capacity_mw": float(all_india_match.group(8))},
            {"source_code": "SMALL_HYDRO", "capacity_mw": float(res_line_match.group(1))},
            {"source_code": "WIND", "capacity_mw": float(res_line_match.group(2))},
            {"source_code": "BIOMASS", "capacity_mw": round(float(res_line_match.group(3)) + float(res_line_match.group(4)), 2)},
            {"source_code": "SOLAR", "capacity_mw": float(res_line_match.group(5))},
        ]

        return ExtractionResult(
            status="SUCCESS",
            extracted_records=records,
            accepted_records_count=len(records),
            validation_summary=f"Successfully extracted {len(records)} fuel-mode capacity benchmarks from {file_path.name}"
        )

