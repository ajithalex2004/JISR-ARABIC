"""Operational database backup helpers for SQLite and PostgreSQL."""
import argparse
import datetime
import sqlite3
import shutil
import subprocess
from pathlib import Path

from backend.database import DB_PATH, DATABASE_URL, IS_SQLITE


def create_backup(destination: Path):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if IS_SQLITE:
        with sqlite3.connect(DB_PATH) as source, sqlite3.connect(destination) as target:
            source.backup(target)
            result = target.execute("PRAGMA integrity_check").fetchone()[0]
            if result != "ok":
                raise RuntimeError(f"Backup integrity check failed: {result}")
    else:
        if not shutil.which("pg_dump"):
            raise RuntimeError("pg_dump is required for PostgreSQL backups")
        subprocess.run(["pg_dump", "--format=custom", "--file", str(destination), DATABASE_URL], check=True)
    return destination


def restore_backup(source: Path):
    if not source.is_file():
        raise FileNotFoundError(source)
    if IS_SQLITE:
        with sqlite3.connect(source) as backup, sqlite3.connect(DB_PATH) as target:
            target.execute("PRAGMA foreign_keys=OFF")
            backup.backup(target)
            target.execute("PRAGMA foreign_keys=ON")
    else:
        if not shutil.which("pg_restore"):
            raise RuntimeError("pg_restore is required for PostgreSQL restores")
        subprocess.run(["pg_restore", "--clean", "--if-exists", "--dbname", DATABASE_URL, str(source)], check=True)
    return source


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("backup", "restore"), nargs="?", default="backup")
    parser.add_argument("destination", nargs="?", type=Path)
    args = parser.parse_args()
    suffix = "db" if IS_SQLITE else "dump"
    target = args.destination or Path("backups") / f"fahim-{datetime.datetime.utcnow():%Y%m%d-%H%M%S}.{suffix}"
    print((create_backup(target) if args.command == "backup" else restore_backup(target)).resolve())
