"""Application operations; callers provide explicit database sessions and actors."""
import uuid
import datetime
from sqlalchemy.orm import Session
from typing import Optional
from backend.models import ChildProfile, CapsuleProgress
from backend.schemas import CapsuleCompleteRequest
from backend.malazim_bank import get_malazim_booklet
from backend.capsules_bank import get_all_capsules, get_capsule_by_id
from backend.errors import ApplicationError
from backend.modules.curriculum.access import require_lesson, learner_content
from backend.redis_client import cache_get, cache_set

def get_malazim(lesson_id: str, child_id=None, is_reviewer=False, *, db: Session, actor=None):
    """
    Retrieve interactive study booklet for a lesson or grade.
    Contains both:
    - Study Mode (وضع المذاكرة الشامل مع التمارين التفاعلية)
    - Notes / Quick Review Mode (وضع الملاحظات المركزة ومراجعة الـ 15 دقيقة)
    """
    actual_lesson_id = str(lesson_id).strip()
    if actual_lesson_id.lower() in ("grade_7", "7", "g7", "grade7"):
        actual_lesson_id = "lesson_g7_t1_ch01"
    elif actual_lesson_id.lower() in ("grade_6", "6", "g6", "grade6"):
        actual_lesson_id = "lesson_g6_t1_ch01"
    elif actual_lesson_id.lower() in ("grade_5", "5", "g5", "grade5"):
        actual_lesson_id = "lesson_01_ball_games"

    reviewer = bool(actor is not None and getattr(actor, "role", None) in {"admin", "tutor"}) and is_reviewer
    require_lesson(db, actor, actual_lesson_id, child_id, is_reviewer=is_reviewer)
    booklet = get_malazim_booklet(actual_lesson_id)
    if booklet is None:
        raise ApplicationError(404, "Study booklet not available for this lesson")
    return {
        "success": True,
        "booklet": booklet if reviewer else learner_content(booklet)
    }


def list_capsules(child_id: Optional[str]=None, grade: Optional[int]=None, *, db: Session):
    """
    List all 3-to-5 minute bite-sized microlearning capsules.
    Optionally filtered by grade. If grade is omitted and child_id is provided,
    uses the child's default_grade.
    """
    target_grade = grade
    if target_grade is None and child_id:
        child = db.query(ChildProfile.default_grade).filter(ChildProfile.id == child_id).first()
        if child and child[0]:
            target_grade = child[0]

    capsules = get_all_capsules(target_grade)
    completed_ids = set()

    if child_id:
        records = db.query(CapsuleProgress.capsule_id).filter(CapsuleProgress.child_id == child_id).all()
        completed_ids = {r[0] for r in records}

    enriched = []
    for c in capsules:
        enriched.append({
            **c,
            "is_completed": c["id"] in completed_ids
        })

    return {
        "success": True,
        "grade": target_grade,
        "count": len(enriched),
        "completed_count": len(completed_ids),
        "capsules": enriched
    }


def get_capsule(capsule_id: str):
    """Retrieve full content, audio script, and checkpoint quiz for a capsule."""
    cache_key = f"capsule:{capsule_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    capsule = get_capsule_by_id(capsule_id)
    result = {
        "success": True,
        "capsule": capsule
    }
    cache_set(cache_key, result, ttl_seconds=86400)
    return result


def complete_capsule(capsule_id: str, payload: CapsuleCompleteRequest, *, db: Session):
    """
    Record that a student successfully completed a microlearning capsule,
    recording score, duration, and awarding progress.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == payload.child_id).first()
    if not child:
        raise ApplicationError(
            status_code=404,
            detail="Child profile not found."
        )
    if payload.idempotency_key:
        prior = db.query(CapsuleProgress).filter(CapsuleProgress.id == payload.idempotency_key).first()
        if prior:
            return {"success": True, "capsule_id": capsule_id, "child_id": payload.child_id,
                    "score": prior.score, "badge_awarded": None,
                    "message_ar": "تم تسجيل هذه المحاولة مسبقاً."}
    capsule = get_capsule_by_id(capsule_id)
    if not capsule:
        raise ApplicationError(404, "Capsule not found")
    questions = capsule.get("quiz", [])
    if not payload.answers:
        verified_score = 0.0
    else:
        if set(payload.answers) - {str(i) for i in range(len(questions))}:
            raise ApplicationError(422, "Invalid capsule question")
        verified_score = round(sum(payload.answers.get(str(i)) == q.get("correct_index") for i, q in enumerate(questions)) / max(1, len(questions)) * 100, 1)

    # Upsert or record completion
    existing = db.query(CapsuleProgress).filter(
        CapsuleProgress.child_id == payload.child_id,
        CapsuleProgress.capsule_id == capsule_id
    ).first()

    if existing:
        existing.score = max(existing.score, verified_score)
        existing.time_spent_seconds = payload.time_spent_seconds
        existing.completed_at = datetime.datetime.utcnow()
    else:
        progress = CapsuleProgress(
            id=payload.idempotency_key or str(uuid.uuid4()),
            child_id=payload.child_id,
            capsule_id=capsule_id,
            score=verified_score,
            time_spent_seconds=payload.time_spent_seconds,
            completed_at=datetime.datetime.utcnow()
        )
        db.add(progress)

    db.commit()

    return {
        "success": True,
        "capsule_id": capsule_id,
        "child_id": payload.child_id,
        "score": verified_score,
        "badge_awarded": "وسام إتقان الكبسولة الذكية (Smart Capsule Badge) 🏅",
        "message_ar": "أحسنت! تم تسجيل إنجازك بنجاح ونيل وسام الإتقان السريع."
    }



def check_booklet_answer(lesson_id, payload, *, db: Session, actor=None):
    actual_lesson_id = str(lesson_id).strip()
    if actual_lesson_id.lower() in ("grade_7", "7", "g7", "grade7"):
        actual_lesson_id = "lesson_g7_t1_ch01"
    elif actual_lesson_id.lower() in ("grade_6", "6", "g6", "grade6"):
        actual_lesson_id = "lesson_g6_t1_ch01"
    elif actual_lesson_id.lower() in ("grade_5", "5", "g5", "grade5"):
        actual_lesson_id = "lesson_01_ball_games"

    require_lesson(db, actor, actual_lesson_id, payload.child_id)
    booklet = get_malazim_booklet(actual_lesson_id)
    if booklet is None:
        raise ApplicationError(404, "Study booklet not found")
    for section in booklet["study_mode"]["sections"]:
        if section["section_id"] == payload.section_id:
            exercise = section["inline_exercise"]
            if payload.answer < 0 or payload.answer >= len(exercise["options"]):
                raise ApplicationError(422, "Invalid answer option")
            return {"is_correct": payload.answer == exercise["correct_index"],
                    "correct_index": exercise["correct_index"],
                    "explanation_ar": exercise.get("explanation_ar", ""),
                    "explanation_en": exercise.get("explanation_en", "")}
    raise ApplicationError(404, "Exercise not found")


def check_sentence(lesson_id, payload, *, db: Session, actor=None):
    import json
    from backend.models import LessonVersion
    from backend.scoring import evaluate_activity_answer
    require_lesson(db, actor, lesson_id, payload.child_id)
    version = db.query(LessonVersion).filter_by(lesson_id=lesson_id, is_active=True).first()
    if version is None:
        raise ApplicationError(404, "Lesson content not available")
    challenges = json.loads(version.content_json).get("sentence_builder", {}).get("challenges", [])
    for challenge in challenges:
        if challenge["id"] == payload.activity_id:
            result = evaluate_activity_answer({"type": "sentence_builder", "correct_answer": challenge["target_ar"], "points": 1}, payload.answer)
            return {"is_correct": result[0], "feedback_en": result[4]}
    raise ApplicationError(404, "Sentence challenge not found")
