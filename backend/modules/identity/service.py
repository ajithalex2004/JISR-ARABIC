"""Application operations; callers provide explicit database sessions and actors."""
import datetime
import os
import secrets
import bcrypt
import jwt
from sqlalchemy.orm import Session
from typing import Optional
from backend.models import User, OtpCode, ChildProfile, TermAccess, UserSession
from backend.schemas import (
    SignupRequest, SendOtpResponse, OtpVerifyRequest, CreatePasswordAndEnrollRequest,
    LoginRequest, LoginOtpRequest, LoginOtpVerifyRequest, StudentPinLoginRequest,
    AddChildRequest, UpdateChildRequest, ForgotPasswordRequest, ResetPasswordRequest,
    AuthResponse, UserResponse, ChildProfileSchema
)
from backend.security import (
    hash_password, verify_password, create_access_token, decode_access_token,
    generate_otp_code, SECRET_KEY, ALGORITHM
)
from backend.errors import ApplicationError
from backend.modules.identity.access import (
    Principal, visible_children, require_child, require_roles, PARENT_ROLES
)
from backend.email_delivery import send_otp_email
from backend.redis_client import (
    is_session_revoked_in_cache, record_revoked_token, record_revoked_user,
    cache_get, cache_set, cache_delete, record_student_active_session, is_student_session_superseded
)

def serialize_child(c: ChildProfile) -> ChildProfileSchema:
    unlocked_list = []
    if hasattr(c, "term_accesses") and c.term_accesses:
        for a in c.term_accesses:
            if a.is_unlocked:
                unlocked_list.append(f"grade_{a.grade}_term_{a.term}")
    return ChildProfileSchema(
        id=c.id,
        name=c.name,
        gender=c.gender or "Boy",
        age=c.age or 10,
        school_name=c.school_name or "Sunrise International School, Abu Dhabi",
        default_grade=c.default_grade or 5,
        avatar_id=c.avatar_id or "avatar_falcon",
        curriculum_stream=c.curriculum_stream or "MoE / CBSE Arabic (Non-Arabs)",
        access_pin=None,
        diagnostic_completed=True,
        diagnostic_level=c.diagnostic_level or "standard",
        unlocked_terms=unlocked_list,
        is_unlocked=len(unlocked_list) > 0,
    )


def _register_session(token: str, user_id: str, db: Session, child_id: Optional[str] = None):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
    jti = payload["jti"]
    target_child_id = child_id or payload.get("child_id")
    is_learner = payload.get("role") == "learner" or payload.get("session_kind") == "learner"

    if target_child_id and is_learner:
        # Enforce single-device student login: revoke all previous active sessions for this child
        old_sessions = db.query(UserSession).filter(
            UserSession.child_id == target_child_id,
            UserSession.revoked_at.is_(None)
        ).all()
        for old_s in old_sessions:
            old_s.revoked_at = datetime.datetime.utcnow()
            record_revoked_token(old_s.id)
            cache_delete(f"auth_principal:{old_s.id}")
        record_student_active_session(target_child_id, jti)

    db.add(UserSession(
        id=jti,
        user_id=user_id,
        child_id=target_child_id if is_learner else None,
        expires_at=datetime.datetime.utcfromtimestamp(payload["exp"])
    ))
    db.commit()


def _pin_matches(value: str, stored: Optional[str]) -> bool:
    if not stored:
        return False
    try:
        return bcrypt.checkpw(value.encode(), stored.encode())
    except ValueError:
        return secrets.compare_digest(value, stored)


def _enforce_resend_cooldown(db: Session, email: str, purpose: str):
    is_prod = os.getenv("FAHIM_ENV", "development").lower() == "production"
    cooldown = 60 if is_prod else 5
    latest = db.query(OtpCode).filter(OtpCode.email == email, OtpCode.purpose == purpose).order_by(OtpCode.created_at.desc()).first()
    if latest and latest.created_at and (datetime.datetime.utcnow() - latest.created_at).total_seconds() < cooldown:
        remaining = int(cooldown - (datetime.datetime.utcnow() - latest.created_at).total_seconds())
        raise ApplicationError(429, f"Please wait {remaining}s before requesting another code.")


def _debug_otp(code: str) -> Optional[str]:
    # Production environments MUST NEVER expose OTP in response payloads under any circumstances
    if os.getenv("FAHIM_ENV", "development").lower() == "production":
        return None
    if not os.getenv("FAHIM_SMTP_HOST", "").strip() or os.getenv("FAHIM_EXPOSE_DEBUG_OTP", "0") == "1":
        return code
    return None


def get_current_user(authorization: Optional[str]=None, *, db: Session) -> Principal:
    if not authorization or not authorization.startswith("Bearer "):
        raise ApplicationError(
            status_code=401,
            detail="Missing or invalid authentication token"
        )
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise ApplicationError(
            status_code=401,
            detail="Session token expired or invalid"
        )
    jti = payload.get("jti")
    if not jti:
        raise ApplicationError(401, "Session is not revocable")
    user_id = payload.get("sub")
    role = payload.get("role")
    child_id = payload.get("child_id")

    # Enforce single device active session for student / learner
    if (role == "learner" or payload.get("session_kind") == "learner") and child_id:
        if is_student_session_superseded(child_id, jti):
            raise ApplicationError(401, "You have been logged out because this student account logged in from another device.")

    if is_session_revoked_in_cache(jti, user_id):
        raise ApplicationError(401, "Session has expired or was revoked")

    principal_cache_key = f"auth_principal:{jti}"
    cached_p = cache_get(principal_cache_key)
    if cached_p is not None:
        return Principal(
            id=cached_p["id"],
            email=cached_p["email"],
            role=cached_p["role"],
            is_verified=cached_p["is_verified"],
            phone_number=cached_p.get("phone_number"),
            child_id=cached_p.get("child_id"),
            school_id=cached_p.get("school_id")
        )

    if not db.query(UserSession).filter(UserSession.id == jti, UserSession.revoked_at.is_(None), UserSession.expires_at > datetime.datetime.utcnow()).first():
        raise ApplicationError(401, "Session has expired or was revoked")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ApplicationError(status_code=401, detail="User not found")
    role = payload.get("role")
    child_id = payload.get("child_id")
    if role == "learner":
        if payload.get("session_kind") != "learner" or user.role != "parent" or not isinstance(child_id, str) or not db.query(ChildProfile).filter(
            ChildProfile.id == child_id, ChildProfile.parent_id == user.id
        ).first():
            raise ApplicationError(401, "Invalid learner session")
    elif role not in ("parent", "tutor", "admin", "school_admin") or role != user.role:
        raise ApplicationError(401, "Session role is no longer valid")

    principal = Principal(
        id=user.id,
        email=user.email,
        role=role,
        is_verified=user.is_verified,
        phone_number=user.phone_number if role != "learner" else None,
        child_id=child_id,
        school_id=getattr(user, "school_id", None)
    )
    cache_set(principal_cache_key, {
        "id": principal.id,
        "email": principal.email,
        "role": principal.role,
        "is_verified": principal.is_verified,
        "phone_number": principal.phone_number,
        "child_id": principal.child_id,
        "school_id": principal.school_id
    }, ttl_seconds=60)
    return principal


def signup_request_otp(req: SignupRequest, *, db: Session):
    email_clean = req.email.strip().lower()
    _enforce_resend_cooldown(db, email_clean, "signup")
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise ApplicationError(status_code=400, detail="An account with this email already exists. Please log in.")
    db.query(OtpCode).filter(OtpCode.email == email_clean, OtpCode.purpose == "signup").update({"is_used": True})
    code = generate_otp_code()
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    otp_entry = OtpCode(
        email=email_clean,
        code=bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode(),
        purpose="signup",
        expires_at=expires_at,
        is_used=False
    )
    db.add(otp_entry)
    db.commit()
    sent = False
    try:
        sent = send_otp_email(email_clean, code, "signup")
    except Exception as e:
        logger.warning(f"Failed to deliver OTP email: {e}")

    is_prod = os.getenv("FAHIM_ENV", "development").lower() == "production"
    if is_prod and not sent:
        raise ApplicationError(503, "Unable to deliver verification code. Email delivery service is temporarily unavailable.")

    dbg = _debug_otp(code)
    has_smtp = bool(os.getenv("FAHIM_SMTP_HOST", "").strip())
    if not has_smtp and not is_prod:
        dbg = code
        msg = f"Verification code generated: {code} (Local/offline testing mode)."
    else:
        msg = f"OTP verification code sent to {email_clean}. Use the 6-digit code to complete signup."

    return SendOtpResponse(
        success=True,
        message=msg,
        email=email_clean,
        debug_otp=dbg
    )


def verify_otp(req: OtpVerifyRequest, *, db: Session):
    email_clean = req.email.strip().lower()
    now = datetime.datetime.utcnow()
    # In non-production, allow 123456 as a master development OTP bypass
    if os.getenv("FAHIM_ENV", "development").lower() != "production" and req.code.strip() == "123456":
        return {"success": True, "message": "OTP verified successfully. You may now create your password."}

    otp_record = db.query(OtpCode).filter(
        OtpCode.email == email_clean,
        OtpCode.purpose == req.purpose,
        OtpCode.is_used == False,
        OtpCode.expires_at > now
    ).order_by(OtpCode.created_at.desc()).first()
    if otp_record and (otp_record.attempt_count >= 5 or otp_record.locked_at or not bcrypt.checkpw(req.code.strip().encode(), otp_record.code.encode())):
        otp_record.attempt_count += 1
        if otp_record.attempt_count >= 5: otp_record.locked_at = now
        db.commit()
        otp_record = None
    if not otp_record:
        raise ApplicationError(status_code=400, detail="Invalid or expired OTP verification code.")
    return {"success": True, "message": "OTP verified successfully. You may now create your password."}


def create_password_and_enroll(req: CreatePasswordAndEnrollRequest, *, db: Session):
    email_clean = req.email.strip().lower()
    now = datetime.datetime.utcnow()
    is_dev = os.getenv("FAHIM_ENV", "development").lower() != "production"

    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise ApplicationError(status_code=400, detail="An account with this email already exists. Please log in.")

    if is_dev and req.code.strip() == "123456":
        # Master code used in development mode: mark any existing code as used
        db.query(OtpCode).filter(OtpCode.email == email_clean, OtpCode.purpose == "signup").update({"is_used": True})
        db.commit()
    else:
        otp_record = db.query(OtpCode).filter(
            OtpCode.email == email_clean,
            OtpCode.purpose == "signup",
            OtpCode.is_used == False,
            OtpCode.expires_at > now
        ).order_by(OtpCode.created_at.desc()).first()
        if otp_record and (otp_record.attempt_count >= 5 or otp_record.locked_at or not bcrypt.checkpw(req.code.strip().encode(), otp_record.code.encode())):
            otp_record.attempt_count += 1
            if otp_record.attempt_count >= 5: otp_record.locked_at = now
            db.commit()
            otp_record = None
        if not otp_record:
            raise ApplicationError(status_code=400, detail="Invalid or expired OTP code. Please request a new code.")
        otp_record.is_used = True
    user = User(
        email=email_clean,
        password_hash=hash_password(req.password),
        full_name=f"Parent of {req.child_name}",
        role="parent",
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    hashed_pin = bcrypt.hashpw(req.access_pin.strip().encode(), bcrypt.gensalt()).decode() if req.access_pin else None
    child = ChildProfile(
        parent_id=user.id,
        name=req.child_name,
        gender=req.child_gender or "Boy",
        age=req.child_age or 10,
        school_name=req.child_school or "Sunrise International School, Abu Dhabi",
        default_grade=req.child_grade or 5,
        avatar_id=req.avatar_id or "avatar_falcon",
        curriculum_stream=req.curriculum_stream or "MoE / CBSE Arabic (Non-Arabs)",
        access_pin=hashed_pin,
        diagnostic_completed=True,
        diagnostic_level="standard"
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    term_acc = TermAccess(child_id=child.id, grade=child.default_grade, term=1, is_unlocked=False)
    db.add(term_acc)
    db.commit()

    active_child = serialize_child(child)
    token_payload = {"sub": user.id, "email": user.email, "role": user.role, "child_id": child.id}
    access_token = create_access_token(token_payload)
    _register_session(access_token, user.id, db)
    user_resp = UserResponse(id=user.id, email=user.email, role=user.role, phone_number=user.phone_number, is_verified=user.is_verified, children=[active_child])
    return AuthResponse(access_token=access_token, token_type="bearer", user=user_resp, active_child=active_child)


def login(req: LoginRequest, *, db: Session):
    email_clean = req.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise ApplicationError(status_code=401, detail="Incorrect email or password.")
    if not verify_password(req.password, user.password_hash):
        raise ApplicationError(status_code=401, detail="Incorrect email or password.")
    children = db.query(ChildProfile).filter(ChildProfile.parent_id == user.id).all()
    for c in children:
        if not c.diagnostic_completed:
            c.diagnostic_completed = True
            c.diagnostic_level = c.diagnostic_level or "standard"
    if children:
        db.commit()
    if not children and user.role == "admin":
        admin_child = ChildProfile(
            parent_id=user.id,
            name="Admin Supervisor",
            gender="Boy",
            age=12,
            school_name="JISR Learning Platform",
            default_grade=5,
            avatar_id="avatar_falcon",
            curriculum_stream="MoE / CBSE Arabic (Non-Arabs)",
            diagnostic_completed=True,
            diagnostic_level="advanced"
        )
        db.add(admin_child)
        db.commit()
        db.refresh(admin_child)
        children = [admin_child]
    children_schemas = [serialize_child(c) for c in children]
    active_child = children_schemas[0] if children_schemas else None
    token_payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "child_id": active_child.id if active_child else None,
        "school_id": getattr(user, "school_id", None)
    }
    access_token = create_access_token(token_payload)
    _register_session(access_token, user.id, db)
    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        phone_number=user.phone_number,
        is_verified=user.is_verified,
        school_id=getattr(user, "school_id", None),
        children=children_schemas
    )
    return AuthResponse(access_token=access_token, token_type="bearer", user=user_resp, active_child=active_child)


def login_request_otp(req: LoginOtpRequest, *, db: Session):
    email_clean = req.email.strip().lower()
    _enforce_resend_cooldown(db, email_clean, "login_otp")
    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise ApplicationError(status_code=404, detail="No account found with this email. Please sign up first.")
    db.query(OtpCode).filter(OtpCode.email == email_clean, OtpCode.purpose == "login_otp").update({"is_used": True})
    code = generate_otp_code()
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    otp_entry = OtpCode(
        email=email_clean,
        code=bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode(),
        purpose="login_otp",
        expires_at=expires_at,
        is_used=False
    )
    db.add(otp_entry)
    db.commit()
    sent = False
    try:
        sent = send_otp_email(email_clean, code, "login")
    except Exception as e:
        logger.warning(f"Failed to deliver login OTP email: {e}")

    if os.getenv("FAHIM_ENV", "development").lower() == "production" and not sent:
        raise ApplicationError(503, "Unable to deliver verification code. Email delivery service is temporarily unavailable.")

    return SendOtpResponse(
        success=True,
        message=f"Login verification code sent to {email_clean}. Use the 6-digit code to sign in.",
        email=email_clean,
        debug_otp=_debug_otp(code)
    )


def verify_login_otp(req: LoginOtpVerifyRequest, *, db: Session):
    email_clean = req.email.strip().lower()
    now = datetime.datetime.utcnow()
    otp_record = db.query(OtpCode).filter(
        OtpCode.email == email_clean,
        OtpCode.purpose == "login_otp",
        OtpCode.is_used == False,
        OtpCode.expires_at > now
    ).order_by(OtpCode.created_at.desc()).first()
    if otp_record and (otp_record.attempt_count >= 5 or otp_record.locked_at or not bcrypt.checkpw(req.code.strip().encode(), otp_record.code.encode())):
        otp_record.attempt_count += 1
        if otp_record.attempt_count >= 5: otp_record.locked_at = now
        db.commit()
        otp_record = None
    if not otp_record:
        raise ApplicationError(status_code=400, detail="Invalid or expired login OTP. Please request a new code.")
    otp_record.is_used = True
    db.commit()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise ApplicationError(status_code=404, detail="User account not found.")
    children = db.query(ChildProfile).filter(ChildProfile.parent_id == user.id).all()
    children_schemas = [serialize_child(c) for c in children]
    active_child = children_schemas[0] if children_schemas else None
    token_payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "child_id": active_child.id if active_child else None,
        "school_id": getattr(user, "school_id", None)
    }
    access_token = create_access_token(token_payload)
    _register_session(access_token, user.id, db)
    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        phone_number=user.phone_number,
        is_verified=user.is_verified,
        school_id=getattr(user, "school_id", None),
        children=children_schemas
    )
    return AuthResponse(access_token=access_token, token_type="bearer", user=user_resp, active_child=active_child)


def student_pin_login(req: StudentPinLoginRequest, *, db: Session):
    email_clean = req.parent_email.strip().lower()
    pin_clean = req.pin.strip()
    parent = db.query(User).filter(User.email == email_clean).first()
    if not parent:
        raise ApplicationError(status_code=401, detail="Parent account not found for this email.")
    children = db.query(ChildProfile).filter(ChildProfile.parent_id == parent.id).all()
    if not children:
        raise ApplicationError(status_code=404, detail="No student profiles found under this parent account.")
    target_child = None
    if req.child_id:
        target_child = next((c for c in children if c.id == req.child_id), None)
    else:
        for c in children:
            if _pin_matches(pin_clean, c.access_pin):
                target_child = c
                break
    if not target_child or not _pin_matches(pin_clean, target_child.access_pin):
        raise ApplicationError(status_code=401, detail="Incorrect 4-digit PIN for this student. Please check with your parent.")
    if target_child.access_pin and not target_child.access_pin.startswith("$2"):
        target_child.access_pin = bcrypt.hashpw(pin_clean.encode(), bcrypt.gensalt()).decode()
        db.commit()
    active_child = serialize_child(target_child).model_copy(update={"access_pin": None})
    token_payload = {"sub": parent.id, "email": parent.email, "role": "learner", "child_id": target_child.id, "session_kind": "learner"}
    access_token = create_access_token(token_payload)
    _register_session(access_token, parent.id, db)
    children_schemas = [serialize_child(c).model_copy(update={"access_pin": None}) for c in children]
    user_resp = UserResponse(id=parent.id, email=parent.email, role="learner", phone_number=parent.phone_number, is_verified=parent.is_verified, children=children_schemas)
    return AuthResponse(access_token=access_token, token_type="bearer", user=user_resp, active_child=active_child)


def get_children(*, user: User, db: Session):
    children = visible_children(db, user).all()
    if user.role in ("learner", "tutor"):
        return [serialize_child(c).model_copy(update={"access_pin": None}) for c in children]
    return [serialize_child(c) for c in children]


def add_child(req: AddChildRequest, *, user: User, db: Session):
    require_roles(user, PARENT_ROLES)
    hashed_pin = bcrypt.hashpw(req.access_pin.strip().encode(), bcrypt.gensalt()).decode() if req.access_pin else None
    child = ChildProfile(
        parent_id=user.id,
        name=req.name.strip(),
        gender=req.gender or "Boy",
        age=req.age or 10,
        school_name=req.school_name or "Sunrise International School, Abu Dhabi",
        default_grade=req.default_grade or 5,
        avatar_id=req.avatar_id or "avatar_falcon",
        curriculum_stream=req.curriculum_stream or "MoE / CBSE Arabic (Non-Arabs)",
        access_pin=hashed_pin,
        diagnostic_completed=True,
        diagnostic_level="standard"
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    term_acc = TermAccess(child_id=child.id, grade=child.default_grade, term=1, is_unlocked=False)
    db.add(term_acc)
    db.commit()
    return serialize_child(child)


def update_child(child_id: str, req: UpdateChildRequest, *, user: User, db: Session):
    require_roles(user, PARENT_ROLES)
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")
    if child.parent_id != user.id and getattr(user, "role", None) != "admin":
        raise ApplicationError(status_code=403, detail="You do not have permission to edit this child profile")
    if req.name is not None: child.name = req.name.strip()
    if req.gender is not None: child.gender = req.gender
    if req.age is not None: child.age = req.age
    if req.school_name is not None: child.school_name = req.school_name
    if req.default_grade is not None: child.default_grade = req.default_grade
    if req.avatar_id is not None: child.avatar_id = req.avatar_id
    if req.curriculum_stream is not None: child.curriculum_stream = req.curriculum_stream
    if req.access_pin is not None:
        child.access_pin = bcrypt.hashpw(req.access_pin.strip().encode(), bcrypt.gensalt()).decode() if req.access_pin else None
    db.commit()
    db.refresh(child)
    return serialize_child(child)


def switch_active_child(child_id: str, *, user: User, db: Session):
    require_roles(user, PARENT_ROLES)
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")
    if child.parent_id != user.id and getattr(user, "role", None) != "admin":
        raise ApplicationError(status_code=403, detail="You do not have access to this child profile")
    children = db.query(ChildProfile).filter(ChildProfile.parent_id == user.id).all()
    children_schemas = [serialize_child(c) for c in children]
    active_child = serialize_child(child)
    token_payload = {"sub": user.id, "email": user.email, "role": user.role, "child_id": child.id}
    access_token = create_access_token(token_payload)
    _register_session(access_token, user.id, db)
    user_resp = UserResponse(id=user.id, email=user.email, role=user.role, phone_number=user.phone_number, is_verified=user.is_verified, children=children_schemas)
    return AuthResponse(access_token=access_token, token_type="bearer", user=user_resp, active_child=active_child)


def forgot_password_request_otp(req: ForgotPasswordRequest, *, db: Session):
    email_clean = req.email.strip().lower()
    _enforce_resend_cooldown(db, email_clean, "reset_password")
    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        return SendOtpResponse(success=True, message=f"If an account exists for {email_clean}, a password reset code was sent.", email=email_clean)
    db.query(OtpCode).filter(OtpCode.email == email_clean, OtpCode.purpose == "reset_password").update({"is_used": True})
    code = generate_otp_code()
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    otp_entry = OtpCode(
        email=email_clean,
        code=bcrypt.hashpw(code.encode(), bcrypt.gensalt()).decode(),
        purpose="reset_password",
        expires_at=expires_at,
        is_used=False
    )
    db.add(otp_entry)
    db.commit()
    sent = False
    try:
        sent = send_otp_email(email_clean, code, "password reset")
    except Exception as e:
        logger.warning(f"Failed to deliver reset password OTP email: {e}")

    if os.getenv("FAHIM_ENV", "development").lower() == "production" and not sent:
        raise ApplicationError(503, "Unable to deliver verification code. Email delivery service is temporarily unavailable.")

    return SendOtpResponse(
        success=True,
        message=f"Password reset OTP sent to {email_clean}.",
        email=email_clean,
        debug_otp=_debug_otp(code)
    )


def reset_password(req: ResetPasswordRequest, *, db: Session):
    email_clean = req.email.strip().lower()
    now = datetime.datetime.utcnow()
    otp_record = db.query(OtpCode).filter(
        OtpCode.email == email_clean,
        OtpCode.purpose == "reset_password",
        OtpCode.is_used == False,
        OtpCode.expires_at > now
    ).order_by(OtpCode.created_at.desc()).first()
    if otp_record and (otp_record.attempt_count >= 5 or otp_record.locked_at or not bcrypt.checkpw(req.code.strip().encode(), otp_record.code.encode())):
        otp_record.attempt_count += 1
        if otp_record.attempt_count >= 5: otp_record.locked_at = now
        db.commit()
        otp_record = None
    if not otp_record:
        raise ApplicationError(status_code=400, detail="Invalid or expired reset code.")
    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        raise ApplicationError(status_code=404, detail="User account not found.")
    otp_record.is_used = True
    user.password_hash = hash_password(req.new_password)
    record_revoked_user(user.id)
    db.query(UserSession).filter(UserSession.user_id == user.id, UserSession.revoked_at.is_(None)).update({"revoked_at": datetime.datetime.utcnow()})
    db.commit()
    return {"success": True, "message": "Your password has been reset successfully. Please sign in with your new password."}


def logout(authorization: Optional[str], *, db: Session):
    if authorization and authorization.startswith("Bearer "):
        payload = decode_access_token(authorization[7:].strip())
        if payload and payload.get("jti"):
            record_revoked_token(payload["jti"])
            db.query(UserSession).filter(UserSession.id == payload["jti"]).update({"revoked_at": datetime.datetime.utcnow()})
            db.commit()
    return {"success": True, "message": "Signed out."}


def get_current_user_profile(*, user: User, db: Session):
    children = visible_children(db, user).all()
    children_schemas = [serialize_child(c).model_copy(update={"access_pin": None}) if user.role in ("learner", "tutor", "school_admin") else serialize_child(c) for c in children]
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        phone_number=user.phone_number,
        is_verified=user.is_verified,
        school_id=getattr(user, "school_id", None),
        children=children_schemas
    )


def delete_account(*, user: User, db: Session):
    """
    Permanently deletes a user account and cascades all associated learner data,
    sessions, gamification records, and educational history.
    Mandated by Apple App Store Review Guideline 5.1.1(v) & GDPR / UAE Data Law.
    """
    from backend.models import (
        ChildProfile, ClassMembership, TermAccess, LearnerMistake,
        TutorSubmission, CapsuleProgress, AssessmentSession,
        ExamSimulationResult, GamificationProfile, LearnerBadge,
        ConceptMastery, SpacedReviewLog, TutorAssignment, WeeklyDigestNotification,
        PaymentTransaction, UserSession, OtpCode
    )
    user_id = user.id
    user_email = user.email

    # 1. Collect all children for this parent
    children = db.query(ChildProfile).filter(ChildProfile.parent_id == user_id).all()
    child_ids = [c.id for c in children]

    if child_ids:
        # 2. Delete all child-associated educational and progress records
        db.query(ClassMembership).filter(ClassMembership.child_id.in_(child_ids)).delete(synchronize_session=False)
        db.query(TermAccess).filter(TermAccess.child_id.in_(child_ids)).delete(synchronize_session=False)
        db.query(LearnerMistake).filter(LearnerMistake.child_id.in_(child_ids)).delete(synchronize_session=False)
        db.query(TutorSubmission).filter(TutorSubmission.child_id.in_(child_ids)).delete(synchronize_session=False)
        db.query(CapsuleProgress).filter(CapsuleProgress.child_id.in_(child_ids)).delete(synchronize_session=False)
        db.query(AssessmentSession).filter(AssessmentSession.child_id.in_(child_ids)).delete(synchronize_session=False)
        db.query(ExamSimulationResult).filter(ExamSimulationResult.child_id.in_(child_ids)).delete(synchronize_session=False)
        db.query(GamificationProfile).filter(GamificationProfile.child_id.in_(child_ids)).delete(synchronize_session=False)
        db.query(LearnerBadge).filter(LearnerBadge.child_id.in_(child_ids)).delete(synchronize_session=False)
        db.query(ConceptMastery).filter(ConceptMastery.child_id.in_(child_ids)).delete(synchronize_session=False)
        db.query(SpacedReviewLog).filter(SpacedReviewLog.child_id.in_(child_ids)).delete(synchronize_session=False)
        db.query(TutorAssignment).filter(TutorAssignment.child_id.in_(child_ids)).delete(synchronize_session=False)
        db.query(WeeklyDigestNotification).filter(WeeklyDigestNotification.child_id.in_(child_ids)).delete(synchronize_session=False)

        # Anonymize rather than delete PaymentTransactions to satisfy UAE FTA 5-year VAT statutory retention
        db.query(PaymentTransaction).filter(PaymentTransaction.child_id.in_(child_ids)).update({
            PaymentTransaction.anonymized_parent_id: user_id,
            PaymentTransaction.parent_id: None,
            PaymentTransaction.child_id: None,
            PaymentTransaction.promo_code: None,
        }, synchronize_session=False)

        # 3. Delete children profiles
        db.query(ChildProfile).filter(ChildProfile.id.in_(child_ids)).delete(synchronize_session=False)

    # 4. Delete user-level records
    db.query(WeeklyDigestNotification).filter(WeeklyDigestNotification.parent_id == user_id).delete(synchronize_session=False)

    # Anonymize parent transactions for UAE FTA retention
    db.query(PaymentTransaction).filter(PaymentTransaction.parent_id == user_id).update({
        PaymentTransaction.anonymized_parent_id: user_id,
        PaymentTransaction.parent_id: None,
        PaymentTransaction.child_id: None,
        PaymentTransaction.promo_code: None,
    }, synchronize_session=False)

    db.query(TutorAssignment).filter(TutorAssignment.tutor_id == user_id).delete(synchronize_session=False)
    record_revoked_user(user_id)
    db.query(UserSession).filter(UserSession.user_id == user_id).delete(synchronize_session=False)
    db.query(OtpCode).filter(OtpCode.email == user_email).delete(synchronize_session=False)

    # 5. Delete the User record
    db.query(User).filter(User.id == user_id).delete(synchronize_session=False)
    db.commit()

    return {
        "success": True,
        "message": "Account and all associated learner records permanently deleted."
    }
