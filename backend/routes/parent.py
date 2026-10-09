from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.dependencies import get_current_user
from backend.modules.identity.access import Principal, require_child, PARENT_ROLES
"""HTTP adapter: request parsing, dependency injection, and service delegation."""
from fastapi import APIRouter, Depends
from backend.schemas import WeeklyDigestResponse, SendWeeklyDigestRequest, SendWeeklyDigestResponse, ActionableGuidanceResponse
from backend.modules.progress import reporting as service
router = APIRouter(prefix='/api/parent', tags=['Parent Dashboard'])

@router.get('/dashboard/{child_id}')
def get_parent_dashboard(child_id: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Evidence-based parent dashboard.
    Shows honest skill breakdown and missing curriculum coverage.
    """
    require_child(db, actor, child_id, PARENT_ROLES)
    return service.get_parent_dashboard(child_id=child_id, db=db)

@router.get('/weekly-digest/{child_id}', response_model=WeeklyDigestResponse)
def get_weekly_digest(child_id: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Returns a concise weekly digest summarizing study minutes, completed capsules,
    quiz scores, active knowledge gaps, and plain-English guidance tips.
    """
    require_child(db, actor, child_id, PARENT_ROLES)
    return service.get_weekly_digest(child_id=child_id, db=db)

@router.post('/send-digest/{child_id}', response_model=SendWeeklyDigestResponse)
def send_weekly_digest(child_id: str, req: SendWeeklyDigestRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Simulates sending the Weekly Digest via in-app notification or registered parent email.
    """
    require_child(db, actor, child_id, PARENT_ROLES)
    return service.send_weekly_digest(child_id=child_id, req=req, db=db)

@router.post('/send-digest-async/{child_id}')
def send_weekly_digest_async(
    child_id: str,
    req: SendWeeklyDigestRequest,
    db: Session = Depends(get_db),
    actor: Principal = Depends(get_current_user)
):
    """
    Asynchronously enqueue weekly digest generation and email delivery via background task worker.
    """
    require_child(db, actor, child_id, PARENT_ROLES)
    from backend.tasks.queue import enqueue_task
    task = enqueue_task(
        task_type="send_weekly_digest",
        params={
            "child_id": child_id,
            "channel": req.channel,
            "recipient_email": req.recipient_email
        },
        actor_id=actor.id
    )
    return {
        "task_id": task.id,
        "status": task.status,
        "poll_url": f"/api/tasks/{task.id}"
    }

@router.get('/actionable-guidance/{child_id}', response_model=ActionableGuidanceResponse)
def get_actionable_guidance(child_id: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Actionable guidance designed explicitly for non-Arabic speaking parents.
    Provides plain-English speaking suggestions, household games, and praise points.
    """
    require_child(db, actor, child_id, PARENT_ROLES)
    return service.get_actionable_guidance(child_id=child_id, db=db)
