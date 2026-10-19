"""Read (or re-read) the pages of textbooks already uploaded, from Admin > Content.

Uploaded PDFs stay in the content folder (uploads/<edition>.pdf). Queuing the OCR task on the same
file resumes it: pages already read are skipped and failed or unread pages are tried again."""
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from backend.config import content_root
from backend.tasks.queue import enqueue_task, list_recent_tasks

EDITION_ID = re.compile(r"^moe_gr(?:[1-9]|1[0-2])_vol[1-3]_2023$")
OCR_TASK = "process_textbook_ocr"


def stored_pdf(edition_id: str) -> Optional[Path]:
    if not EDITION_ID.match(edition_id or ""):
        return None
    path = content_root() / "uploads" / f"{edition_id}.pdf"
    return path if path.is_file() else None


def books_being_read() -> Set[str]:
    """Editions with an OCR task waiting or running."""
    return {task.params.get("book_edition_id") for task in list_recent_tasks(limit=200)
            if task.task_type == OCR_TASK and task.status in ("pending", "running")}


def queue_book_read(edition_id: str, actor_id: Optional[str]) -> Dict[str, Any]:
    pdf = stored_pdf(edition_id)
    if pdf is None:
        raise LookupError(edition_id)
    task = enqueue_task(task_type=OCR_TASK, actor_id=actor_id, params={
        "pdf_path": str(pdf), "book_edition_id": edition_id, "start_page": 1, "page_count": 0})
    return {"edition_id": edition_id, "task_id": task.id, "poll_url": f"/api/tasks/{task.id}"}


def needs_reading(cell: Dict[str, Any]) -> bool:
    """A stored book with pages failed or not yet read."""
    total = cell.get("total_pages") or 0
    return bool(cell.get("pdf_stored")) and (cell["pages_failed"] > 0 or not total or cell["pages_read"] < total)


def queue_all_book_reads(cells: List[Dict[str, Any]], actor_id: Optional[str]) -> Dict[str, Any]:
    """Queue every stored book that still has pages to read; the worker reads them one after another."""
    busy = books_being_read()
    queued, already = [], []
    for cell in cells:
        if not needs_reading(cell):
            continue
        if cell["edition_id"] in busy:
            already.append(cell["edition_id"])
            continue
        queued.append(queue_book_read(cell["edition_id"], actor_id))
    return {"queued": queued, "already_reading": already}
