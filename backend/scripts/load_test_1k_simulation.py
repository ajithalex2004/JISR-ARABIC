"""
Production Load & Concurrency Stress Testing Suite for JISR Arabic.
Simulates 100–200 concurrent school learners, parents, and school administrators
representing peak school hours traffic for 1,000 registered students.
Measures latency (p50, p95, p99), throughput (RPS), connection pool saturation,
cache hit behavior, and background task queue stability.
"""
import sys
import os
import time
import math
import random
import asyncio
import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional

import httpx

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.database import SessionLocal
from backend.models import User, ChildProfile, School, SchoolClass, UserSession
from backend.security import create_access_token, decode_access_token


class MetricsCollector:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.latencies: List[float] = []
        self.endpoint_latencies: Dict[str, List[float]] = defaultdict(list)
        self.status_codes: Counter = Counter()
        self.errors: List[str] = []
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    async def record(self, endpoint: str, status_code: int, duration_ms: float, error: Optional[str] = None):
        async with self.lock:
            self.latencies.append(duration_ms)
            self.endpoint_latencies[endpoint].append(duration_ms)
            self.status_codes[status_code] += 1
            if error:
                self.errors.append(f"{endpoint}: {error}")

    def percentile(self, data: List[float], p: float) -> float:
        if not data:
            return 0.0
        k = (len(data) - 1) * (p / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return data[int(k)]
        d0 = data[int(f)] * (c - k)
        d1 = data[int(c)] * (k - f)
        return d0 + d1

    def summary(self) -> Dict[str, Any]:
        total_reqs = len(self.latencies)
        duration = max(0.001, self.end_time - self.start_time)
        rps = total_reqs / duration
        sorted_latencies = sorted(self.latencies)

        endpoint_stats = {}
        for ep, lat_list in sorted(self.endpoint_latencies.items()):
            s_lat = sorted(lat_list)
            endpoint_stats[ep] = {
                "count": len(lat_list),
                "avg_ms": round(sum(lat_list) / len(lat_list), 2) if lat_list else 0,
                "p50_ms": round(self.percentile(s_lat, 50), 2),
                "p95_ms": round(self.percentile(s_lat, 95), 2),
                "p99_ms": round(self.percentile(s_lat, 99), 2),
                "max_ms": round(max(lat_list), 2) if lat_list else 0,
            }

        success_count = sum(count for code, count in self.status_codes.items() if 200 <= code < 400)
        success_rate = (success_count / total_reqs * 100.0) if total_reqs > 0 else 0.0

        return {
            "total_requests": total_reqs,
            "duration_seconds": round(duration, 2),
            "requests_per_second": round(rps, 1),
            "success_rate_pct": round(success_rate, 2),
            "status_codes": dict(self.status_codes),
            "overall_latency": {
                "min_ms": round(min(self.latencies), 2) if self.latencies else 0,
                "avg_ms": round(sum(self.latencies) / total_reqs, 2) if total_reqs else 0,
                "p50_ms": round(self.percentile(sorted_latencies, 50), 2),
                "p90_ms": round(self.percentile(sorted_latencies, 90), 2),
                "p95_ms": round(self.percentile(sorted_latencies, 95), 2),
                "p99_ms": round(self.percentile(sorted_latencies, 99), 2),
                "max_ms": round(max(self.latencies), 2) if self.latencies else 0,
            },
            "endpoint_stats": endpoint_stats,
            "error_sample": self.errors[:5],
        }


def prepare_auth_tokens(base_url: str) -> Dict[str, Any]:
    """Pre-generates active sessions for learners, parents, tutors, and admins."""
    print("Preparing authentication sessions in database for load test...")
    with SessionLocal() as db:
        admin_user = db.query(User).filter(User.role == "admin").first()
        parent_user = db.query(User).filter(User.role == "parent").first()
        tutor_user = db.query(User).filter(User.role == "tutor").first()
        children = db.query(ChildProfile).all()

        if not admin_user or not parent_user or not children:
            raise RuntimeError("Database missing required seed users/children for load test")

        tokens = {"admin": None, "tutor": None, "parents": [], "learners": []}

        # Admin token
        t_admin = create_access_token({"sub": admin_user.id, "role": "admin"})
        p_admin = decode_access_token(t_admin)
        db.add(UserSession(
            id=p_admin["jti"],
            user_id=admin_user.id,
            expires_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(days=1)
        ))
        tokens["admin"] = t_admin

        # Tutor token
        if tutor_user:
            t_tutor = create_access_token({"sub": tutor_user.id, "role": "tutor", "school_id": "sunrise_abu_dhabi"})
            p_tutor = decode_access_token(t_tutor)
            db.add(UserSession(
                id=p_tutor["jti"],
                user_id=tutor_user.id,
                expires_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(days=1)
            ))
            tokens["tutor"] = t_tutor

        # Parent token - select child belonging to this parent for access control alignment
        parent_child = db.query(ChildProfile).filter(ChildProfile.parent_id == parent_user.id).first()
        if not parent_child:
            parent_child = children[0]
            parent_user = db.query(User).filter(User.id == parent_child.parent_id).first()

        t_parent = create_access_token({"sub": parent_user.id, "role": "parent"})
        p_parent = decode_access_token(t_parent)
        db.add(UserSession(
            id=p_parent["jti"],
            user_id=parent_user.id,
            expires_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(days=1)
        ))
        tokens["parents"].append({"token": t_parent, "user_id": parent_user.id, "child_id": parent_child.id})

        # Learner tokens (representing active students in school classrooms)
        for child in children[:15]:
            t_child = create_access_token({
                "sub": child.parent_id,
                "role": "learner",
                "child_id": child.id,
                "session_kind": "learner"
            })
            p_child = decode_access_token(t_child)
            db.add(UserSession(
                id=p_child["jti"],
                user_id=child.parent_id,
                expires_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(days=1)
            ))
            tokens["learners"].append({"token": t_child, "child_id": child.id})

        db.commit()
        print(f"Generated sessions: 1 admin, 1 tutor, 1 parent, {len(tokens['learners'])} learners")
        return tokens


async def get_telemetry(client: httpx.AsyncClient) -> Dict[str, Any]:
    """Fetches real-time database pool and task queue telemetry."""
    try:
        res = await client.get("/api/health", timeout=5.0)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {}


async def student_learner_workflow(
    user_id: int,
    client: httpx.AsyncClient,
    learner_info: Dict[str, str],
    stop_event: asyncio.Event,
    collector: MetricsCollector
):
    """Simulates an active student working through lessons, audio, and exercises."""
    headers = {"Authorization": f"Bearer {learner_info['token']}"}
    child_id = learner_info["child_id"]

    actions = [
        ("GET", "/api/curriculum/diagnostic-questions", None),
        ("GET", "/api/curriculum/lessons?grade=5&term=1", None),
        ("GET", "/api/curriculum/lesson/lesson_01_ball_games", None),
        ("GET", "/api/modules/capsules/capsule_01_taa_marbutah", None),
        ("POST", "/api/audio/evaluate-speech", {
            "target_phrase": "أَلْعَابُ الْكُرَةِ",
            "spoken_text": "أَلْعَابُ الْكُرَةِ",
            "child_id": child_id
        }),
        ("POST", "/api/audio/synthesize-async", {
            "text": "كرة السلة رياضة ممتعة",
            "speed": 1.0,
            "lang": "ar-SA"
        }),
    ]

    # Stagger initial session arrival
    await asyncio.sleep(random.uniform(0.05, 1.2))

    while not stop_event.is_set():
        method, path, body = random.choice(actions)
        t0 = time.perf_counter()
        try:
            if method == "GET":
                resp = await client.get(path, headers=headers)
            else:
                resp = await client.post(path, headers=headers, json=body)
            duration_ms = (time.perf_counter() - t0) * 1000.0
            await collector.record(f"{method} {path.split('?')[0]}", resp.status_code, duration_ms)
        except Exception as e:
            duration_ms = (time.perf_counter() - t0) * 1000.0
            await collector.record(f"{method} {path.split('?')[0]}", 599, duration_ms, error=str(e))

        # Realistic student think time (reading, audio listening, solving questions): 1.2s - 3.0s
        await asyncio.sleep(random.uniform(1.2, 3.0))


async def parent_workflow(
    user_id: int,
    client: httpx.AsyncClient,
    parent_info: Dict[str, str],
    stop_event: asyncio.Event,
    collector: MetricsCollector
):
    """Simulates a parent reviewing dashboards, progress reports, and guidance."""
    headers = {"Authorization": f"Bearer {parent_info['token']}"}
    child_id = parent_info["child_id"]

    actions = [
        ("GET", f"/api/parent/dashboard/{child_id}"),
        ("GET", f"/api/parent/weekly-digest/{child_id}"),
        ("GET", f"/api/parent/actionable-guidance/{child_id}"),
    ]

    await asyncio.sleep(random.uniform(0.1, 1.5))

    while not stop_event.is_set():
        method, path = random.choice(actions)
        t0 = time.perf_counter()
        try:
            resp = await client.get(path, headers=headers)
            duration_ms = (time.perf_counter() - t0) * 1000.0
            clean_path = "/".join(path.split("/")[:4]) + "/{child_id}"
            await collector.record(f"{method} {clean_path}", resp.status_code, duration_ms)
        except Exception as e:
            duration_ms = (time.perf_counter() - t0) * 1000.0
            clean_path = "/".join(path.split("/")[:4]) + "/{child_id}"
            await collector.record(f"{method} {clean_path}", 599, duration_ms, error=str(e))

        # Realistic parent think time (reading analytics, digesting guidance): 2.0s - 4.0s
        await asyncio.sleep(random.uniform(2.0, 4.0))


async def staff_workflow(
    user_id: int,
    client: httpx.AsyncClient,
    auth_tokens: Dict[str, Any],
    stop_event: asyncio.Event,
    collector: MetricsCollector
):
    """Simulates school teachers and administrators managing classes and rosters."""
    admin_headers = {"Authorization": f"Bearer {auth_tokens['admin']}"}
    tutor_headers = {"Authorization": f"Bearer {auth_tokens['tutor']}"} if auth_tokens.get("tutor") else admin_headers

    actions = [
        ("GET", "/api/curriculum/schools", admin_headers),
        ("GET", "/api/curriculum/schools/sunrise_abu_dhabi/classes", admin_headers),
        ("GET", "/api/tutor/queue", tutor_headers),
        ("GET", "/api/tasks?limit=10", admin_headers),
    ]

    await asyncio.sleep(random.uniform(0.1, 1.5))

    while not stop_event.is_set():
        method, path, headers = random.choice(actions)
        t0 = time.perf_counter()
        try:
            resp = await client.get(path, headers=headers)
            duration_ms = (time.perf_counter() - t0) * 1000.0
            await collector.record(f"{method} {path.split('?')[0]}", resp.status_code, duration_ms)
        except Exception as e:
            duration_ms = (time.perf_counter() - t0) * 1000.0
            await collector.record(f"{method} {path.split('?')[0]}", 599, duration_ms, error=str(e))

        # Realistic staff think time (grading, reviewing class queue): 1.5s - 3.5s
        await asyncio.sleep(random.uniform(1.5, 3.5))


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


async def run_load_phase(
    phase_name: str,
    target_concurrency: int,
    duration_seconds: int,
    base_url: str,
    auth_tokens: Dict[str, Any]
) -> Dict[str, Any]:
    """Executes a distinct load test phase with target concurrency and duration."""
    print(f"\n{'='*70}")
    print(f">> STARTING {phase_name.upper()}: {target_concurrency} Concurrent Users for {duration_seconds}s")
    print(f"{'='*70}")

    limits = httpx.Limits(max_keepalive_connections=target_concurrency + 50, max_connections=target_concurrency + 100)
    async with httpx.AsyncClient(base_url=base_url, limits=limits, timeout=30.0) as client:
        # Pre-test telemetry
        initial_telemetry = await get_telemetry(client)
        print(f"Initial Pool: {initial_telemetry.get('pool', {})}")
        print(f"Initial Tasks: {initial_telemetry.get('tasks', {})}")

        collector = MetricsCollector()
        stop_event = asyncio.Event()

        # Allocate user roles: ~70% learners, ~15% parents, ~15% staff
        learner_count = int(target_concurrency * 0.70)
        parent_count = int(target_concurrency * 0.15)
        staff_count = max(1, target_concurrency - learner_count - parent_count)

        learners_pool = auth_tokens["learners"]
        parent_info = auth_tokens["parents"][0]

        tasks = []
        collector.start_time = time.perf_counter()

        # Spawn learners
        for i in range(learner_count):
            l_info = learners_pool[i % len(learners_pool)]
            tasks.append(asyncio.create_task(student_learner_workflow(i, client, l_info, stop_event, collector)))

        # Spawn parents
        for i in range(parent_count):
            tasks.append(asyncio.create_task(parent_workflow(i, client, parent_info, stop_event, collector)))

        # Spawn staff
        for i in range(staff_count):
            tasks.append(asyncio.create_task(staff_workflow(i, client, auth_tokens, stop_event, collector)))

        print(f"Spawned {len(tasks)} concurrent tasks ({learner_count} students, {parent_count} parents, {staff_count} staff). Running for {duration_seconds}s...")

        # Sample telemetry mid-run
        await asyncio.sleep(duration_seconds / 2.0)
        mid_telemetry = await get_telemetry(client)
        print(f"Mid-Run Pool Saturation: {mid_telemetry.get('pool', {})}")

        # Finish remaining duration
        await asyncio.sleep(duration_seconds / 2.0)

        # Stop workers
        stop_event.set()
        collector.end_time = time.perf_counter()
        await asyncio.gather(*tasks, return_exceptions=True)

        # Post-test telemetry
        final_telemetry = await get_telemetry(client)
        print(f"Cooldown Pool: {final_telemetry.get('pool', {})}")

        stats = collector.summary()
        stats["phase_name"] = phase_name
        stats["target_concurrency"] = target_concurrency
        stats["initial_pool"] = initial_telemetry.get("pool", {})
        stats["mid_pool"] = mid_telemetry.get("pool", {})
        stats["final_pool"] = final_telemetry.get("pool", {})
        return stats


def print_phase_report(stats: Dict[str, Any]):
    """Pretty prints a structured Markdown table report for a phase."""
    print(f"\n[PHASE REPORT] {stats['phase_name']} ({stats['target_concurrency']} Concurrent Users)")
    print(f"Total Requests: {stats['total_requests']} | Duration: {stats['duration_seconds']}s | Throughput: {stats['requests_per_second']} req/sec")
    print(f"Success Rate: {stats['success_rate_pct']}% | Status Codes: {stats['status_codes']}")
    
    lat = stats["overall_latency"]
    print(f"Latency: Avg={lat['avg_ms']}ms | p50={lat['p50_ms']}ms | p90={lat['p90_ms']}ms | p95={lat['p95_ms']}ms | p99={lat['p99_ms']}ms | Max={lat['max_ms']}ms")
    
    print("\nEndpoint Breakdown:")
    print(f"{'Endpoint':<45} | {'Count':<6} | {'Avg(ms)':<8} | {'p50(ms)':<8} | {'p95(ms)':<8} | {'p99(ms)':<8}")
    print("-" * 95)
    for ep, data in stats["endpoint_stats"].items():
        print(f"{ep:<45} | {data['count']:<6} | {data['avg_ms']:<8} | {data['p50_ms']:<8} | {data['p95_ms']:<8} | {data['p99_ms']:<8}")
    print("-" * 95)


async def main():
    base_url = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")
    print(f"JISR Arabic Load Testing Engine target: {base_url}")

    # Verify server is reachable
    async with httpx.AsyncClient(base_url=base_url) as client:
        try:
            health = await client.get("/api/health", timeout=5.0)
            if health.status_code != 200:
                print(f"Error: Target {base_url} returned {health.status_code}")
                sys.exit(1)
            print("Target is healthy and responsive.")
        except Exception as e:
            print(f"Cannot connect to {base_url}: {e}")
            sys.exit(1)

    auth_tokens = prepare_auth_tokens(base_url)

    # 1. Warmup Phase: 20 users for 10 seconds
    warmup_stats = await run_load_phase("Phase 1: Warmup", target_concurrency=20, duration_seconds=10, base_url=base_url, auth_tokens=auth_tokens)
    print_phase_report(warmup_stats)

    # 2. Target Peak Load: 150 concurrent users for 25 seconds
    peak_stats = await run_load_phase("Phase 2: Target Peak Load", target_concurrency=150, duration_seconds=25, base_url=base_url, auth_tokens=auth_tokens)
    print_phase_report(peak_stats)

    # 3. Upper-Bound Spike Load: 200 concurrent users for 20 seconds
    spike_stats = await run_load_phase("Phase 3: Spike / Stress Test", target_concurrency=200, duration_seconds=20, base_url=base_url, auth_tokens=auth_tokens)
    print_phase_report(spike_stats)

    print("\n" + "="*70)
    print("[COMPLETED] ALL LOAD TEST PHASES COMPLETED SUCCESSFULLY.")
    print("="*70)



if __name__ == "__main__":
    asyncio.run(main())
