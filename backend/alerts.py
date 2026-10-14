"""Failure alerts for the services the app silently falls back from (Gemini, payments, email).

``record_failure`` is called wherever such a failure is caught. Failures are counted per
component over a short window; once a component fails ``FAHIM_ALERT_THRESHOLD`` times
within ``FAHIM_ALERT_WINDOW_SECONDS``, admins are emailed (and an optional chat webhook is
posted to), at most once per ``FAHIM_ALERT_COOLDOWN_SECONDS`` per component.

Recipients: ``FAHIM_ALERT_EMAILS`` (comma separated), or every admin account when unset.
Optional webhook: ``FAHIM_ALERT_WEBHOOK_URL`` (Slack, Google Chat or Discord incoming webhook).
"""
import datetime
import logging
import os
import threading
from typing import List, Optional

from backend.redis_client import cache_get, cache_set, check_rate_limit

logger = logging.getLogger("fahim.alerts")

COMPONENTS = {
    "gemini": "Gemini AI (Ask Fahim, word meanings, solving)",
    "payments": "Payments",
    "email": "Email delivery",
    "server": "Server errors",
}
RECENT_LIMIT = 20
_RECENT_TTL = 7 * 24 * 3600


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def threshold() -> int:
    return max(1, _env_int("FAHIM_ALERT_THRESHOLD", 3))


def window_seconds() -> int:
    return max(60, _env_int("FAHIM_ALERT_WINDOW_SECONDS", 600))


def cooldown_seconds() -> int:
    return max(60, _env_int("FAHIM_ALERT_COOLDOWN_SECONDS", 3600))


def _now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()


def _short(detail) -> str:
    text = " ".join(str(detail or "").split())
    return text[:300]


def recent_failures(component: str) -> List[dict]:
    return cache_get(f"alerts:recent:{component}") or []


def last_alert(component: str) -> Optional[dict]:
    return cache_get(f"alerts:last:{component}")


def failures_in_window(component: str) -> int:
    cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=window_seconds())
    count = 0
    for event in recent_failures(component):
        try:
            if datetime.datetime.fromisoformat(event["at"]) >= cutoff:
                count += 1
        except (KeyError, ValueError):
            continue
    return count


def record_failure(component: str, detail="", *, background: bool = True) -> bool:
    """Note a failure; returns True when this failure triggered an alert."""
    if component not in COMPONENTS:
        component = "server"
    detail = _short(detail)
    try:
        logger.error("service failure", extra={"event": f"failure.{component}", "error": detail})
        events = [{"at": _now_iso(), "detail": detail}] + recent_failures(component)
        cache_set(f"alerts:recent:{component}", events[:RECENT_LIMIT], ttl_seconds=_RECENT_TTL)

        _, count, _ = check_rate_limit(f"alerts:count:{component}", limit=10_000, window_seconds=window_seconds())
        if count < threshold() or cache_get(f"alerts:cooldown:{component}"):
            return False
        cache_set(f"alerts:cooldown:{component}", True, ttl_seconds=cooldown_seconds())
    except Exception as exc:  # alerting must never break the request that failed
        logger.warning("Could not record %s failure: %s", component, exc)
        return False

    subject = f"[JISR alert] {COMPONENTS[component]} is failing"
    body = (
        f"{COMPONENTS[component]} failed {count} times in the last {window_seconds() // 60} minutes.\n\n"
        f"Latest error:\n{detail or '(no details)'}\n\n"
        "Check Admin > System health on the JISR website for recent failures.\n"
        f"You won't get another alert for this for {cooldown_seconds() // 60} minutes."
    )
    if background:
        threading.Thread(target=send_alert, args=(component, subject, body), daemon=True).start()
    else:
        send_alert(component, subject, body)
    return True


def alert_recipients() -> List[str]:
    configured = [e.strip() for e in os.getenv("FAHIM_ALERT_EMAILS", "").split(",") if e.strip()]
    if configured:
        return configured
    try:
        from backend.database import SessionLocal
        from backend.models import User

        db = SessionLocal()
        try:
            return [u.email for u in db.query(User).filter(User.role == "admin").all() if u.email]
        finally:
            db.close()
    except Exception as exc:
        logger.warning("Could not load admin alert recipients: %s", exc)
        return []


def _post_webhook(url: str, text: str) -> None:
    import requests

    # "text" is read by Slack and Google Chat, "content" by Discord.
    response = requests.post(url, json={"text": text, "content": text}, timeout=10)
    response.raise_for_status()


def send_alert(component: str, subject: str, body: str) -> dict:
    """Deliver an alert by email and webhook; failures here are logged, never re-alerted."""
    from backend.email_delivery import email_configured, send_email

    delivered, errors = [], []
    if email_configured():
        for recipient in alert_recipients():
            try:
                send_email(recipient, subject, body, record_failures=False)
                delivered.append(recipient)
            except Exception as exc:
                errors.append(f"{recipient}: {_short(exc)}")
    else:
        errors.append("Email is not configured")
    webhook = os.getenv("FAHIM_ALERT_WEBHOOK_URL", "").strip()
    if webhook:
        try:
            _post_webhook(webhook, f"*{subject}*\n{body}")
            delivered.append("webhook")
        except Exception as exc:
            errors.append(f"webhook: {_short(exc)}")

    result = {"at": _now_iso(), "subject": subject, "delivered_to": delivered, "errors": errors}
    if delivered:
        logger.error("alert sent", extra={"event": f"alert.{component}", "error": subject})
    else:
        logger.error("alert could not be delivered", extra={"event": f"alert.{component}", "error": "; ".join(errors)})
    cache_set(f"alerts:last:{component}", result, ttl_seconds=_RECENT_TTL)
    return result


def component_for_path(path: str) -> str:
    return "payments" if path.startswith("/api/payments") else "server"


def status_report() -> dict:
    """Snapshot for the admin System health panel."""
    return {
        "threshold": threshold(),
        "window_minutes": window_seconds() // 60,
        "cooldown_minutes": cooldown_seconds() // 60,
        "email_configured": _email_configured(),
        "recipients": alert_recipients(),
        "webhook_configured": bool(os.getenv("FAHIM_ALERT_WEBHOOK_URL", "").strip()),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
        "components": [
            {
                "key": key,
                "label": label,
                "failures_in_window": failures_in_window(key),
                "recent_failures": recent_failures(key),
                "last_alert": last_alert(key),
            }
            for key, label in COMPONENTS.items()
        ],
    }


def _email_configured() -> bool:
    from backend.email_delivery import email_configured

    return email_configured()
