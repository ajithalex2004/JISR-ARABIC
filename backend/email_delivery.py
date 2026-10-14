"""Transactional email delivery: Resend HTTP API (when RESEND_API_KEY is set) or SMTP."""
import os
import smtplib
from email.message import EmailMessage

import logging

logger = logging.getLogger("fahim.email")

def _mask_email(email: str) -> str:
    """Mask email for privacy in logs (e.g. jo***@domain.com)."""
    if not email or "@" not in email:
        return "masked_recipient"
    name, domain = email.split("@", 1)
    masked_name = name[:2] + "***" if len(name) > 2 else "***"
    return f"{masked_name}@{domain}"


def _smtp_password() -> str:
    # FAHIM_SMTP_PASS is the documented name; FAHIM_SMTP_PASSWORD is accepted for older configs.
    return os.getenv("FAHIM_SMTP_PASS", "") or os.getenv("FAHIM_SMTP_PASSWORD", "")


def _sender() -> str:
    return os.getenv("FAHIM_SMTP_FROM", "").strip() or "noreply@jisrarabic.com"


def email_configured() -> bool:
    """True when an email transport (Resend API or SMTP) is configured."""
    return bool(os.getenv("RESEND_API_KEY", "").strip() or os.getenv("FAHIM_SMTP_HOST", "").strip())


def _send_via_resend(recipient: str, subject: str, body_text: str) -> None:
    import requests
    response = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {os.environ['RESEND_API_KEY'].strip()}"},
        json={"from": _sender(), "to": [recipient], "subject": subject, "text": body_text},
        timeout=15,
    )
    try:
        response.raise_for_status()
    except Exception as exc:
        # Resend explains rejections (unverified domain, malformed "from", ...) in the body;
        # keep that message so admins can see why an email wasn't sent.
        try:
            reason = response.json().get("message") or response.text
        except Exception:
            reason = getattr(response, "text", "") or exc
        raise RuntimeError(f"Resend rejected the email: {' '.join(str(reason).split())[:300]} [from: {_sender()}]") from exc


def _send_via_smtp(recipient: str, subject: str, body_text: str) -> None:
    host = os.getenv("FAHIM_SMTP_HOST", "").strip()
    port = int(os.getenv("FAHIM_SMTP_PORT", "587"))
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = _sender()
    message["To"] = recipient
    message.set_content(body_text)

    # Support both port 465 (SSL) and port 587 / 25 (STARTTLS)
    if port == 465:
        smtp_conn = smtplib.SMTP_SSL(host, port, timeout=15)
    else:
        smtp_conn = smtplib.SMTP(host, port, timeout=15)
    with smtp_conn as smtp:
        if port != 465 and os.getenv("FAHIM_SMTP_TLS", "1") == "1":
            smtp.starttls()
        username = os.getenv("FAHIM_SMTP_USER", "").strip()
        if username:
            smtp.login(username, _smtp_password())
        smtp.send_message(message)


def send_email(recipient: str, subject: str, body_text: str, *, record_failures: bool = True) -> None:
    """Send a plain-text email through the configured transport; raises on failure."""
    try:
        if os.getenv("RESEND_API_KEY", "").strip():
            _send_via_resend(recipient, subject, body_text)
        else:
            _send_via_smtp(recipient, subject, body_text)
    except Exception as exc:
        if record_failures:
            from backend.alerts import record_failure
            record_failure("email", f"Sending an email to {_mask_email(recipient)} failed: {exc}")
        raise


def send_otp_email(recipient: str, code: str, purpose: str) -> bool:
    masked = _mask_email(recipient)
    if not email_configured():
        logger.info(f"[OTP Delivery] Email not configured for {masked} ({purpose})")
        if os.getenv("FAHIM_ENV", "development").lower() == "production":
            logger.error("[OTP Delivery] Cannot deliver OTP in production: no email transport is configured")
            return False
        return True

    purpose_label = "تسجيل الدخول (Login)" if "login" in purpose else "إنشاء الحساب (Account Signup)" if "signup" in purpose else "استعادة كلمة المرور (Password Reset)"
    subject = f"رمز التحقق لمنصة جسر: {code} | JISR Arabic Verification Code"
    body_text = f"""مرحباً بكم في منصة جسر لتعليم اللغة العربية
Welcome to JISR Arabic Learning Platform

رمز التحقق الخاص بك هو: {code}
Your verification code is: {code}

الغرض: {purpose_label}
صلاحية الرمز: 10 دقائق (Expires in 10 minutes)

إذا لم تقم بطلب هذا الرمز، يُرجى تجاهل هذه الرسالة.
If you did not request this code, please ignore this email.

منصة جسر (JISR Arabic)
"""
    try:
        send_email(recipient, subject, body_text)
        logger.info(f"[OTP Delivery] Successfully dispatched {purpose} verification email to {masked}")
        return True
    except Exception as e:
        logger.warning(f"[OTP Delivery] Failed to send email to {masked} ({purpose}): {e}")
        return False
