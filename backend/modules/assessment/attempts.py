"""Application operations; callers provide explicit database sessions and actors."""
import json
import uuid
import hashlib
import datetime
from sqlalchemy.orm import Session
from backend.models import LearnerAttempt, LearnerMistake, LessonVersion, ChildProfile, ConceptMastery
from backend.schemas import AttemptSubmitRequest, AttemptSubmitResponse
from backend.scoring import evaluate_activity_answer
from backend.errors import ApplicationError
from backend.modules.curriculum.access import require_lesson, learner_content


def _map_activity_to_concept(lesson_id: str, activity_id: str, activity_data: dict) -> tuple:
    act_type = activity_data.get("type", "")
    title = (activity_data.get("title_ar", "") + " " + activity_id).lower()

    if "taa" in title or "تاء" in title or "ortho" in title:
        return ("ortho_taa_marbutah", "التاء المربوطة والهاء", "Taa Marbutah vs. Haa", "orthography")
    if "plural" in title or "جمع" in title:
        return ("plurals_sound", "جمع المذكر والمؤنث السالم", "Sound Plurals (Masculine & Feminine)", "grammar")
    if "jar" in title or "جر" in title:
        return ("prepositions_jar", "حروف الجر والتراكيب", "Prepositions & Genitive Case", "grammar")
    if "conjugation" in title or "فعل" in title or "تصريف" in title:
        return ("conjugation_past", "تصريف الأفعال والضمائر", "Verb Conjugation & Tenses", "grammar")
    if "sentence" in title or "اسمية" in title or act_type == "sentence_builder":
        return ("syntax_nominal", "الجملة الاسمية (المبتدأ والخبر)", "Nominal Sentence (Mubtada & Khabar)", "grammar")
    if "vocab" in title or "مفرد" in title or "كلمات" in title:
        return ("vocab_sports", "المفردات والدلالة اللغوية", "Curriculum Vocabulary & Roots", "vocabulary")
    return ("reading_fluency", "الطلاقة وفهم المقروء", "Reading Fluency & Comprehension", "reading")


def submit_attempt(req: AttemptSubmitRequest, *, db: Session, actor=None):
    """
    Submits a learner attempt for an activity.
    Strictly evaluated on the server using pinned answer key. Client-supplied score is ignored.
    """
    require_lesson(db, actor, req.lesson_id, req.child_id)
    child = db.query(ChildProfile).filter(ChildProfile.id == req.child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")
    if req.idempotency_key:
        prior = db.query(LearnerAttempt).filter(LearnerAttempt.idempotency_key == req.idempotency_key).first()
        if prior:
            return AttemptSubmitResponse(attempt_id=prior.id, is_correct=prior.is_correct,
                score=prior.score, max_score=prior.max_score, feedback_ar="", feedback_en="Already recorded",
                correct_solution=None, is_awaiting_tutor=False)

    # Fetch active lesson content to get pinned answer key
    version_query = db.query(LessonVersion).filter(LessonVersion.lesson_id == req.lesson_id)
    if req.lesson_version_id:
        version = version_query.filter(LessonVersion.id == req.lesson_version_id).first()
        if version is None or version.status != "published":
            raise ApplicationError(409, "The requested lesson version is no longer published")
    else:
        version = version_query.filter(LessonVersion.is_active == True).first()

    if not version:
        raise ApplicationError(status_code=404, detail="Lesson version not found")
    if len(version.content_hash or "") == 64 and hashlib.sha256(version.content_json.encode("utf-8")).hexdigest() != version.content_hash:
        raise ApplicationError(500, "Lesson content integrity check failed")

    content = json.loads(version.content_json)

    # Locate activity in content
    activity_data = None

    # 1. Check prep_check
    if "prep_check" in content and "questions" in content["prep_check"]:
        for q in content["prep_check"]["questions"]:
            if q["id"] == req.activity_id:
                activity_data = {"type": "choice", "correct_answer": q["correct_answer"], "points": 1.0}
                break

    # 2. Check practice_activities
    if not activity_data and "practice_activities" in content:
        for act in content["practice_activities"]:
            if act["id"] == req.activity_id:
                activity_data = act
                break

    # 3. Check sentence_builder
    if not activity_data and "sentence_builder" in content and "challenges" in content["sentence_builder"]:
        for ch in content["sentence_builder"]["challenges"]:
            if ch["id"] == req.activity_id:
                activity_data = {
                    "type": "sentence_builder",
                    "correct_answer": ch["target_ar"],
                    "points": 1.0
                }
                break

    # 4. Check exam_practice
    if not activity_data and "exam_practice" in content and "objective_questions" in content["exam_practice"]:
        for eq in content["exam_practice"]["objective_questions"]:
            if eq["id"] == req.activity_id:
                activity_data = {
                    "type": "choice",
                    "correct_answer": eq["correct_answer"],
                    "points": eq.get("marks", 2.0)
                }
                break

    if not activity_data:
        raise ApplicationError(404, "Assessment activity not found in the active lesson version")

    is_correct, score, max_score, fb_ar, fb_en, correct_solution, is_awaiting_tutor = evaluate_activity_answer(
        activity_data,
        req.user_answer
    )

    # Persist attempt
    attempt_id = str(uuid.uuid4())
    attempt = LearnerAttempt(
        id=attempt_id,
        child_id=child.id,
        lesson_id=req.lesson_id,
        lesson_version_id=version.id,
        activity_id=req.activity_id,
        path_type=req.path_type,
        is_correct=is_correct,
        score=score,
        max_score=max_score,
        user_answer=str(req.user_answer),
        details_json=json.dumps({
            "feedback_ar": fb_ar,
            "feedback_en": fb_en,
            "client_score_rejected": req.client_score is not None
        }),
        idempotency_key=req.idempotency_key
    )
    db.add(attempt)

    # Dynamic Event-Derived Concept Mastery Update
    c_key, c_ar, c_en, cat = _map_activity_to_concept(req.lesson_id, req.activity_id, activity_data)
    cm = db.query(ConceptMastery).filter(
        ConceptMastery.child_id == child.id,
        ConceptMastery.concept_key == c_key
    ).first()
    if not cm:
        cm = ConceptMastery(
            child_id=child.id,
            concept_key=c_key,
            concept_name_ar=c_ar,
            concept_name_en=c_en,
            category=cat,
            mastery_percentage=0.0,
            total_attempts=0,
            correct_attempts=0,
            is_gap=False,
            interval_days=1,
            ease_factor=2.5,
            repetition_count=0
        )
        db.add(cm)
    cm.total_attempts += 1
    if is_correct:
        cm.correct_attempts += 1
    cm.mastery_percentage = round((cm.correct_attempts / cm.total_attempts) * 100.0, 1)
    cm.is_gap = (cm.mastery_percentage < 70.0 and cm.total_attempts >= 2)
    cm.last_practiced_at = datetime.datetime.now(datetime.UTC)

    # If incorrect, log into mistake notebook
    if not is_correct and not is_awaiting_tutor:
        existing_mistake = db.query(LearnerMistake).filter(
            LearnerMistake.child_id == child.id,
            LearnerMistake.lesson_id == req.lesson_id,
            LearnerMistake.activity_id == req.activity_id,
            LearnerMistake.is_resolved == False
        ).first()

        if existing_mistake:
            existing_mistake.review_count += 1
            existing_mistake.wrong_answer = str(req.user_answer)
        else:
            mistake = LearnerMistake(
                child_id=child.id,
                lesson_id=req.lesson_id,
                activity_id=req.activity_id,
                concept_name=activity_data.get("title_ar", "المفردات والقواعد"),
                wrong_answer=str(req.user_answer),
                correct_answer=str(correct_solution or ""),
                is_resolved=False
            )
            db.add(mistake)

    db.commit()

    return AttemptSubmitResponse(
        attempt_id=attempt_id,
        is_correct=is_correct,
        score=score,
        max_score=max_score,
        feedback_ar=fb_ar,
        feedback_en=fb_en,
        correct_solution=correct_solution,
        is_awaiting_tutor=is_awaiting_tutor
    )


def get_mistake_notebook(child_id: str, *, db: Session):
    """Fetch private mistake notebook entries for targeted re-practice."""
    mistakes = db.query(LearnerMistake).filter(
        LearnerMistake.child_id == child_id
    ).order_by(LearnerMistake.created_at.desc()).all()

    return [
        {
            "id": m.id,
            "lesson_id": m.lesson_id,
            "activity_id": m.activity_id,
            "concept_name": m.concept_name,
            "wrong_answer": m.wrong_answer,
            "correct_answer": m.correct_answer,
            "is_resolved": m.is_resolved,
            "review_count": m.review_count,
            "created_at": m.created_at.isoformat()
        }
        for m in mistakes
    ]


def resolve_mistake(mistake_id: int, *, db: Session):
    """Mark a mistake entry as reviewed and resolved."""
    m = db.query(LearnerMistake).filter(LearnerMistake.id == mistake_id).first()
    if not m:
        raise ApplicationError(status_code=404, detail="Mistake entry not found")
    m.is_resolved = True
    db.commit()
    return {"success": True, "message": "Mistake marked as resolved."}
