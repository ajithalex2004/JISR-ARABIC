"""Create or promote a production administrator interactively.

Usage: python -m backend.create_admin
Credentials are entered interactively and never printed or stored in source.
"""
import getpass
import os
from backend.database import SessionLocal
from backend.models import User
from backend.security import hash_password

def main():
    email = input("Admin email: ").strip().lower()
    password = getpass.getpass("Admin password (12+ characters): ")
    confirmation = getpass.getpass("Confirm password: ")
    if not email or "@" not in email:
        raise SystemExit("A valid email is required.")
    if len(password) < 12 or password != confirmation:
        raise SystemExit("Passwords must match and be at least 12 characters.")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            user = User(email=email, full_name="Fahim Administrator")
            db.add(user)
        user.password_hash = hash_password(password)
        user.role = "admin"
        user.is_verified = True
        db.commit()
        print("Administrator account created/updated.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
