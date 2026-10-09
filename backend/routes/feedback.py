import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import UserFeedback
from backend.schemas import UserFeedbackCreate, UserFeedbackResponse
from backend.api.dependencies import get_optional_user, get_current_user
from backend.modules.identity.access import Principal, require_roles

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("", response_model=UserFeedbackResponse)
def submit_feedback(
    payload: UserFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Optional[Principal] = Depends(get_optional_user),
):
    """Submit user feedback, feature suggestions, bug reports, or content reviews."""
    if not payload.comment or not payload.comment.strip():
        raise HTTPException(status_code=400, detail="Feedback comment cannot be empty.")

    feedback_id = str(uuid.uuid4())
    feedback = UserFeedback(
        id=feedback_id,
        user_id=current_user.id if current_user else None,
        child_id=payload.child_id,
        rating=max(1, min(5, payload.rating)),
        category=payload.category or "general",
        comment=payload.comment.strip(),
        contact_email=payload.contact_email or (getattr(current_user, 'email', None) if current_user else None),
        grade=payload.grade or 5,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(feedback)
    db.commit()

    return UserFeedbackResponse(
        success=True,
        message="شكرًا لمشاركتك القيّمة! تم استلام ملاحظاتك بنجاح وسنعمل على تطوير التجربة التعليمية.",
        feedback_id=feedback_id,
    )


@router.get("")
def list_feedbacks(
    category: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    actor: Principal = Depends(get_current_user),
):
    """Retrieve submitted feedbacks for administrative and continuous quality improvement."""
    require_roles(actor, ("admin", "school_admin"))
    query = db.query(UserFeedback).order_by(UserFeedback.created_at.desc())
    if category:
        query = query.filter(UserFeedback.category == category)
    items = query.limit(limit).all()

    return [
        {
            "id": f.id,
            "user_id": f.user_id,
            "child_id": f.child_id,
            "rating": f.rating,
            "category": f.category,
            "comment": f.comment,
            "contact_email": f.contact_email,
            "grade": f.grade,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in items
    ]
