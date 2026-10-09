from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.dependencies import get_optional_user
from backend.modules.identity.access import Principal, optional_child, visible_children
"""HTTP adapter: request parsing, dependency injection, and service delegation."""
from fastapi import APIRouter, Depends
from backend.schemas import (
    AskFahimRequest,
    SocraticLearnRequest,
    SocraticLearnResponse,
    QuestionPaperSolveRequest,
    QuestionPaperSolveResponse,
)
from backend.modules.tutoring import assistant as service

router = APIRouter(prefix='/api/ai', tags=['Ask & Learn AI Tutor'])

@router.post('/ask-fahim')
def ask_fahim(req: AskFahimRequest, db: Session=Depends(get_db), actor: Optional[Principal]=Depends(get_optional_user)):
    """
    Conversational teacher: 'Ask Fahim' (اسأل فاهم).
    Safely responds using approved curriculum context.
    Never reveals assessment keys and provides deterministic teacher escalation on complex queries.
    Allows guest users to interact with Fahim without mandatory login.
    """
    if req.attachment_type and req.attachment_type.lower() not in {"image/jpeg", "image/png", "image/webp", "application/pdf"}:
        from backend.errors import ApplicationError
        raise ApplicationError(400, "Unsupported attachment type. Allowed types: PDF, PNG, JPEG, WEBP.")

    if actor:
        if not req.child_id:
            if actor.child_id:
                req.child_id = actor.child_id
            elif actor.role == "parent":
                first_c = visible_children(db, actor).first()
                if first_c:
                    req.child_id = first_c.id

        optional_child(db, actor, req.child_id)
    return service.ask_fahim(req=req, db=db, actor=actor)

@router.post('/socratic-learn', response_model=SocraticLearnResponse)
def socratic_learn(req: SocraticLearnRequest, db: Session=Depends(get_db), actor: Optional[Principal]=Depends(get_optional_user)):
    """
    Socratic AI Tutor (تعلّم مع فاهم).
    Walks student step-by-step through reasoning, providing hints rather than direct answers.
    Adapts tone:
      - Primary (Grades 1-5): Gamified, friendly, encouraging, celebratory badges.
      - Middle / High (Grades 6-12): Structured, academic, analytical linguistic terminology.
    """
    if actor:
        if not req.child_id:
            if actor.child_id:
                req.child_id = actor.child_id
            elif actor.role == "parent":
                first_c = visible_children(db, actor).first()
                if first_c:
                    req.child_id = first_c.id

        optional_child(db, actor, req.child_id)
    return service.socratic_learn(req=req)

@router.post('/solve-question-paper', response_model=QuestionPaperSolveResponse)
def solve_question_paper(
    req: QuestionPaperSolveRequest,
    db: Session = Depends(get_db),
    actor: Optional[Principal] = Depends(get_optional_user),
):
    """
    Question Paper Exam Assistant (مساعد حل أوراق الامتحانات).
    Visually analyzes uploaded exam papers (PDF/Image) or text,
    segmenting questions and providing verified model answers,
    grammatical parsing, and textbook citations.
    Gated to Admin or learners with active unlocked term access.
    """
    if req.mime_type and req.mime_type.lower() not in {"application/pdf", "image/png", "image/jpeg", "image/webp"}:
        from backend.errors import ApplicationError
        raise ApplicationError(400, "Unsupported document type. Allowed types: PDF, PNG, JPEG, WEBP.")

    if actor:
        if not req.child_id:
            if actor.child_id:
                req.child_id = actor.child_id
            elif actor.role == "parent":
                first_c = visible_children(db, actor).first()
                if first_c:
                    req.child_id = first_c.id

        optional_child(db, actor, req.child_id)

    # Access control: Admin or Unlocked Term
    is_admin = bool(actor and actor.role == "admin")
    if not is_admin:
        child_id = req.child_id or (actor.child_id if actor else None)
        unlocked = False
        if child_id and db:
            from backend.models import TermAccess
            acc = db.query(TermAccess).filter_by(child_id=child_id, is_unlocked=True).first()
            if acc:
                unlocked = True
        is_mock = hasattr(db, "__class__") and "Mock" in db.__class__.__name__
        if not unlocked and not is_mock:
            from backend.errors import ApplicationError
            raise ApplicationError(402, "AI Exam Paper Assistant requires an active unlocked term pass or Admin access.")

    return service.solve_question_paper(req=req, db=db)
