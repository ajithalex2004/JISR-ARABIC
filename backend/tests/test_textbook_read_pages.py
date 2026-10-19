"""Admin > Content: read the unread and failed pages of uploaded textbooks without re-uploading."""
import datetime
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import BookEdition, ScannedPage, User, UserSession
from backend.security import create_access_token, decode_access_token, hash_password
from backend.tasks.queue import clear_task_queue, list_recent_tasks


class TestReadTextbookPages(unittest.TestCase):
    def setUp(self):
        clear_task_queue()
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"FAHIM_CONTENT_DIR": self.tmp.name})
        self.env.start()
        uploads = Path(self.tmp.name) / "uploads"
        uploads.mkdir()
        # Grade 1 Term 1: stored, 2 of 3 pages read and 1 failed. Grade 2 Term 1: stored, fully read.
        for book in ("moe_gr1_vol1_2023", "moe_gr2_vol1_2023"):
            (uploads / f"{book}.pdf").write_bytes(b"%PDF-1.4")
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        with self.session() as db:
            pw = hash_password("TestPassword123!")
            for uid, role in (("ad", "admin"), ("ta", "tutor")):
                db.add(User(id=uid, email=f"{uid}@test.local", full_name=uid, role=role, password_hash=pw, is_verified=True))
            db.add_all([BookEdition(id="moe_gr1_vol1_2023", title="G1", total_pages=3),
                        BookEdition(id="moe_gr2_vol1_2023", title="G2", total_pages=1)])
            db.add_all([ScannedPage(book_edition_id="moe_gr1_vol1_2023", pdf_page=p, printed_page=p, ocr_text_ar="نص",
                                    review_status=status) for p, status in ((1, "ai_ocr"), (2, "extraction_failed"))])
            db.add(ScannedPage(book_edition_id="moe_gr2_vol1_2023", pdf_page=1, printed_page=1, ocr_text_ar="نص",
                               review_status="ai_ocr"))
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
        self.env.stop()
        self.tmp.cleanup()
        clear_task_queue()

    def auth(self, user, role):
        token = create_access_token({"sub": user, "role": role})
        payload = decode_access_token(token)
        with self.session() as db:
            db.add(UserSession(id=payload["jti"], user_id=user,
                               expires_at=datetime.datetime.utcfromtimestamp(payload["exp"])))
            db.commit()
        return {"Authorization": f"Bearer {token}"}

    def ocr_tasks(self):
        return [t for t in list_recent_tasks(limit=50) if t.task_type == "process_textbook_ocr"]

    def test_read_one_book_from_the_stored_pdf(self):
        headers = self.auth("ad", "admin")
        res = self.client.post("/api/admin/textbooks/moe_gr1_vol1_2023/read-pages", headers=headers)
        self.assertEqual(res.status_code, 200, res.text)
        [task] = self.ocr_tasks()
        self.assertEqual(task.params["book_edition_id"], "moe_gr1_vol1_2023")
        self.assertTrue(task.params["pdf_path"].endswith("uploads/moe_gr1_vol1_2023.pdf"))
        self.assertEqual((task.params["start_page"], task.params["page_count"]), (1, 0))
        # Asking again while it waits does not queue the book twice.
        again = self.client.post("/api/admin/textbooks/moe_gr1_vol1_2023/read-pages", headers=headers)
        self.assertEqual(again.status_code, 409)
        progress = self.client.get("/api/admin/content-progress", headers=headers).json()
        cell = progress["grades"][0]["terms"][0]
        self.assertTrue(cell["pdf_stored"] and cell["reading_queued"])

    def test_missing_pdf_and_bad_ids_are_refused(self):
        headers = self.auth("ad", "admin")
        self.assertEqual(self.client.post("/api/admin/textbooks/moe_gr3_vol1_2023/read-pages", headers=headers).status_code, 404)
        self.assertEqual(self.client.post("/api/admin/textbooks/..%2Fsecret/read-pages", headers=headers).status_code, 404)
        self.assertEqual(self.ocr_tasks(), [])

    def test_only_admins(self):
        res = self.client.post("/api/admin/textbooks/read-pages", headers=self.auth("ta", "tutor"))
        self.assertEqual(res.status_code, 403)

    def test_read_all_queues_only_books_with_pages_left(self):
        headers = self.auth("ad", "admin")
        before = self.client.get("/api/admin/content-progress", headers=headers).json()
        self.assertEqual(before["summary"]["books_to_read"], 1)
        res = self.client.post("/api/admin/textbooks/read-pages", headers=headers).json()
        self.assertEqual([q["edition_id"] for q in res["queued"]], ["moe_gr1_vol1_2023"])
        again = self.client.post("/api/admin/textbooks/read-pages", headers=headers).json()
        self.assertEqual((again["queued"], again["already_reading"]), ([], ["moe_gr1_vol1_2023"]))
        self.assertEqual(len(self.ocr_tasks()), 1)


if __name__ == "__main__":
    unittest.main()
