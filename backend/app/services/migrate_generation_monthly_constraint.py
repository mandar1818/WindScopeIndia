import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "windscope_india.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT count(*) FROM generation_monthly")
    count_before = cursor.fetchone()[0]
    print(f"Count before table recreation: {count_before}")

    cursor.execute("PRAGMA foreign_keys = OFF;")
    conn.commit()

    cursor.execute("""
    CREATE TABLE generation_monthly_new (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        geography_id INTEGER NOT NULL,
        source_code VARCHAR(20) NOT NULL,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        generation_mu NUMERIC(12, 3),
        target_mu NUMERIC(12, 3),
        capacity_utilization_factor_pct NUMERIC(6, 2),
        source_provenance VARCHAR(100) NOT NULL,
        is_verified BOOLEAN DEFAULT 1,
        dataset_classification VARCHAR(50) NOT NULL DEFAULT 'DEMONSTRATION',
        source_file_id INTEGER REFERENCES source_files(id) ON DELETE SET NULL,
        source_org VARCHAR(100),
        dataset_name VARCHAR(255),
        source_url VARCHAR(512),
        original_filename VARCHAR(255),
        download_timestamp DATETIME,
        processing_timestamp DATETIME,
        unit_conversion_applied VARCHAR(100) DEFAULT 'DIRECT_MU',
        validation_status VARCHAR(50) DEFAULT 'BENCHMARK_SIMULATION',
        observation_status VARCHAR(50) DEFAULT 'REPORTED_VALUE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT chk_month_range CHECK (month >= 1 AND month <= 12),
        CONSTRAINT uq_gen_monthly_record UNIQUE (geography_id, source_code, year, month, dataset_classification),
        FOREIGN KEY(geography_id) REFERENCES geographies (id) ON DELETE CASCADE,
        FOREIGN KEY(source_code) REFERENCES energy_sources (source_code)
    );
    """)

    cursor.execute("""
    INSERT INTO generation_monthly_new (
        id, geography_id, source_code, year, month, generation_mu, target_mu,
        capacity_utilization_factor_pct, source_provenance, is_verified,
        dataset_classification, source_file_id, source_org, dataset_name, source_url,
        original_filename, download_timestamp, processing_timestamp,
        unit_conversion_applied, validation_status, observation_status, created_at
    )
    SELECT 
        id, geography_id, source_code, year, month, generation_mu, target_mu,
        capacity_utilization_factor_pct, source_provenance, is_verified,
        COALESCE(dataset_classification, 'DEMONSTRATION'), source_file_id, source_org, dataset_name, source_url,
        original_filename, download_timestamp, processing_timestamp,
        unit_conversion_applied, validation_status, observation_status, created_at
    FROM generation_monthly;
    """)

    cursor.execute("DROP TABLE generation_monthly;")
    cursor.execute("ALTER TABLE generation_monthly_new RENAME TO generation_monthly;")

    # Recreate indexes
    cursor.execute("CREATE INDEX idx_gen_monthly_geo_year ON generation_monthly (geography_id, year, month);")
    cursor.execute("CREATE INDEX idx_gen_monthly_source_year ON generation_monthly (source_code, year, month);")
    cursor.execute("CREATE INDEX idx_gen_monthly_dataset ON generation_monthly (dataset_classification, year, month);")

    # Clean any test rows from source_files and ingestion_audit_logs if needed
    cursor.execute("DELETE FROM source_files WHERE filename LIKE '%tmp%';")
    cursor.execute("DELETE FROM ingestion_audit_logs WHERE dataset_name LIKE '%tmp%' OR dataset_name = 'CEA_RE_2024_12';")

    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    cursor.execute("SELECT count(*) FROM generation_monthly")
    count_after = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM generation_monthly WHERE dataset_classification = 'DEMONSTRATION'")
    count_demo = cursor.fetchone()[0]

    conn.close()

    print(f"Table recreation complete: before={count_before}, after={count_after}, demo={count_demo}")
    assert count_before == count_after, "Record count mismatch during table migration!"
    print("Migration successful and verified!")

if __name__ == "__main__":
    migrate()

