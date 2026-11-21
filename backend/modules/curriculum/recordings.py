"""Native-speaker recordings of exact Arabic texts (letters, syllables, words, sentences).

A recording replaces the synthetic voice wherever the app plays that text: /api/audio/synthesize
looks here first. Admins record in the browser or upload a file from Admin > Native audio, working
through the Foundation recording script (backend/foundation_data.recording_script).
"""
import hashlib
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.errors import ApplicationError
from backend.models import RecordedAudio

MAX_BYTES = 2 * 1024 * 1024  # a letter, word or sentence is a few seconds
ALLOWED_TYPES = {"audio/webm", "audio/ogg", "audio/mpeg", "audio/mp3", "audio/mp4", "audio/x-m4a", "audio/m4a",
                 "audio/aac", "audio/wav", "audio/x-wav", "audio/wave"}


def normalize(text: str) -> str:
    """The key a text is recorded under: the exact text, vowel marks included, with spaces collapsed."""
    return " ".join((text or "").split())


def recording_url(row: RecordedAudio) -> str:
    # The version (a hash of the clip) changes when a text is re-recorded, so browsers fetch the new one.
    version = hashlib.sha1(f"{row.id}:{row.size_bytes}:{row.created_at}".encode()).hexdigest()[:10]
    return f"/api/audio/recordings/{row.id}?v={version}"


def find_recording(db: Session, text: str) -> Optional[RecordedAudio]:
    key = normalize(text)
    if not key:
        return None
    return db.query(RecordedAudio).filter(RecordedAudio.text == key).first()


def lookup_url(text: str) -> Optional[str]:
    """The recording URL for a text, or None. Never fails the audio request it is part of."""
    from backend.database import SessionLocal
    try:
        db = SessionLocal()
    except Exception:
        return None
    try:
        row = db.query(RecordedAudio.id, RecordedAudio.size_bytes, RecordedAudio.created_at) \
            .filter(RecordedAudio.text == normalize(text)).first()
        return recording_url(row) if row else None
    except Exception:
        return None
    finally:
        db.close()


def save_recording(db: Session, text: str, data: bytes, mime_type: str, *, speaker: str = "",
                   actor_id: Optional[str] = None) -> RecordedAudio:
    key = normalize(text)
    if not key:
        raise ApplicationError(400, "The text to record is empty")
    if len(key) > 500:
        raise ApplicationError(400, "The text is too long (500 characters at most)")
    mime = (mime_type or "").split(";")[0].strip().lower()
    if mime not in ALLOWED_TYPES:
        raise ApplicationError(400, f"Unsupported audio type '{mime_type}'. Use webm, ogg, mp3, m4a or wav.")
    if not data:
        raise ApplicationError(400, "The recording is empty")
    if len(data) > MAX_BYTES:
        raise ApplicationError(413, "The recording is too large (2 MB at most)")
    row = find_recording(db, key)
    if row is None:
        row = RecordedAudio(text=key)
        db.add(row)
    import datetime
    row.audio, row.mime_type, row.size_bytes = data, mime, len(data)
    row.speaker = (speaker or "").strip()[:120] or None
    row.created_by = actor_id
    row.created_at = datetime.datetime.utcnow()
    db.commit()
    return row


def delete_recording(db: Session, recording_id: str) -> None:
    row = db.get(RecordedAudio, recording_id)
    if row is None:
        raise ApplicationError(404, "Recording not found")
    db.delete(row)
    db.commit()


def script_status(db: Session) -> Dict[str, Any]:
    """The Foundation recording script with what is recorded so far."""
    from backend.foundation_data import recording_script
    script = recording_script()
    rows = {r.text: r for r in db.query(RecordedAudio.id, RecordedAudio.text, RecordedAudio.size_bytes,
                                       RecordedAudio.created_at, RecordedAudio.speaker).all()}
    items: List[Dict[str, Any]] = []
    for item in script:
        row = rows.get(item["text"])
        items.append({**item, "recording_id": row.id if row else None,
                      "url": recording_url(row) if row else None, "speaker": row.speaker if row else None})
    done = sum(1 for i in items if i["recording_id"])
    return {"total": len(items), "recorded": done, "items": items}
