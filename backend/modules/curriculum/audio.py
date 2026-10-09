"""Audio policy and cache metadata for the three-level speech strategy."""
import hashlib
import os
import re
import json
import urllib.request
import urllib.error

def get_tts_info():
    """Returns supported TTS modes, Arabic voice configs, and playback parameters."""
    return {
        "engine": "Curriculum audio cache → server TTS → browser speech fallback",
        "server_provider": os.getenv("FAHIM_TTS_PROVIDER", "google").lower(),
        "server_generation_enabled": True,
        "provider_label": "Synthetic Arabic Speech (نطق آلي اصطناعي - ليس تسجيلاً رسمياً للمعلم)",
        "supported_speeds": [
            {"id": "normal", "label_en": "Normal (1.0x)", "label_ar": "عادي", "rate": 1.0},
            {"id": "gentle", "label_en": "Gentle (0.8x)", "label_ar": "هادئ", "rate": 0.8},
            {"id": "slow", "label_en": "Slow (0.6x)", "label_ar": "بطيء ومفصل", "rate": 0.6}
        ],
        "supported_repeats": [1, 2, 3],
        "voices": [
            {"id": "ar-SA-Standard", "name": "Modern Standard Arabic (ar-SA)", "lang": "ar-SA", "approved": True},
            {"id": "ar-AE-Standard", "name": "Emirati Arabic Support (ar-AE)", "lang": "ar-AE", "approved": _is_voice_approved("ar-AE")},
        ]
    }


def synthesize_audio(speed: float=1.0, lang: str='ar-SA', content_version: str='1', *, text: str):
    """
    Server-side TTS metadata endpoint.
    Labels audio explicitly as synthetic to satisfy Section 11.
    """
    normalized = re.sub(r"\s+", " ", text).strip()
    voice = lang or "ar-SA"
    if not _is_voice_approved(voice):
        return {
            "text": text, "normalized_text": normalized, "speed": speed, "lang": voice,
            "status": "approval_required", "audio_url": None, "is_synthetic": True,
            "attribution": "Fahim Synthetic Speech Engine (نطق آلي تجريبي)",
            "can_use_browser_speech": True,
            "fallback_order": ["curriculum_cache", "server_tts", "browser_speech"]
        }
    pronunciation_settings = "standard-arabic-v1"
    cache_key = hashlib.sha256(f"{normalized}|{voice}|{content_version}|{pronunciation_settings}".encode("utf-8")).hexdigest()
    remote_filename = f"{cache_key}.mp3"
    from backend.storage import get_storage_adapter
    storage = get_storage_adapter()

    cache_root = os.getenv("FAHIM_AUDIO_CACHE_DIR", os.path.join("tmp", "audio-cache"))
    cache_path = os.path.join(cache_root, remote_filename)
    cached = os.path.isfile(cache_path) or storage.file_exists(remote_filename)
    manifest_path = os.path.join(cache_root, "manifest.json")
    manifest = {}
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as handle:
                manifest = json.load(handle)
        except (OSError, ValueError):
            manifest = {}
    if not cached:
        os.makedirs(cache_root, exist_ok=True)
        if os.getenv("FAHIM_TTS_PROVIDER", "").lower() == "azure":
            try:
                _generate_azure_audio(normalized, voice, cache_path)
                cached = os.path.isfile(cache_path)
            except (OSError, urllib.error.URLError, RuntimeError):
                cached = False
        if not cached:
            try:
                _generate_google_tts(normalized, cache_path)
                cached = os.path.isfile(cache_path)
            except (OSError, urllib.error.URLError, RuntimeError):
                cached = False

        if cached:
            storage.upload_file(cache_path, remote_filename, content_type="audio/mpeg")
            manifest[cache_key] = {"voice": voice, "content_version": content_version}
            try:
                with open(manifest_path, "w", encoding="utf-8") as handle:
                    json.dump(manifest, handle, ensure_ascii=False, indent=2)
            except OSError:
                pass

    audio_url = storage.get_url(remote_filename) if cached else None

    return {
        "text": text,
        "normalized_text": normalized,
        "speed": speed,
        "lang": voice,
        "cache_key": cache_key,
        "content_version": content_version,
        "pronunciation_settings": pronunciation_settings,
        "status": "ready" if cached else "generation_required",
        "reuse_existing": cache_key in manifest or cached,
        "regenerate_only_if_source_changes": True,
        "audio_url": audio_url,
        "is_synthetic": True,
        "attribution": "Fahim Synthetic Speech Engine (نطق آلي تجريبي)",
        "can_use_browser_speech": True,
        "fallback_order": ["curriculum_cache", "server_tts", "browser_speech"]
    }


def _generate_google_tts(text: str, target_path: str) -> None:
    """Generate authentic Arabic MP3 audio through Google TTS with segment chunking."""
    import urllib.parse
    words = text.split()
    if not words:
        raise RuntimeError("No text provided for Google TTS generation")

    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > 120:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    combined_audio = bytearray()
    for chunk in chunks:
        q = urllib.parse.quote(chunk)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={q}&tl=ar&client=tw-ob"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://translate.google.com/",
            }
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            audio_bytes = response.read()
            if audio_bytes and len(audio_bytes) > 64:
                combined_audio.extend(audio_bytes)

    if not combined_audio or len(combined_audio) < 128:
        raise RuntimeError("Google TTS returned empty or invalid audio data")

    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
    temp_target = target_path + ".tmp"
    with open(temp_target, "wb") as handle:
        handle.write(combined_audio)
    os.replace(temp_target, target_path)


def _generate_azure_audio(text: str, voice: str, target_path: str) -> None:
    """Generate one normal-speed MP3 through Azure Speech when configured."""
    key = os.getenv("FAHIM_AZURE_SPEECH_KEY", "").strip()
    region = os.getenv("FAHIM_AZURE_SPEECH_REGION", "").strip()
    if not key or not region:
        raise RuntimeError("Azure Speech provider is not configured")
    voice_name = os.getenv("FAHIM_AZURE_SPEECH_VOICE", "ar-SA-HamedNeural")
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    body = f"<speak version='1.0' xml:lang='ar-SA'><voice name='{voice_name}'>{escaped}</voice></speak>".encode("utf-8")
    request = urllib.request.Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=body,
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": "Fahim-Audio-Generator/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        audio = response.read()
    if not audio or len(audio) < 128:
        raise RuntimeError("TTS provider returned an empty audio asset")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    temporary = target_path + ".tmp"
    with open(temporary, "wb") as handle:
        handle.write(audio)
    os.replace(temporary, target_path)


def _is_voice_approved(lang: str) -> bool:
    approved = {item.strip() for item in os.getenv("FAHIM_APPROVED_TTS_VOICES", "ar-SA,ar-AE").split(",") if item.strip()}
    return lang in approved


def _normalize_arabic(text: str) -> str:
    """Strip tashkeel, tatweel, and punctuation for phonetic alignment."""
    if not text:
        return ""
    # Strip tashkeel (fathah, dammah, kasrah, sukoon, shaddah, tanween)
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    # Strip tatweel (kashida)
    text = re.sub(r'\u0640', '', text)
    # Normalize punctuation and extra spaces
    text = re.sub(r'[،؛؟!.,:\"\'\(\)\[\]\-]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Compute standard Levenshtein edit distance."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def evaluate_pronunciation(req, db=None) -> dict:
    """
    Evaluates student spoken Arabic against target phrase using UAE MoE phonological rubric.
    Analyses key phoneme confusions:
      - ث / س (Tha / Seen)
      - ت / ط (Taa / Taa')
      - ذ / ز / ظ (Thal / Zay / Zhaa')
      - ة / ه (Taa Marbutah / Haa)
      - ص / س (Saad / Seen)
      - ض / د / ظ (Daad / Daal / Zhaa')
      - ق / ك / غ (Qaaf / Kaaf / Ghayn)
      - ح / ه (Haa / Haa')
    """
    target = req.target_phrase.strip()
    spoken = (req.spoken_text or "").strip()

    if not spoken:
        from backend.errors import ApplicationError
        if req.audio_base64:
            raise ApplicationError(
                status_code=422,
                detail="Automated speech-to-text transcription could not recognize Arabic speech from the audio payload. Please re-record or provide a spoken transcript."
            )
        raise ApplicationError(status_code=422, detail="No spoken speech or transcript was provided for evaluation")

    norm_target = _normalize_arabic(target)
    norm_spoken = _normalize_arabic(spoken)

    if not norm_target:
        from backend.errors import ApplicationError
        raise ApplicationError(status_code=422, detail="Target phrase cannot be empty")

    # 1. Base Levenshtein similarity
    max_len = max(len(norm_target), len(norm_spoken))
    dist = _levenshtein_distance(norm_target, norm_spoken)
    char_similarity = max(0.0, 1.0 - (dist / max(1, max_len)))

    # 2. Word-level overlap
    target_words = norm_target.split()
    spoken_words = norm_spoken.split()
    matched_words = sum(1 for w in target_words if w in spoken_words)
    word_accuracy = matched_words / max(1, len(target_words))

    # 3. Phoneme-specific confusion checks (UAE MoE priority distinctions)
    phoneme_pairs = [
        ("ث/س", "ث", ["س"]),
        ("ت/ط", "ط", ["ت"]),
        ("ذ/ز/ظ", "ذ", ["ز", "ظ"]),
        ("ة/ه", "ة", ["ه"]),
        ("ص/س", "ص", ["س"]),
        ("ض/د/ظ", "ض", ["د", "ظ"]),
        ("ق/ك", "ق", ["ك", "غ"]),
        ("ح/ه", "ح", ["ه"])
    ]

    phoneme_scores = {}
    detected_mistakes = []
    phoneme_penalty = 0.0

    for pair_label, target_char, confused_chars in phoneme_pairs:
        target_count = norm_target.count(target_char)
        if target_count > 0:
            confusion_occurred = 0
            for t_word, s_word in zip(target_words, spoken_words):
                if target_char in t_word:
                    for conf in confused_chars:
                        expected_sub = t_word.replace(target_char, conf)
                        if expected_sub == s_word:
                            confusion_occurred += 1
                            detected_mistakes.append(f"استبدال حرف ({target_char}) بحرف ({conf}) في كلمة: {t_word}")
                            break

            if confusion_occurred > 0:
                score = max(30.0, 100.0 - (confusion_occurred / target_count) * 60.0)
                phoneme_penalty += 8.0 * confusion_occurred
            else:
                score = 98.0
            phoneme_scores[pair_label] = round(score, 1)
        else:
            phoneme_scores[pair_label] = 95.0

    # 4. Overall score computation
    raw_score = (char_similarity * 0.5 + word_accuracy * 0.5) * 100.0 - phoneme_penalty
    overall_score = round(max(10.0, min(100.0, raw_score)), 1)
    accuracy_percentage = overall_score

    # 5. Fluency rating and feedback
    if overall_score >= 90.0:
        fluency_rating = "ممتاز (Excellent)"
        feedback_ar = "نطق متميز ومخارج حروف واضحة ودقيقة جداً! أحسنت يا بطل!"
        feedback_en = "Outstanding pronunciation with clear phoneme articulation and accurate cadence! Well done, champion!"
    elif overall_score >= 75.0:
        fluency_rating = "جيد جداً (Very Good)"
        feedback_ar = "قراءة جيدة جداً ونطق سليم لمعظم مخارج الحروف. استمر في التدرب!"
        feedback_en = "Very good reading and proper phoneme delivery. Keep practicing to reach excellence!"
    elif overall_score >= 60.0:
        fluency_rating = "مقبول (Satisfactory)"
        feedback_ar = "محاولة طيبة، يُرجى الانتباه لمخارج الحروف المتشابهة والتأني في النطق."
        feedback_en = "Good effort! Pay close attention to subtle phonological distinctions and articulate carefully."
    else:
        fluency_rating = "يحتاج إلى تدريب إضافي (Needs Practice)"
        feedback_ar = "حاول مرة أخرى بهدوء واستمع إلى التسجيل النموذجي قبل القراءة."
        feedback_en = "Please listen to the model teacher recording and try again with deliberate articulation."

    if detected_mistakes:
        feedback_ar += " ملحوظة: " + "، ".join(detected_mistakes[:2]) + "."

    # 6. Optional Gamification XP recording if db and child_id provided
    is_pass = overall_score >= 70.0
    if db and req.child_id and is_pass:
        try:
            from backend.models import GamificationProfile
            prof = db.query(GamificationProfile).filter(GamificationProfile.child_id == req.child_id).first()
            if prof:
                prof.total_xp += 15
                db.commit()
        except Exception:
            pass

    return {
        "overall_score": overall_score,
        "accuracy_percentage": accuracy_percentage,
        "fluency_rating": fluency_rating,
        "feedback_ar": feedback_ar,
        "feedback_en": feedback_en,
        "phoneme_scores": phoneme_scores,
        "detected_mistakes": detected_mistakes,
        "target_phrase": target,
        "recognized_text": spoken,
        "is_pass": is_pass
    }
