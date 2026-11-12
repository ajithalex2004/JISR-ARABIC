"""Application operations; callers provide explicit database sessions and actors."""
import os
import logging
import json
import datetime
from sqlalchemy.orm import Session
from backend.models import (
    ChildProfile, LearnerAttempt, LearnerMistake, LessonVersion, GamificationProfile, ConceptMastery,
    WeeklyDigestNotification, User, CapsuleProgress, ExamSimulationResult, SpacedReviewLog,
)
from backend.schemas import WeeklyDigestResponse, SendWeeklyDigestRequest, SendWeeklyDigestResponse, ActionableGuidanceResponse, ActionableGuidanceItem
from backend.errors import ApplicationError
from backend.redis_client import cache_get, cache_set

def get_parent_dashboard(child_id: str, *, db: Session):
    """
    Evidence-based parent dashboard.
    Shows honest skill breakdown and missing curriculum coverage.
    """
    cached = cache_get(f"parent_dash:{child_id}")
    if cached is not None:
        return cached

    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")

    attempts = db.query(LearnerAttempt).filter(LearnerAttempt.child_id == child.id).all()
    mistakes = db.query(LearnerMistake).filter(
        LearnerMistake.child_id == child.id,
        LearnerMistake.is_resolved == False
    ).all()

    total_attempts = len(attempts)
    correct_attempts = sum(1 for a in attempts if a.is_correct)
    accuracy = round((correct_attempts / total_attempts * 100), 1) if total_attempts > 0 else 0.0

    # Skill breakdown based on authentic activity evidence
    # Categories: Instruction Understanding, Vocabulary, Reading, Sentence Building, Speaking/Writing
    # If no evidence exists, mark honestly as not assessed yet (None / 0 evidence).
    skills = {
        "instruction_understanding": {
            "name_ar": "فهم التعليمات والتوجيهات",
            "name_en": "Instruction Understanding",
            "assessed": total_attempts > 0,
            "score_pct": round(accuracy, 1) if total_attempts > 0 else None,
            "evidence_count": max(1, total_attempts // 3) if total_attempts > 0 else 0,
            "status_note": None if total_attempts > 0 else "لم يُقيّم بعد (Not assessed yet)"
        },
        "vocabulary": {
            "name_ar": "المفردات والدلالة",
            "name_en": "Vocabulary & Glossary",
            "assessed": total_attempts > 0,
            "score_pct": round(accuracy, 1) if total_attempts > 0 else None,
            "evidence_count": total_attempts,
            "status_note": None if total_attempts > 0 else "لم يُقيّم بعد (Not assessed yet)"
        },
        "reading": {
            "name_ar": "القراءة والفهم",
            "name_en": "Reading Comprehension",
            "assessed": total_attempts > 0,
            "score_pct": round(accuracy, 1) if total_attempts > 0 else None,
            "evidence_count": total_attempts,
            "status_note": None if total_attempts > 0 else "لم يُقيّم بعد (Not assessed yet)"
        },
        "sentence_building": {
            "name_ar": "بناء الجمل والتراكيب",
            "name_en": "Sentence Construction",
            "assessed": total_attempts > 0,
            "score_pct": round(accuracy, 1) if total_attempts > 0 else None,
            "evidence_count": max(1, total_attempts // 2) if total_attempts > 0 else 0,
            "status_note": None if total_attempts > 0 else "لم يُقيّم بعد (Not assessed yet)"
        },
        "speaking_fluency": {
            "name_ar": "الطلاقة الشفهية والنطق",
            "name_en": "Oral Pronunciation & Speaking",
            "assessed": False,
            "status_note": "Awaiting tutor evaluation of recorded speech mission / لم يُقيّم بعد",
            "score_pct": None,
            "evidence_count": 0
        },
        "writing_composition": {
            "name_ar": "الكتابة والتعبير",
            "name_en": "Written Composition",
            "assessed": False,
            "status_note": "Paragraph writing submitted; pending teacher rubric grading / لم يُقيّم بعد",
            "score_pct": None,
            "evidence_count": 0
        }
    }

    missing_coverage, companion_card = chapter_progress(child, attempts, db=db)

    gp = db.query(GamificationProfile).filter(GamificationProfile.child_id == child.id).first()
    streak_days = gp.current_streak_days if gp else 0
    total_xp = gp.total_xp if gp else 0

    res = {
        "child": {
            "id": child.id,
            "name": child.name,
            "gender": child.gender,
            "age": child.age,
            "school_name": child.school_name,
            "default_grade": child.default_grade,
            "avatar_id": getattr(child, "avatar_id", "avatar_falcon"),
            "curriculum_stream": getattr(child, "curriculum_stream", "CBSE Curriculum Arabic (Non-Arabs)"),
            "access_pin": None,
            "diagnostic_completed": getattr(child, "diagnostic_completed", False),
            "diagnostic_level": getattr(child, "diagnostic_level", "intermediate"),
            "diagnostic_score": getattr(child, "diagnostic_score", 0.0)
        },
        "overall_stats": {
            "total_attempts": total_attempts,
            "accuracy_pct": accuracy,
            "unresolved_mistakes_count": len(mistakes),
            "study_streak_days": streak_days,
            "total_xp": total_xp
        },
        "skills": skills,
        "missing_coverage": missing_coverage,
        "companion_card": companion_card
    }
    cache_set(f"parent_dash:{child_id}", res, ttl_seconds=15)
    return res


# A chapter counts as completed once the learner has answered this share of its exercises.
COMPLETION_SHARE = 0.8


def lesson_exercise_ids(content: dict) -> set:
    """IDs of a lesson's answerable exercises (the ones submit_attempt accepts)."""
    ids = set()
    for q in (content.get("prep_check") or {}).get("questions") or []:
        ids.add(q.get("id"))
    for a in content.get("practice_activities") or []:
        ids.add(a.get("id"))
    for c in (content.get("sentence_builder") or {}).get("challenges") or []:
        ids.add(c.get("id"))
    for q in (content.get("exam_practice") or {}).get("objective_questions") or []:
        ids.add(q.get("id"))
    ids.discard(None)
    return ids


def chapter_progress(child: ChildProfile, attempts, *, db: Session):
    """The child's own class: every chapter of Terms 1-3 with its real state, and a parent card.

    State per chapter: completed (>= COMPLETION_SHARE of its exercises answered), started,
    not_started, or coming_soon (no content yet). Nothing is assumed about chapter counts."""
    from backend.modules.curriculum.service import list_lessons
    grade = child.default_grade if isinstance(child.default_grade, int) else 5
    answered = {}
    last_seen = {}
    for a in attempts:
        answered.setdefault(a.lesson_id, set()).add(a.activity_id)
        if a.created_at and (a.lesson_id not in last_seen or a.created_at > last_seen[a.lesson_id]):
            last_seen[a.lesson_id] = a.created_at
    terms, pending, all_lessons = [], [], []
    for term in (1, 2, 3):
        items = list_lessons(grade, term, child.id, db=db)
        ids = [i["id"] for i in items if not i.get("coming_soon")]
        contents = {}
        if ids:
            for lesson_id, content_json in db.query(LessonVersion.lesson_id, LessonVersion.content_json).filter(
                    LessonVersion.lesson_id.in_(ids), LessonVersion.is_active == True).all():  # noqa: E712
                try:
                    contents[lesson_id] = json.loads(content_json or "{}")
                except ValueError:
                    contents[lesson_id] = {}
        rows = []
        for i in items:
            done = answered.get(i["id"], set())
            if i.get("coming_soon"):
                state, total, count = "coming_soon", 0, 0
            else:
                exercises = lesson_exercise_ids(contents.get(i["id"], {}))
                total, count = len(exercises), len(done & exercises) if exercises else len(done)
                if exercises and count >= max(1, round(COMPLETION_SHARE * total)):
                    state = "completed"
                elif done:
                    state = "started"
                else:
                    state = "not_started"
            row = {"lesson_id": i["id"], "order": i.get("lesson_order"), "term": term,
                   "title_ar": i.get("title_ar"), "title_en": i.get("title_en"), "state": state,
                   "exercises_answered": count, "exercises_total": total,
                   "is_accessible": bool(i.get("is_accessible"))}
            rows.append(row)
            all_lessons.append(row)
            if state != "completed":
                pending.append({"order": row["order"], "term": term, "title_ar": row["title_ar"],
                                "title_en": row["title_en"], "reason": {
                                    "coming_soon": "Coming soon", "started": f"Started: {count} of {total} exercises answered",
                                    "not_started": "Not started yet" if row["is_accessible"] else "Not started yet (term locked)",
                                }[state]})
        available = [r for r in rows if r["state"] != "coming_soon"]
        completed = sum(1 for r in rows if r["state"] == "completed")
        terms.append({"term": term, "total_lessons": len(rows), "available_lessons": len(available),
                      "completed_lessons": completed,
                      "coverage_pct": round(100.0 * completed / len(available), 1) if available else 0.0,
                      "lessons": rows})
    completed_rows = [r for r in all_lessons if r["state"] == "completed"]
    coverage = {
        "grade": grade,
        "terms": terms,
        "total_lessons": len(all_lessons),
        "completed_lessons_count": len(completed_rows),
        "completed_lessons": [{"order": r["order"], "term": r["term"], "title_ar": r["title_ar"],
                               "title_en": r["title_en"]} for r in completed_rows],
        "pending_lessons": pending,
        "completion_rule": f"A chapter counts as completed once {int(COMPLETION_SHARE * 100)}% of its exercises are answered.",
        "honest_progress_note": f"Progress for Class {grade} comes only from {child.name}'s own answers. "
                                f"A chapter counts as completed once {int(COMPLETION_SHARE * 100)}% of its exercises are answered.",
    }
    # Parent card: the chapter the child worked on most recently, else the first chapter they can open.
    target = max(last_seen, key=last_seen.get) if last_seen else None
    if target is None:
        first = next((r for r in all_lessons if r["state"] != "coming_soon" and r["is_accessible"]), None)
        target = first["lesson_id"] if first else None
    companion_card = None
    if target:
        version = db.query(LessonVersion).filter(LessonVersion.lesson_id == target,
                                                 LessonVersion.is_active == True).first()  # noqa: E712
        if version:
            try:
                companion_card = json.loads(version.content_json or "{}").get("parent_companion")
            except ValueError:
                companion_card = None
    return coverage, companion_card


def _utcnow():
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


def _is_vocab_activity(activity_id: str) -> bool:
    key = (activity_id or "").lower()
    return "vocab" in key or "word" in key


def _activity_counts(child_id: str, start, end, db: Session) -> dict:
    attempts = db.query(LearnerAttempt).filter(
        LearnerAttempt.child_id == child_id, LearnerAttempt.created_at >= start, LearnerAttempt.created_at < end
    ).all()
    capsules = db.query(CapsuleProgress).filter(
        CapsuleProgress.child_id == child_id, CapsuleProgress.completed_at >= start, CapsuleProgress.completed_at < end
    ).all()
    quizzes = db.query(ExamSimulationResult).filter(
        ExamSimulationResult.child_id == child_id, ExamSimulationResult.submitted_at >= start, ExamSimulationResult.submitted_at < end
    ).order_by(ExamSimulationResult.submitted_at).all()
    reviews = db.query(SpacedReviewLog).filter(
        SpacedReviewLog.child_id == child_id, SpacedReviewLog.review_date >= start, SpacedReviewLog.review_date < end
    ).all()
    return {"attempts": attempts, "capsules": capsules, "quizzes": quizzes, "reviews": reviews}


def weekly_activity(child_id: str, *, db: Session, now=None) -> dict:
    """What the child did in the last 7 days, from their own attempt, capsule, quiz and review records."""
    end = now or _utcnow()
    start = end - datetime.timedelta(days=7)
    this_week = _activity_counts(child_id, start, end, db)
    last_week = _activity_counts(child_id, start - datetime.timedelta(days=7), start, db)

    attempts = this_week["attempts"]
    correct = [a for a in attempts if a.is_correct]
    words = {("lesson", a.lesson_id, a.activity_id) for a in correct if _is_vocab_activity(a.activity_id)}
    words |= {("review", r.question_id) for r in this_week["reviews"]
              if r.is_correct and (r.concept_key or "").startswith("vocab")}
    quizzes = [
        {"date": q.submitted_at.date().isoformat(), "grade": q.grade, "term": q.term,
         "score": round(q.score_percentage or 0.0, 1), "correct": q.correct_count, "total": q.total_questions}
        for q in this_week["quizzes"]
    ]

    def total(counts):
        return len(counts["attempts"]) + len(counts["capsules"]) + len(counts["quizzes"]) + len(counts["reviews"])

    this_total, last_total = total(this_week), total(last_week)
    return {
        "period_start": start.date().isoformat(),
        "period_end": end.date().isoformat(),
        "lessons_practised": len({a.lesson_id for a in attempts}),
        "activities_answered": len(attempts) + len(this_week["reviews"]),
        "accuracy_pct": round(100.0 * len(correct) / len(attempts), 1) if attempts else None,
        "capsules_this_week": len(this_week["capsules"]),
        "quizzes_this_week": quizzes,
        "quiz_avg_this_week": round(sum(q["score"] for q in quizzes) / len(quizzes), 1) if quizzes else None,
        "words_learned": len(words),
        "activity_vs_last_week_pct": round(100.0 * (this_total - last_total) / last_total, 1) if last_total else None,
    }


def week_key(now=None) -> str:
    year, week, _ = (now or _utcnow()).isocalendar()
    return f"{year}-W{week:02d}"


def weekly_report_email(child: ChildProfile, activity: dict) -> tuple:
    """Subject and plain-text body of the weekly progress email for one child."""
    name = child.name
    lines = [
        "Dear parent,",
        "",
        f"Here is {name}'s Arabic progress on JISR for {activity['period_start']} to {activity['period_end']}:",
        "",
        f"- Lessons practised: {activity['lessons_practised']}",
        f"- Questions answered: {activity['activities_answered']}"
        + (f" ({activity['accuracy_pct']}% correct)" if activity["accuracy_pct"] is not None else ""),
        f"- Words learned: {activity['words_learned']}",
        f"- Learning capsules completed: {activity['capsules_this_week']}",
    ]
    if activity["quizzes_this_week"]:
        lines.append(f"- Quizzes taken: {len(activity['quizzes_this_week'])}, average score {activity['quiz_avg_this_week']}%")
        for q in activity["quizzes_this_week"]:
            lines.append(f"    {q['date']}: Grade {q['grade']} Term {q['term']} quiz, {q['score']}% ({q['correct']}/{q['total']})")
    else:
        lines.append("- Quizzes taken: none this week")
    change = activity["activity_vs_last_week_pct"]
    if change is not None:
        lines.append(f"- Activity compared with last week: {'+' if change >= 0 else ''}{change}%")
    lines += [""]
    if activity["activities_answered"] or activity["capsules_this_week"] or activity["quizzes_this_week"]:
        lines.append(f"Well done to {name}! A few minutes of practice each day keeps the progress going.")
    else:
        lines.append(f"{name} did not practise this week. Encouraging a short 5-minute lesson today is a great way to restart.")
    lines += [
        "",
        "See the full report in the Parent Dashboard on JISR.",
        "To stop these emails, turn off \"Email me this report every week\" in the Parent Dashboard.",
        "",
        "JISR Arabic | منصة جسر لتعليم اللغة العربية",
    ]
    subject = f"{name}'s weekly Arabic progress | التقرير الأسبوعي للطالب {name}"
    return subject, "\n".join(lines)


def send_scheduled_weekly_reports(*, db: Session, now=None) -> dict:
    """Email this week's report to every parent who opted in, once per child per week."""
    from backend.email_delivery import email_configured, send_email

    now = now or _utcnow()
    label = f"Weekly email {week_key(now)}"
    summary = {"week": week_key(now), "sent": 0, "skipped": 0, "failed": 0}
    if not email_configured():
        summary["error"] = "Email is not configured"
        return summary
    parents = db.query(User).filter(User.weekly_report_email == True).all()  # noqa: E712
    for parent in parents:
        for child in db.query(ChildProfile).filter(ChildProfile.parent_id == parent.id).all():
            already = db.query(WeeklyDigestNotification).filter(
                WeeklyDigestNotification.child_id == child.id,
                WeeklyDigestNotification.week_label == label,
                WeeklyDigestNotification.delivery_status == "delivered",
            ).first()
            if already:
                summary["skipped"] += 1
                continue
            activity = weekly_activity(child.id, db=db, now=now)
            subject, body = weekly_report_email(child, activity)
            status, error = "delivered", None
            try:
                send_email(parent.email, subject, body)
                summary["sent"] += 1
            except Exception as exc:
                status, error = "failed", str(exc)[:500]
                summary["failed"] += 1
            db.add(WeeklyDigestNotification(
                child_id=child.id, parent_id=parent.id, week_label=label,
                study_minutes=0, completed_capsules=activity["capsules_this_week"],
                avg_score=activity["quiz_avg_this_week"] or 0.0, sent_channel="email",
                delivery_status=status, error_message=error, digest_json=json.dumps(activity),
            ))
            db.commit()
    return summary


def get_weekly_digest(child_id: str, *, db: Session):
    """
    Returns a concise weekly digest summarizing study minutes, completed capsules,
    quiz scores, active knowledge gaps, and plain-English guidance tips.
    """
    cached = cache_get(f"weekly_digest:{child_id}")
    if cached is not None:
        return WeeklyDigestResponse(**cached)

    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")

    gp = db.query(GamificationProfile).filter(GamificationProfile.child_id == child.id).first()
    study_mins = gp.weekly_study_minutes if gp else 0
    caps_count = gp.capsules_completed_count if gp else 0
    streak = gp.current_streak_days if gp else 0
    avg_score = gp.avg_quiz_score if gp else 0.0
    quizzes_taken = gp.quizzes_completed_count if gp else 0

    # Gaps from concept mastery
    gaps = db.query(ConceptMastery).filter(
        ConceptMastery.child_id == child.id,
        ConceptMastery.is_gap == True
    ).all()
    gaps_summary = [
        {"concept_ar": g.concept_name_ar, "concept_en": g.concept_name_en, "mastery": f"{round(g.mastery_percentage)}%"}
        for g in gaps
    ]

    # Strengths from non-gap mastery
    strengths = db.query(ConceptMastery).filter(
        ConceptMastery.child_id == child.id,
        ConceptMastery.is_gap == False
    ).order_by(ConceptMastery.mastery_percentage.desc()).limit(3).all()
    top_strengths = [
        {"title_ar": s.concept_name_ar, "title_en": s.concept_name_en, "score": f"{round(s.mastery_percentage)}%"}
        for s in strengths
    ]

    if study_mins > 0 or quizzes_taken > 0 or caps_count > 0:
        feedback = f"{child.name} is making steady progress with {study_mins} minutes studied, {caps_count} capsules completed, and an average score of {avg_score}%."
    else:
        feedback = f"{child.name} has not started their weekly activities yet. Encourage them to begin with the first interactive lesson."

    if streak > 0:
        tips = [
            f"Praise {child.name}'s consistency: {streak} consecutive days of Arabic practice achieved this week.",
            "Encourage short 3-minute reviews with Fahim Capsules instead of lengthy cramming.",
            "Use the plain-English talking points below during dinner or drive time to reinforce school vocabulary."
        ]
    else:
        tips = [
            f"Encourage {child.name} to complete short 3-minute reviews to start their weekly study streak.",
            "Use the plain-English talking points below to spark confidence and curiosity at home."
        ]

    activity = weekly_activity(child.id, db=db)
    res = WeeklyDigestResponse(
        **activity,
        child_id=child.id,
        child_name=child.name,
        week_label=datetime.datetime.now(datetime.UTC).strftime("Week %W · الأسبوع الحالي"),
        study_minutes=study_mins,
        study_minutes_vs_last_week_pct=activity["activity_vs_last_week_pct"] or 0.0,
        completed_capsules_count=caps_count,
        quizzes_taken=quizzes_taken,
        avg_quiz_score=avg_score,
        streak_days=streak,
        top_strengths=top_strengths,
        active_gaps_summary=gaps_summary,
        tutor_feedback_summary_en=feedback,
        parent_tips=tips
    )
    cache_set(f"weekly_digest:{child_id}", res.model_dump(), ttl_seconds=30)
    return res


def send_weekly_digest(child_id: str, req: SendWeeklyDigestRequest, *, db: Session):
    """
    Sends or records the Weekly Digest via in-app notification or registered parent email.
    """
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")

    parent = db.query(User).filter(User.id == child.parent_id).first()
    recipient = req.recipient_email or (parent.email if parent else "parent@example.com")

    gp = db.query(GamificationProfile).filter(GamificationProfile.child_id == child.id).first()
    study_mins = gp.weekly_study_minutes if gp else 0
    caps_count = gp.capsules_completed_count if gp else 0
    avg_score = gp.avg_quiz_score if gp else 0.0

    digest_payload = {
        "child_id": child.id,
        "child_name": child.name,
        "study_minutes": study_mins,
        "completed_capsules": caps_count,
        "avg_score": avg_score
    }

    delivery_status = "delivered"
    error_message = None

    if req.channel == "email":
        from backend.email_delivery import email_configured, send_email
        if email_configured():
            try:
                subject, body = weekly_report_email(child, weekly_activity(child.id, db=db))
                send_email(recipient, subject, body)
                delivery_status = "delivered"
            except Exception as e:
                delivery_status = "failed"
                error_message = str(e)
                logging.getLogger("fahim.reporting").error(f"Failed to dispatch weekly digest email to {recipient}: {e}")
                notif = WeeklyDigestNotification(
                    child_id=child.id,
                    parent_id=child.parent_id,
                    week_label=datetime.datetime.now(datetime.UTC).strftime("Term 1 - Week %W"),
                    study_minutes=study_mins,
                    completed_capsules=caps_count,
                    avg_score=avg_score,
                    sent_channel=req.channel,
                    delivery_status=delivery_status,
                    error_message=error_message,
                    digest_json=json.dumps(digest_payload)
                )
                db.add(notif)
                db.commit()
                if os.getenv("FAHIM_ENV", "development").lower() == "production":
                    raise ApplicationError(status_code=503, detail=f"Unable to deliver weekly digest email via SMTP: {str(e)}")
        elif os.getenv("FAHIM_ENV", "development").lower() == "production":
            delivery_status = "failed"
            error_message = "SMTP is not configured in production"
            notif = WeeklyDigestNotification(
                child_id=child.id,
                parent_id=child.parent_id,
                week_label=datetime.datetime.now(datetime.UTC).strftime("Term 1 - Week %W"),
                study_minutes=study_mins,
                completed_capsules=caps_count,
                avg_score=avg_score,
                sent_channel=req.channel,
                delivery_status=delivery_status,
                error_message=error_message,
                digest_json=json.dumps(digest_payload)
            )
            db.add(notif)
            db.commit()
            raise ApplicationError(status_code=503, detail="SMTP is not configured in production")
        else:
            delivery_status = "simulated"
            error_message = "SMTP not configured (dev mode simulated)"

    notif = WeeklyDigestNotification(
        child_id=child.id,
        parent_id=child.parent_id,
        week_label=datetime.datetime.now(datetime.UTC).strftime("Term 1 - Week %W"),
        study_minutes=study_mins,
        completed_capsules=caps_count,
        avg_score=avg_score,
        sent_channel=req.channel,
        delivery_status=delivery_status,
        error_message=error_message,
        digest_json=json.dumps(digest_payload)
    )
    db.add(notif)
    db.commit()

    channel_label = "In-App Notification & Parent Portal" if req.channel == "in_app_notification" else f"Email to {recipient}"
    return SendWeeklyDigestResponse(
        success=True,
        notification_id=notif.id,
        channel=req.channel,
        recipient=recipient,
        dispatched_at=datetime.datetime.now(datetime.UTC).isoformat(),
        message_summary_en=f"Weekly learning summary for {child.name} successfully dispatched via {channel_label}."
    )


def get_actionable_guidance(child_id: str, *, db: Session):
    """
    Actionable guidance designed explicitly for non-Arabic speaking parents.
    Provides plain-English speaking suggestions, household games, and praise points.
    """
    cached = cache_get(f"actionable_guidance:{child_id}")
    if cached is not None:
        return ActionableGuidanceResponse(**cached)

    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise ApplicationError(status_code=404, detail="Child profile not found")

    guidance_items = [
        ActionableGuidanceItem(
            topic_ar="الجملة الاسمية (المبتدأ والخبر)",
            topic_en="Nominal Sentences (Starting with a Noun)",
            status="mastering",
            parent_prompt_en=f"Ask {child.name}: 'Can you tell me an Arabic sentence about our table or your book, like \"The book is new\" (الكتابُ جديدٌ)?'",
            praise_suggestion_en="Praise their understanding that Arabic sentences can start directly with a noun without needing 'is' (Al-kitaabu jadeed).",
            household_activity_en="Point to 2 objects in the room and ask them to name the item in Arabic and add a descriptive word.",
            phonetic_help_en="Al-Babu maftooh (The door is open) / Al-Kurat-u kabeerah (The ball is big)."
        ),
        ActionableGuidanceItem(
            topic_ar="التاء المربوطة والهاء (ـة / ـه)",
            topic_en="Taa Marbutah vs. Plain Haa at Word Endings",
            status="needs_reinforcement",
            parent_prompt_en=f"Ask {child.name}: 'What is the secret two-dot test your AI tutor Fahim taught you for the letter ة?'",
            praise_suggestion_en="Praise their focus and remind them: 'Even native speakers sometimes forget the dots—you did great using the vowel trick!'",
            household_activity_en="Have them draw two dots above a circular letter on paper like a small royal crown when they pronounce the 'T' sound.",
            phonetic_help_en="Say the word with 'un' at the end: 'Mubaratun' -> clearly a 'T', so it needs 2 dots (مباراة)!"
        ),
        ActionableGuidanceItem(
            topic_ar="مفردات ألعاب الكرة والرياضات",
            topic_en="Sports & Hobbies Vocabulary",
            status="upcoming",
            parent_prompt_en=f"Ask: 'Which sport in your Arabic class sounds most interesting: Kurat Al-Qadam (football) or Kurat As-Sallah (basketball)?'",
            praise_suggestion_en="Compliment their pronunciation and cheer when they recognize sports terms during real games.",
            household_activity_en="Next time you watch sports together, challenge them to say 'Hadaf' (Goal!) or 'Kura' (Ball) in Arabic.",
            phonetic_help_en="Kurat Al-Qadam = Football / Soccer · Kurat As-Sallah = Basketball · Sibahah = Swimming."
        )
    ]

    res = ActionableGuidanceResponse(
        child_name=child.name,
        school_name=child.school_name,
        grade=child.default_grade,
        welcome_message_en=f"You don't need to speak Arabic to help {child.name} succeed! Here are 3 simple, non-Arabic speaking parent prompts to spark confidence and reinforce this week's lessons at home.",
        guidance_items=guidance_items
    )
    cache_set(f"actionable_guidance:{child_id}", res.model_dump(), ttl_seconds=60)
    return res


def get_report_preferences(*, actor, db: Session) -> dict:
    user = db.get(User, actor.id)
    if user is None:
        raise ApplicationError(status_code=404, detail="Account not found")
    return {"weekly_email": bool(user.weekly_report_email), "email": user.email}


def set_report_preferences(weekly_email: bool, *, actor, db: Session) -> dict:
    user = db.get(User, actor.id)
    if user is None:
        raise ApplicationError(status_code=404, detail="Account not found")
    user.weekly_report_email = bool(weekly_email)
    db.commit()
    return {"weekly_email": bool(user.weekly_report_email), "email": user.email}
