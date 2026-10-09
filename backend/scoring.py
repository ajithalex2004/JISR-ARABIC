import re
import unicodedata
from typing import Dict, Any, Tuple, Optional

# Arabic Unicode ranges for Tashkeel (diacritics) and Tatweel
ARABIC_DIACRITICS = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]")
TATWEEL = re.compile(r"\u0640")
PUNCTUATION = re.compile(r"[؟!\.,،؛:\'\"()\[\]\-—]")

def normalize_arabic_text(text: str, strip_diacritics: bool = True) -> str:
    """
    Normalizes Arabic text according to Section 10 specification:
    - Normalises whitespace
    - Removes final/surrounding punctuation
    - Strips tatweel (kashida)
    - Strips optional vowel marks (tashkeel) if specified
    - PRESERVES meaningful distinctions:
      * ة (taa marbuta) is NOT normalized to ه (haa)
      * ي (yaa) is NOT normalized to ى (alif maqsura)
      * Hamza distinctions are preserved
    """
    if not text:
        return ""
    
    # Unicode normalize
    norm = unicodedata.normalize("NFKC", str(text).strip())
    
    # Strip tatweel
    norm = TATWEEL.sub("", norm)
    
    # Strip diacritics
    if strip_diacritics:
        norm = ARABIC_DIACRITICS.sub("", norm)
        
    # Strip punctuation
    norm = PUNCTUATION.sub("", norm)
    
    # Normalize whitespace to single spaces
    norm = re.sub(r"\s+", " ", norm).strip()
    
    return norm


def evaluate_activity_answer(
    activity_data: Dict[str, Any],
    user_answer: Any
) -> Tuple[bool, float, float, str, str, Optional[Any], bool]:
    """
    Evaluates learner's submitted answer strictly on the server.
    Returns:
    (is_correct, score, max_score, feedback_ar, feedback_en, correct_solution, is_awaiting_tutor)
    """
    activity_type = activity_data.get("type", "choice")
    max_score = float(activity_data.get("points", 1.0))
    pinned_answer = activity_data.get("correct_answer")
    declared_alternatives = activity_data.get("acceptable_alternatives", [])
    
    # 1. Subjective/Tutor-graded (writing or free speech)
    if activity_type in ["writing", "speaking", "tutor_rubric"]:
        return (
            True,
            0.0,
            max_score,
            "تم استلام إجابتك وإرسالها للمعلم للمراجعة وتقديم الملاحظات.",
            "Your submission was received and routed to your teacher for review and feedback.",
            None,
            True
        )

    # 2. Multiple choice / Option selection
    if activity_type == "choice":
        # Check against stable option ID
        user_str = str(user_answer).strip().lower()
        correct_str = str(pinned_answer).strip().lower()
        is_correct = (user_str == correct_str)
        
        # If user passed Arabic text instead of option ID, compare normalized
        if not is_correct and isinstance(user_answer, str):
            norm_user = normalize_arabic_text(user_answer)
            norm_correct = normalize_arabic_text(str(activity_data.get("correct_label", "")))
            if norm_correct and norm_user == norm_correct:
                is_correct = True

        score = max_score if is_correct else 0.0
        fb_ar = "أحسنت! إجابة صحيحة وممتازة." if is_correct else "إجابة غير صحيحة، حاول مجددًا."
        fb_en = "Excellent! Correct answer." if is_correct else "Incorrect. Let's review the rule and try again."
        return (is_correct, score, max_score, fb_ar, fb_en, pinned_answer, False)

    # 3. Sentence builder / Tile ordering
    if activity_type in ["sentence_builder", "ordering"]:
        # user_answer can be list of words/ids or a single string
        if isinstance(user_answer, list):
            user_tokens = [normalize_arabic_text(t) for t in user_answer]
            user_joined = " ".join([t for t in user_tokens if t])
        else:
            user_joined = normalize_arabic_text(str(user_answer))
            
        correct_norm = normalize_arabic_text(str(pinned_answer))
        is_correct = (user_joined == correct_norm)
        
        # Check declared acceptable alternatives
        if not is_correct:
            for alt in declared_alternatives:
                if user_joined == normalize_arabic_text(alt):
                    is_correct = True
                    break

        score = max_score if is_correct else 0.0
        fb_ar = "ممتاز! قمت ببناء الجملة بالترتيب الصحيح." if is_correct else "الترتيب غير صحيح، انتبه لقواعد ترتيب الجملة في العربية."
        fb_en = "Great job! You assembled the sentence correctly." if is_correct else "Sentence order is incorrect. Check the subject and predicate."
        return (is_correct, score, max_score, fb_ar, fb_en, pinned_answer, False)

    # 4. Short answer / Fill in the blank
    if activity_type in ["fill_blank", "short_text"]:
        norm_user = normalize_arabic_text(str(user_answer))
        norm_correct = normalize_arabic_text(str(pinned_answer))
        is_correct = (norm_user == norm_correct)

        if not is_correct:
            for alt in declared_alternatives:
                if norm_user == normalize_arabic_text(alt):
                    is_correct = True
                    break

        score = max_score if is_correct else 0.0
        fb_ar = "إجابة صحيحة ورائعة!" if is_correct else "إجابة غير دقيقة. راجع المفردات وحاول مرة أخرى."
        fb_en = "Correct and accurate!" if is_correct else "Not quite right. Check vocabulary and try again."
        return (is_correct, score, max_score, fb_ar, fb_en, pinned_answer, False)

    # 5. Matching pairs
    if activity_type == "matching":
        # expects dict of user pairs {k: v}
        correct_pairs = pinned_answer if isinstance(pinned_answer, dict) else {}
        if not isinstance(user_answer, dict):
            return (False, 0.0, max_score, "صيغة غير صحيحة", "Invalid format", pinned_answer, False)
        
        correct_count = 0
        total_pairs = len(correct_pairs) or 1
        for k, v in correct_pairs.items():
            if str(user_answer.get(k, "")).strip() == str(v).strip():
                correct_count += 1
                
        is_correct = (correct_count == total_pairs)
        score = (correct_count / total_pairs) * max_score
        fb_ar = f"أحسنت! طابقت {correct_count} من {total_pairs} عناصر."
        fb_en = f"Well done! You matched {correct_count} of {total_pairs} pairs correctly."
        return (is_correct, score, max_score, fb_ar, fb_en, pinned_answer, False)

    # Default fallback
    return (False, 0.0, max_score, "تم استلام الإجابة", "Answer recorded", pinned_answer, False)
