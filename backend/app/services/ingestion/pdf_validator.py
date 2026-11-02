"""
PDF Validator.
Validates PDF structure, magic bytes, integrity, page count, and encryption state.
"""

from pathlib import Path
from typing import Dict, Any
import pdfplumber
from pypdf import PdfReader


class PDFValidationError(Exception):
    pass


def validate_pdf_file(file_path: Path) -> Dict[str, Any]:
    """
    Validates a PDF file on disk.
    Checks:
      1. File exists and is non-empty.
      2. PDF magic bytes (%PDF-).
      3. Can be opened by pypdf and pdfplumber without corruption.
      4. Is not encrypted / password protected.
      5. Contains at least one extractable page.
    """
    path = Path(file_path)
    if not path.exists():
        raise PDFValidationError(f"File does not exist: {path}")

    file_size = path.stat().st_size
    if file_size < 100:
        raise PDFValidationError(f"File too small ({file_size} bytes) to be a valid PDF: {path}")

    # Check magic bytes
    with open(path, "rb") as f:
        header = f.read(5)
        if header != b"%PDF-":
            raise PDFValidationError(f"Invalid PDF header: expected b'%PDF-', got {header!r}")

    # Inspect with pypdf
    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            raise PDFValidationError(f"PDF is encrypted or password-protected: {path.name}")
        total_pages = len(reader.pages)
        if total_pages < 1:
            raise PDFValidationError(f"PDF contains no pages: {path.name}")
    except PDFValidationError:
        raise
    except Exception as e:
        raise PDFValidationError(f"Corrupt or unreadable PDF file: {str(e)}") from e

    # Check with pdfplumber
    try:
        with pdfplumber.open(str(path)) as pdf:
            pages_count = len(pdf.pages)
    except Exception as e:
        raise PDFValidationError(f"pdfplumber failed to open PDF: {str(e)}") from e

    return {
        "is_valid": True,
        "page_count": total_pages,
        "file_size_bytes": file_size,
        "filename": path.name,
    }

