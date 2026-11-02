"""
Canonical Indian State and Union Territory Name Mapper.
Converts report state strings, typos, abbreviations, and regional variants
to standard ISO 3166-2:IN geography codes.
"""

import re
from typing import Optional, Tuple

# Mapping of normalized names / regex patterns to ISO codes
CANONICAL_STATE_PATTERNS = [
    # States (28)
    (r"^(andhra(\s+pradesh)?|ap)$", "IN-AP"),
    (r"^(arunachal(\s+pradesh)?|ar)$", "IN-AR"),
    (r"^(assam|as)$", "IN-AS"),
    (r"^(bihar|br)$", "IN-BR"),
    (r"^(chhattisgarh|chhatisgarh|ct|cg)$", "IN-CT"),
    (r"^(goa|ga)$", "IN-GA"),
    (r"^(gujarat|gujrat|gj)$", "IN-GJ"),
    (r"^(haryana|hr)$", "IN-HR"),
    (r"^(himachal(\s+pradesh)?|hp)$", "IN-HP"),
    (r"^(jharkhand|jh)$", "IN-JH"),
    (r"^(karnataka|ka)$", "IN-KA"),
    (r"^(kerala|kl)$", "IN-KL"),
    (r"^(madhya(\s+pradesh)?|mp)$", "IN-MP"),
    (r"^(maharashtra|mah|mh)$", "IN-MH"),
    (r"^(manipur|mn)$", "IN-MN"),
    (r"^(meghalaya|ml)$", "IN-ML"),
    (r"^(mizoram|mz)$", "IN-MZ"),
    (r"^(nagaland|nl)$", "IN-NL"),
    (r"^(odisha|orissa|or|od)$", "IN-OR"),
    (r"^(punjab|pb)$", "IN-PB"),
    (r"^(rajasthan|rj)$", "IN-RJ"),
    (r"^(sikkim|sk)$", "IN-SK"),
    (r"^(tamil\s*nadu|tamilnadu|tn)$", "IN-TN"),
    (r"^(telangana|tg|ts)$", "IN-TG"),
    (r"^(tripura|tr)$", "IN-TR"),
    (r"^(uttar(\s+pradesh)?|up)$", "IN-UP"),
    (r"^(uttarakhand|uttaranchal|ut|uk)$", "IN-UT"),
    (r"^(west\s*bengal|bengal|wb)$", "IN-WB"),

    # Union Territories (8)
    (r"^(andaman(\s*(&|and)\s*nicobar(\s*islands?)?)?|a\s*&\s*n\s*islands?|an)$", "IN-AN"),
    (r"^(chandigarh|ch)$", "IN-CH"),
    (r"^(dadra(\s*(&|and)\s*nagar\s*haveli)?(\s*(&|and)\s*daman\s*(&|and)\s*diu)?|d&nh?\s*(&|and)?\s*dd|daman\s*(&|and)\s*diu|dnh|dh)$", "IN-DH"),
    (r"^(delhi|nct\s*of\s*delhi|dl)$", "IN-DL"),
    (r"^(jammu(\s*(&|and)\s*kashmir)?|j\s*&\s*k|jk)$", "IN-JK"),
    (r"^(ladakh|la)$", "IN-LA"),
    (r"^(lakshadweep|ld)$", "IN-LD"),
    (r"^(puducherry|pondicherry|py)$", "IN-PY"),
]

NATIONAL_TOTAL_PATTERNS = [
    r"^all\s*india$",
    r"^all\s*india\s*total$",
    r"^total\s*all\s*india$",
    r"^national\s*total$",
    r"^grand\s*total$",
    r"^total$",
    r"^total\s*\(re\)$",
    r"^total\s*re$",
    r"^total\s*res$",
    r"^india$",
]

REGIONAL_SUBTOTAL_PATTERNS = [
    (r"^(northern\s*region|nr(\s*total)?)$", "NR"),
    (r"^(western\s*region|wr(\s*total)?)$", "WR"),
    (r"^(southern\s*region|sr(\s*total)?)$", "SR"),
    (r"^(eastern\s*region|er(\s*total)?)$", "ER"),
    (r"^(north\s*eastern\s*region|ner(\s*total)?)$", "NER"),
]


def clean_state_str(raw: str) -> str:
    """Normalizes whitespace, removes footnote numbers, punctuation, asterisks."""
    if not raw:
        return ""
    text = str(raw).strip().lower()
    # Remove footnote markers like *, #, (1), etc.
    text = re.sub(r"[\*\#\^\d+\(\)\[\]]", " ", text)
    # Remove special characters
    text = re.sub(r"[,;:\.]", " ", text)
    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def map_state_name(raw_name: str) -> Tuple[Optional[str], str]:
    """
    Maps a raw state name string from a report to its ISO code or categorization.

    Returns:
        (code_or_identifier, entity_category)
        Where entity_category is one of:
          - 'STATE_OR_UT' -> code is ISO e.g. 'IN-GJ'
          - 'NATIONAL_TOTAL' -> code is 'NATIONAL_TOTAL'
          - 'REGIONAL_SUBTOTAL' -> code is region e.g. 'WR'
          - 'UNKNOWN' -> code is None
    """
    cleaned = clean_state_str(raw_name)
    if not cleaned:
        return None, "UNKNOWN"

    # 1. Check National Totals
    for pat in NATIONAL_TOTAL_PATTERNS:
        if re.search(pat, cleaned):
            return "NATIONAL_TOTAL", "NATIONAL_TOTAL"

    # 2. Check Regional Subtotals
    for pat, reg_code in REGIONAL_SUBTOTAL_PATTERNS:
        if re.search(pat, cleaned):
            return reg_code, "REGIONAL_SUBTOTAL"

    # 3. Check Canonical States & UTs
    for pat, iso_code in CANONICAL_STATE_PATTERNS:
        if re.search(pat, cleaned):
            return iso_code, "STATE_OR_UT"

    return None, "UNKNOWN"

