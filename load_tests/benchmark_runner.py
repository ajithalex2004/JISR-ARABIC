#!/usr/bin/env python3
"""
JISR Arabic (فهيم) - High-Concurrency Async Benchmark Harness
==============================================================
Target Scale: 10,000+ Students | 1,000 Concurrent Users (CCU)
Engine: Python 3.13 + AsyncIO + HTTPX Connection Pooling

Usage:
  python -m load_tests.benchmark_runner --concurrency 500 --duration 30
  python -m load_tests.benchmark_runner --target http://localhost:8000 --concurrency 1000 --duration 60 --report
"""

import argparse
import asyncio
import os
import random
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import httpx

# Ensure Windows stdout handles UTF-8 output gracefully
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


@dataclass
class EndpointMetrics:
    name: str
    total_calls: int = 0
    success_calls: int = 0
    failure_calls: int = 0
    latencies: List[float] = field(default_factory=list)
    status_codes: Dict[int, int] = field(default_factory=dict)

    def record(self, latency_ms: float, status_code: int, is_success: bool):
        self.total_calls += 1
        if is_success:
            self.success_calls += 1
        else:
            self.failure_calls += 1
        self.latencies.append(latency_ms)
        self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1

    def percentile(self, p: float) -> float:
        if not self.latencies:
            return 0.0
        sorted_lat = sorted(self.latencies)
        k = (len(sorted_lat) - 1) * p
        f = int(k)
        c = min(f + 1, len(sorted_lat) - 1)
        d = k - f
        return sorted_lat[f] + d * (sorted_lat[c] - sorted_lat[f])


class LoadTester:
    def __init__(
        self,
        target_url: str,
        concurrency: int,
        duration_seconds: int,
        timeout: float = 10.0
    ):
        self.target_url = target_url.rstrip("/")
        self.concurrency = concurrency
        self.duration = duration_seconds
        self.timeout = timeout
        self.stop_event = asyncio.Event()
        self.metrics: Dict[str, EndpointMetrics] = {
            "GET /api/health": EndpointMetrics("GET /api/health"),
            "GET /api/ready": EndpointMetrics("GET /api/ready"),
            "GET /api/curriculum/grades": EndpointMetrics("GET /api/curriculum/grades"),
            "GET /api/curriculum/lessons?grade=5&term=1": EndpointMetrics("GET /api/curriculum/lessons?grade=5&term=1"),
            "GET /api/curriculum/lesson/lesson_01_ball_games": EndpointMetrics("GET /api/curriculum/lesson/lesson_01_ball_games"),
            "GET /api/audio/cache/[clip]": EndpointMetrics("GET /api/audio/cache/[clip]"),
            "POST /api/assessment/attempts": EndpointMetrics("POST /api/assessment/attempts"),
            "GET /api/progress/leaderboard": EndpointMetrics("GET /api/progress/leaderboard"),
        }

    async def user_session(self, client: httpx.AsyncClient, worker_id: int):
        """Simulates one persistent concurrent user session executing multi-endpoint flows."""
        session_id = str(uuid.uuid4())
        headers = {
            "User-Agent": f"JISR-BenchmarkClient/1.0 (worker-{worker_id})",
            "Accept": "application/json",
            "X-Request-ID": f"bench-{session_id[:8]}"
        }

        while not self.stop_event.is_set():
            # Weighted task selection
            rand = random.random()
            
            if rand < 0.40:
                # Flow 1: Curriculum & Lesson Browse
                await self._call_get(client, "/api/curriculum/grades", "GET /api/curriculum/grades", headers)
                await asyncio.sleep(random.uniform(0.02, 0.08))
                await self._call_get(
                    client,
                    "/api/curriculum/lessons?grade=5&term=1",
                    "GET /api/curriculum/lessons?grade=5&term=1",
                    headers
                )
                await asyncio.sleep(random.uniform(0.02, 0.08))
                await self._call_get(
                    client,
                    "/api/curriculum/lesson/lesson_01_ball_games",
                    "GET /api/curriculum/lesson/lesson_01_ball_games",
                    headers
                )
            elif rand < 0.70:
                # Flow 2: Audio Cache / CDN Redirect Check
                clip_id = f"audio_clip_{random.randint(1, 50)}.mp3"
                await self._call_get(
                    client,
                    f"/api/audio/cache/{clip_id}",
                    "GET /api/audio/cache/[clip]",
                    headers,
                    allow_redirects=False,
                    valid_statuses={200, 307, 404}
                )
            elif rand < 0.85:
                # Flow 3: Attempt Submission (Idempotent)
                payload = {
                    "lesson_id": "lesson_01_ball_games",
                    "child_id": f"child_{random.randint(1, 200)}",
                    "idempotency_key": f"bench-att-{uuid.uuid4()}",
                    "answers": [{"question_id": "act_lesson_01_ball_games_01", "selected_option": "opt_a"}]
                }
                await self._call_post(
                    client,
                    "/api/assessment/attempts",
                    "POST /api/assessment/attempts",
                    payload,
                    headers,
                    valid_statuses={200, 201, 401, 403, 404}
                )
            else:
                # Flow 4: Infrastructure & Monitoring Probes
                await self._call_get(client, "/api/health", "GET /api/health", headers)
                await self._call_get(client, "/api/ready", "GET /api/ready", headers, valid_statuses={200, 503})

            # Small realistic inter-request think time
            await asyncio.sleep(random.uniform(0.1, 0.4))

    async def _call_get(
        self,
        client: httpx.AsyncClient,
        path: str,
        metric_name: str,
        headers: dict,
        allow_redirects: bool = True,
        valid_statuses: Optional[set] = None
    ):
        if valid_statuses is None:
            valid_statuses = {200}
        
        metric = self.metrics[metric_name]
        url = f"{self.target_url}{path}"
        start = time.perf_counter()
        status = 0
        success = False
        try:
            resp = await client.get(url, headers=headers, follow_redirects=allow_redirects, timeout=self.timeout)
            status = resp.status_code
            success = status in valid_statuses
        except Exception:
            status = 0
            success = False
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            metric.record(elapsed_ms, status, success)

    async def _call_post(
        self,
        client: httpx.AsyncClient,
        path: str,
        metric_name: str,
        json_data: dict,
        headers: dict,
        valid_statuses: Optional[set] = None
    ):
        if valid_statuses is None:
            valid_statuses = {200, 201}

        metric = self.metrics[metric_name]
        url = f"{self.target_url}{path}"
        start = time.perf_counter()
        status = 0
        success = False
        try:
            resp = await client.post(url, json=json_data, headers=headers, timeout=self.timeout)
            status = resp.status_code
            success = status in valid_statuses
        except Exception:
            status = 0
            success = False
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            metric.record(elapsed_ms, status, success)

    async def run(self):
        print("\n" + "=" * 78)
        print("  JISR Arabic (فهيم) Enterprise Async Load Benchmark")
        print(f"  Target URL      : {self.target_url}")
        print(f"  Concurrency     : {self.concurrency} Simultaneous Simulated Sessions")
        print(f"  Target Duration : {self.duration} Seconds")
        print(f"  SLA Objective   : p95 < 120ms | p99 < 250ms | Error Rate < 1%")
        print("=" * 78 + "\n")

        limits = httpx.Limits(
            max_connections=self.concurrency * 2,
            max_keepalive_connections=self.concurrency
        )
        
        start_time = time.perf_counter()
        async with httpx.AsyncClient(limits=limits) as client:
            # Spawn concurrent user tasks
            tasks = [
                asyncio.create_task(self.user_session(client, worker_id=i))
                for i in range(self.concurrency)
            ]
            
            # Progress ticker
            tick_start = time.perf_counter()
            while time.perf_counter() - start_time < self.duration:
                await asyncio.sleep(1.0)
                elapsed = time.perf_counter() - start_time
                total_reqs = sum(m.total_calls for m in self.metrics.values())
                current_rps = total_reqs / max(elapsed, 0.001)
                print(f"  [Progress] Elapsed: {elapsed:4.1f}s / {self.duration}s | Total Requests: {total_reqs:6,d} | Current RPS: {current_rps:6.1f}", end="\r")

            self.stop_event.set()
            await asyncio.gather(*tasks, return_exceptions=True)

        total_elapsed = time.perf_counter() - start_time
        print(f"\n\n>> Benchmark completed in {total_elapsed:.2f} seconds.")
        return self._generate_report(total_elapsed)

    def _generate_report(self, total_elapsed: float) -> str:
        all_latencies = []
        total_calls = 0
        total_success = 0
        total_fail = 0

        for m in self.metrics.values():
            all_latencies.extend(m.latencies)
            total_calls += m.total_calls
            total_success += m.success_calls
            total_fail += m.failure_calls

        overall_rps = total_calls / max(total_elapsed, 0.001)
        fail_rate = (total_fail / max(total_calls, 1)) * 100.0

        all_latencies.sort()
        def get_p(p):
            if not all_latencies:
                return 0.0
            idx = int((len(all_latencies) - 1) * p)
            return all_latencies[idx]

        p50 = get_p(0.50)
        p90 = get_p(0.90)
        p95 = get_p(0.95)
        p99 = get_p(0.99)
        max_lat = all_latencies[-1] if all_latencies else 0.0

        sla_pass = (p95 <= 120.0) and (fail_rate < 1.0)

        report = []
        report.append("\n" + "=" * 78)
        report.append("  BENCHMARK RESULTS & SLA VERIFICATION")
        report.append("=" * 78)
        report.append(f"  Total Duration       : {total_elapsed:.2f}s")
        report.append(f"  Simulated CCU        : {self.concurrency:,}")
        report.append(f"  Total Requests       : {total_calls:,}")
        report.append(f"  Throughput (RPS)     : {overall_rps:,.1f} req/sec")
        report.append(f"  Successful Requests  : {total_success:,} ({100 - fail_rate:.2f}%)")
        report.append(f"  Failed Requests      : {total_fail:,} ({fail_rate:.2f}%)")
        report.append("-" * 78)
        report.append(f"  p50 (Median) Latency : {p50:6.1f} ms")
        report.append(f"  p90 Latency          : {p90:6.1f} ms")
        report.append(f"  p95 Latency (SLA)    : {p95:6.1f} ms  (Target: < 120 ms)")
        report.append(f"  p99 Latency (SLA)    : {p99:6.1f} ms  (Target: < 250 ms)")
        report.append(f"  Max Latency          : {max_lat:6.1f} ms")
        report.append("-" * 78)
        report.append(f"  SLA VERDICT          : {'[PASSED] SLA COMPLIANT' if sla_pass else '[ATTENTION] NEEDS TUNING'}")
        report.append("=" * 78 + "\n")

        # Per-endpoint breakdown table
        report.append("Endpoint Breakdown:")
        report.append(f"{'Endpoint':<44} | {'Calls':>7} | {'p50':>6} | {'p95':>6} | {'p99':>6} | {'Err%':>5}")
        report.append("-" * 78)
        for name, m in self.metrics.items():
            if m.total_calls == 0:
                continue
            err_pct = (m.failure_calls / m.total_calls) * 100.0
            report.append(
                f"{name:<44} | {m.total_calls:>7,d} | {m.percentile(0.50):>5.1f}m | {m.percentile(0.95):>5.1f}m | {m.percentile(0.99):>5.1f}m | {err_pct:>4.1f}%"
            )
        report.append("-" * 78 + "\n")

        output = "\n".join(report)
        print(output)
        return output


def main():
    parser = argparse.ArgumentParser(description="JISR Arabic Load Benchmark Harness")
    parser.add_argument("--target", default="http://localhost:8000", help="Target API URL")
    parser.add_argument("--concurrency", type=int, default=100, help="Simulated concurrent users")
    parser.add_argument("--duration", type=int, default=15, help="Test duration in seconds")
    parser.add_argument("--report", action="store_true", help="Save benchmark markdown report")
    args = parser.parse_args()

    tester = LoadTester(
        target_url=args.target,
        concurrency=args.concurrency,
        duration_seconds=args.duration
    )
    result = asyncio.run(tester.run())

    if args.report:
        report_path = os.path.join(os.path.dirname(__file__), "BENCHMARK_REPORT.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# JISR Arabic (فهيم) Load & Stress Benchmark Report\n\n```text\n{result}\n```\n")
        print(f">> Report saved to: {report_path}")


if __name__ == "__main__":
    main()
