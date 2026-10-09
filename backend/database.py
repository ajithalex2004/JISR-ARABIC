import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fahim.db")
try:
    from dotenv import load_dotenv
    # Production environments must rely strictly on container/orchestrator environment variables.
    # In non-production, load local .env but NEVER override existing deployment variables.
    if os.getenv("FAHIM_ENV", "development").lower() != "production":
        env_file = os.path.join(BASE_DIR, ".env")
        if os.path.exists(env_file):
            load_dotenv(env_file, override=False)
except ImportError:
    pass
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
IS_SQLITE = DATABASE_URL.startswith("sqlite")
if os.getenv("FAHIM_ENV", "development").lower() == "production" and IS_SQLITE:
    raise RuntimeError("Production database configuration cannot use SQLite")

engine_kwargs = {"pool_pre_ping": True}
if IS_SQLITE:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "pool_size": int(os.getenv("DB_POOL_SIZE", "15")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "1800")),
    })
engine = create_engine(DATABASE_URL, **engine_kwargs)

if IS_SQLITE:
    @event.listens_for(engine, "connect")
    def configure_sqlite(connection, _):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def run_migrations():
    """Compatibility wrapper; deployments should use `python -m backend.migrations upgrade`."""
    from backend.migrations import upgrade
    upgrade()


def get_db_pool_status():
    """Retrieve connection pool metrics for health checks and observability.
    In production, details are masked to prevent infrastructure reconnaissance.
    """
    if os.getenv("FAHIM_ENV", "development").lower() == "production":
        return {"status": "configured"}
    pool = getattr(engine, "pool", None)
    if pool is None:
        return {"type": "none"}
    status = {"type": pool.__class__.__name__}
    for attr in ("size", "checkedin", "checkedout", "overflow"):
        fn = getattr(pool, attr, None)
        if callable(fn):
            try:
                status[attr] = fn()
            except Exception:
                pass
    return status

