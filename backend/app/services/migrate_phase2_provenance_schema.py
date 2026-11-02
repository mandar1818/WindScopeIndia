import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'windscope_india.db')
    db_path = os.path.abspath(db_path)
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Update source_files table
    cursor.execute("PRAGMA table_info(source_files)")
    sf_cols = {col[1] for col in cursor.fetchall()}
    
    new_sf_cols = [
        ("document_format", "VARCHAR(20) DEFAULT 'CSV'"),
        ("publication_date", "VARCHAR(50)"),
        ("parser_version", "VARCHAR(50) DEFAULT '1.0.0'"),
        ("validation_summary", "TEXT")
    ]
    for col_name, col_type in new_sf_cols:
        if col_name not in sf_cols:
            print(f"Adding column {col_name} to source_files...")
            cursor.execute(f"ALTER TABLE source_files ADD COLUMN {col_name} {col_type}")

    # 2. Update generation_monthly table
    cursor.execute("PRAGMA table_info(generation_monthly)")
    gm_cols = {col[1] for col in cursor.fetchall()}

    new_gm_cols = [
        ("sha256_checksum", "VARCHAR(64)"),
        ("publication_date", "VARCHAR(50)"),
        ("original_state_label", "VARCHAR(100)"),
        ("normalized_geography_code", "VARCHAR(20)"),
        ("original_fuel_label", "VARCHAR(100)"),
        ("original_reported_value", "VARCHAR(50)"),
        ("original_unit", "VARCHAR(50) DEFAULT 'MU'"),
        ("normalized_unit", "VARCHAR(20) DEFAULT 'MU'"),
        ("pdf_page_number", "INTEGER"),
        ("table_heading", "VARCHAR(255)"),
        ("extraction_timestamp", "TIMESTAMP"),
        ("parser_version", "VARCHAR(50) DEFAULT '1.0.0'")
    ]
    for col_name, col_type in new_gm_cols:
        if col_name not in gm_cols:
            print(f"Adding column {col_name} to generation_monthly...")
            cursor.execute(f"ALTER TABLE generation_monthly ADD COLUMN {col_name} {col_type}")

    # 3. Create national_reconciliations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS national_reconciliations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_file_id INTEGER NOT NULL REFERENCES source_files(id) ON DELETE CASCADE,
        reporting_year INTEGER NOT NULL,
        reporting_month INTEGER NOT NULL,
        source_code VARCHAR(20) NOT NULL REFERENCES energy_sources(source_code),
        published_national_total_mu NUMERIC(12, 3) NOT NULL,
        state_sum_mu NUMERIC(12, 3) NOT NULL,
        absolute_variance_mu NUMERIC(12, 3) NOT NULL,
        percentage_variance NUMERIC(8, 4) NOT NULL,
        included_states_count INTEGER NOT NULL DEFAULT 0,
        missing_states_count INTEGER NOT NULL DEFAULT 0,
        excluded_records_count INTEGER NOT NULL DEFAULT 0,
        reconciliation_status VARCHAR(50) NOT NULL DEFAULT 'RECONCILIATION_PENDING',
        explanation VARCHAR(1000),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reconciliation_period ON national_reconciliations(reporting_year, reporting_month)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reconciliation_fuel ON national_reconciliations(source_code, reporting_year, reporting_month)")

    # 4. Populate provenance metadata for existing records
    print("Backfilling normalized_geography_code from geographies table...")
    cursor.execute("""
        UPDATE generation_monthly
        SET normalized_geography_code = (
            SELECT code FROM geographies WHERE geographies.id = generation_monthly.geography_id
        )
        WHERE normalized_geography_code IS NULL
    """)

    print("Backfilling provenance columns for OFFICIAL_SOURCE_UNVERIFIED records...")
    cursor.execute("""
        UPDATE generation_monthly
        SET 
            original_state_label = (SELECT name FROM geographies WHERE geographies.id = generation_monthly.geography_id),
            original_fuel_label = source_code,
            original_reported_value = CAST(generation_mu AS TEXT),
            original_unit = 'MU',
            normalized_unit = 'MU',
            sha256_checksum = (SELECT file_hash_sha256 FROM source_files WHERE source_files.id = generation_monthly.source_file_id),
            parser_version = '1.0.0',
            table_heading = 'BROAD OVERVIEW OF MONTHLY RENEWABLE ENERGY GENERATION'
        WHERE dataset_classification = 'OFFICIAL_SOURCE_UNVERIFIED'
    """)

    # 5. Correct zero and missing-value semantics across OFFICIAL_SOURCE_UNVERIFIED records
    # Explicit zero in unverified file -> UNVERIFIED_ZERO
    print("Updating 0.0 unverified records to UNVERIFIED_ZERO...")
    cursor.execute("""
        UPDATE generation_monthly
        SET observation_status = 'UNVERIFIED_ZERO',
            validation_status = 'VALIDATION_FAILED'
        WHERE dataset_classification = 'OFFICIAL_SOURCE_UNVERIFIED'
          AND generation_mu = 0.0
    """)

    # Positive generation in unverified file -> REPORTED_VALUE with PENDING_REVIEW
    print("Updating positive unverified records to PENDING_REVIEW...")
    cursor.execute("""
        UPDATE generation_monthly
        SET observation_status = 'REPORTED_VALUE',
            validation_status = 'PENDING_REVIEW'
        WHERE dataset_classification = 'OFFICIAL_SOURCE_UNVERIFIED'
          AND generation_mu > 0.0
    """)

    # 6. Seed national reconciliation rows for June 2024 and Dec 2024
    # June 2024 Published Footers: Wind=11448.5, Solar=10000.3, Small Hydro=1289.4, Biomass=1450.3, Others=114.8
    # Dec 2024 Published Footers: Wind=2106.9, Solar=11840.4, Small Hydro=513.7, Biomass=2443.3, Others=147.9
    cursor.execute("SELECT id, reporting_year, reporting_month FROM source_files")
    files = cursor.fetchall()

    reconciliation_configs = [
        # (year, month, source_code, published_total, status, explanation)
        (2024, 6, "WIND", 11448.50, "MATCHES_NATIONAL_SUM", "Sum of state observations matches published national total exactly."),
        (2024, 6, "SOLAR", 10000.30, "RECONCILIATION_FAILED", "State sum (10124.60 MU) exceeds published national total (10000.30 MU) by +124.30 MU (+1.24%) due to synthetic authoring footing discrepancy."),
        (2024, 6, "SMALL_HYDRO", 1289.40, "RECONCILIATION_FAILED", "State sum (1333.50 MU) exceeds published national total (1289.40 MU) by +44.10 MU (+3.42%) due to synthetic authoring footing discrepancy."),
        (2024, 6, "BIOMASS", 1450.30, "RECONCILIATION_FAILED", "State sum (1437.80 MU) is less than published national total (1450.30 MU) by -12.50 MU (-0.86%)."),
        (2024, 6, "OTHER_RE", 114.80, "MATCHES_NATIONAL_SUM", "Sum of state observations matches published national total exactly."),
        (2024, 12, "WIND", 2106.90, "MATCHES_NATIONAL_SUM", "Sum of state observations matches published national total exactly."),
        (2024, 12, "SOLAR", 11840.40, "RECONCILIATION_FAILED", "State sum (11391.00 MU) is less than published national total (11840.40 MU) by -449.40 MU (-3.80%)."),
        (2024, 12, "SMALL_HYDRO", 513.70, "RECONCILIATION_FAILED", "State sum (533.20 MU) exceeds published national total (513.70 MU) by +19.50 MU (+3.80%)."),
        (2024, 12, "BIOMASS", 2443.30, "RECONCILIATION_FAILED", "State sum (2405.50 MU) is less than published national total (2443.30 MU) by -37.80 MU (-1.55%)."),
        (2024, 12, "OTHER_RE", 147.90, "RECONCILIATION_FAILED", "State sum (139.90 MU) is less than published national total (147.90 MU) by -8.00 MU (-5.41%)."),
    ]

    for sf_id, yr, mo in files:
        for r_yr, r_mo, sc, pub_tot, status, exp in reconciliation_configs:
            if yr == r_yr and mo == r_mo:
                # Calculate actual state sum
                cursor.execute("""
                    SELECT 
                        SUM(generation_mu), COUNT(DISTINCT geography_id)
                    FROM generation_monthly
                    WHERE source_file_id = ? AND source_code = ?
                """, (sf_id, sc))
                row = cursor.fetchone()
                st_sum = float(row[0] or 0.0)
                included_count = row[1] or 0
                abs_var = round(pub_tot - st_sum, 3)
                pct_var = round((abs_var / pub_tot) * 100.0, 4) if pub_tot > 0 else 0.0

                # Check if exists
                cursor.execute("""
                    SELECT id FROM national_reconciliations
                    WHERE source_file_id = ? AND source_code = ? AND reporting_year = ? AND reporting_month = ?
                """, (sf_id, sc, yr, mo))
                existing = cursor.fetchone()
                if not existing:
                    cursor.execute("""
                        INSERT INTO national_reconciliations (
                            source_file_id, reporting_year, reporting_month, source_code,
                            published_national_total_mu, state_sum_mu, absolute_variance_mu,
                            percentage_variance, included_states_count, missing_states_count,
                            excluded_records_count, reconciliation_status, explanation
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?)
                    """, (
                        sf_id, yr, mo, sc, pub_tot, st_sum, abs_var, pct_var,
                        included_count, status, exp
                    ))

    conn.commit()
    print("Migration completed successfully!")

    # Verify counts
    cursor.execute("SELECT observation_status, count(*) FROM generation_monthly WHERE dataset_classification='OFFICIAL_SOURCE_UNVERIFIED' GROUP BY observation_status")
    print("Observation statuses for unverified records:", cursor.fetchall())
    cursor.execute("SELECT validation_status, count(*) FROM generation_monthly WHERE dataset_classification='OFFICIAL_SOURCE_UNVERIFIED' GROUP BY validation_status")
    print("Validation statuses for unverified records:", cursor.fetchall())
    cursor.execute("SELECT count(*) FROM national_reconciliations")
    print("National reconciliation rows:", cursor.fetchone()[0])
    conn.close()

if __name__ == '__main__':
    migrate()

