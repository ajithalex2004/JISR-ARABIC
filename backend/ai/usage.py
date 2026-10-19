"""AI usage accounting: one row per AI call, daily limits per learner, monthly budget alerts.

Settings (environment):
  FAHIM_AI_PRICES             JSON of USD per million tokens per model, e.g.
                              {"gemini-3.5-flash-lite": {"input": 0.1, "output": 0.4}}.
                              Models without a price are counted in tokens but not in dollars.
  FAHIM_AI_DAILY_LIMIT        AI requests per learner per day for learner features (default 60, 0 = off)
  FAHIM_SPEECH_DAILY_LIMIT    speaking-practice recordings transcribed per learner per day (default 40, 0 = off)
  FAHIM_AI_MONTHLY_BUDGET_USD Monthly AI budget; alerts at 50%, 80% and 100% (unset = no budget)
  FAHIM_AI_BUDGET_HARD_STOP   1 = once the budget is spent, learner features pause until next month
Recording never breaks the AI call it describes.
"""
import datetime
import json
import logging
import os
from typing import Any, Dict, Optional

from sqlalchemy import func

logger = logging.getLogger("fahim.ai")

# Features a learner can call at will; these count towards the daily limit.
LEARNER_FEATURES = ("ask_fahim", "learn_with_fahim", "paper_solver")
BUDGET_THRESHOLDS = (50, 80, 100)

_session_factory = None


def set_session_factory(factory) -> None:
    """Tests point usage recording at their own database."""
    global _session_factory
    _session_factory = factory


def _session():
    if _session_factory is not None:
        return _session_factory()
    from backend.database import SessionLocal
    return SessionLocal()


def _env_float(name: str) -> Optional[float]:
    try:
        value = os.getenv(name, "").strip()
        return float(value) if value else None
    except ValueError:
        return None


def daily_limit() -> int:
    value = _env_float("FAHIM_AI_DAILY_LIMIT")
    return 60 if value is None else max(0, int(value))


def monthly_budget() -> Optional[float]:
    budget = _env_float("FAHIM_AI_MONTHLY_BUDGET_USD")
    return budget if budget and budget > 0 else None


def prices() -> Dict[str, Dict[str, float]]:
    try:
        return json.loads(os.getenv("FAHIM_AI_PRICES", "") or "{}")
    except ValueError:
        logger.warning("FAHIM_AI_PRICES is not valid JSON; costs are not calculated")
        return {}


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    price = prices().get(model or "")
    if not isinstance(price, dict):
        return None
    try:
        return round(input_tokens / 1e6 * float(price.get("input", 0))
                     + output_tokens / 1e6 * float(price.get("output", 0)), 6)
    except (TypeError, ValueError):
        return None


def _now() -> datetime.datetime:
    return datetime.datetime.utcnow()


def _month_start(now: datetime.datetime) -> datetime.datetime:
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def record(*, feature: str, provider: str, model: str, input_tokens: int = 0, output_tokens: int = 0,
           ok: bool = True, fallback: bool = False, latency_ms: Optional[int] = None,
           learner_id: Optional[str] = None, error: Optional[str] = None) -> Optional[float]:
    """Store one call; returns its cost (None when the model has no price)."""
    from backend.models import AIUsage

    cost = cost_usd(model, input_tokens, output_tokens) if ok else None
    try:
        db = _session()
        try:
            db.add(AIUsage(feature=feature, provider=provider, model=model, input_tokens=input_tokens,
                           output_tokens=output_tokens, cost_usd=cost, ok=ok, fallback=fallback,
                           latency_ms=latency_ms, learner_id=learner_id,
                           error=(" ".join(str(error).split())[:300] if error else None)))
            db.commit()
        finally:
            db.close()
    except Exception as exc:
        logger.debug("Could not record AI usage: %s", exc)
        return cost
    if cost:
        check_budget()
    return cost


def learner_feature_calls_today(learner_id: str, feature: str) -> int:
    """Successful calls of one feature by this learner since midnight (server time)."""
    from backend.models import AIUsage

    start = _now().replace(hour=0, minute=0, second=0, microsecond=0)
    try:
        db = _session()
        try:
            return db.query(func.count(AIUsage.id)).filter(
                AIUsage.learner_id == learner_id, AIUsage.created_at >= start,
                AIUsage.feature == feature, AIUsage.ok.is_(True),
            ).scalar() or 0
        finally:
            db.close()
    except Exception as exc:
        logger.debug("Could not read AI usage: %s", exc)
        return 0


def learner_calls_today(learner_id: str) -> int:
    from backend.models import AIUsage

    start = _now().replace(hour=0, minute=0, second=0, microsecond=0)
    try:
        db = _session()
        try:
            return db.query(func.count(AIUsage.id)).filter(
                AIUsage.learner_id == learner_id, AIUsage.created_at >= start,
                AIUsage.feature.in_(LEARNER_FEATURES), AIUsage.ok.is_(True),
            ).scalar() or 0
        finally:
            db.close()
    except Exception as exc:
        logger.debug("Could not read AI usage: %s", exc)
        return 0


def month_cost() -> float:
    from backend.models import AIUsage

    try:
        db = _session()
        try:
            return float(db.query(func.coalesce(func.sum(AIUsage.cost_usd), 0.0)).filter(
                AIUsage.created_at >= _month_start(_now())).scalar() or 0.0)
        finally:
            db.close()
    except Exception:
        return 0.0


def budget_spent() -> bool:
    budget = monthly_budget()
    return bool(budget) and month_cost() >= budget


def check_budget() -> None:
    """Alert once per threshold per month as spending passes 50%, 80% and 100% of the budget."""
    from backend import alerts
    from backend.redis_client import cache_get, cache_set

    budget = monthly_budget()
    if not budget:
        return
    spent = month_cost()
    month = _now().strftime("%Y-%m")
    for threshold in BUDGET_THRESHOLDS:
        if spent < budget * threshold / 100:
            continue
        key = f"ai:budget_alert:{month}:{threshold}"
        if cache_get(key):
            continue
        cache_set(key, True, ttl_seconds=40 * 86400)
        hard_stop = threshold == 100 and os.getenv("FAHIM_AI_BUDGET_HARD_STOP", "") == "1"
        alerts.notify("ai", f"[JISR alert] AI spending reached {threshold}% of the monthly budget",
                      f"AI spending this month is ${spent:.2f} of the ${budget:.2f} budget ({threshold}%)."
                      + (" Learner AI features are paused until next month (FAHIM_AI_BUDGET_HARD_STOP=1)." if hard_stop else "")
                      + "\n\nSee Admin > System health for spending by feature.")


def report() -> Dict[str, Any]:
    """This month's AI usage for the System health cost panel."""
    from backend.models import AIUsage

    now = _now()
    start = _month_start(now)
    budget = monthly_budget()
    result: Dict[str, Any] = {
        "month": now.strftime("%Y-%m"), "budget_usd": budget, "daily_limit": daily_limit(),
        "hard_stop": os.getenv("FAHIM_AI_BUDGET_HARD_STOP", "") == "1",
        "prices_configured": sorted(prices().keys()),
        "calls": 0, "failed_calls": 0, "fallback_calls": 0, "input_tokens": 0, "output_tokens": 0,
        "cost_usd": 0.0, "unpriced_calls": 0, "by_feature": [], "by_provider": [],
    }
    try:
        db = _session()
        try:
            def grouped(column):
                return db.query(
                    column, func.count(AIUsage.id),
                    func.sum(case_ok(AIUsage)), func.coalesce(func.sum(AIUsage.input_tokens), 0),
                    func.coalesce(func.sum(AIUsage.output_tokens), 0), func.coalesce(func.sum(AIUsage.cost_usd), 0.0),
                ).filter(AIUsage.created_at >= start).group_by(column).all()

            for key, rows in (("by_feature", grouped(AIUsage.feature)), ("by_provider", grouped(AIUsage.provider))):
                result[key] = sorted(({"name": name, "calls": calls, "ok": int(ok or 0), "input_tokens": int(inp),
                                       "output_tokens": int(out), "cost_usd": round(float(cost), 4)}
                                      for name, calls, ok, inp, out, cost in rows), key=lambda r: -r["calls"])
            month = db.query(AIUsage).filter(AIUsage.created_at >= start)
            result["calls"] = month.count()
            result["failed_calls"] = month.filter(AIUsage.ok.is_(False)).count()
            result["fallback_calls"] = month.filter(AIUsage.fallback.is_(True), AIUsage.ok.is_(True)).count()
            result["unpriced_calls"] = month.filter(AIUsage.ok.is_(True), AIUsage.cost_usd.is_(None)).count()
            result["input_tokens"] = sum(r["input_tokens"] for r in result["by_provider"])
            result["output_tokens"] = sum(r["output_tokens"] for r in result["by_provider"])
            result["cost_usd"] = round(sum(r["cost_usd"] for r in result["by_provider"]), 4)
        finally:
            db.close()
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"[:300]
    if budget:
        result["budget_used_pct"] = round(result["cost_usd"] / budget * 100, 1)
    return result


def case_ok(model):
    from sqlalchemy import case
    return case((model.ok.is_(True), 1), else_=0)
