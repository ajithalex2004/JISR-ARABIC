"""Small SMTP adapter for transactional OTP delivery."""
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


def send_otp_email(recipient: str, code: str, purpose: str) -> bool:
    host = os.getenv("FAHIM_SMTP_HOST", "").strip()
    masked = _mask_email(recipient)
    if not host:
        logger.info(f"[OTP Delivery] SMTP not configured for {masked} ({purpose})")
        if os.getenv("FAHIM_ENV", "development").lower() == "production":
            logger.error("[OTP Delivery] Cannot deliver OTP in production: FAHIM_SMTP_HOST is not configured")
            return False
        return True

    port = int(os.getenv("FAHIM_SMTP_PORT", "587"))
    sender = os.getenv("FAHIM_SMTP_FROM", "").strip() or "noreply@jisr-arabic.com"
    purpose_label = "تسجيل الدخول (Login)" if "login" in purpose else "إنشاء الحساب (Account Signup)" if "signup" in purpose else "استعادة كلمة المرور (Password Reset)"

    try:
        message = EmailMessage()
        message["Subject"] = f"رمز التحقق لمنصة جسر: {code} | JISR Arabic Verification Code"
        message["From"] = sender
        message["To"] = recipient

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
            password = os.getenv("FAHIM_SMTP_PASSWORD", "")
            if username:
                smtp.login(username, password)
            smtp.send_message(message)

        logger.info(f"[OTP Delivery] Successfully dispatched {purpose} verification email to {masked}")
        return True
    except Exception as e:
        logger.warning(f"[OTP Delivery] Failed to send email to {masked} ({purpose}): {e}")
        return False
