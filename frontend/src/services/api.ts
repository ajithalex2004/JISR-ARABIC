import type {
  AuthResponse, ChildProfile, LessonSummary, LessonPackage, TermSummary, MistakeEntry,
  DiagnosticQuestion, DiagnosticResult, LearningPlan, TaxInvoiceData, PaymentReceipt, VoucherRedeemResult,
  SpeechEvaluationResult
} from '../types';

export const API_BASE = ((import.meta as any).env?.VITE_API_URL || 'http://127.0.0.1:8000');

export function createApiUrl(path: string): URL {
  const base = API_BASE.startsWith('http')
    ? API_BASE
    : (typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1:8000');
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  const fullPath = API_BASE.startsWith('http') ? `${API_BASE}${cleanPath}` : cleanPath;
  return new URL(fullPath, base);
}

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('fahim_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Central transport: every application API request carries the current session.
export async function authenticatedFetch(input: RequestInfo | URL, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  const token = localStorage.getItem('fahim_token');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const res = await fetch(input, { ...init, headers });
  if (res.status === 401 || res.status === 403) {
    const data = await res.clone().json().catch(() => ({}));
    const message = data.detail || (res.status === 401 ? 'Please sign in to continue.' : 'You do not have access to this action.');
    window.dispatchEvent(new CustomEvent('fahim:access-denied', { detail: { status: res.status, message } }));
    throw new Error(message);
  }
  return res;
}

export const api = {
  async tutorAssignmentOptions() {
    const res = await authenticatedFetch(`${API_BASE}/api/admin/tutor-assignment-options`);
    if (!res.ok) throw new Error('Could not load assignment options');
    return res.json();
  },
  async tutorAssignments() {
    const res = await authenticatedFetch(`${API_BASE}/api/admin/tutor-assignments`);
    if (!res.ok) throw new Error('Could not load tutor assignments');
    return res.json();
  },
  async setTutorAssignment(tutorId: string, childId: string, enabled: boolean) {
    const res = await authenticatedFetch(`${API_BASE}/api/admin/tutor-assignments/${encodeURIComponent(tutorId)}/${encodeURIComponent(childId)}`, { method: enabled ? 'PUT' : 'DELETE' });
    if (!res.ok) throw new Error((await res.json()).detail || 'Could not update assignment');
    return res.json();
  },

  // Auth
  async signup(email: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to request signup OTP');
    return res.json();
  },

  async verifyOtp(email: string, code: string, purpose: string = 'signup') {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/verify-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code, purpose })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Invalid or expired OTP');
    return res.json();
  },

  async createPasswordAndEnroll(data: {
    email: string;
    code: string;
    password: string;
    child_name: string;
    child_gender: string;
    child_age: number;
    child_school: string;
    child_grade: number;
    avatar_id?: string;
    curriculum_stream?: string;
    access_pin?: string;
  }): Promise<AuthResponse> {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/create-password-enroll`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to complete registration');
    const authData: AuthResponse = await res.json();
    localStorage.setItem('fahim_token', authData.access_token);
    return authData;
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Invalid email or password');
    const authData: AuthResponse = await res.json();
    localStorage.setItem('fahim_token', authData.access_token);
    return authData;
  },

  async loginOtpRequest(email: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/login-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to send login code');
    return res.json();
  },

  async loginOtpVerify(email: string, code: string): Promise<AuthResponse> {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/verify-login-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Invalid or expired login code');
    const authData: AuthResponse = await res.json();
    localStorage.setItem('fahim_token', authData.access_token);
    return authData;
  },

  async studentPinLogin(parent_email: string, pin: string, child_id?: string): Promise<AuthResponse> {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/student-pin-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ parent_email, pin, child_id })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Incorrect student PIN or parent email');
    const authData: AuthResponse = await res.json();
    localStorage.setItem('fahim_token', authData.access_token);
    return authData;
  },

  async getChildren(): Promise<ChildProfile[]> {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/children`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error('Failed to fetch children');
    return res.json();
  },

  async addChild(data: {
    name: string;
    gender?: string;
    age?: number;
    school_name?: string;
    default_grade?: number;
    avatar_id?: string;
    curriculum_stream?: string;
    access_pin?: string;
  }): Promise<ChildProfile> {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/children`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to add child profile');
    return res.json();
  },

  async updateChild(childId: string, data: Partial<ChildProfile>): Promise<ChildProfile> {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/children/${childId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to update child profile');
    return res.json();
  },

  async switchChild(childId: string): Promise<AuthResponse> {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/switch-child/${childId}`, {
      method: 'POST',
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to switch child profile');
    const authData: AuthResponse = await res.json();
    localStorage.setItem('fahim_token', authData.access_token);
    return authData;
  },

  async forgotPassword(email: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to request password reset code');
    return res.json();
  },

  async resetPassword(email: string, code: string, new_password: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code, new_password })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to reset password');
    return res.json();
  },

  async deleteAccount(): Promise<{ success: boolean; message: string }> {
    const res = await authenticatedFetch(`${API_BASE}/api/auth/account`, {
      method: 'DELETE',
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to delete account');
    localStorage.removeItem('fahim_token');
    return res.json();
  },

  async getMe() {
    if (!localStorage.getItem('fahim_token')) return null;
    const res = await authenticatedFetch(`${API_BASE}/api/auth/me`, {
      headers: { ...getAuthHeader() }
    });
    if (!res.ok) return null;
    return res.json();
  },

  // Curriculum
  async getGrades() {
    const res = await authenticatedFetch(`${API_BASE}/api/curriculum/grades`);
    return res.json();
  },

  async getTerms(grade: number = 5, childId?: string): Promise<TermSummary[]> {
    const url = createApiUrl('/api/curriculum/terms');
    url.searchParams.append('grade', String(grade));
    if (childId) url.searchParams.append('child_id', childId);
    const res = await authenticatedFetch(url.toString());
    return res.json();
  },

  async getLessons(grade: number = 5, term: number = 1, childId?: string): Promise<LessonSummary[]> {
    const url = createApiUrl('/api/curriculum/lessons');
    url.searchParams.append('grade', String(grade));
    url.searchParams.append('term', String(term));
    if (childId) url.searchParams.append('child_id', childId);
    const res = await authenticatedFetch(url.toString());
    return res.json();
  },

  async getLessonContent(lessonId: string, childId?: string): Promise<{ lesson: any; content: LessonPackage }> {
    try {
      const url = createApiUrl(`/api/curriculum/lesson/${lessonId}`);
      if (childId) url.searchParams.append('child_id', childId);
      const res = await authenticatedFetch(url.toString());
      if (res.status === 402) {
        throw new Error('PAYMENT_REQUIRED');
      }
      if (res.ok) {
        return await res.json();
      }
    } catch (e: any) {
      if (e.message === 'PAYMENT_REQUIRED') throw e;
      // Fallback to relative path via Vite proxy
      try {
        const fallbackUrl = `/api/curriculum/lesson/${lessonId}${childId ? `?child_id=${childId}` : ''}`;
        const res2 = await authenticatedFetch(fallbackUrl);
        if (res2.status === 402) throw new Error('PAYMENT_REQUIRED');
        if (res2.ok) return await res2.json();
      } catch (e2: any) {
        if (e2.message === 'PAYMENT_REQUIRED') throw e2;
      }
      throw new Error(e.message || 'Failed to load lesson');
    }
    throw new Error('Failed to load lesson package');
  },

  // Payments
  async checkoutTerm(data: {
    child_id: string;
    grade: number;
    term: number;
    package_type?: string;
    card_number?: string;
    promo_code?: string;
  }) {
    const res = await authenticatedFetch(`${API_BASE}/api/payments/checkout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Payment failed');
    return res.json();
  },

  async checkoutAnnual(data: {
    child_id: string;
    grade?: number;
    card_number?: string;
    promo_code?: string;
  }) {
    const res = await authenticatedFetch(`${API_BASE}/api/payments/checkout-annual`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Annual checkout failed');
    return res.json();
  },

  async redeemVoucher(data: {
    child_id: string;
    grade: number;
    code: string;
  }): Promise<VoucherRedeemResult> {
    const res = await authenticatedFetch(`${API_BASE}/api/payments/redeem-voucher`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Voucher redemption failed');
    return res.json();
  },

  async getTaxInvoice(receiptNumber: string): Promise<TaxInvoiceData> {
    const res = await authenticatedFetch(`${API_BASE}/api/payments/invoice/${encodeURIComponent(receiptNumber)}`);
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to fetch tax invoice');
    return res.json();
  },

  async getReceipts(childId: string): Promise<PaymentReceipt[]> {
    const res = await authenticatedFetch(`${API_BASE}/api/payments/receipts?child_id=${childId}`);
    if (!res.ok) throw new Error('Failed to load transaction history');
    return res.json();
  },

  // Attempts
  async submitAttempt(data: {
    child_id: string;
    lesson_id: string;
    activity_id: string;
    path_type: string;
    user_answer: any;
    lesson_version_id?: string;
  }) {
    const res = await authenticatedFetch(`${API_BASE}/api/attempts/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  async getMistakes(childId: string): Promise<MistakeEntry[]> {
    const res = await authenticatedFetch(`${API_BASE}/api/attempts/mistakes?child_id=${childId}`);
    return res.json();
  },

  async resolveMistake(mistakeId: number) {
    const res = await authenticatedFetch(`${API_BASE}/api/attempts/mistakes/${mistakeId}/resolve`, {
      method: 'POST'
    });
    return res.json();
  },

  // Tutor
  async submitForTutor(data: {
    child_id: string;
    lesson_id: string;
    activity_id: string;
    submission_type: string;
    content_text?: string;
    audio_url?: string;
  }) {
    const res = await authenticatedFetch(`${API_BASE}/api/tutor/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  async getTutorQueue(statusFilter: string = 'all') {
    const res = await authenticatedFetch(`${API_BASE}/api/tutor/queue?status_filter=${statusFilter}`);
    return res.json();
  },

  async reviewTutorSubmission(data: {
    submission_id: string;
    tutor_score: number;
    tutor_feedback: string;
  }) {
    const res = await authenticatedFetch(`${API_BASE}/api/tutor/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  // Parent Dashboard
  async getParentDashboard(childId: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/parent/dashboard/${childId}`);
    return res.json();
  },

  // Textbook OCR Reader & Coverage
  async getCoverageReport() {
    const res = await authenticatedFetch(`${API_BASE}/api/admin/coverage-report`);
    return res.json();
  },

  async getOcrPage(pdfPage: number, editionId?: string) {
    const query = editionId ? `?edition_id=${encodeURIComponent(editionId)}` : '';
    const res = await authenticatedFetch(`${API_BASE}/api/admin/ocr-page/${pdfPage}${query}`);
    return res.json();
  },

  async solveQuestion(questionAr: string, contextAr?: string, grade?: number) {
    const res = await authenticatedFetch(`${API_BASE}/api/admin/solve-question`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_ar: questionAr, context_ar: contextAr, grade: grade || 6 })
    });
    if (!res.ok) throw new Error('Failed to solve question');
    return res.json();
  },
  async getQualityReport() {
    const res = await authenticatedFetch(`${API_BASE}/api/admin/quality-report`);
    if (!res.ok) throw new Error('Failed to load quality report');
    return res.json();
  },

  async getCurriculumReview(term?: number, grade?: number) {
    const params = new URLSearchParams();
    if (term) params.append('term', String(term));
    if (grade) params.append('grade', String(grade));
    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await authenticatedFetch(`${API_BASE}/api/admin/curriculum-review${query}`);
    return res.json();
  },

  async updateCurriculumStatus(lessonId: string, status: 'content_pending' | 'published') {
    const res = await authenticatedFetch(`${API_BASE}/api/admin/curriculum-review/${lessonId}/status?status=${status}`, { method: 'PUT' });
    return res.json();
  },

  async uploadCurriculumPdf(file: File, grade?: number, term?: number, startPage: number = 1, pageCount?: number) {
    const body = new FormData();
    body.append('file', file);
    if (grade !== undefined) body.append('grade', grade.toString());
    if (term !== undefined) body.append('term', term.toString());
    if (startPage !== undefined) body.append('start_page', startPage.toString());
    if (pageCount !== undefined) body.append('page_count', pageCount.toString());
    const res = await authenticatedFetch(`${API_BASE}/api/admin/curriculum-upload`, { method: 'POST', body });
    return res.json();
  },

  async getTask(taskId: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/tasks/${taskId}`);
    if (!res.ok) throw new Error('Failed to fetch task status');
    return res.json();
  },

  // Admin Scaling
  async adminAddTerm(data: any) {
    const res = await authenticatedFetch(`${API_BASE}/api/admin/add-term`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  async adminAddClass(data: any) {
    const res = await authenticatedFetch(`${API_BASE}/api/admin/add-class`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  async adminAddLesson(data: any) {
    const res = await authenticatedFetch(`${API_BASE}/api/admin/add-lesson`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  // Ask Fahim AI
  async askFahim(question: string, contextLessonId?: string, childId?: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/ai/ask-fahim`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, context_lesson_id: contextLessonId, child_id: childId })
    });
    return res.json();
  },

  async solveQuestionPaper(data: {
    paper_title?: string;
    document_base64?: string;
    mime_type?: string;
    text_content?: string;
    grade?: number;
    term?: number;
    child_id?: string;
    force_escalation?: boolean;
  }) {
    const res = await authenticatedFetch(`${API_BASE}/api/ai/solve-question-paper`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to process question paper');
    return res.json();
  },

  async evaluateSpeech(data: {
    target_phrase: string;
    spoken_text?: string;
    audio_base64?: string;
    child_id?: string;
    lesson_id?: string;
    phoneme_targets?: string[];
  }): Promise<SpeechEvaluationResult> {
    const res = await authenticatedFetch(`${API_BASE}/api/audio/evaluate-speech`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to evaluate speech');
    return res.json();
  },

  // Onboarding & Baseline Diagnostic
  async getDiagnosticQuestions(grade: number = 5, stream?: string): Promise<{ success: boolean; count: number; questions: DiagnosticQuestion[] }> {
    const streamParam = stream ? `&stream=${encodeURIComponent(stream)}` : '';
    const res = await authenticatedFetch(`${API_BASE}/api/curriculum/diagnostic-questions?grade=${grade}${streamParam}`);
    if (!res.ok) throw new Error('Failed to load diagnostic questions');
    return res.json();
  },

  async submitDiagnostic(childId: string, answers: Record<string, number>): Promise<DiagnosticResult> {
    const res = await authenticatedFetch(`${API_BASE}/api/curriculum/submit-diagnostic`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ child_id: childId, answers })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to submit diagnostic assessment');
    return res.json();
  },

  async getLearningPlan(childId: string): Promise<{
    success: boolean;
    child_id: string;
    child_name: string;
    diagnostic_completed: boolean;
    diagnostic_level: string;
    diagnostic_score: number;
    learning_plan: LearningPlan;
  }> {
    const res = await authenticatedFetch(`${API_BASE}/api/curriculum/learning-plan/${childId}`);
    if (!res.ok) throw new Error('Failed to load learning plan');
    return res.json();
  },

  async updateOnboardingProfile(data: {
    child_id: string;
    name?: string;
    gender?: string;
    age?: number;
    school_name?: string;
    default_grade?: number;
    selected_term?: number;
    avatar_id?: string;
    curriculum_stream?: string;
    access_pin?: string;
  }): Promise<{ success: boolean; message: string; child: ChildProfile }> {
    const res = await authenticatedFetch(`${API_BASE}/api/curriculum/onboarding-profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to update onboarding profile');
    return res.json();
  },

  // ---------------------------------------------------------
  // CORE LEARNING & TUTORING MODULES (ركائز التعلم الذكي)
  // ---------------------------------------------------------

  // 3.1 Socratic AI Learn
  async socraticLearn(data: {
    topic: string;
    student_input: string;
    conversation_history?: Array<{ sender: string; text: string }>;
    grade?: number;
    child_id?: string;
  }) {
    const res = await authenticatedFetch(`${API_BASE}/api/ai/socratic-learn`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to connect to Socratic AI Tutor');
    return res.json();
  },

  // 3.3 Malazim Study Booklets
  async getMalazim(lessonId: string = 'lesson_01_ball_games', childId?: string, grade?: number) {
    const params = new URLSearchParams();
    if (childId) params.append('child_id', childId);
    if (grade) params.append('grade', String(grade));
    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await authenticatedFetch(`${API_BASE}/api/modules/malazim/${lessonId}${query}`);
    if (!res.ok) throw new Error('Failed to load study booklet');
    return res.json();
  },

  async checkSentence(lessonId: string, activityId: string, answer: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/modules/sentences/${lessonId}/check`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ activity_id: activityId, answer })
    });
    if (!res.ok) throw new Error('Unable to check sentence');
    return res.json();
  },

  async checkBookletAnswer(lessonId: string, sectionId: string, answer: number, childId?: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/modules/malazim/${lessonId}/check`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ section_id: sectionId, answer, child_id: childId })
    });
    if (!res.ok) throw new Error('Unable to check answer. Please try again.');
    return res.json();
  },

  // 3.4 Microlearning Capsules
  async listCapsules(childId?: string, grade?: number) {
    const params = new URLSearchParams();
    if (childId) params.append('child_id', childId);
    if (grade) params.append('grade', String(grade));
    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await authenticatedFetch(`${API_BASE}/api/modules/capsules${query}`);
    if (!res.ok) throw new Error('Failed to load learning capsules');
    return res.json();
  },

  async getCapsule(capsuleId: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/modules/capsules/${capsuleId}`);
    if (!res.ok) throw new Error('Failed to load capsule details');
    return res.json();
  },

  async completeCapsule(capsuleId: string, data: { child_id: string; score?: number; time_spent_seconds?: number }) {
    const res = await authenticatedFetch(`${API_BASE}/api/modules/capsules/${capsuleId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to complete capsule');
    return res.json();
  },

  // 3.5 Adaptive Assessments & Exam Simulation
  async getAdaptiveAssessment(lessonId: string = 'lesson_01_ball_games', childId?: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/modules/assessments/adaptive/${lessonId}${childId ? `?child_id=${encodeURIComponent(childId)}` : ''}`);
    if (!res.ok) throw new Error('Failed to load adaptive assessment');
    return res.json();
  },

  async getExamSimulation(grade: number = 5, term: number = 1, childId?: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/modules/assessments/exam-simulation/${grade}/${term}${childId ? `?child_id=${encodeURIComponent(childId)}` : ''}`);
    if (!res.ok) throw new Error('Failed to load exam simulation');
    return res.json();
  },

  async submitExamSimulation(data: {
    child_id: string;
    grade: number;
    term: number;
    answers: Record<string, number>;
    time_taken_seconds: number;
    session_id?: string;
  }) {
    const res = await authenticatedFetch(`${API_BASE}/api/modules/assessments/submit-exam`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to evaluate exam simulation');
    return res.json();
  },

  // 4.1 Mastery Tracking & Knowledge Gap Heatmap
  async getMasteryHeatmap(childId: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/mastery/heatmap/${childId}`);
    if (!res.ok) throw new Error('Failed to load mastery heatmap');
    return res.json();
  },

  async getGapReviewSession(childId: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/mastery/review-session/${childId}`);
    if (!res.ok) throw new Error('Failed to load gap review session');
    return res.json();
  },

  async recordDrillAnswer(data: {
    child_id: string;
    concept_key: string;
    question_id: string;
    selected_index: number;
    is_correct: boolean;
  }) {
    const res = await authenticatedFetch(`${API_BASE}/api/mastery/record-drill`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to record drill answer');
    return res.json();
  },

  // 4.2 Parent Supervision Dashboard: Weekly Digest & Actionable Guidance
  async getWeeklyDigest(childId: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/parent/weekly-digest/${childId}`);
    if (!res.ok) throw new Error('Failed to load weekly digest');
    return res.json();
  },

  async sendWeeklyDigest(childId: string, data: { channel: string; recipient_email?: string }) {
    const res = await authenticatedFetch(`${API_BASE}/api/parent/send-digest/${childId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to dispatch weekly digest');
    return res.json();
  },

  async getActionableGuidance(childId: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/parent/actionable-guidance/${childId}`);
    if (!res.ok) throw new Error('Failed to load actionable parent guidance');
    return res.json();
  },

  // 4.3 Gamification & Motivation
  async getGamificationProfile(childId: string) {
    const res = await authenticatedFetch(`${API_BASE}/api/gamification/profile/${childId}`);
    if (!res.ok) throw new Error('Failed to load gamification profile');
    return res.json();
  },

  async getLeaderboard(grade: number = 5, schoolName?: string, currentChildId?: string) {
    const url = createApiUrl('/api/gamification/leaderboard');
    url.searchParams.append('grade', String(grade));
    if (schoolName) url.searchParams.append('school_name', schoolName);
    if (currentChildId) url.searchParams.append('current_child_id', currentChildId);
    const res = await authenticatedFetch(url.toString());
    if (!res.ok) throw new Error('Failed to load leaderboard');
    return res.json();
  },

  async awardXP(data: { child_id: string; activity_type: string; xp_amount: number; reason?: string }) {
    const res = await authenticatedFetch(`${API_BASE}/api/gamification/award-xp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to award XP');
    return res.json();
  }
};


