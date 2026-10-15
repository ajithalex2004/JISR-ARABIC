"""New prices, the JISR10 promo code, auto-renewing subscriptions and their receipts / tax invoices."""
import datetime
import hashlib
import hmac
import json
import os
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.errors import ApplicationError
from backend.main import app
from backend.models import ChildProfile, PaymentTransaction, PromoCode, Subscription, TermAccess, User
from backend.modules.billing import pricing, subscriptions
from backend.redis_client import _fallback_cache, _fallback_rate_buckets, _fallback_revoked_tokens
from backend.security import hash_password

SECRET = "whsec_test_secret_for_webhook_signing_2026"


class PricingTest(unittest.TestCase):
    def test_prices(self):
        one = pricing.quote([2])
        self.assertEqual((one["total_usd"], one["discount_usd"], one["package_type"]), (10.0, 0.0, "term"))
        self.assertEqual((one["subtotal_usd"], one["vat_usd"]), (9.52, 0.48))
        self.assertEqual(pricing.quote([1, 2])["total_usd"], 20.0)
        year = pricing.quote([1, 2, 3])
        self.assertEqual((year["list_price_usd"], year["annual_discount_usd"], year["total_usd"]), (30.0, 4.5, 25.5))
        self.assertEqual(year["package_type"], "annual")
        promo = pricing.quote([1, 2, 3], promo_pct=10)
        self.assertEqual((promo["promo_discount_usd"], promo["total_usd"], promo["discount_usd"]), (2.55, 22.95, 7.05))


class CheckoutAndSubscriptionsTest(unittest.TestCase):
    def setUp(self):
        for cache in (_fallback_cache, _fallback_revoked_tokens, _fallback_rate_buckets):
            cache.clear()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        password = hash_password("Pass12345!")
        with self.session() as db:
            users = [User(id=f"parent_{i}", email=f"p{i}@test.local", full_name=f"Parent {i}", role="parent",
                          password_hash=password, is_verified=True) for i in range(12)]
            db.add_all(users + [User(id="admin_user", email="admin@test.local", full_name="Admin", role="admin",
                                     password_hash=password, is_verified=True)])
            db.commit()
            db.add_all([ChildProfile(id=f"child_{i}", parent_id=f"parent_{i}", name=f"Child {i}", default_grade=5)
                        for i in range(12)])
            now = datetime.datetime.utcnow()
            db.add(PromoCode(code="JISR10", discount_pct=10, max_users=10, is_active=True,
                             valid_from=now - datetime.timedelta(days=1), valid_until=now + datetime.timedelta(days=30)))
            db.commit()

        def scoped_db():
            with self.session() as db:
                yield db

        app.dependency_overrides[get_db] = scoped_db
        self.client = TestClient(app)
        self.env = patch.dict(os.environ, {"FAHIM_ENV": "development", "FAHIM_PAYMENT_PROVIDER": "",
                                           "STRIPE_SECRET_KEY": "", "FAHIM_PAYMENT_WEBHOOK_SECRET": SECRET})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.client.close()
        app.dependency_overrides.pop(get_db, None)
        self.engine.dispose()

    def _headers(self, i=0, email=None):
        email = email or f"p{i}@test.local"
        tokens = self.__dict__.setdefault("_tokens", {})
        if email not in tokens:
            _fallback_rate_buckets.clear()
            res = self.client.post("/api/auth/login", json={"email": email, "password": "Pass12345!"})
            self.assertEqual(res.status_code, 200, res.text)
            tokens[email] = {"Authorization": f"Bearer {res.json()['access_token']}"}
        return tokens[email]

    def _checkout(self, i=0, **body):
        payload = {"child_id": f"child_{i}", "grade": 5, "plan": "term", "terms": [1], **body}
        return self.client.post("/api/payments/start-checkout", json=payload, headers=self._headers(i))

    # --- prices & promo codes -------------------------------------------------------------

    def test_quote_shows_the_annual_discount_and_promo(self):
        res = self.client.post("/api/payments/quote", headers=self._headers(),
                               json={"child_id": "child_0", "plan": "annual", "promo_code": "jisr10"})
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()
        self.assertEqual((data["list_price_usd"], data["annual_discount_usd"], data["promo_discount_usd"], data["total_usd"]),
                         (30.0, 4.5, 2.55, 22.95))
        self.assertEqual(data["provider"], "simulated")
        self.assertEqual(self.client.get("/api/payments/prices").json()["annual_usd"], 25.5)

    def test_jisr10_works_for_the_first_ten_families_once_each(self):
        for i in range(10):
            res = self._checkout(i, promo_code="JISR10")
            self.assertEqual(res.status_code, 200, res.text)
            self.assertEqual(res.json()["amount_usd"], 9.0)
        again = self._checkout(0, terms=[2], promo_code="JISR10")
        self.assertEqual(again.status_code, 400)
        self.assertIn("already used", again.json()["detail"])
        eleventh = self._checkout(10, promo_code="JISR10")
        self.assertEqual(eleventh.status_code, 400)
        self.assertIn("maximum of 10 families", eleventh.json()["detail"])
        self.assertEqual(self._checkout(10).json()["amount_usd"], 10.0)

    def test_promo_validity_window_set_by_admin(self):
        admin = self._headers(email="admin@test.local")
        promos = self.client.get("/api/admin/promo-codes", headers=admin).json()
        jisr10 = next(p for p in promos if p["code"] == "JISR10")
        self.assertEqual((jisr10["state"], jisr10["used"], jisr10["max_users"]), ("active", 0, 10))
        past = (datetime.datetime.utcnow() - datetime.timedelta(days=2)).isoformat()
        updated = self.client.patch(f"/api/admin/promo-codes/{jisr10['id']}", headers=admin,
                                    json={"valid_until": past, "valid_from": None}).json()
        self.assertEqual(updated["state"], "expired")
        res = self._checkout(0, promo_code="JISR10")
        self.assertEqual(res.status_code, 400)
        self.assertIn("expired", res.json()["detail"])

        created = self.client.post("/api/admin/promo-codes", headers=admin,
                                   json={"code": "eid25", "discount_pct": 25, "max_users": 3}).json()
        self.assertEqual((created["code"], created["discount_pct"], created["max_users"]), ("EID25", 25.0, 3))
        self.assertEqual(self.client.get("/api/admin/promo-codes", headers=self._headers(1)).status_code, 403)

    # --- receipts & tax invoices ----------------------------------------------------------

    def test_every_payment_has_a_receipt_and_tax_invoice(self):
        res = self._checkout(0, terms=[1, 2])
        data = res.json()
        self.assertEqual(data["amount_usd"], 20.0)
        self.assertTrue(data["receipt_number"].startswith("FHM-"))
        invoice = self.client.get(f"/api/payments/invoice/{data['receipt_number']}", headers=self._headers()).json()
        self.assertEqual(invoice["invoice_number"], data["tax_invoice_number"])
        self.assertEqual(invoice["trn"], "100458923100003")
        self.assertEqual((invoice["total_usd"], invoice["subtotal_usd"], invoice["vat_amount_usd"]), (20.0, 19.05, 0.95))
        self.assertIn("Terms 1, 2", invoice["items"][0]["description_en"])

    # --- auto-renewing subscriptions (simulated) -------------------------------------------

    def test_annual_auto_renew_charges_again_and_unlocks_the_new_grade(self):
        res = self._checkout(0, plan="annual", auto_renew=True, promo_code="JISR10")
        self.assertEqual(res.status_code, 200, res.text)
        first = res.json()
        self.assertEqual(first["amount_usd"], 22.95)
        subs = self.client.get("/api/payments/subscriptions", headers=self._headers()).json()
        self.assertEqual(len(subs), 1)
        self.assertEqual((subs[0]["plan"], subs[0]["status"], subs[0]["renewal_price_usd"]), ("annual", "active", 25.5))

        with self.session() as db:
            db.get(ChildProfile, "child_0").default_grade = 6  # the child moves up a grade
            db.commit()
            renewed = subscriptions.renew_due_simulated(db, now=datetime.datetime.utcnow() + datetime.timedelta(days=370))
            self.assertEqual(renewed, 1)
            payments = db.query(PaymentTransaction).filter_by(child_id="child_0").order_by(PaymentTransaction.created_at).all()
            self.assertEqual([float(p.amount_usd) for p in payments], [22.95, 25.5])  # promo on the first payment only
            self.assertEqual(len({p.receipt_number for p in payments}), 2)
            self.assertTrue(all(p.tax_invoice_number and p.subscription_id for p in payments))
            self.assertEqual(db.query(TermAccess).filter_by(child_id="child_0", grade=6, is_unlocked=True).count(), 3)

    def test_term_auto_renew_moves_to_the_next_term_and_cancel_stops_it(self):
        self._checkout(1, terms=[1], auto_renew=True)
        sub = self.client.get("/api/payments/subscriptions", headers=self._headers(1)).json()[0]
        self.assertEqual((sub["plan"], sub["next_term"], sub["renewal_months"]), ("term", 2, 4))
        with self.session() as db:
            subscriptions.renew_due_simulated(db, now=datetime.datetime.utcnow() + datetime.timedelta(days=125))
            self.assertTrue(db.query(TermAccess).filter_by(child_id="child_1", grade=5, term=2, is_unlocked=True).first())

        cancelled = self.client.post(f"/api/payments/subscriptions/{sub['id']}/cancel", headers=self._headers(1)).json()
        self.assertTrue(cancelled["cancel_at_period_end"])
        self.assertEqual(self.client.post(f"/api/payments/subscriptions/{sub['id']}/cancel", headers=self._headers(2)).status_code, 404)
        with self.session() as db:
            subscriptions.renew_due_simulated(db, now=datetime.datetime.utcnow() + datetime.timedelta(days=400))
            self.assertEqual(db.get(Subscription, sub["id"]).status, "canceled")
            self.assertEqual(db.query(PaymentTransaction).filter_by(child_id="child_1").count(), 2)
        self.assertEqual(self._checkout(1, terms=[1, 2], auto_renew=True).status_code, 400)

    def test_production_without_stripe_refuses_card_checkout(self):
        with patch.dict(os.environ, {"FAHIM_ENV": "production"}):
            res = self._checkout(0)
        self.assertEqual(res.status_code, 503)

    # --- Stripe ----------------------------------------------------------------------------

    def test_stripe_checkout_session_for_an_annual_subscription(self):
        calls = []

        class Response:
            def __init__(self, status, payload):
                self.status_code, self._payload, self.content, self.text = status, payload, b"x", json.dumps(payload)

            def json(self):
                return self._payload

        def fake_request(method, url, data=None, headers=None, timeout=None):
            calls.append((method, url, dict(data or [])))
            if url.endswith("/coupons/JISR-ONCE-10_0") and method == "GET":
                return Response(404, {"error": {"message": "No such coupon"}})
            if url.endswith("/checkout/sessions"):
                return Response(200, {"id": "cs_1", "url": "https://checkout.stripe.com/c/pay/cs_1"})
            return Response(200, {"id": "JISR-ONCE-10_0"})

        with patch.dict(os.environ, {"FAHIM_PAYMENT_PROVIDER": "stripe", "STRIPE_SECRET_KEY": "sk_test_x"}), \
                patch("httpx.request", side_effect=fake_request):
            res = self._checkout(0, plan="annual", auto_renew=True, promo_code="JISR10")
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json(), {"provider": "stripe", "checkout_url": "https://checkout.stripe.com/c/pay/cs_1"})
        session = next(data for method, url, data in calls if url.endswith("/checkout/sessions"))
        self.assertEqual(session["mode"], "subscription")
        self.assertEqual(session["line_items[0][price_data][unit_amount]"], "2550")
        self.assertEqual(session["line_items[0][price_data][recurring][interval]"], "year")
        self.assertEqual(session["discounts[0][coupon]"], "JISR-ONCE-10_0")
        self.assertEqual(session["subscription_data[metadata][terms]"], "1,2,3")
        self.assertEqual(session["customer_email"], "p0@test.local")

    def _webhook(self, event_type, obj, event_id="evt_1"):
        body = json.dumps({"id": event_id, "type": event_type, "data": {"object": obj}}).encode()
        stamp = str(int(time.time()))
        sig = hmac.new(SECRET.encode(), f"{stamp}.".encode() + body, hashlib.sha256).hexdigest()
        return self.client.post("/api/payments/webhook", content=body, headers={"stripe-signature": f"t={stamp},v1={sig}"})

    def test_stripe_subscription_webhooks_record_each_renewal(self):
        meta = {"flow": "checkout_v2", "child_id": "child_3", "parent_id": "parent_3", "grade": "5",
                "terms": "1,2,3", "plan": "annual", "promo_code": "JISR10"}
        self.assertEqual(self._webhook("checkout.session.completed", {
            "id": "cs_9", "mode": "subscription", "subscription": "sub_9", "customer": "cus_9", "metadata": meta,
        }).status_code, 200)
        period_end = int(time.time()) + 365 * 86400
        invoice = {"id": "in_1", "subscription": "sub_9", "amount_paid": 2295, "subscription_details": {"metadata": meta},
                   "lines": {"data": [{"period": {"end": period_end}}]}}
        first = self._webhook("invoice.paid", invoice).json()
        self.assertTrue(first["receipt_number"].startswith("FHM-"))
        self.assertEqual(self._webhook("invoice.paid", invoice).json()["receipt_number"], first["receipt_number"])  # idempotent
        renewal = {**invoice, "id": "in_2", "amount_paid": 2550}
        self.assertNotEqual(self._webhook("invoice.paid", renewal, "evt_2").json()["receipt_number"], first["receipt_number"])
        self._webhook("customer.subscription.deleted", {"id": "sub_9", "status": "canceled"}, "evt_3")
        with self.session() as db:
            sub = db.query(Subscription).filter_by(provider_subscription_id="sub_9").one()
            self.assertEqual((sub.status, sub.provider_customer_id), ("canceled", "cus_9"))
            payments = db.query(PaymentTransaction).filter_by(subscription_id=sub.id).all()
            self.assertEqual(sorted(float(p.amount_usd) for p in payments), [22.95, 25.5])
            self.assertEqual(db.query(TermAccess).filter_by(child_id="child_3", is_unlocked=True).count(), 3)
            promo = db.query(PromoCode).filter_by(code="JISR10").one()
            self.assertEqual(pricing.promo_uses(promo, db), 1)

    def test_stripe_one_off_payment_webhook(self):
        meta = {"flow": "checkout_v2", "child_id": "child_4", "parent_id": "parent_4", "grade": "5", "terms": "2",
                "plan": "term", "promo_code": ""}
        res = self._webhook("checkout.session.completed", {"id": "cs_one", "mode": "payment", "payment_status": "paid",
                                                           "amount_total": 1000, "metadata": meta})
        self.assertEqual(res.status_code, 200, res.text)
        # The payment intent of the same checkout is ignored (no double recording).
        self.assertEqual(self._webhook("payment_intent.succeeded", {"id": "pi_1", "metadata": {}}, "evt_pi").status_code, 200)
        with self.session() as db:
            payments = db.query(PaymentTransaction).filter_by(child_id="child_4").all()
            self.assertEqual([(float(p.amount_usd), p.terms_purchased) for p in payments], [(10.0, "2")])


if __name__ == "__main__":
    unittest.main()
