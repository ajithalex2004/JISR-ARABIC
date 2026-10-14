"""A child may only use their registered grade and grades the parent has paid for."""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.errors import ApplicationError
from backend.main import app
from backend.models import ChildProfile, Lesson, TermAccess, User
from backend.modules.curriculum.access import require_lesson
from backend.modules.curriculum.entitlements import entitled_grades
from backend.redis_client import _fallback_cache, _fallback_revoked_tokens
from backend.security import hash_password


class TestGradeEntitlements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = hash_password("ParentPass123!")

    def setUp(self):
        _fallback_cache.clear()
        _fallback_revoked_tokens.clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        with self.session() as db:
            db.add(User(id="parent_ann", email="parent.ann@test.local", full_name="Parent of Ann",
                        role="parent", password_hash=self.password_hash, is_verified=True))
            db.commit()
            db.add(ChildProfile(id="child_ann", parent_id="parent_ann", name="Ann Maria", gender="Girl", age=11,
                                school_name="School", default_grade=6, access_pin="1234"))
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

    def _unlock(self, grade, term=1):
        with self.session() as db:
            db.add(TermAccess(child_id="child_ann", grade=grade, term=term, is_unlocked=True))
            db.commit()

    def _parent_headers(self):
        res = self.client.post("/api/auth/login", json={"email": "parent.ann@test.local", "password": "ParentPass123!"})
        self.assertEqual(res.status_code, 200, res.text)
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    def _student_headers(self):
        res = self.client.post("/api/auth/student-pin-login", json={
            "parent_email": "parent.ann@test.local", "pin": "1234", "child_id": "child_ann"})
        self.assertEqual(res.status_code, 200, res.text)
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    def test_entitled_grades_are_registered_plus_paid(self):
        self._unlock(7)
        with self.session() as db:
            db.add(TermAccess(child_id="child_ann", grade=8, term=1, is_unlocked=False))
            db.commit()
            child = db.get(ChildProfile, "child_ann")
            self.assertEqual(entitled_grades(child, db), [6, 7])

    def test_parent_sees_only_registered_and_paid_grades(self):
        headers = self._parent_headers()
        self.assertEqual([g["grade"] for g in self.client.get("/api/curriculum/grades", headers=headers).json()], [6])
        self._unlock(7)
        self.assertEqual([g["grade"] for g in self.client.get("/api/curriculum/grades", headers=headers).json()], [6, 7])

    def test_student_sees_only_their_grade_even_with_other_paid_grades(self):
        self._unlock(7)
        grades = self.client.get("/api/curriculum/grades", headers=self._student_headers()).json()
        self.assertEqual([g["grade"] for g in grades], [6])

    def test_switching_grade_requires_payment(self):
        headers = self._parent_headers()
        res = self.client.post("/api/curriculum/active-grade", json={"child_id": "child_ann", "grade": 7}, headers=headers)
        self.assertEqual(res.status_code, 402, res.text)
        self._unlock(7)
        res = self.client.post("/api/curriculum/active-grade", json={"child_id": "child_ann", "grade": 7}, headers=headers)
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()["default_grade"], 7)
        # Grade 6 was registered but never paid for, so it is no longer open after the move.
        self.assertEqual(res.json()["entitled_grades"], [7])

    def test_student_cannot_switch_grade(self):
        self._unlock(7)
        res = self.client.post("/api/curriculum/active-grade", json={"child_id": "child_ann", "grade": 7},
                               headers=self._student_headers())
        self.assertEqual(res.status_code, 403, res.text)

    def test_educational_plan_cannot_move_to_unpaid_grade(self):
        res = self.client.post("/api/curriculum/onboarding-profile",
                               json={"child_id": "child_ann", "default_grade": 5}, headers=self._parent_headers())
        self.assertEqual(res.status_code, 402, res.text)
        with self.session() as db:
            self.assertEqual(db.get(ChildProfile, "child_ann").default_grade, 6)

    def test_lessons_of_other_grades_are_locked_even_free_chapters(self):
        child = SimpleNamespace(id="child_ann", name="Ann Maria", default_grade=6, term_accesses=[])
        demo_g5 = SimpleNamespace(grade=5, term=1, is_first_chapter_demo=True)
        demo_g6 = SimpleNamespace(grade=6, term=1, is_first_chapter_demo=True)
        actor = SimpleNamespace(role="parent", id="parent_ann", child_id=None)

        def db_for(lesson):
            db = MagicMock()
            db.get.side_effect = lambda model, _id: {Lesson: lesson, ChildProfile: child}.get(model)
            db.query.return_value.filter.return_value.all.return_value = []
            return db

        from unittest.mock import patch
        with patch("backend.modules.curriculum.access.optional_child"):
            with self.assertRaises(ApplicationError) as ctx:
                require_lesson(db_for(demo_g5), actor, "lesson_01_ball_games", child_id="child_ann")
            self.assertEqual(ctx.exception.status_code, 402)
            self.assertIs(require_lesson(db_for(demo_g6), actor, "lesson_g6_t1_ch01", child_id="child_ann"), demo_g6)


if __name__ == "__main__":
    unittest.main()
