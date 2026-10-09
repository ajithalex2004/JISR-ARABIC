"""
Pillar 6 Verification: Background Task Processing & Asynchronous Worker Queue.
Tests task enqueueing, state management, worker execution lifecycle,
asynchronous audio generation, bulk student enrollment, weekly digests,
multi-tenant authorization on task status endpoints, and queue telemetry.
"""
import json
import datetime
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import (
    User, ChildProfile, School, SchoolClass, ClassMembership,
    MembershipAuditEvent, UserSession,
)
from backend.security import hash_password, create_access_token, decode_access_token
from backend.tasks.queue import (
    enqueue_task,
    get_task_status,
    update_task_status,
    get_queue_metrics,
    list_recent_tasks,
    clear_task_queue,
)
from backend.tasks.handlers import set_task_session_factory
from backend.tasks.worker import TaskWorker


class TestPillar6TaskQueue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = hash_password("SecurePass123!")

    def setUp(self):
        clear_task_queue()
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
        set_task_session_factory(self.session)

        with self.session() as db:
            # Seed users
            self.admin = User(id="usr_admin", email="admin@jisr.ae", full_name="Super Admin", role="admin", is_verified=True, password_hash=self.password_hash)
            self.school_admin_1 = User(id="usr_sa1", email="sa1@jisr.ae", full_name="School Admin 1", role="school_admin", school_id="sch_1", is_verified=True, password_hash=self.password_hash)
            self.school_admin_2 = User(id="usr_sa2", email="sa2@jisr.ae", full_name="School Admin 2", role="school_admin", school_id="sch_2", is_verified=True, password_hash=self.password_hash)
            self.parent_1 = User(id="usr_p1", email="parent1@jisr.ae", full_name="Parent 1", role="parent", is_verified=True, password_hash=self.password_hash)
            self.parent_2 = User(id="usr_p2", email="parent2@jisr.ae", full_name="Parent 2", role="parent", is_verified=True, password_hash=self.password_hash)

            db.add_all([self.admin, self.school_admin_1, self.school_admin_2, self.parent_1, self.parent_2])

            # Seed schools and classes
            self.school_1 = School(id="sch_1", name="Al Ittihad Academy")
            self.school_2 = School(id="sch_2", name="Al Nahda School")
            self.class_1a = SchoolClass(id="cls_1a", school_id="sch_1", name="Grade 5A", grade=5, is_active=True)
            self.class_2a = SchoolClass(id="cls_2a", school_id="sch_2", name="Grade 5B", grade=5, is_active=True)

            db.add_all([self.school_1, self.school_2, self.class_1a, self.class_2a])

            # Seed learners
            self.child_1 = ChildProfile(id="ch_1", parent_id="usr_p1", name="Zayd", school_id="sch_1", default_grade=5)
            self.child_2 = ChildProfile(id="ch_2", parent_id="usr_p1", name="Fatima", school_id="sch_1", default_grade=5)
            self.child_3 = ChildProfile(id="ch_3", parent_id="usr_p2", name="Tariq", school_id="sch_2", default_grade=5)

            db.add_all([self.child_1, self.child_2, self.child_3])
            db.commit()

        def scoped_db():
            with self.session() as db:
                yield db

        app.dependency_overrides[get_db] = scoped_db
        self.client = TestClient(app)
        self.worker = TaskWorker(worker_id="test-worker")

    def tearDown(self):
        set_task_session_factory(None)
        clear_task_queue()
        self.client.close()
        app.dependency_overrides.pop(get_db, None)
        self.engine.dispose()

    def auth_headers(self, user_id: str, role: str = "parent", school_id: str = None, child_id: str = None) -> dict:
        token_payload = {
            "sub": user_id,
            "role": role,
            "school_id": school_id,
            "child_id": child_id,
            "session_kind": "learner" if role == "learner" else None,
        }
        token = create_access_token(token_payload)
        payload = decode_access_token(token)
        with self.session() as db:
            db.add(UserSession(
                id=payload["jti"],
                user_id=user_id,
                expires_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(days=1)
            ))
            db.commit()
        return {"Authorization": f"Bearer {token}"}

    def test_01_task_enqueue_and_status_tracking(self):
        """Verify task lifecycle states: pending -> running -> completed."""
        task = enqueue_task(
            task_type="test_task",
            params={"number": 42},
            actor_id="usr_p1"
        )
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.progress, 0)

        # Status inspection
        fetched = get_task_status(task.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.params["number"], 42)

        # Update to running
        running = update_task_status(task.id, status="running", progress=50)
        self.assertEqual(running.status, "running")
        self.assertEqual(running.progress, 50)
        self.assertIsNotNone(running.started_at)

        # Complete
        completed = update_task_status(task.id, status="completed", progress=100, result={"output": 84})
        self.assertEqual(completed.status, "completed")
        self.assertEqual(completed.progress, 100)
        self.assertEqual(completed.result["output"], 84)
        self.assertIsNotNone(completed.completed_at)

    def test_02_task_worker_processes_registered_handler(self):
        """Verify TaskWorker pops and executes registered task handler."""
        task = enqueue_task(
            task_type="synthesize_audio",
            params={"text": "صباح الخير", "speed": 1.0, "lang": "ar-SA"},
            actor_id="usr_p1"
        )
        self.assertEqual(task.status, "pending")

        processed = self.worker.process_one_task(timeout=1)
        self.assertTrue(processed)

        finished = get_task_status(task.id)
        self.assertEqual(finished.status, "completed")
        self.assertEqual(finished.progress, 100)
        self.assertIsNotNone(finished.result)
        self.assertIn("audio_url", finished.result)

    def test_03_task_worker_handles_failure_gracefully(self):
        """Verify TaskWorker catches exceptions and marks tasks as failed with errors."""
        task = enqueue_task(
            task_type="unregistered_type",
            params={},
            actor_id="usr_p1"
        )
        processed = self.worker.process_one_task(timeout=1)
        self.assertTrue(processed)

        failed = get_task_status(task.id)
        self.assertEqual(failed.status, "failed")
        self.assertIn("No handler registered", failed.error)

    def test_04_async_audio_synthesis_api(self):
        """Verify POST /api/audio/synthesize-async enqueues and allows polling."""
        headers = self.auth_headers("usr_p1", role="parent")
        res = self.client.post(
            "/api/audio/synthesize-async",
            headers=headers,
            json={"text": "أهلاً وسهلاً بك في جسر العربية", "speed": 1.0, "lang": "ar-SA"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("task_id", data)
        self.assertEqual(data["status"], "pending")

        task_id = data["task_id"]

        # Process via worker
        self.worker.process_one_task(timeout=1)

        # Poll status
        poll_res = self.client.get(f"/api/tasks/{task_id}", headers=headers)
        self.assertEqual(poll_res.status_code, 200)
        poll_data = poll_res.json()
        self.assertEqual(poll_data["status"], "completed")
        self.assertEqual(poll_data["progress"], 100)
        self.assertIsNotNone(poll_data["result"]["audio_url"])

    def test_05_bulk_enroll_learners_background_job(self):
        """Verify asynchronous bulk learner enrollment into a school class."""
        headers = self.auth_headers("usr_sa1", role="school_admin", school_id="sch_1")
        res = self.client.post(
            "/api/admin/schools/classes/cls_1a/bulk-enroll",
            headers=headers,
            json={"learner_ids": ["ch_1", "ch_2"]}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("task_id", data)
        self.assertEqual(data["total_learners"], 2)

        # Worker processes the enrollment
        self.worker.process_one_task(timeout=1)

        # Check task completion
        status_res = self.client.get(f"/api/tasks/{data['task_id']}", headers=headers)
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.json()
        self.assertEqual(status_data["status"], "completed")
        self.assertEqual(status_data["result"]["enrolled_count"], 2)

        # Verify DB memberships
        with self.session() as db:
            m1 = db.get(ClassMembership, ("cls_1a", "ch_1"))
            m2 = db.get(ClassMembership, ("cls_1a", "ch_2"))
            self.assertIsNotNone(m1)
            self.assertIsNotNone(m2)

            audits = db.query(MembershipAuditEvent).filter(MembershipAuditEvent.class_id == "cls_1a").all()
            self.assertGreaterEqual(len(audits), 2)

    def test_06_async_weekly_digest_dispatch(self):
        """Verify POST /api/parent/send-digest-async/{child_id} dispatches digest via worker."""
        headers = self.auth_headers("usr_p1", role="parent")
        res = self.client.post(
            "/api/parent/send-digest-async/ch_1",
            headers=headers,
            json={"channel": "in_app_notification"}
        )
        self.assertEqual(res.status_code, 200)
        task_id = res.json()["task_id"]

        # Worker processes digest
        self.worker.process_one_task(timeout=1)

        poll = self.client.get(f"/api/tasks/{task_id}", headers=headers)
        self.assertEqual(poll.status_code, 200)
        self.assertEqual(poll.json()["status"], "completed")
        self.assertTrue(poll.json()["result"]["success"])

    def test_07_task_authorization_and_multi_tenant_boundaries(self):
        """Verify multi-tenant barriers prevent unauthorized principals from viewing other tasks."""
        # Parent 1 creates a task
        p1_task = enqueue_task(
            task_type="test_task",
            params={},
            actor_id="usr_p1",
            school_id="sch_1"
        )

        p1_headers = self.auth_headers("usr_p1", role="parent")
        p2_headers = self.auth_headers("usr_p2", role="parent")
        sa1_headers = self.auth_headers("usr_sa1", role="school_admin", school_id="sch_1")
        sa2_headers = self.auth_headers("usr_sa2", role="school_admin", school_id="sch_2")
        admin_headers = self.auth_headers("usr_admin", role="admin")

        # Parent 1 can inspect their own task
        self.assertEqual(self.client.get(f"/api/tasks/{p1_task.id}", headers=p1_headers).status_code, 200)

        # Parent 2 is forbidden
        self.assertEqual(self.client.get(f"/api/tasks/{p1_task.id}", headers=p2_headers).status_code, 403)

        # School Admin 1 (same school) can inspect
        self.assertEqual(self.client.get(f"/api/tasks/{p1_task.id}", headers=sa1_headers).status_code, 200)

        # School Admin 2 (different school) is forbidden
        self.assertEqual(self.client.get(f"/api/tasks/{p1_task.id}", headers=sa2_headers).status_code, 403)

        # Super Admin can inspect any task
        self.assertEqual(self.client.get(f"/api/tasks/{p1_task.id}", headers=admin_headers).status_code, 200)

    def test_08_health_and_readiness_report_task_metrics(self):
        """Verify /api/health and /api/ready expose task queue telemetry."""
        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)
        h_data = health.json()
        self.assertIn("tasks", h_data)
        self.assertIn("queue_depth", h_data["tasks"])
        self.assertIn("backend", h_data["tasks"])

        ready = self.client.get("/api/ready")
        self.assertEqual(ready.status_code, 200)
        r_data = ready.json()
        self.assertIn("tasks", r_data)
        self.assertIn(r_data["checks"]["task_queue"], ["ok", "healthy"])


if __name__ == "__main__":
    unittest.main()
