"""
Document Fingerprinting & Two-Tier Result Caching Service.

Provides:
  - L1: High-speed In-Memory Cache (sub-millisecond dictionary lookups)
  - L2: Persistent Database Cache via SQLAlchemy DocumentSolutionCache
  - Dual Fingerprinting:
      1. Cryptographic Content Hashing (SHA-256 of raw document bytes / base64)
      2. Semantic Text Normalization Hashing (stripped diacritics, whitespace-collapsed)

Prevents redundant AI model calls, reduces operational costs to $0.00 for duplicate
or shared worksheets across students, and cuts latency from 2-3 seconds down to <5ms.
"""

import os
import re
import json
import hashlib
import datetime
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from backend.observability import logger

# Bump when the way papers are answered changes: answers cached under an older version (e.g. long
# explanations, or answers made without reading the paper) are then never served again.
CACHE_VERSION = "answers-only-v2"

# L1 In-Memory Cache: {content_hash: {data, cached_at, hits, gen}}
_L1_MEMORY_CACHE: Dict[str, Dict[str, Any]] = {}
_MAX_L1_ENTRIES = 500

# Each API worker process keeps its own L1 copy. Clearing stored answers bumps this shared
# generation (Redis), so every worker drops L1 copies made before the clear.
_GENERATION_KEY = "papers:cache_generation"
_GENERATION_TTL_SECONDS = 10 * 365 * 24 * 3600


def _generation() -> str:
    try:
        from backend.redis_client import cache_get
        return str(cache_get(_GENERATION_KEY) or "0")
    except Exception:
        return "0"


def _bump_generation() -> None:
    import uuid
    try:
        from backend.redis_client import cache_set
        cache_set(_GENERATION_KEY, uuid.uuid4().hex, ttl_seconds=_GENERATION_TTL_SECONDS)
    except Exception as err:
        logger.warning(f"Could not bump the paper cache generation: {err}")


def _l1_get(content_hash: str) -> Optional[Dict[str, Any]]:
    entry = _L1_MEMORY_CACHE.get(content_hash)
    if entry is None:
        return None
    if entry.get("gen") != _generation():  # cleared by an admin (possibly in another worker)
        _L1_MEMORY_CACHE.pop(content_hash, None)
        return None
    return entry


def _l1_put(content_hash: str, entry: Dict[str, Any]) -> None:
    if content_hash not in _L1_MEMORY_CACHE and len(_L1_MEMORY_CACHE) >= _MAX_L1_ENTRIES:
        _L1_MEMORY_CACHE.pop(next(iter(_L1_MEMORY_CACHE)), None)
    _L1_MEMORY_CACHE[content_hash] = dict(entry, gen=_generation())


def _strip_arabic_tashkeel(text: str) -> str:
    """Remove Arabic vowels/harakat (fatha, damma, kasra, sukun, shadda, tanween) for semantic matching."""
    tashkeel_pattern = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
    return tashkeel_pattern.sub('', text)


def compute_content_hash(raw_data: Any) -> str:
    """Compute SHA-256 cryptographic fingerprint from raw base64 or bytes."""
    if not raw_data:
        return ""
    if isinstance(raw_data, str):
        # Strip data URL prefix if present
        if "," in raw_data:
            raw_data = raw_data.split(",", 1)[1]
        data_bytes = raw_data.encode("utf-8")
    elif isinstance(raw_data, bytes):
        data_bytes = raw_data
    else:
        data_bytes = str(raw_data).encode("utf-8")

    return hashlib.sha256(CACHE_VERSION.encode("utf-8") + b":" + data_bytes).hexdigest()


def compute_semantic_hash(text: Optional[str]) -> Optional[str]:
    """
    Compute normalized semantic fingerprint of document text content.
    Allows matching when photos of the same worksheet have different pixel hashes
    but identical text content.
    """
    if not text or not text.strip():
        return None

    cleaned = _strip_arabic_tashkeel(text.strip().lower())
    # Collapse multiple whitespaces and punctuation
    cleaned = re.sub(r'[\s\.,،؛:!\?\(\)\[\]\-]+', ' ', cleaned).strip()
    if len(cleaned) < 20:
        return None

    # Take leading representative window (up to 1200 characters)
    window = cleaned[:1200]
    return hashlib.sha256(f"{CACHE_VERSION}:{window}".encode("utf-8")).hexdigest()


def get_cached_paper(
    content_hash: str,
    semantic_hash: Optional[str] = None,
    db: Optional[Session] = None,
) -> Optional[Dict[str, Any]]:
    """
    Check L1 (in-memory) then L2 (database) for previously solved document solutions.
    Returns parsed dictionary or None.
    """
    if not content_hash and not semantic_hash:
        return None

    # 1. Check L1 Memory Cache
    entry = _l1_get(content_hash) if content_hash else None
    if entry is not None:
        entry["hit_count"] = entry.get("hit_count", 0) + 1
        entry["last_accessed_at"] = datetime.datetime.utcnow().isoformat()
        logger.info(f"[L1 Cache Hit] Found document {content_hash[:12]} in memory (Hits: {entry['hit_count']})")
        return entry.get("data")

    # 2. Check L2 Database Cache
    if db:
        try:
            from backend.models import DocumentSolutionCache
            record = None
            if content_hash:
                record = db.query(DocumentSolutionCache).filter_by(content_hash=content_hash).first()
            if not record and semantic_hash:
                record = db.query(DocumentSolutionCache).filter_by(semantic_hash=semantic_hash).first()

            if record:
                # Increment metrics
                record.hit_count = (record.hit_count or 0) + 1
                record.last_accessed_at = datetime.datetime.utcnow()
                try:
                    db.commit()
                except Exception as commit_err:
                    db.rollback()
                    logger.warning(f"Failed to commit cache hit increment: {commit_err}")

                parsed_data = {
                    "paper_title": record.paper_title or "Worksheet Solution",
                    "total_questions": record.total_questions or 0,
                    "file_name": record.file_name,
                    "file_type": record.file_type,
                    "questions": json.loads(record.questions_json),
                    "cached": True,
                    "hit_count": record.hit_count,
                }

                # Promote to L1 Memory Cache
                _l1_put(record.content_hash, {
                    "data": parsed_data,
                    "cached_at": (record.created_at or datetime.datetime.utcnow()).isoformat(),
                    "hit_count": record.hit_count,
                })

                logger.info(f"[L2 Cache Hit] Loaded document {record.content_hash[:12]} from DB (Hits: {record.hit_count})")
                return parsed_data
        except Exception as err:
            logger.warning(f"Error querying L2 document cache: {err}")

    return None


def save_cached_paper(
    content_hash: str,
    semantic_hash: Optional[str],
    file_name: Optional[str],
    file_type: str,
    paper_title: str,
    questions: List[Dict[str, Any]],
    db: Optional[Session] = None,
) -> None:
    """Save parsed question paper solutions into L1 Memory and L2 Database."""
    if not content_hash or not questions:
        return

    data = {
        "paper_title": paper_title,
        "total_questions": len(questions),
        "file_name": file_name,
        "file_type": file_type,
        "questions": questions,
        "cached": True,
        "hit_count": 1,
    }

    # 1. Save to L1 Memory Cache
    _l1_put(content_hash, {
        "data": data,
        "cached_at": datetime.datetime.utcnow().isoformat(),
        "hit_count": 1,
    })

    # 2. Save to L2 Database Cache
    if db:
        try:
            from backend.models import DocumentSolutionCache
            existing = db.query(DocumentSolutionCache).filter_by(content_hash=content_hash).first()
            if existing:
                existing.questions_json = json.dumps(questions, ensure_ascii=False)
                existing.paper_title = paper_title
                existing.total_questions = len(questions)
                existing.last_accessed_at = datetime.datetime.utcnow()
                existing.hit_count = (existing.hit_count or 0) + 1
            else:
                new_cache = DocumentSolutionCache(
                    content_hash=content_hash,
                    semantic_hash=semantic_hash,
                    file_name=file_name,
                    file_type=file_type,
                    paper_title=paper_title,
                    total_questions=len(questions),
                    questions_json=json.dumps(questions, ensure_ascii=False),
                    hit_count=1,
                    created_at=datetime.datetime.utcnow(),
                    last_accessed_at=datetime.datetime.utcnow(),
                )
                db.add(new_cache)
            db.commit()
            logger.info(f"[L2 Cache Stored] Saved document {content_hash[:12]} ({len(questions)} questions) to DB cache.")
        except Exception as err:
            if db:
                db.rollback()
            logger.warning(f"Failed to persist document solution to L2 cache: {err}")


def get_cached_question_answer(
    content_hash: str,
    question_number: int,
    semantic_hash: Optional[str] = None,
    db: Optional[Session] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieve specific question (e.g. Q1, Q9, Q13) directly from cached paper."""
    paper = get_cached_paper(content_hash, semantic_hash, db)
    if not paper or "questions" not in paper:
        return None

    for q in paper["questions"]:
        if q.get("question_number") == question_number:
            return q

    return None


# --- Admin: review and clear stored answers -----------------------------------------------------

def _iso(value) -> Optional[str]:
    return value.isoformat() if value else None


def list_cached_papers(db: Session, limit: int = 200) -> Dict[str, Any]:
    """Stored paper answers, most recently used first (without the answers themselves)."""
    from backend.models import DocumentSolutionCache
    query = db.query(DocumentSolutionCache)
    total = query.count()
    rows = query.order_by(DocumentSolutionCache.last_accessed_at.desc()).limit(limit).all()
    return {
        "total": total,
        "papers": [{
            "id": r.id,
            "paper_title": r.paper_title or r.file_name or "Untitled paper",
            "file_name": r.file_name,
            "file_type": r.file_type,
            "total_questions": r.total_questions or 0,
            "reuses": max(0, (r.hit_count or 1) - 1),  # the first save counts as 1
            "created_at": _iso(r.created_at),
            "last_accessed_at": _iso(r.last_accessed_at),
        } for r in rows],
    }


def get_cached_paper_detail(db: Session, paper_id: int) -> Optional[Dict[str, Any]]:
    """One stored paper with its questions and answers, for an admin to check."""
    from backend.models import DocumentSolutionCache
    record = db.get(DocumentSolutionCache, paper_id)
    if record is None:
        return None
    try:
        questions = json.loads(record.questions_json or "[]")
    except ValueError:
        questions = []
    return {
        "id": record.id,
        "paper_title": record.paper_title or record.file_name or "Untitled paper",
        "questions": [{
            "question_number": q.get("question_number"),
            "question_text_ar": q.get("question_text_ar"),
            "question_text_en": q.get("question_text_en"),
            "model_answer_ar": q.get("model_answer_ar"),
            "model_answer_en": q.get("model_answer_en"),
        } for q in questions if isinstance(q, dict)],
    }


def clear_cached_papers(db: Session, paper_id: Optional[int] = None) -> int:
    """Delete one stored paper (paper_id) or all of them; returns how many were deleted.

    The next upload of a cleared paper is read again by the AI. In-memory copies in every API
    worker are dropped too (shared generation), not only in this one.
    """
    from backend.models import DocumentSolutionCache
    query = db.query(DocumentSolutionCache)
    if paper_id is not None:
        query = query.filter(DocumentSolutionCache.id == paper_id)
    deleted = query.delete(synchronize_session=False)
    db.commit()
    _L1_MEMORY_CACHE.clear()
    _bump_generation()
    logger.info(f"[Cache Cleared] Removed {deleted} stored paper answer(s)"
                + (f" (paper {paper_id})" if paper_id is not None else " (all)"))
    return deleted
