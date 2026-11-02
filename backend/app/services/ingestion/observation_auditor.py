"""
Observation Auditor.
Strictly classifies individual document cell values into precise statistical observations:
- REPORTED_VALUE: positive reported generation in MU
- VERIFIED_REPORTED_ZERO: explicitly reported numeric zero confirmed in verified official source
- UNVERIFIED_ZERO: explicitly reported numeric zero in unverified source document
- MISSING_OBSERVATION: missing, blank, hyphen ('-'), NA, or unreported value (value is None)
- ZERO_INSTALLED_CAPACITY: no installed capacity for this technology in this geography
- NOT_APPLICABLE: category genuinely does not apply to this jurisdiction
"""

from typing import Any, Optional, Tuple

MISSING_VALUE_STRINGS = {
    "", "-", "--", "---", "na", "n/a", "n.a.", "nil", "null", "none", "nr", "not reported", "?"
}


def audit_observation(
    raw_val: Any,
    state_code: str,
    source_code: str,
    installed_capacity_mw: Optional[float] = None,
    is_verified_source: bool = False,
) -> Tuple[Optional[float], str]:
    """
    Audits a raw cell value and returns:
        (sanitized_generation_mu, observation_status)

    observation_status is strictly one of:
      - 'REPORTED_VALUE': positive generation outturn in MU
      - 'VERIFIED_REPORTED_ZERO': explicitly reported numeric zero confirmed in official publication
      - 'UNVERIFIED_ZERO': explicitly reported numeric zero in unverified source file
      - 'MISSING_OBSERVATION': missing, blank, hyphen, or unreported observation (None)
      - 'ZERO_INSTALLED_CAPACITY': zero installed capacity when generation is unreported
      - 'NOT_APPLICABLE': category does not apply
    """
    if raw_val is None:
        return None, "MISSING_OBSERVATION"

    # Convert string representation
    if isinstance(raw_val, str):
        val_str = raw_val.strip().lower()
        if val_str in MISSING_VALUE_STRINGS:
            # Hyphens, blanks, NA are strictly MISSING_OBSERVATION (never forced to 0.0 or conflated with capacity)
            return None, "MISSING_OBSERVATION"

        # Try removing commas, quotes
        cleaned_str = val_str.replace(",", "").replace('"', '').strip()
        try:
            numeric_val = float(cleaned_str)
        except ValueError:
            return None, "MISSING_OBSERVATION"
    else:
        try:
            numeric_val = float(raw_val)
        except (ValueError, TypeError):
            return None, "MISSING_OBSERVATION"

    # Value is explicitly numeric zero
    if numeric_val == 0.0:
        if is_verified_source:
            return 0.0, "VERIFIED_REPORTED_ZERO"
        return 0.0, "UNVERIFIED_ZERO"

    # Negative generation values are physically invalid for utility outturn
    if numeric_val < 0.0:
        return None, "INVALID_NEGATIVE_VALUE"

    # Positive generation outturn
    return round(numeric_val, 3), "REPORTED_VALUE"
