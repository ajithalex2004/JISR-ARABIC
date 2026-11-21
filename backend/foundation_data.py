"""Basic Foundation of Arabic: four stages (A to D) taught before Class 1.

A  Letters and writing      B  Reading mechanics
C  First grammar            D  Writing and punctuation

Each lesson has the rule (Arabic and English), points, worked examples (fully vowelled, so the
Arab-English line and audio work), an optional table, an optional interactive activity and a short
quiz. Served by GET /api/modules/foundation; backend/tests/test_foundation.py checks the content.

Activities (rendered by frontend/src/components/learning/FoundationViewer.tsx):
  alphabet       the 28 letters and hamza, tap to hear each name
  letter_shapes  a letter's four shapes (alone, start, middle, end)
  vowel_grid     a letter with every vowel mark, tap to hear
  sort           tap each item into the right group (buckets)
  syllables      split words into syllables, tap to reveal
  builder        put jumbled words in order to make a sentence
"""
from typing import Any, Dict, List, Optional

KING_LETTERS = ["ا", "د", "ذ", "ر", "ز", "و"]
SUN_LETTERS = ["ت", "ث", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ل", "ن"]
MOON_LETTERS = ["ا", "ب", "ج", "ح", "خ", "ع", "غ", "ف", "ق", "ك", "م", "ه", "و", "ي"]

# (letter, name, English sound hint)
ALPHABET = [
    ("ا", "أَلِف", "a / long aa"), ("ب", "بَاء", "b"), ("ت", "تَاء", "t"), ("ث", "ثَاء", "th (think)"),
    ("ج", "جِيم", "j"), ("ح", "حَاء", "strong breathy h"), ("خ", "خَاء", "kh (Scottish loch)"),
    ("د", "دَال", "d"), ("ذ", "ذَال", "th (this)"), ("ر", "رَاء", "rolled r"), ("ز", "زَاي", "z"),
    ("س", "سِين", "s"), ("ش", "شِين", "sh"), ("ص", "صَاد", "heavy s"), ("ض", "ضَاد", "heavy d"),
    ("ط", "طَاء", "heavy t"), ("ظ", "ظَاء", "heavy th (this)"), ("ع", "عَيْن", "deep throat sound"),
    ("غ", "غَيْن", "gh (French r)"), ("ف", "فَاء", "f"), ("ق", "قَاف", "deep k"), ("ك", "كَاف", "k"),
    ("ل", "لَام", "l"), ("م", "مِيم", "m"), ("ن", "نُون", "n"), ("ه", "هَاء", "h"), ("و", "وَاو", "w / long uu"),
    ("ي", "يَاء", "y / long ii"), ("ء", "هَمْزَة", "glottal stop (uh-oh)"),
]


def ex(ar: str, en: str, note: str = "") -> Dict[str, str]:
    return {"ar": ar, "en": en, **({"note": note} if note else {})}


def q(question_en: str, options: List[str], correct: int, explain_en: str, question_ar: str = "") -> Dict[str, Any]:
    return {"question_en": question_en, "question_ar": question_ar, "options": options,
            "correct_index": correct, "explain_en": explain_en}


def lesson(lid: str, title_ar: str, title_en: str, summary_en: str, points: List[str],
           examples: List[Dict[str, str]], quiz: List[Dict[str, Any]], *, table: Optional[Dict[str, Any]] = None,
           activity: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    out = {"id": lid, "title_ar": title_ar, "title_en": title_en, "summary_en": summary_en,
           "points": points, "examples": examples, "quiz": quiz}
    if table:
        out["table"] = table
    if activity:
        out["activity"] = activity
    return out


def sort_activity(prompt_en: str, buckets: List[Dict[str, str]], items: List[Dict[str, str]]) -> Dict[str, Any]:
    return {"type": "sort", "prompt_en": prompt_en, "buckets": buckets, "items": items}


# ---------------------------------------------------------------------------------------------
# Stage A: Letters and writing
# ---------------------------------------------------------------------------------------------

STAGE_A = [
    lesson("a1_alphabet", "الحُرُوفُ الهِجَائِيَّةُ", "The alphabet",
           "Arabic has 28 letters plus the hamza (ء). It is written and read from right to left.",
           ["There are 28 letters, plus the hamza (ء).",
            "Arabic is written and read from right to left.",
            "Each letter has a name (بَاء) and a sound (b).",
            "Tap a letter to hear its name."],
           [ex("أَسَدٌ بَابٌ تَاجٌ ثَوْبٌ", "a lion, a door, a crown, a robe: words that start with the first four letters"),
            ex("كِتَابٌ", "a book: read it from right to left: كِ تَا بٌ")],
           [q("How many letters does the Arabic alphabet have (without the hamza)?", ["26", "28", "30"], 1,
              "Arabic has 28 letters; the hamza (ء) is counted separately."),
            q("Which way is Arabic read?", ["Left to right", "Right to left", "Top to bottom"], 1,
              "Arabic is read and written from right to left.")],
           activity={"type": "alphabet"}),

    lesson("a2_letter_shapes", "أَشْكَالُ الحَرْفِ", "The four shapes of a letter",
           "Most letters change shape with their place in the word: alone, at the start, in the middle and at the end.",
           ["Alone: ع",
            "At the start of a word: عـ (عَيْنٌ)",
            "In the middle: ـعـ (سَعِيدٌ)",
            "At the end: ـع (سَمِعَ)",
            "The dots and the main body stay the same; only the joining strokes change."],
           [ex("عَيْنٌ", "an eye: ع at the start"), ex("سَعِيدٌ", "happy: ع in the middle"),
            ex("سَمِعَ", "he heard: ع at the end"), ex("بَيْتٌ", "a house: ب at the start")],
           [q("Which shape of ع is used at the start of a word?", ["ع", "عـ", "ـع"], 1,
              "At the start of a word, ع joins only to the letter after it: عـ."),
            q("In the word سَعِيدٌ, where is the letter ع?", ["At the start", "In the middle", "At the end"], 1,
              "س comes first, then ع in the middle: سَـعِـيدٌ.")],
           activity={"type": "letter_shapes"}),

    lesson("a3_king_letters", "الحُرُوفُ المَلِكِيَّةُ وَالحُرُوفُ العَادِيَّةُ", "King letters and normal letters",
           "Six King letters (ا د ذ ر ز و) never join the letter after them. The other 22 letters join on both sides.",
           ["King letters (6): ا د ذ ر ز و. They join the letter before them, never the letter after.",
            "After a King letter, the next letter starts again in its 'start' shape, leaving a gap inside the word.",
            "Normal letters (22) join on both sides.",
            "Also: ة and ى only come at the end of a word, ء stands alone, and لـ + ا is written لا."],
           [ex("دَارٌ", "a house: د and ا and ر do not join forward"),
            ex("وَرْدٌ", "roses: و, ر and د are all King letters"),
            ex("كَتَبَ", "he wrote: all normal letters, joined on both sides"),
            ex("مَدْرَسَةٌ", "a school: the gaps come after د and ر")],
           [q("Which of these is a King letter?", ["ب", "ر", "م"], 1,
              "ر is one of the six King letters (ا د ذ ر ز و): it never joins the letter after it."),
            q("How many King letters are there?", ["4", "6", "8"], 1, "There are six: ا د ذ ر ز و."),
            q("In دَارٌ, why is there a gap after د?", ["د is a King letter", "د has a dot", "د is a moon letter"], 0,
              "د is a King letter, so it does not join the letter after it.")],
           activity=sort_activity("Tap each letter, then choose its group.",
                                  [{"id": "king", "label": "King letter (joins only before)"},
                                   {"id": "normal", "label": "Normal letter (joins both sides)"}],
                                  [{"text": t, "bucket": "king" if t in KING_LETTERS else "normal"}
                                   for t in ["ا", "ب", "د", "س", "ذ", "م", "ر", "ك", "ز", "ل", "و", "ع"]])),

    lesson("a4_letter_families", "الحُرُوفُ المُتَشَابِهَةُ رَسْمًا", "Letter families: same shape, different dots",
           "Many letters share one shape and differ only in the number and place of their dots.",
           ["Count the dots and look where they are: above or below the letter.",
            "ب has one dot below, ت has two dots above, ث has three dots above.",
            "ج has a dot inside, ح has none, خ has a dot above."],
           [ex("بَابٌ", "a door"), ex("تَاجٌ", "a crown"), ex("ثَوْبٌ", "a robe"),
            ex("جَمَلٌ", "a camel"), ex("حِصَانٌ", "a horse"), ex("خُبْزٌ", "bread")],
           [q("Which letter has three dots above?", ["ب", "ت", "ث"], 2, "ث has three dots above."),
            q("Which letter has one dot below?", ["ب", "ن", "خ"], 0, "ب has one dot below; ن has one dot above.")],
           table={"headers": ["Shape", "Letters", "How to tell them apart"],
                  "rows": [["ٮ", "ب ت ث ن ي", "ب 1 below · ت 2 above · ث 3 above · ن 1 above · ي 2 below"],
                           ["ح", "ج ح خ", "ج dot inside · ح no dot · خ dot above"],
                           ["د", "د ذ", "ذ has a dot above"], ["ر", "ر ز", "ز has a dot above"],
                           ["س", "س ش", "ش has three dots above"], ["ص", "ص ض", "ض has a dot above"],
                           ["ط", "ط ظ", "ظ has a dot above"], ["ع", "ع غ", "غ has a dot above"],
                           ["ف", "ف ق", "ف 1 dot above · ق 2 dots above"]]}),

    lesson("a5_sound_pairs", "الحُرُوفُ المُتَقَارِبَةُ صَوْتًا", "Letters that sound alike",
           "Some letters sound close to English speakers. Listen carefully: changing the letter changes the meaning.",
           ["ح is breathy from the throat; ه is a light h.",
            "ع is a deep throat sound; ء is a short stop.",
            "ق is deep in the throat; ك is like English k.",
            "ص, ط, ض and ظ are the heavy partners of س, ت, د and ذ."],
           [ex("قَلْبٌ", "a heart (ق)"), ex("كَلْبٌ", "a dog (ك)"), ex("سَيْفٌ", "a sword (س)"),
            ex("صَيْفٌ", "summer (ص)"), ex("تِينٌ", "figs (ت)"), ex("طِينٌ", "mud (ط)"),
            ex("عَلِمَ", "he knew (ع)"), ex("أَلِمَ", "he felt pain (ء)")],
           [q("Which word means 'summer'?", ["سَيْفٌ", "صَيْفٌ"], 1, "صَيْفٌ (heavy ص) is summer; سَيْفٌ is a sword."),
            q("Which word means 'a heart'?", ["قَلْبٌ", "كَلْبٌ"], 0, "قَلْبٌ (deep ق) is a heart; كَلْبٌ is a dog.")],
           table={"headers": ["Pair", "Word 1", "Word 2"],
                  "rows": [["ق / ك", "قَلْبٌ (heart)", "كَلْبٌ (dog)"], ["س / ص", "سَيْفٌ (sword)", "صَيْفٌ (summer)"],
                           ["ت / ط", "تِينٌ (figs)", "طِينٌ (mud)"], ["ع / ء", "عَلِمَ (knew)", "أَلِمَ (felt pain)"],
                           ["ث / س", "ثَمَرٌ (fruit)", "سَمَرٌ (evening talk)"], ["د / ض", "دَرْسٌ (lesson)", "ضِرْسٌ (molar tooth)"]]}),

    lesson("a6_heavy_light", "الحُرُوفُ المُفَخَّمَةُ وَالمُرَقَّقَةُ", "Heavy and light letters",
           "Seven letters are said 'heavy', from the back of the mouth: خ ص ض غ ط ق ظ. The rest are light.",
           ["Heavy letters: خ ص ض غ ط ق ظ. Remember them with خُصَّ ضَغْطٍ قِظْ.",
            "Heavy letters make the vowel next to them sound deeper.",
            "Light letters are said at the front of the mouth."],
           [ex("طَائِرٌ", "a bird: heavy ط"), ex("صَبَاحٌ", "morning: heavy ص"), ex("قَمَرٌ", "a moon: heavy ق"),
            ex("تُفَّاحٌ", "apples: light ت")],
           [q("Which letter is heavy?", ["ت", "ط", "د"], 1, "ط is heavy; ت and د are light."),
            q("Which word starts with a heavy letter?", ["صَبَاحٌ", "سَمَكٌ", "بَيْتٌ"], 0, "ص is heavy.")],
           activity=sort_activity("Is the letter heavy or light?",
                                  [{"id": "heavy", "label": "Heavy (مُفَخَّم)"}, {"id": "light", "label": "Light (مُرَقَّق)"}],
                                  [{"text": t, "bucket": "heavy" if t in "خصضغطقظ" else "light"}
                                   for t in ["ص", "س", "ط", "ت", "ق", "ك", "ظ", "ذ", "خ", "ح", "ض", "د"]])),
]

# ---------------------------------------------------------------------------------------------
# Stage B: Reading mechanics
# ---------------------------------------------------------------------------------------------

STAGE_B = [
    lesson("b1_short_vowels", "الحَرَكَاتُ وَالسُّكُونُ", "Short vowels and sukun",
           "Three small marks give a letter its short vowel; the sukun shows the letter has no vowel.",
           ["Fatha ـَ (a): بَ", "Kasra ـِ (i): بِ", "Damma ـُ (u): بُ",
            "Sukun ـْ (no vowel): the letter joins the vowel before it: مِنْ"],
           [ex("كَتَبَ", "he wrote: fatha on every letter"), ex("مِنْ", "from: kasra then sukun"),
            ex("قُمْ", "stand up: damma then sukun")],
           [q("Which mark is the kasra?", ["ـَ", "ـِ", "ـُ"], 1, "The kasra is a small stroke below the letter (i)."),
            q("What does the sukun ـْ mean?", ["A long vowel", "No vowel", "A doubled letter"], 1,
              "The sukun means the letter has no vowel.")],
           activity={"type": "vowel_grid", "marks": ["fatha", "kasra", "damma", "sukun"]}),

    lesson("b2_long_vowels", "حُرُوفُ المَدِّ", "Long vowels",
           "Three letters stretch a vowel: ا after fatha (aa), ي after kasra (ii), و after damma (uu).",
           ["ا after a fatha: بَا (baa)", "ي after a kasra: بِي (bii)", "و after a damma: بُو (buu)",
            "آ is a long 'aa' at the start: آمَنَ"],
           [ex("بَابٌ", "a door: long aa"), ex("فِيلٌ", "an elephant: long ii"), ex("فُولٌ", "beans: long uu")],
           [q("Which word has a long 'uu'?", ["بَابٌ", "فِيلٌ", "فُولٌ"], 2, "فُولٌ has و after a damma: a long uu."),
            q("Which letter makes a long 'ii'?", ["ا", "و", "ي"], 2, "ي after a kasra makes a long ii.")],
           activity={"type": "vowel_grid", "marks": ["fatha", "kasra", "damma", "long_a", "long_i", "long_u"]}),

    lesson("b3_tanween", "التَّنْوِينُ", "Tanween",
           "A doubled vowel mark at the end of a word adds an 'n' sound.",
           ["Tanween fath ـً (an): كِتَابًا. It usually adds an alif.",
            "Tanween kasr ـٍ (in): كِتَابٍ", "Tanween damm ـٌ (un): كِتَابٌ",
            "No alif after ة: مَدْرَسَةً"],
           [ex("كِتَابٌ", "a book (kitaabun)"), ex("كِتَابًا", "a book (kitaaban)"), ex("كِتَابٍ", "a book (kitaabin)"),
            ex("مَدْرَسَةً", "a school: no extra alif after ة")],
           [q("Which word has tanween damm?", ["كِتَابٌ", "كِتَابًا", "كِتَابٍ"], 0, "ـٌ is tanween damm (un)."),
            q("Which ending is written without an extra alif?", ["كِتَابًا", "مَدْرَسَةً", "بَابًا"], 1,
              "After ة, tanween fath takes no alif.")],
           activity={"type": "vowel_grid", "marks": ["tanween_fath", "tanween_kasr", "tanween_damm"]}),

    lesson("b4_shadda", "الشَّدَّةُ", "Shadda",
           "The shadda ـّ doubles a letter: the first half has a sukun, the second half carries the vowel.",
           ["The shadda sits on the letter: ـّ", "It still takes a vowel: بَّ بِّ بُّ",
            "مُدَرِّسٌ is read mu-dar-ri-sun: the ر is said twice."],
           [ex("مُدَرِّسٌ", "a teacher"), ex("سُكَّرٌ", "sugar"), ex("قِطٌّ", "a cat")],
           [q("What does the shadda do?", ["Lengthens a vowel", "Doubles a letter", "Removes the vowel"], 1,
              "The shadda doubles the letter it sits on."),
            q("In سُكَّرٌ, which letter is doubled?", ["س", "ك", "ر"], 1, "The shadda is on ك: suk-ka-run.")],
           activity={"type": "vowel_grid", "marks": ["shadda_fatha", "shadda_kasra", "shadda_damma"]}),

    lesson("b5_sun_moon", "الحُرُوفُ الشَّمْسِيَّةُ وَالقَمَرِيَّةُ", "Sun and moon letters",
           "After ال, sun letters swallow the ل and take a shadda; with moon letters the ل is pronounced.",
           ["Sun letters (14): ت ث د ذ ر ز س ش ص ض ط ظ ل ن",
            "With a sun letter the ل is silent and the next letter gets a shadda: الشَّمْسُ (ash-shams).",
            "Moon letters (14): ا ب ج ح خ ع غ ف ق ك م ه و ي",
            "With a moon letter the ل is pronounced and takes a sukun: القَمَرُ (al-qamar)."],
           [ex("الشَّمْسُ", "the sun: sun letter ش"), ex("القَمَرُ", "the moon: moon letter ق"),
            ex("النَّجْمُ", "the star: sun letter ن"), ex("البَيْتُ", "the house: moon letter ب")],
           [q("In الشَّمْسُ, is the ل pronounced?", ["Yes", "No"], 1, "ش is a sun letter, so the ل is silent."),
            q("Which word starts with a moon letter after ال?", ["الشَّمْسُ", "النَّجْمُ", "القَمَرُ"], 2,
              "ق is a moon letter: the ل is pronounced.")],
           activity=sort_activity("Is the letter after ال a sun or a moon letter?",
                                  [{"id": "sun", "label": "☀ Sun letter (ل silent)"}, {"id": "moon", "label": "☾ Moon letter (ل said)"}],
                                  [{"text": w, "bucket": b} for w, b in [
                                      ("الشَّمْسُ", "sun"), ("القَمَرُ", "moon"), ("النَّجْمُ", "sun"), ("البَيْتُ", "moon"),
                                      ("الدَّرْسُ", "sun"), ("الكِتَابُ", "moon"), ("السَّمَاءُ", "sun"), ("الوَلَدُ", "moon")]])),

    lesson("b6_hamza", "هَمْزَةُ القَطْعِ وَهَمْزَةُ الوَصْلِ", "The two hamzas",
           "The strong hamza (أ إ) is always pronounced; the joining hamza (ا) is silent in the middle of speech.",
           ["Strong hamza (هَمْزَةُ القَطْعِ): written أ or إ and always pronounced: أَكَلَ، إِلَى.",
            "Joining hamza (هَمْزَةُ الوَصْلِ): written ا without a hamza sign.",
            "It is said only when you start speaking with it, and dropped in the middle: فِي البَيْتِ (fil-bayt)."],
           [ex("أَكَلَ", "he ate: strong hamza"), ex("إِلَى", "to: strong hamza"),
            ex("فِي البَيْتِ", "in the house: the ا of ال is silent"), ex("وَاسْمِي", "and my name: the ا is silent")],
           [q("Which word starts with a strong hamza?", ["أَكَلَ", "البَيْتُ"], 0, "أ with the hamza sign is a strong hamza."),
            q("In فِي البَيْتِ, is the ا of ال pronounced?", ["Yes", "No"], 1,
              "It is a joining hamza, dropped in the middle of speech.")]),

    lesson("b7_alif_maqsura", "الأَلِفُ المَقْصُورَةُ وَاليَاءُ", "ى or ي?",
           "ى (alif maqsura) has no dots and says 'aa'; ي (yaa) has two dots and says 'ii' or 'y'.",
           ["ى comes only at the end of a word and sounds like a long 'aa': إِلَى، عَلَى.",
            "ي has two dots below: فِي (fii), بَيْتٌ (bayt)."],
           [ex("إِلَى", "to: ى says aa"), ex("عَلَى", "on: ى says aa"), ex("فِي", "in: ي says ii"),
            ex("مُوسَى", "Musa (a name): ى says aa")],
           [q("Which word ends with alif maqsura?", ["فِي", "عَلَى"], 1, "عَلَى ends with ى (no dots), said 'aa'."),
            q("What sound does ى make at the end of إِلَى?", ["ii", "aa", "uu"], 1, "ى is a long 'aa'.")]),

    lesson("b8_stopping", "الوَقْفُ", "Stopping at the end of a word",
           "When you stop on a word, its last short vowel is dropped.",
           ["The last vowel is dropped: كِتَابٌ → كِتَابْ",
            "ة is said 'h' when you stop: مَدْرَسَةٌ → madrasah",
            "Tanween fath becomes a long 'aa': شُكْرًا → shukraa"],
           [ex("كِتَابٌ", "a book: stop on kitaab"), ex("مَدْرَسَةٌ", "a school: stop on madrasah"),
            ex("شُكْرًا", "thank you: stop on shukraa")],
           [q("How do you stop on مَدْرَسَةٌ?", ["madrasatun", "madrasah", "madrasa-t"], 1,
              "At a stop, ة is said as 'h'."),
            q("How do you stop on شُكْرًا?", ["shukran", "shukraa", "shukr"], 1, "Tanween fath becomes a long 'aa'.")]),

    lesson("b9_stop_test", "التَّاءُ المَرْبُوطَةُ وَالمَفْتُوحَةُ وَالهَاءُ", "The stop test: ة, ت or ه?",
           "To spell the last letter, stop on it: if you hear 'h' write ة; if you hear 't' write ت.",
           ["Stop on the last letter.",
            "You hear 'h' → write ة (taa marbuta): شَجَرَة، مَدْرَسَة.",
            "You hear 't' → write ت (open taa): بَيْت، بِنْت، زَيْت.",
            "To tell ة from ه, read on into a vowel: ة turns into 't' (شَجَرَةٌ shajaratun), ه stays 'h' (وَجْهٌ wajhun)."],
           [ex("شَجَرَةٌ", "a tree: stop → h, so ة"), ex("بَيْتٌ", "a house: stop → t, so ت"),
            ex("وَجْهٌ", "a face: always h, so ه"), ex("بِنْتٌ", "a girl: stop → t, so ت")],
           [q("Stop on 'madrasa…'. You hear 'h'. Which letter ends the word?", ["ة", "ت"], 0, "An 'h' at the stop means ة."),
            q("Which word ends with an open taa (ت)?", ["سَاعَة", "صَوْت", "وَرْدَة"], 1, "صَوْت: you hear 't' when you stop.")],
           activity=sort_activity("Stop on the last letter: which one is it?",
                                  [{"id": "marbuta", "label": "ة (h when you stop)"}, {"id": "open", "label": "ت (always t)"},
                                   {"id": "haa", "label": "ه (always h)"}],
                                  [{"text": w, "bucket": b} for w, b in [
                                      ("شَجَرَة", "marbuta"), ("بَيْت", "open"), ("وَجْه", "haa"), ("سَاعَة", "marbuta"),
                                      ("صَوْت", "open"), ("فَوَاكِه", "haa"), ("وَرْدَة", "marbuta"), ("بِنْت", "open")]])),

    lesson("b10_syllables", "تَحْلِيلُ الكَلِمَةِ إِلَى مَقَاطِعَ", "Splitting words into syllables",
           "Split a word by ear into syllables, then put it back together.",
           ["A letter with a short vowel is one syllable: فَ / تَ / حَ.",
            "A letter with sukun joins the syllable before it: مَسْ / بَ / حُ.",
            "A long vowel joins the syllable before it: فُ / صُو / لُ.",
            "A shadda letter counts twice: its first half closes the syllable before it: مُ / حَمْ / مَ / دٌ.",
            "ال with a moon letter: الْ / قَ / مَ / رُ. With a sun letter: الرُّ / سُ / لُ."],
           [ex("فَتَحَ", "he opened: فَ / تَ / حَ"), ex("مَسْبَحٌ", "a swimming pool: مَسْ / بَ / حٌ"),
            ex("فُصُولٌ", "classes: فُ / صُو / لٌ"), ex("مُحَمَّدٌ", "Muhammad: مُ / حَمْ / مَ / دٌ")],
           [q("How many syllables are in فَتَحَ?", ["2", "3", "4"], 1, "فَ / تَ / حَ: three syllables."),
            q("In مَسْبَحٌ, which syllable has the sukun?", ["مَسْ", "بَ", "حٌ"], 0, "مَسْ: the س has a sukun and joins مَ.")],
           activity={"type": "syllables", "items": [
               {"word": "فَتَحَ", "parts": ["فَ", "تَ", "حَ"]},
               {"word": "مَسْبَحٌ", "parts": ["مَسْ", "بَ", "حٌ"]},
               {"word": "فُصُولٌ", "parts": ["فُ", "صُو", "لٌ"]},
               {"word": "مُحَمَّدٌ", "parts": ["مُ", "حَمْ", "مَ", "دٌ"]},
               {"word": "القَمَرُ", "parts": ["الْ", "قَ", "مَ", "رُ"]},
               {"word": "الرُّسُلُ", "parts": ["الرُّ", "سُ", "لُ"]},
               {"word": "الطَّيَّارَةُ", "parts": ["الطَّيْ", "يَا", "رَ", "ةُ"]}]}),
]

# ---------------------------------------------------------------------------------------------
# Stage C: First grammar
# ---------------------------------------------------------------------------------------------

STAGE_C = [
    lesson("c1_gender", "المُذَكَّرُ وَالمُؤَنَّثُ", "Masculine and feminine",
           "Arabic nouns are masculine or feminine; ة at the end usually marks the feminine.",
           ["Add ة to many masculine nouns to make them feminine: مُعَلِّمٌ → مُعَلِّمَةٌ.",
            "Use هَذَا for masculine nouns and هَذِهِ for feminine ones."],
           [ex("مُعَلِّمٌ", "a (male) teacher"), ex("مُعَلِّمَةٌ", "a (female) teacher"),
            ex("طَالِبٌ نَشِيطٌ", "an active (male) student"), ex("طَالِبَةٌ نَشِيطَةٌ", "an active (female) student")],
           [q("What is the feminine of طَالِبٌ?", ["طَالِبَةٌ", "طُلَّابٌ", "طَالِبَانِ"], 0, "Add ة: طَالِبَةٌ."),
            q("Which word is feminine?", ["بَيْتٌ", "شَجَرَةٌ", "قَلَمٌ"], 1, "شَجَرَةٌ ends with ة.")]),

    lesson("c2_number", "المُفْرَدُ وَالمُثَنَّى وَالجَمْعُ", "Singular, dual and plural",
           "Arabic has a special form for two (the dual), as well as singular and plural.",
           ["Dual: add ـَانِ (or ـَيْنِ after a preposition or as an object): كِتَابٌ → كِتَابَانِ / كِتَابَيْنِ.",
            "With ة, the ة becomes ت before the dual ending: شَجَرَةٌ → شَجَرَتَانِ.",
            "Masculine plural: ـُونَ / ـِينَ: مُعَلِّمُونَ. Feminine plural: ـَاتٌ: مُعَلِّمَاتٌ.",
            "Some plurals change inside the word (broken plural): كِتَابٌ → كُتُبٌ."],
           [ex("كِتَابَانِ", "two books"), ex("شَجَرَتَانِ", "two trees"), ex("مُعَلِّمُونَ", "(male) teachers"),
            ex("مُعَلِّمَاتٌ", "(female) teachers"), ex("كُتُبٌ", "books (broken plural)")],
           [q("What is the dual of قَلَمٌ?", ["قَلَمَانِ", "أَقْلَامٌ", "قَلَمَةٌ"], 0, "Add ـَانِ: قَلَمَانِ."),
            q("What is the dual of شَجَرَةٌ?", ["شَجَرَةَانِ", "شَجَرَتَانِ", "أَشْجَارٌ"], 1,
              "The ة becomes ت: شَجَرَتَانِ.")],
           table={"headers": ["", "Masculine", "Feminine"],
                  "rows": [["Singular", "كِتَابٌ · مُعَلِّمٌ", "شَجَرَةٌ · مُعَلِّمَةٌ"],
                           ["Dual", "كِتَابَانِ / كِتَابَيْنِ", "شَجَرَتَانِ / شَجَرَتَيْنِ"],
                           ["Plural", "مُعَلِّمُونَ / مُعَلِّمِينَ · كُتُبٌ", "مُعَلِّمَاتٌ"]]}),

    lesson("c3_demonstratives", "أَسْمَاءُ الإِشَارَةِ", "Pointing words (this, these, that)",
           "Pointing words change with gender and number.",
           ["Near: هَذَا (m) · هَذِهِ (f) · هَذَانِ (two, m) · هَاتَانِ (two, f) · هَؤُلَاءِ (plural)",
            "Far: ذَلِكَ (m) · تِلْكَ (f)"],
           [ex("هَذَا قَلَمٌ", "this is a pen"), ex("هَذِهِ وَرْدَةٌ", "this is a rose"),
            ex("هَذَانِ وَلَدَانِ", "these are two boys"), ex("هَؤُلَاءِ طُلَّابٌ", "these are students"),
            ex("تِلْكَ سَيَّارَةٌ", "that is a car")],
           [q("Choose the right word: ….. شَجَرَةٌ", ["هَذَا", "هَذِهِ"], 1, "شَجَرَةٌ is feminine: هَذِهِ شَجَرَةٌ."),
            q("Which word points to two girls?", ["هَذَانِ", "هَاتَانِ", "هَؤُلَاءِ"], 1, "هَاتَانِ is for two (feminine).")]),

    lesson("c4_pronouns", "الضَّمَائِرُ المُنْفَصِلَةُ", "Pronouns",
           "Separate pronouns stand for people: I, you, he, she, we, they.",
           ["أَنَا (I) · نَحْنُ (we)", "أَنْتَ (you, m) · أَنْتِ (you, f) · أَنْتُمْ (you, plural)",
            "هُوَ (he) · هِيَ (she) · هُمْ (they)"],
           [ex("أَنَا طَالِبٌ", "I am a student"), ex("هِيَ مُعَلِّمَةٌ", "she is a teacher"),
            ex("نَحْنُ أَصْدِقَاءُ", "we are friends")],
           [q("Which pronoun means 'she'?", ["هُوَ", "هِيَ", "هُمْ"], 1, "هِيَ means she."),
            q("Which pronoun talks to one girl?", ["أَنْتَ", "أَنْتِ", "أَنْتُمْ"], 1, "أَنْتِ (with kasra) is 'you' for a girl.")]),

    lesson("c5_relative", "الأَسْمَاءُ المَوْصُولَةُ", "Relative pronouns (who, which)",
           "Relative pronouns join a description to a noun, like 'who' and 'which' in English.",
           ["الَّذِي (m) · الَّتِي (f)", "اللَّذَانِ (two, m) · اللَّتَانِ (two, f)", "الَّذِينَ (plural, m) · اللَّاتِي (plural, f)"],
           [ex("الوَلَدُ الَّذِي يَقْرَأُ نَشِيطٌ", "the boy who is reading is active"),
            ex("البِنْتُ الَّتِي تَرْسُمُ مَاهِرَةٌ", "the girl who is drawing is skilful"),
            ex("الطُّلَّابُ الَّذِينَ نَجَحُوا سُعَدَاءُ", "the students who passed are happy")],
           [q("Complete: البِنْتُ ….. تَكْتُبُ أُخْتِي", ["الَّذِي", "الَّتِي", "الَّذِينَ"], 1, "البِنْتُ is feminine: الَّتِي."),
            q("Which one is for a group of boys?", ["الَّذِي", "اللَّذَانِ", "الَّذِينَ"], 2, "الَّذِينَ is the masculine plural.")],
           table={"headers": ["", "Masculine", "Feminine"],
                  "rows": [["Singular", "الَّذِي", "الَّتِي"], ["Dual", "اللَّذَانِ", "اللَّتَانِ"], ["Plural", "الَّذِينَ", "اللَّاتِي"]]}),

    lesson("c6_prepositions", "حُرُوفُ الجَرِّ", "Prepositions",
           "Prepositions link words; the noun after them takes a kasra.",
           ["مِنْ (from) · إِلَى (to) · عَنْ (about) · عَلَى (on) · فِي (in)",
            "بِـ (with, by) · لِـ (for) · كَـ (like)",
            "The noun after a preposition takes kasra: فِي البَيْتِ."],
           [ex("ذَهَبْتُ إِلَى المَدْرَسَةِ", "I went to school"), ex("الكِتَابُ عَلَى المَكْتَبِ", "the book is on the desk"),
            ex("كَتَبْتُ بِالقَلَمِ", "I wrote with the pen")],
           [q("Which vowel does the noun after a preposition take?", ["Fatha", "Kasra", "Damma"], 1,
              "After a preposition the noun takes kasra: فِي البَيْتِ."),
            q("Choose the right ending: فِي الحَدِيقَ…", ["ـةُ", "ـةَ", "ـةِ"], 2, "After فِي: فِي الحَدِيقَةِ.")]),

    lesson("c7_time_place", "ظَرْفُ الزَّمَانِ وَظَرْفُ المَكَانِ", "Time and place words",
           "Time words answer 'when?' (مَتَى) and place words answer 'where?' (أَيْنَ).",
           ["Time: صَبَاحًا · مَسَاءً · لَيْلًا · الآنَ · قَبْلَ · بَعْدَ · يَوْمَ",
            "Place: فَوْقَ · تَحْتَ · أَمَامَ · خَلْفَ · بَيْنَ · عِنْدَ · يَمِينَ · يَسَارَ"],
           [ex("أَذْهَبُ إِلَى المَدْرَسَةِ صَبَاحًا", "I go to school in the morning"),
            ex("القِطُّ تَحْتَ الطَّاوِلَةِ", "the cat is under the table"),
            ex("جَلَسْتُ أَمَامَ المُعَلِّمِ", "I sat in front of the teacher")],
           [q("Which word answers 'when?'", ["تَحْتَ", "مَسَاءً", "خَلْفَ"], 1, "مَسَاءً (in the evening) is a time word."),
            q("Which word answers 'where?'", ["فَوْقَ", "الآنَ", "لَيْلًا"], 0, "فَوْقَ (above) is a place word.")],
           activity=sort_activity("Time word or place word?",
                                  [{"id": "time", "label": "Time (مَتَى؟)"}, {"id": "place", "label": "Place (أَيْنَ؟)"}],
                                  [{"text": w, "bucket": b} for w, b in [
                                      ("صَبَاحًا", "time"), ("فَوْقَ", "place"), ("مَسَاءً", "time"), ("تَحْتَ", "place"),
                                      ("الآنَ", "time"), ("أَمَامَ", "place"), ("لَيْلًا", "time"), ("خَلْفَ", "place")]])),

    lesson("c8_questions", "أَسْلُوبُ الاسْتِفْهَامِ", "Asking questions",
           "Each question word asks about something different.",
           ["مَنْ (who) · مَا / مَاذَا (what) · أَيْنَ (where) · مَتَى (when)",
            "كَيْفَ (how) · كَمْ (how many) · لِمَاذَا (why)",
            "هَلْ / أَ ask yes-or-no questions: answer نَعَمْ or لَا.",
            "A question ends with ؟"],
           [ex("مَنْ هَذَا؟", "who is this?"), ex("أَيْنَ القَلَمُ؟", "where is the pen?"),
            ex("كَمْ عُمُرُكَ؟", "how old are you?"), ex("هَلْ أَنْتَ جَائِعٌ؟", "are you hungry?")],
           [q("Which word asks 'where'?", ["مَتَى", "أَيْنَ", "كَيْفَ"], 1, "أَيْنَ asks about a place."),
            q("Which question is answered with نَعَمْ or لَا?", ["مَنْ أَنْتَ؟", "هَلْ تُحِبُّ القِرَاءَةَ؟", "كَمْ كِتَابًا عِنْدَكَ؟"], 1,
              "هَلْ asks a yes-or-no question.")]),

    lesson("c9_emphasis", "أَسْلُوبُ التَّوْكِيدِ", "Emphasis",
           "Use إِنَّ or قَدْ to make a statement stronger.",
           ["إِنَّ + noun with fatha + predicate with damma: إِنَّ العِلْمَ نُورٌ.",
            "قَدْ / لَقَدْ + past verb ('indeed', 'already'): قَدْ نَجَحَ أَحْمَدُ."],
           [ex("إِنَّ العِلْمَ نُورٌ", "indeed, knowledge is light"), ex("قَدْ نَجَحَ أَحْمَدُ", "Ahmed has indeed passed"),
            ex("لَقَدْ وَصَلَ القِطَارُ", "the train has arrived")],
           [q("After إِنَّ, which vowel does the noun take?", ["Damma", "Fatha", "Kasra"], 1, "إِنَّ العِلْمَ: the noun takes fatha."),
            q("Which sentence uses emphasis?", ["العِلْمُ نُورٌ", "إِنَّ العِلْمَ نُورٌ"], 1, "إِنَّ makes the statement emphatic.")]),

    lesson("c10_negation", "أَسْلُوبُ النَّفْيِ وَالنَّهْيِ", "Negation: saying 'not'",
           "Different negation words go with different verbs and times.",
           ["لَا + present verb: does not: لَا أَلْعَبُ الآنَ.",
            "لَا + present verb with sukun: don't! (an order): لَا تَلْعَبْ فِي الشَّارِعِ.",
            "لَمْ + present verb with sukun: did not (past): لَمْ يَذْهَبْ.",
            "لَنْ + present verb with fatha: will not: لَنْ أَتَأَخَّرَ.",
            "مَا + past verb: did not: مَا ذَهَبْتُ.",
            "لَيْسَ for a noun sentence: is not: لَيْسَ الجَوُّ حَارًّا."],
           [ex("لَا أَلْعَبُ الآنَ", "I am not playing now"), ex("لَا تَلْعَبْ فِي الشَّارِعِ", "don't play in the street"),
            ex("لَمْ يَذْهَبْ", "he did not go"), ex("لَنْ أَتَأَخَّرَ", "I will not be late"),
            ex("لَيْسَ الجَوُّ حَارًّا", "the weather is not hot")],
           [q("Which word negates the future ('will not')?", ["لَمْ", "لَنْ", "لَيْسَ"], 1, "لَنْ means 'will not'."),
            q("Which sentence is an order not to do something?", ["لَا أَلْعَبُ", "لَا تَلْعَبْ", "لَمْ أَلْعَبْ"], 1,
              "لَا تَلْعَبْ (with sukun) is 'don't play!'.")],
           table={"headers": ["Word", "Used with", "Meaning", "Example"],
                  "rows": [["لَا", "present verb", "does not", "لَا أَلْعَبُ"], ["لَا", "present verb + sukun", "don't!", "لَا تَلْعَبْ"],
                           ["لَمْ", "present verb + sukun", "did not", "لَمْ يَذْهَبْ"], ["لَنْ", "present verb + fatha", "will not", "لَنْ أَتَأَخَّرَ"],
                           ["مَا", "past verb", "did not", "مَا ذَهَبْتُ"], ["لَيْسَ", "noun sentence", "is not", "لَيْسَ الجَوُّ حَارًّا"]]}),

    lesson("c11_exception", "أَسْلُوبُ الاسْتِثْنَاءِ: إِلَّا وَغَيْرُ", "Except: إِلَّا and غَيْر",
           "إِلَّا and غَيْر both mean 'except'.",
           ["After إِلَّا the excepted noun takes fatha: نَجَحَ الطُّلَّابُ إِلَّا خَالِدًا.",
            "غَيْر carries the fatha itself and the noun after it takes kasra: نَجَحَ الطُّلَّابُ غَيْرَ خَالِدٍ."],
           [ex("نَجَحَ الطُّلَّابُ إِلَّا خَالِدًا", "the students passed except Khalid"),
            ex("نَجَحَ الطُّلَّابُ غَيْرَ خَالِدٍ", "the students passed except Khalid"),
            ex("حَضَرَ الأَصْدِقَاءُ إِلَّا سَعِيدًا", "the friends came except Saeed")],
           [q("Choose the right ending: جَاءَ الأَوْلَادُ إِلَّا عَلِيّ…", ["ـًا", "ـٍ", "ـٌ"], 0, "After إِلَّا: إِلَّا عَلِيًّا (fatha)."),
            q("After غَيْرَ, the noun takes…", ["Fatha", "Kasra", "Damma"], 1, "غَيْرَ خَالِدٍ: the noun takes kasra.")]),

    lesson("c12_parts_of_speech", "أَقْسَامُ الكَلَامِ وَأَزْمِنَةُ الفِعْلِ", "Parts of speech and verb tenses",
           "Every word is a noun (اسم), a verb (فعل) or a particle (حرف). Verbs have past, present and command forms.",
           ["Noun (اسم): a name of a person, place or thing: كِتَابٌ.",
            "Verb (فعل): an action with a time: كَتَبَ.",
            "Particle (حرف): a linking word: فِي، مِنْ، عَلَى.",
            "Past: كَتَبَ (he wrote) · Present: يَكْتُبُ (he writes) · Command: اُكْتُبْ (write!)"],
           [ex("كَتَبَ", "he wrote: past"), ex("يَكْتُبُ", "he writes: present"), ex("اُكْتُبْ", "write!: command")],
           [q("What is يَلْعَبُ?", ["Past verb", "Present verb", "Command"], 1, "يَلْعَبُ (he plays) is present."),
            q("Which word is a particle (حرف)?", ["قَلَمٌ", "فِي", "ذَهَبَ"], 1, "فِي (in) is a particle.")],
           activity=sort_activity("Noun, verb or particle?",
                                  [{"id": "noun", "label": "Noun (اسم)"}, {"id": "verb", "label": "Verb (فعل)"},
                                   {"id": "particle", "label": "Particle (حرف)"}],
                                  [{"text": w, "bucket": b} for w, b in [
                                      ("كِتَابٌ", "noun"), ("كَتَبَ", "verb"), ("فِي", "particle"), ("مَدْرَسَةٌ", "noun"),
                                      ("يَلْعَبُ", "verb"), ("عَلَى", "particle"), ("قَلَمٌ", "noun"), ("اُكْتُبْ", "verb")]])),

    lesson("c13_sentences", "الجُمْلَةُ الاسْمِيَّةُ وَالجُمْلَةُ الفِعْلِيَّةُ", "Nominal and verbal sentences",
           "A nominal sentence starts with a noun; a verbal sentence starts with a verb.",
           ["Nominal sentence: subject (مُبْتَدَأ) + predicate (خَبَر), both with damma: البَيْتُ كَبِيرٌ.",
            "Verbal sentence: verb (فِعْل) + doer (فَاعِل) with damma: كَتَبَ الطَّالِبُ."],
           [ex("البَيْتُ كَبِيرٌ", "the house is big: nominal"), ex("الشَّمْسُ مُشْرِقَةٌ", "the sun is shining: nominal"),
            ex("كَتَبَ الطَّالِبُ", "the student wrote: verbal"), ex("تَلْعَبُ البِنْتُ", "the girl plays: verbal")],
           [q("Which is a verbal sentence?", ["البَيْتُ كَبِيرٌ", "كَتَبَ الطَّالِبُ"], 1, "It starts with the verb كَتَبَ."),
            q("In البَيْتُ كَبِيرٌ, what is كَبِيرٌ?", ["The subject (مُبْتَدَأ)", "The predicate (خَبَر)", "The doer (فَاعِل)"], 1,
              "كَبِيرٌ tells us about the subject: it is the predicate.")]),
]

# ---------------------------------------------------------------------------------------------
# Stage D: Writing and punctuation
# ---------------------------------------------------------------------------------------------

STAGE_D = [
    lesson("d1_punctuation", "عَلَامَاتُ التَّرْقِيمِ", "Punctuation",
           "Punctuation marks help the reader. The Arabic comma (،) and question mark (؟) face the other way.",
           ["النُّقْطَةُ . ends a sentence.", "الفَاصِلَةُ ، separates items or linked sentences.",
            "عَلَامَةُ الاسْتِفْهَامِ ؟ ends a question.", "عَلَامَةُ التَّعَجُّبِ ! shows surprise or strong feeling.",
            "النُّقْطَتَانِ : come before speech or a list.", "عَلَامَتَا التَّنْصِيصِ « » go around quoted words.",
            "القَوْسَانِ ( ) hold an explanation."],
           [ex("ذَهَبْتُ إِلَى المَدْرَسَةِ.", "I went to school."),
            ex("اشْتَرَيْتُ تُفَّاحًا، وَمَوْزًا، وَعِنَبًا.", "I bought apples, bananas and grapes."),
            ex("أَيْنَ تَسْكُنُ؟", "Where do you live?"), ex("مَا أَجْمَلَ السَّمَاءَ!", "How beautiful the sky is!"),
            ex("قَالَ المُعَلِّمُ: اجْلِسُوا.", "The teacher said: sit down.")],
           [q("Which mark ends a question in Arabic?", ["?", "؟", "!"], 1, "Arabic uses the reversed question mark ؟."),
            q("Which mark goes before speech?", [".", ":", "،"], 1, "The colon (:) comes before speech: قَالَ المُعَلِّمُ: …"),
            q("Which sentence is punctuated correctly?", ["مَا أَجْمَلَ الوَرْدَ؟", "مَا أَجْمَلَ الوَرْدَ!"], 1,
              "مَا أَجْمَلَ… expresses wonder, so it takes !")],
           table={"headers": ["Mark", "Name", "Use"],
                  "rows": [[".", "النُّقْطَةُ", "end of a sentence"], ["،", "الفَاصِلَةُ", "between items or linked sentences"],
                           ["؟", "عَلَامَةُ الاسْتِفْهَامِ", "after a question"], ["!", "عَلَامَةُ التَّعَجُّبِ", "surprise or strong feeling"],
                           [":", "النُّقْطَتَانِ", "before speech or a list"], ["« »", "عَلَامَتَا التَّنْصِيصِ", "around quoted words"],
                           ["( )", "القَوْسَانِ", "an explanation"]]}),

    lesson("d2_build_sentences", "تَرْتِيبُ الكَلِمَاتِ", "Building sentences",
           "Put the words in order to make a correct sentence.",
           ["Start a nominal sentence with the subject: البَيْتُ كَبِيرٌ.",
            "Start a verbal sentence with the verb: يَلْعَبُ الوَلَدُ بِالكُرَةِ.",
            "End with the right punctuation mark."],
           [ex("يَلْعَبُ الوَلَدُ بِالكُرَةِ.", "the boy plays with the ball."),
            ex("الشَّمْسُ مُشْرِقَةٌ.", "the sun is shining.")],
           [q("Which order makes a correct sentence?", ["الوَلَدُ يَلْعَبُ بِالكُرَةِ", "بِالكُرَةِ الوَلَدُ يَلْعَبُ"], 0,
              "الوَلَدُ يَلْعَبُ بِالكُرَةِ: subject, then verb, then the rest.")],
           activity={"type": "builder", "items": [
               {"words": ["يَلْعَبُ", "الوَلَدُ", "بِالكُرَةِ"], "en": "The boy plays with the ball."},
               {"words": ["ذَهَبْتُ", "إِلَى", "المَدْرَسَةِ"], "en": "I went to school."},
               {"words": ["القِطُّ", "تَحْتَ", "الطَّاوِلَةِ"], "en": "The cat is under the table."},
               {"words": ["هَذِهِ", "وَرْدَةٌ", "جَمِيلَةٌ"], "en": "This is a beautiful rose."}]}),

    lesson("d3_paragraph", "الفِكْرَةُ العَامَّةُ", "Short paragraphs and the main idea",
           "Join sentences into a short paragraph, and find what the whole paragraph is about.",
           ["A paragraph is a few sentences about one idea.",
            "The main idea (الفِكْرَةُ العَامَّةُ) is what the whole paragraph is about, not one detail.",
            "Link sentences with وَ (and), ثُمَّ (then) and لِأَنَّ (because)."],
           [ex("اسْتَيْقَظَ سَعِيدٌ صَبَاحًا، ثُمَّ تَنَاوَلَ فُطُورَهُ، وَذَهَبَ إِلَى المَدْرَسَةِ.",
               "Saeed woke up in the morning, then ate his breakfast and went to school."),
            ex("أُحِبُّ القِرَاءَةَ لِأَنَّهَا مُفِيدَةٌ.", "I love reading because it is useful.")],
           [q("What is the main idea of: اسْتَيْقَظَ سَعِيدٌ صَبَاحًا، ثُمَّ تَنَاوَلَ فُطُورَهُ، وَذَهَبَ إِلَى المَدْرَسَةِ.",
              ["Saeed's morning", "Saeed's breakfast", "Saeed's school bag"], 0,
              "The whole paragraph describes Saeed's morning."),
            q("Which word means 'then'?", ["وَ", "ثُمَّ", "لِأَنَّ"], 1, "ثُمَّ means 'then'.")]),
]

STAGES = [
    {"id": "A", "title_ar": "الحُرُوفُ وَالكِتَابَةُ", "title_en": "Letters and writing",
     "summary_en": "The alphabet, letter shapes, King letters, letter families and the sounds that are easy to confuse.",
     "lessons": STAGE_A},
    {"id": "B", "title_ar": "قَوَاعِدُ القِرَاءَةِ", "title_en": "Reading mechanics",
     "summary_en": "Vowels, sukun, long vowels, tanween, shadda, sun and moon letters, hamza, the stop test and syllables.",
     "lessons": STAGE_B},
    {"id": "C", "title_ar": "قَوَاعِدُ أَوَّلِيَّةٌ", "title_en": "First grammar",
     "summary_en": "Gender, the dual and plural, pointing words, pronouns, prepositions, questions, emphasis, negation and simple sentences.",
     "lessons": STAGE_C},
    {"id": "D", "title_ar": "الكِتَابَةُ وَالتَّرْقِيمُ", "title_en": "Writing and punctuation",
     "summary_en": "Punctuation, building sentences and short paragraphs.",
     "lessons": STAGE_D},
]


def foundation_course() -> Dict[str, Any]:
    return {
        "title_ar": "أَسَاسِيَّاتُ اللُّغَةِ العَرَبِيَّةِ",
        "title_en": "Basic Foundation of Arabic",
        "summary_en": "Four stages, from the alphabet to writing your first paragraph, taken before Class 1.",
        "alphabet": [{"letter": l, "name": n, "sound_en": s, "king": l in KING_LETTERS} for l, n, s in ALPHABET],
        "stages": STAGES,
    }
