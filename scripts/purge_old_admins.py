import os
import sys
import sqlite3
from dotenv import load_dotenv

load_dotenv('backend/.env')
from sqlalchemy import create_engine, text

def purge_postgres(pg_url):
    print("\n==========================================")
    print("Purging unauthorized admins from Neon Postgres")
    print("==========================================")
    engine = create_engine(pg_url)
    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT id, email FROM users WHERE (role = 'admin' OR LOWER(email) IN ('admin@fahim.ae', 'admin@jisr.ae')) AND LOWER(email) != 'alex@exlsolutions.ae'")
        ).fetchall()
        print('Users found for deletion:', rows)
        for r in rows:
            uid, email = r
            del_sess = conn.execute(text("DELETE FROM user_sessions WHERE user_id = :uid"), {'uid': uid}).rowcount
            print(f'  Deleted {del_sess} sessions for {email}')
            del_child = conn.execute(text("DELETE FROM child_profiles WHERE parent_id = :uid"), {'uid': uid}).rowcount
            print(f'  Deleted {del_child} child profiles for {email}')
            conn.execute(text("DELETE FROM users WHERE id = :uid"), {'uid': uid})
            print(f'  Deleted user record {email} (ID: {uid})')

        remaining = conn.execute(text("SELECT id, email, role, is_verified FROM users WHERE role = 'admin'")).fetchall()
        print("\nVerified Remaining Admins in Neon Postgres:")
        for u in remaining:
            print(f"  -> Email: {u[1]} | Role: {u[2]} | Verified: {u[3]} | ID: {u[0]}")

def purge_sqlite(sqlite_path):
    print("\n==========================================")
    print(f"Purging unauthorized admins from SQLite: {sqlite_path}")
    print("==========================================")
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    # Check if tables exist
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cur.fetchall()]
    print('SQLite tables:', tables)

    cur.execute("SELECT id, email FROM users WHERE (role = 'admin' OR LOWER(email) IN ('admin@fahim.ae', 'admin@jisr.ae')) AND LOWER(email) != 'alex@exlsolutions.ae'")
    rows = cur.fetchall()
    print('Users found for deletion in SQLite:', rows)
    for r in rows:
        uid, email = r
        if 'user_sessions' in tables:
            cur.execute("DELETE FROM user_sessions WHERE user_id = ?", (uid,))
        if 'child_profiles' in tables:
            cur.execute("DELETE FROM child_profiles WHERE parent_id = ?", (uid,))
        cur.execute("DELETE FROM users WHERE id = ?", (uid,))
        print(f"  Deleted SQLite user record {email} (ID: {uid})")
    conn.commit()

    cur.execute("SELECT id, email, role, is_verified FROM users WHERE role = 'admin'")
    remaining = cur.fetchall()
    print("\nVerified Remaining Admins in SQLite:")
    for u in remaining:
        print(f"  -> Email: {u[1]} | Role: {u[2]} | Verified: {u[3]} | ID: {u[0]}")
    conn.close()

if __name__ == "__main__":
    pg_url = os.environ.get("DATABASE_URL")
    if pg_url:
        purge_postgres(pg_url)

    sqlite_path = os.path.abspath("backend/fahim.db")
    if os.path.exists(sqlite_path):
        purge_sqlite(sqlite_path)

    print("\nAll databases purged and verified successfully.")
