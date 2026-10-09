from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.dependencies import get_current_user
from backend.modules.identity.access import Principal, require_child, require_roles, require_submission, FAMILY_ROLES, STAFF_ROLES
"""HTTP adapter: request parsing, dependency injection, and service delegation."""
from fastapi import APIRouter, Depends
from backend.schemas import TutorSubmissionRequest, TutorReviewRequest
from backend.modules.tutoring import service as service
router = APIRouter(prefix='/api/tutor', tags=['Tutor Queue & Rubric'])

@router.post('/submit')
def submit_for_tutor(req: TutorSubmissionRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """Student submits writing or speaking audio for tutor review."""
    require_child(db, actor, req.child_id, FAMILY_ROLES)
    return service.submit_for_tutor(req=req, db=db)

@router.get('/queue')
def get_tutor_queue(status_filter: str='pending', db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """Tutor work queue displaying pending and reviewed student submissions."""
    require_roles(actor, STAFF_ROLES)
    return service.get_tutor_queue(status_filter=status_filter, db=db, actor=actor)

@router.post('/review')
def review_submission(req: TutorReviewRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """Assigned tutor grades and provides feedback on student writing or audio."""
    require_submission(db, actor, req.submission_id)
    return service.review_submission(req=req, db=db, actor=actor)

@router.get('/submissions/{child_id}')
def get_child_submissions(child_id: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """Fetch all submissions and tutor feedback for a specific child."""
    require_child(db, actor, child_id)
    return service.get_child_submissions(child_id=child_id, db=db)
