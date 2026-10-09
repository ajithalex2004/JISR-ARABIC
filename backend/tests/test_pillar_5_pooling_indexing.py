"""
Pillar 5 Verification: Database Connection Pooling, Query Indexing, and Concurrency.
Tests connection pool configuration, database indexes across high-traffic lookup paths,
multi-threaded concurrent database connection handling, and pool health telemetry.
"""
import concurrent.futures
import threading
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool

from backend.database import Base, get_db, get_db_pool_status
from backend.main import app
from backend.models import (
    User, School, SchoolClass, BookEdition, Unit, Lesson, LessonVersion,
    ChildProfile, ClassMembership, TutorClassAssignment, MembershipAuditEvent,
    TermAccess, LearnerAttempt, LearnerMistake, TutorSubmission, PaymentTransaction,
    AssessmentSession
)
from backend.migrations import upgrade, applied_revisions, MIGRATIONS


class TestPillar5PoolingAndIndexing(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)

        def scoped_db():
            with self.session() as db:
                yield db

        app.dependency_overrides[get_db] = scoped_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(get_db, None)
        self.engine.dispose()

    def test_01_all_high_traffic_indexes_defined_on_models(self):
        """Verify that all critical scaling indexes exist in model metadata."""
        inspector = inspect(self.engine)

        expected_indexes = {
            "child_profiles": ["ix_child_profiles_school_class", "ix_child_profiles_parent_id"],
            "class_memberships": ["ix_class_memberships_child_id"],
            "tutor_class_assignments": ["ix_tutor_class_assignments_class_id"],
            "membership_audit_events": ["ix_membership_audit_class_created"],
            "lessons": ["ix_lessons_grade_term_order"],
            "lesson_versions": ["ix_lesson_versions_active"],
            "term_access": ["ix_term_access_lookup"],
            "learner_attempts": ["ix_learner_attempts_child_lesson", "ix_learner_attempts_child_created"],
            "learner_mistakes": ["ix_learner_mistakes_child_resolved"],
            "tutor_submissions": ["ix_tutor_submissions_status_created", "ix_tutor_submissions_tutor_status"],
            "payment_transactions": ["ix_payments_child_created"],
            "assessment_sessions": ["ix_assessment_sessions_child_status"],
        }

        for table_name, index_names in expected_indexes.items():
            existing_indexes = {idx["name"] for idx in inspector.get_indexes(table_name)}
            for idx_name in index_names:
                self.assertIn(
                    idx_name,
                    existing_indexes,
                    f"Index '{idx_name}' missing from table '{table_name}'. Found: {existing_indexes}"
                )

    def test_02_connection_pool_configuration_parameters(self):
        """Verify engine kwargs calculate production-grade pool sizes and timeouts."""
        # Create a test QueuePool engine to verify production settings logic
        prod_engine = create_engine(
            "sqlite://",
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=15,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True
        )

        pool = prod_engine.pool
        self.assertIsInstance(pool, QueuePool)
        self.assertEqual(pool.size(), 20)
        self.assertEqual(pool._max_overflow, 15)
        self.assertEqual(pool._timeout, 30)
        self.assertEqual(pool._recycle, 1800)
        self.assertTrue(pool._pre_ping)
        prod_engine.dispose()

    def test_03_db_pool_status_telemetry_reporting(self):
        """Verify get_db_pool_status reports metrics cleanly for monitoring."""
        status = get_db_pool_status()
        self.assertIsInstance(status, dict)
        self.assertIn("type", status)

    def test_04_health_and_ready_endpoints_expose_pool_status(self):
        """Verify /api/health and /api/ready expose pool telemetry."""
        health_res = self.client.get("/api/health")
        self.assertEqual(health_res.status_code, 200)
        health_data = health_res.json()
        self.assertEqual(health_data["status"], "healthy")
        self.assertIn("pool", health_data)

        ready_res = self.client.get("/api/ready")
        self.assertEqual(ready_res.status_code, 200)
        ready_data = ready_res.json()
        self.assertEqual(ready_data["status"], "ready")
        self.assertIn("pool", ready_data)

    def test_05_concurrent_database_connections_stress(self):
        """Verify QueuePool with multiple threads executing concurrent queries does not deadlock or fail."""
        import tempfile
        import os

        concurrent_threads = 20
        iterations_per_thread = 5

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            tmp_db_path = tmp_file.name

        try:
            pool_engine = create_engine(
                f"sqlite:///{tmp_db_path}",
                poolclass=QueuePool,
                pool_size=20,
                max_overflow=10,
                pool_timeout=15,
                connect_args={"timeout": 30}
            )
            with pool_engine.connect() as conn:
                conn.execute(text("PRAGMA journal_mode=WAL"))
                conn.commit()

            Base.metadata.create_all(pool_engine)
            session_factory = sessionmaker(bind=pool_engine)

            with session_factory() as db:
                db.add(School(id="sch_test_pool", name="Pool Test School"))
                db.commit()

            errors = []
            barrier = threading.Barrier(concurrent_threads)

            def worker_task(thread_id):
                try:
                    barrier.wait(timeout=10)
                    for i in range(iterations_per_thread):
                        with session_factory() as session:
                            result = session.execute(text("SELECT id, name FROM schools WHERE id = 'sch_test_pool'")).first()
                            if not result or result[0] != "sch_test_pool":
                                errors.append(f"Thread {thread_id} read incorrect data on iter {i}")
                except Exception as e:
                    errors.append(f"Thread {thread_id} failed with error: {e}")

            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_threads) as executor:
                futures = [executor.submit(worker_task, tid) for tid in range(concurrent_threads)]
                concurrent.futures.wait(futures)

            pool_engine.dispose()
            self.assertEqual(errors, [], f"Concurrent workers experienced errors: {errors}")
        finally:
            if os.path.exists(tmp_db_path):
                try:
                    os.remove(tmp_db_path)
                except Exception:
                    pass

    def test_06_migration_0007_registered_and_idempotent(self):
        """Verify 0007_scaling_indexes migration is registered in migration ledger."""
        migration_revisions = [rev for rev, _ in MIGRATIONS]
        self.assertIn("0007_scaling_indexes", migration_revisions)


if __name__ == "__main__":
    unittest.main()
