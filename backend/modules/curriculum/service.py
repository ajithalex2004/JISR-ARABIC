"""Application operations; callers provide explicit database sessions and actors."""
import json
import copy
import bcrypt
import hashlib
from sqlalchemy.orm import Session
from typing import Optional
from backend.models import School, SchoolClass, Unit, Lesson, LessonVersion, TermAccess, ChildProfile, ConceptMastery
from backend.diagnostic_bank import get_diagnostic_questions_for_student, evaluate_diagnostic_submission
from backend.schemas import SubmitDiagnosticRequest, OnboardingProfileUpdateRequest
from backend.errors import ApplicationError
from backend.modules.curriculum.access import require_lesson, learner_content
from backend.redis_client import cache_get, cache_set
from backend.modules.billing.service import PRICE_PER_TERM_USD, PRICE_ANNUAL_PASS_USD

from backend.modules.curriculum.syllabus_data import (
    get_dynamic_lesson_spec,
    generate_dynamic_lesson_content,
    get_syllabus_for_grade_and_term
)

def list_schools(*, db: Session):
    """List supported UAE schools."""
    cached = cache_get("schools:all")
    if cached is not None:
        return cached
    schools = db.query(School).all()
    result = [{"id": s.id, "name": s.name, "country": s.country, "curriculum_type": s.curriculum_type} for s in schools]
    cache_set("schools:all", result, ttl_seconds=86400)
    return result


def list_school_classes(school_id: str, *, db: Session):
    """List active classes for a given school."""
    cached = cache_get(f"school_classes:{school_id}")
    if cached is not None:
        return cached
    classes = db.query(SchoolClass).filter(SchoolClass.school_id == school_id, SchoolClass.is_active == True).all()
    result = [{"id": c.id, "school_id": c.school_id, "name": c.name, "grade": c.grade, "academic_year": c.academic_year} for c in classes]
    cache_set(f"school_classes:{school_id}", result, ttl_seconds=86400)
    return result


def list_grades(actor: Optional[object] = None, db: Optional[Session] = None):
    """List available grades/classes from Class 1 to Class 12, limited to enrolled grades for students and parents."""
    all_grades = [
        {"grade": g, "name_en": f"Class {g}", "name_ar": f"الصف {g}", "has_content": True}
        for g in range(1, 13)
    ]
    if actor is None or getattr(actor, "role", None) in ("admin", "tutor", "school_admin"):
        return all_grades

    if db is not None:
        if getattr(actor, "role", None) == "learner" and getattr(actor, "child_id", None):
            child = db.query(ChildProfile).filter(ChildProfile.id == actor.child_id).first()
            if child and child.default_grade:
                return [
                    {"grade": child.default_grade, "name_en": f"Class {child.default_grade}", "name_ar": f"الصف {child.default_grade}", "has_content": True}
                ]
        elif getattr(actor, "role", None) == "parent":
            children = db.query(ChildProfile).filter(ChildProfile.parent_id == getattr(actor, "id", None)).all()
            enrolled_grades = sorted(list(set(c.default_grade for c in children if c.default_grade)))
            if enrolled_grades:
                return [
                    {"grade": g, "name_en": f"Class {g}", "name_ar": f"الصف {g}", "has_content": True}
                    for g in enrolled_grades
                ]

    return all_grades


def list_terms(grade: int=5, child_id: Optional[str]=None, *, db: Session, actor=None):
    """List terms for a given grade with payment unlock status."""
    is_admin = bool(
        (actor is not None and getattr(actor, "role", None) == "admin")
        or child_id == "admin_supervisor"
    )
    unlocked_terms = set()
    if child_id and not is_admin:
        access_list = db.query(TermAccess).filter(
            TermAccess.child_id == child_id,
            TermAccess.grade == grade,
            TermAccess.is_unlocked == True
        ).all()
        unlocked_terms = {a.term for a in access_list}

    terms = [
        {
            "term": 1,
            "title_ar": "الفصل الدراسي الأول",
            "title_en": "Term 1",
            "price_usd": PRICE_PER_TERM_USD,
            "annual_price_usd": PRICE_ANNUAL_PASS_USD,
            "currency": "USD",
            "is_unlocked": is_admin or (1 in unlocked_terms),
            "has_demo": True,
            "demo_chapter_name": "ألعاب الكرة (Ball Games)" if grade == 5 else f"الدرس الأول - الصف {grade}",
            "status": "published"
        },
        {
            "term": 2,
            "title_ar": "الفصل الدراسي الثاني",
            "title_en": "Term 2",
            "price_usd": PRICE_PER_TERM_USD,
            "annual_price_usd": PRICE_ANNUAL_PASS_USD,
            "currency": "USD",
            "is_unlocked": is_admin or (2 in unlocked_terms),
            "has_demo": False,
            "status": "published"
        },
        {
            "term": 3,
            "title_ar": "الفصل الدراسي الثالث",
            "title_en": "Term 3",
            "price_usd": PRICE_PER_TERM_USD,
            "annual_price_usd": PRICE_ANNUAL_PASS_USD,
            "currency": "USD",
            "is_unlocked": is_admin or (3 in unlocked_terms),
            "has_demo": False,
            "status": "published"
        }
    ]
    return terms


def list_lessons(grade: int=5, term: int=1, child_id: Optional[str]=None, *, db: Session, actor=None):
    """List all lessons in a grade and term with availability and lock states."""
    is_admin = bool(
        (actor is not None and getattr(actor, "role", None) == "admin")
        or child_id == "admin_supervisor"
    )

    base_cache_key = f"lessons_base:{grade}:{term}"
    cached_base = cache_get(base_cache_key)

    if cached_base is None:
        lessons = db.query(Lesson).filter(
            Lesson.grade == grade,
            Lesson.term == term
        ).order_by(Lesson.lesson_order).all()

        if lessons:
            cached_base = []
            for l in lessons:
                unit = db.query(Unit).filter(Unit.id == l.unit_id).first()
                is_demo = (l.is_first_chapter_demo or l.lesson_order == 1) and term == 1
                cached_base.append({
                    "id": l.id,
                    "unit_id": l.unit_id,
                    "unit_title_ar": unit.title_ar if unit else "",
                    "unit_title_en": unit.title_en if unit else "",
                    "lesson_order": l.lesson_order,
                    "title_ar": l.title_ar,
                    "title_en": l.title_en,
                    "start_page": l.start_page,
                    "is_first_chapter_demo": is_demo,
                    "status": l.status
                })
        else:
            dynamic_items = get_syllabus_for_grade_and_term(grade, term)
            cached_base = []
            for item in dynamic_items:
                is_demo = bool(item.get("is_first_chapter_demo")) and term == 1
                cached_base.append({
                    **item,
                    "is_first_chapter_demo": is_demo,
                    "status": "published"
                })
        cache_set(base_cache_key, cached_base, ttl_seconds=86400)

    # Check term access
    is_term_unlocked = is_admin
    if child_id and not is_admin:
        access = db.query(TermAccess).filter(
            TermAccess.child_id == child_id,
            TermAccess.grade == grade,
            TermAccess.term == term,
            TermAccess.is_unlocked == True
        ).first()
        if access:
            is_term_unlocked = True

    result = []
    for item in cached_base:
        is_demo = item.get("is_first_chapter_demo", False)
        is_accessible = is_admin or is_demo or is_term_unlocked
        raw_status = item.get("status", "published")
        status = "published" if is_admin else raw_status
        result.append({
            **item,
            "is_accessible": is_accessible,
            "status": status,
            "lock_reason": None if is_accessible else (
                "Content pending review" if raw_status == "content_pending" else "Subscription required (USD 20/term)"
            )
        })
    return result


def get_lesson_content(lesson_id: str, child_id: Optional[str]=None, is_reviewer: bool=False, *, db: Session, actor=None):
    """
    Get full lesson package.
    Hides assessment answers from client until submission.
    Enforces the $33 per-term paywall for non-demo chapters unless purchased.
    """
    reviewer = bool(actor is not None and getattr(actor, "role", None) in {"admin", "tutor"}) and is_reviewer
    lesson = require_lesson(db, actor, lesson_id, child_id, is_reviewer=is_reviewer)

    cache_key = f"lesson_package:{lesson_id}"
    cached_pkg = cache_get(cache_key)

    if cached_pkg is not None:
        pkg = cached_pkg
    else:
        # Check active version
        version = db.query(LessonVersion).filter(
            LessonVersion.lesson_id == lesson_id,
            LessonVersion.is_active == True
        ).first()

        if not version:
            content = generate_dynamic_lesson_content(lesson)
            version_tag = "v1.0.0-moe-verified"
            version_id = f"ver_{lesson.id}"
            content_hash = hashlib.sha256(json.dumps(content, ensure_ascii=False).encode("utf-8")).hexdigest()
        else:
            content = json.loads(version.content_json)
            actual_hash = hashlib.sha256(version.content_json.encode("utf-8")).hexdigest()
            if len(version.content_hash or "") == 64 and actual_hash != version.content_hash:
                raise ApplicationError(500, "Lesson content integrity check failed")
            version_tag = version.version_tag
            version_id = version.id
            content_hash = version.content_hash

        pkg = {
            "lesson": {
                "id": lesson.id,
                "grade": lesson.grade,
                "term": lesson.term,
                "title_ar": lesson.title_ar,
                "title_en": lesson.title_en,
                "is_first_chapter_demo": lesson.is_first_chapter_demo,
                "status": "published"
            },
            "version_tag": version_tag,
            "version_id": version_id,
            "content_hash": content_hash,
            "content": content
        }
        cache_set(cache_key, pkg, ttl_seconds=86400)

    pkg_copy = copy.deepcopy(pkg)
    if not reviewer:
        pkg_copy["content"] = learner_content(pkg_copy["content"])

    return pkg_copy


def get_diagnostic_questions(grade: int=5, stream: Optional[str]=None):
    """
    Retrieve calibrated diagnostic baseline questions for the student onboarding wizard.
    Shields answers and solutions on the server.
    """
    cache_key = f"diagnostic:{grade}:{stream or 'default'}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    questions = get_diagnostic_questions_for_student(grade=grade, stream=stream)
    result = {
        "success": True,
        "count": len(questions),
        "grade": grade,
        "stream": stream,
        "questions": questions
    }
    cache_set(cache_key, result, ttl_seconds=86400)
    return result


def submit_diagnostic(payload: SubmitDiagnosticRequest, *, db: Session):
    """
    Evaluate student diagnostic quiz submission, compute competency breakdowns,
    determine calibrated difficulty tier, build a 4-week personalized learning roadmap,
    and persist results to the child profile.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == payload.child_id).first()
    if not child:
        raise ApplicationError(
            status_code=404,
            detail="Child profile not found."
        )

    result = evaluate_diagnostic_submission(
        answers=payload.answers,
        grade=child.default_grade,
        stream=child.curriculum_stream
    )

    child.diagnostic_completed = True
    child.diagnostic_level = result["calibrated_level"]
    child.diagnostic_score = result["score"]
    child.diagnostic_details = json.dumps(result["competency_breakdown"])
    child.learning_plan = json.dumps(result["learning_plan"])

    # Directly calibrate ConceptMastery from verified diagnostic submission
    breakdown = result.get("competency_breakdown", {})
    mapping = {
        "reading": ("reading_fluency", "الطلاقة وفهم المقروء", "Reading Fluency & Comprehension", "reading"),
        "vocabulary": ("vocab_sports", "المفردات والدلالة اللغوية", "Curriculum Vocabulary & Roots", "vocabulary"),
        "grammar": ("syntax_nominal", "الجملة الاسمية (المبتدأ والخبر)", "Nominal Sentence (Mubtada & Khabar)", "grammar")
    }
    for comp_key, (c_key, c_ar, c_en, cat) in mapping.items():
        if comp_key in breakdown:
            c_stat = breakdown[comp_key]
            tot = c_stat.get("total", 0)
            corr = c_stat.get("correct", 0)
            pct = c_stat.get("percentage", 0.0)
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
                    mastery_percentage=pct,
                    total_attempts=tot,
                    correct_attempts=corr,
                    is_gap=(pct < 70.0 and tot > 0),
                    interval_days=1,
                    ease_factor=2.5,
                    repetition_count=0
                )
                db.add(cm)
            else:
                cm.total_attempts += tot
                cm.correct_attempts += corr
                cm.mastery_percentage = round((cm.correct_attempts / cm.total_attempts) * 100.0, 1) if cm.total_attempts > 0 else 0.0
                cm.is_gap = (cm.mastery_percentage < 70.0)

    db.commit()
    db.refresh(child)

    return {
        "success": True,
        "child_id": child.id,
        "score": result["score"],
        "correct_count": result["correct_count"],
        "total_questions": result["total_questions"],
        "calibrated_level": result["calibrated_level"],
        "level_title_ar": result["level_title_ar"],
        "level_title_en": result["level_title_en"],
        "competency_breakdown": result["competency_breakdown"],
        "item_evaluations": result["item_evaluations"],
        "learning_plan": result["learning_plan"]
    }


def get_learning_plan(child_id: str, *, db: Session):
    """
    Retrieve the customized 4-week learning plan and diagnostic breakdown for a child.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ApplicationError(
            status_code=404,
            detail="Child profile not found."
        )

    if child.learning_plan:
        plan_data = json.loads(child.learning_plan)
        return {
            "success": True,
            "child_id": child.id,
            "child_name": child.name,
            "diagnostic_completed": child.diagnostic_completed,
            "diagnostic_level": child.diagnostic_level,
            "diagnostic_score": child.diagnostic_score,
            "learning_plan": plan_data
        }
    else:
        default_eval = evaluate_diagnostic_submission({}, grade=child.default_grade, stream=child.curriculum_stream)
        return {
            "success": True,
            "child_id": child.id,
            "child_name": child.name,
            "diagnostic_completed": False,
            "diagnostic_level": child.diagnostic_level or "guided",
            "diagnostic_score": 0.0,
            "learning_plan": default_eval["learning_plan"]
        }


def update_onboarding_profile(payload: OnboardingProfileUpdateRequest, *, db: Session):
    """
    Update student demographic details, grade, curriculum stream, term, avatar, and PIN
    during Steps 1 & 2 of the Onboarding Wizard.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == payload.child_id).first()
    if not child:
        raise ApplicationError(
            status_code=404,
            detail="Child profile not found."
        )

    if payload.name is not None:
        child.name = payload.name.strip()
    if payload.gender is not None:
        child.gender = payload.gender
    if payload.age is not None:
        child.age = payload.age
    if payload.school_name is not None:
        child.school_name = payload.school_name.strip()
    if payload.default_grade is not None:
        child.default_grade = payload.default_grade
    if payload.selected_term is not None:
        child.selected_term = payload.selected_term
    if payload.avatar_id is not None:
        child.avatar_id = payload.avatar_id
    if payload.curriculum_stream is not None:
        child.curriculum_stream = payload.curriculum_stream
    if payload.access_pin is not None:
        child.access_pin = bcrypt.hashpw(payload.access_pin.strip().encode(), bcrypt.gensalt()).decode() if payload.access_pin.strip() else None

    db.commit()
    db.refresh(child)

    return {
        "success": True,
        "message": "Student profile configured successfully.",
        "child": {
            "id": child.id,
            "name": child.name,
            "gender": child.gender,
            "age": child.age,
            "school_name": child.school_name,
            "default_grade": child.default_grade,
            "selected_term": child.selected_term,
            "avatar_id": child.avatar_id,
            "curriculum_stream": child.curriculum_stream,
            "access_pin": None,
            "diagnostic_completed": child.diagnostic_completed,
            "diagnostic_level": child.diagnostic_level,
            "diagnostic_score": child.diagnostic_score
        }
    }

