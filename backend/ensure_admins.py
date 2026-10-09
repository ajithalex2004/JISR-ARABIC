import os
import uuid
from dotenv import load_dotenv
if os.getenv("FAHIM_ENV", "development").lower() != "production":
    load_dotenv('backend/.env', override=False)
from backend.security import hash_password
from sqlalchemy import create_engine, text

ADMIN_EMAIL = os.getenv("INITIAL_ADMIN_EMAIL", "").strip().lower()
ADMIN_PASSWORD = os.getenv("INITIAL_ADMIN_PASSWORD", "").strip()
ADMIN_NAME = os.getenv("INITIAL_ADMIN_NAME", "System Administrator").strip()

def ensure_admins_in_db(db_url, is_sqlite=False):
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        print("Skipping admin provisioning: INITIAL_ADMIN_EMAIL and INITIAL_ADMIN_PASSWORD are not set.")
        return

    print(f"\n--- Checking DB: {db_url[:45]}... ---")
    engine = create_engine(db_url)
    with engine.begin() as conn:
        email = ADMIN_EMAIL
        name = ADMIN_NAME
        hashed = hash_password(ADMIN_PASSWORD)
        row = conn.execute(text("SELECT id, email, role FROM users WHERE LOWER(email) = :email"), {"email": email}).fetchone()
        if row:
            user_id, existing_email, role = row
            print(f"Updating password & role for existing user: {existing_email} (ID: {user_id})")
            conn.execute(
                text("UPDATE users SET password_hash = :hash, role = 'admin', is_verified = TRUE WHERE LOWER(email) = :email"),
                {"hash": hashed, "email": email}
            )
        else:
            new_id = str(uuid.uuid4())
            print(f"Creating new admin user: {email} (ID: {new_id})")
            conn.execute(
                text("INSERT INTO users (id, email, password_hash, full_name, role, is_verified) VALUES (:id, :email, :hash, :name, 'admin', TRUE)"),
                {"id": new_id, "email": email, "hash": hashed, "name": name}
            )
        # Verify
        users = conn.execute(text("SELECT email, role, is_verified FROM users WHERE role = 'admin'")).fetchall()
        print("Admins in DB:")
        for user in users:
            print(f"  - {user[0]} (Role: {user[1]}, Verified: {user[2]})")

if __name__ == "__main__":
    # 1. Update Neon Postgres DB
    pg_url = os.environ.get("DATABASE_URL")
    if pg_url:
        ensure_admins_in_db(pg_url, is_sqlite=False)

    # 2. Update SQLite DB
    sqlite_path = os.path.abspath("backend/fahim.db")
    if os.path.exists(sqlite_path):
        ensure_admins_in_db(f"sqlite:///{sqlite_path}", is_sqlite=True)
