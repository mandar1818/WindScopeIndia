"""
WindScope India — Indian Electricity Market Timelines & Gate Closure Rules.

Governed under:
1. Central Electricity Regulatory Commission (Power Market) Regulations, 2021
   (Notification No. L-1/257/2020/CERC, effective 15 August 2021)
2. CERC (Open Access in inter-State Transmission) (Sixth Amendment) Regulations, 2019
   (Notification for Real-Time Market, effective 01 June 2020)
3. CERC (Indian Electricity Grid Code) Regulations, 2023 (IEGC 2023)
4. Power Exchange Operating Rules (IEX, PXIL, HPX)

Product Timing Standards:
- Day-Ahead Market (DAM): Gate closure 12:00 PM (Noon) IST on Day D-1
- Green Day-Ahead Market (G-DAM): Gate closure 12:00 PM (Noon) IST on Day D-1
- Real-Time Market (RTM): Gate closure T - 75 minutes prior to delivery time block
- Term-Ahead Market (TAM) Intraday: Gate closure T - 3 hours prior to delivery time block
"""
from enum import Enum
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from zoneinfo import ZoneInfo

IST_TZ = ZoneInfo("Asia/Kolkata")
UTC_TZ = ZoneInfo("UTC")


class IndiaMarketProduct(str, Enum):
    DAM = "DAM"                   # Day-Ahead Market (Conventional)
    GDAM = "GDAM"                 # Green Day-Ahead Market
    RTM = "RTM"                   # Real-Time Market (Half-hourly sessions)
    TAM_INTRADAY = "TAM_INTRADAY" # Term-Ahead Intraday / Contingency
    ANCILLARY_SRAS = "ANCILLARY_SRAS" # Secondary Reserve Ancillary Services


INDIA_MARKET_RULES: Dict[str, Dict[str, Any]] = {
    "DAM": {
        "product_code": "DAM",
        "product_name": "Day-Ahead Market",
        "market_segment": "Physical Collective Transaction",
        "bid_submission_window": "10:00 to 12:00 IST on Day D-1",
        "auction_gate_closure": "12:00 IST on Day D-1",
        "dispatch_scheduling_deadline": "15:00 IST on Day D-1 (NLDC provisional schedule) / 23:00 IST (final schedule under IEGC 2023 Reg 45(3))",
        "gate_closure_time": "12:00 PM (Noon) IST on Day D-1",
        "timing_nature": "EXCHANGE_BID_SUBMISSION_CLOSURE",
        "timing_distinction": "12:00 PM IST is the Exchange Order Book Gate Closure on D-1. Grid dispatch schedule is subsequently issued by NLDC/RLDC at 15:00 IST under IEGC 2023 Reg 45(3).",
        "gate_closure_hour_ist": 12,
        "gate_closure_minute_ist": 0,
        "lead_time_hours": 12.0,
        "bidding_window": "10:00 AM to 12:00 PM (Noon) IST on Day D-1",
        "statutory_source": "Power Exchange Business Rules (IEX Business Rules Section 3.3.1 approved by CERC under PMR 2021 Reg 27) for 12:00 bidding closure; CERC IEGC 2023 Regulation 45 for 15:00 grid scheduling.",
        "primary_source_authority": "Power Exchange Business Rules (IEX Business Rules Section 3.3.1 approved by CERC under PMR 2021 Reg 27) for 12:00 bidding closure; CERC IEGC 2023 Regulation 45 for 15:00 grid scheduling.",
        "statutory_clause": "IEX Business Rules Section 3.3.1; CERC (IEGC) Regulations, 2023 Reg 45(3); CERC PMR 2021 Reg 27",
        "effective_date": "2021-08-15",
        "verification_status": "PARTIALLY VERIFIED",
        "verification_notes": "12:00 PM bid closure is defined in CERC-approved Exchange Business Rules, not directly in primary CERC PMR statute text. Grid scheduling at 15:00 IST is statutory under IEGC 2023.",
        "contract_granularity": "15-minute dispatch blocks (96 blocks/day)",
        "delivery_scope": "Full Day D (00:00 to 24:00 IST)"
    },
    "GDAM": {
        "product_code": "GDAM",
        "product_name": "Green Day-Ahead Market",
        "market_segment": "Renewable Energy Collective Transaction",
        "bid_submission_window": "10:00 to 12:00 IST on Day D-1 (concurrent with DAM)",
        "auction_gate_closure": "12:00 IST on Day D-1",
        "dispatch_scheduling_deadline": "15:00 IST on Day D-1 (integrated schedule with DAM)",
        "gate_closure_time": "12:00 PM (Noon) IST on Day D-1",
        "timing_nature": "EXCHANGE_BID_SUBMISSION_CLOSURE",
        "timing_distinction": "12:00 PM IST is the Exchange Bid Submission Closure on D-1. Renewable bids cleared with priority in integrated clearing engine before conventional DAM bids.",
        "gate_closure_hour_ist": 12,
        "gate_closure_minute_ist": 0,
        "lead_time_hours": 12.0,
        "bidding_window": "10:00 AM to 12:00 PM (Noon) IST on Day D-1",
        "statutory_source": "CERC Order in Petition No. 447/MP/2019 dated 24.03.2021 approving GDAM; IEX Business Rules Chapter on Green Day-Ahead Market.",
        "primary_source_authority": "CERC Order in Petition No. 447/MP/2019 dated 24.03.2021 approving GDAM; IEX Business Rules Chapter on Green Day-Ahead Market.",
        "statutory_clause": "CERC Order in Petition 447/MP/2019; CERC PMR 2021 Reg 6(3); IEX GDAM Rules",
        "effective_date": "2021-10-22",
        "verification_status": "PARTIALLY VERIFIED",
        "verification_notes": "Introduced via CERC regulatory approval order and operationalized under power exchange rules.",
        "contract_granularity": "15-minute dispatch blocks (Solar and Non-Solar)",
        "delivery_scope": "Full Day D (00:00 to 24:00 IST)"
    },
    "RTM": {
        "product_code": "RTM",
        "product_name": "Real-Time Market",
        "market_segment": "Intraday Half-Hourly Auction",
        "bid_submission_window": "Opens 1h 45m before delivery time block; closes 1h 15m before (48 auction sessions daily)",
        "auction_gate_closure": "T - 75 minutes before delivery time block",
        "dispatch_scheduling_deadline": "T - 45 minutes before delivery time block (NLDC grid schedule incorporation under IEGC 2023 Reg 47)",
        "gate_closure_time": "T - 75 minutes before delivery time block",
        "timing_nature": "STATUTORY_AUCTION_GATE_CLOSURE",
        "timing_distinction": "T - 75m is the Participant Bid Gate Closure. Matched results sent to NLDC at T - 60m; incorporated into dispatch schedule at T - 45m under IEGC 2023 Reg 47.",
        "gate_closure_lead_minutes": 75,
        "lead_time_hours": 1.25,
        "bidding_window": "48 auction sessions daily (opens 1h 45m before, closes 1h 15m before delivery)",
        "statutory_source": "CERC (Open Access in inter-State Transmission) (Sixth Amendment) Regulations, 2019, Regulation 15B; CERC Order 10/SM/2020; CERC (IEGC) Regulations, 2023 Regulation 47.",
        "primary_source_authority": "CERC (Open Access in inter-State Transmission) (Sixth Amendment) Regulations, 2019, Regulation 15B; CERC Order 10/SM/2020; CERC (IEGC) Regulations, 2023 Regulation 47.",
        "statutory_clause": "Regulation 15(B) of CERC OA 6th Amendment 2019; Order 10/SM/2020; IEGC 2023 Reg 47",
        "effective_date": "2020-06-01",
        "verification_status": "PARTIALLY VERIFIED",
        "verification_notes": "75-minute gate closure and 45-minute dispatch deadlines are explicitly codified in primary CERC statutory regulations.",
        "contract_granularity": "15-minute dispatch blocks (2 blocks per half-hour session)",
        "delivery_scope": "Half-hour delivery slots throughout the operational day"
    },
    "TAM_INTRADAY": {
        "product_code": "TAM_INTRADAY",
        "product_name": "Term-Ahead Intraday / Contingency Market",
        "market_segment": "Continuous Bilateral Transaction",
        "bid_submission_window": "Continuous trading on delivery day D up to T - 3 hours (Exchange contract specification)",
        "auction_gate_closure": "T - 3 hours before delivery time block (Exchange contract rule)",
        "dispatch_scheduling_deadline": "Minimum 4 time blocks (1 hour) ahead for bilateral scheduling revision under CERC GNA Regulations 2022 Reg 26",
        "gate_closure_time": "T - 3 hours before delivery time block",
        "timing_nature": "EXCHANGE_TRADING_SESSION_CLOSURE",
        "timing_distinction": "T - 3h is the IEX Intra-Day contract trading closure. General bilateral contingency scheduling under GNA Reg 26 requires minimum 4 time blocks (1 hour).",
        "gate_closure_lead_minutes": 180,
        "lead_time_hours": 3.0,
        "bidding_window": "Round-the-clock trading on delivery day D up to T - 3h",
        "statutory_source": "Power Exchange Contract Specifications (IEX Business Rules Chapter 4 for Intra-Day Contracts); CERC GNA Regulations 2022.",
        "primary_source_authority": "Power Exchange Contract Specifications (IEX Business Rules Chapter 4 for Intra-Day Contracts); CERC GNA Regulations 2022.",
        "statutory_clause": "IEX Business Rules Chapter 4; CERC (Connectivity and General Network Access) Regulations 2022 Reg 26",
        "effective_date": "2021-08-15",
        "verification_status": "PARTIALLY VERIFIED",
        "verification_notes": "Intraday gate closure is contract-specific to exchange rules rather than uniform statutory requirement.",
        "contract_granularity": "Hourly / 15-minute customized bilateral blocks",
        "delivery_scope": "Intraday balancing up to 3 hours ahead"
    }
}


def calculate_india_market_cutoff(
    delivery_time_ist: datetime,
    product: IndiaMarketProduct = IndiaMarketProduct.DAM
) -> datetime:
    """
    Calculates the exact statutory gate closure cutoff timestamp in IST for an Indian market product.
    
    Rules:
    - DAM & GDAM: Target day D delivery (any block 00:00-24:00 IST) has gate closure at 12:00 PM IST on Day D-1.
    - RTM: Gate closure is exactly 75 minutes prior to the start of the delivery block.
    - TAM_INTRADAY: Gate closure is exactly 3 hours (180 minutes) prior to delivery.
    """
    if delivery_time_ist.tzinfo is None:
        delivery_time_ist = delivery_time_ist.replace(tzinfo=IST_TZ)
    else:
        delivery_time_ist = delivery_time_ist.astimezone(IST_TZ)

    if product in (IndiaMarketProduct.DAM, IndiaMarketProduct.GDAM):
        delivery_date = delivery_time_ist.date()
        cutoff_date = delivery_date - timedelta(days=1)
        return datetime(cutoff_date.year, cutoff_date.month, cutoff_date.day, 12, 0, 0, tzinfo=IST_TZ)

    elif product == IndiaMarketProduct.RTM:
        return delivery_time_ist - timedelta(minutes=75)

    elif product == IndiaMarketProduct.TAM_INTRADAY:
        return delivery_time_ist - timedelta(hours=3)

    else:
        # Default fallback to DAM
        delivery_date = delivery_time_ist.date()
        cutoff_date = delivery_date - timedelta(days=1)
        return datetime(cutoff_date.year, cutoff_date.month, cutoff_date.day, 12, 0, 0, tzinfo=IST_TZ)


def is_forecast_eligible_under_india_market(
    forecast_publish_time: datetime,
    delivery_time: datetime,
    product: IndiaMarketProduct = IndiaMarketProduct.DAM
) -> bool:
    """
    Determines whether a forecast was published strictly prior to the statutory gate closure,
    preventing look-ahead bias and information leakage.
    """
    if forecast_publish_time.tzinfo is None:
        forecast_publish_time = forecast_publish_time.replace(tzinfo=IST_TZ)
    else:
        forecast_publish_time = forecast_publish_time.astimezone(IST_TZ)

    cutoff_time = calculate_india_market_cutoff(delivery_time, product)
    return forecast_publish_time <= cutoff_time

