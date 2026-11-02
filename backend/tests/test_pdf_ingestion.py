import pytest
import tempfile
from pathlib import Path
from pypdf import PdfWriter
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.geography import Geography
from app.models.generation import GenerationMonthly
from app.models.source_file import SourceFile
from app.models.reconciliation import NationalReconciliation
from app.services.ingestion.pdf_downloader import validate_url, DownloadSecurityError, StrictDomainRedirectHandler
from app.services.ingestion.observation_auditor import audit_observation
from app.services.ingestion.pdf_validator import validate_pdf_file, PDFValidationError
from app.services.ingestion.pdf_archival import archive_official_pdf, DuplicateDocumentError, calculate_sha256
from app.services.ingestion.pdf_table_extractor import clean_cell_text, stitch_multipage_tables
from app.services.ingestion.pdf_reconciliation import compute_reconciliation, save_reconciliation_record
from app.services.ingestion.pdf_pipeline import run_pdf_ingestion_pipeline, PDFPipelineError


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_blank_pdf(file_path: Path, pages: int = 1):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    with open(file_path, "wb") as f:
        writer.write(f)


def test_pdf_downloader_domain_validation():
    # Approved domains
    assert validate_url("https://npp.gov.in/public-reports/cea/report.pdf").hostname == "npp.gov.in"
    assert validate_url("https://cea.nic.in/reports/report.pdf").hostname == "cea.nic.in"
    assert validate_url("https://grid-india.in/report.pdf").hostname == "grid-india.in"

    # Blocked unapproved domain
    with pytest.raises(DownloadSecurityError):
        validate_url("https://malicious-domain.com/fake_cea.pdf")

    # Blocked unsupported scheme
    with pytest.raises(DownloadSecurityError):
        validate_url("ftp://npp.gov.in/report.pdf")


def test_pdf_validator_valid_and_invalid(tmp_path):
    # Valid PDF
    valid_pdf = tmp_path / "valid.pdf"
    create_blank_pdf(valid_pdf, pages=2)
    res = validate_pdf_file(valid_pdf)
    assert res["is_valid"] is True
    assert res["page_count"] == 2

    # Invalid header (not a PDF)
    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_text("This is not a PDF file", encoding="utf-8")
    with pytest.raises(PDFValidationError):
        validate_pdf_file(fake_pdf)

    # Empty file
    empty_pdf = tmp_path / "empty.pdf"
    empty_pdf.write_bytes(b"")
    with pytest.raises(PDFValidationError):
        validate_pdf_file(empty_pdf)


def test_pdf_archival_and_deduplication(db_session: Session, tmp_path):
    test_pdf = tmp_path / "test_archival.pdf"
    create_blank_pdf(test_pdf, pages=1)

    # First archival succeeds
    sf = archive_official_pdf(
        db=db_session,
        source_pdf_path=test_pdf,
        reporting_year=2025,
        reporting_month=1,
        source_org="Central Electricity Authority",
        dataset_title="Test Archival PDF",
        source_url="https://npp.gov.in/test.pdf",
        allow_reprocessing=True,
    )
    assert sf.id is not None
    assert sf.document_format == "PDF"
    assert sf.file_hash_sha256 == calculate_sha256(test_pdf)

    # Duplicate without allow_reprocessing raises DuplicateDocumentError
    with pytest.raises(DuplicateDocumentError):
        archive_official_pdf(
            db=db_session,
            source_pdf_path=test_pdf,
            reporting_year=2025,
            reporting_month=1,
            source_org="Central Electricity Authority",
            dataset_title="Test Archival PDF",
            source_url="https://npp.gov.in/test.pdf",
            allow_reprocessing=False,
        )

    # Cleanup test record
    db_session.delete(sf)
    db_session.commit()


def test_clean_cell_text_and_stitch():
    assert clean_cell_text("  Haryana \n State  ") == "Haryana State"
    assert clean_cell_text(None) is None
    assert clean_cell_text("   ") is None

    # Table stitching across sequential pages
    t1 = {
        "page_number": 1,
        "rows": [["State", "Capacity"], ["Haryana", "2500.0"]],
        "page_text": "Page 1 Header",
    }
    t2 = {
        "page_number": 2,
        "rows": [["State", "Capacity"], ["Punjab", "3200.0"]],
        "page_text": "Page 2 Continuation",
    }
    stitched = stitch_multipage_tables([t1, t2])
    assert len(stitched) == 1
    assert stitched[0]["page_number"] == "1-2"
    assert len(stitched[0]["rows"]) == 3  # Header plus 2 state rows


def test_pdf_reconciliation_calculations():
    # Exact match on verified official state observations
    res_verified = compute_reconciliation(
        published_total=1000.0,
        state_sum=1000.0,
        included_states_count=36,
        dataset_classification="VERIFIED_OFFICIAL",
    )
    assert res_verified["reconciliation_status"] == "MATCHES_VERIFIED_STATE_SUM"
    assert res_verified["absolute_variance_mu"] == 0.0
    assert res_verified["percentage_variance"] == 0.0

    # Match on unverified state observations (cannot claim verified match)
    res_unverified = compute_reconciliation(
        published_total=1000.0,
        state_sum=1000.0,
        included_states_count=36,
        dataset_classification="OFFICIAL_SOURCE_UNVERIFIED",
    )
    assert res_unverified["reconciliation_status"] == "UNVERIFIED_STATE_SUM"
    assert res_unverified["percentage_variance"] == 0.0

    # Discrepancy > tolerance
    res_fail = compute_reconciliation(
        published_total=1000.0,
        state_sum=950.0,
        included_states_count=36,
        tolerance_pct=0.05,
    )
    assert res_fail["reconciliation_status"] == "DISCREPANCY_OUTSIDE_TOLERANCE"
    assert res_fail["absolute_variance_mu"] == 50.0
    assert res_fail["percentage_variance"] == 5.0

    # National Total Only (document has only national total, no state breakdown)
    res_national = compute_reconciliation(
        published_total=14212.67,
        state_sum=0.0,
        included_states_count=0,
        is_national_only=True,
    )
    assert res_national["reconciliation_status"] == "NATIONAL_TOTAL_ONLY"
    assert res_national["state_sum_mu"] is None
    assert res_national["absolute_variance_mu"] is None
    assert res_national["percentage_variance"] is None
    assert res_national["mathematical_reconciliation"] == "NOT_APPLICABLE"
    assert res_national["geographic_coverage"] == "NATIONAL_AGGREGATE_ONLY"

    # Incomplete geographic coverage (< 36 states)
    res_incomplete = compute_reconciliation(
        published_total=1000.0,
        state_sum=1000.0,
        included_states_count=30,
        dataset_classification="VERIFIED_OFFICIAL",
    )
    assert res_incomplete["reconciliation_status"] == "INCOMPLETE_GEOGRAPHIC_COVERAGE"

    # Incompatible unit
    res_unit = compute_reconciliation(
        published_total=1000.0,
        state_sum=1000.0,
        included_states_count=36,
        unit_matched=False,
    )
    assert res_unit["reconciliation_status"] == "UNIT_MISMATCH"

    # Incompatible fuel mapping
    res_fuel = compute_reconciliation(
        published_total=1000.0,
        state_sum=1000.0,
        included_states_count=36,
        fuel_matched=False,
    )
    assert res_fuel["reconciliation_status"] == "FUEL_MAPPING_MISMATCH"


def test_pdf_pipeline_provenance_and_isolation(db_session: Session, tmp_path):
    test_pdf = tmp_path / "test_pipeline.pdf"
    create_blank_pdf(test_pdf, pages=1)

    result = run_pdf_ingestion_pipeline(
        db=db_session,
        source_url_or_path=str(test_pdf),
        reporting_year=2025,
        reporting_month=2,
        source_org="Central Electricity Authority",
        dataset_title="Test Pipeline PDF",
        is_remote_url=False,
        allow_reprocessing=True,
    )
    assert result["status"] == "SUCCESS"
    assert "validation_report_path" in result

    # Check that SourceFile record exists
    sf = db_session.query(SourceFile).filter(SourceFile.id == result["source_file_id"]).first()
    assert sf is not None
    assert sf.ingestion_status == "COMPLETED"

    # Cleanup test records completely including reconciliations
    db_session.query(NationalReconciliation).filter(NationalReconciliation.source_file_id == sf.id).delete()
    db_session.query(GenerationMonthly).filter(GenerationMonthly.source_file_id == sf.id).delete()
    db_session.delete(sf)
    db_session.commit()


def test_redirect_handler_blocks_unapproved_destination():
    import urllib.request
    handler = StrictDomainRedirectHandler()
    req = urllib.request.Request("https://npp.gov.in/initial.pdf")
    # Redirecting to an unapproved external domain is blocked
    with pytest.raises(DownloadSecurityError) as exc_info:
        handler.redirect_request(req, None, 302, "Found", {}, "https://evil-server.org/stolen.pdf")
    assert "not in the approved official portals allowlist" in str(exc_info.value)

    # Redirecting to another approved government portal succeeds
    valid_redirect = handler.redirect_request(req, None, 302, "Found", {}, "https://cea.nic.in/gazette.pdf")
    assert valid_redirect.full_url == "https://cea.nic.in/gazette.pdf"


def test_observation_semantics_and_negative_rejection():
    # Negative generation outturn physically rejected
    val_neg, status_neg = audit_observation("-15.0", "IN-GJ", "WIND")
    assert val_neg is None
    assert status_neg == "INVALID_NEGATIVE_VALUE"

    # Explicit numerical zero in unverified source -> UNVERIFIED_ZERO
    val_zero_u, status_zero_u = audit_observation("0.0", "IN-DL", "WIND", is_verified_source=False)
    assert val_zero_u == 0.0
    assert status_zero_u == "UNVERIFIED_ZERO"

    # Explicit numerical zero in verified source -> VERIFIED_REPORTED_ZERO
    val_zero_v, status_zero_v = audit_observation("0.0", "IN-DL", "WIND", is_verified_source=True)
    assert val_zero_v == 0.0
    assert status_zero_v == "VERIFIED_REPORTED_ZERO"

    # Blanks and hyphens are strictly MISSING_OBSERVATION
    for s in ["", "-", "--", "NA", "N/A", "NIL", "NULL"]:
        val_m, status_m = audit_observation(s, "IN-BR", "WIND")
        assert val_m is None
        assert status_m == "MISSING_OBSERVATION"


def test_capacity_pdf_ingestion_engine(db_session: Session):
    from app.services.ingestion.capacity_ingestion import parse_and_ingest_capacity_pdf
    pdf_path = Path("backend/data/raw/cea/2024/2024_06_capacity1-2024-06.pdf")
    if pdf_path.exists():
        res = parse_and_ingest_capacity_pdf(
            db=db_session,
            pdf_path=pdf_path,
            reporting_year=2024,
            reporting_month=6,
            allow_reprocessing=True,
        )
        assert res["status"] == "SUCCESS"
        assert res["records_count"] == 8
        assert res["sha256"] == "c57def4cdb5054d11ab2b9b94333e8ec07ca5e4f80805fef0d9aff7abf8b36ee"



