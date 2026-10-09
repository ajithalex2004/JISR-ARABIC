"""HTTP adapter: request parsing, dependency injection, and service delegation."""
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User
from backend.schemas import (
    SignupRequest, SendOtpResponse, OtpVerifyRequest, CreatePasswordAndEnrollRequest,
    LoginRequest, LoginOtpRequest, LoginOtpVerifyRequest, StudentPinLoginRequest,
    AddChildRequest, UpdateChildRequest, ForgotPasswordRequest, ResetPasswordRequest,
    AuthResponse, UserResponse, ChildProfileSchema
)
from backend.api.dependencies import get_current_user, require_role
from backend.modules.identity.access import Principal
from backend.modules.identity import service as service
from backend.observability import audit_event

router = APIRouter(prefix='/api/auth', tags=['Authentication'])

@router.post('/signup', response_model=SendOtpResponse)
def signup_request_otp(req: SignupRequest, db: Session=Depends(get_db)):
    """Request one-time OTP for first-time email signup."""
    return service.signup_request_otp(req=req, db=db)

@router.post('/verify-otp')
def verify_otp(req: OtpVerifyRequest, db: Session=Depends(get_db)):
    """Verify that the supplied OTP is valid and not expired."""
    return service.verify_otp(req=req, db=db)

@router.post('/create-password-enroll', response_model=AuthResponse)
def create_password_and_enroll(req: CreatePasswordAndEnrollRequest, db: Session=Depends(get_db)):
    """Complete signup: verify OTP, set password, and enroll child."""
    return service.create_password_and_enroll(req=req, db=db)

@router.post('/login', response_model=AuthResponse)
def login(req: LoginRequest, db: Session=Depends(get_db)):
    """Sign in with email ID and password. Automatically activates enrolled child profile."""
    result = service.login(req=req, db=db)
    audit_event("auth.login.success", user_id=getattr(getattr(result, "user", None), "id", None), method="password")
    return result

@router.post('/login-otp', response_model=SendOtpResponse)
def login_request_otp(req: LoginOtpRequest, db: Session=Depends(get_db)):
    """Request a 6-digit one-time password (OTP) for passwordless login."""
    return service.login_request_otp(req=req, db=db)

@router.post('/verify-login-otp', response_model=AuthResponse)
def verify_login_otp(req: LoginOtpVerifyRequest, db: Session=Depends(get_db)):
    """Authenticate and issue JWT session using verified login OTP."""
    return service.verify_login_otp(req=req, db=db)

@router.post('/student-pin-login', response_model=AuthResponse)
def student_pin_login(req: StudentPinLoginRequest, db: Session=Depends(get_db)):
    """Quick direct login for learners using Parent Email and 4-digit Student PIN."""
    result = service.student_pin_login(req=req, db=db)
    audit_event("auth.login.success", user_id=getattr(getattr(result, "user", None), "id", None), method="student_pin")
    return result

@router.get('/children', response_model=List[ChildProfileSchema])
def get_children(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    """Retrieve all linked child profiles for the authenticated parent or admin."""
    return service.get_children(user=user, db=db)

@router.post('/children', response_model=ChildProfileSchema)
def add_child(req: AddChildRequest, user: User=Depends(require_role(['parent', 'admin'])), db: Session=Depends(get_db)):
    """Add a new child profile to the parent account."""
    return service.add_child(req=req, user=user, db=db)

@router.patch('/children/{child_id}', response_model=ChildProfileSchema)
def update_child(child_id: str, req: UpdateChildRequest, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    """Update profile details, avatar, or PIN for a child."""
    return service.update_child(child_id=child_id, req=req, user=user, db=db)

@router.post('/switch-child/{child_id}', response_model=AuthResponse)
def switch_active_child(child_id: str, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    """Switch the active child profile for the parent session."""
    return service.switch_active_child(child_id=child_id, user=user, db=db)

@router.post('/forgot-password', response_model=SendOtpResponse)
def forgot_password_request_otp(req: ForgotPasswordRequest, db: Session=Depends(get_db)):
    """Forgot password request: generates reset OTP."""
    return service.forgot_password_request_otp(req=req, db=db)

@router.post('/reset-password')
def reset_password(req: ResetPasswordRequest, db: Session=Depends(get_db)):
    """Reset password using verified OTP."""
    return service.reset_password(req=req, db=db)

@router.post('/logout')
def logout(authorization: str = Header(None), actor: Principal=Depends(get_current_user), db: Session=Depends(get_db)):
    result = service.logout(authorization=authorization, db=db)
    audit_event("auth.logout", user_id=getattr(actor, "id", None))
    return result

@router.get('/me', response_model=UserResponse)
def get_current_user_profile(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    """Get authenticated user profile and children."""
    return service.get_current_user_profile(user=user, db=db)

@router.delete('/account')
def delete_account(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    """Permanently delete user account and all child learner data (App Store Guideline 5.1.1(v))."""
    result = service.delete_account(user=user, db=db)
    audit_event("auth.account_deleted", user_id=getattr(user, "id", None))
    return result
