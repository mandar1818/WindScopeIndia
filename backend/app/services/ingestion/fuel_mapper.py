"""
Canonical Fuel Stream Mapper.
Maps column headers and fuel names from CEA, NPP, and Grid-India reports
to standard WindScope energy source codes.
"""

import re
from typing import Optional

FUEL_PATTERNS = [
    # Wind Power
    (r"^(wind(\s*(power|energy|gen|generation))?|wtg)$", "WIND"),

    # Solar Power
    (r"^(solar(\s*(power|pv|photovoltaic|energy|gen|generation))?|ground\s*mounted\s*solar|rooftop\s*solar)$", "SOLAR"),

    # Large Hydro (>25 MW)
    (r"^(large\s*hydro|hydro\s*\(?>\s*25\s*mw\)?|hydro\s*\(?above\s*25\s*mw\)?|conventional\s*hydro|hydro)$", "LARGE_HYDRO"),

    # Small Hydro (<=25 MW)
    (r"^(small\s*hydro(\s*power)?|shp|hydro\s*\(?<=\s*25\s*mw\)?|hydro\s*\(?up\s*to\s*25\s*mw\)?|mini\s*hydro|micro\s*hydro)$", "SMALL_HYDRO"),

    # Biomass / Bagasse Cogeneration
    (r"^(biomass(\s*(power|energy|cogen|cogeneration))?|bagasse(\s*(cogen|cogeneration))?|bio\s*power|agro\s*residue)$", "BIOMASS"),

    # Waste to Energy / Other RE
    (r"^(waste\s*to\s*energy|wte|other\s*re|other\s*res|others|hybrid)$", "OTHER_RE"),

    # Summary Totals
    (r"^(total(\s*(re|res|renewable|renewables|gen|generation))?|all\s*sources)$", "TOTAL_RE"),
]


def clean_fuel_str(raw: str) -> str:
    """Normalizes fuel string."""
    if not raw:
        return ""
    text = str(raw).strip().lower()
    text = re.sub(r"[\*\#\^\d+\(\)\[\]]", " ", text)
    text = re.sub(r"[,;:\.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def map_fuel_stream(raw_fuel: str) -> Optional[str]:
    """
    Maps raw fuel text to canonical fuel source_code or 'TOTAL_RE'.
    Returns None if unrecognized.
    """
    cleaned = clean_fuel_str(raw_fuel)
    if not cleaned:
        return None

    # Check against regex patterns
    for pat, code in FUEL_PATTERNS:
        if re.search(pat, cleaned):
            return code

    return None

