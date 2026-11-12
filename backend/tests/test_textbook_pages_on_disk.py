"""Books loaded with the bulk content upload count as present, and a page is never served from another book."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.errors import ApplicationError
from backend.modules.curriculum.authoring import get_page_image
from backend.modules.curriculum.content_progress import content_progress, pages_on_disk


class TestTextbookPagesOnDisk(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        # Class 3 Term 2 arrived with the content upload: images and page text, no PDF, no page rows.
        for n in (8, 9, 10):
            img = root / "pdf_pages_sample" / "moe_gr3_vol2_2023" / f"page_{n}.png"
            img.parent.mkdir(parents=True, exist_ok=True)
            img.write_bytes(b"\x89PNG class3")
            txt = root / "vision-output-new" / "moe_gr3_vol2_2023" / f"page_{n}.json"
            txt.parent.mkdir(parents=True, exist_ok=True)
            txt.write_text(json.dumps({"textAnnotations": [{"description": "نص"}]}), encoding="utf-8")
        # Class 5 Term 1 has page 10 too; Class 11 has nothing.
        five = root / "pdf_pages_sample" / "moe_gr5_vol1_2023" / "page_10.png"
        five.parent.mkdir(parents=True, exist_ok=True)
        five.write_bytes(b"\x89PNG class5")
        (root / "pdf_pages_sample" / "page_10.png").write_bytes(b"\x89PNG legacy")
        self.env = patch.dict(os.environ, {"FAHIM_CONTENT_DIR": str(root)})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_a_book_serves_only_its_own_pages(self):
        self.assertTrue(get_page_image(10, "moe_gr3_vol2_2023").endswith("moe_gr3_vol2_2023/page_10.png"))
        with self.assertRaises(ApplicationError) as ctx:
            get_page_image(10, "moe_gr11_vol1_2023")  # used to return Class 5's page 10
        self.assertEqual(ctx.exception.status_code, 404)
        with self.assertRaises(ApplicationError):
            get_page_image(11, "moe_gr3_vol2_2023")  # page missing from this book: no other book's page 11
        with self.assertRaises(ApplicationError) as ctx:
            get_page_image(10, "../secret")
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertTrue(get_page_image(10).endswith("pdf_pages_sample/page_10.png"))  # legacy, no book named

    def test_report_counts_pages_from_the_content_upload(self):
        self.assertEqual(pages_on_disk()["moe_gr3_vol2_2023"], {"images": 3, "text": 3})
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
        db = sessionmaker(bind=engine)()
        try:
            report = content_progress(db)
        finally:
            db.close()
            engine.dispose()
        cells = {(c["grade"], c["term"]): c for row in report["grades"] for c in row["terms"]}
        c3 = cells[(3, 2)]
        self.assertTrue(c3["uploaded"] and c3["book_read"])
        self.assertEqual((c3["page_images_on_disk"], c3["pages_text_on_disk"]), (3, 3))
        self.assertNotIn("Grade 3 Term 2", report["summary"]["books_missing_list"])
        self.assertIn("Grade 11 Term 1", report["summary"]["books_missing_list"])


if __name__ == "__main__":
    unittest.main()
