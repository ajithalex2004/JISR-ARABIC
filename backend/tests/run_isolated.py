"""Run backend tests against a disposable database, never backend/fahim.db.

Usage: python -B -m backend.tests.run_isolated
"""
import tempfile
import unittest
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="fahim-tests-") as directory:
        db_path = (Path(directory) / "test.db").as_posix()
        # Tests always use the disposable SQLite fixture, regardless of a local
        # production .env used to run the application against Neon.
        os.environ["FAHIM_ENV"] = "development"
        os.environ["FAHIM_SEED_DEMO"] = "1"
        os.environ["FAHIM_EXPOSE_DEBUG_OTP"] = "1"
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

        import backend.database as database
        import backend.migrations as migrations

        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        database.engine = engine
        migrations.engine = engine
        database.SessionLocal = sessionmaker(
            bind=engine, autocommit=False, autoflush=False,
        )
        try:
            resolved_file = Path(__file__).resolve()
            suite = unittest.defaultTestLoader.discover(
                str(resolved_file.parent), pattern="test_*.py",
                top_level_dir=str(resolved_file.parents[2]),
            )
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            return 0 if result.wasSuccessful() else 1
        finally:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
