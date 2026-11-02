"""
CEA Source Adapter.
Handles official Central Electricity Authority (cea.nic.in) publications:
1. OPM Sub-Report 1 & 16 Conventional & Hydro generation (PDF)
2. REMD Monthly RE extractions (CSV/XLSX)
"""
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.services.ingestion.adapters.base import BaseSourceAdapter, ExtractionResult
from app.services.ingestion.pdf_validator import validate_pdf_file
from app.services.ingestion.pdf_table_extractor import extract_all_tables_from_pdf
from app.services.ingestion.parser_cea import CEAParser


class CEAAdapter(BaseSourceAdapter):
    def __init__(self):
        super().__init__(
            source_org="Central Electricity Authority",
            allowed_domains=["cea.nic.in", "gen-re.cea.gov.in"]
        )

    def parse_file(self, file_path: Path, reporting_year: int, reporting_month: Optional[int]) -> ExtractionResult:
        if not file_path.exists():
            return ExtractionResult(
                status="FAILED",
                errors=[f"File not found: {file_path}"]
            )

        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            # PDF parsing via pdfplumber
            val = validate_pdf_file(file_path)
            if not val["is_valid"]:
                return ExtractionResult(
                    status="FAILED",
                    errors=[f"Invalid PDF: {val.get('error')}"]
                )

            extracted = extract_all_tables_from_pdf(file_path)
            if not extracted:
                return ExtractionResult(
                    status="PARTIAL",
                    validation_summary=f"Parsed PDF {file_path.name} with 0 records extracted"
                )

            return ExtractionResult(
                status="SUCCESS",
                extracted_records=extracted,
                accepted_records_count=len(extracted),
                validation_summary=f"Successfully extracted {len(extracted)} station observations from Sub-Report 16"
            )

        elif suffix in (".csv", ".xlsx", ".xls"):
            parser = CEAParser()
            parsed_data = parser.parse_file(file_path, reporting_year, reporting_month or 1)
            records = parsed_data.get("records", [])
            errors = parsed_data.get("errors", [])
            status = "SUCCESS" if records and not errors else ("PARTIAL" if records else "FAILED")
            return ExtractionResult(
                status=status,
                extracted_records=records,
                accepted_records_count=len(records),
                rejected_records_count=len(errors),
                errors=errors,
                validation_summary=f"Extracted {len(records)} records from CEA REMD CSV ({len(errors)} rejected)"
            )

        else:
            return ExtractionResult(
                status="FAILED",
                errors=[f"Unsupported CEA format: {suffix}. Supported: PDF, CSV, XLSX"]
            )
