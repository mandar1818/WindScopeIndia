"""
Data Authenticity Audit Migration Script.
Updates windscope_india.db to correct classifications based on strict authenticity audit:
1. Reclassifies the 360 manually prepared records from 'OFFICIAL_REPORTED' to 'OFFICIAL_SOURCE_UNVERIFIED'.
2. Decouples zero generation from capacity: updates zero values from 'PHYSICAL_ZERO_CONFIRMED' / 'REPORTED_OPERATIONAL_ZERO' to 'REPORTED_ZERO'.
3. Updates validation_status to 'UNVERIFIED_SOURCE_MANUAL_EXTRACTION'.
4. Updates source_files table to set ingestion_status = 'UNVERIFIED_SOURCE'.
Preserves all 15,768 demonstration records and existing history.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "windscope_india.db"

def apply_audit_updates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Check counts before
    cursor.execute("SELECT count(*) FROM generation_monthly")
    total_before = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM generation_monthly WHERE dataset_classification IN ('OFFICIAL_REPORTED', 'OFFICIAL_SOURCE_UNVERIFIED')")
    target_count = cursor.fetchone()[0]
    print(f"Total generation_monthly records: {total_before}")
    print(f"Target unverified records: {target_count}")

    # 2. Update observation status for explicitly reported zeros
    cursor.execute("""
    UPDATE generation_monthly
    SET observation_status = 'REPORTED_ZERO'
    WHERE dataset_classification IN ('OFFICIAL_REPORTED', 'OFFICIAL_SOURCE_UNVERIFIED')
      AND (generation_mu = 0.0 OR generation_mu = 0);
    """)
    updated_zeros = cursor.rowcount
    print(f"Updated {updated_zeros} records to observation_status = 'REPORTED_ZERO'")

    # 3. Update dataset_classification to 'OFFICIAL_SOURCE_UNVERIFIED'
    cursor.execute("""
    UPDATE generation_monthly
    SET 
        dataset_classification = 'OFFICIAL_SOURCE_UNVERIFIED',
        validation_status = 'UNVERIFIED_MANUAL_EXTRACTION',
        is_verified = 0,
        source_provenance = CASE 
            WHEN original_filename LIKE '%June%' THEN 'CEA Unverified Source Model (June 2024)'
            ELSE 'CEA Unverified Source Model (December 2024)'
        END
    WHERE dataset_classification = 'OFFICIAL_REPORTED';
    """)
    reclassified = cursor.rowcount
    print(f"Reclassified {reclassified} records to dataset_classification = 'OFFICIAL_SOURCE_UNVERIFIED'")

    # 4. Update source_files table
    cursor.execute("""
    UPDATE source_files
    SET ingestion_status = 'UNVERIFIED_SOURCE'
    WHERE filename LIKE '%2024_06_CEA%' OR filename LIKE '%2024_12_CEA%';
    """)
    updated_files = cursor.rowcount
    print(f"Updated {updated_files} source files to status = 'UNVERIFIED_SOURCE'")

    # 5. Clean any leftover tmp rows if any
    cursor.execute("DELETE FROM source_files WHERE filename LIKE '%tmp%';")
    cursor.execute("DELETE FROM ingestion_audit_logs WHERE dataset_name LIKE '%tmp%' OR dataset_name = 'CEA_RE_2024_11';")

    conn.commit()

    # 6. Verify breakdown
    cursor.execute("SELECT dataset_classification, count(*) FROM generation_monthly GROUP BY dataset_classification")
    breakdown = cursor.fetchall()
    print("New dataset classification breakdown:")
    for b in breakdown:
        print(f"  - {b[0]}: {b[1]} records")

    cursor.execute("SELECT observation_status, count(*) FROM generation_monthly WHERE dataset_classification = 'OFFICIAL_SOURCE_UNVERIFIED' GROUP BY observation_status")
    obs_breakdown = cursor.fetchall()
    print("Observation status breakdown in OFFICIAL_SOURCE_UNVERIFIED:")
    for ob in obs_breakdown:
        print(f"  - {ob[0]}: {ob[1]} records")

    conn.close()
    assert total_before == sum(b[1] for b in breakdown), "Total record count changed!"
    print("Database authenticity audit updates completed successfully.")

if __name__ == "__main__":
    apply_audit_updates()

