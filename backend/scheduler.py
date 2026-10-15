"""In-process scheduler for periodic jobs: the Gemini health check and the weekly parent emails.

Runs in production (or when FAHIM_ENABLE_SCHEDULER=1). Each job takes a short-lived cache
lock before running, so several API replicas don't duplicate work; the weekly email job is
additionally idempotent per child and week.
"""
import datetime
import logging
import os
import threading

from backend.redis_client import cache_get, cache_set

logger = logging.getLogger("fahim.scheduler")

TICK_SECONDS = 300
GEMINI_PROBE_EVERY_SECONDS = 20 * 60
# Scheduled checks failing this many times in a row means Gemini is down, not a blip: alert at once.
# (The usual "3 failures in 10 minutes" rule can't be met by a check that runs every 20 minutes.)
GEMINI_PROBE_FAILURES_TO_ALERT = 2
# Weekly report goes out on Sunday from 04:00 UTC (08:00 UAE time).
WEEKLY_REPORT_WEEKDAY = 6
WEEKLY_REPORT_HOUR_UTC = 4

_thread = None
_stop = threading.Event()


def _claim(job: str, ttl_seconds: int) -> bool:
    key = f"scheduler:lock:{job}"
    if cache_get(key):
        return False
    cache_set(key, True, ttl_seconds=ttl_seconds)
    return True


def run_gemini_probe():
    from backend.modules.tutoring.assistant import probe_gemini

    result = probe_gemini()
    cache_set("scheduler:last:gemini_probe", {**result, "at": datetime.datetime.now(datetime.UTC).isoformat()}, ttl_seconds=86400)
    return result


def run_weekly_reports(now=None):
    from backend.database import SessionLocal
    from backend.modules.progress.reporting import send_scheduled_weekly_reports

    db = SessionLocal()
    try:
        summary = send_scheduled_weekly_reports(db=db, now=now)
    finally:
        db.close()
    logger.info("weekly reports", extra={"event": "weekly_reports", "error": str(summary)})
    cache_set("scheduler:last:weekly_reports", {**summary, "at": datetime.datetime.now(datetime.UTC).isoformat()}, ttl_seconds=8 * 86400)
    return summary


def weekly_reports_due(now: datetime.datetime) -> bool:
    return now.weekday() == WEEKLY_REPORT_WEEKDAY and now.hour >= WEEKLY_REPORT_HOUR_UTC


def run_scheduled_gemini_probe():
    """The periodic check: alerts when it fails GEMINI_PROBE_FAILURES_TO_ALERT times in a row."""
    from backend import alerts

    result = run_gemini_probe()
    streak = 0 if result.get("ok") else int(cache_get("scheduler:gemini_probe_failures") or 0) + 1
    cache_set("scheduler:gemini_probe_failures", streak, ttl_seconds=86400)
    if streak >= GEMINI_PROBE_FAILURES_TO_ALERT:
        minutes = (streak - 1) * GEMINI_PROBE_EVERY_SECONDS // 60
        alerts.alert_now("gemini", f"The automatic Gemini check has failed {streak} times in a row "
                                   f"(over about {minutes} minutes). Ask Fahim, word meanings, solving help, "
                                   "textbook reading and lesson drafting are not working.", result.get("error"))
    return result


def tick(now=None):
    now = now or datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    if _claim("gemini_probe", GEMINI_PROBE_EVERY_SECONDS - 30):
        try:
            run_scheduled_gemini_probe()
        except Exception as exc:
            logger.warning("Gemini probe job failed: %s", exc)
    if weekly_reports_due(now) and _claim(f"weekly_reports:{now.date().isoformat()}:{now.hour}", 3600):
        try:
            run_weekly_reports(now)
        except Exception as exc:
            logger.warning("Weekly report job failed: %s", exc)


def _loop():
    # Let the app finish starting before the first check.
    if _stop.wait(60):
        return
    while not _stop.is_set():
        tick()
        _stop.wait(TICK_SECONDS)


def scheduler_enabled() -> bool:
    if os.getenv("FAHIM_ENABLE_SCHEDULER", "").lower() in ("1", "true", "yes"):
        return True
    if os.getenv("FAHIM_DISABLE_SCHEDULER", "").lower() in ("1", "true", "yes"):
        return False
    return os.getenv("FAHIM_ENV", "development").lower() == "production"


def start():
    global _thread
    if _thread is not None or not scheduler_enabled():
        return
    _stop.clear()
    _thread = threading.Thread(target=_loop, name="jisr-scheduler", daemon=True)
    _thread.start()


def stop():
    global _thread
    _stop.set()
    _thread = None
