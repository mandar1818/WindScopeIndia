"""
WindScope India — Phase 2 Final Remediation Script.
Applies all forensic database updates required by Task 1, Task 2, and Task 3:
1. Adds 5 separated dimension columns to national_reconciliations table.
2. Updates national_reconciliations schema to allow NULL for state_sum_mu, absolute_variance_mu, percentage_variance.
3. Corrects below-tolerance reconciliation records (June Solar 1.24%, June Biomass 0.86%, Dec Biomass 1.55%) to UNVERIFIED_STATE_SUM.
4. Corrects NATIONAL_TOTAL_ONLY records (June Hydro, Nuclear, Thermal) to have NULL state_sum, NULL variance, NULL variance_pct.
5. Audits and downgrades all 5,037 demonstration PHYSICAL_ZERO_CONFIRMED records to UNVERIFIED_ZERO.
"""

import sqlite3
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
db_path = backend_dir / "windscope_india.db"

def run_remediation():
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # =========================================================================
    # PART 1: AUDIT & UPDATE OBSERVATION STATUSES IN generation_monthly (TASK 3)
    # =========================================================================
    print("\n--- PART 1: AUDITING OBSERVATION STATUSES (TASK 3) ---")
    cursor.execute("SELECT observation_status, count(*) FROM generation_monthly GROUP BY observation_status")
    before_obs = cursor.fetchall()
    print("Before Observation Status Breakdown:")
    for status, count in before_obs:
        print(f"  {status}: {count}")

    # Downgrade demonstration records from PHYSICAL_ZERO_CONFIRMED to UNVERIFIED_ZERO
    cursor.execute("""
        UPDATE generation_monthly
        SET observation_status = 'UNVERIFIED_ZERO'
        WHERE observation_status = 'PHYSICAL_ZERO_CONFIRMED';
    """)
    downgraded_count = cursor.rowcount
    print(f"Downgraded {downgraded_count} records from 'PHYSICAL_ZERO_CONFIRMED' to 'UNVERIFIED_ZERO'.")

    cursor.execute("SELECT observation_status, count(*) FROM generation_monthly GROUP BY observation_status")
    after_obs = cursor.fetchall()
    print("\nAfter Observation Status Breakdown:")
    for status, count in after_obs:
        print(f"  {status}: {count}")

    # =========================================================================
    # PART 2: NATIONAL RECONCILIATIONS SCHEMA & DIMENSION COLUMNS (TASK 1 & 2)
    # =========================================================================
    print("\n--- PART 2: UPDATING NATIONAL RECONCILIATIONS SCHEMA & COLUMNS (TASK 1 & 2) ---")
    cursor.execute("PRAGMA table_info(national_reconciliations)")
    nr_cols = {col[1] for col in cursor.fetchall()}

    new_nr_cols = [
        ("mathematical_reconciliation", "VARCHAR(50) DEFAULT 'NOT_APPLICABLE'"),
        ("source_verification_status", "VARCHAR(50) DEFAULT 'OFFICIAL_SOURCE_UNVERIFIED'"),
        ("geographic_coverage", "VARCHAR(50) DEFAULT 'NATIONAL_AGGREGATE_ONLY'"),
        ("fuel_mapping_validity", "VARCHAR(50) DEFAULT 'VALID_FUEL_MAPPING'"),
        ("unit_compatibility", "VARCHAR(50) DEFAULT 'COMPATIBLE_UNITS'"),
    ]

    for col_name, col_type in new_nr_cols:
        if col_name not in nr_cols:
            print(f"Adding column '{col_name}' to national_reconciliations...")
            cursor.execute(f"ALTER TABLE national_reconciliations ADD COLUMN {col_name} {col_type}")

    # In SQLite, to modify NOT NULL constraints on state_sum_mu, absolute_variance_mu, percentage_variance,
    # we recreate the table if needed or verify that SQLite allows NULL updates.
    # Note: in SQLite ALTER TABLE, columns without explicit NOT NULL allow NULLs, but if original CREATE TABLE had NOT NULL:
    cursor.execute("PRAGMA table_info(national_reconciliations)")
    table_info = cursor.fetchall()
    # Check if state_sum_mu has notnull=1
    state_sum_notnull = next((col[3] for col in table_info if col[1] == "state_sum_mu"), 0)
    
    if state_sum_notnull == 1:
        print("Recreating national_reconciliations to allow NULL in state_sum_mu, absolute_variance_mu, percentage_variance...")
        cursor.execute("""
            CREATE TABLE national_reconciliations_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file_id INTEGER NOT NULL REFERENCES source_files(id) ON DELETE CASCADE,
                reporting_year INTEGER NOT NULL,
                reporting_month INTEGER NOT NULL,
                source_code VARCHAR(20) NOT NULL REFERENCES energy_sources(source_code),
                published_national_total_mu NUMERIC(12, 3) NOT NULL,
                state_sum_mu NUMERIC(12, 3),
                absolute_variance_mu NUMERIC(12, 3),
                percentage_variance NUMERIC(8, 4),
                included_states_count INTEGER NOT NULL DEFAULT 0,
                missing_states_count INTEGER NOT NULL DEFAULT 0,
                excluded_records_count INTEGER NOT NULL DEFAULT 0,
                reconciliation_status VARCHAR(50) NOT NULL DEFAULT 'NOT_RECONCILED',
                mathematical_reconciliation VARCHAR(50) NOT NULL DEFAULT 'NOT_APPLICABLE',
                source_verification_status VARCHAR(50) NOT NULL DEFAULT 'OFFICIAL_SOURCE_UNVERIFIED',
                geographic_coverage VARCHAR(50) NOT NULL DEFAULT 'NATIONAL_AGGREGATE_ONLY',
                fuel_mapping_validity VARCHAR(50) NOT NULL DEFAULT 'VALID_FUEL_MAPPING',
                unit_compatibility VARCHAR(50) NOT NULL DEFAULT 'COMPATIBLE_UNITS',
                explanation VARCHAR(1000),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            INSERT INTO national_reconciliations_new (
                id, source_file_id, reporting_year, reporting_month, source_code,
                published_national_total_mu, state_sum_mu, absolute_variance_mu, percentage_variance,
                included_states_count, missing_states_count, excluded_records_count,
                reconciliation_status, mathematical_reconciliation, source_verification_status,
                geographic_coverage, fuel_mapping_validity, unit_compatibility,
                explanation, created_at
            )
            SELECT 
                id, source_file_id, reporting_year, reporting_month, source_code,
                published_national_total_mu, state_sum_mu, absolute_variance_mu, percentage_variance,
                included_states_count, missing_states_count, excluded_records_count,
                reconciliation_status,
                COALESCE(mathematical_reconciliation, 'NOT_APPLICABLE'),
                COALESCE(source_verification_status, 'OFFICIAL_SOURCE_UNVERIFIED'),
                COALESCE(geographic_coverage, 'NATIONAL_AGGREGATE_ONLY'),
                COALESCE(fuel_mapping_validity, 'VALID_FUEL_MAPPING'),
                COALESCE(unit_compatibility, 'COMPATIBLE_UNITS'),
                explanation, created_at
            FROM national_reconciliations;
        """)
        cursor.execute("DROP TABLE national_reconciliations;")
        cursor.execute("ALTER TABLE national_reconciliations_new RENAME TO national_reconciliations;")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reconciliation_period ON national_reconciliations(reporting_year, reporting_month);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reconciliation_fuel ON national_reconciliations(source_code, reporting_year, reporting_month);")
        print("Table national_reconciliations successfully recreated with nullable variance columns.")

    # =========================================================================
    # PART 3: UPDATING RECONCILIATION RECORDS WITH ACCURATE DATA (TASK 1 & 2)
    # =========================================================================
    print("\n--- PART 3: UPDATING RECONCILIATION RECORDS (TASK 1 & 2) ---")

    # 1. June 2024 CSV Records
    # Wind (0.00% exact match, unverified source)
    cursor.execute("""
        UPDATE national_reconciliations
        SET 
            reconciliation_status = 'UNVERIFIED_STATE_SUM',
            mathematical_reconciliation = 'EXACT_MATCH',
            source_verification_status = 'OFFICIAL_SOURCE_UNVERIFIED',
            geographic_coverage = 'COMPLETE_36_JURISDICTIONS',
            fuel_mapping_validity = 'VALID_FUEL_MAPPING',
            unit_compatibility = 'COMPATIBLE_UNITS',
            explanation = 'State sum (11,448.50 MU) exactly matches published national footer, but source dataset is unverified CSV (OFFICIAL_SOURCE_UNVERIFIED). Cannot claim verified official status.'
        WHERE reporting_year = 2024 AND reporting_month = 6 AND source_code = 'WIND';
    """)

    # Solar (1.24% variance <= 2.0% tolerance, unverified source)
    cursor.execute("""
        UPDATE national_reconciliations
        SET 
            reconciliation_status = 'UNVERIFIED_STATE_SUM',
            mathematical_reconciliation = 'WITHIN_TOLERANCE',
            source_verification_status = 'OFFICIAL_SOURCE_UNVERIFIED',
            geographic_coverage = 'COMPLETE_36_JURISDICTIONS',
            fuel_mapping_validity = 'VALID_FUEL_MAPPING',
            unit_compatibility = 'COMPATIBLE_UNITS',
            explanation = 'State sum (10,124.60 MU) reconciles with published national footer (10,000.30 MU) within 2.0% statutory tolerance (variance: 1.24%, +124.30 MU), but source dataset is unverified CSV (OFFICIAL_SOURCE_UNVERIFIED). Cannot claim verified official status.'
        WHERE reporting_year = 2024 AND reporting_month = 6 AND source_code = 'SOLAR';
    """)

    # Small Hydro (3.42% variance > 2.0% tolerance)
    cursor.execute("""
        UPDATE national_reconciliations
        SET 
            reconciliation_status = 'DISCREPANCY_OUTSIDE_TOLERANCE',
            mathematical_reconciliation = 'OUTSIDE_TOLERANCE',
            source_verification_status = 'OFFICIAL_SOURCE_UNVERIFIED',
            geographic_coverage = 'COMPLETE_36_JURISDICTIONS',
            fuel_mapping_validity = 'VALID_FUEL_MAPPING',
            unit_compatibility = 'COMPATIBLE_UNITS',
            explanation = 'Sum of states (1,333.50 MU) differs from published total (1,289.40 MU) by 3.42% (+44.10 MU), exceeding statutory tolerance threshold (2.0%).'
        WHERE reporting_year = 2024 AND reporting_month = 6 AND source_code = 'SMALL_HYDRO';
    """)

    # Biomass (0.86% variance <= 2.0% tolerance, unverified source)
    cursor.execute("""
        UPDATE national_reconciliations
        SET 
            reconciliation_status = 'UNVERIFIED_STATE_SUM',
            mathematical_reconciliation = 'WITHIN_TOLERANCE',
            source_verification_status = 'OFFICIAL_SOURCE_UNVERIFIED',
            geographic_coverage = 'COMPLETE_36_JURISDICTIONS',
            fuel_mapping_validity = 'VALID_FUEL_MAPPING',
            unit_compatibility = 'COMPATIBLE_UNITS',
            explanation = 'State sum (1,437.80 MU) reconciles with published national footer (1,450.30 MU) within 2.0% statutory tolerance (variance: 0.86%, -12.50 MU), but source dataset is unverified CSV (OFFICIAL_SOURCE_UNVERIFIED). Cannot claim verified official status.'
        WHERE reporting_year = 2024 AND reporting_month = 6 AND source_code = 'BIOMASS';
    """)

    # Other RE (0.00% exact match, unverified source)
    cursor.execute("""
        UPDATE national_reconciliations
        SET 
            reconciliation_status = 'UNVERIFIED_STATE_SUM',
            mathematical_reconciliation = 'EXACT_MATCH',
            source_verification_status = 'OFFICIAL_SOURCE_UNVERIFIED',
            geographic_coverage = 'COMPLETE_36_JURISDICTIONS',
            fuel_mapping_validity = 'VALID_FUEL_MAPPING',
            unit_compatibility = 'COMPATIBLE_UNITS',
            explanation = 'State sum (114.80 MU) exactly matches published national footer, but source dataset is unverified CSV (OFFICIAL_SOURCE_UNVERIFIED). Cannot claim verified official status.'
        WHERE reporting_year = 2024 AND reporting_month = 6 AND source_code = 'OTHER_RE';
    """)

    # 2. December 2024 CSV Records
    # Wind (0.00% exact match, unverified source)
    cursor.execute("""
        UPDATE national_reconciliations
        SET 
            reconciliation_status = 'UNVERIFIED_STATE_SUM',
            mathematical_reconciliation = 'EXACT_MATCH',
            source_verification_status = 'OFFICIAL_SOURCE_UNVERIFIED',
            geographic_coverage = 'COMPLETE_36_JURISDICTIONS',
            fuel_mapping_validity = 'VALID_FUEL_MAPPING',
            unit_compatibility = 'COMPATIBLE_UNITS',
            explanation = 'State sum (2,106.90 MU) exactly matches published national footer, but source dataset is unverified CSV (OFFICIAL_SOURCE_UNVERIFIED). Cannot claim verified official status.'
        WHERE reporting_year = 2024 AND reporting_month = 12 AND source_code = 'WIND';
    """)

    # Solar (3.80% variance > 2.0% tolerance)
    cursor.execute("""
        UPDATE national_reconciliations
        SET 
            reconciliation_status = 'DISCREPANCY_OUTSIDE_TOLERANCE',
            mathematical_reconciliation = 'OUTSIDE_TOLERANCE',
            source_verification_status = 'OFFICIAL_SOURCE_UNVERIFIED',
            geographic_coverage = 'COMPLETE_36_JURISDICTIONS',
            fuel_mapping_validity = 'VALID_FUEL_MAPPING',
            unit_compatibility = 'COMPATIBLE_UNITS',
            explanation = 'Sum of states (11,391.00 MU) differs from published total (11,840.40 MU) by 3.80% (-449.40 MU), exceeding statutory tolerance threshold (2.0%).'
        WHERE reporting_year = 2024 AND reporting_month = 12 AND source_code = 'SOLAR';
    """)

    # Small Hydro (3.80% variance > 2.0% tolerance)
    cursor.execute("""
        UPDATE national_reconciliations
        SET 
            reconciliation_status = 'DISCREPANCY_OUTSIDE_TOLERANCE',
            mathematical_reconciliation = 'OUTSIDE_TOLERANCE',
            source_verification_status = 'OFFICIAL_SOURCE_UNVERIFIED',
            geographic_coverage = 'COMPLETE_36_JURISDICTIONS',
            fuel_mapping_validity = 'VALID_FUEL_MAPPING',
            unit_compatibility = 'COMPATIBLE_UNITS',
            explanation = 'Sum of states (533.20 MU) differs from published total (513.70 MU) by 3.80% (+19.50 MU), exceeding statutory tolerance threshold (2.0%).'
        WHERE reporting_year = 2024 AND reporting_month = 12 AND source_code = 'SMALL_HYDRO';
    """)

    # Biomass (1.55% variance <= 2.0% tolerance, unverified source)
    cursor.execute("""
        UPDATE national_reconciliations
        SET 
            reconciliation_status = 'UNVERIFIED_STATE_SUM',
            mathematical_reconciliation = 'WITHIN_TOLERANCE',
            source_verification_status = 'OFFICIAL_SOURCE_UNVERIFIED',
            geographic_coverage = 'COMPLETE_36_JURISDICTIONS',
            fuel_mapping_validity = 'VALID_FUEL_MAPPING',
            unit_compatibility = 'COMPATIBLE_UNITS',
            explanation = 'State sum (2,405.50 MU) reconciles with published national footer (2,443.30 MU) within 2.0% statutory tolerance (variance: 1.55%, -37.80 MU), but source dataset is unverified CSV (OFFICIAL_SOURCE_UNVERIFIED). Cannot claim verified official status.'
        WHERE reporting_year = 2024 AND reporting_month = 12 AND source_code = 'BIOMASS';
    """)

    # Other RE (5.41% variance > 2.0% tolerance)
    cursor.execute("""
        UPDATE national_reconciliations
        SET 
            reconciliation_status = 'DISCREPANCY_OUTSIDE_TOLERANCE',
            mathematical_reconciliation = 'OUTSIDE_TOLERANCE',
            source_verification_status = 'OFFICIAL_SOURCE_UNVERIFIED',
            geographic_coverage = 'COMPLETE_36_JURISDICTIONS',
            fuel_mapping_validity = 'VALID_FUEL_MAPPING',
            unit_compatibility = 'COMPATIBLE_UNITS',
            explanation = 'Sum of states (139.90 MU) differs from published total (147.90 MU) by 5.41% (-8.00 MU), exceeding statutory tolerance threshold (2.0%).'
        WHERE reporting_year = 2024 AND reporting_month = 12 AND source_code = 'OTHER_RE';
    """)

    # 3. June 2024 PDF Gazette Records (TASK 2 - NULL semantics for NATIONAL_TOTAL_ONLY)
    # Hydro, Nuclear, Thermal
    for sc in ['HYDRO', 'NUCLEAR', 'THERMAL']:
        cursor.execute(f"""
            UPDATE national_reconciliations
            SET 
                state_sum_mu = NULL,
                absolute_variance_mu = NULL,
                percentage_variance = NULL,
                included_states_count = 0,
                reconciliation_status = 'NATIONAL_TOTAL_ONLY',
                mathematical_reconciliation = 'NOT_APPLICABLE',
                source_verification_status = 'VERIFIED_OFFICIAL',
                geographic_coverage = 'NATIONAL_AGGREGATE_ONLY',
                fuel_mapping_validity = 'VALID_FUEL_MAPPING',
                unit_compatibility = 'COMPATIBLE_UNITS',
                explanation = 'Official publication (CEA Sub-Report 1) contains All-India national aggregate only ({sc}). No state-level observations exist in this statutory source document to reconcile against.'
            WHERE reporting_year = 2024 AND reporting_month = 6 AND source_code = '{sc}';
        """)

    conn.commit()

    # Verify reconciliations table
    print("\n--- FINAL RECONCILIATIONS AUDIT ---")
    cursor.execute("""
        SELECT id, reporting_year, reporting_month, source_code,
               published_national_total_mu, state_sum_mu, absolute_variance_mu, percentage_variance,
               reconciliation_status, mathematical_reconciliation, source_verification_status, geographic_coverage
        FROM national_reconciliations
        ORDER BY reporting_year DESC, reporting_month DESC, source_code
    """)
    rows = cursor.fetchall()
    for r in rows:
        st_sum_str = f"{r[5]:.2f}" if r[5] is not None else "NULL"
        abs_v_str = f"{r[6]:.2f}" if r[6] is not None else "NULL"
        pct_v_str = f"{r[7]:.2f}%" if r[7] is not None else "NULL"
        print(f"ID {r[0]:2d}: {r[1]}-{r[2]:02d} | Fuel={r[3]:<12} | Pub={r[4]:10.2f} | Sum={st_sum_str:>8} | AbsV={abs_v_str:>8} | PctV={pct_v_str:>7} | Status={r[8]:<28} | Math={r[9]:<18} | Source={r[10]:<28} | Geo={r[11]}")

    conn.close()
    print("\nPhase 2 Final Remediation applied successfully.")

if __name__ == "__main__":
    run_remediation()

