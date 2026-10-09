"""
HTTP adapter: Background task status inspection and task registry endpoints.
Allows clients to poll execution status, progress, and results of long-running operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any

from backend.api.dependencies import get_current_user
from backend.modules.identity.access import Principal, require_roles
from backend.tasks.queue import get_task_status, list_recent_tasks, get_queue_metrics

router = APIRouter(prefix="/api/tasks", tags=["Background Tasks"])


@router.get("/metrics")
def task_queue_metrics(actor: Principal = Depends(get_current_user)):
    """
    Returns queue depth and background worker status.
    Restricted to platform and school administrators.
    """
    require_roles(actor, ("admin", "school_admin"))
    return get_queue_metrics()


@router.get("/{task_id}")
def get_task(task_id: str, actor: Principal = Depends(get_current_user)):
    """
    Retrieve the status, progress percentage, and results of an asynchronous task.
    Enforces multi-tenant ownership boundaries.
    """
    task = get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Super admin has global visibility
    if actor.role == "admin":
        return task.to_dict()

    # School admin has visibility over their school tasks or tasks they launched
    if actor.role == "school_admin":
        if task.actor_id == actor.id or (task.school_id and task.school_id == actor.school_id):
            return task.to_dict()
        raise HTTPException(status_code=403, detail="Forbidden: task belongs to another school")

    # Regular users (parents, tutors, learners) can only inspect their own tasks
    if task.actor_id and task.actor_id == actor.id:
        return task.to_dict()

    raise HTTPException(status_code=403, detail="Forbidden: cannot inspect tasks created by another account")


@router.get("")
def list_tasks(
    limit: int = Query(20, ge=1, le=100),
    actor: Principal = Depends(get_current_user)
):
    """
    List recent tasks submitted by or visible to the authenticated principal.
    """
    require_roles(actor, ("admin", "school_admin"))
    school_filter = actor.school_id if actor.role == "school_admin" else None
    tasks = list_recent_tasks(school_id=school_filter, limit=limit)
    return [t.to_dict() for t in tasks]
