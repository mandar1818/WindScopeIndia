"""
WindScope India — Pytest Configuration & Test Fixtures
"""
import pytest
from datetime import datetime, timezone
from app.services.india_market_rules import IST_TZ

UTC = timezone.utc


@pytest.fixture
def sample_ist_delivery_time() -> datetime:
    """Standard Indian electricity delivery timestamp in IST."""
    return datetime(2026, 1, 15, 14, 0, 0, tzinfo=IST_TZ)
