export interface ChildProfile {
  id: string;
  name: string;
  gender: string;
  age: number;
  school_name: string;
  default_grade: number;
  avatar_id?: string;
  curriculum_stream?: string;
  access_pin?: string;
  diagnostic_completed?: boolean;
  diagnostic_level?: string;
  selected_term?: number;
  diagnostic_score?: number;
  diagnostic_details?: string;
  learning_plan?: string;
}

export interface DiagnosticOption {
  id: number;
  text_ar: string;
  text_en: string;
}

export interface DiagnosticQuestion {
  id: string;
  competency: string;
  competency_ar: string;
  competency_en: string;
  difficulty: string;
  passage_ar?: string | null;
  question_ar: string;
  question_en: string;
  options: DiagnosticOption[];
}

export interface CompetencyStat {
  name_ar: string;
  name_en: string;
  correct: number;
  total: number;
  percentage: number;
}

export interface Milestone {
  week: number;
  title_ar: string;
  title_en: string;
  focus_ar: string;
  focus_en: string;
  target_activities: string[];
  estimated_hours: number;
}

export interface LearningPlan {
  calibrated_level: string;
  level_title_ar: string;
  level_title_en: string;
  level_summary_ar: string;
  level_summary_en: string;
  overall_score: number;
  correct_count: number;
  total_questions: number;
  competency_breakdown: Record<string, CompetencyStat>;
  strengths: string[];
  growth_areas: string[];
  recommended_grade: number;
  stream?: string;
  recommended_first_chapter: string;
  milestones: Milestone[];
}

export interface DiagnosticResult {
  success: boolean;
  child_id: string;
  score: number;
  correct_count: number;
  total_questions: number;
  calibrated_level: string;
  level_title_ar: string;
  level_title_en: string;
  competency_breakdown: Record<string, CompetencyStat>;
  item_evaluations: Array<{
    question_id: string;
    competency: string;
    selected_option: number | null;
    correct_option: number;
    is_correct: boolean;
    explanation_ar: string;
    explanation_en: string;
  }>;
  learning_plan: LearningPlan;
}

export interface User {
  id: string;
  email: string;
  role: 'parent' | 'tutor' | 'admin' | 'learner';
  phone_number?: string;
  is_verified: boolean;
  children: ChildProfile[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
  active_child?: ChildProfile;
}

export interface LessonSummary {
  id: string;
  unit_id: string;
  unit_title_ar: string;
  unit_title_en: string;
  lesson_order: number;
  title_ar: string;
  title_en: string;
  start_page: number;
  is_first_chapter_demo: boolean;
  is_accessible: boolean;
  status: 'published' | 'draft' | 'content_pending' | 'awaiting_textbook';
  lock_reason?: string;
}

export interface TermSummary {
  term: number;
  title_ar: string;
  title_en: string;
  price_usd: number;
  currency: string;
  is_unlocked: boolean;
  has_demo: boolean;
  demo_chapter_name?: string;
  status: string;
  status_label_en?: string;
}

export interface VocabularyCard {
  id: string;
  word_ar: string;
  vowelled_ar: string;
  meaning_en: string;
  definition_ar: string;
  example_ar: string;
  example_en: string;
  root: string;
  category: string;
}

export interface InstructionVerb {
  verb_ar: string;
  transliteration: string;
  meaning_en: string;
  action_guidance: string;
  sample_sentence_ar: string;
  sample_sentence_en: string;
}

export interface SentenceChallenge {
  id: string;
  target_en: string;
  target_ar: string;
  tiles: string[];
  distractors: string[];
}

export interface PracticeOption {
  id: string;
  label_ar: string;
  label_en: string;
}

export interface PracticeActivity {
  id: string;
  type: string;
  title_ar: string;
  title_en: string;
  prompt_ar: string;
  prompt_en: string;
  options: PracticeOption[];
  points: number;
}

export interface LessonPackage {
  lesson_id: string;
  version: string;
  title_ar: string;
  title_en: string;
  unit_title_ar: string;
  unit_title_en: string;
  grade: number;
  term: number;
  start_page: number;
  pdf_start_page: number;
  prep_check: {
    title_ar: string;
    title_en: string;
    description_en: string;
    questions: Array<{
      id: string;
      prompt_ar: string;
      prompt_en: string;
      options: PracticeOption[];
    }>;
  };
  learning_paths: {
    foundation: { title_ar: string; title_en: string; pacing: string; target: string };
    guided: { title_ar: string; title_en: string; pacing: string; target: string };
    independent: { title_ar: string; title_en: string; pacing: string; target: string };
  };
  instruction_decoder: InstructionVerb[];
  vocabulary_cards: VocabularyCard[];
  grammar_lab: {
    title_ar: string;
    title_en: string;
    sections: Array<{
      rule_name_ar: string;
      rule_name_en: string;
      explanation_en: string;
      examples: Array<{ phrase_ar: string; translation_en: string }>;
    }>;
  };
  sentence_builder: {
    title_ar: string;
    title_en: string;
    challenges: SentenceChallenge[];
  };
  listen_speak_studio: {
    title_ar: string;
    title_en: string;
    passage_ar: string;
    passage_en: string;
    audio_scripts: Array<{ id: string; text_ar: string; text_en: string }>;
  };
  practice_activities: PracticeActivity[];
  speaking_mission: {
    title_ar: string;
    title_en: string;
    scenario_en: string;
    prompts_ar: string[];
    prompts_en?: string[];
    recording_task_en: string;
  };
  parent_companion: {
    title_ar: string;
    title_en: string;
    summary_en: string;
    dinner_table_prompts: Array<{ arabic: string; english: string; phonetic: string }>;
    home_practice_checklist: string[];
  };
  tutor_handover: {
    title_ar: string;
    title_en: string;
    learner_focus: string;
    unobserved_fields_note: string;
    rubric_categories: Array<{ key: string; name_en: string; weight: string }>;
  };
  exam_practice: {
    title_ar: string;
    title_en: string;
    total_marks: number;
    objective_questions: Array<{
      id: string;
      prompt_ar: string;
      prompt_en: string;
      options: PracticeOption[];
      marks: number;
    }>;
    writing_task: {
      id: string;
      prompt_ar: string;
      prompt_en: string;
      marks: number;
    };
  };
  spaced_recall: {
    title_ar: string;
    title_en: string;
    linked_concepts: Array<{
      concept_name_ar: string;
      concept_name_en: string;
      source_lesson: string;
      target_lesson: string;
      recall_question_ar: string;
      recall_question_en: string;
    }>;
  };
}

export interface MistakeEntry {
  id: number;
  lesson_id: string;
  activity_id: string;
  concept_name: string;
  wrong_answer: string;
  correct_answer: string;
  is_resolved: boolean;
  review_count: number;
  created_at: string;
}

// --- Mastery & Knowledge Gap Interfaces ---
export interface ConceptMasteryItem {
  concept_key: string;
  concept_name_ar: string;
  concept_name_en: string;
  category: string;
  mastery_percentage: number;
  total_attempts: number;
  correct_attempts: number;
  is_gap: boolean;
  persistent_mistake_count: number;
  status_label_en: string;
  status_label_ar: string;
  color_hex: string;
  last_practiced_at?: string | null;
  next_scheduled_review?: string | null;
}

export interface MasteryHeatmapData {
  child_id: string;
  child_name: string;
  grade: number;
  overall_mastery_pct: number;
  total_concepts_tracked: number;
  active_gaps_count: number;
  concepts_by_category: Record<string, ConceptMasteryItem[]>;
  knowledge_gaps: ConceptMasteryItem[];
}

export interface GapReviewQuestion {
  id: string;
  concept_key: string;
  concept_name_ar: string;
  concept_name_en: string;
  prompt_ar: string;
  prompt_en: string;
  options: string[];
  correct_index: number;
  explanation_ar: string;
  explanation_en: string;
}

export interface GapReviewSession {
  child_id: string;
  session_title_ar: string;
  session_title_en: string;
  targeted_gaps_count: number;
  questions: GapReviewQuestion[];
}

export interface RecordDrillResponse {
  child_id: string;
  concept_key: string;
  new_mastery_pct: number;
  is_gap_resolved: boolean;
  xp_awarded: number;
  feedback_ar: string;
  feedback_en: string;
}

// --- Gamification & Motivation Interfaces ---
export interface LearnerBadge {
  badge_key: string;
  title_ar: string;
  title_en: string;
  description_ar: string;
  description_en: string;
  icon: string;
  category: string;
  is_unlocked: boolean;
  unlocked_at?: string | null;
}

export interface GamificationProfile {
  child_id: string;
  child_name: string;
  avatar_id: string;
  total_xp: number;
  level: number;
  xp_to_next_level: number;
  level_progress_pct: number;
  heritage_rank_ar: string;
  heritage_rank_en: string;
  current_streak_days: number;
  longest_streak_days: number;
  weekly_study_minutes: number;
  capsules_completed_count: number;
  quizzes_completed_count: number;
  avg_quiz_score: number;
  unlocked_badges_count: number;
  badges: LearnerBadge[];
}

export interface LeaderboardEntry {
  rank: number;
  child_id: string;
  name: string;
  avatar_id: string;
  school_name: string;
  grade: number;
  total_xp: number;
  streak_days: number;
  is_current_user: boolean;
}

export interface LeaderboardData {
  cohort_title: string;
  school_name: string;
  grade: number;
  current_child_rank: number;
  total_participants: number;
  leaderboard: LeaderboardEntry[];
}

// --- Parent Supervision Interfaces ---
export interface ActionableGuidanceItem {
  topic_ar: string;
  topic_en: string;
  status: 'mastering' | 'needs_reinforcement' | 'upcoming';
  parent_prompt_en: string;
  praise_suggestion_en: string;
  household_activity_en: string;
  phonetic_help_en?: string;
}

export interface ActionableGuidanceData {
  child_name: string;
  school_name: string;
  grade: number;
  welcome_message_en: string;
  guidance_items: ActionableGuidanceItem[];
}

export interface WeeklyDigestData {
  child_id: string;
  child_name: string;
  week_label: string;
  study_minutes: number;
  study_minutes_vs_last_week_pct: number;
  completed_capsules_count: number;
  quizzes_taken: number;
  avg_quiz_score: number;
  streak_days: number;
  top_strengths: Array<{ title_ar: string; title_en: string; score: string }>;
  active_gaps_summary: Array<{ concept_ar: string; concept_en: string; mastery: string }>;
  tutor_feedback_summary_en: string;
  parent_tips: string[];
}

// --- Monetization & Invoicing Interfaces ---
export interface TaxInvoiceItem {
  description_ar: string;
  description_en: string;
  qty: number;
  unit_price_usd: number;
  discount_usd: number;
  taxable_amount_usd: number;
  vat_rate_pct: number;
  vat_amount_usd: number;
  total_usd: number;
  total_aed: number;
}

export interface TaxInvoiceData {
  invoice_number: string;
  trn: string;
  issue_date: string;
  parent_name: string;
  parent_email: string;
  student_name: string;
  school_name: string;
  grade: number;
  package_type: string;
  payment_method: string;
  currency_usd: string;
  currency_aed: string;
  fx_rate: number;
  subtotal_usd: number;
  vat_amount_usd: number;
  total_usd: number;
  total_aed: number;
  items: TaxInvoiceItem[];
  status: string;
}

export interface PaymentReceipt {
  id: string;
  receipt_number: string;
  tax_invoice_number?: string;
  grade: number;
  term: number;
  package_type: string;
  amount_usd: number;
  subtotal_usd: number;
  vat_amount_usd: number;
  amount_aed: number;
  currency: string;
  status: string;
  payment_method: string;
  card_last4?: string;
  promo_code?: string;
  voucher_code?: string;
  school_name?: string;
  trn: string;
  created_at: string;
}

export interface VoucherRedeemResult {
  success: boolean;
  message: string;
  voucher_code: string;
  package_type: string;
  unlocked_terms: number[];
  receipt_number: string;
  school_name?: string;
}

export interface SpeechEvaluationResult {
  overall_score: number;
  accuracy_percentage: number;
  fluency_rating: string;
  feedback_ar: string;
  feedback_en: string;
  phoneme_scores: Record<string, number>;
  detected_mistakes: string[];
  target_phrase: string;
  recognized_text: string;
  is_pass: boolean;
}

