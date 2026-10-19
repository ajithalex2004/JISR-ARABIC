"""Import authored curriculum content without demo users or demo vouchers.

Run from the project root after migrations:
    python -m backend.content_import

On Railway, set IMPORT_CONTENT_ON_DEPLOY=1 on the API service to run this once at start-up
(see docs/MOBILE_RELEASE_RUNBOOK.md); remove the variable afterwards.
"""
from backend.curriculum_seed import seed_database
from backend.database import SessionLocal
from backend.models import Lesson
from backend.redis_client import invalidate_lesson_cache


def main():
    db = SessionLocal()
    try:
        seed_database(db, include_demo_data=False)
        lessons = db.query(Lesson.id, Lesson.grade, Lesson.term).all()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    # Lesson packages are cached for a day; drop them so learners get the new content now.
    for lesson_id, grade, term in lessons:
        invalidate_lesson_cache(lesson_id, grade=grade, term=term)
    print(f"Curriculum content imported without demo accounts; cache cleared for {len(lessons)} lessons.")


if __name__ == "__main__":
    main()
