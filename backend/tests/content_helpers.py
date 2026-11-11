"""Test helper: give lessons a real published version, so they open for learners.

Lessons without one (or whose published version is the placeholder template) are
"Coming soon" for learners and don't open (backend/modules/curriculum/coming_soon.py).
"""
import hashlib
import json

from backend.models import LessonVersion


def publish_real_content(db, *lesson_ids):
    for lesson_id in lesson_ids:
        content = json.dumps({"title_ar": "درس", "vocabulary_cards": [{"word_ar": "كُرَةٌ"}]}, ensure_ascii=False)
        db.add(LessonVersion(id=f"ver_real_{lesson_id}", lesson_id=lesson_id, content_json=content,
                             content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
                             is_active=True, status="published"))
    db.commit()
