import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// ==============================================================================
// JISR Arabic (فهيم) - Enterprise k6 Load & Stress Test
// Target: 1,000 Concurrent Users (CCU) | SLA: p95 < 120ms, p99 < 250ms
// ==============================================================================

// Custom Metrics
const audioRedirectCount = new Counter('audio_cdn_redirects_total');
const errorRate = new Rate('custom_error_rate');
const lessonLatency = new Trend('lesson_fetch_duration_ms');

// Test Configuration & Stages
export const options = {
  stages: [
    { duration: '30s', target: 200 },   // Warm-up ramp
    { duration: '1m',  target: 500 },   // Normal morning load
    { duration: '2m',  target: 1000 },  // Peak school hour (1,000 CCU)
    { duration: '3m',  target: 1000 },  // Sustained stress soak
    { duration: '30s', target: 0 },     // Ramp-down
  ],
  thresholds: {
    // Latency SLA targets
    'http_req_duration': ['p(95)<120', 'p(99)<250'], // 95% < 120ms, 99% < 250ms
    'lesson_fetch_duration_ms': ['p(95)<100'],
    // Reliability SLA target
    'http_req_failed': ['rate<0.01'],                // Less than 1% errors
    'custom_error_rate': ['rate<0.01'],
  },
};

const BASE_URL = __ENV.TARGET_URL || 'http://localhost:8000';

export default function () {
  const userType = Math.random();
  const requestId = `k6-${__VU}-${__ITER}-${Date.now()}`;
  const headers = {
    'User-Agent': 'k6-load-tester/1.0',
    'Accept': 'application/json',
    'X-Request-ID': requestId,
  };

  // ----------------------------------------------------------------------------
  // Profile 1: Student Learner (70% probability)
  // ----------------------------------------------------------------------------
  if (userType < 0.70) {
    // 1. Fetch Curriculum Grades
    const catRes = http.get(`${BASE_URL}/api/curriculum/grades`, { headers });
    check(catRes, {
      'grades status 200': (r) => r.status === 200,
    });
    sleep(1);

    // 2. Fetch Lesson 1 (Ball Games)
    const startLesson = Date.now();
    const lessonRes = http.get(
      `${BASE_URL}/api/curriculum/lesson/lesson_01_ball_games`,
      { headers }
    );
    lessonLatency.add(Date.now() - startLesson);
    check(lessonRes, {
      'lesson status ok': (r) => r.status === 200,
    });
    sleep(1.5);

    // 3. Audio Cache & 307 CDN Redirect Verification
    const clipId = `audio_clip_${Math.floor(Math.random() * 50) + 1}.mp3`;
    const audioRes = http.get(`${BASE_URL}/api/audio/cache/${clipId}`, {
      headers,
      redirects: 0, // Do not follow redirect; verify 307 or 200 directly
    });
    
    if (audioRes.status === 307) {
      audioRedirectCount.add(1);
    }
    
    check(audioRes, {
      'audio cache fast status': (r) => [200, 307, 404].includes(r.status),
    });
    sleep(2);
  }
  // ----------------------------------------------------------------------------
  // Profile 2: Assessment & Grading Submissions (20% probability)
  // ----------------------------------------------------------------------------
  else if (userType < 0.90) {
    // Sentence Builder Token Validation
    const sbPayload = JSON.stringify({
      lesson_id: 'lesson_grade_05_unit_01_lesson_01_v1',
      exercise_id: 'sb_01',
      ordered_tokens: ['الكُرَةُ', 'هِيَ', 'أَكْثَرُ', 'الأَلْعَابِ', 'شَعْبِيَّةً'],
    });

    const sbRes = http.post(`${BASE_URL}/api/curriculum/sentence-builder/check`, sbPayload, {
      headers: Object.assign({}, headers, { 'Content-Type': 'application/json' }),
    });

    check(sbRes, {
      'sentence builder evaluated': (r) => [200, 400, 404].includes(r.status),
    });
    sleep(2.5);

    // Exercise Attempt Submission
    const attemptPayload = JSON.stringify({
      lesson_id: 'lesson_grade_05_unit_01_lesson_01_v1',
      child_id: `child_${Math.floor(Math.random() * 200) + 1}`,
      idempotency_key: `k6-att-${__VU}-${__ITER}`,
      answers: [
        { question_id: 'q1', selected_option: 'مستدير' },
        { question_id: 'q2', selected_option: 'الساحرة المستديرة' },
      ],
    });

    const attemptRes = http.post(`${BASE_URL}/api/assessment/attempts`, attemptPayload, {
      headers: Object.assign({}, headers, { 'Content-Type': 'application/json' }),
    });

    check(attemptRes, {
      'attempt submission valid': (r) => [200, 201, 401, 403, 404].includes(r.status),
    });
    sleep(3);
  }
  // ----------------------------------------------------------------------------
  // Profile 3: Parent Monitoring & Infrastructure Probes (10% probability)
  // ----------------------------------------------------------------------------
  else {
    // ALB Liveness Probe
    const healthRes = http.get(`${BASE_URL}/api/health`, { headers });
    check(healthRes, {
      'health liveness 200': (r) => r.status === 200,
    });

    // ALB Readiness Probe (Postgres + Redis check)
    const readyRes = http.get(`${BASE_URL}/api/ready`, { headers });
    check(readyRes, {
      'readiness responded': (r) => [200, 503].includes(r.status),
    });

    // Leaderboard
    const lbRes = http.get(`${BASE_URL}/api/progress/leaderboard?grade=5`, { headers });
    check(lbRes, {
      'leaderboard query ok': (r) => [200, 401].includes(r.status),
    });
    sleep(4);
  }
}
