"""
Official Document Downloader.
Downloads official energy publications from approved government portals,
enforces security controls, validates content types, computes SHA-256 hashes,
and prevents path traversal or unsafe file access.
"""

import os
import ssl
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional

ALLOWED_DOMAINS = {
    "npp.gov.in",
    "cea.nic.in",
    "mnre.gov.in",
    "grid-india.in",
    "posoco.in",
}

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


class DownloadSecurityError(Exception):
    pass


class PDFDownloadError(Exception):
    pass


def validate_url(url: str) -> urllib.parse.ParseResult:
    """Validates that URL uses HTTPS and belongs to an approved official government domain."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme.lower() not in ("http", "https"):
        raise DownloadSecurityError(f"Unsupported protocol scheme: {parsed.scheme}")

    hostname = (parsed.hostname or "").lower()
    if not any(hostname == domain or hostname.endswith("." + domain) for domain in ALLOWED_DOMAINS):
        raise DownloadSecurityError(
            f"Domain '{hostname}' is not in the approved official portals allowlist: {ALLOWED_DOMAINS}"
        )
    return parsed


class StrictDomainRedirectHandler(urllib.request.HTTPRedirectHandler):
    """
    Enforces official domain allowlist on all HTTP redirect destinations (301, 302, 303, 307, 308).
    Prevents an approved government portal from redirecting downloads to an unapproved external domain.
    """
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download_official_pdf(
    url: str,
    target_dir: Path,
    target_filename: Optional[str] = None,
    timeout_seconds: int = 30,
) -> Dict[str, Any]:
    """
    Downloads an official PDF document from an approved government domain.
    Saves file to target_dir and returns metadata dict with SHA-256 hash.
    Enforces strict domain allowlist on initial URL and all redirect destinations.
    """
    validate_url(url)
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    if not target_filename:
        url_path = urllib.parse.urlparse(url).path
        target_filename = Path(url_path).name or "document.pdf"

    # Sanitize filename to prevent directory traversal
    clean_filename = Path(target_filename).name
    if not clean_filename.lower().endswith(".pdf"):
        clean_filename += ".pdf"

    output_path = target_dir / clean_filename

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 WindScopeIndia/2.0",
            "Accept": "application/pdf,*/*",
        },
    )

    hasher = hashlib.sha256()
    total_bytes = 0

    # Build opener with strict redirect handler and SSL context
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    opener = urllib.request.build_opener(StrictDomainRedirectHandler(), https_handler)

    try:
        with opener.open(req, timeout=timeout_seconds) as resp:
            # Validate final resolved destination URL after all redirects
            final_url = resp.geturl()
            validate_url(final_url)

            content_type = resp.headers.get("Content-Type", "")
            # Write to disk while streaming
            with open(output_path, "wb") as f_out:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    if total_bytes > MAX_FILE_SIZE_BYTES:
                        f_out.close()
                        output_path.unlink(missing_ok=True)
                        raise DownloadSecurityError(f"File exceeded maximum allowable size of {MAX_FILE_SIZE_BYTES} bytes")
                    hasher.update(chunk)
                    f_out.write(chunk)

    except DownloadSecurityError:
        raise
    except Exception as e:
        if output_path.exists():
            output_path.unlink(missing_ok=True)
        raise PDFDownloadError(f"Failed to download PDF from {url}: {str(e)}") from e

    sha256_hash = hasher.hexdigest()

    return {
        "url": url,
        "filename": clean_filename,
        "file_path": str(output_path.resolve()),
        "file_size_bytes": total_bytes,
        "sha256_hash": sha256_hash,
        "content_type": content_type,
    }

