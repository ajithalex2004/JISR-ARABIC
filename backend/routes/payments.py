from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.dependencies import get_current_user, get_optional_user
from backend.modules.identity.access import Principal, require_child, require_invoice, require_roles, PARENT_ROLES
from backend.observability import audit_event
"""HTTP adapter: request parsing, dependency injection, and service delegation."""
from fastapi import APIRouter, Depends, Header, Request
from backend.schemas import PaymentCheckoutRequest, PaymentResponse, AnnualCheckoutRequest, VoucherRedeemRequest, VoucherRedeemResponse, TaxInvoiceResponse
from backend.modules.billing import service as service
router = APIRouter(prefix='/api/payments', tags=['Payments'])

@router.post('/webhook')
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """
    Native Stripe Webhook receiver with cryptographic signature verification.
    Verifies webhook secret, parses checkout.session.completed or payment_intent.succeeded,
    and idempotently activates term access.
    """
    body = await request.body()
    return service.handle_stripe_webhook(body, stripe_signature, db=db)

@router.post('/checkout', response_model=PaymentResponse)
def checkout_term(req: PaymentCheckoutRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Unlock a Single Term for USD 20 (or USD 50 if package_type='annual').
    Supports card details and promo code.
    Immediately updates TermAccess to True upon successful checkout.
    """
    require_child(db, actor, req.child_id, PARENT_ROLES)
    result = service.checkout_term(req=req, db=db)
    audit_event("payment.checkout", user_id=getattr(actor, "id", None), child_id=req.child_id, status="accepted")
    return result

@router.post('/checkout-annual', response_model=PaymentResponse)
def checkout_annual_pass(req: AnnualCheckoutRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Unlock Full Academic Year (Terms 1, 2, and 3) for USD 50 (15% discount).
    """
    require_child(db, actor, req.child_id, PARENT_ROLES)
    return service.checkout_annual_pass(req=req, db=db)

@router.post('/provider-webhook')
def provider_webhook(event_id: str, child_id: str, grade: int, term: int, status: str,
                     signature: str = Header(None), actor: Principal=Depends(get_optional_user), db: Session=Depends(get_db)):
    """Apply a signed provider event exactly once; client checkout cannot unlock production access."""
    return service.reconcile_provider_event(event_id, child_id, grade, term, status, signature, db=db)

@router.post('/redeem-voucher', response_model=VoucherRedeemResponse)
def redeem_voucher(req: VoucherRedeemRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Redeem a school-sponsored license code or institutional pass (e.g., SUNRISE2026, ADEK-ARABIC-100).
    Grants immediate full access without requiring card details.
    """
    require_child(db, actor, req.child_id, PARENT_ROLES)
    result = service.redeem_voucher(req=req, db=db)
    audit_event("payment.voucher_redeemed", user_id=getattr(actor, "id", None), child_id=req.child_id)
    return result

@router.get('/invoice/{receipt_number}', response_model=TaxInvoiceResponse)
def get_tax_invoice(receipt_number: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Retrieve official UAE Federal Tax Authority (FTA)-compliant Tax Invoice.
    Includes TRN, 5% VAT itemization, and dual currency representation (USD & AED).
    """
    require_invoice(db, actor, receipt_number)
    return service.get_tax_invoice(receipt_number=receipt_number, db=db)

@router.get('/receipts')
def list_receipts(child_id: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """List purchase receipts and transaction history for a learner."""
    require_child(db, actor, child_id, PARENT_ROLES)
    return service.list_receipts(child_id=child_id, db=db)

@router.post('/refund/{receipt_number}')
def refund_payment(receipt_number: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    require_roles(actor, ("admin",))
    return service.refund_transaction(receipt_number, db=db)
