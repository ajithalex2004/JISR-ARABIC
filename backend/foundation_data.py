"""Foundation in Basic Arabic: four stages (A to D) taught before Class 1.

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

# ---------------------------------------------------------------------------------------------
# Extra lessons: reading extras (B), core concepts and grammar extras (C), everyday Arabic (E)
# ---------------------------------------------------------------------------------------------

def cards(prompt_en: str, items: List[tuple]) -> Dict[str, Any]:
    """Word cards: tap to hear, with the English meaning."""
    return {"type": "cards", "prompt_en": prompt_en, "items": [{"ar": a, "en": e} for a, e in items]}


EXTRA_B = [
    lesson("b11_hidden_alif", "كَلِمَاتٌ فِيهَا أَلِفٌ تُنْطَقُ وَلَا تُكْتَبُ", "Words with a hidden alif",
           "A few very common words have a long 'aa' you hear but do not see written.",
           ["هَذَا is said haadhaa: there is a long aa after هـ that is not written.",
            "The same in هَذِهِ (haadhihi), ذَلِكَ (dhaalika), لَكِنْ (laakin), هَؤُلَاءِ (haa'ulaa'i).",
            "In the Qur'an and some books it is shown as a small upright alif: هٰذَا، الرَّحْمٰنُ، اللّٰهُ.",
            "Learn these words by sight: they appear on almost every page."],
           [ex("هَذَا كِتَابٌ", "this is a book (haadhaa)"), ex("ذَلِكَ بَيْتٌ", "that is a house (dhaalika)"),
            ex("لَكِنْ", "but (laakin)"), ex("اللّٰهُ", "Allah: the long aa is shown by a small alif")],
           [q("How do you say هَذَا?", ["hadha (short a)", "haadhaa (long aa)"], 1,
              "هَذَا has a hidden long aa after هـ: haadhaa."),
            q("Which word has a long aa you hear but don't see?", ["هُوَ", "لَكِنْ", "هِيَ"], 1,
              "لَكِنْ is said laakin: the alif is not written.")]),

    lesson("b12_silent_letters", "حُرُوفٌ تُكْتَبُ وَلَا تُنْطَقُ", "Silent letters",
           "Some letters are written but not pronounced.",
           ["The alif after the plural و is silent: كَتَبُوا (katabuu), ذَهَبُوا (dhahabuu).",
            "The و at the end of the name عَمْرٌو is silent: it is said 'amr.",
            "The ل of ال is silent before a sun letter: الشَّمْسُ (ash-shams).",
            "The joining hamza is silent in the middle of speech: فِي البَيْتِ (fil-bayt)."],
           [ex("كَتَبُوا", "they wrote: the last alif is silent"), ex("ذَهَبُوا", "they went: the last alif is silent"),
            ex("عَمْرٌو", "Amr (a name): the و is silent"), ex("الشَّمْسُ", "the sun: the ل is silent")],
           [q("In كَتَبُوا, which letter is silent?", ["ك", "و", "ا"], 2,
              "The alif after the plural و is written but not pronounced."),
            q("Which name ends with a silent و?", ["عُمَرُ", "عَمْرٌو"], 1, "عَمْرٌو is said 'amr; the و only tells it apart from عُمَرُ.")]),

    lesson("b13_vowel_length", "الحَرَكَةُ القَصِيرَةُ وَالطَّوِيلَةُ", "Short or long vowel? The meaning changes",
           "Making a vowel short or long can turn one word into a different word.",
           ["كَتَبَ (he wrote) and كَاتَبَ (he wrote to someone) differ only in a long aa.",
            "مَلِكٌ is a king; مَالِكٌ is an owner.", "جَمَلٌ is a camel; جَمَالٌ is beauty.",
            "Hold a long vowel about twice as long as a short one."],
           [ex("كَتَبَ", "he wrote"), ex("كَاتَبَ", "he wrote to (someone)"), ex("مَلِكٌ", "a king"),
            ex("مَالِكٌ", "an owner"), ex("جَمَلٌ", "a camel"), ex("جَمَالٌ", "beauty")],
           [q("Which word means 'an owner'?", ["مَلِكٌ", "مَالِكٌ"], 1, "مَالِكٌ has a long aa: maalik, an owner."),
            q("Which word has only short vowels?", ["جَمَلٌ", "جَمَالٌ"], 0, "جَمَلٌ (a camel) has no long vowel.")],
           activity=sort_activity("Does the word have a long vowel?",
                                  [{"id": "long", "label": "Has a long vowel"}, {"id": "short", "label": "Only short vowels"}],
                                  [{"text": w, "bucket": b} for w, b in [
                                      ("كَتَبَ", "short"), ("كَاتَبَ", "long"), ("مَلِكٌ", "short"), ("مَالِكٌ", "long"),
                                      ("جَمَلٌ", "short"), ("جَمَالٌ", "long"), ("قَلَمٌ", "short"), ("فِيلٌ", "long")]])),

    lesson("b14_hamza_seats", "مَوَاقِعُ الهَمْزَةِ", "Where the hamza sits",
           "The hamza can sit on an alif, a waw, a dotless yaa, or alone on the line.",
           ["At the start of a word the hamza always sits on an alif: أَسَدٌ، إِبِلٌ.",
            "In the middle it follows the strongest vowel next to it: kasra → ئ (بِئْرٌ), damma → ؤ (سُؤَالٌ), fatha → أ (سَأَلَ).",
            "At the end, after a long vowel or a sukun, it sits alone on the line: سَمَاءٌ، شَيْءٌ."],
           [ex("أَسَدٌ", "a lion: hamza on alif"), ex("سُؤَالٌ", "a question: hamza on waw"),
            ex("بِئْرٌ", "a well: hamza on a dotless yaa"), ex("سَمَاءٌ", "a sky: hamza on the line")],
           [q("Where does the hamza sit in سُؤَالٌ?", ["On alif (أ)", "On waw (ؤ)", "On yaa (ئ)"], 1,
              "The damma before it is the strongest vowel, so it sits on waw: ؤ."),
            q("Which word has the hamza alone on the line?", ["سَمَاءٌ", "سَأَلَ", "بِئْرٌ"], 0,
              "After the long aa at the end, the hamza sits on the line: سَمَاءٌ.")]),

    lesson("b15_fluency", "القِرَاءَةُ الطَّلِيقَةُ", "Reading fluently",
           "Read short sentences aloud, first slowly and correctly, then smoothly.",
           ["Listen to the model reading first.", "Read word by word, with every vowel.",
            "Read the sentence again, more smoothly. Then time yourself.",
            "Fluent reading is correct and smooth, not just fast."],
           [ex("البَيْتُ كَبِيرٌ وَجَمِيلٌ.", "the house is big and beautiful."),
            ex("يَلْعَبُ أَحْمَدُ بِالكُرَةِ فِي الحَدِيقَةِ.", "Ahmed plays with the ball in the garden.")],
           [q("What should you do first?", ["Listen to the model reading", "Read as fast as you can", "Skip the vowels"], 0,
              "Listening first shows you how the sentence should sound."),
            q("Reading fluently means reading…", ["correctly and smoothly", "only fast", "without vowels"], 0,
              "Fluency is correct and smooth reading.")],
           activity={"type": "fluency", "items": [
               "ذَهَبَ الوَلَدُ إِلَى المَدْرَسَةِ.",
               "البَيْتُ كَبِيرٌ وَجَمِيلٌ.",
               "يَلْعَبُ أَحْمَدُ بِالكُرَةِ فِي الحَدِيقَةِ.",
               "قَرَأَتْ مَرْيَمُ قِصَّةً جَمِيلَةً قَبْلَ النَّوْمِ."]}),
]

EXTRA_C = [
    lesson("c14_definite", "النَّكِرَةُ وَالمَعْرِفَةُ", "Definite and indefinite: ال or tanween",
           "A word with tanween means 'a …'; a word with ال means 'the …'. A word never has both.",
           ["Indefinite (نَكِرَة): ends in tanween: كِتَابٌ (a book).",
            "Definite (مَعْرِفَة): starts with ال and has no tanween: الكِتَابُ (the book).",
            "Never both: البَيْتٌ is wrong.", "Names are definite without ال: أَحْمَدُ، مَرْيَمُ."],
           [ex("كِتَابٌ", "a book"), ex("الكِتَابُ", "the book"), ex("شَجَرَةٌ", "a tree"), ex("الشَّجَرَةُ", "the tree")],
           [q("Which word means 'the house'?", ["بَيْتٌ", "البَيْتُ"], 1, "ال makes it definite: البَيْتُ."),
            q("Which word is wrong?", ["البَيْتٌ", "البَيْتُ", "بَيْتٌ"], 0, "A word can't have both ال and tanween.")],
           activity=sort_activity("Definite (the …) or indefinite (a …)?",
                                  [{"id": "def", "label": "Definite (the …)"}, {"id": "indef", "label": "Indefinite (a …)"}],
                                  [{"text": w, "bucket": b} for w, b in [
                                      ("كِتَابٌ", "indef"), ("الكِتَابُ", "def"), ("قَلَمٌ", "indef"), ("المَدْرَسَةُ", "def"),
                                      ("شَجَرَةٌ", "indef"), ("الوَلَدُ", "def"), ("بَابٌ", "indef"), ("الشَّمْسُ", "def")]])),

    lesson("c15_attached_pronouns", "الضَّمَائِرُ المُتَّصِلَةُ", "Attached pronouns: my, your, his, her",
           "Small endings joined to a noun show whose it is: كِتَابِي (my book), كِتَابُهَا (her book).",
           ["ـِي my · ـُكَ your (boy) · ـُكِ your (girl) · ـُهُ his · ـُهَا her · ـُنَا our · ـُهُمْ their",
            "Before these endings, ة becomes ت: مَدْرَسَةٌ → مَدْرَسَتِي.",
            "The same endings join verbs and prepositions: يُحِبُّنِي، مَعَكَ، لَهُ."],
           [ex("هَذَا كِتَابِي", "this is my book"), ex("بَيْتُهُ كَبِيرٌ", "his house is big"),
            ex("هَذِهِ مَدْرَسَتِي", "this is my school"), ex("قَلَمُكَ جَمِيلٌ", "your pen is beautiful")],
           [q("Which means 'her book'?", ["كِتَابُهُ", "كِتَابُهَا", "كِتَابِي"], 1, "ـُهَا means her."),
            q("How do you write 'my school'?", ["مَدْرَسَةِي", "مَدْرَسَتِي"], 1, "ة becomes ت before the ending: مَدْرَسَتِي.")],
           table={"headers": ["Ending", "Meaning", "Example"],
                  "rows": [["ـِي", "my", "كِتَابِي"], ["ـُكَ / ـُكِ", "your (boy / girl)", "كِتَابُكَ / كِتَابُكِ"],
                           ["ـُهُ", "his", "كِتَابُهُ"], ["ـُهَا", "her", "كِتَابُهَا"], ["ـُنَا", "our", "كِتَابُنَا"],
                           ["ـُهُمْ", "their", "كِتَابُهُمْ"]]}),

    lesson("c16_adjectives", "النَّعْتُ وَالمَنْعُوتُ", "Adjectives match their noun",
           "An adjective comes after its noun and copies it: masculine or feminine, with or without ال, and the same ending.",
           ["Gender: بَيْتٌ كَبِيرٌ · سَيَّارَةٌ كَبِيرَةٌ.",
            "ال: if the noun has ال, so does the adjective: البَيْتُ الكَبِيرُ.",
            "Ending: the adjective takes the same vowel as the noun: فِي بَيْتٍ كَبِيرٍ."],
           [ex("بَيْتٌ كَبِيرٌ", "a big house"), ex("البَيْتُ الكَبِيرُ", "the big house"),
            ex("سَيَّارَةٌ جَمِيلَةٌ", "a beautiful car"), ex("السَّيَّارَةُ الجَمِيلَةُ", "the beautiful car")],
           [q("Complete: البِنْتُ ….", ["الذَّكِيُّ", "الذَّكِيَّةُ", "ذَكِيَّةٌ"], 1,
              "The noun is feminine with ال, so the adjective is too: البِنْتُ الذَّكِيَّةُ."),
            q("Which is correct?", ["بَيْتٌ الكَبِيرُ", "بَيْتٌ كَبِيرٌ"], 1, "No ال on the noun, so none on the adjective.")]),

    lesson("c17_idafa", "الإِضَافَةُ", "The possessive construct: X of Y",
           "Two nouns side by side mean 'X of Y': كِتَابُ الطَّالِبِ (the student's book).",
           ["The first word has no ال and no tanween: كِتَابُ.",
            "The second word takes kasra: الطَّالِبِ.",
            "Read it as 'the book of the student' = 'the student's book'."],
           [ex("كِتَابُ الطَّالِبِ", "the student's book"), ex("بَابُ البَيْتِ", "the door of the house"),
            ex("سَيَّارَةُ أَبِي", "my father's car"), ex("مُعَلِّمُ المَدْرَسَةِ", "the school's teacher")],
           [q("Which means 'the door of the house'?", ["البَابُ البَيْتِ", "بَابُ البَيْتِ", "بَابٌ البَيْتُ"], 1,
              "The first word has no ال and no tanween; the second takes kasra."),
            q("In كِتَابُ الطَّالِبِ, which vowel does the second word take?", ["Fatha", "Kasra", "Damma"], 1,
              "The second word of the construct takes kasra.")]),

    lesson("c18_present_tense", "الفِعْلُ المُضَارِعُ مَعَ الضَّمَائِرِ", "Present-tense verbs with pronouns",
           "A present verb starts with أ، نـ، يـ or تـ to show who is doing the action.",
           ["أَكْتُبُ I write · نَكْتُبُ we write",
            "تَكْتُبُ you write (boy) · تَكْتُبِينَ you write (girl)",
            "يَكْتُبُ he writes · تَكْتُبُ she writes · يَكْتُبُونَ they write",
            "Remember the four starting letters: أ ن ي ت."],
           [ex("أَنَا أَكْتُبُ الدَّرْسَ", "I write the lesson"), ex("هِيَ تَقْرَأُ قِصَّةً", "she reads a story"),
            ex("نَحْنُ نَلْعَبُ", "we play"), ex("هُمْ يَدْرُسُونَ", "they study")],
           [q("Which means 'she writes'?", ["يَكْتُبُ", "تَكْتُبُ", "أَكْتُبُ"], 1, "تَكْتُبُ is 'she writes' (and 'you write' to a boy)."),
            q("Which means 'we write'?", ["نَكْتُبُ", "يَكْتُبُونَ", "تَكْتُبِينَ"], 0, "نـ at the start means 'we'.")],
           table={"headers": ["Pronoun", "Verb", "Meaning"],
                  "rows": [["أَنَا", "أَكْتُبُ", "I write"], ["نَحْنُ", "نَكْتُبُ", "we write"], ["أَنْتَ", "تَكْتُبُ", "you write (boy)"],
                           ["أَنْتِ", "تَكْتُبِينَ", "you write (girl)"], ["هُوَ", "يَكْتُبُ", "he writes"], ["هِيَ", "تَكْتُبُ", "she writes"],
                           ["هُمْ", "يَكْتُبُونَ", "they write"]]}),

    lesson("c19_roots", "الجَذْرُ وَالأُسْرَةُ اللُّغَوِيَّةُ", "Roots: one root, many words",
           "Most Arabic words grow from a root of three letters. Know the root and you can guess the meaning.",
           ["The root ك ت ب is about writing: كَتَبَ، كَاتِبٌ، كِتَابٌ، مَكْتَبٌ، مَكْتَبَةٌ.",
            "To find the root, take away the extra letters (م، ا، ة، ي، و، ت…) and keep the three main ones.",
            "Words with مَـ at the start are often places: مَكْتَبٌ، مَلْعَبٌ، مَدْرَسَةٌ."],
           [ex("كَتَبَ", "he wrote (ك ت ب)"), ex("مَكْتَبَةٌ", "a library (ك ت ب)"),
            ex("مَدْرَسَةٌ", "a school (د ر س)"), ex("مَلْعَبٌ", "a playground (ل ع ب)")],
           [q("What is the root of مَكْتَبَةٌ?", ["ك ت ب", "م ك ت", "ت ب ة"], 0, "Take away م and ة: ك ت ب."),
            q("Which word is NOT from the root د ر س?", ["مَدْرَسَةٌ", "دَرْسٌ", "مَلْعَبٌ"], 2, "مَلْعَبٌ comes from ل ع ب (play).")],
           activity={"type": "roots", "families": [
               {"root": "ك ت ب", "meaning_en": "writing", "words": [
                   {"ar": "كَتَبَ", "en": "he wrote"}, {"ar": "كَاتِبٌ", "en": "a writer"}, {"ar": "كِتَابٌ", "en": "a book"},
                   {"ar": "مَكْتَبٌ", "en": "a desk / an office"}, {"ar": "مَكْتَبَةٌ", "en": "a library"}]},
               {"root": "د ر س", "meaning_en": "studying", "words": [
                   {"ar": "دَرَسَ", "en": "he studied"}, {"ar": "دَرْسٌ", "en": "a lesson"}, {"ar": "مَدْرَسَةٌ", "en": "a school"},
                   {"ar": "مُدَرِّسٌ", "en": "a teacher"}]},
               {"root": "ع ل م", "meaning_en": "knowing", "words": [
                   {"ar": "عَلِمَ", "en": "he knew"}, {"ar": "عِلْمٌ", "en": "knowledge"}, {"ar": "مُعَلِّمٌ", "en": "a teacher"},
                   {"ar": "عَالِمٌ", "en": "a scientist"}]},
               {"root": "ل ع ب", "meaning_en": "playing", "words": [
                   {"ar": "لَعِبَ", "en": "he played"}, {"ar": "لُعْبَةٌ", "en": "a toy / a game"}, {"ar": "مَلْعَبٌ", "en": "a playground"},
                   {"ar": "لَاعِبٌ", "en": "a player"}]}]}),

    lesson("c20_linking_words", "أَدَوَاتُ الرَّبْطِ", "Linking words",
           "Linking words join words and sentences.",
           ["وَ and · فَـ and then (straight after) · ثُمَّ then (later)",
            "أَوْ or · لَكِنْ but · لِأَنَّ because"],
           [ex("أَكَلْتُ خُبْزًا وَجُبْنًا", "I ate bread and cheese"), ex("دَخَلَ المُعَلِّمُ فَوَقَفَ الطُّلَّابُ", "the teacher came in and the students stood up"),
            ex("دَرَسْتُ ثُمَّ نِمْتُ", "I studied, then I slept"), ex("الجَوُّ حَارٌّ لَكِنَّهُ جَمِيلٌ", "the weather is hot but it is nice")],
           [q("Which word means 'because'?", ["لَكِنْ", "لِأَنَّ", "أَوْ"], 1, "لِأَنَّ means because."),
            q("Which word means 'then, after a while'?", ["فَـ", "ثُمَّ"], 1, "ثُمَّ shows a gap in time; فَـ is straight after.")]),

    lesson("c21_kaana", "كَانَ: الجُمْلَةُ فِي المَاضِي", "كَانَ: saying 'was'",
           "كَانَ (was) turns a nominal sentence into the past. The predicate then takes fatha.",
           ["الجَوُّ جَمِيلٌ → كَانَ الجَوُّ جَمِيلًا (the weather was nice).",
            "The subject keeps damma; the predicate takes fatha (or tanween fath).",
            "For a feminine subject use كَانَتْ: كَانَتِ السَّمَاءُ صَافِيَةً."],
           [ex("كَانَ الجَوُّ جَمِيلًا", "the weather was nice"), ex("كَانَتِ السَّمَاءُ صَافِيَةً", "the sky was clear"),
            ex("كَانَ الطَّالِبُ مُجْتَهِدًا", "the student was hard-working")],
           [q("Complete: كَانَ الطَّالِبُ …", ["مُجْتَهِدٌ", "مُجْتَهِدًا"], 1, "After كَانَ, the predicate takes fatha: مُجْتَهِدًا."),
            q("Which word goes with البِنْتُ?", ["كَانَ", "كَانَتْ"], 1, "البِنْتُ is feminine: كَانَتْ.")]),

    lesson("c22_comparing", "اسْمُ التَّفْضِيلِ", "Comparing: bigger than…",
           "Use the pattern أَفْعَلُ + مِنْ to compare two things.",
           ["كَبِيرٌ → أَكْبَرُ (bigger) · صَغِيرٌ → أَصْغَرُ (smaller)",
            "طَوِيلٌ → أَطْوَلُ (taller) · جَمِيلٌ → أَجْمَلُ (more beautiful)",
            "Add مِنْ for 'than': الفِيلُ أَكْبَرُ مِنَ القِطِّ."],
           [ex("الفِيلُ أَكْبَرُ مِنَ القِطِّ", "the elephant is bigger than the cat"),
            ex("أَخِي أَطْوَلُ مِنِّي", "my brother is taller than me"),
            ex("بُرْجُ خَلِيفَةَ أَعْلَى بُرْجٍ فِي العَالَمِ", "Burj Khalifa is the tallest tower in the world")],
           [q("What is 'bigger'?", ["أَكْبَرُ", "كِبَارٌ", "كَبِيرَةٌ"], 0, "كَبِيرٌ on the pattern أَفْعَلُ: أَكْبَرُ."),
            q("Complete: الجَبَلُ أَعْلَى … البَيْتِ", ["مِنَ", "فِي", "عَلَى"], 0, "'Than' is مِنْ: أَعْلَى مِنَ البَيْتِ.")]),

    lesson("c23_numbers", "الأَعْدَادُ مِنْ ١ إِلَى ١٠", "Numbers 1 to 10",
           "Count from one to ten, and read the Arabic digits ٠ – ٩.",
           ["Arabic digits: ٠ ١ ٢ ٣ ٤ ٥ ٦ ٧ ٨ ٩.",
            "Numbers are written left to right, even inside Arabic text: ١٢ is twelve.",
            "With nouns, 3–10 take the opposite gender (ثَلَاثَةُ أَقْلَامٍ، ثَلَاثُ بَنَاتٍ). Learn the counting words first."],
           [ex("وَاحِدٌ، اثْنَانِ، ثَلَاثَةٌ", "one, two, three"), ex("عِنْدِي خَمْسَةُ أَقْلَامٍ", "I have five pens"),
            ex("عُمُرِي عَشْرُ سَنَوَاتٍ", "I am ten years old")],
           [q("Which number is ٧?", ["سَبْعَةٌ", "تِسْعَةٌ", "سِتَّةٌ"], 0, "٧ is seven: سَبْعَةٌ."),
            q("How is twelve written in Arabic digits?", ["١٢", "٢١"], 0, "Digits run left to right: ١٢.")],
           activity=cards("Tap a number to hear it.", [
               ("وَاحِدٌ", "1 ١ one"), ("اثْنَانِ", "2 ٢ two"), ("ثَلَاثَةٌ", "3 ٣ three"), ("أَرْبَعَةٌ", "4 ٤ four"),
               ("خَمْسَةٌ", "5 ٥ five"), ("سِتَّةٌ", "6 ٦ six"), ("سَبْعَةٌ", "7 ٧ seven"), ("ثَمَانِيَةٌ", "8 ٨ eight"),
               ("تِسْعَةٌ", "9 ٩ nine"), ("عَشَرَةٌ", "10 ١٠ ten")])),
]

STAGE_E = [
    lesson("e1_greetings", "التَّحِيَّاتُ وَعِبَارَاتُ الأَدَبِ", "Greetings and polite words",
           "Everyday greetings, their replies and polite phrases.",
           ["Each greeting has its own reply: صَبَاحُ الخَيْرِ → صَبَاحُ النُّورِ.",
            "السَّلَامُ عَلَيْكُمْ → وَعَلَيْكُمُ السَّلَامُ.",
            "Say شُكْرًا (thank you) and reply عَفْوًا (you're welcome)."],
           [ex("السَّلَامُ عَلَيْكُمْ", "peace be upon you (hello)"), ex("وَعَلَيْكُمُ السَّلَامُ", "and upon you be peace (reply)"),
            ex("كَيْفَ حَالُكَ؟", "how are you?"), ex("بِخَيْرٍ، وَالحَمْدُ لِلَّهِ", "fine, thank God")],
           [q("What is the reply to صَبَاحُ الخَيْرِ?", ["صَبَاحُ النُّورِ", "مَعَ السَّلَامَةِ"], 0, "صَبَاحُ الخَيْرِ → صَبَاحُ النُّورِ."),
            q("How do you say 'thank you'?", ["عَفْوًا", "شُكْرًا"], 1, "شُكْرًا is thank you; عَفْوًا is the reply.")],
           activity=cards("Tap a phrase to hear it.", [
               ("السَّلَامُ عَلَيْكُمْ", "hello (peace be upon you)"), ("وَعَلَيْكُمُ السَّلَامُ", "reply to hello"),
               ("صَبَاحُ الخَيْرِ", "good morning"), ("صَبَاحُ النُّورِ", "reply to good morning"),
               ("مَسَاءُ الخَيْرِ", "good evening"), ("أَهْلًا وَسَهْلًا", "welcome"),
               ("مِنْ فَضْلِكَ", "please"), ("شُكْرًا", "thank you"), ("عَفْوًا", "you're welcome"),
               ("مَعَ السَّلَامَةِ", "goodbye")])),

    lesson("e2_introduce", "أُعَرِّفُ بِنَفْسِي", "Introducing yourself",
           "Say your name, age, class, where you live and what you like.",
           ["اِسْمِي … my name is …", "عُمُرِي … سَنَوَاتٍ I am … years old", "أَنَا فِي الصَّفِّ … I am in Class …",
            "أَسْكُنُ فِي … I live in …", "أُحِبُّ … I like …"],
           [ex("اِسْمِي مَرْيَمُ", "my name is Maryam"), ex("عُمُرِي عَشْرُ سَنَوَاتٍ", "I am ten years old"),
            ex("أَنَا فِي الصَّفِّ الخَامِسِ", "I am in Class 5"), ex("أَسْكُنُ فِي دُبَيّ", "I live in Dubai"),
            ex("أُحِبُّ القِرَاءَةَ", "I like reading")],
           [q("How do you say 'my name is'?", ["اِسْمِي", "اِسْمُكَ"], 0, "اِسْمِي: name + ـِي (my)."),
            q("Which means 'I live in'?", ["أَسْكُنُ فِي", "أُحِبُّ"], 0, "أَسْكُنُ فِي means I live in.")],
           activity={"type": "builder", "items": [
               {"words": ["اِسْمِي", "مَرْيَمُ"], "en": "My name is Maryam."},
               {"words": ["أَنَا", "فِي", "الصَّفِّ", "الخَامِسِ"], "en": "I am in Class 5."},
               {"words": ["أَسْكُنُ", "فِي", "دُبَيّ"], "en": "I live in Dubai."},
               {"words": ["أُحِبُّ", "القِرَاءَةَ", "وَالرَّسْمَ"], "en": "I like reading and drawing."}]}),

    lesson("e3_family_body", "أُسْرَتِي وَجِسْمِي", "My family and my body",
           "Words for the family and the parts of the body.",
           ["Family: أَبٌ، أُمٌّ، أَخٌ، أُخْتٌ، جَدٌّ، جَدَّةٌ.", "Body: رَأْسٌ، عَيْنٌ، أُذُنٌ، أَنْفٌ، فَمٌ، يَدٌ، رِجْلٌ.",
            "Add ـِي for 'my': أَبِي، أُمِّي، يَدِي."],
           [ex("هَذَا أَبِي وَهَذِهِ أُمِّي", "this is my father and this is my mother"), ex("لِي أَخٌ وَأُخْتٌ", "I have a brother and a sister"),
            ex("أَرَى بِعَيْنِي", "I see with my eye")],
           [q("Which word means 'grandmother'?", ["جَدٌّ", "جَدَّةٌ", "أُمٌّ"], 1, "جَدَّةٌ is grandmother (ة for feminine)."),
            q("Which body part do you hear with?", ["أُذُنٌ", "أَنْفٌ", "فَمٌ"], 0, "أُذُنٌ is an ear.")],
           activity=cards("Tap a word to hear it.", [
               ("أَبٌ", "father"), ("أُمٌّ", "mother"), ("أَخٌ", "brother"), ("أُخْتٌ", "sister"), ("جَدٌّ", "grandfather"),
               ("جَدَّةٌ", "grandmother"), ("رَأْسٌ", "head"), ("عَيْنٌ", "eye"), ("أُذُنٌ", "ear"), ("أَنْفٌ", "nose"),
               ("فَمٌ", "mouth"), ("يَدٌ", "hand"), ("رِجْلٌ", "leg / foot")])),

    lesson("e4_colours_classroom", "الأَلْوَانُ وَأَدَوَاتُ الصَّفِّ", "Colours and the classroom",
           "Colour words and the things in your classroom.",
           ["Colours: أَحْمَرُ، أَزْرَقُ، أَخْضَرُ، أَصْفَرُ، أَبْيَضُ، أَسْوَدُ.",
            "A colour for a feminine noun changes: قَلَمٌ أَحْمَرُ but وَرْدَةٌ حَمْرَاءُ.",
            "Classroom: قَلَمٌ، كِتَابٌ، دَفْتَرٌ، مِمْحَاةٌ، حَقِيبَةٌ، سَبُّورَةٌ، كُرْسِيٌّ."],
           [ex("القَلَمُ أَحْمَرُ", "the pen is red"), ex("الحَقِيبَةُ زَرْقَاءُ", "the bag is blue"),
            ex("فِي حَقِيبَتِي دَفْتَرٌ وَمِمْحَاةٌ", "in my bag there is a notebook and an eraser")],
           [q("Which word means 'green'?", ["أَخْضَرُ", "أَصْفَرُ", "أَزْرَقُ"], 0, "أَخْضَرُ is green."),
            q("Which is 'an eraser'?", ["دَفْتَرٌ", "مِمْحَاةٌ", "سَبُّورَةٌ"], 1, "مِمْحَاةٌ is an eraser.")],
           activity=cards("Tap a word to hear it.", [
               ("أَحْمَرُ", "red"), ("أَزْرَقُ", "blue"), ("أَخْضَرُ", "green"), ("أَصْفَرُ", "yellow"), ("أَبْيَضُ", "white"),
               ("أَسْوَدُ", "black"), ("قَلَمٌ", "pen"), ("دَفْتَرٌ", "notebook"), ("مِمْحَاةٌ", "eraser"),
               ("حَقِيبَةٌ", "bag"), ("سَبُّورَةٌ", "board"), ("كُرْسِيٌّ", "chair")])),

    lesson("e5_food", "الطَّعَامُ وَالشَّرَابُ", "Food and drink",
           "Words for food and drink, and how to ask for something politely.",
           ["Food: خُبْزٌ، أَرُزٌّ، دَجَاجٌ، سَمَكٌ، تُفَّاحٌ، مَوْزٌ.", "Drinks: مَاءٌ، حَلِيبٌ، عَصِيرٌ.",
            "Ask politely: أُرِيدُ … مِنْ فَضْلِكَ."],
           [ex("أَنَا جَائِعٌ", "I am hungry"), ex("أُرِيدُ مَاءً مِنْ فَضْلِكَ", "I would like water, please"),
            ex("أُحِبُّ الأَرُزَّ وَالدَّجَاجَ", "I like rice and chicken")],
           [q("Which word means 'milk'?", ["حَلِيبٌ", "عَصِيرٌ", "مَاءٌ"], 0, "حَلِيبٌ is milk."),
            q("How do you ask politely for water?", ["أُرِيدُ مَاءً مِنْ فَضْلِكَ", "مَاءٌ!"], 0, "Add مِنْ فَضْلِكَ (please).")],
           activity=cards("Tap a word to hear it.", [
               ("خُبْزٌ", "bread"), ("أَرُزٌّ", "rice"), ("دَجَاجٌ", "chicken"), ("سَمَكٌ", "fish"), ("تُفَّاحٌ", "apples"),
               ("مَوْزٌ", "bananas"), ("مَاءٌ", "water"), ("حَلِيبٌ", "milk"), ("عَصِيرٌ", "juice")])),

    lesson("e6_days_months", "أَيَّامُ الأُسْبُوعِ وَالشُّهُورُ", "Days of the week and months",
           "The days of the week and the twelve months.",
           ["The week starts with يَوْمُ الأَحَدِ (Sunday) in many Arab countries; the UAE weekend is السَّبْتُ وَالأَحَدُ.",
            "Ask the day: مَا اليَوْمُ؟ Answer: اليَوْمُ الخَمِيسُ.",
            "Months used in the UAE: يَنَايِرُ، فِبْرَايِرُ، مَارِسُ … دِيسَمْبَرُ."],
           [ex("اليَوْمُ الخَمِيسُ", "today is Thursday"), ex("عِيدُ مِيلَادِي فِي شَهْرِ مَايُو", "my birthday is in May")],
           [q("Which day is Friday?", ["الجُمُعَةُ", "الخَمِيسُ", "السَّبْتُ"], 0, "الجُمُعَةُ is Friday."),
            q("How do you ask 'what day is it?'", ["مَا اليَوْمُ؟", "كَمْ عُمُرُكَ؟"], 0, "مَا اليَوْمُ؟ asks for the day.")],
           activity=cards("Tap a day or month to hear it.", [
               ("الأَحَدُ", "Sunday"), ("الاثْنَيْنُ", "Monday"), ("الثُّلَاثَاءُ", "Tuesday"), ("الأَرْبِعَاءُ", "Wednesday"),
               ("الخَمِيسُ", "Thursday"), ("الجُمُعَةُ", "Friday"), ("السَّبْتُ", "Saturday"),
               ("يَنَايِرُ", "January"), ("فِبْرَايِرُ", "February"), ("مَارِسُ", "March"), ("أَبْرِيلُ", "April"),
               ("مَايُو", "May"), ("يُونْيُو", "June"), ("يُولْيُو", "July"), ("أُغُسْطُسُ", "August"),
               ("سِبْتَمْبَرُ", "September"), ("أُكْتُوبَرُ", "October"), ("نُوفَمْبَرُ", "November"), ("دِيسَمْبَرُ", "December")])),
]


def _order(lessons: List[Dict[str, Any]], ids: List[str]) -> List[Dict[str, Any]]:
    by_id = {l["id"]: l for l in lessons}
    assert set(ids) == set(by_id), set(ids) ^ set(by_id)
    return [by_id[i] for i in ids]


# Stage B and C mix the first lessons with the extras, in teaching order.
STAGE_B_ORDERED = _order(STAGE_B + EXTRA_B, [
    "b1_short_vowels", "b2_long_vowels", "b13_vowel_length", "b3_tanween", "b4_shadda", "b5_sun_moon", "b6_hamza",
    "b14_hamza_seats", "b7_alif_maqsura", "b11_hidden_alif", "b12_silent_letters", "b8_stopping", "b9_stop_test",
    "b10_syllables", "b15_fluency"])
STAGE_C_ORDERED = _order(STAGE_C + EXTRA_C, [
    "c1_gender", "c14_definite", "c2_number", "c16_adjectives", "c3_demonstratives", "c4_pronouns",
    "c15_attached_pronouns", "c5_relative", "c6_prepositions", "c17_idafa", "c7_time_place", "c12_parts_of_speech",
    "c18_present_tense", "c19_roots", "c13_sentences", "c21_kaana", "c20_linking_words", "c8_questions",
    "c9_emphasis", "c10_negation", "c11_exception", "c22_comparing", "c23_numbers"])

STAGES = [
    {"id": "A", "title_ar": "الحُرُوفُ وَالكِتَابَةُ", "title_en": "Letters and writing",
     "summary_en": "The alphabet, letter shapes, King letters, letter families and the sounds that are easy to confuse.",
     "lessons": STAGE_A},
    {"id": "B", "title_ar": "قَوَاعِدُ القِرَاءَةِ", "title_en": "Reading mechanics",
     "summary_en": "Vowels, long and short, tanween, shadda, sun and moon letters, hamza, hidden and silent letters, the stop test, syllables and fluent reading.",
     "lessons": STAGE_B_ORDERED},
    {"id": "C", "title_ar": "قَوَاعِدُ أَوَّلِيَّةٌ", "title_en": "First grammar",
     "summary_en": "ال and tanween, gender and number, adjectives, pronouns (separate and attached), the possessive construct, verbs, roots, linking words, كان, questions, negation, comparing and numbers.",
     "lessons": STAGE_C_ORDERED},
    {"id": "D", "title_ar": "الكِتَابَةُ وَالتَّرْقِيمُ", "title_en": "Writing and punctuation",
     "summary_en": "Punctuation, building sentences and short paragraphs.",
     "lessons": STAGE_D},
    {"id": "E", "title_ar": "العَرَبِيَّةُ فِي حَيَاتِي", "title_en": "Everyday Arabic",
     "summary_en": "Greetings, introducing yourself, family, body, colours, the classroom, food, days and months.",
     "lessons": STAGE_E},
]

# The vowel grid's sounds for a letter L: one pattern per mark (the frontend and the recording
# script both build the syllables from here, so recorded audio matches what is played).
VOWEL_MARKS = [
    {"id": "fatha", "label_en": "Fatha (a)", "pattern": "{L}َ"},
    {"id": "kasra", "label_en": "Kasra (i)", "pattern": "{L}ِ"},
    {"id": "damma", "label_en": "Damma (u)", "pattern": "{L}ُ"},
    {"id": "sukun", "label_en": "Sukun (no vowel)", "pattern": "أَ{L}ْ"},
    {"id": "long_a", "label_en": "Long aa", "pattern": "{L}َا"},
    {"id": "long_i", "label_en": "Long ii", "pattern": "{L}ِي"},
    {"id": "long_u", "label_en": "Long uu", "pattern": "{L}ُو"},
    {"id": "tanween_fath", "label_en": "Tanween fath (an)", "pattern": "{L}ًا"},
    {"id": "tanween_kasr", "label_en": "Tanween kasr (in)", "pattern": "{L}ٍ"},
    {"id": "tanween_damm", "label_en": "Tanween damm (un)", "pattern": "{L}ٌ"},
    {"id": "shadda_fatha", "label_en": "Shadda + fatha", "pattern": "أَ{L}َّ"},
    {"id": "shadda_kasra", "label_en": "Shadda + kasra", "pattern": "أَ{L}ِّ"},
    {"id": "shadda_damma", "label_en": "Shadda + damma", "pattern": "أَ{L}ُّ"},
]
# Letters shown in the vowel grid (not ا or ء, which don't carry these marks on their own).
GRID_LETTERS = [l for l, _, _ in ALPHABET if l not in ("ا", "ء")]

# Words in a chapter's grammar rule (rule_name_en / rule_name_ar) or title that show it teaches this
# lesson's topic: used for the "In your textbook" links. Lower-case English, no tashkeel.
TEXTBOOK_KEYWORDS: Dict[str, List[str]] = {
    "a1_alphabet": ["alphabet"], "a2_letter_shapes": ["letter forms", "letter shapes", "letter positions"],
    "a3_king_letters": ["non-connect", "connecting letters"], "a4_letter_families": ["dots"],
    "a5_sound_pairs": ["pronunciation", "similar sounds"], "a6_heavy_light": ["emphatic", "heavy letters"],
    "b1_short_vowels": ["short vowel", "harakat"], "b2_long_vowels": ["long vowel", "madd"],
    "b13_vowel_length": ["long vowel", "madd"], "b3_tanween": ["tanween", "nunation"], "b4_shadda": ["shadda"],
    "b5_sun_moon": ["sun letter", "moon letter", "solar", "lunar"], "b6_hamza": ["hamza", "hamzat"],
    "b14_hamza_seats": ["hamza"], "b7_alif_maqsura": ["alif maqsura", "maqsura"], "b11_hidden_alif": ["dagger alif"],
    "b12_silent_letters": ["plural waw", "five verbs"], "b8_stopping": ["pause", "waqf"],
    "b9_stop_test": ["taa marbuta", "ta marbuta", "marbutah"], "b10_syllables": ["syllable"], "b15_fluency": ["fluency", "reading aloud"],
    "c1_gender": ["gender", "masculine", "feminine"], "c14_definite": ["definite", "al- prefix"],
    "c2_number": ["dual", "singular", "broken plural", "sound plural", "plural noun"], "c16_adjectives": ["adjective", "concord", "agreement"],
    "c3_demonstratives": ["demonstrative"], "c4_pronouns": ["personal pronoun", "separate pronoun"],
    "c15_attached_pronouns": ["attached", "possessive"], "c5_relative": ["relative pronoun"],
    "c6_prepositions": ["preposition"], "c17_idafa": ["idafa", "construct", "genitive construct"],
    "c7_time_place": ["adverb", "time and place"], "c12_parts_of_speech": ["parts of speech", "past tense"],
    "c18_present_tense": ["present tense"], "c19_roots": ["root", "derivation", "derived"],
    "c13_sentences": ["nominal sentence", "verbal sentence"], "c21_kaana": ["kana"],
    "c20_linking_words": ["conjunction", "connector", "sequence"], "c8_questions": ["interrogative", "question"],
    "c9_emphasis": ["inna", "emphasis"], "c10_negation": ["negation", "prohibit"], "c11_exception": ["exception", "istithna"],
    "c22_comparing": ["comparative", "superlative"], "c23_numbers": ["numbers", "numeral", "counting"],
    "d1_punctuation": ["punctuation", "colon", "comma", "question mark", "exclamat"],
    "d2_build_sentences": ["word order", "sentence order"], "d3_paragraph": ["main idea", "paragraph"],
    "e1_greetings": ["greeting"], "e2_introduce": ["introduc"], "e3_family_body": ["family", "body"],
    "e4_colours_classroom": ["colour", "color", "school"], "e5_food": ["food"], "e6_days_months": ["days", "week", "month"],
}


def all_lessons():
    for stage in STAGES:
        yield from stage["lessons"]


def foundation_course() -> Dict[str, Any]:
    return {
        "title_ar": "أَسَاسِيَّاتُ اللُّغَةِ العَرَبِيَّةِ",
        "title_en": "Foundation in Basic Arabic",
        "summary_en": "Five stages, from the alphabet to everyday Arabic, taken before Class 1.",
        "alphabet": [{"letter": l, "name": n, "sound_en": s, "king": l in KING_LETTERS} for l, n, s in ALPHABET],
        "vowel_marks": VOWEL_MARKS,
        "grid_letters": GRID_LETTERS,
        "stages": STAGES,
    }


def get_lesson(lesson_id: str) -> Optional[Dict[str, Any]]:
    return next((l for l in all_lessons() if l["id"] == lesson_id), None)


def recording_script() -> List[Dict[str, str]]:
    """Every Arabic text the Foundation course plays, grouped, for a native speaker to record.

    Letters and syllables first (the sounds learners copy most), then words and sentences.
    """
    seen, out = set(), []

    def add(text: str, group: str, hint: str = "") -> None:
        text = " ".join(text.split())
        if text and text not in seen:
            seen.add(text)
            out.append({"text": text, "group": group, "hint": hint})

    for l, name, sound in ALPHABET:
        add(name, "1 Letter names", f"{l}: {sound}")
    for letter in GRID_LETTERS:
        for mark in VOWEL_MARKS:
            add(mark["pattern"].replace("{L}", letter), "2 Syllables", f"{letter} · {mark['label_en']}")
    for lesson in all_lessons():
        activity = lesson.get("activity") or {}
        for part in (activity.get("items") or []):
            if isinstance(part, dict) and part.get("parts"):
                for syllable in part["parts"]:
                    add(syllable, "2 Syllables", f"from {part['word']}")
    for lesson in all_lessons():
        activity = lesson.get("activity") or {}
        for ex_ in lesson["examples"]:
            add(ex_["ar"], "3 Words and sentences", ex_["en"])
        for item in activity.get("items") or []:
            if isinstance(item, str):
                add(item, "3 Words and sentences", "fluency")
            elif isinstance(item, dict):
                if item.get("ar"):
                    add(item["ar"], "3 Words and sentences", item.get("en", ""))
                elif item.get("text"):
                    add(item["text"], "3 Words and sentences", lesson["title_en"])
                elif item.get("word"):
                    add(item["word"], "3 Words and sentences", "syllables")
                elif item.get("words"):
                    add(" ".join(item["words"]), "3 Words and sentences", item.get("en", ""))
        for family in activity.get("families") or []:
            for word in family["words"]:
                add(word["ar"], "3 Words and sentences", word["en"])
    return out
