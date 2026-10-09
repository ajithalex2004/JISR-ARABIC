"""
Distributed task queue and task state manager.
Stores task descriptors and execution state in Redis with automatic 24-hour TTL,
with thread-safe in-memory fallback for development and test environments.
"""
import os
import time
import json
import uuid
import queue
import logging
import threading
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List

from backend.redis_client import get_redis_client

logger = logging.getLogger("fahim.tasks")

QUEUE_NAME = "fahim:task_queue"
TASK_PREFIX = "fahim:task:"
TASK_TTL_SECONDS = 86400  # 24 hours

# In-memory fallback
_tasks_lock = threading.Lock()
_in_memory_queue: queue.Queue = queue.Queue()
_in_memory_tasks: Dict[str, Dict[str, Any]] = {}
_in_memory_task_ids: List[str] = []


def clear_task_queue():
    """Clear in-memory and Redis queues (useful for testing or queue flushing)."""
    client = get_redis_client()
    if client:
        try:
            client.delete(QUEUE_NAME)
        except Exception:
            pass
    with _tasks_lock:
        while not _in_memory_queue.empty():
            try:
                _in_memory_queue.get_nowait()
            except queue.Empty:
                break
        _in_memory_tasks.clear()
        _in_memory_task_ids.clear()


@dataclass
class TaskInfo:
    id: str
    task_type: str
    status: str  # "pending", "running", "completed", "failed"
    progress: int  # 0 to 100
    params: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    actor_id: Optional[str] = None
    school_id: Optional[str] = None
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskInfo":
        params = data.get("params", {})
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except Exception:
                params = {}
        result = data.get("result")
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception:
                pass
        return cls(
            id=str(data["id"]),
            task_type=str(data["task_type"]),
            status=str(data.get("status", "pending")),
            progress=int(data.get("progress", 0)),
            params=params,
            result=result,
            error=data.get("error"),
            actor_id=data.get("actor_id"),
            school_id=data.get("school_id"),
            created_at=str(data.get("created_at", "")),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
        )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def enqueue_task(
    task_type: str,
    params: Dict[str, Any],
    actor_id: Optional[str] = None,
    school_id: Optional[str] = None,
) -> TaskInfo:
    """
    Enqueues a background task into the queue and records initial state.
    """
    task_id = str(uuid.uuid4())
    task = TaskInfo(
        id=task_id,
        task_type=task_type,
        status="pending",
        progress=0,
        params=params,
        actor_id=actor_id,
        school_id=school_id,
        created_at=_now_iso(),
    )

    client = get_redis_client()
    if client:
        try:
            key = f"{TASK_PREFIX}{task_id}"
            serialized = {
                "id": task.id,
                "task_type": task.task_type,
                "status": task.status,
                "progress": str(task.progress),
                "params": json.dumps(task.params, ensure_ascii=False),
                "result": json.dumps(task.result or {}, ensure_ascii=False) if task.result else "",
                "error": task.error or "",
                "actor_id": task.actor_id or "",
                "school_id": task.school_id or "",
                "created_at": task.created_at,
                "started_at": task.started_at or "",
                "completed_at": task.completed_at or "",
            }
            pipe = client.pipeline()
            pipe.hset(key, mapping=serialized)
            pipe.expire(key, TASK_TTL_SECONDS)
            pipe.rpush(QUEUE_NAME, task_id)
            pipe.execute()
            logger.info(f"Enqueued task {task_id} ({task_type}) to Redis")
            return task
        except Exception as e:
            logger.warning(f"Redis enqueue failed ({e}), checking environment fallback")
            if os.getenv("FAHIM_ENV", "development").lower() == "production":
                from backend.errors import ApplicationError
                raise ApplicationError(503, "Task queue is unavailable in production")

    if os.getenv("FAHIM_ENV", "development").lower() == "production":
        from backend.errors import ApplicationError
        raise ApplicationError(503, "Task queue is unavailable in production")

    # In-memory fallback (only permitted in development and test environments)
    with _tasks_lock:
        _in_memory_tasks[task_id] = task.to_dict()
        _in_memory_task_ids.append(task_id)
        _in_memory_queue.put(task_id)

    logger.info(f"Enqueued task {task_id} ({task_type}) to in-memory queue")
    return task


def get_task_status(task_id: str) -> Optional[TaskInfo]:
    """
    Retrieves the current state of a task by ID.
    """
    client = get_redis_client()
    if client:
        try:
            key = f"{TASK_PREFIX}{task_id}"
            data = client.hgetall(key)
            if data and "id" in data:
                return TaskInfo.from_dict(data)
        except Exception as e:
            logger.warning(f"Redis get_task_status failed ({e}), checking in-memory")

    with _tasks_lock:
        if task_id in _in_memory_tasks:
            return TaskInfo.from_dict(_in_memory_tasks[task_id])
    return None


def update_task_status(
    task_id: str,
    status: Optional[str] = None,
    progress: Optional[int] = None,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
) -> Optional[TaskInfo]:
    """
    Updates the execution state and progress of an active task.
    """
    client = get_redis_client()
    now_str = _now_iso()

    updates: Dict[str, Any] = {}
    if status is not None:
        updates["status"] = status
        if status == "running":
            updates["started_at"] = now_str
        elif status in ("completed", "failed"):
            updates["completed_at"] = now_str
    if progress is not None:
        updates["progress"] = max(0, min(100, int(progress)))
    if result is not None:
        updates["result"] = result
    if error is not None:
        updates["error"] = error

    if client:
        try:
            key = f"{TASK_PREFIX}{task_id}"
            redis_updates = {}
            for k, v in updates.items():
                if k in ("params", "result"):
                    redis_updates[k] = json.dumps(v, ensure_ascii=False) if v is not None else ""
                else:
                    redis_updates[k] = str(v)
            if redis_updates:
                client.hset(key, mapping=redis_updates)
                client.expire(key, TASK_TTL_SECONDS)
            data = client.hgetall(key)
            if data and "id" in data:
                return TaskInfo.from_dict(data)
        except Exception as e:
            logger.warning(f"Redis update_task_status failed ({e}), using in-memory")

    with _tasks_lock:
        if task_id in _in_memory_tasks:
            current = _in_memory_tasks[task_id]
            for k, v in updates.items():
                current[k] = v
            return TaskInfo.from_dict(current)

    return None


def pop_task(timeout: int = 1) -> Optional[str]:
    """
    Retrieves the next task ID to execute. Blocks up to `timeout` seconds.
    """
    client = get_redis_client()
    if client:
        try:
            # BLPOP blocks on queue
            item = client.blpop(QUEUE_NAME, timeout=timeout)
            if item:
                _, task_id = item
                return task_id
        except Exception as e:
            logger.warning(f"Redis pop_task failed ({e}), checking in-memory queue")

    try:
        return _in_memory_queue.get(timeout=timeout)
    except queue.Empty:
        return None


def list_recent_tasks(
    actor_id: Optional[str] = None,
    school_id: Optional[str] = None,
    limit: int = 50,
) -> List[TaskInfo]:
    """
    Lists recent tasks, optionally filtered by actor or school.
    """
    tasks: List[TaskInfo] = []
    client = get_redis_client()
    if client:
        try:
            # Scan recent task keys using scan_iter to avoid blocking Redis keyspace
            keys = []
            for k in client.scan_iter(match=f"{TASK_PREFIX}*", count=100):
                keys.append(k)
                if len(keys) >= limit * 4:
                    break
            for k in keys[-limit:]:
                d = client.hgetall(k)
                if d and "id" in d:
                    t = TaskInfo.from_dict(d)
                    if actor_id and t.actor_id != actor_id:
                        continue
                    if school_id and t.school_id != school_id:
                        continue
                    tasks.append(t)
            tasks.sort(key=lambda x: x.created_at, reverse=True)
            return tasks[:limit]
        except Exception as e:
            logger.warning(f"Redis list_recent_tasks failed ({e}), using in-memory")

    with _tasks_lock:
        for tid in reversed(_in_memory_task_ids[-limit:]):
            if tid in _in_memory_tasks:
                t = TaskInfo.from_dict(_in_memory_tasks[tid])
                if actor_id and t.actor_id != actor_id:
                    continue
                if school_id and t.school_id != school_id:
                    continue
                tasks.append(t)
    return tasks[:limit]


def get_queue_metrics() -> Dict[str, Any]:
    """
    Returns metrics on queue depth and operational backend.
    """
    client = get_redis_client()
    if client:
        try:
            depth = client.llen(QUEUE_NAME)
            return {
                "backend": "redis",
                "queue_depth": depth,
                "status": "healthy",
            }
        except Exception:
            pass

    if os.getenv("FAHIM_ENV", "development").lower() == "production":
        return {
            "backend": "unavailable",
            "queue_depth": 0,
            "status": "degraded",
        }

    return {
        "backend": "in_memory",
        "queue_depth": _in_memory_queue.qsize(),
        "status": "healthy",
    }
