from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.dependencies import get_current_user
from backend.modules.identity.access import Principal, require_child, require_mistake, FAMILY_ROLES
"""HTTP adapter: request parsing, dependency injection, and service delegation."""
from fastapi import APIRouter, Depends
from backend.schemas import AttemptSubmitRequest, AttemptSubmitResponse
from backend.modules.assessment import attempts as service
router = APIRouter(prefix='/api/attempts', tags=['Attempts & Scoring'])

@router.post('/submit', response_model=AttemptSubmitResponse)
def submit_attempt(req: AttemptSubmitRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Submits a learner attempt for an activity.
    Strictly evaluated on the server using pinned answer key. Client-supplied score is ignored.
    """
    require_child(db, actor, req.child_id, FAMILY_ROLES)
    return service.submit_attempt(req=req, db=db, actor=actor)

@router.get('/mistakes')
def get_mistake_notebook(child_id: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """Fetch private mistake notebook entries for targeted re-practice."""
    require_child(db, actor, child_id)
    return service.get_mistake_notebook(child_id=child_id, db=db)

@router.post('/mistakes/{mistake_id}/resolve')
def resolve_mistake(mistake_id: int, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """Mark a mistake entry as reviewed and resolved."""
    require_mistake(db, actor, mistake_id)
    return service.resolve_mistake(mistake_id=mistake_id, db=db)
