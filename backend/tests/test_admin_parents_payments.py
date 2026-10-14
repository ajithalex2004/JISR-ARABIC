"""Admins can list and manage parent accounts and see every payment and voucher redemption."""
import datetime
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import ChildProfile, PaymentTransaction, TermAccess, User
from backend.redis_client import _fallback_cache, _fallback_rate_buckets, _fallback_revoked_tokens
from backend.security import hash_password


class TestAdminParentsAndPayments(unittest.TestCase):
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
        now = datetime.datetime.utcnow()
        with self.session() as db:
            db.add_all([
                User(id="parent_alex", email="alex@test.local", full_name="Alex Joseph", phone_number="0501234567",
                     role="parent", password_hash=self.password_hash, is_verified=True),
                User(id="parent_sara", email="sara@test.local", full_name="Sara Khan",
                     role="parent", password_hash=self.password_hash, is_verified=True),
                User(id="admin_user", email="admin@test.local", full_name="Admin",
                     role="admin", password_hash=self.password_hash, is_verified=True),
            ])
            db.commit()
            db.add_all([
                ChildProfile(id="child_ann", parent_id="parent_alex", name="Ann Maria", default_grade=6),
                ChildProfile(id="child_sam", parent_id="parent_alex", name="Sam", default_grade=3),
                ChildProfile(id="child_lina", parent_id="parent_sara", name="Lina", default_grade=4),
            ])
            db.commit()
            db.add_all([
                TermAccess(child_id="child_ann", grade=6, term=1, is_unlocked=True),
                TermAccess(child_id="child_ann", grade=7, term=1, is_unlocked=True),
                PaymentTransaction(id="pay_card", parent_id="parent_alex", child_id="child_ann", grade=6, term=1,
                                   amount_usd=20.0, payment_method="card", status="succeeded",
                                   receipt_number="RCPT-1", created_at=now - datetime.timedelta(days=3)),
                PaymentTransaction(id="pay_voucher", parent_id="parent_alex", child_id="child_ann", grade=7, term=1,
                                   amount_usd=0.0, payment_method="school_voucher", voucher_code="SCHOOL50",
                                   status="succeeded", receipt_number="RCPT-2", created_at=now - datetime.timedelta(days=1)),
                PaymentTransaction(id="pay_refund", parent_id="parent_sara", child_id="child_lina", grade=4, term=1,
                                   amount_usd=20.0, payment_method="card", status="succeeded", receipt_number="RCPT-3",
                                   refunded_at=now, created_at=now - datetime.timedelta(days=40)),
                PaymentTransaction(id="pay_pending", parent_id="parent_sara", child_id="child_lina", grade=4, term=2,
                                   amount_usd=20.0, payment_method="card", status="pending", receipt_number="RCPT-4",
                                   created_at=now),
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
        _fallback_rate_buckets.clear()

    def _headers(self, email="admin@test.local"):
        res = self.client.post("/api/auth/login", json={"email": email, "password": "Pass12345!"})
        self.assertEqual(res.status_code, 200, res.text)
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    def test_parent_list_shows_students_grades_and_payments(self):
        res = self.client.get("/api/admin/parents", params={"q": "alex"}, headers=self._headers())
        self.assertEqual(res.status_code, 200, res.text)
        [alex] = res.json()
        self.assertEqual(alex["students_count"], 2)
        ann = next(s for s in alex["students"] if s["name"] == "Ann Maria")
        self.assertEqual(ann["entitled_grades"], [6, 7])
        self.assertEqual(alex["payments_count"], 2)
        self.assertEqual(alex["total_paid_usd"], 20.0)
        self.assertEqual(alex["voucher_redemptions"], 1)

        by_child = self.client.get("/api/admin/parents", params={"q": "lina"}, headers=self._headers()).json()
        self.assertEqual([p["id"] for p in by_child], ["parent_sara"])

    def test_parent_detail_lists_payments_newest_first(self):
        res = self.client.get("/api/admin/parents/parent_alex", headers=self._headers())
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual([p["receipt_number"] for p in res.json()["payments"]], ["RCPT-2", "RCPT-1"])
        self.assertEqual(res.json()["payments"][0]["child_name"], "Ann Maria")

    def test_admin_adds_edits_and_deletes_parent(self):
        headers = self._headers()
        created = self.client.post("/api/admin/parents", json={
            "email": "New.Parent@test.local", "password": "Welcome123", "full_name": "New Parent"}, headers=headers)
        self.assertEqual(created.status_code, 200, created.text)
        parent_id = created.json()["id"]
        login = self.client.post("/api/auth/login", json={"email": "new.parent@test.local", "password": "Welcome123"})
        self.assertEqual(login.status_code, 200, login.text)

        self.assertEqual(self.client.post("/api/admin/parents", json={
            "email": "alex@test.local", "password": "Welcome123"}, headers=headers).status_code, 409)
        self.assertEqual(self.client.post("/api/admin/parents", json={
            "email": "x@test.local", "password": "short"}, headers=headers).status_code, 400)

        edited = self.client.patch(f"/api/admin/parents/{parent_id}", json={
            "full_name": "Renamed Parent", "phone_number": "0559999999", "weekly_report_email": True}, headers=headers)
        self.assertEqual(edited.status_code, 200, edited.text)
        self.assertEqual((edited.json()["full_name"], edited.json()["weekly_report_email"]), ("Renamed Parent", True))
        self.assertEqual(self.client.patch(f"/api/admin/parents/{parent_id}", json={
            "email": "sara@test.local"}, headers=headers).status_code, 409)

        deleted = self.client.delete("/api/admin/parents/parent_sara", headers=headers)
        self.assertEqual(deleted.status_code, 200, deleted.text)
        with self.session() as db:
            self.assertIsNone(db.get(User, "parent_sara"))
            self.assertIsNone(db.get(ChildProfile, "child_lina"))
            kept = db.get(PaymentTransaction, "pay_refund")
            self.assertIsNotNone(kept)
            self.assertEqual(kept.anonymized_parent_id, "parent_sara")
        self.assertIn(self.client.delete("/api/admin/parents/admin_user", headers=headers).status_code, (400, 404))

    def test_payments_overview_summary_and_filters(self):
        headers = self._headers()
        res = self.client.get("/api/admin/payments", headers=headers)
        self.assertEqual(res.status_code, 200, res.text)
        summary = res.json()["summary"]
        self.assertEqual(summary["count"], 4)
        self.assertEqual(summary["revenue_usd"], 20.0)
        self.assertEqual(summary["voucher_redemptions"], 1)
        self.assertEqual(summary["refunded_count"], 1)
        self.assertEqual(summary["pending_count"], 1)
        statuses = {p["receipt_number"]: p["status"] for p in res.json()["payments"]}
        self.assertEqual(statuses["RCPT-3"], "refunded")

        vouchers = self.client.get("/api/admin/payments", params={"method": "voucher"}, headers=headers).json()
        self.assertEqual([p["voucher_code"] for p in vouchers["payments"]], ["SCHOOL50"])
        family = self.client.get("/api/admin/payments", params={"q": "sara"}, headers=headers).json()
        self.assertEqual(sorted(p["receipt_number"] for p in family["payments"]), ["RCPT-3", "RCPT-4"])
        recent = self.client.get("/api/admin/payments", params={"days": 30}, headers=headers).json()
        self.assertNotIn("RCPT-3", [p["receipt_number"] for p in recent["payments"]])

    def test_parents_cannot_use_admin_pages(self):
        headers = self._headers("alex@test.local")
        for path in ("/api/admin/parents", "/api/admin/payments", "/api/admin/system-health"):
            self.assertEqual(self.client.get(path, headers=headers).status_code, 403, path)
        self.assertEqual(self.client.delete("/api/admin/parents/parent_sara", headers=headers).status_code, 403)


if __name__ == "__main__":
    unittest.main()
