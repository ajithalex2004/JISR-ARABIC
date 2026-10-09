from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.dependencies import get_current_user, get_optional_user
from backend.modules.identity.access import Principal, require_child, optional_child, FAMILY_ROLES
"""HTTP adapter: request parsing, dependency injection, and service delegation."""
from fastapi import APIRouter, Depends, Query
from backend.schemas import CapsuleCompleteRequest, SubmitExamSimulationRequest
from backend.modules.curriculum import learning as service
from backend.modules.assessment import exams
router = APIRouter(prefix='/api/modules', tags=['Core Learning & Tutoring Modules'])

@router.get('/malazim')
def get_malazim_default(
    grade: Optional[int] = Query(None),
    lesson_id: Optional[str] = Query(None),
    child_id: Optional[str] = None,
    is_reviewer: bool = False,
    db: Session = Depends(get_db),
    actor: Optional[Principal] = Depends(get_optional_user)
):
    """
    Retrieve interactive study booklet by grade or lesson.
    Defaults to the requested grade or Grade 5.
    """
    lid = lesson_id or (f"grade_{grade}" if grade else "lesson_01_ball_games")
    return service.get_malazim(lesson_id=lid, child_id=child_id, is_reviewer=is_reviewer, db=db, actor=actor)

@router.get('/malazim/{lesson_id}')
def get_malazim(lesson_id: str, child_id: Optional[str]=None, is_reviewer: bool=False, db: Session=Depends(get_db), actor: Optional[Principal]=Depends(get_optional_user)):
    """
    Retrieve interactive study booklet for a lesson.
    Contains both:
    - Study Mode (وضع المذاكرة الشامل مع التمارين التفاعلية)
    - Notes / Quick Review Mode (وضع الملاحظات المركزة ومراجعة الـ 15 دقيقة)
    """
    return service.get_malazim(lesson_id=lesson_id, child_id=child_id, is_reviewer=is_reviewer, db=db, actor=actor)

@router.get('/capsules')
def list_capsules(
    child_id: Optional[str] = Query(None),
    grade: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    actor: Optional[Principal] = Depends(get_optional_user)
):
    """
    List all 3-to-5 minute bite-sized microlearning capsules.
    Optionally filtered by student grade (Grade 5 or Grade 6).
    """
    optional_child(db, actor, child_id)
    return service.list_capsules(child_id=child_id, grade=grade, db=db)

@router.get('/capsules/{capsule_id}')
def get_capsule(capsule_id: str):
    """Retrieve full content, audio script, and checkpoint quiz for a capsule."""
    return service.get_capsule(capsule_id=capsule_id)

@router.post('/capsules/{capsule_id}/complete')
def complete_capsule(capsule_id: str, payload: CapsuleCompleteRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Record that a student successfully completed a microlearning capsule,
    recording score, duration, and awarding progress.
    """
    require_child(db, actor, payload.child_id, FAMILY_ROLES)
    return service.complete_capsule(capsule_id=capsule_id, payload=payload, db=db)

@router.get('/assessments/adaptive/{lesson_id}')
def get_adaptive_assessment(lesson_id: str, child_id: Optional[str]=None, is_reviewer: bool=False, db: Session=Depends(get_db), actor: Optional[Principal]=Depends(get_optional_user)):
    """
    Retrieve adaptive flow-state questions categorized by Bloom's Taxonomy
    and progressive difficulty tiers (easy, medium, hard, challenge).
    """
    return exams.get_adaptive_assessment(lesson_id=lesson_id, child_id=child_id, is_reviewer=is_reviewer, db=db, actor=actor)

@router.get('/assessments/exam-simulation/{grade}/{term}')
def get_exam_simulation(grade: int=5, term: int=1, child_id: Optional[str]=None, db: Session=Depends(get_db), actor: Optional[Principal]=Depends(get_optional_user)):
    """
    Retrieve full-length official UAE Ministry of Education (MoE) practice exam.
    Includes 20-minute countdown limit, Bloom-tagged items, and marks weighting.
    """
    return exams.get_exam_simulation(grade=grade, term=term, child_id=child_id, db=db, actor=actor)

@router.post('/assessments/submit-exam')
def submit_exam_simulation(payload: SubmitExamSimulationRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Submit timed exam simulation. Evaluates answers server-side against pinned keys.
    Computes Bloom's Taxonomy mastery radar, generates detailed solution walkthroughs,
    and records results in student portfolio.
    """
    require_child(db, actor, payload.child_id, FAMILY_ROLES)
    return exams.submit_exam_simulation(payload=payload, db=db, actor=actor)


from pydantic import BaseModel, StrictInt

class BookletAnswer(BaseModel):
    section_id: str
    answer: StrictInt
    child_id: Optional[str] = None

@router.post('/malazim/{lesson_id}/check')
def check_booklet_answer(lesson_id: str, payload: BookletAnswer, db: Session=Depends(get_db), actor: Optional[Principal]=Depends(get_optional_user)):
    return service.check_booklet_answer(lesson_id, payload, db=db, actor=actor)


class SentenceAnswer(BaseModel):
    activity_id: str
    answer: str
    child_id: Optional[str] = None

@router.post('/sentences/{lesson_id}/check')
def check_sentence(lesson_id: str, payload: SentenceAnswer, db: Session=Depends(get_db), actor: Optional[Principal]=Depends(get_optional_user)):
    return service.check_sentence(lesson_id, payload, db=db, actor=actor)
