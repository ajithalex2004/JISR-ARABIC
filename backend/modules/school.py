"""School/class administration, multi-tenant scoping, and explicit membership authorization."""
import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.models import (
    School, SchoolClass, ClassMembership, TutorClassAssignment,
    MembershipAuditEvent, ChildProfile, User
)
from backend.errors import ApplicationError
from backend.modules.identity.access import (
    require_roles, require_class_scope, require_school_scope, SCHOOL_ADMIN_ROLES
)
from backend.redis_client import invalidate_school_cache


def _audit(db: Session, actor_id: str, action: str, class_id: str, child_id: Optional[str] = None, tutor_id: Optional[str] = None):
    db.add(MembershipAuditEvent(
        actor_id=actor_id,
        action=action,
        class_id=class_id,
        child_id=child_id,
        tutor_id=tutor_id,
        created_at=datetime.datetime.utcnow()
    ))


def serialize_class(item: SchoolClass) -> Dict[str, Any]:
    return {
        "id": item.id,
        "school_id": item.school_id,
        "name": item.name,
        "grade": item.grade,
        "academic_year": item.academic_year,
        "is_active": item.is_active
    }


def create_class(payload, *, db: Session, actor) -> Dict[str, Any]:
    require_roles(actor, SCHOOL_ADMIN_ROLES)
    if actor.role == "school_admin":
        if not actor.school_id or payload.school_id != actor.school_id:
            raise ApplicationError(403, "Cannot create class for another school")

    school = db.get(School, payload.school_id)
    if not school:
        raise ApplicationError(404, "School not found")

    if db.get(SchoolClass, payload.id):
        raise ApplicationError(409, "Class already exists")

    school_class = SchoolClass(
        id=payload.id,
        school_id=payload.school_id,
        name=payload.name.strip(),
        grade=payload.grade,
        academic_year=payload.academic_year,
        is_active=True
    )
    db.add(school_class)
    db.commit()
    db.refresh(school_class)

    _audit(db, actor.id, "class_created", payload.id)
    db.commit()
    invalidate_school_cache(payload.school_id)
    return serialize_class(school_class)


def set_class_active(class_id: str, active: bool, *, db: Session, actor) -> Dict[str, Any]:
    school_class = require_class_scope(db, actor, class_id)
    school_class.is_active = active
    _audit(db, actor.id, "class_activated" if active else "class_deactivated", class_id)
    db.commit()
    db.refresh(school_class)
    invalidate_school_cache(school_class.school_id)
    return serialize_class(school_class)


def enroll(class_id: str, child_id: str, *, db: Session, actor) -> Dict[str, Any]:
    school_class = require_class_scope(db, actor, class_id)
    if not school_class.is_active:
        raise ApplicationError(409, "Class is inactive")

    child = db.get(ChildProfile, child_id)
    if not child:
        raise ApplicationError(404, "Learner not found")

    if actor.role == "school_admin":
        if child.school_id and child.school_id != actor.school_id:
            raise ApplicationError(403, "Cannot enroll learner from a different school")

    membership = db.get(ClassMembership, (class_id, child_id))
    if not membership:
        membership = ClassMembership(class_id=class_id, child_id=child_id)
        db.add(membership)

    child.school_id = school_class.school_id
    child.class_id = class_id
    _audit(db, actor.id, "learner_enrolled", class_id, child_id=child_id)
    db.commit()
    return {"success": True, "class_id": class_id, "child_id": child_id}


def remove(class_id: str, child_id: str, *, db: Session, actor) -> Dict[str, Any]:
    require_class_scope(db, actor, class_id)
    membership = db.get(ClassMembership, (class_id, child_id))
    if not membership:
        raise ApplicationError(404, "Membership not found")

    db.delete(membership)
    child = db.get(ChildProfile, child_id)
    if child and child.class_id == class_id:
        child.class_id = None

    _audit(db, actor.id, "learner_removed", class_id, child_id=child_id)
    db.commit()
    return {"success": True, "class_id": class_id, "child_id": child_id}


def roster(class_id: str, *, db: Session, actor) -> Dict[str, Any]:
    school_class = require_class_scope(db, actor, class_id)
    members = (
        db.query(ClassMembership, ChildProfile)
        .join(ChildProfile, ChildProfile.id == ClassMembership.child_id)
        .filter(ClassMembership.class_id == class_id)
        .all()
    )
    return {
        "class": serialize_class(school_class),
        "learners": [
            {
                "id": child.id,
                "name": child.name,
                "grade": child.default_grade,
                "school_id": child.school_id
            }
            for _, child in members
        ]
    }


def assign_tutor(class_id: str, tutor_id: str, *, db: Session, actor) -> Dict[str, Any]:
    require_class_scope(db, actor, class_id)
    tutor = db.get(User, tutor_id)
    if not tutor or tutor.role != "tutor":
        raise ApplicationError(400, "User is not a tutor")

    if actor.role == "school_admin":
        if tutor.school_id and tutor.school_id != actor.school_id:
            raise ApplicationError(403, "Tutor belongs to a different school")

    assignment = db.get(TutorClassAssignment, (tutor_id, class_id))
    if not assignment:
        db.add(TutorClassAssignment(tutor_id=tutor_id, class_id=class_id))

    _audit(db, actor.id, "tutor_assigned", class_id, tutor_id=tutor_id)
    db.commit()
    return {"success": True, "class_id": class_id, "tutor_id": tutor_id}


def unassign_tutor(class_id: str, tutor_id: str, *, db: Session, actor) -> Dict[str, Any]:
    require_class_scope(db, actor, class_id)
    assignment = db.get(TutorClassAssignment, (tutor_id, class_id))
    if assignment:
        db.delete(assignment)

    _audit(db, actor.id, "tutor_unassigned", class_id, tutor_id=tutor_id)
    db.commit()
    return {"success": True, "class_id": class_id, "tutor_id": tutor_id}


def tutor_classes(tutor_id: str, *, db: Session, actor) -> List[Dict[str, Any]]:
    require_roles(actor, ("admin", "school_admin", "tutor"))
    if actor.role == "tutor" and actor.id != tutor_id:
        raise ApplicationError(403, "Tutors may view only their own classes")

    query = (
        db.query(SchoolClass)
        .join(TutorClassAssignment, TutorClassAssignment.class_id == SchoolClass.id)
        .filter(TutorClassAssignment.tutor_id == tutor_id, SchoolClass.is_active == True)
    )
    if actor.role == "school_admin":
        query = query.filter(SchoolClass.school_id == actor.school_id)

    return [serialize_class(item) for item in query.all()]


def list_classes(school_id: Optional[str] = None, *, db: Session, actor) -> List[Dict[str, Any]]:
    require_roles(actor, ("admin", "school_admin", "tutor"))
    if actor.role == "school_admin":
        target_school = actor.school_id
        return [serialize_class(c) for c in db.query(SchoolClass).filter(SchoolClass.school_id == target_school).all()]
    elif actor.role == "tutor":
        query = (
            db.query(SchoolClass)
            .join(TutorClassAssignment, TutorClassAssignment.class_id == SchoolClass.id)
            .filter(TutorClassAssignment.tutor_id == actor.id, SchoolClass.is_active == True)
        )
        return [serialize_class(c) for c in query.all()]
    else:
        query = db.query(SchoolClass)
        if school_id:
            query = query.filter(SchoolClass.school_id == school_id)
        return [serialize_class(c) for c in query.all()]


def get_audit_events(class_id: Optional[str] = None, *, db: Session, actor) -> List[Dict[str, Any]]:
    require_roles(actor, SCHOOL_ADMIN_ROLES)
    query = db.query(MembershipAuditEvent)
    if actor.role == "school_admin":
        query = query.join(SchoolClass, SchoolClass.id == MembershipAuditEvent.class_id).filter(
            SchoolClass.school_id == actor.school_id
        )
    if class_id:
        require_class_scope(db, actor, class_id)
        query = query.filter(MembershipAuditEvent.class_id == class_id)

    events = query.order_by(MembershipAuditEvent.created_at.desc()).all()
    return [
        {
            "id": e.id,
            "actor_id": e.actor_id,
            "action": e.action,
            "class_id": e.class_id,
            "child_id": e.child_id,
            "tutor_id": e.tutor_id,
            "created_at": e.created_at.isoformat()
        }
        for e in events
    ]
