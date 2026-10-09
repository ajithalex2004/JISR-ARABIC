"""
Unit and integration tests for JISR Arabic load testing harness and configuration.
"""

import ast
import os
import unittest
from load_tests.benchmark_runner import EndpointMetrics, LoadTester


class TestLoadTestingHarness(unittest.TestCase):
    def test_endpoint_metrics_percentile_calculation(self):
        """EndpointMetrics accurately calculates percentiles (p50, p95, p99)."""
        m = EndpointMetrics("GET /api/test")
        # Add 100 sample latencies: 1ms to 100ms
        for i in range(1, 101):
            m.record(latency_ms=float(i), status_code=200, is_success=True)

        self.assertEqual(m.total_calls, 100)
        self.assertEqual(m.success_calls, 100)
        self.assertEqual(m.failure_calls, 0)
        
        # Verify percentiles
        self.assertAlmostEqual(m.percentile(0.50), 50.5, delta=1.0)
        self.assertAlmostEqual(m.percentile(0.95), 95.05, delta=1.0)
        self.assertAlmostEqual(m.percentile(0.99), 99.01, delta=1.0)

    def test_load_tester_initialization_and_report_generation(self):
        """LoadTester configures concurrency, endpoints, and generates SLA reports."""
        tester = LoadTester(target_url="http://127.0.0.1:8000", concurrency=50, duration_seconds=5)
        self.assertEqual(tester.concurrency, 50)
        self.assertEqual(tester.duration, 5)
        self.assertIn("GET /api/health", tester.metrics)
        self.assertIn("GET /api/curriculum/grades", tester.metrics)
        self.assertIn("POST /api/assessment/attempts", tester.metrics)

        # Simulate metrics and verify report formatting
        tester.metrics["GET /api/health"].record(latency_ms=12.5, status_code=200, is_success=True)
        report = tester._generate_report(total_elapsed=1.0)
        self.assertIn("BENCHMARK RESULTS & SLA VERIFICATION", report)
        self.assertIn("Simulated CCU        : 50", report)
        self.assertIn("GET /api/health", report)

    def test_locustfile_and_k6_structure_integrity(self):
        """Verify that locustfile.py and k6_load_test.js contain valid targets and weights."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        locust_path = os.path.join(base_dir, "load_tests", "locustfile.py")
        k6_path = os.path.join(base_dir, "load_tests", "k6_load_test.js")

        self.assertTrue(os.path.exists(locust_path))
        self.assertTrue(os.path.exists(k6_path))

        # Check Python syntax of locustfile.py without invoking gevent
        with open(locust_path, "r", encoding="utf-8") as f:
            locust_content = f.read()
            tree = ast.parse(locust_content)
            self.assertIsNotNone(tree)
            self.assertIn("class StudentUser", locust_content)
            self.assertIn("weight = 70", locust_content)
            self.assertIn("class AssessmentUser", locust_content)
            self.assertIn("weight = 20", locust_content)
            self.assertIn("class ParentAndAdminUser", locust_content)
            self.assertIn("weight = 10", locust_content)

        # Check k6 script targets
        with open(k6_path, "r", encoding="utf-8") as f:
            k6_content = f.read()
            self.assertIn("target: 1000", k6_content)
            self.assertIn("'http_req_duration': ['p(95)<120', 'p(99)<250']", k6_content)
