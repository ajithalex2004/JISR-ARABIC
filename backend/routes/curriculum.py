from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.dependencies import get_current_user, get_optional_user
from backend.modules.identity.access import Principal, require_child, optional_child, require_roles, FAMILY_ROLES, PARENT_ROLES, STAFF_ROLES
"""HTTP adapter: request parsing, dependency injection, and service delegation."""
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.schemas import SubmitDiagnosticRequest, OnboardingProfileUpdateRequest, ActiveGradeRequest, AlignmentRequest, WordGlossesRequest
from backend.modules.curriculum import service as service
router = APIRouter(prefix='/api/curriculum', tags=['Curriculum'])

@router.get('/schools')
def list_schools(db: Session=Depends(get_db)):
    """List supported UAE schools."""
    return service.list_schools(db=db)

@router.get('/schools/{school_id}/classes')
def list_school_classes(school_id: str, db: Session=Depends(get_db), actor: Optional[Principal]=Depends(get_optional_user)):
    """List active classes for a given school."""
    return service.list_school_classes(school_id=school_id, db=db)

@router.get('/grades')
def list_grades(db: Session=Depends(get_db), actor: Optional[Principal]=Depends(get_optional_user)):
    """List available grades/classes from Class 1 to Class 12, limited to enrolled grades for students and parents."""
    return service.list_grades(actor=actor, db=db)

@router.get('/terms')
def list_terms(grade: int=Query(5, description='Grade level'), child_id: Optional[str]=Query(None, description='Child profile ID to check access'), db: Session=Depends(get_db), actor: Optional[Principal]=Depends(get_optional_user)):
    """List terms for a given grade with payment unlock status."""
    optional_child(db, actor, child_id)
    return service.list_terms(grade=grade, child_id=child_id, db=db, actor=actor)

@router.get('/lessons')
def list_lessons(grade: int=Query(5), term: int=Query(1), child_id: Optional[str]=Query(None), db: Session=Depends(get_db), actor: Optional[Principal]=Depends(get_optional_user)):
    """List all lessons in a grade and term with availability and lock states."""
    optional_child(db, actor, child_id)
    return service.list_lessons(grade=grade, term=term, child_id=child_id, db=db, actor=actor)

@router.get('/lesson/{lesson_id}')
def get_lesson_content(lesson_id: str, child_id: Optional[str]=Query(None), is_reviewer: bool=Query(False), db: Session=Depends(get_db), actor: Optional[Principal]=Depends(get_optional_user)):
    """
    Get full lesson package.
    Hides assessment answers from client until submission.
    Enforces the $33 per-term paywall for non-demo chapters unless purchased.
    """
    return service.get_lesson_content(lesson_id=lesson_id, child_id=child_id, is_reviewer=is_reviewer, db=db, actor=actor)

@router.get('/diagnostic-questions')
def get_diagnostic_questions(grade: int=Query(5, description='Target student grade level'), stream: Optional[str]=Query(None, description='Curriculum stream')):
    """
    Retrieve calibrated diagnostic baseline questions for the student onboarding wizard.
    Shields answers and solutions on the server.
    """
    return service.get_diagnostic_questions(grade=grade, stream=stream)

@router.post('/submit-diagnostic')
def submit_diagnostic(payload: SubmitDiagnosticRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Evaluate student diagnostic quiz submission, compute competency breakdowns,
    determine calibrated difficulty tier, build a 4-week personalized learning roadmap,
    and persist results to the child profile.
    """
    require_child(db, actor, payload.child_id, FAMILY_ROLES)
    return service.submit_diagnostic(payload=payload, db=db)

@router.get('/learning-plan/{child_id}')
def get_learning_plan(child_id: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Retrieve the customized 4-week learning plan and diagnostic breakdown for a child.
    """
    require_child(db, actor, child_id)
    return service.get_learning_plan(child_id=child_id, db=db)

@router.post('/onboarding-profile')
def update_onboarding_profile(payload: OnboardingProfileUpdateRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Update student demographic details, grade, curriculum stream, term, avatar, and PIN
    during Steps 1 & 2 of the Onboarding Wizard.
    """
    require_child(db, actor, payload.child_id, PARENT_ROLES)
    return service.update_onboarding_profile(payload=payload, db=db, actor=actor)

@router.post('/active-grade')
def set_active_grade(payload: ActiveGradeRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """Move a child to another grade the parent has already paid for (parents and admins only)."""
    require_child(db, actor, payload.child_id, PARENT_ROLES)
    return service.set_active_grade(child_id=payload.child_id, grade=payload.grade, db=db, actor=actor)

@router.get('/textbook-info/{edition_id}')
def textbook_info(edition_id: str, db: Session=Depends(get_db)):
    """How many pages a textbook edition has, for the reader's page navigation."""
    from backend.modules.curriculum.authoring import get_textbook_info
    return get_textbook_info(edition_id, db=db)

@router.get('/word-gloss')
def word_gloss(word: str=Query(..., max_length=40), context: str=Query('', max_length=300)):
    """English meaning of one Arabic word, for tooltips when the client dictionary has no entry."""
    from backend.modules.curriculum.glossary import gloss_word
    return gloss_word(word, context) or {"translation": None, "part_of_speech": None, "source": None}

@router.post('/word-glosses')
def word_glosses(payload: WordGlossesRequest):
    """English meanings for the unknown words of one sentence, fetched ahead so word tooltips open instantly."""
    from backend.modules.curriculum.glossary import gloss_words
    glosses = gloss_words([w[:40] for w in payload.words], payload.context)
    return {"glosses": {word: ({"translation": g["translation"], "part_of_speech": g["part_of_speech"]} if g else None)
                        for word, g in glosses.items()}}

@router.get('/root-family')
def root_family(root: str=Query('', max_length=20), word: str=Query('', max_length=60)):
    """A root's word family for the Root Tree Explorer: words from the learner's lessons plus AI-suggested relatives."""
    from backend.modules.curriculum.roots import root_family as build
    result = build(root or None, word or None)
    if result is None:
        raise HTTPException(status_code=422, detail="Send a vocabulary word or a 3-4 letter Arabic root such as ك-ت-ب.")
    return result

@router.post('/alignments')
def sentence_alignments(payload: AlignmentRequest, db: Session=Depends(get_db)):
    """Arabic-English matching chunks for each sentence pair (null where none is available)."""
    from backend.modules.curriculum.alignment import get_alignments
    return {"alignments": get_alignments(db, [(p.ar, p.en) for p in payload.pairs])}

@router.get('/page-alignments/{pdf_page}')
def page_alignments(pdf_page: int, edition_id: Optional[str]=Query(None, max_length=80), db: Session=Depends(get_db),
                    actor: Principal=Depends(get_current_user)):
    """Arabic-English matching chunks for the lines of a textbook page (signed-in users, like the page text)."""
    from backend.modules.curriculum.alignment import get_page_alignments
    return {"lines": get_page_alignments(db, pdf_page, edition_id)}
