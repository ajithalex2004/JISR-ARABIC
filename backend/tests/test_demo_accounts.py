"""Demo and test accounts are removed from the live database; real accounts are left alone."""
import unittest

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.curriculum_seed import seed_database
from backend.database import Base
from backend.demo_accounts import remove_demo_accounts
from backend.models import ChildProfile, User


class TestDemoAccounts(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        event.listen(self.engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_demo_and_test_accounts_removed_real_ones_kept(self):
        seed_database(self.db, include_demo_data=True)
        self.db.add_all([
            User(email="student_test_1790399250@example.com", full_name="Parent of Zayed", role="parent", password_hash="x"),
            User(email="real.parent@gmail.com", role="parent", password_hash="x"),
            User(email="student_test_staff@example.com", role="admin", password_hash="x"),
        ])
        self.db.commit()

        removed = remove_demo_accounts(self.db)
        self.assertEqual(sorted(removed), ["cohort.parents@sunrise.ae", "parent@fahim.ae",
                                           "student_test_1790399250@example.com", "tutor@fahim.ae"])
        self.assertEqual(sorted(u.email for u in self.db.query(User).all()),
                         ["real.parent@gmail.com", "student_test_staff@example.com"])
        self.assertEqual(self.db.query(ChildProfile).count(), 0)
        self.assertEqual(remove_demo_accounts(self.db), [])  # nothing left to do

    def test_scheduler_removes_them_once_and_reports_the_result(self):
        from unittest.mock import patch
        from backend import scheduler
        from backend.redis_client import _fallback_cache, cache_get

        _fallback_cache.clear()
        seed_database(self.db, include_demo_data=True)
        factory = sessionmaker(bind=self.engine)
        with patch("backend.database.SessionLocal", factory), \
                patch.object(scheduler, "run_gemini_probe", return_value={"ok": True}):
            scheduler.tick()
            self.assertIn("parent@fahim.ae", cache_get("scheduler:last:demo_cleanup")["removed"])
            with patch.object(scheduler, "run_demo_cleanup") as again:
                scheduler.tick()  # claimed for 6 hours
            again.assert_not_called()
            with patch("backend.demo_accounts.remove_demo_accounts", side_effect=RuntimeError("boom")):
                result = scheduler.run_demo_cleanup()
        self.assertEqual(result["error"], "RuntimeError: boom")
        self.assertEqual(cache_get("scheduler:last:demo_cleanup")["error"], "RuntimeError: boom")
        _fallback_cache.clear()


if __name__ == "__main__":
    unittest.main()
