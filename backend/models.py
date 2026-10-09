import datetime
import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, UniqueConstraint, Index, Numeric
)
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    role = Column(String(50), default="parent")  # parent, tutor, admin, learner, school_admin
    school_id = Column(String(100), ForeignKey("schools.id"), nullable=True, index=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    children = relationship("ChildProfile", back_populates="parent", cascade="all, delete-orphan")


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), index=True, nullable=False)
    code = Column(String(128), nullable=False)  # bcrypt hash; plaintext is never persisted
    purpose = Column(String(50), nullable=False)  # 'signup', 'reset_password', 'login_otp'
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    attempt_count = Column(Integer, default=0, nullable=False)
    locked_at = Column(DateTime, nullable=True)


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    child_id = Column(String(36), nullable=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ChildProfile(Base):
    __tablename__ = "child_profiles"
    __table_args__ = (
        Index("ix_child_profiles_school_class", "school_id", "class_id"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    gender = Column(String(20), default="Boy")  # Boy, Girl, Other
    age = Column(Integer, default=10)
    school_name = Column(String(255), default="Sunrise International School, Abu Dhabi")
    school_id = Column(String(100), ForeignKey("schools.id"), nullable=True, index=True)
    class_id = Column(String(100), ForeignKey("school_classes.id"), nullable=True, index=True)
    default_grade = Column(Integer, default=5)
    selected_term = Column(Integer, default=1)
    avatar_id = Column(String(50), default="avatar_falcon")  # falcon, gazelle, palm, oryx, camel
    curriculum_stream = Column(String(100), default="MoE / CBSE Arabic (Non-Arabs)")
    access_pin = Column(String(128), nullable=True)
    diagnostic_completed = Column(Boolean, default=False)
    diagnostic_level = Column(String(50), default="intermediate")
    diagnostic_score = Column(Float, default=0.0)
    diagnostic_details = Column(Text, nullable=True)  # JSON string of skill breakdowns
    learning_plan = Column(Text, nullable=True)  # JSON string of personalized roadmap
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    parent = relationship("User", back_populates="children")
    term_accesses = relationship("TermAccess", back_populates="child", cascade="all, delete-orphan")


class TermAccess(Base):
    __tablename__ = "term_access"
    __table_args__ = (
        UniqueConstraint("child_id", "grade", "term", name="uq_term_access_scope"),
        Index("ix_term_access_lookup", "child_id", "grade", "term", "is_unlocked"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    grade = Column(Integer, nullable=False)
    term = Column(Integer, nullable=False)
    is_unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)
    transaction_ref = Column(String(100), nullable=True)

    child = relationship("ChildProfile", back_populates="term_accesses")


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    __table_args__ = (
        Index("ix_payments_child_created", "child_id", "created_at"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=True, index=True)
    anonymized_parent_id = Column(String(36), nullable=True)
    grade = Column(Integer, nullable=False)
    term = Column(Integer, nullable=False)
    amount_usd = Column(Numeric(10, 2), default=20.00)
    subtotal_usd = Column(Numeric(10, 2), default=47.62)
    vat_amount_usd = Column(Numeric(10, 2), default=2.38)
    discount_amount_usd = Column(Numeric(10, 2), default=0.00)
    amount_cents = Column(Integer, default=2000)
    currency = Column(String(10), default="USD")
    package_type = Column(String(50), default="term")  # term, annual
    status = Column(String(50), default="succeeded")
    payment_method = Column(String(50), default="card")  # card, voucher, school_license
    card_last4 = Column(String(10), default="4242")
    promo_code = Column(String(50), nullable=True)
    voucher_code = Column(String(50), nullable=True)
    receipt_number = Column(String(100), unique=True, nullable=False)
    tax_invoice_number = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    idempotency_key = Column(String(128), unique=True, nullable=True)
    provider_event_id = Column(String(128), unique=True, nullable=True)
    refunded_at = Column(DateTime, nullable=True)


class School(Base):
    __tablename__ = "schools"

    id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100), default="United Arab Emirates")
    curriculum_type = Column(String(100), default="CBSE & UAE Ministry")


class SchoolClass(Base):
    __tablename__ = "school_classes"
    id = Column(String(100), primary_key=True)
    school_id = Column(String(100), ForeignKey("schools.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    grade = Column(Integer, nullable=False)
    academic_year = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)


class ClassMembership(Base):
    __tablename__ = "class_memberships"
    __table_args__ = (
        Index("ix_class_memberships_child_id", "child_id"),
    )
    class_id = Column(String(100), ForeignKey("school_classes.id"), primary_key=True)
    child_id = Column(String(36), ForeignKey("child_profiles.id"), primary_key=True)
    role = Column(String(30), default="learner", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class TutorClassAssignment(Base):
    __tablename__ = "tutor_class_assignments"
    __table_args__ = (
        Index("ix_tutor_class_assignments_class_id", "class_id"),
    )
    tutor_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    class_id = Column(String(100), ForeignKey("school_classes.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class MembershipAuditEvent(Base):
    __tablename__ = "membership_audit_events"
    __table_args__ = (
        Index("ix_membership_audit_class_created", "class_id", "created_at"),
    )
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(40), nullable=False)
    class_id = Column(String(100), nullable=False)
    child_id = Column(String(36), nullable=True)
    tutor_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class CurriculumAuditEvent(Base):
    __tablename__ = "curriculum_audit_events"
    __table_args__ = (
        Index("ix_curriculum_audit_lesson_created", "lesson_id", "created_at"),
    )
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(50), nullable=False)  # rollback, approve, publish, import
    lesson_id = Column(String(100), nullable=False)
    version_id = Column(String(100), nullable=False)
    version_tag = Column(String(50), nullable=True)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)



class VoucherCode(Base):
    __tablename__ = "voucher_codes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)
    school_id = Column(String(100), ForeignKey("schools.id"), nullable=True)
    package_type = Column(String(50), default="annual")  # term, annual, discount
    discount_pct = Column(Float, default=100.0)
    max_redemptions = Column(Integer, default=500)
    redeemed_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class BookEdition(Base):
    __tablename__ = "book_editions"

    id = Column(String(100), primary_key=True)
    title = Column(String(255), nullable=False)
    series_name = Column(String(255), default="العربية تجمعنا")
    volume = Column(Integer, default=1)
    academic_year = Column(String(50), default="2023–2024")
    publication_year = Column(String(50), default="2023–2024")
    pdf_filename = Column(String(255), default="1693219092.pdf")
    total_pages = Column(Integer, default=108)


class CurriculumGrade(Base):
    __tablename__ = "curriculum_grades"

    id = Column(String(50), primary_key=True)  # e.g., "grade_5", "grade_6"
    grade_number = Column(Integer, unique=True, nullable=False, index=True)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class CurriculumTerm(Base):
    __tablename__ = "curriculum_terms"
    __table_args__ = (
        UniqueConstraint("grade", "term", name="uq_curriculum_grade_term"),
    )

    id = Column(String(50), primary_key=True)  # e.g., "grade_5_term_1"
    grade = Column(Integer, nullable=False, index=True)
    term = Column(Integer, nullable=False)
    title_ar = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=False)
    price_usd = Column(Numeric(10, 2), default=20.00)
    status = Column(String(50), default="ready_for_lessons")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Unit(Base):
    __tablename__ = "units"

    id = Column(String(100), primary_key=True)
    book_edition_id = Column(String(100), ForeignKey("book_editions.id"), nullable=False)
    unit_number = Column(Integer, nullable=False)
    title_ar = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=False)


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        Index("ix_lessons_grade_term_order", "grade", "term", "lesson_order"),
    )

    id = Column(String(100), primary_key=True)
    unit_id = Column(String(100), ForeignKey("units.id"), nullable=False, index=True)
    grade = Column(Integer, default=5)
    term = Column(Integer, default=1)
    lesson_order = Column(Integer, nullable=False)
    title_ar = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=False)
    start_page = Column(Integer, nullable=False)
    is_first_chapter_demo = Column(Boolean, default=False)
    status = Column(String(50), default="published")  # published, draft, content_pending, awaiting_textbook


class LessonVersion(Base):
    __tablename__ = "lesson_versions"
    __table_args__ = (
        Index("ix_lesson_versions_active", "lesson_id", "is_active"),
    )

    id = Column(String(100), primary_key=True)
    lesson_id = Column(String(100), ForeignKey("lessons.id"), nullable=False)
    version_tag = Column(String(50), default="0.2.0")
    content_json = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False)
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default="published", nullable=False)
    published_at = Column(DateTime, nullable=True)
    created_by = Column(String(36), nullable=True)
    reviewed_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class LearnerAttempt(Base):
    __tablename__ = "learner_attempts"
    __table_args__ = (
        Index("ix_learner_attempts_child_lesson", "child_id", "lesson_id"),
        Index("ix_learner_attempts_child_created", "child_id", "created_at"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=False)
    lesson_id = Column(String(100), ForeignKey("lessons.id"), nullable=False)
    lesson_version_id = Column(String(100), nullable=True)
    activity_id = Column(String(100), nullable=False)
    path_type = Column(String(50), default="guided")
    is_correct = Column(Boolean, default=False)
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=1.0)
    user_answer = Column(Text, nullable=True)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    idempotency_key = Column(String(128), unique=True, nullable=True)


class LearnerMistake(Base):
    __tablename__ = "learner_mistakes"
    __table_args__ = (
        Index("ix_learner_mistakes_child_resolved", "child_id", "is_resolved"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=False)
    lesson_id = Column(String(100), nullable=False)
    activity_id = Column(String(100), nullable=False)
    concept_name = Column(String(255), nullable=False)
    wrong_answer = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    review_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class TutorSubmission(Base):
    __tablename__ = "tutor_submissions"
    __table_args__ = (
        Index("ix_tutor_submissions_status_created", "status", "created_at"),
        Index("ix_tutor_submissions_tutor_status", "tutor_id", "status"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=False)
    lesson_id = Column(String(100), nullable=False)
    activity_id = Column(String(100), nullable=False)
    submission_type = Column(String(50), default="writing")  # writing, speaking
    content_text = Column(Text, nullable=True)
    audio_url = Column(String(500), nullable=True)
    tutor_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    tutor_score = Column(Float, nullable=True)
    tutor_feedback = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, reviewed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)


class ScannedPage(Base):
    __tablename__ = "scanned_pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_edition_id = Column(String(100), nullable=False)
    pdf_page = Column(Integer, nullable=False)
    printed_page = Column(Integer, nullable=False)
    ocr_text_ar = Column(Text, nullable=False)
    confidence = Column(Float, default=0.9)
    review_status = Column(String(50), default="automatic_unverified")


class CapsuleProgress(Base):
    __tablename__ = "capsule_progress"
    __table_args__ = (UniqueConstraint("child_id", "capsule_id", name="uq_capsule_progress"),)

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=False)
    capsule_id = Column(String(100), nullable=False)
    score = Column(Float, default=100.0)
    time_spent_seconds = Column(Integer, default=180)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)


class AssessmentSession(Base):
    __tablename__ = "assessment_sessions"
    __table_args__ = (
        Index("ix_assessment_sessions_child_status", "child_id", "status"),
    )
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    grade = Column(Integer, nullable=False)
    term = Column(Integer, nullable=False)
    bank_hash = Column(String(64), nullable=False)
    started_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="active", nullable=False)


class ExamSimulationResult(Base):
    __tablename__ = "exam_simulation_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=False)
    grade = Column(Integer, default=5)
    term = Column(Integer, default=1)
    score_percentage = Column(Float, default=0.0)
    correct_count = Column(Integer, default=0)
    total_questions = Column(Integer, default=10)
    time_taken_seconds = Column(Integer, default=0)
    session_id = Column(String(36), ForeignKey("assessment_sessions.id"), nullable=True)
    bloom_breakdown = Column(Text, nullable=True)  # JSON string
    item_responses = Column(Text, nullable=True)  # JSON string
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    idempotency_key = Column(String(128), unique=True, nullable=True)


class GamificationProfile(Base):
    __tablename__ = "gamification_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id"), unique=True, nullable=False)
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    heritage_rank_ar = Column(String(100), default="مستكشف الصحراء")
    heritage_rank_en = Column(String(100), default="Desert Explorer")
    current_streak_days = Column(Integer, default=1)
    longest_streak_days = Column(Integer, default=1)
    last_activity_date = Column(DateTime, default=datetime.datetime.utcnow)
    weekly_study_minutes = Column(Integer, default=0)
    capsules_completed_count = Column(Integer, default=0)
    quizzes_completed_count = Column(Integer, default=0)
    avg_quiz_score = Column(Float, default=0.0)


class LearnerBadge(Base):
    __tablename__ = "learner_badges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=False)
    badge_key = Column(String(50), nullable=False)
    title_ar = Column(String(100), nullable=False)
    title_en = Column(String(100), nullable=False)
    description_ar = Column(Text, nullable=False)
    description_en = Column(Text, nullable=False)
    icon = Column(String(20), default="🏆")
    category = Column(String(50), default="general")
    is_unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)


class ConceptMastery(Base):
    __tablename__ = "concept_mastery"
    __table_args__ = (UniqueConstraint("child_id", "concept_key", name="uq_concept_mastery"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=False)
    concept_key = Column(String(50), nullable=False)
    concept_name_ar = Column(String(100), nullable=False)
    concept_name_en = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # vocabulary, reading, grammar, orthography, speaking
    mastery_percentage = Column(Float, default=0.0)
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    is_gap = Column(Boolean, default=False)
    persistent_mistake_count = Column(Integer, default=0)
    last_practiced_at = Column(DateTime, default=datetime.datetime.utcnow)
    next_scheduled_review = Column(DateTime, nullable=True)
    interval_days = Column(Integer, default=1)
    ease_factor = Column(Float, default=2.5)
    repetition_count = Column(Integer, default=0)


class SpacedReviewLog(Base):
    __tablename__ = "spaced_review_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    concept_key = Column(String(50), nullable=False)
    question_id = Column(String(100), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    interval_days = Column(Integer, nullable=False)
    ease_factor = Column(Float, nullable=False)
    repetition_count = Column(Integer, default=1)
    review_date = Column(DateTime, default=datetime.datetime.utcnow)


class TutorAssignment(Base):
    """Explicit administrator-managed access; school names never grant access."""
    __tablename__ = "tutor_assignments"

    tutor_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    child_id = Column(String(36), ForeignKey("child_profiles.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class WeeklyDigestNotification(Base):
    __tablename__ = "weekly_digest_notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=False)
    parent_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    week_label = Column(String(100), default="Week 1")
    study_minutes = Column(Integer, default=0)
    completed_capsules = Column(Integer, default=0)
    avg_score = Column(Float, default=0.0)
    digest_json = Column(Text, nullable=True)
    sent_channel = Column(String(50), default="in_app_notification")
    delivery_status = Column(String(50), default="delivered")  # delivered, failed, pending
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class UserFeedback(Base):
    __tablename__ = "user_feedbacks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    child_id = Column(String(36), ForeignKey("child_profiles.id"), nullable=True)
    rating = Column(Integer, default=5)
    category = Column(String(50), default="general")  # feature, bug, curriculum, general
    comment = Column(Text, nullable=False)
    contact_email = Column(String(255), nullable=True)
    grade = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DocumentSolutionCache(Base):
    """
    Persistent L2 cache for question papers and worksheets.
    Stores extracted questions and verified model answers keyed by cryptographic content hash (SHA-256)
    and semantic fingerprint. Allows zero-cost, sub-millisecond retrieval when duplicate papers are uploaded.
    """
    __tablename__ = "document_solution_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_hash = Column(String(64), unique=True, index=True, nullable=False)
    semantic_hash = Column(String(64), index=True, nullable=True)
    file_name = Column(String(255), nullable=True)
    file_type = Column(String(50), default="pdf")
    paper_title = Column(String(255), nullable=True)
    total_questions = Column(Integer, default=0)
    questions_json = Column(Text, nullable=False)
    hit_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_accessed_at = Column(DateTime, default=datetime.datetime.utcnow)

