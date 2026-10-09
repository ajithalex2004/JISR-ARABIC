from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.dependencies import get_current_user
from backend.modules.identity.access import Principal, require_child, FAMILY_ROLES
"""HTTP adapter: request parsing, dependency injection, and service delegation."""
from fastapi import APIRouter, Depends
from backend.schemas import MasteryHeatmapResponse, GapReviewSessionResponse, RecordDrillAnswerRequest, RecordDrillAnswerResponse
from backend.modules.progress import mastery as service
router = APIRouter(prefix='/api/mastery', tags=['Mastery & Knowledge Gaps'])

@router.get('/heatmap/{child_id}', response_model=MasteryHeatmapResponse)
def get_mastery_heatmap(child_id: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Returns real-time concept mastery percentages, color-coded heatmap data,
    and isolates persistent knowledge gaps.
    """
    require_child(db, actor, child_id)
    return service.get_mastery_heatmap(child_id=child_id, db=db)

@router.get('/review-session/{child_id}', response_model=GapReviewSessionResponse)
def get_gap_review_session(child_id: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Automatically creates a personalized review session targeting the child's
    active knowledge gaps using spaced-repetition methodology.
    """
    require_child(db, actor, child_id)
    return service.get_gap_review_session(child_id=child_id, db=db)

@router.post('/record-drill', response_model=RecordDrillAnswerResponse)
def record_drill_answer(req: RecordDrillAnswerRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Records an answer in the gap recovery drill, recalibrates mastery percentage,
    clears knowledge gaps if proficiency threshold is met, and awards XP.
    """
    require_child(db, actor, req.child_id, FAMILY_ROLES)
    return service.record_drill_answer(req=req, db=db)
