"""Import authored curriculum content without demo users or demo vouchers.

Run from the project root after migrations:
    python -m backend.content_import
"""
from backend.curriculum_seed import seed_database
from backend.database import SessionLocal

def main():
    db = SessionLocal()
    try:
        seed_database(db, include_demo_data=False)
        print("Curriculum content imported without demo accounts.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
