"""
Background task processing system for JISR.
Provides asynchronous job queues for audio generation (TTS), textbook OCR ingestion,
bulk class student enrollment, and parent progress digest delivery.
"""
from backend.tasks.queue import (
    enqueue_task,
    get_task_status,
    list_recent_tasks,
    get_queue_metrics,
    clear_task_queue,
    TaskInfo,
)
from backend.tasks.worker import (
    TaskWorker,
    start_in_process_worker,
    stop_in_process_worker,
)

__all__ = [
    "enqueue_task",
    "get_task_status",
    "list_recent_tasks",
    "get_queue_metrics",
    "clear_task_queue",
    "TaskInfo",
    "TaskWorker",
    "start_in_process_worker",
    "stop_in_process_worker",
]
