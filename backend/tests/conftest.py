"""Test-only compatibility settings for local OTP flow coverage."""
import os

# OTPs are never exposed by default in application environments. Tests opt in
# explicitly so the delivery adapter can be exercised without an email service.
os.environ.setdefault("FAHIM_EXPOSE_DEBUG_OTP", "1")
