import datetime
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import User, ChildProfile, UserSession
from backend.security import hash_password
from backend.redis_client import _fallback_cache, _fallback_revoked_tokens

class TestSingleDeviceAndGradeLimit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = hash_password("ParentPass123!")

    def setUp(self):
        # Clear in-memory caches
        _fallback_cache.clear()
        _fallback_revoked_tokens.clear()

        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)

        with self.session() as db:
            # Parent user
            parent = User(
                id="parent_ann",
                email="parent.ann@test.local",
                full_name="Parent of Ann",
                role="parent",
                password_hash=self.password_hash,
                is_verified=True
            )
            # Admin user
            admin = User(
                id="admin_user",
                email="admin@jisr.ae",
                full_name="Admin",
                role="admin",
                password_hash=self.password_hash,
                is_verified=True
            )
            db.add(parent)
            db.add(admin)
            db.commit()

            # Ann Maria: Grade 6
            child = ChildProfile(
                id="child_ann",
                parent_id="parent_ann",
                name="Ann Maria",
                gender="Girl",
                age=11,
                school_name="Abu Dhabi International School",
                default_grade=6,
                access_pin="1234",
                curriculum_stream="MoE / UAE Advanced Stream"
            )
            db.add(child)
            db.commit()

        def scoped_db():
            with self.session() as db:
                yield db

        app.dependency_overrides[get_db] = scoped_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(get_db, None)
        self.engine.dispose()

    def test_single_device_login_and_grade_restrictions(self):
        # 1. Student logs in from Device 1
        res1 = self.client.post("/api/auth/student-pin-login", json={
            "parent_email": "parent.ann@test.local",
            "pin": "1234",
            "child_id": "child_ann"
        })
        self.assertEqual(res1.status_code, 200, res1.text)
        token_device_1 = res1.json()["access_token"]
        headers_device_1 = {"Authorization": f"Bearer {token_device_1}"}

        # Device 1 accesses /api/curriculum/grades -> should ONLY return Grade 6
        grades_res1 = self.client.get("/api/curriculum/grades", headers=headers_device_1)
        self.assertEqual(grades_res1.status_code, 200)
        grades_data1 = grades_res1.json()
        self.assertEqual(len(grades_data1), 1)
        self.assertEqual(grades_data1[0]["grade"], 6)

        # 2. Student logs in from Device 2 with the same credentials
        res2 = self.client.post("/api/auth/student-pin-login", json={
            "parent_email": "parent.ann@test.local",
            "pin": "1234",
            "child_id": "child_ann"
        })
        self.assertEqual(res2.status_code, 200, res2.text)
        token_device_2 = res2.json()["access_token"]
        headers_device_2 = {"Authorization": f"Bearer {token_device_2}"}

        # Device 2 works fine and returns Grade 6
        grades_res2 = self.client.get("/api/curriculum/grades", headers=headers_device_2)
        self.assertEqual(grades_res2.status_code, 200)
        grades_data2 = grades_res2.json()
        self.assertEqual(len(grades_data2), 1)
        self.assertEqual(grades_data2[0]["grade"], 6)

        # 3. Device 1 attempts to make an authenticated request -> MUST be rejected (401)
        stale_res = self.client.get("/api/curriculum/grades", headers=headers_device_1)
        self.assertEqual(stale_res.status_code, 401, f"Expected 401 but got {stale_res.status_code}: {stale_res.text}")
        self.assertIn("logged out", stale_res.json()["detail"].lower())

        # 4. Parent logs in -> /api/curriculum/grades should ONLY return their enrolled children's grades [6]
        login_res = self.client.post("/api/auth/login", json={
            "email": "parent.ann@test.local",
            "password": "ParentPass123!"
        })
        self.assertEqual(login_res.status_code, 200)
        parent_headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

        parent_grades = self.client.get("/api/curriculum/grades", headers=parent_headers)
        self.assertEqual(parent_grades.status_code, 200)
        self.assertEqual(len(parent_grades.json()), 1)
        self.assertEqual(parent_grades.json()[0]["grade"], 6)

        # 5. Admin logs in -> /api/curriculum/grades returns all 12 grades
        admin_login = self.client.post("/api/auth/login", json={
            "email": "admin@jisr.ae",
            "password": "ParentPass123!"
        })
        self.assertEqual(admin_login.status_code, 200)
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
        admin_grades = self.client.get("/api/curriculum/grades", headers=admin_headers)
        self.assertEqual(admin_grades.status_code, 200)
        self.assertEqual(len(admin_grades.json()), 12)

if __name__ == '__main__':
    unittest.main()
