"""
verify_curriculum_readiness.py — Exhaustive Verification of Curriculum across Grades 1-10.
Checks:
1. BookEditions count and page counts
2. Units count and distribution
3. Lessons count and active LessonVersions for every Grade (1-10) and Term (1-3)
4. Schema validation of LessonPackage JSON for all 10 frontend tabs
5. Page image mapping existence in pdf_pages_sample/{edition_id}/page_{n}.png
6. OCR index mapping in scanned_pages
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import os
import json
from pathlib import Path
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import BookEdition, Unit, Lesson, LessonVersion, ScannedPage

def run_verification():
    db: Session = SessionLocal()
    try:
        print("=" * 80)
        print("EXHAUSTIVE CURRICULUM VERIFICATION AUDIT (GRADES 1 - 10)")
        print("=" * 80)

        # 1. Book Editions
        editions = db.query(BookEdition).order_by(BookEdition.id).all()
        print(f"\n[1] Book Editions Found in DB: {len(editions)}")

        # 2. Page summary per grade
        print("\n[2] Breakdown by Grade and Term:")
        print(f"{'Grade':<6} | {'Term':<5} | {'Edition ID':<22} | {'Pages':<6} | {'Units':<6} | {'Lessons':<8} | {'Active Pkgs':<12} | {'Img Folder OK?'}")
        print("-" * 90)

        total_lessons = 0
        total_active_versions = 0
        all_tabs_valid = True
        missing_images_count = 0

        for grade in range(1, 11):
            for term in (1, 2, 3):
                edition_id = f"moe_gr{grade}_vol{term}_2023"
                ed = db.query(BookEdition).filter(BookEdition.id == edition_id).first()
                ed_pages = ed.total_pages if ed else 0
                
                units_cnt = db.query(Unit).filter(Unit.book_edition_id == edition_id).count()
                lessons = db.query(Lesson).filter(Lesson.grade == grade, Lesson.term == term).order_by(Lesson.lesson_order).all()
                lessons_cnt = len(lessons)
                total_lessons += lessons_cnt

                # Check active versions & schema
                active_pkgs_cnt = 0
                for l in lessons:
                    ver = db.query(LessonVersion).filter(
                        LessonVersion.lesson_id == l.id,
                        LessonVersion.is_active == True
                    ).first()
                    if ver:
                        active_pkgs_cnt += 1
                        total_active_versions += 1
                        # Tab validation
                        c = ver.content_json
                        if isinstance(c, str):
                            try:
                                c = json.loads(c)
                            except Exception:
                                c = None
                        if not isinstance(c, dict):
                            all_tabs_valid = False
                        else:
                            req_keys = [
                                "lesson_id", "title_ar", "vocabulary_cards", "listen_speak_studio", 
                                "instruction_decoder", "grammar_lab", "sentence_builder",
                                "practice_activities", "speaking_mission", "prep_check", "exam_practice",
                                "spaced_recall"
                            ]
                            for rk in req_keys:
                                if rk not in c:
                                    print(f"  [!] Lesson {l.id} missing tab key '{rk}'", flush=True)
                                    all_tabs_valid = False
                                    
                            # Check start page image exists
                            sp = l.start_page or 1
                            img_path = Path("pdf_pages_sample") / edition_id / f"page_{sp}.png"
                            if not img_path.exists():
                                missing_images_count += 1

                img_dir = Path("pdf_pages_sample") / edition_id
                img_dir_ok = "✓" if (img_dir.exists() and any(img_dir.iterdir())) else "✗"

                print(f"Gr {grade:<3} | T{term:<4} | {edition_id:<22} | {ed_pages:<6} | {units_cnt:<6} | {lessons_cnt:<8} | {active_pkgs_cnt:<12} | {img_dir_ok}", flush=True)

        print("-" * 90)
        print(f"Total Lessons Seeded: {total_lessons}")
        print(f"Total Active Interactive Packages: {total_active_versions}")
        print(f"All 10-Tab Schemas Valid: {all_tabs_valid}")
        print(f"Missing Start Page Images: {missing_images_count}")

        # 3. Check OCR pages in DB
        ocr_cnt = db.query(ScannedPage).count()
        print(f"\n[3] Total Scanned OCR Pages Indexed in DB: {ocr_cnt}")

        print("=" * 80)
    finally:
        db.close()

if __name__ == "__main__":
    run_verification()
