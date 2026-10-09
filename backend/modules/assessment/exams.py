"""Application operations; callers provide explicit database sessions and actors."""
import json
import uuid
import datetime
import hashlib
from sqlalchemy.orm import Session
from backend.models import ChildProfile, ExamSimulationResult, AssessmentSession, ConceptMastery, LearnerMistake, LearnerAttempt
from backend.models import Lesson, LessonVersion
from backend.schemas import SubmitExamSimulationRequest
from backend.assessment_bank import get_official_exam_simulation, evaluate_exam_submission, get_adaptive_flow_questions
from backend.errors import ApplicationError
from backend.modules.curriculum.access import require_lesson, learner_content


def _questions_for_scope(grade: int, term: int, *, db: Session):
    """Build an exam bank from the active published curriculum versions."""
    questions = []
    lessons = db.query(Lesson).filter(Lesson.grade == grade, Lesson.term == term).order_by(Lesson.lesson_order).all()
    for lesson in lessons:
        version = db.query(LessonVersion).filter(
            LessonVersion.lesson_id == lesson.id,
            LessonVersion.is_active == True,
            LessonVersion.status == "published",
        ).first()
        if not version:
            continue
        try:
            content = json.loads(version.content_json)
        except (TypeError, ValueError):
            continue
        for question in content.get("exam_practice", {}).get("objective_questions", []):
            if not isinstance(question, dict):
                continue
            item = dict(question)
            if "correct_index" not in item:
                options = item.get("options", [])
                correct_ans = item.get("correct_answer")
                idx = next((i for i, opt in enumerate(options) if isinstance(opt, dict) and opt.get("id") == correct_ans), None)
                if idx is not None:
                    item["correct_index"] = idx
                else:
                    continue
            item["id"] = f"{lesson.id}:{question.get('id', len(questions))}"
            item.setdefault("points", question.get("marks", 1))
            item.setdefault("bloom_level", "understanding")
            item.setdefault("bloom_name_ar", "الفهم والاستيعاب")
            item.setdefault("bloom_name_en", "Understanding & Comprehension")
            item.setdefault("difficulty", question.get("difficulty", "medium"))
            item.setdefault("question_ar", question.get("prompt_ar", question.get("question", "")))
            item.setdefault("question_en", question.get("prompt_en", question.get("question_en", "")))
            item.setdefault("solution_walkthrough_ar", "")
            item.setdefault("solution_walkthrough_en", "")
            raw_options = item.get("options", [])
            if raw_options and isinstance(raw_options[0], dict):
                item["options_en"] = [opt.get("label_en", opt.get("text_en", "")) for opt in raw_options]
                item["options"] = [opt.get("label_ar", opt.get("text_ar", str(opt))) for opt in raw_options]
            questions.append(item)
    return questions


def _exam_questions(grade: int, term: int, *, db: Session):
    # Consult published curriculum content dynamically from database first
    published = _questions_for_scope(grade, term, db=db)
    if published:
        return published

    # Fallback to curated static assessment banks if curriculum content is pending publication
    if grade == 5 and term == 1:
        from backend.assessment_bank import ASSESSMENT_QUESTIONS
        return ASSESSMENT_QUESTIONS
    elif grade == 5 and term == 2:
        from backend.assessment_bank import ASSESSMENT_QUESTIONS_TERM2
        return ASSESSMENT_QUESTIONS_TERM2
    elif grade == 5 and term == 3:
        from backend.assessment_bank import ASSESSMENT_QUESTIONS_TERM3
        return ASSESSMENT_QUESTIONS_TERM3

    raise ApplicationError(404, "No published assessment content is available for this grade and term")

def get_adaptive_assessment(lesson_id: str, child_id=None, is_reviewer=False, *, db: Session, actor=None):
    """
    Retrieve adaptive flow-state questions categorized by Bloom's Taxonomy
    and progressive difficulty tiers (easy, medium, hard, challenge).
    Dynamically calibrates question flow, scaffolding hints, and targeted remediation based
    on learner's active mastery, knowledge gaps, and unresolved mistakes.
    """
    reviewer = bool(actor is not None and getattr(actor, "role", None) in {"admin", "tutor"}) and is_reviewer
    require_lesson(db, actor, lesson_id, child_id, is_reviewer=is_reviewer)
    raw_questions = get_adaptive_flow_questions(lesson_id)
    if not raw_questions:
        raise ApplicationError(404, "Assessment not available for this lesson")

    # If no child_id is provided, return default baseline flow
    if not child_id:
        return {
            "success": True,
            "lesson_id": lesson_id,
            "adaptive_questions": raw_questions if reviewer else learner_content(raw_questions),
            "adaptive_telemetry": {
                "calibrated_tier": "standard",
                "targeted_gaps_count": 0,
                "active_mistakes_count": 0,
                "hints_scaffolded": False,
                "adaptation_mode": "baseline_uncalibrated"
            }
        }

    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    active_mistakes = db.query(LearnerMistake).filter(
        LearnerMistake.child_id == child_id,
        LearnerMistake.is_resolved == False
    ).all()
    gaps = db.query(ConceptMastery).filter(
        ConceptMastery.child_id == child_id,
        ConceptMastery.is_gap == True
    ).all()
    recent_attempts = db.query(LearnerAttempt).filter(
        LearnerAttempt.child_id == child_id
    ).order_by(LearnerAttempt.created_at.desc()).limit(10).all()

    # 1. Calibrate mastery tier
    accuracy = (sum(1 for a in recent_attempts if a.is_correct) / len(recent_attempts)) if recent_attempts else None
    diagnostic_level = getattr(child, "diagnostic_level", "intermediate") if child else "intermediate"

    if (len(active_mistakes) >= 2) or (accuracy is not None and accuracy < 0.6) or (diagnostic_level == "beginner"):
        calibrated_tier = "foundation"
    elif (accuracy is not None and accuracy >= 0.8 and len(active_mistakes) == 0) or (diagnostic_level == "advanced"):
        calibrated_tier = "mastery"
    else:
        calibrated_tier = "standard"

    # 2. Extract gap keywords to target remediation
    gap_keywords = set()
    for g in gaps:
        if g.concept_name_ar:
            gap_keywords.add(g.concept_name_ar.strip())
        if g.concept_name_en:
            gap_keywords.add(g.concept_name_en.strip().lower())
    for m in active_mistakes:
        concept_val = getattr(m, "concept_name", None) or getattr(m, "concept", None)
        if concept_val:
            gap_keywords.add(concept_val.strip().lower())

    # 3. Partition questions by difficulty and gap relevance
    remediation_questions = []
    other_questions = []
    for q in raw_questions:
        q_copy = dict(q)
        q_text = (q_copy.get("question_ar", "") + " " + q_copy.get("question_en", "")).lower()
        is_gap_match = any(kw.lower() in q_text for kw in gap_keywords if len(kw) >= 3)
        if is_gap_match:
            q_copy["is_targeted_remediation"] = True
            remediation_questions.append(q_copy)
        else:
            q_copy["is_targeted_remediation"] = False
            other_questions.append(q_copy)

    # 4. Filter and sequence according to calibrated tier
    if calibrated_tier == "foundation":
        # Foundation: prioritize easy/medium, scaffold hints on all questions
        for q in other_questions + remediation_questions:
            if not q.get("hint_ar"):
                q["hint_ar"] = "تلميح: راجع نص الدرس وقواعده الأساسية بعناية."
            if not q.get("hint_en"):
                q["hint_en"] = "Hint: Review the foundational lesson text and rules carefully."
        easy_pool = [q for q in other_questions if q.get("difficulty") == "easy"]
        med_pool = [q for q in other_questions if q.get("difficulty") == "medium"]
        hard_pool = [q for q in other_questions if q.get("difficulty") in ("hard", "challenge")]
        adapted = remediation_questions + easy_pool + med_pool + hard_pool
    elif calibrated_tier == "mastery":
        # Mastery: prioritize medium/hard/challenge, test higher-order Bloom's skills
        med_pool = [q for q in other_questions if q.get("difficulty") == "medium"]
        hard_pool = [q for q in other_questions if q.get("difficulty") in ("hard", "challenge")]
        easy_pool = [q for q in other_questions if q.get("difficulty") == "easy"]
        adapted = remediation_questions + hard_pool + med_pool + easy_pool
    else:
        # Standard: progressive flow easy -> medium -> hard
        easy_pool = [q for q in other_questions if q.get("difficulty") == "easy"]
        med_pool = [q for q in other_questions if q.get("difficulty") == "medium"]
        hard_pool = [q for q in other_questions if q.get("difficulty") in ("hard", "challenge")]
        adapted = remediation_questions + easy_pool + med_pool + hard_pool

    return {
        "success": True,
        "lesson_id": lesson_id,
        "adaptive_questions": adapted if reviewer else learner_content(adapted),
        "adaptive_telemetry": {
            "calibrated_tier": calibrated_tier,
            "targeted_gaps_count": len(gaps),
            "active_mistakes_count": len(active_mistakes),
            "remediation_items_count": len(remediation_questions),
            "hints_scaffolded": calibrated_tier == "foundation",
            "adaptation_mode": "learner_mastery_calibrated"
        }
    }


def get_exam_simulation(grade: int=5, term: int=1, child_id=None, *, db: Session, actor=None):
    """
    Retrieve full-length official UAE Ministry of Education (MoE) practice exam.
    Includes 20-minute countdown limit, Bloom-tagged items, and marks weighting.
    """
    require_exam(db, actor, grade, term, child_id)
    questions = _exam_questions(grade, term, db=db)
    exam = get_official_exam_simulation(grade=grade, term=term, questions=questions)
    session_id = None
    if child_id:
        bank_hash = hashlib.sha256(json.dumps([(q.get("id"), q.get("correct_index")) for q in questions], sort_keys=True).encode()).hexdigest()
        session = AssessmentSession(child_id=child_id, grade=grade, term=term, bank_hash=bank_hash,
                                    expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=20))
        db.add(session)
        db.commit()
        session_id = session.id
    return {
        "success": True,
        "exam": exam,
        "session_id": session_id
    }


def submit_exam_simulation(payload: SubmitExamSimulationRequest, *, db: Session, actor=None):
    """
    Submit timed exam simulation. Evaluates answers server-side against pinned keys.
    Computes Bloom's Taxonomy mastery radar, generates detailed solution walkthroughs,
    and records results in student portfolio.
    """
    require_exam(db, actor, payload.grade, payload.term, payload.child_id)
    if payload.time_taken_seconds < 0:
        raise ApplicationError(422, "Invalid elapsed time")
    if payload.time_taken_seconds > 1200:
        raise ApplicationError(422, "Exam time limit exceeded")
    if payload.idempotency_key:
        prior = db.query(ExamSimulationResult).filter(ExamSimulationResult.idempotency_key == payload.idempotency_key).first()
        if prior:
            return {"success": True, "result_id": prior.id, "child_id": prior.child_id,
                    "grade": prior.grade, "term": prior.term, "time_taken_seconds": prior.time_taken_seconds,
                    "evaluation": {"percentage": prior.score_percentage, "correct_count": prior.correct_count,
                                    "total_questions": prior.total_questions}}
    child = db.query(ChildProfile).filter(ChildProfile.id == payload.child_id).first()
    if not child:
        raise ApplicationError(
            status_code=404,
            detail="Child profile not found."
        )

    questions = _exam_questions(payload.grade, payload.term, db=db)
    session = None
    if payload.session_id:
        session = db.query(AssessmentSession).filter(AssessmentSession.id == payload.session_id, AssessmentSession.child_id == payload.child_id).first()
        if not session or session.status != "active" or session.expires_at < datetime.datetime.utcnow():
            raise ApplicationError(409, "Assessment session has expired or is invalid")
        bank_hash = hashlib.sha256(json.dumps([(q.get("id"), q.get("correct_index")) for q in questions], sort_keys=True).encode()).hexdigest()
        if session.grade != payload.grade or session.term != payload.term or session.bank_hash != bank_hash:
            raise ApplicationError(409, "Assessment content changed; restart the exam")

    eval_result = evaluate_exam_submission(payload.answers, questions=questions)

    record = ExamSimulationResult(
        id=str(uuid.uuid4()),
        child_id=payload.child_id,
        grade=payload.grade,
        term=payload.term,
        score_percentage=eval_result["percentage"],
        correct_count=eval_result["correct_count"],
        total_questions=eval_result["total_questions"],
        time_taken_seconds=payload.time_taken_seconds,
        bloom_breakdown=json.dumps(eval_result["bloom_breakdown"]),
        item_responses=json.dumps(payload.answers),
        submitted_at=datetime.datetime.utcnow()
        ,idempotency_key=payload.idempotency_key
        ,session_id=session.id if session else None
    )
    if session:
        session.status = "completed"
        session.completed_at = datetime.datetime.utcnow()
    db.add(record)

    # Directly calibrate ConceptMastery from verified exam evaluation categories
    category_breakdown = eval_result.get("category_breakdown", {})
    mapping = {
        "comprehension": ("reading_fluency", "الطلاقة وفهم المقروء", "Reading Fluency & Comprehension", "reading"),
        "vocabulary": ("vocab_sports", "المفردات والدلالة اللغوية", "Curriculum Vocabulary & Roots", "vocabulary"),
        "grammar": ("syntax_nominal", "الجملة الاسمية (المبتدأ والخبر)", "Nominal Sentence (Mubtada & Khabar)", "grammar"),
        "orthography": ("ortho_taa_marbutah", "التاء المربوطة والهاء", "Taa Marbutah vs. Haa", "orthography")
    }
    for comp_key, (c_key, c_ar, c_en, cat) in mapping.items():
        if comp_key in category_breakdown:
            c_stat = category_breakdown[comp_key]
            tot = c_stat.get("total", 0)
            corr = c_stat.get("correct", 0)
            cm = db.query(ConceptMastery).filter(
                ConceptMastery.child_id == payload.child_id,
                ConceptMastery.concept_key == c_key
            ).first()
            if not cm:
                cm = ConceptMastery(
                    child_id=payload.child_id,
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
            cm.total_attempts += tot
            cm.correct_attempts += corr
            cm.mastery_percentage = round((cm.correct_attempts / cm.total_attempts) * 100.0, 1) if cm.total_attempts > 0 else 0.0
            cm.is_gap = (cm.mastery_percentage < 70.0)
            cm.last_practiced_at = datetime.datetime.now(datetime.UTC)

    db.commit()
    db.refresh(record)

    return {
        "success": True,
        "result_id": record.id,
        "child_id": payload.child_id,
        "child_name": child.name,
        "grade": payload.grade,
        "term": payload.term,
        "time_taken_seconds": payload.time_taken_seconds,
        "evaluation": eval_result
    }



def require_exam(db, actor, grade, term, child_id):
    if grade < 1 or grade > 12 or term not in (1, 2, 3):
        raise ApplicationError(404, "Exam not available for this grade and term")
    if child_id:
        child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
        if not child:
            raise ApplicationError(404, "Child profile not found")
    # Authorization is enforced against the requested learner rather than a
    # hardcoded demo lesson, allowing each curriculum edition to provide its
    # own assessment bank as it is imported.
    if actor is not None and child_id:
        from backend.modules.identity.access import require_child
        from backend.models import TermAccess
        require_child(db, actor, child_id)
        reviewer = bool(getattr(actor, "role", None) in ("admin", "tutor"))
        if not reviewer:
            demo_lesson = db.query(Lesson).filter(Lesson.grade == grade, Lesson.term == term, Lesson.is_first_chapter_demo == True).first()
            if not demo_lesson:
                access = db.query(TermAccess).filter_by(child_id=child_id, grade=grade, term=term, is_unlocked=True).first()
                if access is None:
                    raise ApplicationError(402, "This term is locked. Unlock it to continue.")
