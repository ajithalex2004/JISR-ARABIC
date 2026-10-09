"""Application operations; callers provide explicit database sessions and actors."""
import uuid
import datetime
from sqlalchemy.orm import Session
from backend.models import TutorSubmission, ChildProfile
from backend.schemas import TutorSubmissionRequest, TutorReviewRequest
from backend.errors import ApplicationError
from backend.modules.identity.access import visible_children, require_roles, require_submission, STAFF_ROLES

def submit_for_tutor(req: TutorSubmissionRequest, *, db: Session):
    """Student submits writing or speaking audio for tutor review."""
    child = db.query(ChildProfile).filter(ChildProfile.id == req.child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")

    submission = TutorSubmission(
        id=str(uuid.uuid4()),
        child_id=child.id,
        lesson_id=req.lesson_id,
        activity_id=req.activity_id,
        submission_type=req.submission_type,
        content_text=req.content_text,
        audio_url=req.audio_url,
        status="pending"
    )
    db.add(submission)
    db.commit()

    return {
        "success": True,
        "submission_id": submission.id,
        "message": "Submission routed to tutor queue successfully."
    }


def get_tutor_queue(status_filter: str='pending', *, actor, db: Session):
    """Tutor work queue displaying pending and reviewed student submissions."""
    require_roles(actor, STAFF_ROLES)
    query = db.query(TutorSubmission).filter(TutorSubmission.child_id.in_(visible_children(db, actor).with_entities(ChildProfile.id)))
    if status_filter != "all":
        query = query.filter(TutorSubmission.status == status_filter)
    
    submissions = query.order_by(TutorSubmission.created_at.desc()).all()

    results = []
    for s in submissions:
        child = db.query(ChildProfile).filter(ChildProfile.id == s.child_id).first()
        results.append({
            "id": s.id,
            "child_name": child.name if child else "Student",
            "school_name": child.school_name if child else "",
            "grade": child.default_grade if child else 5,
            "lesson_id": s.lesson_id,
            "activity_id": s.activity_id,
            "submission_type": s.submission_type,
            "content_text": s.content_text,
            "audio_url": s.audio_url,
            "status": s.status,
            "tutor_score": s.tutor_score,
            "tutor_feedback": s.tutor_feedback,
            "created_at": s.created_at.isoformat()
        })
    return results


def review_submission(req: TutorReviewRequest, *, actor, db: Session):
    """Assigned tutor grades and provides feedback on student writing or audio."""
    sub = require_submission(db, actor, req.submission_id)
    if not sub:
        raise ApplicationError(status_code=404, detail="Submission not found")
    if req.tutor_score < 0 or req.tutor_score > 100:
        raise ApplicationError(422, "Tutor score must be between 0 and 100")

    sub.tutor_id = actor.id
    sub.tutor_score = req.tutor_score
    sub.tutor_feedback = req.tutor_feedback
    sub.status = "reviewed"
    sub.reviewed_at = datetime.datetime.utcnow()
    db.commit()

    return {"success": True, "message": "Feedback and rubric score saved."}


def get_child_submissions(child_id: str, *, db: Session):
    """Fetch all submissions and tutor feedback for a specific child."""
    subs = db.query(TutorSubmission).filter(
        TutorSubmission.child_id == child_id
    ).order_by(TutorSubmission.created_at.desc()).all()

    return [
        {
            "id": s.id,
            "lesson_id": s.lesson_id,
            "submission_type": s.submission_type,
            "content_text": s.content_text,
            "audio_url": s.audio_url,
            "status": s.status,
            "tutor_score": s.tutor_score,
            "tutor_feedback": s.tutor_feedback,
            "created_at": s.created_at.isoformat(),
            "reviewed_at": s.reviewed_at.isoformat() if s.reviewed_at else None
        }
        for s in subs
    ]

