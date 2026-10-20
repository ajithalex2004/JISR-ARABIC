"""Guests may read the textbook pages of a book's free first chapter, and only those."""
import datetime
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import Lesson, Unit, User, UserSession
from backend.modules.curriculum.access import free_chapter_pages
from backend.redis_client import _fallback_rate_buckets
from backend.security import create_access_token, decode_access_token, hash_password


class TestFreeChapterPages(unittest.TestCase):
    def setUp(self):
        _fallback_rate_buckets.clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        with self.session() as db:
            db.add(User(id="p1", email="p1@test.local", full_name="p", role="parent",
                        password_hash=hash_password("TestPassword123!"), is_verified=True))
            db.add(Unit(id="u1", book_edition_id="moe_gr5_vol1_2023", unit_number=1, title_ar="و", title_en="U"))
            db.commit()
            # Chapter 1 starts on printed page 7 (PDF page 8); chapter 2 on printed page 17 (PDF page 18).
            db.add_all([
                Lesson(id="c1", unit_id="u1", grade=5, term=1, lesson_order=1, title_ar="د", title_en="L1",
                       start_page=7, is_first_chapter_demo=True),
                Lesson(id="c2", unit_id="u1", grade=5, term=1, lesson_order=2, title_ar="د", title_en="L2", start_page=17),
            ])
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

    def auth(self):
        token = create_access_token({"sub": "p1", "role": "parent"})
        payload = decode_access_token(token)
        with self.session() as db:
            db.add(UserSession(id=payload["jti"], user_id="p1",
                               expires_at=datetime.datetime.utcfromtimestamp(payload["exp"])))
            db.commit()
        return {"Authorization": f"Bearer {token}"}

    def test_free_chapter_pages(self):
        with self.session() as db:
            self.assertEqual(free_chapter_pages(None, db), set(range(8, 18)))
            self.assertEqual(free_chapter_pages("moe_gr5_vol2_2023", db), set())
            self.assertEqual(free_chapter_pages("../etc", db), set())

    def test_guests_read_only_the_free_chapter(self):
        self.assertEqual(self.client.get("/api/admin/ocr-page/14").status_code, 200)
        self.assertEqual(self.client.get("/api/admin/ocr-page/30").status_code, 401)
        self.assertEqual(self.client.get("/api/admin/ocr-page/14?edition_id=moe_gr5_vol2_2023").status_code, 401)
        self.assertEqual(self.client.get("/api/admin/ocr-page/30", headers=self.auth()).status_code, 200)

    def test_lesson_package_names_its_book_and_pages(self):
        res = self.client.get("/api/curriculum/lesson/c1")
        self.assertEqual(res.status_code, 200, res.text)
        lesson = res.json()["lesson"]
        self.assertEqual(lesson["edition_id"], "moe_gr5_vol1_2023")
        self.assertEqual(lesson["chapter_pages"], list(range(8, 18)))
        # Every page the lesson lists is one a guest may read.
        with self.session() as db:
            self.assertTrue(set(lesson["chapter_pages"]) <= free_chapter_pages(lesson["edition_id"], db))


if __name__ == "__main__":
    unittest.main()
