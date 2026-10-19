"""Teacher review of Arabic-English word matches."""
import datetime
import json
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import SentenceAlignment, User, UserSession
from backend.modules.curriculum import alignment
from backend.redis_client import _fallback_cache, _fallback_rate_buckets
from backend.security import create_access_token, decode_access_token, hash_password

AR = "الحِصَانُ سَرِيعٌ جِدًّا."
EN = "The horse is very fast."
CHUNKS = [{"ar": [0], "en": [0, 1]}, {"ar": [1], "en": [4]}, {"ar": [2], "en": [3]}]


class TestAlignmentReview(unittest.TestCase):
    def setUp(self):
        _fallback_cache.clear()
        _fallback_rate_buckets.clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        with self.session() as db:
            pw = hash_password("TestPassword123!")
            for uid, role in (("ad", "admin"), ("ta", "tutor"), ("pa", "parent")):
                db.add(User(id=uid, email=f"{uid}@test.local", full_name=uid, role=role, password_hash=pw, is_verified=True))
            self.id = alignment.pair_id(AR, EN)
            db.add(SentenceAlignment(id=self.id, arabic=AR, english=EN, chunks_json=json.dumps(CHUNKS), status="ai",
                                     provider="gemini"))
            db.add(SentenceAlignment(id="u1", arabic="كَلِمَةٌ", english="A word", chunks_json="[]", status="unusable"))
            db.add(SentenceAlignment(id="ok1", arabic="نَعَمْ", english="Yes", chunks_json='[{"ar": [0], "en": [0]}]',
                                     status="approved"))
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

    def auth(self, user, role):
        token = create_access_token({"sub": user, "role": role})
        payload = decode_access_token(token)
        with self.session() as db:
            db.add(UserSession(id=payload["jti"], user_id=user,
                               expires_at=datetime.datetime.utcfromtimestamp(payload["exp"])))
            db.commit()
        return {"Authorization": f"Bearer {token}"}

    def review(self, body, alignment_id=None, user=("ad", "admin")):
        return self.client.post(f"/api/admin/alignments/{alignment_id or self.id}/review", json=body,
                                headers=self.auth(*user))

    def test_list_shows_counts_and_filters(self):
        res = self.client.get("/api/admin/alignments", headers=self.auth("ta", "tutor"))
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()
        self.assertEqual(data["counts"], {"ai": 1, "approved": 1, "rejected": 0, "unusable": 1})
        self.assertEqual([i["arabic"] for i in data["items"]], [AR])
        self.assertEqual(data["items"][0]["chunks"], CHUNKS)
        found = self.client.get("/api/admin/alignments", params={"status": "approved", "q": "Yes"},
                                headers=self.auth("ad", "admin")).json()
        self.assertEqual(found["total"], 1)

    def test_only_staff_can_review(self):
        self.assertEqual(self.client.get("/api/admin/alignments").status_code, 401)
        self.assertEqual(self.client.get("/api/admin/alignments", headers=self.auth("pa", "parent")).status_code, 403)
        self.assertEqual(self.review({"action": "approve"}, user=("pa", "parent")).status_code, 403)

    def test_approve_reject_and_learners_never_see_rejected(self):
        res = self.review({"action": "approve"})
        self.assertEqual(res.json()["status"], "approved")
        self.assertEqual(res.json()["reviewed_by"], "ad")
        with self.session() as db:
            self.assertEqual(alignment.get_alignments(db, [(AR, EN)]), [CHUNKS])
        self.assertEqual(self.review({"action": "reject"}).json()["status"], "rejected")
        with self.session() as db:
            self.assertEqual(alignment.get_alignments(db, [(AR, EN)]), [None])

    def test_teacher_edits_are_checked_and_saved(self):
        edited = [{"ar": [0], "en": [1]}]  # leaving words unmatched is allowed for a teacher
        res = self.review({"action": "approve", "chunks": edited})
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()["chunks"], edited)
        bad = self.review({"action": "approve", "chunks": [{"ar": [0, 2], "en": [1]}]})  # Arabic words not adjacent
        self.assertEqual(bad.status_code, 422)
        self.assertEqual(self.review({"action": "approve", "chunks": [{"ar": [0], "en": [1]}, {"ar": [1], "en": [1]}]}).status_code, 422)

    def test_unusable_needs_an_edit_or_regeneration(self):
        self.assertEqual(self.review({"action": "approve"}, "u1").status_code, 422)
        self.assertEqual(self.review({"action": "approve", "chunks": [{"ar": [0], "en": [0, 1]}]}, "u1").json()["status"],
                         "approved")

    def test_regenerate_deletes_so_the_ai_matches_again(self):
        self.assertEqual(self.review({"action": "regenerate"}).json()["status"], "deleted")
        with self.session() as db:
            self.assertIsNone(db.get(SentenceAlignment, self.id))
        self.assertEqual(self.review({"action": "approve"}).status_code, 404)
        self.assertEqual(self.review({"action": "publish"}, "ok1").status_code, 422)


if __name__ == "__main__":
    unittest.main()
