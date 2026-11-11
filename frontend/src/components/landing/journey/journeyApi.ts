/**
 * Live data for the journey phone on the welcome page: the real chapters of a class, the
 * content of a chapter the visitor can open, and (when signed in) the child's own activity.
 * Kept free of the app's api.ts so the landing bundle stays small.
 */
const API_BASE: string = ((import.meta as any).env?.VITE_API_URL ?? '');

export interface JourneyLesson {
  id: string;
  lesson_order: number;
  title_ar: string;
  title_en: string;
  unit_title_ar?: string;
  unit_title_en?: string;
  start_page?: number;
  is_first_chapter_demo: boolean;
  is_accessible: boolean;
  status: string;
  lock_reason?: string | null;
}

export interface VocabCard {
  word_ar: string;
  vowelled_ar?: string;
  meaning_en: string;
  example_ar?: string;
  example_en?: string;
}

export interface ChapterContent {
  lessonId: string;
  grade: number;
  term: number;
  titleAr: string;
  titleEn: string;
  startPage?: number;
  words: VocabCard[];
}

export interface LessonActivity { lesson_id: string; attempts: number; correct: number; last_activity: string | null }

export interface Session { token: string; childId: string; childName: string; grade: number; role: string }

function readToken(): string | null {
  try { return window.localStorage.getItem('fahim_token'); } catch { return null; }
}
function readActiveChild(): string | null {
  try { return window.localStorage.getItem('active_child_id'); } catch { return null; }
}

async function getJson<T>(path: string, token?: string | null, signal?: AbortSignal): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    signal,
  });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json() as Promise<T>;
}

/** The signed-in family's active child, or null for visitors (or an expired login). */
export async function loadSession(signal?: AbortSignal): Promise<Session | null> {
  const token = readToken();
  if (!token) return null;
  try {
    const me = await getJson<{ role: string; children: { id: string; name: string; default_grade: number }[] }>('/api/auth/me', token, signal);
    if (!me.children?.length) return null;
    const wanted = readActiveChild();
    const child = me.children.find((c) => c.id === wanted) ?? me.children[0];
    return { token, childId: child.id, childName: child.name, grade: child.default_grade || 5, role: me.role };
  } catch {
    return null;
  }
}

export function loadLessons(grade: number, term: number, session: Session | null, signal?: AbortSignal) {
  const child = session ? `&child_id=${encodeURIComponent(session.childId)}` : '';
  return getJson<JourneyLesson[]>(`/api/curriculum/lessons?grade=${grade}&term=${term}${child}`, session?.token, signal);
}

export async function loadChapter(lessonId: string, session: Session | null, signal?: AbortSignal): Promise<ChapterContent> {
  const child = session ? `?child_id=${encodeURIComponent(session.childId)}` : '';
  const pkg = await getJson<{ lesson: { grade: number; term: number; title_ar: string; title_en: string }; content: any }>(
    `/api/curriculum/lesson/${encodeURIComponent(lessonId)}${child}`, session?.token, signal);
  const c = pkg.content || {};
  const words: VocabCard[] = (Array.isArray(c.vocabulary_cards) ? c.vocabulary_cards : [])
    .filter((v: any) => v && typeof v.word_ar === 'string' && typeof v.meaning_en === 'string')
    .map((v: any) => ({ word_ar: v.word_ar, vowelled_ar: v.vowelled_ar, meaning_en: v.meaning_en, example_ar: v.example_ar, example_en: v.example_en }));
  return {
    lessonId, grade: pkg.lesson.grade, term: pkg.lesson.term,
    titleAr: c.title_ar || pkg.lesson.title_ar, titleEn: c.title_en || pkg.lesson.title_en,
    startPage: c.start_page, words,
  };
}

export async function loadActivity(session: Session, grade: number, term: number, signal?: AbortSignal): Promise<LessonActivity[]> {
  const q = `child_id=${encodeURIComponent(session.childId)}&grade=${grade}&term=${term}`;
  const res = await getJson<{ lessons: LessonActivity[] }>(`/api/curriculum/journey?${q}`, session.token, signal);
  return res.lessons || [];
}

export async function loadGloss(word: string, context: string): Promise<string | null> {
  try {
    const q = `word=${encodeURIComponent(word.slice(0, 40))}&context=${encodeURIComponent(context.slice(0, 300))}`;
    const g = await getJson<{ translation: string | null }>(`/api/curriculum/word-gloss?${q}`);
    return g.translation || null;
  } catch {
    return null;
  }
}

const MARKS = /[ً-ٰٟـ]/g;
/** Arabic without tashkeel or the article, for matching a word in a sentence to a vocabulary card. */
export function bareArabic(s: string): string {
  return s.replace(MARKS, '').replace(/[^ء-ي]/g, '').replace(/^(وال|بال|فال|كال|لل|ال)/, '');
}
