"""
PDF Table Extractor.
Extracts structured tabular data from official energy PDF publications using pdfplumber.
Handles multi-page tables, header detection, nested columns, and cell sanitation.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pdfplumber


class TableExtractionError(Exception):
    pass


def clean_cell_text(val: Any) -> Optional[str]:
    """Cleans extracted cell string, removing linebreaks and excess spaces."""
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    # Replace multiple internal whitespaces/newlines with single space
    s = re.sub(r"\s+", " ", s)
    return s


def extract_all_tables_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extracts all tables across all pages of a PDF.
    Returns a list of dicts:
      [
        {
          "page_number": int,
          "table_index": int,
          "rows": List[List[Optional[str]]],
          "page_text": str
        },
        ...
      ]
    """
    path = Path(pdf_path)
    extracted_tables: List[Dict[str, Any]] = []

    try:
        with pdfplumber.open(str(path)) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_num = page_idx + 1
                page_text = page.extract_text() or ""
                tables = page.extract_tables() or []

                for t_idx, raw_table in enumerate(tables):
                    cleaned_rows: List[List[Optional[str]]] = []
                    for row in raw_table:
                        cleaned_row = [clean_cell_text(cell) for cell in row]
                        # Discard entirely empty rows
                        if any(c is not None for c in cleaned_row):
                            cleaned_rows.append(cleaned_row)

                    if cleaned_rows:
                        extracted_tables.append({
                            "page_number": page_num,
                            "table_index": t_idx,
                            "rows": cleaned_rows,
                            "page_text": page_text,
                        })
    except Exception as e:
        raise TableExtractionError(f"Failed to extract tables from {path.name}: {str(e)}") from e

    return extracted_tables


def stitch_multipage_tables(tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detects and merges contiguous tables that span across sequential pages.
    """
    if len(tables) <= 1:
        return tables

    stitched: List[Dict[str, Any]] = []
    current_table = tables[0].copy()
    current_last_page = int(str(current_table["page_number"]).split("-")[-1])

    for nxt in tables[1:]:
        nxt_page = int(str(nxt["page_number"]).split("-")[-1])
        # If next table is on the immediately following page and column count matches
        if (
            nxt_page == current_last_page + 1
            and len(nxt["rows"]) > 0
            and len(nxt["rows"][0]) == len(current_table["rows"][0])
        ):
            # Check if first row is a header repeat or data row
            first_row_str = " ".join(c or "" for c in nxt["rows"][0]).lower()
            start_row = 1 if any(k in first_row_str for k in ("state", "region", "category", "s.no", "ownership")) else 0
            current_table["rows"].extend(nxt["rows"][start_row:])
            current_table["page_number"] = f"{current_table['page_number']}-{nxt_page}"
            current_table["page_text"] += "\n" + nxt["page_text"]
            current_last_page = nxt_page
        else:
            stitched.append(current_table)
            current_table = nxt.copy()
            current_last_page = nxt_page

    stitched.append(current_table)
    return stitched

