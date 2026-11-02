"""
Migration script for Phase 2: Provenance & Classification
Safely updates windscope_india.db to add source_files and new columns to generation_monthly.
Preserves all 18,213 existing records intact.
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "windscope_india.db"

def run_migration():
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return False

    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Count records before
    cursor.execute("SELECT count(*) FROM generation_monthly")
    count_before = cursor.fetchone()[0]
    print(f"Existing generation_monthly records before migration: {count_before}")

    # 2. Create source_files table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS source_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename VARCHAR(255) NOT NULL UNIQUE,
        file_path VARCHAR(512) NOT NULL,
        file_hash_sha256 VARCHAR(64) NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        source_org VARCHAR(100) NOT NULL,
        dataset_title VARCHAR(255) NOT NULL,
        source_url VARCHAR(512) NOT NULL,
        reporting_year INTEGER NOT NULL,
        reporting_month INTEGER,
        download_timestamp DATETIME NOT NULL,
        ingestion_status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
        records_extracted INTEGER NOT NULL DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_files_hash ON source_files (file_hash_sha256);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_files_year_month ON source_files (reporting_year, reporting_month);")
    print("Table 'source_files' ensured.")

    # 3. Check existing columns in generation_monthly
    cursor.execute("PRAGMA table_info(generation_monthly)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    print(f"Existing columns in generation_monthly: {len(existing_cols)}")

    columns_to_add = [
        ("dataset_classification", "VARCHAR(50) DEFAULT 'DEMONSTRATION'"),
        ("source_file_id", "INTEGER REFERENCES source_files(id) ON DELETE SET NULL"),
        ("source_org", "VARCHAR(100)"),
        ("dataset_name", "VARCHAR(255)"),
        ("source_url", "VARCHAR(512)"),
        ("original_filename", "VARCHAR(255)"),
        ("download_timestamp", "DATETIME"),
        ("processing_timestamp", "DATETIME"),
        ("unit_conversion_applied", "VARCHAR(100) DEFAULT 'DIRECT_MU'"),
        ("validation_status", "VARCHAR(50) DEFAULT 'BENCHMARK_SIMULATION'"),
        ("observation_status", "VARCHAR(50) DEFAULT 'REPORTED_VALUE'"),
    ]

    for col_name, col_def in columns_to_add:
        if col_name not in existing_cols:
            alter_query = f"ALTER TABLE generation_monthly ADD COLUMN {col_name} {col_def};"
            cursor.execute(alter_query)
            print(f"Added column: {col_name}")
        else:
            print(f"Column already exists: {col_name}")

    # 4. Create index on dataset_classification, year, month
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_gen_monthly_dataset 
    ON generation_monthly (dataset_classification, year, month);
    """)

    # 5. Update existing demonstration records with clear provenance metadata
    cursor.execute("""
    UPDATE generation_monthly 
    SET 
        dataset_classification = 'DEMONSTRATION',
        source_org = COALESCE(source_org, 'WindScope Research Benchmark'),
        dataset_name = COALESCE(dataset_name, 'India Multi-Year RE Benchmark Simulation'),
        unit_conversion_applied = COALESCE(unit_conversion_applied, 'DIRECT_MU'),
        validation_status = COALESCE(validation_status, 'BENCHMARK_SIMULATION'),
        observation_status = CASE 
            WHEN generation_mu IS NULL THEN 'MISSING_OBSERVATION'
            WHEN generation_mu = 0 THEN 'PHYSICAL_ZERO_CONFIRMED'
            ELSE 'REPORTED_VALUE'
        END
    WHERE dataset_classification IS NULL OR dataset_classification = 'DEMONSTRATION';
    """)

    conn.commit()

    # 6. Verify count after
    cursor.execute("SELECT count(*) FROM generation_monthly")
    count_after = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM generation_monthly WHERE dataset_classification = 'DEMONSTRATION'")
    count_demo = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM source_files")
    count_files = cursor.fetchone()[0]

    conn.close()
    print(f"Migration completed successfully.")
    print(f"Records before: {count_before}, Records after: {count_after}, Demonstration records: {count_demo}")
    print(f"Source files count: {count_files}")

    assert count_before == count_after, "Record count mismatch during migration!"
    return True

if __name__ == "__main__":
    run_migration()

