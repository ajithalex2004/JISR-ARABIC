"""The single entry point for AI calls, with automatic switching between providers.

    from backend.ai.gateway import AIRequest, generate
    reply = generate(AIRequest(feature="ask_fahim", prompt=..., system=..., json=True))

Providers are tried in FAHIM_AI_PROVIDERS order (default "gemini,anthropic"), skipping any that
is not configured. When a provider runs out of credits/quota, or fails FAILURES_TO_SWITCH times
in a row with an outage-type error (key/model rejected, server error, unreachable), it is set
aside for SWITCH_MINUTES and calls go to the next provider; admins get an alert. A provider that
is set aside is still tried as a last resort when every other one fails too.

Errors that are about the request itself (e.g. a schema the model rejects) are not outages: they
are raised to the caller unchanged, without switching provider.

Every call is recorded in the ai_usage table (backend.ai.usage), which also enforces the
per-learner daily limit and the monthly budget.
"""
import datetime
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.ai import usage
from backend.ai.errors import AILimitReached, AIUnavailable
from backend.ai.providers import PROVIDERS, GeminiProvider
from backend.gemini_quota import GeminiQuotaExhausted, call_with_quota_retry, is_quota_error, pause_message
from backend.redis_client import cache_get, cache_set

logger = logging.getLogger("fahim.ai")

SWITCH_MINUTES = 10
FAILURES_TO_SWITCH = 3
_UNSET = object()


@dataclass
class AIRequest:
    feature: str                      # e.g. "ask_fahim"; used for usage reports and limits
    prompt: str
    system: Optional[str] = None
    attachments: List[Tuple[Union[bytes, Path], str]] = field(default_factory=list)  # (data, mime type)
    json: bool = False                # reply must be a JSON object
    schema: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    child_safe: bool = True
    tier: str = "fast"                # "fast" (chat) or "strong" (page reading, drafting)
    gemini_model: Optional[str] = None
    learner_id: Optional[str] = None  # counts towards this learner's daily limit
    retry_on_rate_limit: bool = False  # wait and retry a rate limit when no other provider is left
    timeout: float = 120.0


@dataclass
class AIResponse:
    text: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: Optional[float] = None
    fallback: bool = False


def provider_order() -> List[str]:
    names = [n.strip().lower() for n in (os.getenv("FAHIM_AI_PROVIDERS") or "gemini,anthropic").split(",")]
    return [n for n in names if n in PROVIDERS]


def _providers(gemini_client=_UNSET) -> List[Any]:
    result = []
    for name in provider_order():
        if name == "gemini":
            provider = GeminiProvider() if gemini_client is _UNSET else GeminiProvider(client=gemini_client)
            if gemini_client is not _UNSET and gemini_client is None:
                continue
        else:
            provider = PROVIDERS[name]()
        if provider.available():
            result.append(provider)
    return result


def available(gemini_client=_UNSET) -> bool:
    return bool(_providers(gemini_client))


# --- automatic switching ------------------------------------------------------------------

_CODE_IN_TEXT = re.compile(r"^\s*(\d{3})\b")


def _status_code(exc: BaseException) -> Optional[int]:
    for attr in ("code", "status_code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    match = _CODE_IN_TEXT.match(str(exc))
    return int(match.group(1)) if match else None


def is_outage(exc: BaseException) -> bool:
    """True when the provider itself is failing (switch provider), False for a bad request."""
    if isinstance(exc, AIUnavailable) or is_quota_error(exc):
        return True
    text = str(exc).lower()
    code = _status_code(exc)
    if code is not None:
        if code in (400, 413, 422):
            return "credit balance" in text  # Claude reports exhausted credits as a 400
        return code in (401, 402, 403, 404, 408, 409, 429) or code >= 500
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return True
    module = type(exc).__module__ or ""
    return module.startswith(("httpx", "httpcore", "requests", "google.api_core", "google.genai"))


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def switched_until(name: str) -> Optional[datetime.datetime]:
    value = cache_get(f"ai:switched:{name}")
    try:
        until = datetime.datetime.fromisoformat(value) if value else None
    except (TypeError, ValueError):
        return None
    return until if until and until > _now() else None


def _note_success(name: str) -> None:
    if cache_get(f"ai:failures:{name}"):
        cache_set(f"ai:failures:{name}", 0, ttl_seconds=3600)


def _note_failure(name: str, exc: BaseException, feature: str, fallback: Optional[str]) -> None:
    failures = int(cache_get(f"ai:failures:{name}") or 0) + 1
    cache_set(f"ai:failures:{name}", failures, ttl_seconds=3600)
    if switched_until(name) or not (is_quota_error(exc) or failures >= FAILURES_TO_SWITCH):
        return
    until = _now() + datetime.timedelta(minutes=SWITCH_MINUTES)
    cache_set(f"ai:switched:{name}", until.isoformat(), ttl_seconds=SWITCH_MINUTES * 60)
    from backend import alerts
    reason = "is out of credits or quota" if is_quota_error(exc) else f"failed {failures} times in a row"
    target = f"AI requests now go to {fallback} for {SWITCH_MINUTES} minutes." if fallback \
        else "No other AI provider is configured, so AI features may not work."
    alerts.alert_now("ai", f"{name} {reason} (last feature: {feature}). {target}", str(exc))


def status() -> List[Dict[str, Any]]:
    """Provider list for System health: configured, set aside until when, recent failures."""
    from backend.ai.providers import AnthropicProvider
    result = []
    for name in provider_order():
        provider = PROVIDERS[name]()
        until = switched_until(name)
        entry = {"name": name, "configured": provider.available(),
                 "switched_until": until.isoformat() if until else None,
                 "consecutive_failures": int(cache_get(f"ai:failures:{name}") or 0)}
        if isinstance(provider, AnthropicProvider):
            entry["models"] = {"fast": provider.model_for(AIRequest(feature="", prompt="")),
                               "strong": provider.model_for(AIRequest(feature="", prompt="", tier="strong"))}
        result.append(entry)
    return result


# --- the call -----------------------------------------------------------------------------

def _check_limits(request: AIRequest) -> None:
    if request.feature not in usage.LEARNER_FEATURES:
        return
    if os.getenv("FAHIM_AI_BUDGET_HARD_STOP", "") == "1" and usage.budget_spent():
        raise AILimitReached("budget", "The monthly AI budget is used up.")
    limit = usage.daily_limit()
    if request.learner_id and limit and usage.learner_calls_today(request.learner_id) >= limit:
        raise AILimitReached("daily", f"This learner has used today's {limit} AI requests.")


def generate(request: AIRequest, *, gemini_client=_UNSET) -> AIResponse:
    """Answer with the first provider that can; see the module docstring for the rules.

    gemini_client lets callers that already hold a Gemini client (and tests) pass it in;
    None means Gemini is not available for this call.
    """
    providers = _providers(gemini_client)
    if not providers:
        raise AIUnavailable("No AI provider is configured (set GEMINI_API_KEY or ANTHROPIC_API_KEY).")
    _check_limits(request)

    primary = providers[0].name
    ordered = [p for p in providers if not switched_until(p.name)] + [p for p in providers if switched_until(p.name)]
    failures: List[Tuple[str, BaseException]] = []
    for index, provider in enumerate(ordered):
        last = index == len(ordered) - 1
        next_name = ordered[index + 1].name if not last else None
        model = provider.model_for(request)
        started = time.perf_counter()
        try:
            if request.retry_on_rate_limit and last:
                text, model, tokens_in, tokens_out = call_with_quota_retry(
                    lambda: provider.generate(request), label=f"{request.feature} via {provider.name}")
            else:
                text, model, tokens_in, tokens_out = provider.generate(request)
        except Exception as exc:
            latency = round((time.perf_counter() - started) * 1000)
            usage.record(feature=request.feature, provider=provider.name, model=model, ok=False,
                         fallback=provider.name != primary, latency_ms=latency,
                         learner_id=request.learner_id, error=str(exc))
            if not is_outage(exc):
                raise
            from backend import alerts
            alerts.record_failure("gemini" if provider.name == "gemini" else "ai",
                                  f"{request.feature} via {provider.name} ({model}): {exc}")
            _note_failure(provider.name, exc, request.feature, next_name)
            failures.append((provider.name, exc))
            logger.warning("AI %s via %s failed, %s: %s", request.feature, provider.name,
                           f"trying {next_name}" if next_name else "no provider left", exc)
            continue
        latency = round((time.perf_counter() - started) * 1000)
        _note_success(provider.name)
        cost = usage.record(feature=request.feature, provider=provider.name, model=model,
                            input_tokens=tokens_in, output_tokens=tokens_out, ok=True,
                            fallback=provider.name != primary, latency_ms=latency, learner_id=request.learner_id)
        return AIResponse(text=text, provider=provider.name, model=model, input_tokens=tokens_in,
                          output_tokens=tokens_out, cost_usd=cost, fallback=provider.name != primary)

    if all(is_quota_error(exc) for _, exc in failures):
        raise GeminiQuotaExhausted(pause_message(failures[0][1]))
    summary = "; ".join(f"{name}: {' '.join(str(exc).split())[:150]}" for name, exc in failures)
    raise AIUnavailable(f"AI is unavailable ({summary})")


def probe_gemini(gemini_client=_UNSET) -> AIResponse:
    """One tiny Gemini call for the health check (no switching: it tests Gemini itself)."""
    provider = GeminiProvider() if gemini_client is _UNSET else GeminiProvider(client=gemini_client)
    request = AIRequest(feature="health_check", prompt="Reply with the single word: ok", child_safe=False)
    started = time.perf_counter()
    model = provider.model_for(request)
    try:
        text, model, tokens_in, tokens_out = provider.generate(request)
    except Exception as exc:
        usage.record(feature="health_check", provider="gemini", model=model, ok=False,
                     latency_ms=round((time.perf_counter() - started) * 1000), error=str(exc))
        raise
    usage.record(feature="health_check", provider="gemini", model=model, input_tokens=tokens_in,
                 output_tokens=tokens_out, latency_ms=round((time.perf_counter() - started) * 1000))
    _note_success("gemini")
    return AIResponse(text=text, provider="gemini", model=model, input_tokens=tokens_in, output_tokens=tokens_out)
