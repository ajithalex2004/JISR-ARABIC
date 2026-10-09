from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.dependencies import get_current_user
from backend.modules.identity.access import Principal, require_roles
"""HTTP adapter: request parsing, dependency injection, and service delegation."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import shutil
from backend.models import Lesson, LessonVersion, ScannedPage
from backend.schemas import AdminAddTermRequest, AdminAddClassRequest, AdminAddLessonRequest, AdminUpdateEditionRequest
from fastapi.responses import FileResponse
from backend.modules.curriculum import authoring as service
from backend.modules.tutoring import assignments
from backend.modules import school
from backend.schemas import ClassCreateRequest, ClassMembershipRequest, TutorClassRequest
from backend.redis_client import invalidate_lesson_cache, invalidate_school_cache
router = APIRouter(prefix='/api/admin', tags=['Content Administration & Scaling'])

@router.post('/schools/classes')
def create_school_class(payload: ClassCreateRequest, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin', 'school_admin'))
    return school.create_class(payload, db=db, actor=actor)

@router.get('/schools/classes')
def list_school_classes(school_id: str | None = None, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin', 'school_admin', 'tutor'))
    return school.list_classes(school_id=school_id, db=db, actor=actor)

@router.put('/schools/classes/{class_id}/active')
def set_school_class_active(class_id: str, active: bool, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin', 'school_admin'))
    return school.set_class_active(class_id, active, db=db, actor=actor)

@router.post('/schools/classes/{class_id}/learners')
def enroll_learner(class_id: str, payload: ClassMembershipRequest, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin', 'school_admin'))
    return school.enroll(class_id, payload.child_id, db=db, actor=actor)

@router.post('/schools/classes/{class_id}/bulk-enroll')
def bulk_enroll_learners(
    class_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    actor: Principal = Depends(get_current_user)
):
    """
    Asynchronously enroll a batch of students into a class via background worker.
    Prevents long database transaction locks when onboarding school grade cohorts.
    """
    require_roles(actor, ('admin', 'school_admin'))
    from backend.modules.identity.access import require_class_scope
    school_class = require_class_scope(db, actor, class_id)
    learner_ids = payload.get("learner_ids", [])
    if not learner_ids:
        raise HTTPException(status_code=400, detail="learner_ids list cannot be empty")
    from backend.tasks.queue import enqueue_task
    task = enqueue_task(
        task_type="bulk_enroll_learners",
        params={
            "class_id": class_id,
            "learner_ids": learner_ids,
            "actor_id": actor.id,
            "actor_school_id": actor.school_id,
            "actor_role": actor.role
        },
        actor_id=actor.id,
        school_id=school_class.school_id
    )
    return {
        "task_id": task.id,
        "status": task.status,
        "class_id": class_id,
        "total_learners": len(learner_ids),
        "poll_url": f"/api/tasks/{task.id}"
    }

@router.delete('/schools/classes/{class_id}/learners/{child_id}')
def remove_learner(class_id: str, child_id: str, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin', 'school_admin'))
    return school.remove(class_id, child_id, db=db, actor=actor)

@router.get('/schools/classes/{class_id}/roster')
def class_roster(class_id: str, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin', 'school_admin', 'tutor'))
    return school.roster(class_id, db=db, actor=actor)

@router.post('/schools/classes/{class_id}/tutors')
def assign_class_tutor(class_id: str, payload: TutorClassRequest, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin', 'school_admin'))
    return school.assign_tutor(class_id, payload.tutor_id, db=db, actor=actor)

@router.delete('/schools/classes/{class_id}/tutors/{tutor_id}')
def unassign_class_tutor(class_id: str, tutor_id: str, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin', 'school_admin'))
    return school.unassign_tutor(class_id, tutor_id, db=db, actor=actor)

@router.get('/schools/classes/{class_id}/audit-log')
def class_audit_log(class_id: str, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin', 'school_admin'))
    return school.get_audit_events(class_id=class_id, db=db, actor=actor)

@router.get('/tutors/{tutor_id}/classes')
def tutor_classes(tutor_id: str, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin', 'school_admin', 'tutor'))
    if actor.role == 'tutor' and actor.id != tutor_id:
        raise HTTPException(status_code=403, detail='Tutors may view only their own classes')
    return school.tutor_classes(tutor_id, db=db, actor=actor)

@router.post('/curriculum-upload')
def upload_curriculum_pdf(
    file: UploadFile = File(...),
    grade: Optional[int] = Form(None),
    term: Optional[int] = Form(None),
    start_page: int = Form(1),
    page_count: Optional[int] = Form(None),
    actor: Principal = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stage a textbook PDF for OCR and enqueue background OCR processing; restricted to Super Admins."""
    require_roles(actor, ('admin',))
    filename = Path(file.filename or '').name
    if not filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail='Only PDF files are accepted')
    upload_dir = Path(__file__).resolve().parents[2] / 'tmp' / 'admin_curriculum_uploads'
    upload_dir.mkdir(parents=True, exist_ok=True)
    target = upload_dir / filename
    with target.open('wb') as output:
        shutil.copyfileobj(file.file, output)

    # Auto-detect grade and term from filename if not explicitly supplied
    import re
    if grade is None:
        g_match = re.search(r'(?:grade|gr|g|class|cls)[\s_-]?(\d+)', filename, re.IGNORECASE)
        grade = int(g_match.group(1)) if g_match else 5
    if term is None:
        t_match = re.search(r'(?:term|vol|t)[\s_-]?(\d+)', filename, re.IGNORECASE)
        term = int(t_match.group(1)) if t_match else 1

    book_edition_id = f"moe_gr{grade}_vol{term}_2023"

    # Auto-detect total page count from PDF if not provided
    if not page_count:
        try:
            import pypdf
            reader = pypdf.PdfReader(target)
            page_count = len(reader.pages)
        except Exception:
            page_count = 10

    from backend.models import BookEdition
    edition = db.query(BookEdition).filter(BookEdition.id == book_edition_id).first()
    if not edition:
        edition = BookEdition(
            id=book_edition_id,
            title=f"اللغة العربية - الصف {grade} - الجزء {term}",
            series_name="العربية تجمعنا",
            volume=term,
            academic_year="2023-2024",
            total_pages=page_count or 120
        )
        db.add(edition)
        db.commit()

    from backend.tasks.queue import enqueue_task
    task = enqueue_task(
        task_type="process_textbook_ocr",
        params={
            "pdf_path": str(target),
            "book_edition_id": book_edition_id,
            "grade": grade,
            "term": term,
            "start_page": start_page,
            "page_count": page_count
        },
        actor_id=actor.id
    )
    return {
        "filename": filename,
        "path": str(target),
        "status": "processing_ocr",
        "book_edition_id": book_edition_id,
        "grade": grade,
        "term": term,
        "page_count": page_count,
        "task_id": task.id,
        "poll_url": f"/api/tasks/{task.id}"
    }

@router.get('/curriculum-review')
def curriculum_review(term: int | None = None, grade: int | None = None, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin',))
    query = db.query(Lesson)
    if grade is not None:
        query = query.filter(Lesson.grade == grade)
    if term in (1, 2, 3):
        query = query.filter(Lesson.term == term)
    lessons = query.order_by(Lesson.grade, Lesson.term, Lesson.lesson_order).all()
    return [{"id": l.id, "grade": l.grade, "term": l.term, "title_ar": l.title_ar, "title_en": l.title_en,
             "start_page": l.start_page, "status": l.status,
             "pages": [{"pdf_page": p.pdf_page, "ocr_text_ar": p.ocr_text_ar, "review_status": p.review_status}
                       for p in db.query(ScannedPage).filter(ScannedPage.book_edition_id.in_([f"moe_gr{l.grade}_vol{l.term}_2023", f"moe_gr{l.grade}_vol{l.term}"]), ScannedPage.pdf_page >= l.start_page, ScannedPage.pdf_page < l.start_page + 10).order_by(ScannedPage.pdf_page).all()]}
            for l in lessons]

@router.put('/curriculum-review/{lesson_id}/status')
def update_curriculum_status(lesson_id: str, status: str, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin',))
    if status not in ('content_pending', 'published'):
        raise HTTPException(status_code=400, detail='status must be content_pending or published')
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail='lesson not found')
    if status == 'published':
        active = db.query(LessonVersion).filter(LessonVersion.lesson_id == lesson_id, LessonVersion.is_active == True, LessonVersion.status == 'published').first()
        if active is None:
            raise HTTPException(status_code=409, detail='Approve and publish a lesson version before publishing this lesson')
    lesson.status = status
    db.commit()
    invalidate_lesson_cache(lesson_id, grade=lesson.grade, term=lesson.term)
    return {"id": lesson.id, "status": lesson.status}

@router.post('/lessons/{lesson_id}/versions/{version_id}/approve')
def approve_lesson_version(lesson_id: str, version_id: str, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin',))
    return service.approve_lesson_version(lesson_id, version_id, db=db, actor=actor)

@router.post('/lessons/{lesson_id}/versions/{version_id}/publish')
def publish_lesson_version(lesson_id: str, version_id: str, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    require_roles(actor, ('admin',))
    result = service.publish_lesson_version(lesson_id, version_id, db=db, actor=actor)
    lesson = db.get(Lesson, lesson_id)
    if lesson:
        lesson.status = 'published'
        db.commit()
        invalidate_lesson_cache(lesson_id, grade=lesson.grade, term=lesson.term)
    return result


@router.get('/tutor-assignments')
def list_tutor_assignments(actor: Principal = Depends(get_current_user), db: Session = Depends(get_db)):
    return assignments.list_assignments(actor=actor, db=db)


@router.get('/tutor-assignment-options')
def tutor_assignment_options(actor: Principal = Depends(get_current_user), db: Session = Depends(get_db)):
    return assignments.assignment_options(actor=actor, db=db)


@router.put('/tutor-assignments/{tutor_id}/{child_id}')
def assign_tutor(tutor_id: str, child_id: str, actor: Principal = Depends(get_current_user), db: Session = Depends(get_db)):
    return assignments.set_assignment(tutor_id, child_id, actor=actor, db=db)


@router.delete('/tutor-assignments/{tutor_id}/{child_id}')
def unassign_tutor(tutor_id: str, child_id: str, actor: Principal = Depends(get_current_user), db: Session = Depends(get_db)):
    return assignments.revoke_assignment(tutor_id, child_id, actor=actor, db=db)

@router.get('/coverage-report')
def get_coverage_report():
    """Coverage report for whole-book content and pronunciation targets (Section 11)."""
    return service.get_coverage_report()

@router.get('/quality-report')
def get_quality_report(db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    """Run pre-publication OCR, translation, duplication, and boundary checks."""
    require_roles(actor, ('admin',))
    return service.get_quality_report(db=db)

@router.get('/ocr-page/{pdf_page}')
def get_ocr_page(pdf_page: int, edition_id: str | None = None, db: Session = Depends(get_db)):
    """Fetch OCR transcription, image reference, and confidence for a book page."""
    return service.get_ocr_page(pdf_page=pdf_page, edition_id=edition_id, db=db)

class SolveQuestionPayload(BaseModel):
    question_ar: str
    context_ar: str | None = None
    grade: int | None = 6

@router.post('/solve-question')
def solve_curriculum_question(payload: SolveQuestionPayload, actor: Principal = Depends(get_current_user)):
    """Generate or retrieve a verified model answer with Arabic (vowels), Arabzi, and English."""
    require_roles(actor, ('admin', 'school_admin', 'tutor'))
    return service.solve_curriculum_question(
        question_ar=payload.question_ar,
        context_ar=payload.context_ar,
        grade=payload.grade
    )

@router.get('/page-image/{pdf_page}')
def get_page_image(pdf_page: int, edition_id: str | None = None):
    """Serve authentic scanned book page image from sample cache or edition subfolder."""
    return FileResponse(service.get_page_image(pdf_page=pdf_page, edition_id=edition_id), media_type='image/png')

@router.get('/textbook-library')
def get_textbook_library(db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    """List all 30 MoE textbook volumes with indexing, page counts, and rendering telemetry."""
    require_roles(actor, ('admin', 'school_admin', 'tutor'))
    return service.get_textbook_library(db=db)

@router.get('/textbook-pages/{edition_id}')
def get_textbook_pages(edition_id: str, db: Session = Depends(get_db), actor: Principal = Depends(get_current_user)):
    """List all scanned pages with OCR text preview and high-res image references for an edition."""
    require_roles(actor, ('admin', 'school_admin', 'tutor'))
    return service.get_textbook_pages(edition_id=edition_id, db=db)

@router.post('/add-term')
def add_term(req: AdminAddTermRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    ADD_TERM mode:
    Configures a new term container with price (e.g. USD 33).
    """
    require_roles(actor, ('admin',))
    return service.add_term(req=req, db=db)

@router.post('/add-class')
def add_class(req: AdminAddClassRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    ADD_CLASS mode:
    Creates a new Grade/Class container (e.g. Class 6) without editing application code.
    """
    require_roles(actor, ('admin',))
    return service.add_class(req=req, db=db)

@router.post('/add-lesson')
def add_lesson(req: AdminAddLessonRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    ADD_LESSON mode:
    Imports and validates a 12-feature lesson JSON package.
    Ensures idempotency (reimporting identical hash does not duplicate).
    """
    require_roles(actor, ('admin',))
    return service.add_lesson(req=req, db=db, actor=actor)

@router.post('/update-edition')
def update_edition(req: AdminUpdateEditionRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    UPDATE_EDITION mode:
    Registers a new textbook edition without altering old student results or in-progress assessments.
    """
    require_roles(actor, ('admin',))
    return service.update_edition(req=req, db=db)

@router.post('/lessons/{lesson_id}/rollback/{version_id}')
def rollback_lesson(lesson_id: str, version_id: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    require_roles(actor, ('admin',))
    return service.rollback_lesson(lesson_id, version_id, db=db, actor=actor)

@router.post('/bulk-ingest')
def bulk_ingest_curriculum(payload: list[dict] | dict, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    BULK_INGEST:
    Imports and validates an array of lesson packages (or single package) for Grades 1 to 10 across all 3 terms.
    """
    require_roles(actor, ('admin',))
    from backend.scripts.bulk_ingest_curriculum import ingest_single_package
    items = payload if isinstance(payload, list) else [payload]
    results = []
    for pkg in items:
        res = ingest_single_package(pkg, db)
        results.append(res)
    return {
        "total": len(items),
        "successful": sum(1 for r in results if r.get("success")),
        "details": results
    }

