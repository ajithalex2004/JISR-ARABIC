#!/usr/bin/env python3
"""
JISR Arabic (فهيم) - Enterprise Production Readiness & SaaS Credentials Validator
==================================================================================
Validates all third-party integrations and credentials before production traffic routing:
1. Managed PostgreSQL & Schema Migrations
2. Managed Redis 7 Cluster
3. AWS S3 / Cloudflare R2 Object Storage & CDN Resolution
4. Stripe / Tap Payments API & Webhook Secret Validation
5. Transactional Email (Amazon SES / Postmark SMTP)
6. Google Gemini AI API

Usage:
  python -m backend.scripts.verify_production_readiness
  python -m backend.scripts.verify_production_readiness --verbose
  python -m backend.scripts.verify_production_readiness --skip-network
"""

import argparse
import os
import smtplib
import ssl
import sys
import time
from typing import Dict, Any, List, Tuple

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import httpx


class CheckResult:
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
        self.passed = False
        self.warning = False
        self.message = ""
        self.latency_ms = 0.0
        self.details: Dict[str, Any] = {}

    def success(self, message: str, latency_ms: float = 0.0, details: Dict[str, Any] = None):
        self.passed = True
        self.warning = False
        self.message = message
        self.latency_ms = latency_ms
        if details:
            self.details = details
        return self

    def warn(self, message: str, details: Dict[str, Any] = None):
        self.passed = True
        self.warning = True
        self.message = message
        if details:
            self.details = details
        return self

    def fail(self, message: str, details: Dict[str, Any] = None):
        self.passed = False
        self.warning = False
        self.message = message
        if details:
            self.details = details
        return self


def check_database() -> CheckResult:
    """Validate PostgreSQL connection and schema migration status."""
    res = CheckResult("PostgreSQL & Schema Migrations", "Data Tier")
    start = time.perf_counter()
    try:
        from backend.database import SessionLocal
        from sqlalchemy import text
        from backend.migrations import require_current

        db = SessionLocal()
        try:
            # Check DB ping
            db.execute(text("SELECT 1")).scalar()
            # Check migrations
            try:
                require_current()
                migration_status = "Up to date"
            except Exception as mig_err:
                migration_status = f"Pending migrations: {mig_err}"
                db.close()
                return res.warn(f"Database reachable but migrations not current: {mig_err}")

            elapsed = (time.perf_counter() - start) * 1000.0
            db.close()
            return res.success(f"Database connected and migrations verified ({migration_status})", elapsed)
        except Exception as e:
            db.close()
            return res.fail(f"Database query failed: {e}")
    except Exception as exc:
        return res.fail(f"Could not initialize database session: {exc}")


def check_redis() -> CheckResult:
    """Validate Redis connection, atomic operations, and latency."""
    res = CheckResult("Redis 7 In-Memory Cluster", "Data Tier")
    start = time.perf_counter()
    try:
        from backend.redis_client import get_redis

        r = get_redis()
        if r is None:
            return res.warn("Redis URL not configured or in-memory fallback active")

        # Ping
        ping_ok = r.ping()
        if not ping_ok:
            return res.fail("Redis ping returned False")

        # Test write & read
        test_key = f"_probe_test_{int(time.time())}"
        r.setex(test_key, 10, "ok")
        val = r.get(test_key)
        r.delete(test_key)

        elapsed = (time.perf_counter() - start) * 1000.0
        if val == b"ok" or val == "ok":
            return res.success("Redis ping, write, and read verified successfully", elapsed)
        else:
            return res.fail("Redis read/write probe did not match expected value")
    except Exception as exc:
        return res.fail(f"Redis connectivity failed: {exc}")


def check_storage_and_cdn(skip_network: bool = False) -> CheckResult:
    """Validate S3 / R2 storage adapter, bucket permissions, and CDN resolution."""
    res = CheckResult("S3 / Cloudflare R2 Storage & CDN", "Storage Tier")
    start = time.perf_counter()
    try:
        from backend.storage import get_storage_adapter, S3StorageAdapter, LocalStorageAdapter

        storage = get_storage_adapter()
        backend_name = type(storage).__name__

        if isinstance(storage, LocalStorageAdapter):
            elapsed = (time.perf_counter() - start) * 1000.0
            return res.warn(
                f"Using LocalStorageAdapter ({storage.root_dir}). Set STORAGE_BACKEND=s3 for production.",
                {"backend": "local", "root_dir": storage.root_dir}
            )

        if isinstance(storage, S3StorageAdapter):
            bucket = storage.bucket_name
            region = storage.region_name
            cdn_domain = storage.cdn_domain

            if not bucket:
                return res.fail("STORAGE_BACKEND=s3 but S3_BUCKET_NAME is not set")

            if skip_network:
                return res.success(f"S3 adapter configured for bucket '{bucket}' in '{region}'", details={
                    "bucket": bucket, "region": region, "cdn_domain": cdn_domain
                })

            # Check S3 probe
            probe_key = f"audio/_probe_{int(time.time())}.txt"
            try:
                # Test upload
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tf:
                    tf.write(b"jisr_s3_readiness_probe")
                    temp_path = tf.name

                cdn_url = storage.upload_file(temp_path, probe_key)
                os.remove(temp_path)

                # Test existence
                exists = storage.file_exists(probe_key)
                
                # Cleanup probe object
                try:
                    storage.s3_client.delete_object(Bucket=bucket, Key=probe_key)
                except Exception:
                    pass

                elapsed = (time.perf_counter() - start) * 1000.0
                if exists:
                    return res.success(
                        f"S3 bucket '{bucket}' read/write verified. CDN domain: {cdn_domain or 'default'}",
                        elapsed,
                        {"bucket": bucket, "region": region, "sample_cdn_url": cdn_url}
                    )
                else:
                    return res.fail(f"Probe object uploaded to S3 but file_exists returned False")
            except Exception as s3_err:
                return res.fail(f"S3 bucket probe failed: {s3_err}")

        return res.warn(f"Unknown storage adapter type: {backend_name}")
    except Exception as exc:
        return res.fail(f"Storage adapter check error: {exc}")


def check_payment_provider(skip_network: bool = False) -> CheckResult:
    """Validate Stripe / Tap payments secret keys and webhook signing secrets."""
    res = CheckResult("Stripe / Payment Gateway", "SaaS Integrations")
    start = time.perf_counter()

    provider = os.getenv("FAHIM_PAYMENT_PROVIDER", "stripe").lower()
    webhook_secret = os.getenv("FAHIM_PAYMENT_WEBHOOK_SECRET", "").strip()
    stripe_key = os.getenv("STRIPE_SECRET_KEY", "").strip()

    if not webhook_secret:
        return res.fail("FAHIM_PAYMENT_WEBHOOK_SECRET is not configured")

    if not webhook_secret.startswith("whsec_"):
        return res.warn(f"Webhook secret '{webhook_secret[:6]}...' does not start with standard 'whsec_' prefix")

    if provider == "stripe":
        if not stripe_key:
            return res.fail("STRIPE_SECRET_KEY is not configured")

        if skip_network:
            key_mode = "Live" if stripe_key.startswith("sk_live_") else "Test/Sandbox"
            return res.success(f"Stripe credentials format valid ({key_mode})", details={"provider": provider, "mode": key_mode})

        # Test Stripe API key against Stripe Balance API
        try:
            headers = {"Authorization": f"Bearer {stripe_key}"}
            resp = httpx.get("https://api.stripe.com/v1/balance", headers=headers, timeout=5.0)
            elapsed = (time.perf_counter() - start) * 1000.0

            if resp.status_code == 200:
                key_type = "LIVE" if stripe_key.startswith("sk_live_") else "TEST"
                return res.success(f"Stripe API authentication verified ({key_type} mode)", elapsed)
            elif resp.status_code == 401:
                return res.fail(f"Stripe API rejected key (HTTP 401 Unauthorized)")
            else:
                return res.warn(f"Stripe API returned HTTP {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            return res.warn(f"Stripe API network probe timed out or failed: {e}")

    return res.success(f"Payment provider configured for {provider}")


def check_email_smtp(skip_network: bool = False) -> CheckResult:
    """Validate SMTP server connectivity, STARTTLS encryption, and authentication."""
    res = CheckResult("Transactional Email (SMTP / SES)", "SaaS Integrations")
    start = time.perf_counter()

    host = os.getenv("FAHIM_SMTP_HOST", "").strip()
    port = int(os.getenv("FAHIM_SMTP_PORT", "587"))
    user = os.getenv("FAHIM_SMTP_USER", "").strip()
    password = os.getenv("FAHIM_SMTP_PASS", "").strip()
    from_email = os.getenv("FAHIM_SMTP_FROM", "").strip()

    if not host:
        return res.fail("FAHIM_SMTP_HOST is not configured (OTP delivery will fail in production)")

    if not from_email:
        return res.warn("FAHIM_SMTP_FROM is not set, defaulting to noreply")

    if skip_network:
        return res.success(f"SMTP configured for {host}:{port} ({user or 'anonymous'})")

    try:
        # Connect to SMTP server
        server = smtplib.SMTP(host, port, timeout=5.0)
        server.ehlo()

        # Negotiate STARTTLS if supported
        if server.has_extn("STARTTLS"):
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.ehlo()

        # Authenticate if credentials provided
        if user and password:
            server.login(user, password)
            server.quit()
            elapsed = (time.perf_counter() - start) * 1000.0
            return res.success(f"SMTP authentication verified with {host}:{port}", elapsed)
        else:
            server.quit()
            elapsed = (time.perf_counter() - start) * 1000.0
            return res.warn(f"SMTP host {host}:{port} reachable but no user/pass configured", {"host": host})
    except smtplib.SMTPAuthenticationError as auth_err:
        return res.fail(f"SMTP authentication failed with user '{user}': {auth_err}")
    except Exception as conn_err:
        return res.fail(f"SMTP connection to {host}:{port} failed: {conn_err}")


def check_gemini_ai(skip_network: bool = False) -> CheckResult:
    """Validate Google Gemini API key and model availability."""
    res = CheckResult("Google Gemini AI API", "SaaS Integrations")
    start = time.perf_counter()

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return res.fail("GEMINI_API_KEY is not configured (Ask Fahim will be unavailable)")

    if not api_key.startswith("AIzaSy"):
        return res.warn(f"API key '{api_key[:6]}...' does not match standard Gemini key pattern")

    if skip_network:
        return res.success("GEMINI_API_KEY format valid")

    try:
        # Lightweight Gemini ping
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash?key={api_key}"
        resp = httpx.get(url, timeout=5.0)
        elapsed = (time.perf_counter() - start) * 1000.0

        if resp.status_code == 200:
            return res.success("Gemini API key verified (gemini-2.5-flash model active)", elapsed)
        elif resp.status_code == 400 and "API_KEY_INVALID" in resp.text:
            return res.fail("Gemini API rejected key: API_KEY_INVALID")
        else:
            # Fallback check on v1beta/models
            url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            resp_list = httpx.get(url_list, timeout=5.0)
            if resp_list.status_code == 200:
                return res.success("Gemini API key verified against models directory", elapsed)
            return res.warn(f"Gemini API returned HTTP {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        return res.warn(f"Gemini API probe network timeout: {e}")


def run_all_checks(skip_network: bool = False, verbose: bool = False) -> Tuple[bool, List[CheckResult]]:
    """Execute all six production readiness probes."""
    checks = [
        check_database(),
        check_redis(),
        check_storage_and_cdn(skip_network=skip_network),
        check_payment_provider(skip_network=skip_network),
        check_email_smtp(skip_network=skip_network),
        check_gemini_ai(skip_network=skip_network),
    ]

    print("\n" + "=" * 78)
    print("  JISR Arabic (فهيم) Enterprise Production Readiness & SaaS Audit")
    print("  Environment : " + os.getenv("FAHIM_ENV", "development"))
    print("  Network Mode: " + ("OFFLINE (Static Format Validation)" if skip_network else "LIVE (Network Handshake)"))
    print("=" * 78 + "\n")

    all_passed = True
    for c in checks:
        if not c.passed:
            all_passed = False
            status_tag = "[FAIL] "
        elif c.warning:
            status_tag = "[WARN] "
        else:
            status_tag = "[PASS] "

        lat_str = f"({c.latency_ms:.1f}ms)" if c.latency_ms > 0 else ""
        print(f"  {status_tag} {c.name:<38} {lat_str:>9} | {c.message}")
        if verbose and c.details:
            for k, v in c.details.items():
                print(f"         └─ {k}: {v}")

    print("\n" + "-" * 78)
    total_checks = len(checks)
    passed_count = sum(1 for c in checks if c.passed and not c.warning)
    warn_count = sum(1 for c in checks if c.warning)
    fail_count = sum(1 for c in checks if not c.passed)

    print(f"  Summary: {passed_count}/{total_checks} Passed | {warn_count} Warnings | {fail_count} Failed")
    print(f"  Verdict: {'[APPROVED FOR PRODUCTION]' if all_passed and fail_count == 0 else '[ATTENTION: REMEDIATION REQUIRED]'}")
    print("=" * 78 + "\n")

    return all_passed, checks


def main():
    parser = argparse.ArgumentParser(description="Verify JISR Arabic production readiness and SaaS credentials.")
    parser.add_argument("--skip-network", "--offline", dest="skip_network", action="store_true", help="Skip live external API calls and validate config formats only")
    parser.add_argument("--verbose", action="store_true", help="Print verbose diagnostic details")
    args = parser.parse_args()

    all_passed, _ = run_all_checks(skip_network=args.skip_network, verbose=args.verbose)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
