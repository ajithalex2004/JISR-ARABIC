"""The welcome page's journey shows a signed-in family their child's real activity per chapter."""
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import ChildProfile, LearnerAttempt, Lesson, Unit, User
from backend.redis_client import _fallback_cache, _fallback_rate_buckets, _fallback_revoked_tokens
from backend.security import hash_password


class TestLessonJourney(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = hash_password("ParentPass123!")

    def setUp(self):
        for cache in (_fallback_cache, _fallback_revoked_tokens, _fallback_rate_buckets):
            cache.clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        with self.session() as db:
            for who in ("ann", "bob"):
                db.add(User(id=f"parent_{who}", email=f"{who}@test.local", full_name=who, role="parent",
                            password_hash=self.password_hash, is_verified=True))
            db.add(Unit(id="u", book_edition_id="b", unit_number=1, title_ar="و", title_en="U"))
            db.commit()
            db.add(ChildProfile(id="kid_ann", parent_id="parent_ann", name="Ann", default_grade=5))
            db.add_all([Lesson(id=f"g5_{i}", unit_id="u", grade=5, term=1, lesson_order=i, title_ar="د", title_en="L",
                               start_page=6) for i in (1, 2)])
            db.add(Lesson(id="g6_1", unit_id="u", grade=6, term=1, lesson_order=1, title_ar="د", title_en="L", start_page=6))
            db.commit()
            for i, ok in enumerate([True, True, False]):
                db.add(LearnerAttempt(child_id="kid_ann", lesson_id="g5_1", activity_id=f"a{i}", is_correct=ok))
            db.add(LearnerAttempt(child_id="kid_ann", lesson_id="g6_1", activity_id="x", is_correct=True))
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

    def _headers(self, who):
        res = self.client.post("/api/auth/login", json={"email": f"{who}@test.local", "password": "ParentPass123!"})
        self.assertEqual(res.status_code, 200, res.text)
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    def test_counts_only_this_class_and_term(self):
        res = self.client.get("/api/curriculum/journey?child_id=kid_ann&grade=5&term=1", headers=self._headers("ann"))
        self.assertEqual(res.status_code, 200, res.text)
        lessons = {l["lesson_id"]: l for l in res.json()["lessons"]}
        self.assertEqual(set(lessons), {"g5_1"})  # g5_2 untouched, g6_1 is another class
        self.assertEqual((lessons["g5_1"]["attempts"], lessons["g5_1"]["correct"]), (3, 2))
        self.assertIsNotNone(lessons["g5_1"]["last_activity"])

    def test_needs_a_login_and_the_childs_own_family(self):
        self.assertEqual(self.client.get("/api/curriculum/journey?child_id=kid_ann&grade=5").status_code, 401)
        res = self.client.get("/api/curriculum/journey?child_id=kid_ann&grade=5", headers=self._headers("bob"))
        self.assertIn(res.status_code, (403, 404))


if __name__ == "__main__":
    unittest.main()
