# JISR Arabic (فهيم) Load & Stress Benchmark Report

```text

==============================================================================
  BENCHMARK RESULTS & SLA VERIFICATION
==============================================================================
  Total Duration       : 15.94s
  Simulated CCU        : 100
  Total Requests       : 598
  Throughput (RPS)     : 37.5 req/sec
  Successful Requests  : 597 (99.83%)
  Failed Requests      : 1 (0.17%)
------------------------------------------------------------------------------
  p50 (Median) Latency : 1276.2 ms
  p90 Latency          : 4077.2 ms
  p95 Latency (SLA)    : 5324.0 ms  (Target: < 120 ms)
  p99 Latency (SLA)    : 6310.3 ms  (Target: < 250 ms)
  Max Latency          : 7560.0 ms
------------------------------------------------------------------------------
  SLA VERDICT          : [ATTENTION] NEEDS TUNING
==============================================================================

Endpoint Breakdown:
Endpoint                                     |   Calls |    p50 |    p95 |    p99 |  Err%
------------------------------------------------------------------------------
GET /api/health                              |      50 | 2393.4m | 3568.8m | 5586.0m |  0.0%
GET /api/ready                               |      50 | 3197.6m | 7016.8m | 7494.2m |  0.0%
GET /api/curriculum/grades                   |     119 | 650.7m | 5365.9m | 5797.4m |  0.0%
GET /api/curriculum/lessons?grade=5&term=1   |     119 | 532.8m | 5407.4m | 5659.5m |  0.0%
GET /api/curriculum/lesson/lesson_01_ball_games |     119 | 2464.2m | 4479.8m | 5755.2m |  0.0%
GET /api/audio/cache/[clip]                  |      89 | 665.8m | 4807.6m | 5475.8m |  1.1%
POST /api/assessment/attempts                |      52 | 410.3m | 5148.3m | 5580.1m |  0.0%
------------------------------------------------------------------------------

```
