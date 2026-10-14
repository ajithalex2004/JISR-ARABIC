"""Admins can find a student by student or parent name and correct their saved grade."""
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import ChildProfile, TermAccess, User
from backend.redis_client import _fallback_cache, _fallback_rate_buckets, _fallback_revoked_tokens
from backend.security import hash_password


class TestAdminStudents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = hash_password("Pass12345!")

    def setUp(self):
        _fallback_cache.clear()
        _fallback_revoked_tokens.clear()
        _fallback_rate_buckets.clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        with self.session() as db:
            db.add(User(id="parent_ann", email="parent.ann@test.local", full_name="Alex Joseph",
                        role="parent", password_hash=self.password_hash, is_verified=True))
            db.add(User(id="admin_user", email="admin@test.local", full_name="Admin",
                        role="admin", password_hash=self.password_hash, is_verified=True))
            db.commit()
            db.add(ChildProfile(id="child_ann", parent_id="parent_ann", name="Ann Maria", default_grade=5))
            db.add(ChildProfile(id="child_sam", parent_id="parent_ann", name="Sam", default_grade=3))
            db.commit()
            db.add(TermAccess(child_id="child_ann", grade=5, term=1, is_unlocked=True))
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
        _fallback_rate_buckets.clear()

    def _headers(self, email):
        res = self.client.post("/api/auth/login", json={"email": email, "password": "Pass12345!"})
        self.assertEqual(res.status_code, 200, res.text)
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    def test_search_by_student_and_parent_name(self):
        headers = self._headers("admin@test.local")
        by_student = self.client.get("/api/admin/students", params={"q": "ann m"}, headers=headers)
        self.assertEqual(by_student.status_code, 200, by_student.text)
        self.assertEqual([s["id"] for s in by_student.json()], ["child_ann"])
        ann = by_student.json()[0]
        self.assertEqual(ann["default_grade"], 5)
        self.assertEqual(ann["entitled_grades"], [5])
        self.assertEqual(ann["unlocked_terms"], ["grade_5_term_1"])
        self.assertEqual(ann["parent_email"], "parent.ann@test.local")

        by_parent = self.client.get("/api/admin/students", params={"q": "joseph"}, headers=headers)
        self.assertEqual(sorted(s["id"] for s in by_parent.json()), ["child_ann", "child_sam"])

    def test_admin_sets_grade_without_payment(self):
        headers = self._headers("admin@test.local")
        res = self.client.put("/api/admin/students/child_ann/grade", json={"grade": 6}, headers=headers)
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()["default_grade"], 6)
        self.assertEqual(res.json()["entitled_grades"], [5, 6])
        with self.session() as db:
            self.assertEqual(db.get(ChildProfile, "child_ann").default_grade, 6)

    def test_invalid_grade_and_unknown_student(self):
        headers = self._headers("admin@test.local")
        self.assertEqual(self.client.put("/api/admin/students/child_ann/grade", json={"grade": 13}, headers=headers).status_code, 400)
        self.assertEqual(self.client.put("/api/admin/students/nobody/grade", json={"grade": 6}, headers=headers).status_code, 404)

    def test_parents_cannot_use_admin_students(self):
        headers = self._headers("parent.ann@test.local")
        self.assertEqual(self.client.get("/api/admin/students", headers=headers).status_code, 403)
        res = self.client.put("/api/admin/students/child_ann/grade", json={"grade": 6}, headers=headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(self.client.get("/api/admin/students").status_code, 401)


if __name__ == "__main__":
    unittest.main()
