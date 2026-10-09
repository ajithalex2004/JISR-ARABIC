"""Small, explicit migration runner for supported development/production DBs.

Usage: python -m backend.migrations status|upgrade
"""
import sys
import hashlib
import json
from sqlalchemy import text, inspect

from backend.database import engine


MIGRATIONS = [
    ("0001_legacy_columns", [
        ("users", "phone_number", "VARCHAR(50)"),
        ("child_profiles", "avatar_id", "VARCHAR(50) DEFAULT 'avatar_falcon'"),
        ("child_profiles", "curriculum_stream", "VARCHAR(100) DEFAULT 'MoE / CBSE Arabic (Non-Arabs)'"),
        ("child_profiles", "access_pin", "VARCHAR(128)"),
        ("child_profiles", "diagnostic_completed", "BOOLEAN DEFAULT 0"),
        ("child_profiles", "diagnostic_level", "VARCHAR(50) DEFAULT 'intermediate'"),
        ("child_profiles", "selected_term", "INTEGER DEFAULT 1"),
        ("child_profiles", "diagnostic_score", "FLOAT DEFAULT 0.0"),
        ("child_profiles", "diagnostic_details", "TEXT"),
        ("child_profiles", "learning_plan", "TEXT"),
    ]),
    ("0002_billing_integrity", [
        ("payment_transactions", "package_type", "VARCHAR(50) DEFAULT 'term'"),
        ("payment_transactions", "subtotal_usd", "FLOAT DEFAULT 47.62"),
        ("payment_transactions", "vat_amount_usd", "FLOAT DEFAULT 2.38"),
        ("payment_transactions", "discount_amount_usd", "FLOAT DEFAULT 0.0"),
        ("payment_transactions", "voucher_code", "VARCHAR(50)"),
        ("payment_transactions", "tax_invoice_number", "VARCHAR(100)"),
        ("payment_transactions", "idempotency_key", "VARCHAR(128)"),
        ("payment_transactions", "provider_event_id", "VARCHAR(128)"),
        ("payment_transactions", "refunded_at", "DATETIME"),
    ]),
    ("0003_auth_grading_content", [
        ("otp_codes", "attempt_count", "INTEGER DEFAULT 0"),
        ("otp_codes", "locked_at", "DATETIME"),
        ("learner_attempts", "idempotency_key", "VARCHAR(128)"),
        ("exam_simulation_results", "idempotency_key", "VARCHAR(128)"),
        ("lesson_versions", "status", "VARCHAR(20) DEFAULT 'published'"),
        ("lesson_versions", "published_at", "DATETIME"),
        ("lesson_versions", "created_by", "VARCHAR(36)"),
        ("lesson_versions", "reviewed_by", "VARCHAR(36)"),
    ]),
    ("0004_school_membership", [
        ("child_profiles", "school_id", "VARCHAR(100)"),
        ("child_profiles", "class_id", "VARCHAR(100)"),
    ]),
    ("0005_exam_session_id", [
        ("exam_simulation_results", "session_id", "VARCHAR(64)"),
    ]),
    ("0006_school_admin_and_user_school_id", [
        ("users", "school_id", "VARCHAR(100)"),
    ]),
    ("0007_scaling_indexes", [
        ("child_profiles", "ix_child_profiles_parent_id", "CREATE INDEX IF NOT EXISTS ix_child_profiles_parent_id ON child_profiles (parent_id)"),
        ("child_profiles", "ix_child_profiles_school_class", "CREATE INDEX IF NOT EXISTS ix_child_profiles_school_class ON child_profiles (school_id, class_id)"),
        ("term_access", "ix_term_access_lookup", "CREATE INDEX IF NOT EXISTS ix_term_access_lookup ON term_access (child_id, grade, term, is_unlocked)"),
        ("payment_transactions", "ix_payments_parent_id", "CREATE INDEX IF NOT EXISTS ix_payments_parent_id ON payment_transactions (parent_id)"),
        ("payment_transactions", "ix_payments_child_id", "CREATE INDEX IF NOT EXISTS ix_payments_child_id ON payment_transactions (child_id)"),
        ("payment_transactions", "ix_payments_child_created", "CREATE INDEX IF NOT EXISTS ix_payments_child_created ON payment_transactions (child_id, created_at)"),
        ("class_memberships", "ix_class_memberships_child_id", "CREATE INDEX IF NOT EXISTS ix_class_memberships_child_id ON class_memberships (child_id)"),
        ("tutor_class_assignments", "ix_tutor_class_assignments_class_id", "CREATE INDEX IF NOT EXISTS ix_tutor_class_assignments_class_id ON tutor_class_assignments (class_id)"),
        ("membership_audit_events", "ix_membership_audit_class_created", "CREATE INDEX IF NOT EXISTS ix_membership_audit_class_created ON membership_audit_events (class_id, created_at)"),
        ("lessons", "ix_lessons_grade_term_order", "CREATE INDEX IF NOT EXISTS ix_lessons_grade_term_order ON lessons (grade, term, lesson_order)"),
        ("lesson_versions", "ix_lesson_versions_active", "CREATE INDEX IF NOT EXISTS ix_lesson_versions_active ON lesson_versions (lesson_id, is_active)"),
        ("learner_attempts", "ix_learner_attempts_child_lesson", "CREATE INDEX IF NOT EXISTS ix_learner_attempts_child_lesson ON learner_attempts (child_id, lesson_id)"),
        ("learner_attempts", "ix_learner_attempts_child_created", "CREATE INDEX IF NOT EXISTS ix_learner_attempts_child_created ON learner_attempts (child_id, created_at)"),
        ("learner_mistakes", "ix_learner_mistakes_child_resolved", "CREATE INDEX IF NOT EXISTS ix_learner_mistakes_child_resolved ON learner_mistakes (child_id, is_resolved)"),
        ("tutor_submissions", "ix_tutor_submissions_status_created", "CREATE INDEX IF NOT EXISTS ix_tutor_submissions_status_created ON tutor_submissions (status, created_at)"),
        ("tutor_submissions", "ix_tutor_submissions_tutor_status", "CREATE INDEX IF NOT EXISTS ix_tutor_submissions_tutor_status ON tutor_submissions (tutor_id, status)"),
        ("assessment_sessions", "ix_assessment_sessions_child_status", "CREATE INDEX IF NOT EXISTS ix_assessment_sessions_child_status ON assessment_sessions (child_id, status)"),
    ]),
    ("0008_user_session_child_id", [
        ("user_sessions", "child_id", "VARCHAR(36)"),
        ("user_sessions", "ix_user_sessions_child_id", "CREATE INDEX IF NOT EXISTS ix_user_sessions_child_id ON user_sessions (child_id)"),
    ]),
]


def _ensure_version_table(conn):
    timestamp_type = "TIMESTAMP" if conn.dialect.name == "postgresql" else "DATETIME"
    conn.execute(text(f"CREATE TABLE IF NOT EXISTS schema_migrations (revision VARCHAR(80) PRIMARY KEY, applied_at {timestamp_type} DEFAULT CURRENT_TIMESTAMP NOT NULL)"))
    columns = {item["name"] for item in inspect(conn).get_columns("schema_migrations")}
    if "checksum" not in columns:
        conn.execute(text("ALTER TABLE schema_migrations ADD COLUMN checksum VARCHAR(64)"))


def _checksum(revision, columns):
    return hashlib.sha256(json.dumps([revision, columns], sort_keys=True).encode()).hexdigest()


def applied_revisions(conn):
    _ensure_version_table(conn)
    return {row[0] for row in conn.execute(text("SELECT revision FROM schema_migrations"))}


def upgrade():
    # Explicit bootstrap belongs to the migration command, never application startup.
    # Production startup only verifies the migration ledger; it never mutates
    # schema implicitly.
    from backend.database import Base
    import backend.models  # register metadata
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        applied = applied_revisions(conn)
        for revision, columns in MIGRATIONS:
            expected_checksum = _checksum(revision, columns)
            existing = conn.execute(text("SELECT checksum FROM schema_migrations WHERE revision=:revision"), {"revision": revision}).first()
            if existing and existing[0] and existing[0] != expected_checksum:
                raise RuntimeError(f"Migration checksum mismatch for {revision}; refusing to continue")
            if revision in applied:
                continue
            for table, target, definition in columns:
                inspector = inspect(conn)
                if table not in inspector.get_table_names():
                    continue
                if definition.startswith("CREATE INDEX"):
                    conn.execute(text(definition))
                else:
                    column = target
                    existing = {column_name["name"] for column_name in inspector.get_columns(table)}
                    if column not in existing:
                        normalized = definition.replace("DATETIME", "TIMESTAMP") if conn.dialect.name == "postgresql" else definition
                        normalized = normalized.replace("BOOLEAN DEFAULT 0", "BOOLEAN DEFAULT FALSE") if conn.dialect.name == "postgresql" else normalized
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {normalized}"))
            conn.execute(text("INSERT INTO schema_migrations(revision, checksum) VALUES (:revision, :checksum)"), {"revision": revision, "checksum": expected_checksum})


def pending_revisions():
    with engine.begin() as conn:
        applied = applied_revisions(conn)
        return [revision for revision, _ in MIGRATIONS if revision not in applied]


def require_current():
    with engine.connect() as conn:
        if "schema_migrations" not in inspect(conn).get_table_names():
            raise RuntimeError("Database has not been migrated. Run: python -m backend.migrations upgrade")
        applied = {row[0]: row[1] for row in conn.execute(text("SELECT revision, checksum FROM schema_migrations"))}
        for revision, columns in MIGRATIONS:
            if revision in applied and applied[revision] and applied[revision] != _checksum(revision, columns):
                raise RuntimeError(f"Migration checksum mismatch for {revision}")
    pending = [revision for revision, _ in MIGRATIONS if revision not in applied]
    if pending:
        raise RuntimeError("Database migrations are pending: " + ", ".join(pending))


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    if command == "upgrade":
        upgrade()
        print("Database is current.")
    elif command == "status":
        pending = pending_revisions()
        print("Pending: " + ", ".join(pending) if pending else "Database is current.")
    else:
        raise SystemExit("Usage: python -m backend.migrations status|upgrade")
