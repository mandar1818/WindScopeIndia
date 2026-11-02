"""
WindScope India — Indian Electricity Market Timelines & Gate Closure Regression Tests.

Validates:
1. Day-Ahead Market (DAM) gate closure at 12:00 PM (Noon) IST on Day D-1.
2. Green Day-Ahead Market (GDAM) gate closure at 12:00 PM (Noon) IST on Day D-1.
3. Real-Time Market (RTM) gate closure at T - 75 minutes prior to delivery block.
4. Term-Ahead Market (TAM) Intraday gate closure at T - 3 hours prior to delivery block.
5. Strict anti-leakage eligibility validation.
"""
import pytest
from datetime import datetime

from app.services.india_market_rules import (
    IndiaMarketProduct,
    INDIA_MARKET_RULES,
    calculate_india_market_cutoff,
    is_forecast_eligible_under_india_market,
    IST_TZ
)


def test_india_dam_gate_closure_noon_ist():
    """
    Under CERC Power Market Regulations 2021, Regulation 6:
    DAM bidding closes at 12:00 PM (Noon) IST on Day D-1 for delivery on Day D.
    """
    delivery_sp1 = datetime(2026, 1, 15, 0, 0, 0, tzinfo=IST_TZ)
    cutoff = calculate_india_market_cutoff(delivery_sp1, IndiaMarketProduct.DAM)

    assert cutoff == datetime(2026, 1, 14, 12, 0, 0, tzinfo=IST_TZ)
    assert cutoff.hour == 12
    assert cutoff.minute == 0


def test_india_gdam_gate_closure():
    """
    Green Day-Ahead Market aligns with DAM auction window: 12:00 PM IST on D-1.
    """
    delivery_sp48 = datetime(2026, 1, 15, 12, 0, 0, tzinfo=IST_TZ)
    cutoff = calculate_india_market_cutoff(delivery_sp48, IndiaMarketProduct.GDAM)

    assert cutoff == datetime(2026, 1, 14, 12, 0, 0, tzinfo=IST_TZ)


def test_india_rtm_gate_closure_75_minutes():
    """
    Under CERC RTM regulations:
    Gate closure is strictly T - 75 minutes prior to delivery block.
    """
    # Delivery block at 14:00 IST
    delivery_block = datetime(2026, 1, 15, 14, 0, 0, tzinfo=IST_TZ)
    cutoff = calculate_india_market_cutoff(delivery_block, IndiaMarketProduct.RTM)

    # Cutoff must be 12:45 IST (14:00 minus 75 minutes)
    expected_cutoff = datetime(2026, 1, 15, 12, 45, 0, tzinfo=IST_TZ)
    assert cutoff == expected_cutoff


def test_india_tam_intraday_gate_closure_3_hours():
    """
    Term-Ahead Intraday bilateral trading closes 3 hours (180 mins) prior to delivery.
    """
    delivery_block = datetime(2026, 1, 15, 18, 0, 0, tzinfo=IST_TZ)
    cutoff = calculate_india_market_cutoff(delivery_block, IndiaMarketProduct.TAM_INTRADAY)

    expected_cutoff = datetime(2026, 1, 15, 15, 0, 0, tzinfo=IST_TZ)
    assert cutoff == expected_cutoff


def test_forecast_eligibility_leakage_prevention():
    """
    A forecast published after gate closure must be rejected to prevent look-ahead bias.
    """
    delivery = datetime(2026, 1, 15, 10, 0, 0, tzinfo=IST_TZ)

    # Forecast published at 11:30 AM IST on D-1 -> Eligible for DAM (before 12:00 Noon cutoff)
    f_eligible = datetime(2026, 1, 14, 11, 30, 0, tzinfo=IST_TZ)
    assert is_forecast_eligible_under_india_market(f_eligible, delivery, IndiaMarketProduct.DAM) is True

    # Forecast published at 12:15 PM IST on D-1 -> Ineligible for DAM (after 12:00 Noon cutoff)
    f_ineligible = datetime(2026, 1, 14, 12, 15, 0, tzinfo=IST_TZ)
    assert is_forecast_eligible_under_india_market(f_ineligible, delivery, IndiaMarketProduct.DAM) is False


def test_statutory_metadata_completeness():
    """
    Validates that all statutory sources, effective dates, timing milestones, and verification statuses are documented.
    """
    for prod_code in ["DAM", "GDAM", "RTM", "TAM_INTRADAY"]:
        rule = INDIA_MARKET_RULES[prod_code]
        assert "statutory_source" in rule and len(rule["statutory_source"]) > 10
        assert "effective_date" in rule and len(rule["effective_date"]) == 10
        assert "gate_closure_time" in rule
        assert "timing_nature" in rule
        assert "timing_distinction" in rule
        assert "verification_status" in rule
        assert rule["verification_status"] in ["COMPLETED", "PARTIALLY VERIFIED", "UNVERIFIED"]

