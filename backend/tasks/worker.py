"""
Background worker execution engine.
Pops task descriptors from the task queue, executes registered task handlers,
manages atomic status transitions, and records telemetry.
"""
import os
import sys
import time
import signal
import logging
import threading
from typing import Optional, Dict, Any

from backend.tasks.queue import pop_task, get_task_status, update_task_status
from backend.tasks.handlers import TASK_HANDLERS

logger = logging.getLogger("fahim.tasks.worker")

_in_process_worker: Optional["TaskWorker"] = None
_worker_thread: Optional[threading.Thread] = None


class TaskWorker:
    def __init__(self, worker_id: Optional[str] = None):
        self.worker_id = worker_id or f"worker-{os.getpid()}"
        self.running = False

    def process_one_task(self, timeout: int = 1) -> bool:
        """
        Pops and executes a single task. Returns True if a task was processed, False if queue was empty.
        """
        task_id = pop_task(timeout=timeout)
        if not task_id:
            return False

        task = get_task_status(task_id)
        if not task:
            logger.warning(f"Worker {self.worker_id} popped unknown task_id: {task_id}")
            return False

        if task.status in ("completed", "failed"):
            logger.info(f"Task {task_id} already in terminal state {task.status}")
            return True

        handler = TASK_HANDLERS.get(task.task_type)
        if not handler:
            err_msg = f"No handler registered for task type: '{task.task_type}'"
            logger.error(err_msg)
            update_task_status(task_id, status="failed", error=err_msg)
            return True

        logger.info(f"Worker {self.worker_id} starting task {task_id} ({task.task_type})")
        update_task_status(task_id, status="running", progress=5)

        def progress_callback(pct: int):
            update_task_status(task_id, progress=pct)

        try:
            result = handler(task.params, progress_callback)
            update_task_status(task_id, status="completed", progress=100, result=result)
            logger.info(f"Worker {self.worker_id} successfully completed task {task_id}")
        except Exception as exc:
            err_detail = f"{type(exc).__name__}: {str(exc)}"
            logger.exception(f"Worker {self.worker_id} failed on task {task_id}: {err_detail}")
            update_task_status(task_id, status="failed", error=err_detail)

        return True

    def run_forever(self, poll_interval: float = 0.5):
        """
        Continuously polls and processes tasks until stopped.
        """
        self.running = True
        logger.info(f"TaskWorker {self.worker_id} started listening for jobs")

        while self.running:
            try:
                processed = self.process_one_task(timeout=1)
                if not processed and poll_interval > 0:
                    time.sleep(poll_interval)
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                time.sleep(1)

        logger.info(f"TaskWorker {self.worker_id} stopped cleanly")

    def stop(self):
        self.running = False


def start_in_process_worker() -> TaskWorker:
    """
    Starts an in-process background worker thread if not already running.
    """
    global _in_process_worker, _worker_thread

    if _in_process_worker is not None and _in_process_worker.running:
        return _in_process_worker

    worker = TaskWorker(worker_id="in-process-worker-1")
    t = threading.Thread(target=worker.run_forever, daemon=True, name="FahimTaskWorker")
    t.start()

    _in_process_worker = worker
    _worker_thread = t
    logger.info("In-process background task worker started successfully")
    return worker


def stop_in_process_worker():
    """
    Stops the active in-process background worker thread.
    """
    global _in_process_worker, _worker_thread
    if _in_process_worker:
        _in_process_worker.stop()
        _in_process_worker = None
    if _worker_thread and _worker_thread.is_alive():
        _worker_thread.join(timeout=2)
        _worker_thread = None
    logger.info("In-process background task worker stopped")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    worker = TaskWorker()

    def handle_signal(sig, frame):
        logger.info("Shutdown signal received, stopping worker...")
        worker.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    print(f"JISR Background Task Worker running (PID {os.getpid()}). Press Ctrl+C to terminate.")
    worker.run_forever()
