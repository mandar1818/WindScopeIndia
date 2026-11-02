"""Comprehensive initial schema for WindScope India.
Creates all 13 core analytical and operational tables for clean PostgreSQL
and SQLite deployments, with explicit constraint naming and safe idempotent checks.

Revision ID: af8f7710238a
Revises: None
Create Date: 2026-11-01
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'af8f7710238a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_tables = set(insp.get_table_names())

    # 1. regions
    if "regions" not in existing_tables:
        op.create_table(
            "regions",
            sa.Column("region_code", sa.String(length=10), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("headquarters", sa.String(length=100), nullable=False),
            sa.Column("description", sa.String(length=255), nullable=True),
            sa.PrimaryKeyConstraint("region_code", name="pk_regions"),
        )

    # 2. geographies
    if "geographies" not in existing_tables:
        op.create_table(
            "geographies",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("code", sa.String(length=10), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("entity_type", sa.String(length=20), nullable=False),
            sa.Column("region_code", sa.String(length=10), nullable=False),
            sa.Column("capital", sa.String(length=100), nullable=False),
            sa.Column("latitude", sa.Numeric(precision=8, scale=4), nullable=False),
            sa.Column("longitude", sa.Numeric(precision=8, scale=4), nullable=False),
            sa.Column("geojson_id", sa.String(length=50), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["region_code"], ["regions.region_code"], name="fk_geographies_region_code"),
            sa.PrimaryKeyConstraint("id", name="pk_geographies"),
            sa.UniqueConstraint("code", name="uq_geographies_code"),
        )
        op.create_index("ix_geographies_code", "geographies", ["code"])
        op.create_index("ix_geographies_name", "geographies", ["name"])
        op.create_index("idx_geo_code_type", "geographies", ["code", "entity_type"])

    # 3. energy_sources
    if "energy_sources" not in existing_tables:
        op.create_table(
            "energy_sources",
            sa.Column("source_code", sa.String(length=20), nullable=False),
            sa.Column("display_name", sa.String(length=100), nullable=False),
            sa.Column("unit", sa.String(length=20), nullable=True, server_default="MU"),
            sa.Column("is_variable_re", sa.Boolean(), nullable=True, server_default=sa.text("0")),
            sa.PrimaryKeyConstraint("source_code", name="pk_energy_sources"),
        )

    # 4. source_files
    if "source_files" not in existing_tables:
        op.create_table(
            "source_files",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("filename", sa.String(length=255), nullable=False),
            sa.Column("file_path", sa.String(length=512), nullable=False),
            sa.Column("file_hash_sha256", sa.String(length=64), nullable=False),
            sa.Column("file_size_bytes", sa.Integer(), nullable=False),
            sa.Column("document_format", sa.String(length=20), nullable=False, server_default="CSV"),
            sa.Column("publication_date", sa.String(length=50), nullable=True),
            sa.Column("source_org", sa.String(length=100), nullable=False),
            sa.Column("dataset_title", sa.String(length=255), nullable=False),
            sa.Column("source_url", sa.String(length=512), nullable=False),
            sa.Column("reporting_year", sa.Integer(), nullable=False),
            sa.Column("reporting_month", sa.Integer(), nullable=True),
            sa.Column("download_timestamp", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("parser_version", sa.String(length=50), nullable=True, server_default="1.0.0"),
            sa.Column("ingestion_status", sa.String(length=50), nullable=False, server_default="PENDING"),
            sa.Column("records_extracted", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("validation_summary", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id", name="pk_source_files"),
            sa.UniqueConstraint("filename", name="uq_source_files_filename"),
        )
        op.create_index("ix_source_files_file_hash_sha256", "source_files", ["file_hash_sha256"])
        op.create_index("ix_source_files_reporting_year", "source_files", ["reporting_year"])
        op.create_index("ix_source_files_reporting_month", "source_files", ["reporting_month"])

    # 5. installed_capacity
    if "installed_capacity" not in existing_tables:
        op.create_table(
            "installed_capacity",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("geography_id", sa.Integer(), nullable=False),
            sa.Column("source_code", sa.String(length=20), nullable=False),
            sa.Column("effective_date", sa.Date(), nullable=False),
            sa.Column("capacity_mw", sa.Numeric(precision=12, scale=2), nullable=False),
            sa.Column("source_provenance", sa.String(length=100), nullable=False, server_default="CEA Monthly Executive Summary"),
            sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["geography_id"], ["geographies.id"], name="fk_installed_capacity_geography_id", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["source_code"], ["energy_sources.source_code"], name="fk_installed_capacity_source_code"),
            sa.PrimaryKeyConstraint("id", name="pk_installed_capacity"),
            sa.UniqueConstraint("geography_id", "source_code", "effective_date", name="uq_capacity_geo_source_date"),
        )
        op.create_index("idx_installed_capacity_geo_date", "installed_capacity", ["geography_id", "effective_date"])

    # 6. generation_monthly
    if "generation_monthly" not in existing_tables:
        op.create_table(
            "generation_monthly",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("geography_id", sa.Integer(), nullable=False),
            sa.Column("source_code", sa.String(length=20), nullable=False),
            sa.Column("year", sa.Integer(), nullable=False),
            sa.Column("month", sa.Integer(), nullable=False),
            sa.Column("generation_mu", sa.Numeric(precision=12, scale=3), nullable=True),
            sa.Column("target_mu", sa.Numeric(precision=12, scale=3), nullable=True),
            sa.Column("capacity_utilization_factor_pct", sa.Numeric(precision=6, scale=2), nullable=True),
            sa.Column("source_provenance", sa.String(length=100), nullable=False, server_default="CEA Monthly RE Report"),
            sa.Column("is_verified", sa.Boolean(), nullable=True, server_default=sa.text("1")),
            sa.Column("dataset_classification", sa.String(length=50), nullable=False, server_default="DEMONSTRATION"),
            sa.Column("source_file_id", sa.Integer(), nullable=True),
            sa.Column("source_org", sa.String(length=100), nullable=True),
            sa.Column("dataset_name", sa.String(length=255), nullable=True),
            sa.Column("source_url", sa.String(length=512), nullable=True),
            sa.Column("original_filename", sa.String(length=255), nullable=True),
            sa.Column("sha256_checksum", sa.String(length=64), nullable=True),
            sa.Column("publication_date", sa.String(length=50), nullable=True),
            sa.Column("download_timestamp", sa.DateTime(), nullable=True),
            sa.Column("extraction_timestamp", sa.DateTime(), nullable=True),
            sa.Column("processing_timestamp", sa.DateTime(), nullable=True),
            sa.Column("parser_version", sa.String(length=50), nullable=True, server_default="1.0.0"),
            sa.Column("original_state_label", sa.String(length=100), nullable=True),
            sa.Column("normalized_geography_code", sa.String(length=20), nullable=True),
            sa.Column("original_fuel_label", sa.String(length=100), nullable=True),
            sa.Column("original_reported_value", sa.String(length=50), nullable=True),
            sa.Column("original_unit", sa.String(length=50), nullable=True, server_default="MU"),
            sa.Column("normalized_unit", sa.String(length=20), nullable=False, server_default="MU"),
            sa.Column("unit_conversion_applied", sa.String(length=100), nullable=True, server_default="DIRECT_MU"),
            sa.Column("pdf_page_number", sa.Integer(), nullable=True),
            sa.Column("table_heading", sa.String(length=255), nullable=True),
            sa.Column("validation_status", sa.String(length=50), nullable=False, server_default="UNAUDITED"),
            sa.Column("observation_status", sa.String(length=50), nullable=False, server_default="REPORTED_VALUE"),
            sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
            sa.CheckConstraint("month >= 1 AND month <= 12", name="chk_month_range"),
            sa.ForeignKeyConstraint(["geography_id"], ["geographies.id"], name="fk_gen_monthly_geography_id", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["source_code"], ["energy_sources.source_code"], name="fk_gen_monthly_source_code"),
            sa.ForeignKeyConstraint(["source_file_id"], ["source_files.id"], name="fk_gen_monthly_source_file_id", ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id", name="pk_generation_monthly"),
            sa.UniqueConstraint("geography_id", "source_code", "year", "month", "dataset_classification", name="uq_gen_monthly_record"),
        )
        op.create_index("idx_gen_monthly_geo_year", "generation_monthly", ["geography_id", "year", "month"])
        op.create_index("idx_gen_monthly_source_year", "generation_monthly", ["source_code", "year", "month"])
        op.create_index("idx_gen_monthly_dataset", "generation_monthly", ["dataset_classification", "year", "month"])
        op.create_index("ix_generation_monthly_sha256_checksum", "generation_monthly", ["sha256_checksum"])
        op.create_index("ix_generation_monthly_normalized_geography_code", "generation_monthly", ["normalized_geography_code"])

    # 7. generation_daily
    if "generation_daily" not in existing_tables:
        op.create_table(
            "generation_daily",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("geography_id", sa.Integer(), nullable=False),
            sa.Column("source_code", sa.String(length=20), nullable=False),
            sa.Column("delivery_date", sa.Date(), nullable=False),
            sa.Column("generation_mu", sa.Numeric(precision=12, scale=3), nullable=False),
            sa.Column("peak_generation_mw", sa.Numeric(precision=12, scale=2), nullable=True),
            sa.Column("source_provenance", sa.String(length=100), nullable=False, server_default="CEA Daily RE Report / NPP"),
            sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["geography_id"], ["geographies.id"], name="fk_gen_daily_geography_id", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["source_code"], ["energy_sources.source_code"], name="fk_gen_daily_source_code"),
            sa.PrimaryKeyConstraint("id", name="pk_generation_daily"),
            sa.UniqueConstraint("geography_id", "source_code", "delivery_date", name="uq_gen_daily_record"),
        )
        op.create_index("idx_gen_daily_geo_date", "generation_daily", ["geography_id", "delivery_date"])

    # 8. generation_15min_blocks
    if "generation_15min_blocks" not in existing_tables:
        op.create_table(
            "generation_15min_blocks",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("geography_id", sa.Integer(), nullable=False),
            sa.Column("source_code", sa.String(length=20), nullable=False),
            sa.Column("block_timestamp", sa.DateTime(), nullable=False),
            sa.Column("block_number", sa.Integer(), nullable=False),
            sa.Column("actual_generation_mw", sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column("scheduled_generation_mw", sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column("deviation_mw", sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
            sa.CheckConstraint("block_number >= 1 AND block_number <= 96", name="chk_block_range"),
            sa.ForeignKeyConstraint(["geography_id"], ["geographies.id"], name="fk_gen_15min_geography_id", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["source_code"], ["energy_sources.source_code"], name="fk_gen_15min_source_code"),
            sa.PrimaryKeyConstraint("id", name="pk_generation_15min_blocks"),
            sa.UniqueConstraint("geography_id", "source_code", "block_timestamp", name="uq_gen_15min_block"),
        )
        op.create_index("idx_gen_15min_geo_time", "generation_15min_blocks", ["geography_id", "block_timestamp"])

    # 9. weather_observations
    if "weather_observations" not in existing_tables:
        op.create_table(
            "weather_observations",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("geography_id", sa.Integer(), nullable=False),
            sa.Column("observation_time", sa.DateTime(), nullable=False),
            sa.Column("wind_speed_100m_ms", sa.Numeric(precision=6, scale=2), nullable=True),
            sa.Column("solar_ghi_wm2", sa.Numeric(precision=7, scale=2), nullable=True),
            sa.Column("solar_dni_wm2", sa.Numeric(precision=7, scale=2), nullable=True),
            sa.Column("temperature_celsius", sa.Numeric(precision=5, scale=2), nullable=True),
            sa.Column("cloud_cover_pct", sa.Numeric(precision=5, scale=2), nullable=True),
            sa.Column("weather_source", sa.String(length=50), nullable=True, server_default="ERA5 / Open-Meteo"),
            sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["geography_id"], ["geographies.id"], name="fk_weather_geography_id", ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id", name="pk_weather_observations"),
            sa.UniqueConstraint("geography_id", "observation_time", name="uq_weather_geo_time"),
        )
        op.create_index("idx_weather_geo_time", "weather_observations", ["geography_id", "observation_time"])

    # 10. forecast_records
    if "forecast_records" not in existing_tables:
        op.create_table(
            "forecast_records",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("geography_id", sa.Integer(), nullable=False),
            sa.Column("source_code", sa.String(length=20), nullable=False),
            sa.Column("forecast_type", sa.String(length=50), nullable=False),
            sa.Column("publish_time", sa.DateTime(), nullable=False),
            sa.Column("target_time", sa.DateTime(), nullable=False),
            sa.Column("predicted_generation_mu", sa.Numeric(precision=12, scale=3), nullable=True),
            sa.Column("predicted_generation_mw", sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column("model_version", sa.String(length=50), nullable=False),
            sa.Column("is_eligible_under_cutoff", sa.Boolean(), nullable=True, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["geography_id"], ["geographies.id"], name="fk_forecast_geography_id", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["source_code"], ["energy_sources.source_code"], name="fk_forecast_source_code"),
            sa.PrimaryKeyConstraint("id", name="pk_forecast_records"),
        )
        op.create_index("idx_forecast_geo_target", "forecast_records", ["geography_id", "target_time"])

    # 11. forecast_evaluations
    if "forecast_evaluations" not in existing_tables:
        op.create_table(
            "forecast_evaluations",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("geography_id", sa.Integer(), nullable=False),
            sa.Column("source_code", sa.String(length=20), nullable=False),
            sa.Column("evaluation_date", sa.Date(), nullable=False),
            sa.Column("model_name", sa.String(length=50), nullable=False),
            sa.Column("sample_count", sa.Integer(), nullable=False),
            sa.Column("mae_mu", sa.Numeric(precision=10, scale=3), nullable=False),
            sa.Column("rmse_mu", sa.Numeric(precision=10, scale=3), nullable=False),
            sa.Column("wape_pct", sa.Numeric(precision=6, scale=2), nullable=False),
            sa.Column("signed_bias_mu", sa.Numeric(precision=10, scale=3), nullable=False),
            sa.Column("evaluation_timestamp", sa.DateTime(), nullable=True, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["geography_id"], ["geographies.id"], name="fk_eval_geography_id", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["source_code"], ["energy_sources.source_code"], name="fk_eval_source_code"),
            sa.PrimaryKeyConstraint("id", name="pk_forecast_evaluations"),
            sa.UniqueConstraint("geography_id", "source_code", "evaluation_date", "model_name", name="uq_forecast_eval"),
        )
        op.create_index("idx_eval_geo_date", "forecast_evaluations", ["geography_id", "evaluation_date"])

    # 12. ingestion_audit_logs
    if "ingestion_audit_logs" not in existing_tables:
        op.create_table(
            "ingestion_audit_logs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("dataset_name", sa.String(length=100), nullable=False),
            sa.Column("source_url", sa.String(length=255), nullable=True),
            sa.Column("ingestion_status", sa.String(length=30), nullable=False),
            sa.Column("records_processed", sa.Integer(), nullable=True, server_default=sa.text("0")),
            sa.Column("records_inserted", sa.Integer(), nullable=True, server_default=sa.text("0")),
            sa.Column("records_updated", sa.Integer(), nullable=True, server_default=sa.text("0")),
            sa.Column("error_summary", sa.Text(), nullable=True),
            sa.Column("execution_time_seconds", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("ingested_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id", name="pk_ingestion_audit_logs"),
        )

    # 13. national_reconciliations
    if "national_reconciliations" not in existing_tables:
        op.create_table(
            "national_reconciliations",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("source_file_id", sa.Integer(), nullable=False),
            sa.Column("reporting_year", sa.Integer(), nullable=False),
            sa.Column("reporting_month", sa.Integer(), nullable=False),
            sa.Column("source_code", sa.String(length=20), nullable=False),
            sa.Column("published_national_total_mu", sa.Numeric(precision=12, scale=3), nullable=False),
            sa.Column("state_sum_mu", sa.Numeric(precision=12, scale=3), nullable=True),
            sa.Column("absolute_variance_mu", sa.Numeric(precision=12, scale=3), nullable=True),
            sa.Column("percentage_variance", sa.Numeric(precision=8, scale=4), nullable=True),
            sa.Column("included_states_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("missing_states_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("excluded_records_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("reconciliation_status", sa.String(length=50), nullable=False, server_default="NOT_RECONCILED"),
            sa.Column("mathematical_reconciliation", sa.String(length=50), nullable=False, server_default="NOT_APPLICABLE"),
            sa.Column("source_verification_status", sa.String(length=50), nullable=False, server_default="OFFICIAL_SOURCE_UNVERIFIED"),
            sa.Column("geographic_coverage", sa.String(length=50), nullable=False, server_default="NATIONAL_AGGREGATE_ONLY"),
            sa.Column("fuel_mapping_validity", sa.String(length=50), nullable=False, server_default="VALID_FUEL_MAPPING"),
            sa.Column("unit_compatibility", sa.String(length=50), nullable=False, server_default="COMPATIBLE_UNITS"),
            sa.Column("explanation", sa.String(length=1000), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["source_file_id"], ["source_files.id"], name="fk_reconciliations_source_file_id", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["source_code"], ["energy_sources.source_code"], name="fk_reconciliations_source_code"),
            sa.PrimaryKeyConstraint("id", name="pk_national_reconciliations"),
        )
        op.create_index("idx_reconciliation_period", "national_reconciliations", ["reporting_year", "reporting_month"])
        op.create_index("idx_reconciliation_fuel", "national_reconciliations", ["source_code", "reporting_year", "reporting_month"])


def downgrade() -> None:
    # Drops in reverse dependency order
    op.drop_table("national_reconciliations")
    op.drop_table("ingestion_audit_logs")
    op.drop_table("forecast_evaluations")
    op.drop_table("forecast_records")
    op.drop_table("weather_observations")
    op.drop_table("generation_15min_blocks")
    op.drop_table("generation_daily")
    op.drop_table("generation_monthly")
    op.drop_table("installed_capacity")
    op.drop_table("source_files")
    op.drop_table("energy_sources")
    op.drop_table("geographies")
    op.drop_table("regions")
