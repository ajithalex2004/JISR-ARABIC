from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SignupRequest(BaseModel):
    email: str

class SendOtpResponse(BaseModel):
    success: bool
    message: str
    email: str
    debug_otp: Optional[str] = None  # development-only test adapter

class OtpVerifyRequest(BaseModel):
    email: str
    code: str
    purpose: str = "signup"

class CreatePasswordAndEnrollRequest(BaseModel):
    email: str
    code: str
    password: str
    # Child enrollment fields
    child_name: str
    child_gender: str = "Boy"
    child_age: int = 10
    child_school: str = "Sunrise International School, Abu Dhabi"
    child_grade: int = 5
    avatar_id: Optional[str] = "avatar_falcon"
    curriculum_stream: Optional[str] = "MoE / CBSE Arabic (Non-Arabs)"
    access_pin: Optional[str] = "1234"

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginOtpRequest(BaseModel):
    email: str

class LoginOtpVerifyRequest(BaseModel):
    email: str
    code: str

class StudentPinLoginRequest(BaseModel):
    parent_email: str
    pin: str
    child_id: Optional[str] = None

class AddChildRequest(BaseModel):
    name: str
    gender: str = "Boy"
    age: int = 10
    school_name: str = "Sunrise International School, Abu Dhabi"
    default_grade: int = 5
    avatar_id: Optional[str] = "avatar_falcon"
    curriculum_stream: Optional[str] = "MoE / CBSE Arabic (Non-Arabs)"
    access_pin: Optional[str] = "1234"

class UpdateChildRequest(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    school_name: Optional[str] = None
    default_grade: Optional[int] = None
    avatar_id: Optional[str] = None
    curriculum_stream: Optional[str] = None
    access_pin: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str

class ChildProfileSchema(BaseModel):
    id: str
    name: str
    gender: str
    age: int
    school_name: str
    default_grade: int
    avatar_id: Optional[str] = "avatar_falcon"
    curriculum_stream: Optional[str] = "MoE / CBSE Arabic (Non-Arabs)"
    access_pin: Optional[str] = "1234"
    diagnostic_completed: bool = False
    diagnostic_level: str = "intermediate"
    selected_term: int = 1
    diagnostic_score: float = 0.0
    diagnostic_details: Optional[str] = None
    learning_plan: Optional[str] = None
    unlocked_terms: List[str] = []
    is_unlocked: bool = False

class DiagnosticOptionSchema(BaseModel):
    id: int
    text_ar: str
    text_en: str

class DiagnosticQuestionSchema(BaseModel):
    id: str
    competency: str
    competency_ar: str
    competency_en: str
    difficulty: str
    passage_ar: Optional[str] = None
    question_ar: str
    question_en: str
    options: List[DiagnosticOptionSchema]

class SubmitDiagnosticRequest(BaseModel):
    child_id: str
    answers: Dict[str, int]

class CompetencyStatSchema(BaseModel):
    name_ar: str
    name_en: str
    correct: int
    total: int
    percentage: float

class MilestoneSchema(BaseModel):
    week: int
    title_ar: str
    title_en: str
    focus_ar: str
    focus_en: str
    target_activities: List[str]
    estimated_hours: float

class LearningPlanSchema(BaseModel):
    calibrated_level: str
    level_title_ar: str
    level_title_en: str
    level_summary_ar: str
    level_summary_en: str
    overall_score: float
    correct_count: int
    total_questions: int
    competency_breakdown: Dict[str, CompetencyStatSchema]
    strengths: List[str]
    growth_areas: List[str]
    recommended_grade: int
    stream: Optional[str] = None
    recommended_first_chapter: str
    milestones: List[MilestoneSchema]

class SubmitDiagnosticResponse(BaseModel):
    success: bool
    child_id: str
    score: float
    correct_count: int
    total_questions: int
    calibrated_level: str
    level_title_ar: str
    level_title_en: str
    competency_breakdown: Dict[str, Any]
    item_evaluations: List[Dict[str, Any]]
    learning_plan: LearningPlanSchema

class OnboardingProfileUpdateRequest(BaseModel):
    child_id: str
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    school_name: Optional[str] = None
    default_grade: Optional[int] = None
    selected_term: Optional[int] = None
    avatar_id: Optional[str] = None
    curriculum_stream: Optional[str] = None
    access_pin: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    phone_number: Optional[str] = None
    is_verified: bool
    school_id: Optional[str] = None
    children: List[ChildProfileSchema] = []

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    active_child: Optional[ChildProfileSchema] = None

class PaymentCheckoutRequest(BaseModel):
    child_id: str
    grade: int = 5
    term: int = 1
    terms: Optional[List[int]] = None
    include_ai: bool = True
    package_type: str = "term"
    payment_method: str = "card"
    card_number: Optional[str] = None
    exp_month: Optional[str] = None
    exp_year: Optional[str] = None
    cvc: Optional[str] = None
    cardholder_name: Optional[str] = None
    payment_token: Optional[str] = None
    promo_code: Optional[str] = None
    idempotency_key: Optional[str] = None
    provider_payment_id: Optional[str] = None

class AnnualCheckoutRequest(BaseModel):
    child_id: str
    grade: int = 5
    payment_method: str = "card"
    card_number: Optional[str] = None
    exp_month: Optional[str] = None
    exp_year: Optional[str] = None
    cvc: Optional[str] = None
    cardholder_name: Optional[str] = None
    payment_token: Optional[str] = None
    promo_code: Optional[str] = None
    idempotency_key: Optional[str] = None
    provider_payment_id: Optional[str] = None

class VoucherRedeemRequest(BaseModel):
    child_id: str
    grade: int = 5
    code: str

class VoucherRedeemResponse(BaseModel):
    success: bool
    message: str
    voucher_code: str
    package_type: str
    unlocked_terms: List[int]
    receipt_number: str
    school_name: Optional[str] = None

class TaxInvoiceItem(BaseModel):
    description_ar: str
    description_en: str
    qty: int = 1
    unit_price_usd: float
    discount_usd: float
    taxable_amount_usd: float
    vat_rate_pct: float = 5.0
    vat_amount_usd: float
    total_usd: float
    total_aed: float

class TaxInvoiceResponse(BaseModel):
    invoice_number: str
    trn: str = "100458923100003"
    issue_date: str
    parent_name: str
    parent_email: str
    student_name: str
    school_name: str
    grade: int
    package_type: str
    payment_method: str
    currency_usd: str = "USD"
    currency_aed: str = "AED"
    fx_rate: float = 3.6725
    subtotal_usd: float
    vat_amount_usd: float
    total_usd: float
    total_aed: float
    items: List[TaxInvoiceItem]
    status: str = "PAID"

class PaymentResponse(BaseModel):
    success: bool
    transaction_id: str
    receipt_number: str
    amount_usd: float
    grade: int
    term: int
    package_type: str = "term"
    unlocked_terms: List[int] = [1]
    subtotal_usd: float = 47.62
    vat_amount_usd: float = 2.38
    tax_invoice_number: Optional[str] = None
    status: str
    message: str

class TermStatusResponse(BaseModel):
    grade: int
    term: int
    is_unlocked: bool
    price_usd: float
    has_demo: bool
    demo_lesson_id: Optional[str] = None

class AttemptSubmitRequest(BaseModel):
    child_id: str
    lesson_id: str
    activity_id: str
    path_type: str = "guided"
    user_answer: Any
    client_score: Optional[float] = None  # Server rejects this and computes actual score
    idempotency_key: Optional[str] = None
    # Pin the attempt to the exact published package shown to the learner.
    # Older clients may omit this and will resolve the current active version.
    lesson_version_id: Optional[str] = None

class AttemptSubmitResponse(BaseModel):
    attempt_id: str
    is_correct: bool
    score: float
    max_score: float
    feedback_ar: str
    feedback_en: str
    correct_solution: Optional[Any] = None
    is_awaiting_tutor: bool = False

class TutorSubmissionRequest(BaseModel):
    child_id: str
    lesson_id: str
    activity_id: str
    submission_type: str = "writing"  # writing or speaking
    content_text: Optional[str] = None
    audio_url: Optional[str] = None

class TutorReviewRequest(BaseModel):
    submission_id: str
    tutor_score: float
    tutor_feedback: str

class AdminAddTermRequest(BaseModel):
    grade: int
    term: int
    title_ar: str
    title_en: str
    price_usd: float = 20.0

class AdminAddClassRequest(BaseModel):
    grade_number: int
    name_ar: str
    name_en: str

class ClassCreateRequest(BaseModel):
    id: str
    school_id: str
    name: str
    grade: int
    academic_year: Optional[str] = None

class ClassMembershipRequest(BaseModel):
    child_id: str

class TutorClassRequest(BaseModel):
    tutor_id: str

class AdminAddLessonRequest(BaseModel):
    unit_id: str
    grade: int
    term: int
    lesson_order: int
    title_ar: str
    title_en: str
    start_page: int
    content_json: Dict[str, Any]

class AdminUpdateEditionRequest(BaseModel):
    edition_id: str
    title: str
    academic_year: str
    publication_year: str
    total_pages: int
    pdf_filename: str

class AskFahimRequest(BaseModel):
    question: str = Field(..., max_length=2000)
    context_lesson_id: Optional[str] = "lesson_01_ball_games"
    child_id: Optional[str] = None
    voice_input: Optional[bool] = False
    attachment_base64: Optional[str] = Field(None, max_length=7000000)
    attachment_name: Optional[str] = Field(None, max_length=255)
    attachment_type: Optional[str] = Field(None, max_length=100)

class SocraticLearnRequest(BaseModel):
    topic: str = Field(..., max_length=200)
    student_input: str = Field(..., max_length=2000)
    conversation_history: List[Dict[str, str]] = []
    grade: int = 5
    child_id: Optional[str] = None

class SocraticLearnResponse(BaseModel):
    teacher_name: str
    tone: str  # "primary_gamified" or "middle_academic"
    response_ar: str
    response_en: str
    guiding_hint_ar: Optional[str] = None
    guiding_hint_en: Optional[str] = None
    is_step_mastered: bool = False
    next_socratic_prompt_ar: Optional[str] = None

class QuestionPaperSolveRequest(BaseModel):
    paper_title: Optional[str] = Field("UAE MoE Arabic Exam Paper", max_length=255)
    document_base64: Optional[str] = Field(None, max_length=7000000)
    mime_type: Optional[str] = Field("application/pdf", max_length=100)
    text_content: Optional[str] = Field(None, max_length=10000)
    grade: int = 5
    term: int = 1
    child_id: Optional[str] = None
    force_escalation: bool = False

class SolvedQuestion(BaseModel):
    question_number: int
    question_text_ar: str
    question_text_en: Optional[str] = None
    question_type: str = "mcq"
    model_answer_ar: str
    model_answer_en: str
    explanation_ar: str
    explanation_en: str
    textbook_reference: str
    lesson_id: Optional[str] = None
    rule_summary_ar: Optional[str] = None
    confidence: str = "high"
    escalated: bool = False
    escalation_reason: Optional[str] = None

class QuestionPaperSolveResponse(BaseModel):
    paper_title: str
    grade: int
    term: int
    total_questions: int
    questions: List[SolvedQuestion]
    model_used: str = "gemini-2.0-flash"
    escalation_summary: str = "All questions resolved autonomously using MoE curriculum grounding"

class SpeechEvaluationRequest(BaseModel):
    child_id: Optional[str] = None
    lesson_id: Optional[str] = "lesson_01_ball_games"
    target_phrase: str = Field(..., max_length=500)
    spoken_text: Optional[str] = Field(None, max_length=500)
    audio_base64: Optional[str] = Field(None, max_length=7000000)
    phoneme_targets: Optional[List[str]] = None

class SpeechEvaluationResponse(BaseModel):
    overall_score: float
    accuracy_percentage: float
    fluency_rating: str
    feedback_ar: str
    feedback_en: str
    phoneme_scores: Dict[str, float]
    detected_mistakes: List[str]
    target_phrase: str
    recognized_text: str
    is_pass: bool

class CapsuleCompleteRequest(BaseModel):
    child_id: str
    score: float = 100.0
    time_spent_seconds: int = 180
    answers: Dict[str, int] = {}
    idempotency_key: Optional[str] = None

class SubmitExamSimulationRequest(BaseModel):
    child_id: str
    grade: int = 5
    term: int = 1
    answers: Dict[str, int]
    time_taken_seconds: int
    idempotency_key: Optional[str] = None
    session_id: Optional[str] = None


# --- Mastery & Knowledge Gap Schemas ---
class ConceptMasteryItemSchema(BaseModel):
    concept_key: str
    concept_name_ar: str
    concept_name_en: str
    category: str
    mastery_percentage: float
    total_attempts: int
    correct_attempts: int
    is_gap: bool
    persistent_mistake_count: int
    status_label_en: str
    status_label_ar: str
    color_hex: str
    last_practiced_at: Optional[str] = None
    next_scheduled_review: Optional[str] = None

class MasteryHeatmapResponse(BaseModel):
    child_id: str
    child_name: str
    grade: int
    overall_mastery_pct: float
    total_concepts_tracked: int
    active_gaps_count: int
    concepts_by_category: Dict[str, List[ConceptMasteryItemSchema]]
    knowledge_gaps: List[ConceptMasteryItemSchema]

class GapReviewQuestion(BaseModel):
    id: str
    concept_key: str
    concept_name_ar: str
    concept_name_en: str
    prompt_ar: str
    prompt_en: str
    options: List[str]
    correct_index: int
    explanation_ar: str
    explanation_en: str

class GapReviewSessionResponse(BaseModel):
    child_id: str
    session_title_ar: str
    session_title_en: str
    targeted_gaps_count: int
    questions: List[GapReviewQuestion]

class RecordDrillAnswerRequest(BaseModel):
    child_id: str
    concept_key: str
    question_id: str
    selected_index: int
    is_correct: bool

class RecordDrillAnswerResponse(BaseModel):
    child_id: str
    concept_key: str
    new_mastery_pct: float
    is_gap_resolved: bool
    xp_awarded: int
    feedback_ar: str
    feedback_en: str


# --- Gamification & Motivation Schemas ---
class LearnerBadgeSchema(BaseModel):
    badge_key: str
    title_ar: str
    title_en: str
    description_ar: str
    description_en: str
    icon: str
    category: str
    is_unlocked: bool
    unlocked_at: Optional[str] = None

class GamificationProfileResponse(BaseModel):
    child_id: str
    child_name: str
    avatar_id: str
    total_xp: int
    level: int
    xp_to_next_level: int
    level_progress_pct: float
    heritage_rank_ar: str
    heritage_rank_en: str
    current_streak_days: int
    longest_streak_days: int
    weekly_study_minutes: int
    capsules_completed_count: int
    quizzes_completed_count: int
    avg_quiz_score: float
    unlocked_badges_count: int
    badges: List[LearnerBadgeSchema]

class LeaderboardEntrySchema(BaseModel):
    rank: int
    child_id: str
    name: str
    avatar_id: str
    school_name: str
    grade: int
    total_xp: int
    streak_days: int
    is_current_user: bool

class LeaderboardResponse(BaseModel):
    cohort_title: str
    school_name: str
    grade: int
    current_child_rank: int
    total_participants: int
    leaderboard: List[LeaderboardEntrySchema]

class AwardXPRequest(BaseModel):
    child_id: str
    activity_type: str  # capsule, lesson, exam, gap_drill, streak_bonus
    xp_amount: int
    reason: Optional[str] = None

class AwardXPResponse(BaseModel):
    child_id: str
    total_xp: int
    level: int
    xp_awarded: int
    leveled_up: bool
    new_heritage_rank_ar: Optional[str] = None
    new_heritage_rank_en: Optional[str] = None
    unlocked_badge: Optional[LearnerBadgeSchema] = None


# --- Parent Supervision Schemas ---
class ActionableGuidanceItem(BaseModel):
    topic_ar: str
    topic_en: str
    status: str  # mastering, needs_reinforcement, upcoming
    parent_prompt_en: str
    praise_suggestion_en: str
    household_activity_en: str
    phonetic_help_en: Optional[str] = None

class ActionableGuidanceResponse(BaseModel):
    child_name: str
    school_name: str
    grade: int
    welcome_message_en: str
    guidance_items: List[ActionableGuidanceItem]

class WeeklyDigestResponse(BaseModel):
    child_id: str
    child_name: str
    week_label: str
    study_minutes: int
    study_minutes_vs_last_week_pct: float
    completed_capsules_count: int
    quizzes_taken: int
    avg_quiz_score: float
    streak_days: int
    top_strengths: List[Dict[str, str]]
    active_gaps_summary: List[Dict[str, str]]
    tutor_feedback_summary_en: str
    parent_tips: List[str]

class SendWeeklyDigestRequest(BaseModel):
    channel: str = "in_app_notification"  # in_app_notification, email
    recipient_email: Optional[str] = None

class SendWeeklyDigestResponse(BaseModel):
    success: bool
    notification_id: str
    channel: str
    recipient: str
    dispatched_at: str
    message_summary_en: str


class UserFeedbackCreate(BaseModel):
    rating: int = 5
    category: str = "general"
    comment: str
    contact_email: Optional[str] = None
    grade: Optional[int] = 5
    child_id: Optional[str] = None


class UserFeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: str


class BulkEnrollLearnersRequest(BaseModel):
    learner_ids: List[str]


class BulkEnrollLearnersResponse(BaseModel):
    task_id: str
    status: str
    class_id: str
    total_learners: int
    poll_url: str


class AsyncAudioSynthesizeRequest(BaseModel):
    text: str
    speed: float = 1.0
    lang: str = "ar-SA"
    content_version: str = "1"


class AsyncAudioSynthesizeResponse(BaseModel):
    task_id: str
    status: str
    poll_url: str
