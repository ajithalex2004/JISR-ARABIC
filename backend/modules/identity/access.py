"""Role and resource authorization shared by HTTP adapters and services."""
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from backend.errors import ApplicationError
from backend.models import ChildProfile, TutorAssignment, TutorSubmission, LearnerMistake, PaymentTransaction, ClassMembership, SchoolClass, TutorClassAssignment


@dataclass(frozen=True)
class Principal:
    id: str
    email: str
    role: str
    is_verified: bool
    phone_number: Optional[str] = None
    child_id: Optional[str] = None
    school_id: Optional[str] = None


ALL_ROLES = ("parent", "learner", "tutor", "admin", "school_admin")
FAMILY_ROLES = ("parent", "learner", "admin")
PARENT_ROLES = ("parent", "admin")
STAFF_ROLES = ("tutor", "admin", "school_admin")
NON_LEARNER_ROLES = ("parent", "tutor", "admin", "school_admin")
SCHOOL_ADMIN_ROLES = ("admin", "school_admin")


def require_roles(actor, roles=ALL_ROLES):
    if actor is None:
        raise ApplicationError(401, "Sign in to continue")
    if actor.role not in roles:
        raise ApplicationError(403, "This account cannot perform this action")
    return actor


def require_non_learner(actor):
    """Restrict parent/staff features that are not available to learner logins."""
    return require_roles(actor, NON_LEARNER_ROLES)


def visible_children(db: Session, actor):
    require_roles(actor)
    query = db.query(ChildProfile)
    if actor.role == "parent":
        query = query.filter(ChildProfile.parent_id == actor.id)
    elif actor.role == "learner":
        query = query.filter(ChildProfile.id == actor.child_id, ChildProfile.parent_id == actor.id)
    elif actor.role == "school_admin":
        if not actor.school_id:
            query = query.filter(False)
        else:
            query = query.filter(
                (ChildProfile.school_id == actor.school_id) |
                ChildProfile.id.in_(
                    db.query(ClassMembership.child_id)
                    .join(SchoolClass, SchoolClass.id == ClassMembership.class_id)
                    .filter(SchoolClass.school_id == actor.school_id)
                )
            )
    elif actor.role == "tutor":
        tutor_child_ids = db.query(TutorAssignment.child_id).filter(TutorAssignment.tutor_id == actor.id).union(
            db.query(ClassMembership.child_id).join(TutorClassAssignment, TutorClassAssignment.class_id == ClassMembership.class_id).filter(TutorClassAssignment.tutor_id == actor.id)
        )
        query = query.filter(ChildProfile.id.in_(tutor_child_ids))
        if getattr(actor, "school_id", None):
            query = query.filter(
                (ChildProfile.school_id == actor.school_id) |
                ChildProfile.id.in_(
                    db.query(ClassMembership.child_id)
                    .join(SchoolClass, SchoolClass.id == ClassMembership.class_id)
                    .filter(SchoolClass.school_id == actor.school_id)
                )
            )
    return query


def require_child(db: Session, actor, child_id: str, roles=ALL_ROLES):
    require_roles(actor, roles)
    if child_id == "admin_supervisor" or getattr(actor, "role", None) == "admin":
        return None
    child = visible_children(db, actor).filter(ChildProfile.id == child_id).first()
    if child is None:
        raise ApplicationError(403, "You do not have access to this learner")
    return child


def optional_child(db: Session, actor, child_id):
    if child_id == "admin_supervisor" or getattr(actor, "role", None) == "admin":
        return None
    if child_id is not None:
        return require_child(db, actor, child_id)


def require_school_scope(db: Session, actor, school_id: str):
    """Ensure actor has administrative access to the specified school."""
    require_roles(actor, SCHOOL_ADMIN_ROLES)
    if actor.role == "admin":
        return True
    if actor.role == "school_admin":
        if not actor.school_id or actor.school_id != school_id:
            raise ApplicationError(403, "You do not have access to another school's data")
        return True
    raise ApplicationError(403, "Access denied")


def require_class_scope(db: Session, actor, class_id: str) -> SchoolClass:
    """Ensure actor has administrative or assigned access to the specified school class."""
    require_roles(actor, ("admin", "school_admin", "tutor"))
    school_class = db.get(SchoolClass, class_id)
    if not school_class:
        raise ApplicationError(404, "Class not found")
    if actor.role == "admin":
        return school_class
    if actor.role == "school_admin":
        if not actor.school_id or school_class.school_id != actor.school_id:
            raise ApplicationError(403, "You do not have access to classes from another school")
        return school_class
    if actor.role == "tutor":
        is_assigned = db.query(TutorClassAssignment).filter(
            TutorClassAssignment.tutor_id == actor.id,
            TutorClassAssignment.class_id == class_id
        ).first()
        if not is_assigned:
            raise ApplicationError(403, "You are not assigned to this school class")
        return school_class
    raise ApplicationError(403, "Access denied")


def require_class_membership(db: Session, actor, class_id: str, child_id: str | None = None):
    """Require explicit school-class membership for school-scoped features."""
    require_roles(actor)
    school_class = db.get(SchoolClass, class_id)
    if not school_class or not school_class.is_active:
        raise ApplicationError(404, "Class not found or inactive")

    if actor.role == "admin":
        return True
    elif actor.role == "school_admin":
        if not actor.school_id or school_class.school_id != actor.school_id:
            raise ApplicationError(403, "You do not have access to this school class")
        if child_id:
            require_child(db, actor, child_id)
        return True
    elif actor.role == "tutor":
        is_assigned = db.query(TutorClassAssignment).filter(
            TutorClassAssignment.tutor_id == actor.id,
            TutorClassAssignment.class_id == class_id
        ).first()
        if not is_assigned:
            raise ApplicationError(403, "You are not assigned to this school class")
        if child_id:
            require_child(db, actor, child_id)
        return True
    elif actor.role == "learner":
        query = db.query(ClassMembership).filter(
            ClassMembership.class_id == class_id,
            ClassMembership.child_id == actor.child_id
        )
        if not query.first():
            raise ApplicationError(403, "You do not have access to this school class")
        return True
    elif actor.role == "parent":
        if not child_id:
            raise ApplicationError(400, "child_id required for parent access")
        require_child(db, actor, child_id)
        query = db.query(ClassMembership).filter(
            ClassMembership.class_id == class_id,
            ClassMembership.child_id == child_id
        )
        if not query.first():
            raise ApplicationError(403, "Learner is not enrolled in this school class")
        return True
    raise ApplicationError(403, "Access denied")


def require_mistake(db: Session, actor, mistake_id: int):
    require_roles(actor, FAMILY_ROLES)
    record = db.get(LearnerMistake, mistake_id)
    if record is None:
        raise ApplicationError(404, "Mistake entry not found")
    require_child(db, actor, record.child_id, FAMILY_ROLES)
    return record


def require_submission(db: Session, actor, submission_id: str):
    require_roles(actor, STAFF_ROLES)
    record = db.get(TutorSubmission, submission_id)
    if record is None:
        raise ApplicationError(404, "Submission not found")
    require_child(db, actor, record.child_id, STAFF_ROLES)
    return record


def require_invoice(db: Session, actor, receipt: str):
    require_roles(actor, PARENT_ROLES)
    receipt = receipt.strip()
    txn = db.query(PaymentTransaction).filter(
        (PaymentTransaction.receipt_number == receipt) |
        (PaymentTransaction.tax_invoice_number == receipt) |
        (PaymentTransaction.id == receipt)
    ).first()
    if txn is None:
        raise ApplicationError(404, "Invoice not found")
    require_child(db, actor, txn.child_id, PARENT_ROLES)
    return txn
