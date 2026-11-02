"""
National Sum Reconciliation Engine.
Calculates variance between published national totals and state-wise aggregated sums.
Never forces or artificially scales state numbers to match national totals.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ReconciliationResult(BaseModel):
    reporting_period: str
    source_code: str
    reported_national_total_mu: Optional[float]
    sum_of_states_mu: Optional[float] = None
    discrepancy_mu: Optional[float] = None
    discrepancy_pct: Optional[float] = None
    validation_status: str
    mathematical_reconciliation: str = "NOT_APPLICABLE"
    source_verification_status: str = "OFFICIAL_SOURCE_UNVERIFIED"
    geographic_coverage: str = "NATIONAL_AGGREGATE_ONLY"
    fuel_mapping_validity: str = "VALID_FUEL_MAPPING"
    unit_compatibility: str = "COMPATIBLE_UNITS"
    states_counted: int
    missing_count: int
    zero_count: int
    notes: str


def reconcile_national_total(
    reporting_period: str,
    source_code: str,
    state_values: List[Dict[str, Any]],
    published_national_total: Optional[float] = None,
    tolerance_pct: float = 2.0,
    dataset_classification: str = "OFFICIAL_SOURCE_UNVERIFIED",
    is_national_only: bool = False,
    fuel_matched: bool = True,
    unit_matched: bool = True,
) -> ReconciliationResult:
    """
    Performs audit comparison between published national total and sum of state observations.
    Never marks unverified or demonstration state records as MATCHES_VERIFIED_STATE_SUM.
    Separates mathematical variance from source verification and geographic coverage.
    """
    valid_values = [v["generation_mu"] for v in state_values if v.get("generation_mu") is not None]
    missing_count = sum(1 for v in state_values if v.get("generation_mu") is None)
    zero_count = sum(1 for v in valid_values if v == 0.0)
    sum_states = round(sum(valid_values), 3)

    # 1. National Aggregate Only (no state-level observations exist in publication)
    if is_national_only or (len(valid_values) == 0 and published_national_total is not None and published_national_total > 0):
        return ReconciliationResult(
            reporting_period=reporting_period,
            source_code=source_code,
            reported_national_total_mu=round(published_national_total, 3),
            sum_of_states_mu=None,
            discrepancy_mu=None,
            discrepancy_pct=None,
            validation_status="NATIONAL_TOTAL_ONLY",
            mathematical_reconciliation="NOT_APPLICABLE",
            source_verification_status=dataset_classification,
            geographic_coverage="NATIONAL_AGGREGATE_ONLY",
            fuel_mapping_validity="VALID_FUEL_MAPPING" if fuel_matched else "MISMATCH",
            unit_compatibility="COMPATIBLE_UNITS" if unit_matched else "MISMATCH",
            states_counted=0,
            missing_count=missing_count,
            zero_count=zero_count,
            notes="Source document provides All-India national aggregate only. No state-level observations exist in this document to reconcile against.",
        )

    if not unit_matched:
        return ReconciliationResult(
            reporting_period=reporting_period,
            source_code=source_code,
            reported_national_total_mu=round(published_national_total, 3) if published_national_total else None,
            sum_of_states_mu=sum_states,
            discrepancy_mu=round(published_national_total - sum_states, 3) if published_national_total else None,
            discrepancy_pct=None,
            validation_status="UNIT_MISMATCH",
            mathematical_reconciliation="INCOMPATIBLE_UNITS",
            source_verification_status=dataset_classification,
            geographic_coverage="PARTIAL_COVERAGE" if len(valid_values) < 36 else "COMPLETE_36_JURISDICTIONS",
            fuel_mapping_validity="VALID_FUEL_MAPPING" if fuel_matched else "MISMATCH",
            unit_compatibility="MISMATCH",
            states_counted=len(valid_values),
            missing_count=missing_count,
            zero_count=zero_count,
            notes="Unit mismatch between state observations and national published total.",
        )

    if not fuel_matched:
        return ReconciliationResult(
            reporting_period=reporting_period,
            source_code=source_code,
            reported_national_total_mu=round(published_national_total, 3) if published_national_total else None,
            sum_of_states_mu=sum_states,
            discrepancy_mu=round(published_national_total - sum_states, 3) if published_national_total else None,
            discrepancy_pct=None,
            validation_status="FUEL_MAPPING_MISMATCH",
            mathematical_reconciliation="INCOMPATIBLE_FUELS",
            source_verification_status=dataset_classification,
            geographic_coverage="PARTIAL_COVERAGE" if len(valid_values) < 36 else "COMPLETE_36_JURISDICTIONS",
            fuel_mapping_validity="MISMATCH",
            unit_compatibility="COMPATIBLE_UNITS",
            states_counted=len(valid_values),
            missing_count=missing_count,
            zero_count=zero_count,
            notes="Fuel mapping category mismatch between state observations and national total.",
        )

    if published_national_total is None or published_national_total <= 0:
        return ReconciliationResult(
            reporting_period=reporting_period,
            source_code=source_code,
            reported_national_total_mu=published_national_total,
            sum_of_states_mu=sum_states,
            discrepancy_mu=None,
            discrepancy_pct=None,
            validation_status="NATIONAL_TOTAL_ONLY",
            mathematical_reconciliation="NOT_APPLICABLE",
            source_verification_status=dataset_classification,
            geographic_coverage="PARTIAL_COVERAGE" if len(valid_values) < 36 else "COMPLETE_36_JURISDICTIONS",
            fuel_mapping_validity="VALID_FUEL_MAPPING",
            unit_compatibility="COMPATIBLE_UNITS",
            states_counted=len(valid_values),
            missing_count=missing_count,
            zero_count=zero_count,
            notes="No official national total column published in source file for comparison."
        )

    discrepancy_mu = round(published_national_total - sum_states, 3)
    discrepancy_pct = round((abs(discrepancy_mu) / published_national_total) * 100.0, 2)

    coverage_status = "COMPLETE_36_JURISDICTIONS" if len(valid_values) >= 36 else "PARTIAL_COVERAGE"

    if discrepancy_pct == 0.0:
        math_recon = "EXACT_MATCH"
    elif discrepancy_pct <= tolerance_pct:
        math_recon = "WITHIN_TOLERANCE"
    else:
        math_recon = "OUTSIDE_TOLERANCE"

    # Strict status evaluation
    if discrepancy_pct > tolerance_pct:
        status = "DISCREPANCY_OUTSIDE_TOLERANCE"
        notes = (
            f"Sum of states ({sum_states:.2f} MU) differs from published total ({published_national_total:.2f} MU) "
            f"by {discrepancy_pct}% ({discrepancy_mu:+.2f} MU), exceeding the {tolerance_pct}% audit threshold."
        )
    elif dataset_classification != "VERIFIED_OFFICIAL":
        status = "UNVERIFIED_STATE_SUM"
        if discrepancy_pct == 0.0:
            notes = (
                f"State sum ({sum_states:.2f} MU) exactly matches published national footer, "
                f"but source dataset is unverified ({dataset_classification}). Cannot claim verified official status."
            )
        else:
            notes = (
                f"State sum ({sum_states:.2f} MU) reconciles with published national footer ({published_national_total:.2f} MU) "
                f"within {tolerance_pct}% tolerance (variance: {discrepancy_pct:.2f}%, {discrepancy_mu:+.2f} MU), "
                f"but source dataset is unverified ({dataset_classification}). Cannot claim verified official status."
            )
    elif len(valid_values) < 36:
        status = "INCOMPLETE_GEOGRAPHIC_COVERAGE"
        notes = f"Verified state observations cover only {len(valid_values)} of 36 jurisdictions (variance: {discrepancy_pct:.2f}%)."
    else:
        status = "MATCHES_VERIFIED_STATE_SUM"
        notes = f"Sum of independently verified official state observations matches published national total (variance: {discrepancy_pct:.2f}%)."

    return ReconciliationResult(
        reporting_period=reporting_period,
        source_code=source_code,
        reported_national_total_mu=round(published_national_total, 3),
        sum_of_states_mu=sum_states,
        discrepancy_mu=discrepancy_mu,
        discrepancy_pct=discrepancy_pct,
        validation_status=status,
        mathematical_reconciliation=math_recon,
        source_verification_status=dataset_classification,
        geographic_coverage=coverage_status,
        fuel_mapping_validity="VALID_FUEL_MAPPING",
        unit_compatibility="COMPATIBLE_UNITS",
        states_counted=len(valid_values),
        missing_count=missing_count,
        zero_count=zero_count,
        notes=notes,
    )

