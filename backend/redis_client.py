"""
Centralized Redis client, rate limiting, and session revocation cache for JISR.
Provides low-latency distributed rate limiting and token revocation across multiple API nodes,
with graceful thread-safe in-memory fallback for development environments.
"""
import os
import time
import json
import fnmatch
import copy
import logging
import threading
from collections import defaultdict, deque
from typing import Optional, Tuple, Any, Dict, List

logger = logging.getLogger("fahim.redis")

_redis_client = None
_redis_initialized = False
_redis_last_attempt = 0.0
_redis_retry_interval = 15.0  # seconds between reconnect attempts if offline

# Thread-safe in-memory fallback for local development or transient Redis disconnects
_fallback_lock = threading.Lock()
_fallback_rate_buckets = defaultdict(deque)
_fallback_revoked_tokens = set()
_fallback_revoked_users = set()
_fallback_cache: Dict[str, Tuple[float, Any]] = {}


def get_redis_client():
    """
    Returns an active Redis client, or None if Redis is unconfigured or unreachable.
    Employs a resilient backoff to avoid hammering unreachable servers on every request.
    """
    global _redis_client, _redis_initialized, _redis_last_attempt
    redis_url = os.getenv("REDIS_URL", "").strip()
    if not redis_url:
        return None

    now = time.monotonic()
    if _redis_client is not None:
        return _redis_client

    if _redis_initialized and (now - _redis_last_attempt < _redis_retry_interval):
        return None

    _redis_last_attempt = now
    _redis_initialized = True

    try:
        import redis
        client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_timeout=2.0,
            socket_connect_timeout=2.0,
            health_check_interval=30
        )
        client.ping()
        _redis_client = client
        logger.info(f"Connected to Redis for shared rate limiting and session caching ({redis_url.split('@')[-1]})")
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis connection failed ({e}). Falling back to thread-safe in-memory store.")
        _redis_client = None
        return None


def check_rate_limit(key: str, limit: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
    """
    Check and increment rate limit for a specific key (e.g. client IP + route path).
    Returns:
        (is_allowed: bool, current_count: int, retry_after: int)
    """
    client = get_redis_client()
    if client:
        try:
            redis_key = f"fahim:ratelimit:{key}"
            pipe = client.pipeline()
            pipe.incr(redis_key)
            pipe.ttl(redis_key)
            current_count, ttl = pipe.execute()
            if current_count == 1 or ttl < 0:
                client.expire(redis_key, window_seconds)
                ttl = window_seconds
            is_allowed = current_count <= limit
            retry_after = max(1, ttl if ttl > 0 else window_seconds)
            return is_allowed, current_count, retry_after
        except Exception as err:
            logger.warning(f"Redis rate-limit query failed: {err}; using in-memory fallback")

    # In-memory fallback
    with _fallback_lock:
        now = time.monotonic()
        bucket = _fallback_rate_buckets[key]
        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()
        if len(bucket) >= limit:
            oldest = bucket[0] if bucket else now
            retry_after = max(1, int(window_seconds - (now - oldest)))
            return False, len(bucket) + 1, retry_after
        bucket.append(now)
        return True, len(bucket), 0


def record_revoked_token(jti: str, ttl_seconds: int = 86400 * 7):
    """Mark a JWT token ID (jti) as revoked."""
    if not jti:
        return
    cache_delete(f"auth_principal:{jti}")
    client = get_redis_client()
    if client:
        try:
            client.setex(f"fahim:revoked_token:{jti}", ttl_seconds, "1")
            return
        except Exception as e:
            logger.warning(f"Failed to record revoked token in Redis: {e}")
    with _fallback_lock:
        _fallback_revoked_tokens.add(jti)


def record_revoked_user(user_id: str, ttl_seconds: int = 86400 * 7):
    """Mark all sessions for a user as revoked (e.g. upon password reset or account deletion)."""
    if not user_id:
        return
    cache_delete_pattern("auth_principal:*")
    client = get_redis_client()
    if client:
        try:
            client.setex(f"fahim:revoked_user:{user_id}", ttl_seconds, "1")
            return
        except Exception as e:
            logger.warning(f"Failed to record revoked user in Redis: {e}")
    with _fallback_lock:
        _fallback_revoked_users.add(user_id)


def is_session_revoked_in_cache(jti: Optional[str], user_id: Optional[str] = None) -> bool:
    """
    Fast sub-millisecond check to verify if a token or user has been revoked.
    Returns True if definitely revoked in cache, False otherwise.
    """
    if not jti:
        return True

    client = get_redis_client()
    if client:
        try:
            pipe = client.pipeline()
            pipe.exists(f"fahim:revoked_token:{jti}")
            if user_id:
                pipe.exists(f"fahim:revoked_user:{user_id}")
            results = pipe.execute()
            if any(results):
                return True
        except Exception as e:
            logger.debug(f"Redis session revocation check failed: {e}")

    with _fallback_lock:
        if jti in _fallback_revoked_tokens:
            return True
        if user_id and user_id in _fallback_revoked_users:
            return True

    return False


def record_student_active_session(child_id: str, jti: str, ttl_seconds: int = 86400 * 7):
    """
    Ensure only one active device session exists per student (child_id).
    Stores the most recently authenticated jti for the student.
    """
    if not child_id or not jti:
        return
    client = get_redis_client()
    if client:
        try:
            client.setex(f"fahim:student_active_session:{child_id}", ttl_seconds, jti)
            return
        except Exception as e:
            logger.warning(f"Failed to record student active session in Redis: {e}")
    with _fallback_lock:
        _fallback_cache[f"student_active_session:{child_id}"] = (time.monotonic() + ttl_seconds, jti)


def is_student_session_superseded(child_id: Optional[str], jti: Optional[str]) -> bool:
    """
    Checks if a student's session token (jti) has been superseded by a newer login on another device.
    Returns True if superseded, False if it is the currently active session.
    """
    if not child_id or not jti:
        return False
    client = get_redis_client()
    if client:
        try:
            active_jti = client.get(f"fahim:student_active_session:{child_id}")
            if active_jti and active_jti != jti:
                return True
        except Exception as e:
            logger.debug(f"Redis student active session check failed: {e}")

    with _fallback_lock:
        val = _fallback_cache.get(f"student_active_session:{child_id}")
        if val:
            expiry, active_jti = val
            if time.monotonic() < expiry and active_jti != jti:
                return True

    return False



def cache_set(key: str, value: Any, ttl_seconds: int = 3600) -> bool:
    """
    Store a JSON-serializable value in the distributed cache with a TTL.
    Falls back to thread-safe in-memory cache if Redis is unavailable.
    """
    client = get_redis_client()
    if client:
        try:
            payload = json.dumps(value, ensure_ascii=False)
            client.setex(f"fahim:cache:{key}", ttl_seconds, payload)
            return True
        except Exception as e:
            logger.warning(f"Redis cache_set failed for key {key}: {e}")

    with _fallback_lock:
        _fallback_cache[key] = (time.monotonic() + ttl_seconds, copy.deepcopy(value))
    return True


def cache_get(key: str) -> Optional[Any]:
    """
    Retrieve a cached value by key. Returns None on cache miss or expiration.
    """
    client = get_redis_client()
    if client:
        try:
            raw = client.get(f"fahim:cache:{key}")
            if raw is not None:
                return json.loads(raw)
            return None
        except Exception as e:
            logger.warning(f"Redis cache_get failed for key {key}: {e}")

    with _fallback_lock:
        entry = _fallback_cache.get(key)
        if entry is not None:
            expires_at, val = entry
            if time.monotonic() < expires_at:
                return copy.deepcopy(val)
            del _fallback_cache[key]
    return None


def cache_delete(key: str) -> bool:
    """Remove a specific key from the cache."""
    client = get_redis_client()
    if client:
        try:
            client.delete(f"fahim:cache:{key}")
        except Exception as e:
            logger.warning(f"Redis cache_delete failed for key {key}: {e}")

    with _fallback_lock:
        _fallback_cache.pop(key, None)
    return True


def cache_delete_pattern(pattern: str) -> int:
    """
    Delete all keys matching a glob pattern (e.g. 'lesson:*').
    Returns the count of deleted keys.
    """
    count = 0
    client = get_redis_client()
    if client:
        try:
            full_pattern = f"fahim:cache:{pattern}"
            keys_to_delete = []
            for k in client.scan_iter(match=full_pattern, count=100):
                keys_to_delete.append(k)
            if keys_to_delete:
                count = client.delete(*keys_to_delete)
        except Exception as e:
            logger.warning(f"Redis cache_delete_pattern failed for {pattern}: {e}")

    with _fallback_lock:
        matched = [k for k in _fallback_cache if fnmatch.fnmatch(k, pattern)]
        for k in matched:
            _fallback_cache.pop(k, None)
        count = max(count, len(matched))

    return count


def cache_clear() -> bool:
    """Flush all fahim cache entries."""
    cache_delete_pattern("*")
    with _fallback_lock:
        _fallback_cache.clear()
    return True


def invalidate_lesson_cache(lesson_id: str, grade: Optional[int] = None, term: Optional[int] = None):
    """Evict cached lesson content and associated syllabus/lesson lists."""
    cache_delete(f"lesson_package:{lesson_id}")
    if grade and term:
        cache_delete(f"lessons_base:{grade}:{term}")
    else:
        cache_delete_pattern("lessons_base:*")
    cache_delete_pattern("syllabus:*")


def invalidate_school_cache(school_id: Optional[str] = None):
    """Evict cached school or class listings."""
    cache_delete("schools:all")
    if school_id:
        cache_delete(f"school_classes:{school_id}")
    else:
        cache_delete_pattern("school_classes:*")


get_redis = get_redis_client


