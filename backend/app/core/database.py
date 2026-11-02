import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
from app.core.config import settings

# Dual-engine support: PostgreSQL in production, SQLite locally / in tests
database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)

# Normalize postgres:// to postgresql:// for modern SQLAlchemy 2.x
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
elif "sqlite" in database_url:
    # If using local SQLite, resolve path to backend/windscope_india.db if relative
    if "windscope_india.db" in database_url and not os.path.isabs(database_url.replace("sqlite:///", "")):
        backend_dir = Path(__file__).resolve().parent.parent.parent
        db_file = backend_dir / "windscope_india.db"
        database_url = f"sqlite:///{db_file.as_posix()}"

engine_kwargs = {"echo": False}

if "sqlite" in database_url:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    # For SQLite, NullPool or default is appropriate
else:
    # PostgreSQL production configurations
    connect_args = {}
    ssl_mode = os.getenv("DATABASE_SSL_MODE", settings.DATABASE_SSL_MODE)
    if os.getenv("DATABASE_SSL_REQUIRE", "false").lower() in ("true", "1", "yes") or ssl_mode == "require":
        connect_args["sslmode"] = "require"
    elif ssl_mode and ssl_mode != "disable":
        connect_args["sslmode"] = ssl_mode

    engine_kwargs["connect_args"] = connect_args
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = int(os.getenv("DATABASE_POOL_SIZE", str(settings.DATABASE_POOL_SIZE)))
    engine_kwargs["max_overflow"] = int(os.getenv("DATABASE_MAX_OVERFLOW", str(settings.DATABASE_MAX_OVERFLOW)))
    engine_kwargs["pool_timeout"] = int(os.getenv("DATABASE_POOL_TIMEOUT", str(settings.DATABASE_POOL_TIMEOUT)))
    engine_kwargs["pool_recycle"] = int(os.getenv("DATABASE_POOL_RECYCLE", str(settings.DATABASE_POOL_RECYCLE)))

engine = create_engine(database_url, **engine_kwargs)

if "sqlite" in database_url:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from contextlib import contextmanager

@contextmanager
def get_db_context():
    """Safe context manager for transactional database operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_database_connection():
    """Performs a health check on the active database engine."""
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            is_postgres = "postgresql" in engine.url.drivername
            return {
                "status": "HEALTHY",
                "dialect": engine.url.drivername,
                "is_postgresql": is_postgres,
                "pool_size": engine_kwargs.get("pool_size", "N/A"),
                "check_value": result
            }
    except Exception as exc:
        return {
            "status": "UNHEALTHY",
            "dialect": engine.url.drivername if hasattr(engine, "url") else "unknown",
            "error": str(exc)
        }
