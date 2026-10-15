"""AI gateway: fallback to a second provider, 10-minute switching with alerts, usage and limits."""
import datetime
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from backend.ai import gateway, usage
from backend.ai.errors import AILimitReached, AIUnavailable
from backend.ai.gateway import AIRequest
from backend.ai.providers import AnthropicProvider
from backend.models import AIUsage
from backend.redis_client import _fallback_cache

OUT_OF_CREDITS = RuntimeError("402 RESOURCE_EXHAUSTED. Your prepayment credits are depleted.")
SERVER_ERROR = RuntimeError("503 UNAVAILABLE. The model is overloaded.")


def _gemini(reply="مرحبا", exc=None, calls=None):
    def generate_content(**kwargs):
        if calls is not None:
            calls.append(kwargs)
        if exc:
            raise exc
        return SimpleNamespace(text=reply, usage_metadata=SimpleNamespace(
            prompt_token_count=1000, candidates_token_count=200, thoughts_token_count=50))
    return SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))


class _Response:
    def __init__(self, status, payload):
        self.status_code = status
        self._payload = payload
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


def _claude_ok(text="Claude reply"):
    return _Response(200, {"model": "claude-haiku-5-5", "content": [{"type": "text", "text": text}],
                           "usage": {"input_tokens": 300, "output_tokens": 40}})


class GatewayTest(unittest.TestCase):
    def setUp(self):
        _fallback_cache.clear()
        self._clear_usage()
        self.env = patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key", "FAHIM_AI_PROVIDERS": "gemini,anthropic",
                                           "FAHIM_AI_PRICES": "", "FAHIM_AI_MONTHLY_BUDGET_USD": "",
                                           "FAHIM_AI_DAILY_LIMIT": "", "FAHIM_AI_BUDGET_HARD_STOP": ""})
        self.env.start()
        self.alerts = patch("backend.alerts._dispatch")
        self.dispatch = self.alerts.start()
        self.notify = patch("backend.alerts.send_alert", return_value={"delivered_to": [], "errors": []})
        self.send_alert = self.notify.start()

    def tearDown(self):
        self.env.stop()
        self.alerts.stop()
        self.notify.stop()
        _fallback_cache.clear()
        self._clear_usage()

    def _clear_usage(self):
        with usage._session() as db:
            db.query(AIUsage).delete()
            db.commit()

    def _rows(self):
        with usage._session() as db:
            return [(r.feature, r.provider, r.ok, r.fallback, r.input_tokens, r.output_tokens, r.learner_id)
                    for r in db.query(AIUsage).order_by(AIUsage.id).all()]

    def test_gemini_answers_and_the_call_is_recorded(self):
        reply = gateway.generate(AIRequest(feature="ask_fahim", prompt="hi", learner_id="c1"), gemini_client=_gemini())
        self.assertEqual((reply.provider, reply.text, reply.fallback), ("gemini", "مرحبا", False))
        self.assertEqual(self._rows(), [("ask_fahim", "gemini", True, False, 1000, 250, "c1")])

    def test_out_of_credits_switches_to_claude_for_ten_minutes_and_alerts(self):
        with patch("httpx.post", return_value=_claude_ok()) as post:
            reply = gateway.generate(AIRequest(feature="ask_fahim", prompt="hi"), gemini_client=_gemini(exc=OUT_OF_CREDITS))
            self.assertEqual((reply.provider, reply.text, reply.fallback), ("anthropic", "Claude reply", True))
            until = gateway.switched_until("gemini")
            self.assertIsNotNone(until)
            self.assertAlmostEqual((until - datetime.datetime.now(datetime.UTC)).total_seconds(), 600, delta=5)
            self.assertTrue(any(call.args[0] == "ai" and "anthropic for 10 minutes" in call.args[1]
                                for call in self.dispatch.call_args_list))

            # While Gemini is set aside, Claude answers first and Gemini is not called at all.
            calls = []
            reply = gateway.generate(AIRequest(feature="ask_fahim", prompt="again"), gemini_client=_gemini(calls=calls))
            self.assertEqual(reply.provider, "anthropic")
            self.assertEqual(calls, [])
            self.assertEqual(post.call_count, 2)
        rows = self._rows()
        self.assertEqual(sorted((r[1], r[2]) for r in rows), [("anthropic", True), ("anthropic", True), ("gemini", False)])

    def test_switch_happens_after_three_consecutive_failures(self):
        with patch("httpx.post", return_value=_claude_ok()):
            for attempt in range(3):
                gateway.generate(AIRequest(feature="word_meaning", prompt="x"), gemini_client=_gemini(exc=SERVER_ERROR))
                self.assertEqual(gateway.switched_until("gemini") is not None, attempt == 2)

    def test_success_resets_the_failure_count(self):
        with patch("httpx.post", return_value=_claude_ok()):
            for _ in range(2):
                gateway.generate(AIRequest(feature="word_meaning", prompt="x"), gemini_client=_gemini(exc=SERVER_ERROR))
            gateway.generate(AIRequest(feature="word_meaning", prompt="x"), gemini_client=_gemini())
            gateway.generate(AIRequest(feature="word_meaning", prompt="x"), gemini_client=_gemini(exc=SERVER_ERROR))
        self.assertIsNone(gateway.switched_until("gemini"))

    def test_a_bad_request_is_not_an_outage(self):
        with patch("httpx.post") as post, self.assertRaises(ValueError):
            gateway.generate(AIRequest(feature="lesson_drafting", prompt="x"), gemini_client=_gemini(exc=ValueError("schema rejected")))
        post.assert_not_called()

    def test_every_provider_down_raises_ai_unavailable(self):
        with patch("httpx.post", return_value=_Response(529, {"error": {"message": "Overloaded"}})):
            with self.assertRaises(AIUnavailable) as raised:
                gateway.generate(AIRequest(feature="ask_fahim", prompt="x"), gemini_client=_gemini(exc=SERVER_ERROR))
        self.assertIn("anthropic: 529 Overloaded", str(raised.exception))

    def test_without_an_anthropic_key_gemini_is_the_only_provider(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}), patch("httpx.post") as post:
            with self.assertRaises(AIUnavailable):
                gateway.generate(AIRequest(feature="ask_fahim", prompt="x"), gemini_client=_gemini(exc=OUT_OF_CREDITS))
        post.assert_not_called()

    def test_claude_request_shape(self):
        request = AIRequest(feature="lesson_drafting", prompt="Draft it", system="You write lessons.", json=True,
                            schema={"type": "OBJECT"}, temperature=0.2, max_tokens=900, tier="strong",
                            attachments=[(b"\x89PNG", "image/png")])
        with patch("httpx.post", return_value=_claude_ok('```json\n{"a": 1}\n```')) as post:
            text, model, tokens_in, tokens_out = AnthropicProvider().generate(request)
        self.assertEqual((text, tokens_in, tokens_out), ('{"a": 1}', 300, 40))
        body = post.call_args.kwargs["json"]
        self.assertEqual(body["model"], "claude-sonnet-5-5")
        self.assertEqual((body["max_tokens"], body["temperature"]), (900, 0.2))
        self.assertEqual(body["messages"][0]["content"][0]["type"], "image")
        self.assertEqual(body["messages"][0]["content"][-1], {"type": "text", "text": "Draft it"})
        self.assertIn("valid JSON object", body["system"])
        self.assertIn("school child", body["system"])
        self.assertEqual(post.call_args.kwargs["headers"]["x-api-key"], "test-key")

    def test_daily_limit_applies_to_learner_features_only(self):
        with patch.dict(os.environ, {"FAHIM_AI_DAILY_LIMIT": "2"}):
            for _ in range(2):
                gateway.generate(AIRequest(feature="ask_fahim", prompt="x", learner_id="c1"), gemini_client=_gemini())
            with self.assertRaises(AILimitReached) as raised:
                gateway.generate(AIRequest(feature="learn_with_fahim", prompt="x", learner_id="c1"), gemini_client=_gemini())
            self.assertEqual(raised.exception.reason, "daily")
            gateway.generate(AIRequest(feature="ask_fahim", prompt="x", learner_id="c2"), gemini_client=_gemini())
            gateway.generate(AIRequest(feature="lesson_drafting", prompt="x"), gemini_client=_gemini())

    def test_costs_budget_alerts_and_hard_stop(self):
        prices = json.dumps({"gemini-test": {"input": 1000, "output": 1000}})  # $1.25 per call here
        with patch.dict(os.environ, {"FAHIM_AI_PRICES": prices, "FAHIM_AI_MONTHLY_BUDGET_USD": "2",
                                     "FAHIM_AI_BUDGET_HARD_STOP": "1"}):
            first = gateway.generate(AIRequest(feature="ask_fahim", prompt="x", gemini_model="gemini-test"), gemini_client=_gemini())
            self.assertAlmostEqual(first.cost_usd, 1.25)
            self.assertEqual([c.args[1] for c in self.send_alert.call_args_list],
                             ["[JISR alert] AI spending reached 50% of the monthly budget"])
            gateway.generate(AIRequest(feature="ask_fahim", prompt="x", gemini_model="gemini-test"), gemini_client=_gemini())
            self.assertEqual(len(self.send_alert.call_args_list), 3)  # 80% and 100%, each once
            with self.assertRaises(AILimitReached) as raised:
                gateway.generate(AIRequest(feature="ask_fahim", prompt="x"), gemini_client=_gemini())
            self.assertEqual(raised.exception.reason, "budget")
            report = usage.report()
        self.assertEqual(report["calls"], 2)
        self.assertEqual(report["cost_usd"], 2.5)
        self.assertEqual(report["budget_used_pct"], 125.0)
        self.assertEqual(report["by_feature"][0]["name"], "ask_fahim")
        self.assertEqual(report["unpriced_calls"], 0)

    def test_report_counts_fallbacks_and_failures(self):
        with patch("httpx.post", return_value=_claude_ok()):
            gateway.generate(AIRequest(feature="ask_fahim", prompt="x"), gemini_client=_gemini(exc=OUT_OF_CREDITS))
        report = usage.report()
        self.assertEqual((report["calls"], report["failed_calls"], report["fallback_calls"], report["unpriced_calls"]), (2, 1, 1, 1))
        self.assertEqual({r["name"] for r in report["by_provider"]}, {"gemini", "anthropic"})
        status = {p["name"]: p for p in gateway.status()}
        self.assertTrue(status["anthropic"]["configured"])
        self.assertIsNotNone(status["gemini"]["switched_until"])


if __name__ == "__main__":
    unittest.main()
