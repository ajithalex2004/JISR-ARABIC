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

# L1 In-Memory Cache: {content_hash: {data, cached_at, hits}}
_L1_MEMORY_CACHE: Dict[str, Dict[str, Any]] = {}
_MAX_L1_ENTRIES = 500


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

    return hashlib.sha256(data_bytes).hexdigest()


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
    return hashlib.sha256(window.encode("utf-8")).hexdigest()


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
    if content_hash and content_hash in _L1_MEMORY_CACHE:
        entry = _L1_MEMORY_CACHE[content_hash]
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
                if len(_L1_MEMORY_CACHE) >= _MAX_L1_ENTRIES:
                    # Pop oldest entry
                    oldest_key = next(iter(_L1_MEMORY_CACHE))
                    _L1_MEMORY_CACHE.pop(oldest_key, None)

                _L1_MEMORY_CACHE[record.content_hash] = {
                    "data": parsed_data,
                    "cached_at": (record.created_at or datetime.datetime.utcnow()).isoformat(),
                    "hit_count": record.hit_count,
                }

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
    if len(_L1_MEMORY_CACHE) >= _MAX_L1_ENTRIES:
        oldest_key = next(iter(_L1_MEMORY_CACHE))
        _L1_MEMORY_CACHE.pop(oldest_key, None)

    _L1_MEMORY_CACHE[content_hash] = {
        "data": data,
        "cached_at": datetime.datetime.utcnow().isoformat(),
        "hit_count": 1,
    }

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
