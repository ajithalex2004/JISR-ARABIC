"""Bind request credentials and database sessions to identity services."""
from typing import List, Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.modules.identity import service
from backend.modules.identity.access import Principal


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> Principal:
    return service.get_current_user(authorization=authorization, db=db)


def get_optional_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> Optional[Principal]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return service.get_current_user(authorization=authorization, db=db)


def require_role(allowed_roles: List[str]):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access forbidden: requires one of {allowed_roles}",
            )
        return user
    return role_checker
