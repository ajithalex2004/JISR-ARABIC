"""CLI test script to verify SMTP email sending configuration."""
import os
import sys
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from backend.email_delivery import send_otp_email

def main():
    recipient = sys.argv[1] if len(sys.argv) > 1 else None
    
    host = os.getenv("FAHIM_SMTP_HOST", "").strip()
    port = os.getenv("FAHIM_SMTP_PORT", "587")
    user = os.getenv("FAHIM_SMTP_USER", "").strip()
    sender = os.getenv("FAHIM_SMTP_FROM", "").strip()

    print("=" * 60)
    print("JISR Arabic - SMTP Configuration Test")
    print("=" * 60)
    print(f"SMTP Host: {host or '[NOT SET - Simulation Mode]'}")
    print(f"SMTP Port: {port}")
    print(f"SMTP User: {user or '[NOT SET]'}")
    print(f"SMTP From: {sender or '[NOT SET]'}")
    print("=" * 60)

    if not host:
        print("\n[!] FAHIM_SMTP_HOST is not set in backend/.env.")
        print("    The application is currently running in OFFLINE/SIMULATION mode.")
        print("    In this mode, OTP codes are logged and auto-filled on-screen.")
        print("    To send real emails, please configure backend/.env.")
        return

    if not recipient:
        recipient = user or "test@example.com"
        print(f"\nNo recipient specified. Using default: {recipient}")
        print("Tip: You can specify an email address: python backend/test_smtp.py your_email@example.com\n")

    print(f"Attempting to send test OTP email to: {recipient}...")
    success = send_otp_email(recipient, "987654", "test_verification")
    
    if success:
        print(f"\n[+] SUCCESS! Test email sent successfully to {recipient}.")
        print("    Please check your Inbox (and Spam/Junk folder).")
    else:
        print(f"\n[-] FAILED to send email. Please check your SMTP credentials, port, and security settings.")

if __name__ == "__main__":
    main()
