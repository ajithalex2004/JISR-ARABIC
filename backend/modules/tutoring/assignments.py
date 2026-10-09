"""Explicit grants and immediate revocation of tutor access, scoped for multi-tenancy."""
from backend.models import User, ChildProfile, TutorAssignment
from backend.errors import ApplicationError
from backend.modules.identity.access import require_roles, SCHOOL_ADMIN_ROLES


def set_assignment(tutor_id, child_id, *, actor, db):
    require_roles(actor, SCHOOL_ADMIN_ROLES)
    tutor = db.get(User, tutor_id)
    if tutor is None or tutor.role != "tutor":
        raise ApplicationError(400, "Select a tutor account")
    child = db.get(ChildProfile, child_id)
    if child is None:
        raise ApplicationError(404, "Learner not found")

    if actor.role == "school_admin":
        if child.school_id != actor.school_id:
            raise ApplicationError(403, "Cannot assign tutor to learner from another school")
        if tutor.school_id and tutor.school_id != actor.school_id:
            raise ApplicationError(403, "Tutor belongs to a different school")

    # Composite primary key prevents duplicate grants.
    assignment = db.get(TutorAssignment, (tutor_id, child_id))
    if assignment is None:
        db.add(TutorAssignment(tutor_id=tutor_id, child_id=child_id))
        db.commit()
    return {"success": True, "tutor_id": tutor_id, "child_id": child_id}


def revoke_assignment(tutor_id, child_id, *, actor, db):
    require_roles(actor, SCHOOL_ADMIN_ROLES)
    if actor.role == "school_admin":
        child = db.get(ChildProfile, child_id)
        if child and child.school_id != actor.school_id:
            raise ApplicationError(403, "Cannot revoke assignment for learner from another school")

    assignment = db.get(TutorAssignment, (tutor_id, child_id))
    if assignment:
        db.delete(assignment)
        db.commit()
    return {"success": True}


def list_assignments(*, actor, db):
    require_roles(actor, SCHOOL_ADMIN_ROLES)
    query = db.query(TutorAssignment)
    if actor.role == "school_admin":
        query = query.join(ChildProfile, ChildProfile.id == TutorAssignment.child_id).filter(
            ChildProfile.school_id == actor.school_id
        )
    return [{"tutor_id": a.tutor_id, "child_id": a.child_id} for a in query.all()]


def assignment_options(*, actor, db):
    require_roles(actor, SCHOOL_ADMIN_ROLES)
    tutor_query = db.query(User).filter(User.role == "tutor")
    learner_query = db.query(ChildProfile)
    if actor.role == "school_admin":
        tutor_query = tutor_query.filter(
            (User.school_id == actor.school_id) | (User.school_id.is_(None))
        )
        learner_query = learner_query.filter(ChildProfile.school_id == actor.school_id)

    return {
        "tutors": [{"id": u.id, "name": u.full_name or u.email} for u in tutor_query.all()],
        "learners": [{"id": c.id, "name": c.name, "school_name": c.school_name} for c in learner_query.all()],
    }
