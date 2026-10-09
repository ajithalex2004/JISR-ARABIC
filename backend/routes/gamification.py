from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.dependencies import get_current_user
from backend.modules.identity.access import Principal, require_child, optional_child
"""HTTP adapter: request parsing, dependency injection, and service delegation."""
from fastapi import APIRouter, Depends, Query
from backend.schemas import GamificationProfileResponse, LeaderboardResponse, AwardXPRequest, AwardXPResponse
from backend.modules.progress import rewards as service
router = APIRouter(prefix='/api/gamification', tags=['Gamification & Motivation'])

@router.get('/profile/{child_id}', response_model=GamificationProfileResponse)
def get_gamification_profile(child_id: str, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Returns XP points, current learning streaks, level progress, heritage rank,
    and all unlocked and available mastery badges.
    """
    require_child(db, actor, child_id)
    return service.get_gamification_profile(child_id=child_id, db=db)

@router.get('/leaderboard', response_model=LeaderboardResponse)
def get_leaderboard(grade: int=Query(5, description='Grade cohort'), school_name: Optional[str]=Query(None, description='Filter by school name'), current_child_id: Optional[str]=Query(None, description='Current child to rank'), db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Returns the school/grade cohort leaderboard ranking peers by XP and active learning streaks.
    """
    optional_child(db, actor, current_child_id)
    return service.get_leaderboard(grade=grade, school_name=school_name, current_child_id=current_child_id, db=db, actor=actor)

@router.post('/award-xp', response_model=AwardXPResponse)
def award_xp(req: AwardXPRequest, db: Session=Depends(get_db), actor: Principal=Depends(get_current_user)):
    """
    Awards experience points for lesson activities, capsules, or quizzes.
    Automatically checks for level milestones and new heritage ranks.
    """
    require_child(db, actor, req.child_id, ('admin',))
    return service.award_xp(req=req, db=db)
