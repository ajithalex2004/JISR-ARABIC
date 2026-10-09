import os
import datetime
import random
import secrets
import bcrypt
import jwt
from typing import Optional, Dict, Any

_configured_secret = os.environ.get("FAHIM_SECRET_KEY", "").strip()
if os.environ.get("FAHIM_ENV", "development").lower() == "production" and not _configured_secret:
    raise RuntimeError("FAHIM_SECRET_KEY is required in production; refusing to start with an ephemeral signing key")
# Development may use an ephemeral key, but production is always pinned to an
# operator-provided secret so restarts cannot silently invalidate or fork sessions.
SECRET_KEY = _configured_secret or secrets.token_urlsafe(48)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "jti": secrets.token_urlsafe(18)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None

def generate_otp_code() -> str:
    """Generate a 6-digit one-time passcode."""
    return f"{secrets.randbelow(900000) + 100000}"
