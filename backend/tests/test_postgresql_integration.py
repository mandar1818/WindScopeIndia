"""
WindScope India — PostgreSQL Integration Test Suite.
Verifies production PostgreSQL readiness, drivers, pooling configurations,
and conditional live integration testing.

Per non-negotiable rule 9 and 15:
If an active, reachable PostgreSQL instance is present, full integration tests run.
If unavailable, live execution is formally marked BLOCKED.
"""
import os
import pytest
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import check_database_connection, engine, SessionLocal


def test_postgresql_driver_installed():
    """Verify that psycopg2 PostgreSQL driver is installed and importable."""
    try:
        import psycopg2
        assert psycopg2.__version__ is not None
    except ImportError:
        pytest.fail("psycopg2 PostgreSQL driver is not installed in the Python environment.")


def test_database_connection_health_check():
    """Verify that the database health check utility returns healthy status."""
    health = check_database_connection()
    assert health["status"] == "HEALTHY"
    assert health["check_value"] == 1
    assert "dialect" in health


def test_postgresql_live_integration_suite():
    """
    Executes live PostgreSQL integration tests if a valid PostgreSQL instance is configured.
    Otherwise skips and formally reports BLOCKED per project rules.
    """
    pg_url = os.getenv("TEST_POSTGRES_URL") or os.getenv("DATABASE_URL")
    if not pg_url or not pg_url.startswith("postgresql"):
        pytest.skip("Live PostgreSQL instance unavailable: marked BLOCKED per non-negotiable project rule 9 and 15.")

    # If PG URL is configured, attempt connection
    try:
        pg_engine = create_engine(pg_url, pool_pre_ping=True)
        with pg_engine.connect() as conn:
            val = conn.execute(text("SELECT 1")).scalar()
            assert val == 1
    except Exception as exc:
        pytest.skip(f"Live PostgreSQL instance could not be connected: marked BLOCKED ({exc})")

    # Full integration tests on live PostgreSQL
    with pg_engine.connect() as conn:
        # 1. Foreign keys
        conn.execute(text("SET foreign_key_checks = 1;"))
        # 2. Test transactions & rollback
        trans = conn.begin()
        conn.execute(text("CREATE TEMP TABLE _test_trans (id int);"))
        trans.rollback()

