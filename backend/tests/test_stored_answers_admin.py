"""Admins can review and clear stored question-paper answers; a cleared paper is read again by the AI."""
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import DocumentSolutionCache, User
from backend.modules.tutoring import caching
from backend.redis_client import _fallback_cache, _fallback_rate_buckets, _fallback_revoked_tokens
from backend.security import hash_password

QUESTIONS = [{"question_number": 1, "question_text_ar": "ما ضد كلمة كبير؟", "question_text_en": "Opposite of big?",
              "model_answer_ar": "صَغِيرٌ", "model_answer_en": "small", "explanation_ar": "", "explanation_en": "",
              "textbook_reference": ""}]


class TestStoredAnswersAdmin(unittest.TestCase):
    def setUp(self):
        for cache in (_fallback_cache, _fallback_revoked_tokens, _fallback_rate_buckets, caching._L1_MEMORY_CACHE):
            cache.clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        password = hash_password("Pass12345!")
        with self.session() as db:
            db.add_all([User(id="admin_user", email="admin@test.local", full_name="Admin", role="admin",
                             password_hash=password, is_verified=True),
                        User(id="parent_1", email="p1@test.local", full_name="Parent", role="parent",
                             password_hash=password, is_verified=True)])
            db.commit()
            for name in ("unit-2.pdf", "unit-3.pdf"):
                caching.save_cached_paper(caching.compute_content_hash(name), None, name, "application/pdf",
                                          f"Paper {name}", QUESTIONS, db=db)

        def scoped_db():
            with self.session() as db:
                yield db

        app.dependency_overrides[get_db] = scoped_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.pop(get_db, None)
        self.engine.dispose()
        caching._L1_MEMORY_CACHE.clear()

    def _headers(self, email="admin@test.local"):
        _fallback_rate_buckets.clear()
        res = self.client.post("/api/auth/login", json={"email": email, "password": "Pass12345!"})
        self.assertEqual(res.status_code, 200, res.text)
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    def _stored(self, name):
        with self.session() as db:
            return caching.get_cached_paper(caching.compute_content_hash(name), None, db=db)

    def test_admin_lists_views_and_clears_one_paper(self):
        admin = self._headers()
        listing = self.client.get("/api/admin/stored-answers", headers=admin).json()
        self.assertEqual(listing["total"], 2)
        paper = next(p for p in listing["papers"] if p["file_name"] == "unit-2.pdf")
        self.assertEqual((paper["paper_title"], paper["total_questions"]), ("Paper unit-2.pdf", 1))

        detail = self.client.get(f"/api/admin/stored-answers/{paper['id']}", headers=admin).json()
        self.assertEqual(detail["questions"][0]["model_answer_ar"], "صَغِيرٌ")

        self.assertIsNotNone(self._stored("unit-2.pdf"))  # served from the in-memory copy too
        res = self.client.delete(f"/api/admin/stored-answers/{paper['id']}", headers=admin)
        self.assertEqual(res.json(), {"deleted": 1})
        self.assertIsNone(self._stored("unit-2.pdf"))  # gone from memory and database: next upload uses the AI
        self.assertIsNotNone(self._stored("unit-3.pdf"))  # other papers are kept
        self.assertEqual(self.client.delete(f"/api/admin/stored-answers/{paper['id']}", headers=admin).status_code, 404)
        self.assertEqual(self.client.get(f"/api/admin/stored-answers/{paper['id']}", headers=admin).status_code, 404)

    def test_clear_all_needs_confirmation(self):
        admin = self._headers()
        self.assertEqual(self.client.delete("/api/admin/stored-answers", headers=admin).status_code, 400)
        self.assertEqual(self.client.get("/api/admin/stored-answers", headers=admin).json()["total"], 2)
        res = self.client.delete("/api/admin/stored-answers", params={"confirm": "all"}, headers=admin)
        self.assertEqual(res.json(), {"deleted": 2})
        self.assertEqual(self.client.get("/api/admin/stored-answers", headers=admin).json()["total"], 0)
        self.assertIsNone(self._stored("unit-3.pdf"))

    def test_only_admins_can_see_or_clear(self):
        parent = self._headers("p1@test.local")
        for method, path in (("get", "/api/admin/stored-answers"), ("get", "/api/admin/stored-answers/1"),
                             ("delete", "/api/admin/stored-answers/1"), ("delete", "/api/admin/stored-answers?confirm=all")):
            self.assertEqual(getattr(self.client, method)(path, headers=parent).status_code, 403, path)
        self.assertEqual(self.client.get("/api/admin/stored-answers").status_code, 401)
        with self.session() as db:
            self.assertEqual(db.query(DocumentSolutionCache).count(), 2)

    def test_a_clear_in_one_worker_drops_the_in_memory_copy_in_the_others(self):
        key = caching.compute_content_hash("unit-3.pdf")
        self.assertIsNotNone(caching._l1_get(key))
        # Another worker's in-memory copy, made before the clear (it carries the old generation).
        stale = dict(caching._L1_MEMORY_CACHE[key])
        with self.session() as db:
            caching.clear_cached_papers(db)
        caching._L1_MEMORY_CACHE[key] = stale  # this worker never saw the clear itself
        self.assertIsNone(caching._l1_get(key))
        self.assertNotIn(key, caching._L1_MEMORY_CACHE)


if __name__ == "__main__":
    unittest.main()
