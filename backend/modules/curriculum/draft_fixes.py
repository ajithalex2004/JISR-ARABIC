"""Corrections to AI lesson drafts that are still waiting for teacher review, applied on deploy.

The 20 book-aligned Class 1 lessons (Terms 2-3, see book_restructure.py) were drafted by the AI
from their textbook pages, then pre-checked against the book (the "Class 1 New Lessons - AI
Pre-Check" doc). The clear-cut errors it found are fixed here before teachers review the drafts;
questions that need the book open are left to the teachers.

Like content_fixes.py, a fix never edits a stored version in place: the corrected draft is saved
as a new version, still "content_pending" and still the lesson's AI draft, and the old one is
marked "superseded" and kept in the history. A fix runs only while its wrong text is still in the
pending draft, so it applies once and leaves later edits and published lessons alone.
"""
import datetime
import hashlib
import json
import re
import uuid

from sqlalchemy import inspect, text

from backend.modules.curriculum.content_fixes import _replace_in

_MARK = re.compile(r"[\u064b-\u065f\u0670]")


def E(literal: str) -> str:
    """A regex for literal text whose vowel marks may be stored in any order (e.g. shadda before fatha)."""
    out, i = [], 0
    while i < len(literal):
        ch = literal[i]
        i += 1
        marks = ""
        while i < len(literal) and _MARK.match(literal[i]):
            marks += literal[i]
            i += 1
        out.append(re.escape(ch))
        if marks:
            out.append("[%s]{%d}" % ("".join(sorted(set(marks))), len(marks)))
    return "".join(out)

def _ids(term):
    return [f"lesson_g1_t{term}_bk{i:02d}" for i in range(1, 11)]

# Spelling slips the drafter repeated across lessons.
_EVERY = [
    (E("كَاكِن"), "كَائِن", "Ka'in (creature), not kakin."),
    (E("أَوْ ال"), "أَوِ ال", "Aw takes kasra before al-."),
    (E("يَسْتَخْدَمُ"), "يَسْتَخْدِمُ", "Yastakhdimu."),
    (E("مَظْلِم"), "مُظْلِم", "Muzlim (dark)."),
    (E("مَلَوَّن"), "مُلَوَّن", "Mulawwan (coloured)."),
]

_T = lambda n, b: f"lesson_g1_t{n}_bk{b:02d}"

DRAFT_FIXES = [(lid, p, r, why) for lid in _ids(2) + _ids(3) for p, r, why in _EVERY] + [
    # Term 2
    (_T(2, 1), "^أ-خ-ط-ب-و-ط$", "", "Octopus is a borrowed word with no root."),
    (_T(2, 1), E("أَكُلُ"), "آكُلُ", "I eat is aakulu."),
    (_T(2, 1), r"^(Lion|Octopus) \(أ[َُ]\)$", r"\1", "English options gave the answer away."),
    (_T(2, 2), E("بَذُورٌ"), "بُذُورٌ", "Seeds is buthur."),
    (_T(2, 2), E("يَحْتَوِي العِنَبُ عَلَى حَرْفِ البَاءِ فِي آخِرِهِ."), "كَلِمَةُ (عِنَبٌ) تَنْتَهِي بِحَرْفِ البَاءِ.", "The word ends in Baa, not the fruit."),
    (_T(2, 2), E("The word grapes contains the letter Baa at the end."), "The word 'grapes' (عِنَبٌ) ends with the letter Baa.", "Matches the corrected example."),
    (_T(2, 2), E("الزَّبِيبُ فِيهِ صَوْتُ المَدِّ الطَّوِيلِ."), "فِي كَلِمَةِ (زَبِيبٌ) صَوْتُ المَدِّ الطَّوِيلِ (بِي).", "The word has the long vowel, not the raisins."),
    (_T(2, 2), E("Raisins contain the long vowel sound."), "The word 'raisins' (زَبِيبٌ) has the long vowel sound (bee).", "Matches the corrected example."),
    (_T(2, 2), "^ب-ر-ت-ق-ل$", "", "Orange is a borrowed word with no root."),
    (_T(2, 3), E("التُّوفَاحِ"), "التُّفَّاحِ", "Not a word; apples is at-tuffah."),
    (_T(2, 3), "خَيَالِيٌ(?!ّ)", "خَيَالِيٌّ", "Missing shadda."),
    (_T(2, 4), "^" + E("ثَلَاثَةٌ") + "$", "ثَوْبٌ", "Practice 4 had two right answers (ث is also in the middle of ثلاثة)."),
    (_T(2, 4), E("Three (Thalathah)"), "Garment (Thawb)", "Matches the replaced option."),
    (_T(2, 4), "^ث-ع-ل$", "ث-ع-ل-ب", "Tha'lab has a four-letter root."),
    (_T(2, 4), E("مَفْتَرِس"), "مُفْتَرِس", "Muftaris (predator)."),
    (_T(2, 4), E("يَنِزِلُ"), "يَنْزِلُ", "Yanzilu."),
    (_T(2, 4), E("قَرِائِيِّ"), "قِرَائِيِّ", "Qira'iyy (reading)."),
    (_T(2, 5), E("جِرَانٌ - فِجْلٌ"), "جِدَارٌ - فِجْلٌ", "Not a word; wall (jidar) is a short-Ji example."),
    (_T(2, 5), E("Neighbors - Radish"), "Wall - Radish", "Matches the corrected example."),
    (_T(2, 5), "^جَالِ$", "جَالَ", "Jaala (roamed)."),
    (_T(2, 5), E("الجَرْجِيرَ الخَضْرَاءَ"), "الجَرْجِيرَ الأَخْضَرَ", "Masculine adjective."),
    (_T(2, 5), "حيَوَان", "حَيَوَان", "Missing fatha."),
    (_T(2, 5), E("market dialogue"), "canteen dialogue", "The Arabic says canteen (المقصف)."),
    (_T(2, 6), E("يُوَضَعُ"), "يُوضَعُ", "Yuda'u."),
    (_T(2, 7), E("خَ - خَيَارٌ"), "خَ - خَرُوفٌ", "خِيَار has kasra; sheep is a short-Kha example."),
    (_T(2, 7), E("Short Kha in cucumber vs"), "Short Kha in sheep vs", "Matches the corrected example."),
    (_T(2, 8), E("الْجَزَرَ"), "الذُّرَةَ", "The wolf in the story eats corn, not carrots."),
    (_T(2, 8), E("This wolf eats the carrot."), "This wolf eats the corn.", "Matches the corrected sentence."),
    (_T(2, 9), E("يَعِيشُ فِي الْغَابَةِ"), "يَعِيشُ فِي إِفْرِيقْيَا", "Giraffes don't live in forests."),
    (_T(2, 10), E("السَّنْجَاب"), "السِّنْجَاب", "Sinjab, as on the card."),
    (_T(2, 10), "^(ش-ك-ل|ش-ا-ي)$", "", "Chocolate and tea are borrowed words with no root."),
    (_T(2, 10), E("شَمَامٌ"), "شَمَّامٌ", "Shammam (melon)."),
    (_T(2, 10), E("الشَّوْكُولاتَةَ"), "الشُّوكُولاَتَةَ", "One spelling, as on the card."),
    (_T(2, 10), E("لِلْتَّكَلُّمِ"), "لِلتَّكَلُّمِ", "Stray sukun."),
    (_T(2, 10), E("كَيْفَ تَقُولُ بِاللُّغَةِ العَرَبِيَّةِ: (We are in Grade 1)?"), "كَيْفَ تَقُولُ: نَحْنُ فِي الصَّفِّ الأَوَّلِ؟", "English inside the Arabic question."),
    # Term 3
    (_T(3, 1), E("صَـ - صَابُونٌ / صَارُوخٌ"), "صَـ - صَبَاحٌ / صَا - صَارُوخٌ", "Short and long examples were mixed up."),
    (_T(3, 1), E("Sa (Short) - Rocket (Long Madd Alif)"), "Sa (short): morning / Saa (long): rocket", "Matches the corrected example."),
    (_T(3, 1), E("صُـ - صُوصٌ"), "صُـ - صُنْدُوقٌ / صُو - صُوصٌ", "Short and long examples were mixed up."),
    (_T(3, 1), E("Su (Short) - Chick (Long Madd Waw)"), "Su (short): box / Soo (long): chick", "Matches the corrected example."),
    (_T(3, 1), E("صِـ - صِينَاتٌ / صِيصَانٌ"), "صِـ - صِنَّارَةٌ / صِي - صِيصَانٌ", "صِينَات is not a word."),
    (_T(3, 1), E("Si (Short) - Chicks (Long Madd Yaa)"), "Si (short): fishing rod / See (long): chicks", "Matches the corrected example."),
    (_T(3, 1), E("مَقَصٌّ"), "مِقَصٌّ", "Scissors is miqass."),
    (_T(3, 1), E("صَنَّارَةٌ"), "صِنَّارَةٌ", "Sinnara, as on the card."),
    (_T(3, 1), E("Sannarah"), "Sinnarah", "Matches the corrected spelling."),
    (_T(3, 1), E("صَوْص"), "صُوص", "Soos (chick), as on the card."),
    (_T(3, 1), E("الصَّوْص"), "الصُّوص", "Soos (chick), as on the card."),
    (_T(3, 1), E("عَنْ ال"), "عَنِ ال", "'An takes kasra before al-."),
    (_T(3, 1), E("يَاْكُلُ"), "يَأْكُلُ", "Hamza on the alif."),
    (_T(3, 1), E("يُصْتَادُ"), "يُصْطَادُ", "Yustadu."),
    (_T(3, 1), E("تَوْجَدُ"), "تُوجَدُ", "Tujadu."),
    (_T(3, 1), r" \([أون]\)$", "", "Stray letters after the options."),
    (_T(3, 2), E("ضَوْءٌ (مَدُّ الوَاوِ)"), "وُضُوءٌ (مَدُّ الوَاوِ)", "ضَوْء has no long waw; wudu' does."),
    (_T(3, 2), E("Light (Long vowel Dhoo)"), "Ablution (Long vowel Dhoo)", "Matches the corrected example."),
    (_T(3, 2), E("ضَارٌ (مَدُّ الأَلِفِ)"), "ضَارٌّ (مَدُّ الأَلِفِ)", "Missing shadda."),
    (_T(3, 2), E("أَيُّ الكَلِمَاتِ الآتِيَةِ تَعْنِي (Eggs) فِي القَامُوسِ المُصَوَّرِ؟"), "أَيُّ كَلِمَةٍ تَدُلُّ عَلَى صُورَةِ البَيْضِ فِي القَامُوسِ المُصَوَّرِ؟", "English inside the Arabic question."),
    (_T(3, 2), "[۟۠]", "", "Stray Quranic mark."),
    (_T(3, 2), E("الضَّفْدَع"), "الضِّفْدَع", "Difda', as on the card."),
    (_T(3, 2), E("هَلْ البَيْضُ"), "هَلِ البَيْضُ", "Hal takes kasra before al-."),
    (_T(3, 2), E("ضِدُّ كَلِمَة ("), "ضِدُّ كَلِمَةِ (", "Genitive."),
    (_T(3, 2), "^فَوْقٌ$", "فَوْقَ", "Fawqa."),
    (_T(3, 2), "بَرْمَائِيٌ(?!ّ)", "بَرْمَائِيٌّ", "Missing shadda."),
    (_T(3, 3), E("يُنَثِّرُ"), "يَنْثُرُ", "Yanthuru."),
    (_T(3, 3), E("قطَرَاتٍ"), "قَطَرَاتٍ", "Missing fatha."),
    (_T(3, 3), E("مَالَهُ"), "مَا لَهُ", "Two words."),
    (_T(3, 3), E("الْتَمْيِيزُ"), "التَّمْيِيزُ", "At-tamyiz."),
    (_T(3, 3), E("عِكْسُ"), "عَكْسُ", "'Aks (opposite)."),
    (_T(3, 3), E("المُمَزَّجِ"), "المَمْزُوجِ", "Mamzuj (mixed)."),
    (_T(3, 4), E("جُوعَانُ"), "جَوْعَانُ", "Jaw'an (hungry), as in the exam."),
    (_T(3, 4), E("الْوَلاَدُ"), "الوَلَدُ", "The boy is al-walad."),
    (_T(3, 4), E("يَعْتَذِي"), "يَتَغَذَّى", "Yataghadda (feeds on)."),
    (_T(3, 4), E("بِالْرَّغْبَةِ"), "بِالرَّغْبَةِ", "Stray sukun."),
    (_T(3, 4), E("الْطِّفْلُ"), "الطِّفْلُ", "Stray sukun."),
    (_T(3, 4), E("المُلَكَلِّمِ"), "المُتَكَلِّمِ", "Al-mutakallim (first person)."),
    (_T(3, 4), E("غَابَةٌ / أَشْجَارٌ كَثِيرَةٌ"), "أَشْجَارٌ كَثِيرَةٌ", "The right option repeated the word asked about."),
    (_T(3, 4), E("I search for food in the forest."), "I search for food.", "The Arabic does not mention the forest."),
    (_T(3, 5), "^" + E("دَرَفَ") + "$", "خَرُوفٌ", "Obscure word; a Class 1 child can read sheep."),
    (_T(3, 5), "^Darafa$", "Kharoof (Sheep)", "Matches the replaced option."),
    (_T(3, 5), "^" + E("سَفَحَ") + "$", "سَيْفٌ", "Obscure word; a Class 1 child can read sword."),
    (_T(3, 5), "^Safaha$", "Sayf (Sword)", "Matches the replaced option."),
    (_T(3, 5), E("قَبَّعَةَ"), "قُبَّعَةَ", "Qubba'a (hat)."),
    (_T(3, 5), E("الْثَّوْبَ"), "الثَّوْبَ", "Stray sukun."),
    (_T(3, 5), "^ف-ر-ل$", "", "Strawberry is a borrowed word with no root."),
    (_T(3, 5), E("مَغَذِّيَة"), "مُغَذِّيَة", "Mughaddhiya (nutritious)."),
    (_T(3, 5), E("الْتَمْيِيزُ"), "التَّمْيِيزُ", "At-tamyiz."),
    (_T(3, 6), "^(ل-و-م|ل-م-ن|ك-ي-و)$", "", "Llama, lemon and kiwi are borrowed words with no root."),
    (_T(3, 6), E("اللَّوَحِ"), "اللَّوْحِ", "Al-lawh (board)."),
    (_T(3, 6), E("مِنْ الدَّاخِلِ"), "مِنَ الدَّاخِلِ", "Min takes fatha before al-."),
    (_T(3, 6), E("مَفِيدَةً"), "مُفِيدَةً", "Mufida (healthy)."),
    (_T(3, 6), E("فَتِحٌ"), "فَاتِحٌ", "Fatih (light colour)."),
    (_T(3, 6), "^" + E("كَلِمَة ("), "كَلِمَةُ (", "Nominative."),
    (_T(3, 7), E("الٱخْتِيَارِ"), "الاخْتِيَارِ", "Wrong alef character."),
    (_T(3, 7), E("يَقْوِي"), "يَقْوَى", "Yaqwa."),
    (_T(3, 7), E("Covered / Went mad"), "(Night) fell / Covered", "Child-appropriate meaning."),
    (_T(3, 7), E("مَنْ الَّذِي"), "مَنِ الَّذِي", "Man takes kasra before al-."),
    (_T(3, 7), E("القَرَّائِيِّ"), "القِرَائِيِّ", "Qira'iyy (reading)."),
    (_T(3, 7), E("مِمَّايَلِي"), "مِمَّا يَلِي", "Two words."),
    (_T(3, 7), E("تَجْمَعُ الزُّهُورَ"), "تَجْمَعُ رَحِيقَ الزُّهُورِ", "Bees collect nectar, not flowers."),
    (_T(3, 7), E("the bee collects flowers"), "the bee collects nectar from flowers", "Matches the corrected sentence."),
    (_T(3, 8), E("الـتَّفْرِيقُ"), "التَّفْرِيقُ", "Stray stretch mark."),
    (_T(3, 8), E("وَطْواط"), "وَطْوَاط", "One spelling of bat."),
    (_T(3, 9), E("بِيُوت"), "بُيُوت", "Buyut (houses)."),
    (_T(3, 9), E("تُنْتَهَى"), "تَنْتَهِي", "Tantahi."),
    (_T(3, 9), "^أَمَامٌ$", "أَمَامَ", "Amama."),
    (_T(3, 9), "^فَوْقٌ$", "فَوْقَ", "Fawqa."),
    (_T(3, 9), "^" + E("يَاسَمِينُ") + "$", "يَاسَمِينٌ", "Tanween on the option."),
    (_T(3, 9), "^ي-س-م$", "", "Jasmine is a borrowed word with no root."),
    (_T(3, 10), E("ثَمَانِيَةُ خِرْفَانٍ"), "تِسْعَةُ خِرْفَانٍ", "The book has nine sheep."),
    (_T(3, 10), E("ثَمَانِيَةَ خِرْفَانٍ"), "تِسْعَةَ خِرْفَانٍ", "The book has nine sheep."),
    (_T(3, 10), E("eight sheep"), "nine sheep", "The book has nine sheep."),
    (_T(3, 10), r"(?<=\. )" + E("يَسْتَطِيعُ مَاجِدٌ أَنْ يَعُدَّ مِنْ 1 إِلَى 20."), "يَسْتَطِيعُ مَاجِدٌ أَنْ يَعُدَّ مِنْ 1 إِلَى 20، وَيَسْتَطِيعُ أَنْ يَنُطَّ 20 نَطَّةً.", "The book's sentence about 20 jumps, which practice 4 asks about."),
    (_T(3, 10), r"(?<=\. )" + E("Majid can count from 1 to 20."), "Majid can count from 1 to 20, and he can jump 20 jumps.", "Matches the restored sentence."),
    (_T(3, 10), E("مُكَّوَنٍ"), "مُكَوَّنٍ", "Mukawwan."),
    (_T(3, 10), E("يَنْطَّ"), "يَنُطَّ", "Yanutta."),
    (_T(3, 10), E("جَرْفَانِ"), "خَرُوفَانِ", "Two lambs is kharufan."),
    (_T(3, 10), E("إِثْنَا"), "اثْنَا", "Ithna starts with hamzat wasl."),
    (_T(3, 10), E("عَشَرَةُ قِطَطٍ"), "عَشْرُ قِطَطٍ", "Ten (with a feminine plural) is 'ashru."),
    (_T(3, 10), "^ص-ص-ص$", "ص-و-ص", "Root of chicks."),
    (_T(3, 10), E("عَقْدًا ثَانِيًا بَعْدَ العَشَرَةِ"), "ضِعْفَ العَشَرَةِ", "Twenty is double ten."),
]


AI_DRAFTER = "ai-drafter"  # drafting.AI_DRAFTER; repeated here so this module stays import-light


def apply_draft_fixes(conn, fixes=DRAFT_FIXES) -> list:
    """Save a corrected copy of each pending AI draft that still has a wrong text; returns lesson ids."""
    tables = inspect(conn).get_table_names()
    if "lesson_versions" not in tables:
        return []
    has_audit = "curriculum_audit_events" in tables
    grouped = {}
    for lesson_id, pattern, replacement, reason in fixes:
        grouped.setdefault(lesson_id, []).append((re.compile(pattern), replacement, reason))
    fixed = []
    for lesson_id, items in grouped.items():
        row = conn.execute(text(
            "SELECT id, version_tag, content_json FROM lesson_versions WHERE lesson_id=:l AND status='content_pending' "
            "AND created_by=:by ORDER BY created_at DESC"), {"l": lesson_id, "by": AI_DRAFTER}).first()
        if row is None:
            continue
        try:
            data = json.loads(row.content_json or "")
        except ValueError:
            continue
        reasons = []
        for regex, replacement, reason in items:
            # Count a fix only when it changes the text, so a deploy after it has run does nothing.
            fixed_data, _ = _replace_in(data, regex, replacement)
            if fixed_data != data:
                data = fixed_data
                if reason not in reasons:
                    reasons.append(reason)
        if not reasons:
            continue
        content = json.dumps(data, ensure_ascii=False)
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        new_id = f"{row.id}_fix_{digest[:8]}"[:100]
        tag = f"{row.version_tag or 'ai'}-fix"[:50]
        now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        conn.execute(text("UPDATE lesson_versions SET status='superseded' WHERE id=:id"), {"id": row.id})
        conn.execute(text(
            "INSERT INTO lesson_versions (id, lesson_id, version_tag, content_json, content_hash, is_active, status, "
            "created_by, created_at) VALUES (:id, :l, :tag, :c, :h, :f, 'content_pending', :by, :now)"),
            {"id": new_id, "l": lesson_id, "tag": tag, "c": content, "h": digest, "f": False, "by": AI_DRAFTER,
             "now": now})
        if has_audit:
            conn.execute(text(
                "INSERT INTO curriculum_audit_events (id, actor_id, action, lesson_id, version_id, version_tag, "
                "details_json, created_at) VALUES (:id, NULL, 'draft_fix', :l, :v, :tag, :d, :now)"),
                {"id": str(uuid.uuid4()), "l": lesson_id, "v": new_id, "tag": tag, "now": now,
                 "d": json.dumps({"action": "draft_fix", "replaces": row.id, "fixes": len(reasons),
                                  "reasons": reasons}, ensure_ascii=False)})
        fixed.append(lesson_id)
    return fixed
