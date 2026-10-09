"""
Bulk Curriculum Ingestion Utility for JISR / Fahim Arabic.
Allows uploading and seeding official UAE MoE curriculum packages for Grades 1 to 10 (Terms 1, 2, 3).

Usage Examples:
  # 1. Export starter template for Grade 3 Term 1:
  python -m backend.scripts.bulk_ingest_curriculum --export-template --grade 3 --term 1 --out ./templates/grade3_t1.json

  # 2. Dry-run validate a folder of lesson packages:
  python -m backend.scripts.bulk_ingest_curriculum --dir ./curriculum_files --dry-run

  # 3. Bulk ingest and activate a folder into PostgreSQL:
  python -m backend.scripts.bulk_ingest_curriculum --dir ./curriculum_files

  # 4. Ingest a single multi-lesson JSON file:
  python -m backend.scripts.bulk_ingest_curriculum --file ./curriculum_files/grade1_all_terms.json
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from typing import List, Dict, Any

from backend.database import SessionLocal
from backend.models import BookEdition, Unit, Lesson, LessonVersion
from backend.redis_client import invalidate_lesson_cache
from backend.modules.curriculum.syllabus_data import get_syllabus_for_grade_and_term, generate_dynamic_lesson_content


def validate_lesson_package(pkg: Dict[str, Any]) -> List[str]:
    """Validate that a lesson package conforms to the Fahim curriculum schema."""
    errors = []
    required_top = ["lesson_id", "title_ar", "title_en", "grade", "term"]
    for field in required_top:
        if field not in pkg:
            errors.append(f"Missing required field: '{field}'")

    if "grade" in pkg and not (1 <= int(pkg["grade"]) <= 12):
        errors.append(f"Invalid grade: {pkg.get('grade')} (must be 1-12)")

    if "term" in pkg and not (1 <= int(pkg["term"]) <= 3):
        errors.append(f"Invalid term: {pkg.get('term')} (must be 1-3)")

    return errors


def ingest_single_package(pkg: Dict[str, Any], db, dry_run: bool = False) -> Dict[str, Any]:
    """Ingests a single lesson package into the database."""
    validation_errors = validate_lesson_package(pkg)
    if validation_errors:
        return {
            "success": False,
            "lesson_id": pkg.get("lesson_id", "unknown"),
            "errors": validation_errors
        }

    lesson_id = pkg["lesson_id"]
    grade = int(pkg["grade"])
    term = int(pkg["term"])
    lesson_order = int(pkg.get("lesson_order") or pkg.get("order") or 1)
    title_ar = pkg["title_ar"]
    title_en = pkg["title_en"]
    start_page = int(pkg.get("start_page", 1))
    is_demo = bool(pkg.get("is_first_chapter_demo", lesson_order == 1 and term == 1))

    # Unit resolution
    unit_id = pkg.get("unit_id") or f"moe_g{grade}_t{term}_u{Math_ceil_unit(lesson_order)}"
    unit_title_ar = pkg.get("unit_title_ar", f"الوحدة {Math_ceil_unit(lesson_order)}")
    unit_title_en = pkg.get("unit_title_en", f"Unit {Math_ceil_unit(lesson_order)}")

    # Edition resolution
    edition_id = f"moe_gr{grade}_vol{term}_2023"
    edition_title = f"اللغة العربية - الصف {grade} - الجزء {term}"

    # Serialize content package
    content_str = json.dumps(pkg, ensure_ascii=False)
    content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    if dry_run:
        return {
            "success": True,
            "lesson_id": lesson_id,
            "action": "dry_run_validated",
            "content_hash": content_hash[:12]
        }

    # 1. Ensure BookEdition exists
    edition = db.query(BookEdition).filter(BookEdition.id == edition_id).first()
    if not edition:
        edition = BookEdition(
            id=edition_id,
            title=edition_title,
            series_name="العربية تجمعنا",
            volume=term,
            academic_year="2023-2024",
            total_pages=120
        )
        db.add(edition)
        db.flush()

    # 2. Ensure Unit exists
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        unit = Unit(
            id=unit_id,
            book_edition_id=edition_id,
            unit_number=Math_ceil_unit(lesson_order),
            title_ar=unit_title_ar,
            title_en=unit_title_en
        )
        db.add(unit)
        db.flush()

    # 3. Ensure Lesson entity exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        lesson = Lesson(
            id=lesson_id,
            unit_id=unit_id,
            grade=grade,
            term=term,
            lesson_order=lesson_order,
            title_ar=title_ar,
            title_en=title_en,
            start_page=start_page,
            is_first_chapter_demo=is_demo,
            status="published"
        )
        db.add(lesson)
        db.flush()
    else:
        lesson.title_ar = title_ar
        lesson.title_en = title_en
        lesson.start_page = start_page
        lesson.status = "published"

    # 4. Check or create LessonVersion
    version_tag = pkg.get("version", "1.0.0")
    existing_ver = db.query(LessonVersion).filter(
        LessonVersion.lesson_id == lesson_id,
        LessonVersion.content_hash == content_hash
    ).first()

    if existing_ver:
        existing_ver.is_active = True
        existing_ver.status = "published"
        action = "version_reused_active"
    else:
        # Deactivate old versions
        db.query(LessonVersion).filter(
            LessonVersion.lesson_id == lesson_id
        ).update({"is_active": False})

        new_ver_id = f"ver_{lesson_id}_{version_tag.replace('.', '_')}_{content_hash[:8]}"
        new_version = LessonVersion(
            id=new_ver_id,
            lesson_id=lesson_id,
            version_tag=version_tag,
            content_json=content_str,
            content_hash=content_hash,
            is_active=True,
            status="published"
        )
        db.add(new_version)
        action = "version_created"

    db.commit()
    invalidate_lesson_cache(lesson_id, grade=grade, term=term)

    return {
        "success": True,
        "lesson_id": lesson_id,
        "action": action,
        "content_hash": content_hash[:12]
    }


def Math_ceil_unit(order: int) -> int:
    """Helper to group lessons into units of ~5 lessons each."""
    return max(1, (order - 1) // 5 + 1)


def generate_scaffold_template(grade: int, term: int) -> List[Dict[str, Any]]:
    """Generates an editable JSON template for all chapters in a grade and term."""
    syllabus_items = get_syllabus_for_grade_and_term(grade, term)
    template_packages = []

    for item in syllabus_items:
        dummy_lesson = Lesson(
            id=item["id"],
            grade=grade,
            term=term,
            lesson_order=item["lesson_order"],
            title_ar=item["title_ar"],
            title_en=item["title_en"],
            unit_id=item["unit_id"],
            start_page=item["start_page"],
            is_first_chapter_demo=item.get("is_first_chapter_demo", False),
            status="published"
        )
        # Synthesize full 23-module pedagogical package
        content = generate_dynamic_lesson_content(dummy_lesson)
        template_packages.append(content)

    return template_packages


def main():
    parser = argparse.ArgumentParser(description="Bulk Ingestion & Curriculum Tool for Fahim Arabic")
    parser.add_argument("--dir", type=str, help="Path to directory containing lesson JSON files")
    parser.add_argument("--file", type=str, help="Path to single JSON file (single lesson or list of lessons)")
    parser.add_argument("--grade", type=int, help="Target grade (1-10)")
    parser.add_argument("--term", type=int, help="Target term (1-3)")
    parser.add_argument("--dry-run", action="store_true", help="Validate without committing to database")
    parser.add_argument("--export-template", action="store_true", help="Export starter JSON template for grade/term")
    parser.add_argument("--out", type=str, default="curriculum_template.json", help="Output path for exported template")
    parser.add_argument("--upload-pdf", type=str, help="Path to textbook PDF file to process and index")

    args = parser.parse_args()

    if args.upload_pdf:
        pdf_path = Path(args.upload_pdf)
        if not pdf_path.exists():
            print(f"[!] Error: PDF file '{pdf_path}' does not exist.")
            sys.exit(1)
        grade = args.grade
        term = args.term
        filename = pdf_path.name
        import re
        if grade is None:
            g_match = re.search(r'(?:grade|gr|g|class|cls)[\s_-]?(\d+)', filename, re.IGNORECASE)
            grade = int(g_match.group(1)) if g_match else 5
        if term is None:
            t_match = re.search(r'(?:term|vol|t)[\s_-]?(\d+)', filename, re.IGNORECASE)
            term = int(t_match.group(1)) if t_match else 1

        book_edition_id = f"moe_gr{grade}_vol{term}_2023"
        print(f"[*] Processing textbook PDF: {filename} for Grade {grade}, Term {term} ({book_edition_id})...")

        from backend.tasks.handlers import handle_process_textbook_ocr
        res = handle_process_textbook_ocr(
            {
                "pdf_path": str(pdf_path.resolve()),
                "book_edition_id": book_edition_id,
                "start_page": 1,
                "page_count": 0
            },
            lambda pct: print(f"    Progress: {pct}%") if pct % 25 == 0 or pct == 100 else None
        )
        print(f"[OK] Textbook indexed successfully: {res['pages_processed']} pages processed into '{book_edition_id}'.")
        return

    if args.export_template:
        target_grade = args.grade or 1
        target_term = args.term or 1
        print(f"[*] Generating official curriculum template for Grade {target_grade}, Term {target_term}...")
        templates = generate_scaffold_template(target_grade, target_term)
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        print(f"[OK] Successfully exported {len(templates)} lessons to: {out_path.resolve()}")
        return

    # Ingestion flow
    packages_to_ingest = []

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[!] Error: File '{file_path}' does not exist.")
            sys.exit(1)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                packages_to_ingest.extend(data)
            elif isinstance(data, dict):
                packages_to_ingest.append(data)

    elif args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists():
            print(f"[!] Error: Directory '{dir_path}' does not exist.")
            sys.exit(1)
        for json_file in dir_path.glob("**/*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        packages_to_ingest.extend(data)
                    elif isinstance(data, dict):
                        packages_to_ingest.append(data)
            except Exception as e:
                print(f"[!] Warning: Could not parse {json_file.name}: {e}")

    else:
        print("[!] Error: Please specify either --dir, --file, or --export-template.")
        parser.print_help()
        sys.exit(1)

    print(f"[*] Found {len(packages_to_ingest)} lesson package(s) to process.")
    if args.dry_run:
        print("[*] Running in DRY-RUN mode. No changes will be saved to PostgreSQL.")

    db = SessionLocal()
    success_count = 0
    failure_count = 0

    try:
        for idx, pkg in enumerate(packages_to_ingest, 1):
            lesson_id = pkg.get("lesson_id", f"item_{idx}")
            res = ingest_single_package(pkg, db, dry_run=args.dry_run)
            if res["success"]:
                success_count += 1
                print(f"  [{idx}/{len(packages_to_ingest)}] [OK] {lesson_id} -> {res.get('action')} (hash: {res.get('content_hash')})")
            else:
                failure_count += 1
                print(f"  [{idx}/{len(packages_to_ingest)}] [FAIL] {lesson_id} failed: {res.get('errors')}")

        print(f"\n[=== Ingestion Summary ===]")
        print(f"Total Processed: {len(packages_to_ingest)}")
        print(f"Successful:      {success_count}")
        print(f"Failed:          {failure_count}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
