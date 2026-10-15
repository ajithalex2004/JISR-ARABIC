"""Application operations; callers provide explicit database sessions and actors."""
import uuid
import datetime
import os
import hmac
import hashlib
import json
from sqlalchemy.orm import Session
from backend.models import PaymentTransaction, TermAccess, ChildProfile, User, VoucherCode, School
from backend.schemas import PaymentCheckoutRequest, PaymentResponse, AnnualCheckoutRequest, VoucherRedeemRequest, VoucherRedeemResponse, TaxInvoiceResponse, TaxInvoiceItem
from backend.errors import ApplicationError

from backend.modules.billing.pricing import (  # noqa: E402  (prices live in one place)
    PRICE_PER_TERM_USD, PRICE_ANNUAL_PASS_USD, VAT_RATE, clean_terms, find_promo, quote, record_promo_use,
)
# Development-only codes for testing checkout without a real promo code (refused in production).
DEV_PROMOS = {"DEMOFREE": 100.0, "ADEK100": 100.0, "JISR100": 100.0, "HALFPRICE": 50.0}


AED_PEG = 3.6725               # Official UAE Dirham Peg


FAHIM_TRN = "100458923100003"  # UAE FTA Tax Registration Number


def promo_pct_for(promo: str, *, parent_id, db, is_prod: bool) -> float:
    """Discount % of a promo code: admin-made codes (e.g. JISR10), or test codes outside production."""
    if not promo:
        return 0.0
    from backend.models import PromoCode
    from sqlalchemy import func
    if not is_prod and promo in DEV_PROMOS and not db.query(PromoCode).filter(func.upper(PromoCode.code) == promo).first():
        return DEV_PROMOS[promo]
    return float(find_promo(promo, parent_id=parent_id, db=db).discount_pct)


def send_receipt_email(txn: PaymentTransaction, *, db: Session) -> None:
    """Email the parent the receipt and tax invoice summary (best effort; never fails the payment)."""
    import logging
    try:
        from backend.email_delivery import email_configured, send_email
        parent = db.query(User).filter(User.id == txn.parent_id).first() if txn.parent_id else None
        if not parent or not parent.email or not email_configured():
            return
        invoice = get_tax_invoice(txn.receipt_number, db=db)
        item = invoice.items[0]
        body = (
            f"Thank you for your payment.\n\n"
            f"Receipt number: {txn.receipt_number}\n"
            f"Tax invoice number: {invoice.invoice_number}\n"
            f"Date: {invoice.issue_date}\n\n"
            f"{item.description_en}\n"
            f"Student: {invoice.student_name} (Class {invoice.grade})\n"
            f"Price: USD {item.unit_price_usd:.2f}\n"
            f"Discount: USD {item.discount_usd:.2f}\n"
            f"Taxable amount: USD {invoice.subtotal_usd:.2f}\n"
            f"VAT 5%: USD {invoice.vat_amount_usd:.2f}\n"
            f"Total paid: USD {invoice.total_usd:.2f} (AED {invoice.total_aed:.2f})\n\n"
            f"Supplier TRN: {invoice.trn}\n"
            "You can view and print the full UAE tax invoice in the app under My Subscriptions & Invoices.\n\n"
            "JISR Arabic"
        )
        send_email(parent.email, f"JISR receipt {txn.receipt_number} / Tax invoice {invoice.invoice_number}", body,
                   record_failures=False)
    except Exception as exc:
        logging.getLogger(__name__).warning("Receipt email for %s not sent: %s", txn.receipt_number, exc)


def compute_tax_breakdown(total_amount: float):
    """Compute subtotal (excl. VAT) and 5% UAE VAT from gross total."""
    if total_amount <= 0:
        return 0.0, 0.0
    subtotal = round(total_amount / (1.0 + VAT_RATE), 2)
    vat_amount = round(total_amount - subtotal, 2)
    return subtotal, vat_amount


def checkout_term(req: PaymentCheckoutRequest, *, db: Session, is_verified_provider: bool = False):
    """
    Unlock one term for USD 10, two terms for USD 20, or all three terms (the annual plan) for
    USD 30 less 15% = USD 25.50, less any promo code.
    In production: direct client calls create a pending checkout transaction.
    Access is unlocked only when is_verified_provider=True (via signed provider webhook).
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == req.child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")

    is_prod = os.getenv("FAHIM_ENV", "development").lower() == "production"

    if is_prod and (req.card_number or req.cvc):
        raise ApplicationError(400, "Direct submission of raw card numbers (PAN/CVC) is forbidden in production for PCI-DSS compliance. Use provider-hosted checkout.")

    if req.idempotency_key:
        prior = db.query(PaymentTransaction).filter(PaymentTransaction.idempotency_key == req.idempotency_key).first()
        if prior:
            return _payment_response(prior, db)
    if is_prod:
        if not req.provider_payment_id:
            raise ApplicationError(402, "Complete payment with the configured provider; direct card checkout is disabled")
        if os.getenv("FAHIM_PAYMENT_PROVIDER", "").lower() not in ("stripe", "paypal"):
            raise ApplicationError(503, "A verified Stripe or PayPal provider is required")

    # In development, auto-succeed for developer convenience. In production, require verified provider.
    is_succeeded = is_verified_provider or (not is_prod)
    txn_status = "succeeded" if is_succeeded else "pending"

    is_annual = req.package_type == "annual"
    terms_to_unlock = [1, 2, 3] if is_annual else clean_terms(req.terms, req.term)
    is_annual = len(terms_to_unlock) == 3

    # An unknown or used-up promo code is refused before anything else.
    promo = (req.promo_code or "").strip().upper()
    promo_pct = promo_pct_for(promo, parent_id=child.parent_id, db=db, is_prod=is_prod)

    # Check if all selected terms are already unlocked
    if not is_annual and len(terms_to_unlock) == 1:
        single_term = terms_to_unlock[0]
        existing_access = db.query(TermAccess).filter(
            TermAccess.child_id == child.id,
            TermAccess.grade == req.grade,
            TermAccess.term == single_term,
            TermAccess.is_unlocked == True
        ).first()
        if existing_access:
            return PaymentResponse(
                success=True,
                transaction_id=existing_access.transaction_ref or "ALREADY_ACTIVE",
                receipt_number=f"REC-{req.grade}-{single_term}-ACTIVE",
                amount_usd=0.0,
                grade=req.grade,
                term=single_term,
                package_type="term",
                unlocked_terms=[single_term],
                subtotal_usd=0.0,
                vat_amount_usd=0.0,
                tax_invoice_number=f"INV-REC-{req.grade}-{single_term}",
                status="succeeded",
                message=f"Term {single_term} for Class {req.grade} is already active!"
            )

    # Price: USD 10 a term; all three terms together get 15% off; then any promo code.
    price = quote(terms_to_unlock, promo_pct=promo_pct)
    final_amount = price["total_usd"]
    subtotal, vat_amount = price["subtotal_usd"], price["vat_usd"]

    # Generate transaction reference and receipt
    txn_id = str(uuid.uuid4())
    receipt_num = f"FHM-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{txn_id[:8].upper()}"
    tax_inv_num = f"INV-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{txn_id[:6].upper()}"
    card_last4 = req.card_number[-4:] if req.card_number and len(req.card_number) >= 4 else "4242"

    amount_cents = int(round(final_amount * 100))
    txn = PaymentTransaction(
        id=txn_id,
        parent_id=child.parent_id,
        child_id=child.id,
        grade=req.grade,
        term=0 if is_annual else (terms_to_unlock[0] if len(terms_to_unlock) == 1 else 0),
        amount_usd=round(final_amount, 2),
        subtotal_usd=subtotal,
        vat_amount_usd=vat_amount,
        discount_amount_usd=price["discount_usd"],
        amount_cents=amount_cents,
        currency="USD",
        package_type="annual" if is_annual else "term",
        status=txn_status,
        payment_method=req.payment_method,
        card_last4=card_last4,
        promo_code=promo if promo else None,
        receipt_number=receipt_num,
        tax_invoice_number=tax_inv_num,
        idempotency_key=req.idempotency_key,
        provider_event_id=req.provider_payment_id,
        terms_purchased=",".join(map(str, terms_to_unlock)),
    )
    db.add(txn)

    # Only unlock TermAccess if payment is confirmed
    if is_succeeded:
        for t_num in terms_to_unlock:
            access = db.query(TermAccess).filter(
                TermAccess.child_id == child.id,
                TermAccess.grade == req.grade,
                TermAccess.term == t_num
            ).first()

            if not access:
                access = TermAccess(
                    child_id=child.id,
                    grade=req.grade,
                    term=t_num,
                    is_unlocked=True,
                    unlocked_at=datetime.datetime.utcnow(),
                    transaction_ref=receipt_num
                )
                db.add(access)
            else:
                access.is_unlocked = True
                access.unlocked_at = datetime.datetime.utcnow()
                access.transaction_ref = receipt_num

        # Paying unlocks this grade; it does not move the child to it. A parent
        # switches grades explicitly (POST /api/curriculum/active-grade).
        if req.grade and not child.default_grade:
            child.default_grade = req.grade
        if promo and promo not in DEV_PROMOS:
            record_promo_use(promo, parent_id=child.parent_id, payment_id=txn_id, db=db)

    db.commit()
    if is_succeeded:
        send_receipt_email(txn, db=db)

    pkg_label = "Annual Pass (All Terms 1, 2, & 3 + Ask Fahim AI)" if is_annual else f"Term(s) {', '.join(map(str, terms_to_unlock))} + Ask Fahim AI"
    return PaymentResponse(
        success=is_succeeded,
        transaction_id=txn_id,
        receipt_number=receipt_num,
        amount_usd=float(final_amount),
        grade=req.grade,
        term=terms_to_unlock[0] if len(terms_to_unlock) == 1 else 0,
        package_type="annual" if is_annual else "term",
        unlocked_terms=terms_to_unlock if is_succeeded else [],
        subtotal_usd=float(subtotal),
        vat_amount_usd=float(vat_amount),
        tax_invoice_number=tax_inv_num,
        status=txn_status,
        message=f"Payment of USD {final_amount:.2f} successful! {pkg_label} for Class {req.grade} has been cracked and unlocked." if is_succeeded else f"Checkout initiated for Class {req.grade}. Entitlements will activate once confirmed by the payment provider webhook."
    )


def _payment_response(txn: PaymentTransaction, db: Session):
    is_succeeded = txn.status == "succeeded"
    terms = ([1, 2, 3] if txn.package_type == "annual" else [txn.term]) if is_succeeded else []
    return PaymentResponse(
        success=is_succeeded,
        transaction_id=txn.id,
        receipt_number=txn.receipt_number,
        amount_usd=float(txn.amount_usd) if txn.amount_usd is not None else 0.0,
        grade=txn.grade,
        term=txn.term,
        package_type=txn.package_type,
        unlocked_terms=terms,
        subtotal_usd=float(txn.subtotal_usd) if txn.subtotal_usd is not None else 0.0,
        vat_amount_usd=float(txn.vat_amount_usd) if txn.vat_amount_usd is not None else 0.0,
        tax_invoice_number=txn.tax_invoice_number,
        status=txn.status,
        message="Payment already processed." if is_succeeded else "Payment remains pending provider webhook confirmation."
    )


def reconcile_provider_event(event_id: str, child_id: str, grade: int, term: int,
                             status: str, signature: str, *, db: Session):
    secret = os.getenv("FAHIM_PAYMENT_WEBHOOK_SECRET")
    if not secret:
        raise ApplicationError(503, "Payment provider webhook is not configured")
    payload = f"{event_id}:{child_id}:{grade}:{term}:{status}"
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature or ""):
        raise ApplicationError(401, "Invalid payment provider signature")
    prior = db.query(PaymentTransaction).filter(PaymentTransaction.provider_event_id == event_id).first()
    if prior:
        return _payment_response(prior, db)
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ApplicationError(404, "Child profile not found")
    if status != "succeeded":
        return {"success": False, "status": status, "message": "Payment not confirmed; access remains locked."}
    req = PaymentCheckoutRequest(child_id=child_id, grade=grade, term=term, provider_payment_id=event_id,
                                 idempotency_key=f"provider:{event_id}")
    return checkout_term(req, db=db, is_verified_provider=True)


def refund_transaction(receipt_number: str, *, db: Session):
    txn = db.query(PaymentTransaction).filter(PaymentTransaction.receipt_number == receipt_number).first()
    if not txn:
        raise ApplicationError(404, "Payment transaction not found")
    txn.status = "refunded"
    txn.refunded_at = datetime.datetime.utcnow()
    db.query(TermAccess).filter(TermAccess.transaction_ref == receipt_number).update({"is_unlocked": False})
    db.commit()
    return {"success": True, "status": "refunded", "receipt_number": receipt_number}


def handle_stripe_webhook(body: bytes, stripe_signature: str | None, *, db: Session):
    """
    Verifies Stripe signature v1 and idempotently processes successful checkout events.
    Enforces secret configuration and replay window checks.
    """
    secret = os.getenv("FAHIM_PAYMENT_WEBHOOK_SECRET", "").strip()
    if not secret:
        raise ApplicationError(503, "Payment provider webhook secret is not configured")
    if not stripe_signature:
        raise ApplicationError(401, "Missing Stripe-Signature header")

    parts = {}
    for item in stripe_signature.split(","):
        if "=" in item:
            k, v = item.strip().split("=", 1)
            parts[k] = v
    timestamp = parts.get("t")
    v1 = parts.get("v1")
    if not timestamp or not v1:
        raise ApplicationError(401, "Malformed Stripe-Signature header")

    # Anti-replay window check in production
    try:
        t_int = int(timestamp)
        now_ts = int(datetime.datetime.utcnow().timestamp())
        if abs(now_ts - t_int) > 300 and os.getenv("FAHIM_ENV", "development").lower() == "production":
            raise ApplicationError(400, "Webhook timestamp outside tolerance window")
    except ValueError:
        raise ApplicationError(401, "Invalid timestamp in Stripe-Signature")

    signed_payload = f"{timestamp}.".encode("utf-8") + body
    expected_sig = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, v1):
        raise ApplicationError(401, "Invalid Stripe webhook cryptographic signature")

    try:
        event = json.loads(body.decode("utf-8"))
    except Exception:
        raise ApplicationError(400, "Invalid JSON payload in Stripe webhook")

    event_id = event.get("id")
    event_type = event.get("type")
    data_obj = event.get("data", {}).get("object", {})

    # Hosted checkout (one-off and auto-renewing) and subscription lifecycle events.
    from backend.modules.billing import subscriptions
    handled = subscriptions.handle_event(event_type, data_obj, db)
    if handled is not None:
        return handled

    if event_type in ("checkout.session.completed", "payment_intent.succeeded"):
        metadata = data_obj.get("metadata", {})
        child_id = metadata.get("child_id")
        grade = int(metadata.get("grade", 5))
        term = int(metadata.get("term", 1))
        package_type = metadata.get("package_type", "term")
        provider_id = data_obj.get("id") or event_id

        if not child_id:
            # e.g. the payment_intent of a hosted checkout, recorded from checkout.session.completed instead
            return {"received": True, "event_type": event_type, "ignored": True}

        # Idempotency check
        prior = db.query(PaymentTransaction).filter(
            (PaymentTransaction.provider_event_id == provider_id) |
            (PaymentTransaction.idempotency_key == f"stripe:{provider_id}")
        ).first()
        if prior:
            return _payment_response(prior, db)

        child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
        if not child:
            raise ApplicationError(404, "Child profile not found for webhook event")

        req = PaymentCheckoutRequest(
            child_id=child_id,
            grade=grade,
            term=term,
            package_type=package_type,
            provider_payment_id=provider_id,
            idempotency_key=f"stripe:{provider_id}"
        )
        return checkout_term(req, db=db, is_verified_provider=True)

    return {"received": True, "event_type": event_type}


def checkout_annual_pass(req: AnnualCheckoutRequest, *, db: Session, is_verified_provider: bool = False):
    """
    Unlock the full academic year (Terms 1, 2 and 3): USD 30 less 15% = USD 25.50.
    """
    checkout_req = PaymentCheckoutRequest(
        child_id=req.child_id,
        grade=req.grade,
        term=1,
        package_type="annual",
        payment_method=req.payment_method,
        card_number=req.card_number,
        exp_month=req.exp_month,
        exp_year=req.exp_year,
        cvc=req.cvc,
        cardholder_name=req.cardholder_name,
        promo_code=req.promo_code,
        idempotency_key=req.idempotency_key,
        provider_payment_id=req.provider_payment_id
    )
    return checkout_term(checkout_req, db=db, is_verified_provider=is_verified_provider)


def redeem_voucher(req: VoucherRedeemRequest, *, db: Session):
    """
    Redeem a school-sponsored license code or institutional pass (e.g., SUNRISE2026, ADEK-ARABIC-100).
    Grants immediate full access without requiring card details.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == req.child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")

    clean_code = (req.code or "").strip().upper()
    voucher = db.query(VoucherCode).filter(VoucherCode.code == clean_code).first()

    if not voucher or not voucher.is_active:
        raise ApplicationError(
            status_code=400,
            detail=f"Voucher code '{clean_code}' is invalid, inactive, or does not exist."
        )

    if voucher.expires_at and voucher.expires_at < datetime.datetime.utcnow():
        raise ApplicationError(
            status_code=400,
            detail=f"Voucher code '{clean_code}' expired on {voucher.expires_at.strftime('%Y-%m-%d')}."
        )

    if voucher.redeemed_count >= voucher.max_redemptions:
        raise ApplicationError(
            status_code=400,
            detail=f"Voucher code '{clean_code}' has reached its maximum quota of {voucher.max_redemptions} redemptions."
        )

    # School affinity check if designated
    school_name = "UAE Partner Institution"
    if voucher.school_id:
        sch = db.query(School).filter(School.id == voucher.school_id).first()
        if sch:
            school_name = sch.name

    # Increment redemption counter
    voucher.redeemed_count += 1

    # Determine terms to unlock
    is_annual = voucher.package_type == "annual"
    terms_to_unlock = [1, 2, 3] if is_annual else [1]

    # Generate receipt and invoice identifiers
    txn_id = str(uuid.uuid4())
    receipt_num = f"VCH-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{txn_id[:8].upper()}"
    tax_inv_num = f"INV-VCH-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{txn_id[:6].upper()}"

    # Record 100% sponsored transaction
    txn = PaymentTransaction(
        id=txn_id,
        parent_id=child.parent_id,
        child_id=child.id,
        grade=req.grade,
        term=0 if is_annual else 1,
        amount_usd=0.0,
        subtotal_usd=0.0,
        vat_amount_usd=0.0,
        discount_amount_usd=quote(terms_to_unlock)["list_price_usd"],
        terms_purchased=",".join(map(str, terms_to_unlock)),
        currency="USD",
        package_type="annual" if is_annual else "term",
        status="succeeded",
        payment_method="school_voucher",
        voucher_code=clean_code,
        card_last4="VCHR",
        receipt_number=receipt_num,
        tax_invoice_number=tax_inv_num
    )
    db.add(txn)

    # Unlock student terms
    for t_num in terms_to_unlock:
        access = db.query(TermAccess).filter(
            TermAccess.child_id == child.id,
            TermAccess.grade == req.grade,
            TermAccess.term == t_num
        ).first()

        if not access:
            access = TermAccess(
                child_id=child.id,
                grade=req.grade,
                term=t_num,
                is_unlocked=True,
                unlocked_at=datetime.datetime.utcnow(),
                transaction_ref=receipt_num
            )
            db.add(access)
        else:
            access.is_unlocked = True
            access.unlocked_at = datetime.datetime.utcnow()
            access.transaction_ref = receipt_num

    # Redeeming unlocks this grade; it does not move the child to it.
    if req.grade and not child.default_grade:
        child.default_grade = req.grade

    db.commit()

    pkg_text = "Full Academic Year (Terms 1, 2, & 3)" if is_annual else "Term 1"
    return VoucherRedeemResponse(
        success=True,
        message=f"Institutional voucher '{clean_code}' redeemed successfully! {pkg_text} is now activated courtesy of {school_name}.",
        voucher_code=clean_code,
        package_type=voucher.package_type,
        unlocked_terms=terms_to_unlock,
        receipt_number=receipt_num,
        school_name=school_name
    )


def get_tax_invoice(receipt_number: str, *, db: Session):
    """
    Retrieve official UAE Federal Tax Authority (FTA)-compliant Tax Invoice.
    Includes TRN, 5% VAT itemization, and dual currency representation (USD & AED).
    """
    clean_receipt = receipt_number.strip()
    txn = db.query(PaymentTransaction).filter(
        (PaymentTransaction.receipt_number == clean_receipt) |
        (PaymentTransaction.tax_invoice_number == clean_receipt) |
        (PaymentTransaction.id == clean_receipt)
    ).first()

    if not txn:
        raise ApplicationError(
            status_code=404,
            detail=f"Tax invoice not found for receipt '{clean_receipt}'"
        )

    child = db.query(ChildProfile).filter(ChildProfile.id == txn.child_id).first()
    parent = db.query(User).filter(User.id == txn.parent_id).first()

    parent_name = parent.full_name if parent else "Parent Account"
    parent_email = parent.email if parent else "parent@fahim.ae"
    student_name = child.name if child else "Student"
    school_name = child.school_name if child and child.school_name else "Sunrise International School, Abu Dhabi"

    terms = [int(t) for t in (txn.terms_purchased or "").split(",") if t.strip().isdigit()] \
        or ([1, 2, 3] if (txn.package_type == "annual" or txn.term == 0) else [txn.term])
    is_annual = len(terms) == 3
    gross_total = float(txn.amount_usd or 0.0)
    discount = float(txn.discount_amount_usd or 0.0)
    unit_price = round(gross_total + discount, 2)  # list price before the annual discount and promo
    taxable_amount = float(txn.subtotal_usd) if txn.subtotal_usd is not None else (round(gross_total / 1.05, 2) if gross_total > 0 else 0.0)
    vat_amt = float(txn.vat_amount_usd) if txn.vat_amount_usd is not None else (round(gross_total - taxable_amount, 2) if gross_total > 0 else 0.0)
    total_aed = round(gross_total * AED_PEG, 2)
    renewal = " - auto-renewing subscription" if txn.subscription_id else ""
    terms_en = ", ".join(map(str, terms))

    item = TaxInvoiceItem(
        description_ar=("باقة الاشتراك السنوي الشامل - لغة عربية (الفصول 1، 2، 3)" if is_annual
                        else f"ترخيص الفصل الدراسي {'، '.join(map(str, terms))} - لغة عربية"),
        description_en=(f"Annual Full Academic Pass - Arabic Curriculum (Terms 1, 2, 3) - Class {txn.grade}{renewal}" if is_annual
                        else f"Term{'s' if len(terms) > 1 else ''} {terms_en} Full Arabic Curriculum License - Class {txn.grade}{renewal}"),
        qty=1,
        unit_price_usd=unit_price,
        discount_usd=discount,
        taxable_amount_usd=taxable_amount,
        vat_rate_pct=5.0,
        vat_amount_usd=vat_amt,
        total_usd=gross_total,
        total_aed=total_aed
    )

    inv_num = txn.tax_invoice_number or f"INV-{txn.receipt_number}"
    issue_date_str = txn.created_at.strftime("%d %B %Y, %I:%M %p UTC")

    return TaxInvoiceResponse(
        invoice_number=inv_num,
        trn=FAHIM_TRN,
        issue_date=issue_date_str,
        parent_name=parent_name,
        parent_email=parent_email,
        student_name=student_name,
        school_name=school_name,
        grade=txn.grade,
        package_type="annual" if is_annual else "term",
        payment_method=txn.payment_method,
        currency_usd="USD",
        currency_aed="AED",
        fx_rate=AED_PEG,
        subtotal_usd=taxable_amount,
        vat_amount_usd=vat_amt,
        total_usd=gross_total,
        total_aed=total_aed,
        items=[item],
        status=txn.status.upper()
    )


def list_receipts(child_id: str, *, db: Session):
    """List purchase receipts and transaction history for a learner."""
    txns = db.query(PaymentTransaction).filter(
        PaymentTransaction.child_id == child_id
    ).order_by(PaymentTransaction.created_at.desc()).all()

    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    school_name = child.school_name if child and child.school_name else "Sunrise International School"

    return [
        {
            "id": t.id,
            "receipt_number": t.receipt_number,
            "tax_invoice_number": t.tax_invoice_number or f"INV-{t.receipt_number}",
            "grade": t.grade,
            "term": t.term,
            "package_type": t.package_type or ("annual" if t.term == 0 else "term"),
            "amount_usd": float(t.amount_usd) if t.amount_usd is not None else 0.0,
            "subtotal_usd": float(t.subtotal_usd) if t.subtotal_usd is not None else round(float(t.amount_usd or 0) / 1.05, 2),
            "vat_amount_usd": float(t.vat_amount_usd) if t.vat_amount_usd is not None else round(float(t.amount_usd or 0) - (float(t.amount_usd or 0) / 1.05), 2),
            "amount_aed": round(float(t.amount_usd or 0) * AED_PEG, 2),
            "currency": t.currency,
            "status": t.status,
            "payment_method": t.payment_method,
            "card_last4": t.card_last4,
            "promo_code": t.promo_code,
            "voucher_code": t.voucher_code,
            "terms_purchased": t.terms_purchased,
            "subscription_id": t.subscription_id,
            "school_name": school_name,
            "trn": FAHIM_TRN,
            "created_at": t.created_at.isoformat()
        }
        for t in txns
    ]
