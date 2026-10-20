// All landing-page copy and data in one place, so marketing edits never touch layout code.

export type DemoWord = { ar: string; tr: string; en: string; note: string };
export type DemoSentence = { id: string; label: string; en: string; words: DemoWord[] };

export const DEMO_SENTENCES: DemoSentence[] = [
  {
    id: 'love', label: 'Sentence 1', en: 'I love the Arabic language.',
    words: [
      { ar: 'أُحِبُّ', tr: 'uḥibbu', en: 'I love', note: 'Present-tense verb. The opening أُ means “I”.' },
      { ar: 'اللُّغَةَ', tr: 'al-lughata', en: 'the language', note: 'Noun, the object of the verb, so it ends in a fatḥa (ـَ).' },
      { ar: 'العَرَبِيَّةَ', tr: 'al-ʿarabiyyata', en: 'Arabic', note: 'Adjective. It follows its noun and matches it: feminine, definite, fatḥa.' },
    ],
  },
  {
    id: 'school', label: 'Sentence 2', en: 'I went to school in the morning.',
    words: [
      { ar: 'ذَهَبْتُ', tr: 'dhahabtu', en: 'I went', note: 'Past-tense verb. The ending ـتُ means “I”.' },
      { ar: 'إِلَى', tr: 'ilā', en: 'to', note: 'Preposition. The noun after it takes a kasra (ـِ).' },
      { ar: 'المَدْرَسَةِ', tr: 'al-madrasati', en: 'the school', note: 'Noun after a preposition, so it ends in a kasra.' },
      { ar: 'صَبَاحًا', tr: 'ṣabāḥan', en: 'in the morning', note: 'Adverb of time. The double fatḥa (ـًا) is pronounced “-an”.' },
    ],
  },
];

export const MARQUEE_WORDS: Array<[string, string]> = [
  ['كِتَابٌ', 'book'], ['مَدْرَسَةٌ', 'school'], ['صَدِيقٌ', 'friend'], ['شَمْسٌ', 'sun'], ['بَحْرٌ', 'sea'],
  ['قَلَمٌ', 'pen'], ['بَيْتٌ', 'home'], ['عِلْمٌ', 'knowledge'], ['نَخْلَةٌ', 'palm tree'], ['سَلَامٌ', 'peace'],
];

export const STORY_STEPS = [
  {
    kicker: '01 · The page',
    title: 'Your child’s real textbook, page by page.',
    body: 'The CBSE Arabic textbook pages are in JISR, laid out line for line exactly as printed, with the numbers and examples where the teacher expects them.',
  },
  {
    kicker: '02 · The bridge',
    title: 'Each line, crossed into English.',
    body: 'Tap any line and its meaning appears right beneath it, in the same order. Tap any word to hear it from a native voice, slowed down to 0.6× or 0.3× and repeated until it sounds right.',
  },
  {
    kicker: '03 · The habit',
    title: 'Practise until it sticks.',
    body: 'Quizzes, mind maps and study booklets turn each chapter into practice. The mastery map shows exactly which words are learned and which need one more go.',
  },
];

export const STORY_LINES = [
  { ar: 'إِنْسَانٌ', en: 'Human', head: true },
  { ar: 'الكَائِنُ الحَيُّ العَاقِلُ', en: 'The living, thinking being' },
  { ar: 'الإِنْسَانُ يَتَعَلَّمُ كُلَّ يَوْمٍ.', en: 'A human learns every day.', example: true },
];

export const FEATURES = [
  { id: 'audio', title: 'Native audio for every word', body: 'Normal, 0.6× and 0.3× speeds, with 1–3× repeat. Pronunciation stops being guesswork.', ar: 'اِسْتَمِعْ' },
  { id: 'fahim', title: 'Ask Fahim, the AI tutor', body: 'Stuck on homework? Fahim explains in English, answers in Arabic and reads it aloud.', ar: 'اِسْأَلْ' },
  { id: 'maps', title: 'Mind maps & flowcharts', body: 'Each chapter as one picture: vocabulary, grammar and ideas, connected.', ar: 'اِفْهَمْ' },
  { id: 'booklets', title: 'Smart study booklets', body: 'Printable, exam-ready summaries for revision night.', ar: 'رَاجِعْ' },
  { id: 'exam', title: 'CBSE exam simulation', body: 'Timed practice papers in the real format, marked instantly.', ar: 'تَدَرَّبْ' },
  { id: 'mastery', title: 'Mastery map, ranks & badges', body: 'Progress you can see, with rewards that keep children coming back.', ar: 'تَقَدَّمْ' },
];

export const PLANS = [
  {
    id: 'free', name: 'Try it', price: 'Free', cadence: 'Chapter 1 of each term',
    points: ['The full reader with line-by-line English', 'Native audio for every word', 'No card needed'],
    cta: 'Try a free lesson', intent: 'signup' as const,
  },
  {
    id: 'term', name: 'One term', price: '$10', cadence: 'per term · per child',
    points: ['Every chapter of the term', 'Ask Fahim, mind maps, booklets', 'Exam simulation & mastery map', 'Auto-renew optional'],
    cta: 'Start with a term', intent: 'signup' as const,
  },
  {
    id: 'year', name: 'Full year', price: '$25.50', was: '$30', cadence: 'all 3 terms · per child', badge: 'Save 15%',
    points: ['Terms 1, 2 & 3 unlocked', 'Everything in One term', 'Best value for the school year', 'Auto-renew optional'],
    cta: 'Get the full year', intent: 'signup' as const, featured: true,
  },
];

export const FAQS = [
  { q: 'Who is JISR for?', a: 'Children in UAE schools who learn Arabic as an additional language under the CBSE curriculum, Classes 1 to 10, and the parents who help them with homework without speaking Arabic themselves.' },
  { q: 'Does it follow my child’s school textbook?', a: 'Yes. JISR is built on the CBSE Arabic syllabus and the textbook pages your child already uses, term by term, so what they practise at home is what they meet in class.' },
  { q: 'What is free?', a: 'The first chapter of each term is free, with the full reader, translations and audio. You can explore it without an account.' },
  { q: 'How do payments work?', a: 'Payments are processed securely by Stripe. A term is $10 and the full year is $25.50 (15% off). Every payment comes with a receipt number and a UAE tax invoice. If you choose auto-renew, you can turn it off at any time and keep access until the end of the period you paid for.' },
  { q: 'Can my child use it without my email and password?', a: 'Yes. Each child signs in with your email and their own 4-digit PIN, so they can learn on their own while you keep control of the account and payments.' },
  { q: 'Which devices does it work on?', a: 'Any modern browser on a phone, tablet or computer. Nothing to install: open the site and start learning.' },
];

export const GRADES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
