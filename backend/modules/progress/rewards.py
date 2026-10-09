"""Application operations; callers provide explicit database sessions and actors."""
from typing import Optional
from sqlalchemy.orm import Session
from backend.models import ChildProfile, GamificationProfile, LearnerBadge
from backend.schemas import GamificationProfileResponse, LearnerBadgeSchema, LeaderboardResponse, LeaderboardEntrySchema, AwardXPRequest, AwardXPResponse
from backend.errors import ApplicationError
from backend.modules.identity.access import visible_children

def _calculate_level_and_rank(total_xp: int):
    if total_xp < 300:
        level = 1
        xp_next = 300
        prog = (total_xp / 300.0) * 100
        rank_ar = "مستكشف الصحراء"
        rank_en = "Desert Explorer"
    elif total_xp < 700:
        level = 2
        xp_next = 700
        prog = ((total_xp - 300) / 400.0) * 100
        rank_ar = "فارس الكلمات"
        rank_en = "Knight of Words"
    elif total_xp < 1200:
        level = 3
        xp_next = 1200
        prog = ((total_xp - 700) / 500.0) * 100
        rank_ar = "صقر الفصاحة"
        rank_en = "Falcon of Eloquence"
    else:
        level = 4
        xp_next = 2000
        prog = min(100.0, ((total_xp - 1200) / 800.0) * 100)
        rank_ar = "حكيم الواحة"
        rank_en = "Oasis Sage"
    return level, xp_next, round(prog, 1), rank_ar, rank_en


def get_gamification_profile(child_id: str, *, db: Session):
    """
    Returns XP points, current learning streaks, level progress, heritage rank,
    and all unlocked and available mastery badges.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")

    profile = db.query(GamificationProfile).filter(GamificationProfile.child_id == child.id).first()
    if not profile:
        profile = GamificationProfile(
            child_id=child.id,
            total_xp=0,
            level=1,
            current_streak_days=0,
            longest_streak_days=0,
            weekly_study_minutes=0,
            capsules_completed_count=0,
            quizzes_completed_count=0,
            avg_quiz_score=0.0
        )
        db.add(profile)
        db.commit()

    level, xp_next, prog_pct, rank_ar, rank_en = _calculate_level_and_rank(profile.total_xp)
    profile.level = level
    profile.heritage_rank_ar = rank_ar
    profile.heritage_rank_en = rank_en
    db.commit()

    badges = db.query(LearnerBadge).filter(LearnerBadge.child_id == child.id).all()
    if not badges:
        # Default starter badges - all initially locked until earned by student
        initial_badges = [
            ("streak_champion", "بطل الاستمرارية", "Streak Champion", "حافظ على مذاكرة اللغة العربية 4 أيام متتالية", "Maintained an active 4-day Arabic study streak", "⚡", "streak", False),
            ("falcon_eye", "عين الصقر", "Falcon Eye", "أحرز درجة كاملة 100% في التقييم المبدئي", "Scored 100% on the baseline diagnostic assessment", "🦅", "mastery", False),
            ("capsule_master", "خبير الكبسولات", "Capsule Master", "أتم بنجاح 3 كبسولات لغوية سريعة", "Successfully completed 3 microlearning grammar capsules", "💊", "capsule", False),
            ("mistake_conqueror", "قاهر الأخطاء", "Mistake Conqueror", "صحح 3 أخطاء في دفتر المراجعة الذاتي", "Resolved 3 linguistic items in the Mistake Notebook", "🔍", "recovery", False),
            ("grammar_guru", "فارس النحو", "Grammar Guru", "أتقن مهارة إعراب المبتدأ والخبر بنسبة تفوق 85%", "Mastered nominal sentence syntax with 85%+ accuracy", "🏆", "grammar", False),
            ("reading_pro", "القارئ الماهر", "Fluent Reader", "أكمل قراءة نص ألعاب الكرة وفهم مفرداته", "Completed reading fluency for Ball Games text", "📖", "reading", False)
        ]
        for b_key, t_ar, t_en, d_ar, d_en, icon, cat, unlocked in initial_badges:
            b = LearnerBadge(
                child_id=child.id,
                badge_key=b_key,
                title_ar=t_ar,
                title_en=t_en,
                description_ar=d_ar,
                description_en=d_en,
                icon=icon,
                category=cat,
                is_unlocked=unlocked
            )
            db.add(b)
        db.commit()
        badges = db.query(LearnerBadge).filter(LearnerBadge.child_id == child.id).all()

    badge_schemas = [
        LearnerBadgeSchema(
            badge_key=b.badge_key,
            title_ar=b.title_ar,
            title_en=b.title_en,
            description_ar=b.description_ar,
            description_en=b.description_en,
            icon=b.icon,
            category=b.category,
            is_unlocked=b.is_unlocked,
            unlocked_at=b.unlocked_at.isoformat() if b.unlocked_at else None
        )
        for b in badges
    ]

    return GamificationProfileResponse(
        child_id=child.id,
        child_name=child.name,
        avatar_id=getattr(child, "avatar_id", "avatar_falcon"),
        total_xp=profile.total_xp,
        level=profile.level,
        xp_to_next_level=xp_next,
        level_progress_pct=prog_pct,
        heritage_rank_ar=profile.heritage_rank_ar,
        heritage_rank_en=profile.heritage_rank_en,
        current_streak_days=profile.current_streak_days,
        longest_streak_days=profile.longest_streak_days,
        weekly_study_minutes=profile.weekly_study_minutes,
        capsules_completed_count=profile.capsules_completed_count,
        quizzes_completed_count=profile.quizzes_completed_count,
        avg_quiz_score=round(profile.avg_quiz_score, 1),
        unlocked_badges_count=sum(1 for b in badges if b.is_unlocked),
        badges=badge_schemas
    )


def get_leaderboard(grade: int=5, school_name: Optional[str]=None, current_child_id: Optional[str]=None, *, actor, db: Session):
    """
    Returns the school/grade cohort leaderboard ranking peers by XP and active learning streaks.
    """
    query = visible_children(db, actor).filter(ChildProfile.default_grade == grade)
    if school_name:
        query = query.filter(ChildProfile.school_name == school_name)
    children = query.all()

    entries = []
    for c in children:
        gp = db.query(GamificationProfile).filter(GamificationProfile.child_id == c.id).first()
        xp = gp.total_xp if gp else 100
        streak = gp.current_streak_days if gp else 1
        entries.append({
            "child_id": c.id,
            "name": c.name,
            "avatar_id": getattr(c, "avatar_id", "avatar_falcon"),
            "school_name": c.school_name,
            "grade": c.default_grade,
            "total_xp": xp,
            "streak_days": streak,
            "is_current_user": (c.id == current_child_id)
        })

    # Sort descending by total_xp, then streak
    entries.sort(key=lambda x: (x["total_xp"], x["streak_days"]), reverse=True)

    leaderboard_schemas = []
    current_user_rank = 1
    for idx, e in enumerate(entries, start=1):
        if e["is_current_user"]:
            current_user_rank = idx
        leaderboard_schemas.append(
            LeaderboardEntrySchema(
                rank=idx,
                child_id=e["child_id"],
                name=e["name"],
                avatar_id=e["avatar_id"],
                school_name=e["school_name"],
                grade=e["grade"],
                total_xp=e["total_xp"],
                streak_days=e["streak_days"],
                is_current_user=e["is_current_user"]
            )
        )

    school_label = school_name or "Sunrise International School, Abu Dhabi"
    return LeaderboardResponse(
        cohort_title=f"Class {grade} Authorized Learners (المتعلمون المصرح بهم)",
        school_name=school_label,
        grade=grade,
        current_child_rank=current_user_rank,
        total_participants=len(entries),
        leaderboard=leaderboard_schemas
    )


def award_xp(req: AwardXPRequest, *, db: Session):
    """
    Awards experience points for lesson activities, capsules, or quizzes.
    Automatically checks for level milestones and new heritage ranks.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == req.child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")

    profile = db.query(GamificationProfile).filter(GamificationProfile.child_id == child.id).first()
    if not profile:
        profile = GamificationProfile(child_id=child.id, total_xp=0, level=1)
        db.add(profile)

    old_level = profile.level
    profile.total_xp += req.xp_amount
    new_level, _, _, rank_ar, rank_en = _calculate_level_and_rank(profile.total_xp)

    leveled_up = new_level > old_level
    profile.level = new_level
    profile.heritage_rank_ar = rank_ar
    profile.heritage_rank_en = rank_en
    db.commit()

    return AwardXPResponse(
        child_id=child.id,
        total_xp=profile.total_xp,
        level=new_level,
        xp_awarded=req.xp_amount,
        leveled_up=leveled_up,
        new_heritage_rank_ar=rank_ar if leveled_up else None,
        new_heritage_rank_en=rank_en if leveled_up else None
    )

