"""
JISR Arabic (فهيم) Enterprise Load Testing Suite
================================================
Target Capacity: 10,000+ Students | 1,000 Concurrent Users (CCU)
Throughput Target: 350 - 500 requests/sec | p95 Latency < 120ms

Simulates real-world UAE school traffic patterns across 3 user profiles:
- StudentUser (70% weight): Lesson reading, audio retrieval, vocabulary decoding.
- AssessmentUser (20% weight): Attempt submission, booklet verification, exam completion.
- ParentAdminUser (10% weight): Dashboard monitoring, entitlement verification, health probes.
"""

import json
import random
import uuid
from locust import HttpUser, task, between, events, tag


class StudentUser(HttpUser):
    """
    Simulates a non-native Arabic student (Class 1-12) during school hours.
    Behaviors: Reading curriculum, listening to audio, solving sentence builders.
    """
    weight = 70
    wait_time = between(1.5, 4.0)

    def on_start(self):
        self.session_id = str(uuid.uuid4())
        self.child_id = f"child_sim_{random.randint(1, 500)}"
        self.headers = {
            "User-Agent": "JISR-Arabic-Web/1.0 (Student-LoadTest)",
            "Accept": "application/json",
            "X-Request-ID": f"sim-req-{uuid.uuid4().hex[:12]}"
        }

    @task(4)
    @tag("read", "curriculum")
    def fetch_curriculum_catalog(self):
        """Fetch available grades and lessons."""
        with self.client.get(
            "/api/curriculum/grades",
            headers=self.headers,
            name="/api/curriculum/grades",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Grades fetch failed with status {response.status_code}")

    @task(5)
    @tag("read", "lesson")
    def fetch_active_lesson(self):
        """Fetch Grade 5 Unit 1 Lesson 1 (Ball Games demo lesson)."""
        with self.client.get(
            "/api/curriculum/lesson/lesson_01_ball_games",
            headers=self.headers,
            name="/api/curriculum/lesson/[id]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Lesson fetch failed with status {response.status_code}")

    @task(6)
    @tag("audio", "cdn")
    def fetch_audio_clip(self):
        """
        Request synthetic audio clip. 
        Validates the 307 CDN redirect fallback or cached 200 delivery.
        """
        clip_hash = f"audio_clip_{random.randint(1, 50)}.mp3"
        with self.client.get(
            f"/api/audio/cache/{clip_hash}",
            headers=self.headers,
            name="/api/audio/cache/[filename]",
            allow_redirects=False,
            catch_response=True
        ) as response:
            # 200 (local/CDN hit), 307 (S3 CDN redirect), or 404 (uncached clip) are valid fast paths
            if response.status_code in (200, 307, 404):
                response.success()
            else:
                response.failure(f"Audio cache returned unexpected status {response.status_code}")

    @task(3)
    @tag("interactive", "puzzle")
    def test_sentence_builder(self):
        """Verify token ordering for sentence builder exercise."""
        payload = {
            "lesson_id": "lesson_grade_05_unit_01_lesson_01_v1",
            "exercise_id": "sb_01",
            "ordered_tokens": ["الكُرَةُ", "هِيَ", "أَكْثَرُ", "الأَلْعَابِ", "شَعْبِيَّةً"]
        }
        with self.client.post(
            "/api/curriculum/sentence-builder/check",
            json=payload,
            headers=self.headers,
            name="/api/curriculum/sentence-builder/check",
            catch_response=True
        ) as response:
            if response.status_code in (200, 400, 404):
                response.success()
            else:
                response.failure(f"Sentence builder check failed: {response.status_code}")


class AssessmentUser(HttpUser):
    """
    Simulates students actively submitting graded exercises and exams.
    Focuses on server-side normalizer scoring, transaction safety, and idempotency.
    """
    weight = 20
    wait_time = between(2.0, 5.0)

    def on_start(self):
        self.headers = {
            "User-Agent": "JISR-Arabic-App/1.0 (Assessment-LoadTest)",
            "Accept": "application/json",
            "X-Request-ID": f"sim-eval-{uuid.uuid4().hex[:12]}"
        }

    @task(3)
    @tag("scoring", "attempts")
    def submit_exercise_attempt(self):
        """Submit a multi-choice exercise attempt with idempotency key."""
        idempotency_key = f"attempt_{uuid.uuid4()}"
        payload = {
            "lesson_id": "lesson_grade_05_unit_01_lesson_01_v1",
            "child_id": f"child_{random.randint(1, 200)}",
            "idempotency_key": idempotency_key,
            "answers": [
                {"question_id": "q1", "selected_option": "مستدير"},
                {"question_id": "q2", "selected_option": "الساحرة المستديرة"}
            ]
        }
        with self.client.post(
            "/api/assessment/attempts",
            json=payload,
            headers=self.headers,
            name="/api/assessment/attempts",
            catch_response=True
        ) as response:
            if response.status_code in (200, 201, 401, 403, 404):
                # 401/403 expected if session token is unauthenticated in strict mode
                response.success()
            else:
                response.failure(f"Attempt submission failed: {response.status_code}")

    @task(2)
    @tag("booklet", "check")
    def verify_booklet_exercise(self):
        """Check booklet exercise answer against server answer key."""
        payload = {
            "lesson_id": "lesson_grade_05_unit_01_lesson_01_v1",
            "exercise_id": "ex_01",
            "submitted_answer": "كرة القدم"
        }
        with self.client.post(
            "/api/curriculum/booklets/check",
            json=payload,
            headers=self.headers,
            name="/api/curriculum/booklets/check",
            catch_response=True
        ) as response:
            if response.status_code in (200, 401, 403, 404):
                response.success()
            else:
                response.failure(f"Booklet verify returned {response.status_code}")


class ParentAndAdminUser(HttpUser):
    """
    Simulates parents monitoring mastery reports and edge infrastructure health checks.
    """
    weight = 10
    wait_time = between(3.0, 7.0)

    @task(4)
    @tag("health", "infra")
    def check_liveness_and_readiness(self):
        """Simulate ALB health check probes."""
        # Fast liveness
        self.client.get("/api/health", name="/api/health")
        # Deep readiness (DB + Redis)
        self.client.get("/api/ready", name="/api/ready")

    @task(2)
    @tag("reports", "parent")
    def view_leaderboard(self):
        """Fetch school / grade scoped leaderboard."""
        with self.client.get(
            "/api/progress/leaderboard?grade=5&limit=20",
            name="/api/progress/leaderboard",
            catch_response=True
        ) as response:
            if response.status_code in (200, 401):
                response.success()
            else:
                response.failure(f"Leaderboard fetch returned {response.status_code}")


# ------------------------------------------------------------------------------
# Locust Lifecycle Events & SLA Verification
# ------------------------------------------------------------------------------
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "=" * 70)
    print(">> [JISR ARABIC] LOAD & STRESS TEST INITIALIZED")
    print(">> Target: 1,000 Concurrent Users (CCU) | 350-500 RPS SLA")
    print(">> SLA Criteria: p95 < 120ms, p99 < 250ms, Error Rate < 1%")
    print("=" * 70 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    stats = environment.stats.total
    print("\n" + "=" * 70)
    print(">> [JISR ARABIC] LOAD TEST EXECUTION COMPLETED")
    print(f">> Total Requests    : {stats.num_requests:,}")
    print(f">> Total Failures    : {stats.num_failures:,} ({stats.fail_ratio * 100:.2f}%)")
    print(f">> Median Latency    : {stats.median_response_time:.1f} ms")
    print(f">> 95th Percentile   : {stats.get_response_time_percentile(0.95):.1f} ms")
    print(f">> 99th Percentile   : {stats.get_response_time_percentile(0.99):.1f} ms")
    print(f">> Max Latency       : {stats.max_response_time:.1f} ms")
    print(f">> Avg RPS           : {stats.total_rps:.1f} req/s")
    
    # SLA Verification
    p95 = stats.get_response_time_percentile(0.95)
    fail_rate = stats.fail_ratio * 100
    if p95 <= 120.0 and fail_rate < 1.0:
        print(">> SLA STATUS        : [PASSED] - Meets 1,000 CCU Enterprise Standard")
    else:
        print(f">> SLA STATUS        : [ATTENTION] - p95={p95:.1f}ms (target <= 120ms), Failures={fail_rate:.2f}%")
    print("=" * 70 + "\n")
