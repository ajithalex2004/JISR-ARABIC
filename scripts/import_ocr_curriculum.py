"""Import OCR page text and a reviewed unit/lesson outline for Grade 5 Terms 2–3."""
import glob, json, hashlib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.database import SessionLocal
from backend.models import BookEdition, Unit, Lesson, ScannedPage

TERMS = {
    2: {
        "edition": ("moe_gr5_vol2_2021", "العربية تجمعنا - المستوى الخامس - المجلد الثاني", 2, 72),
        "units": [(3, "مُدُن عالمية", "Global Cities", [("مدن عربية", "Arab Cities"), ("لندن", "London"), ("شنغهاي", "Shanghai")]),
                  (4, "غرائب وعجائب", "Wonders and Marvels", [("عجائب الدنيا السبع", "Seven Wonders of the World"), ("الكهوف والجزر", "Caves and Islands"), ("عجائب الكائنات الحية", "Wonders of Living Creatures")])]
    },
    3: {
        "edition": ("moe_gr5_vol3_2021", "العربية تجمعنا - المستوى الخامس - المجلد الثالث", 3, 46),
        "units": [(5, "التواصل", "Communication", [("الحمام الزاجل", "Carrier Pigeon"), ("الإعلام", "Media"), ("وسائل التواصل", "Communication Tools")]),
                  (6, "كلنا أذكياء", "We Are All Intelligent", [("الحيوان والذكاء", "Animals and Intelligence"), ("الإنسان والذكاء", "Human Intelligence"), ("مدن ذكية", "Smart Cities")])]
    }
}

def load_pages(term):
    files = sorted(glob.glob(fr"vision-output-new\**\term-{term}\*.json", recursive=True))
    pages = []
    for filename in files:
        with open(filename, encoding="utf-8") as handle:
            pages.extend(r.get("fullTextAnnotation", {}).get("text", "") for r in json.load(handle).get("responses", []))
    return pages

def main():
    db = SessionLocal()
    try:
        for term, spec in TERMS.items():
            edition_id, title, volume, total = spec["edition"]
            edition = db.get(BookEdition, edition_id) or BookEdition(id=edition_id, title=title, volume=volume, academic_year="2021–2022", publication_year="2021–2022", pdf_filename=f"term-{term}.pdf", total_pages=total)
            db.add(edition)
            for number, ar, en, lessons in spec["units"]:
                unit_id = f"unit_{number:02d}_term_{term}"
                unit = db.get(Unit, unit_id) or Unit(id=unit_id, book_edition_id=edition_id, unit_number=number, title_ar=ar, title_en=en)
                db.add(unit)
                db.flush()
                for order, (lesson_ar, lesson_en) in enumerate(lessons, 1):
                    lesson_id = f"lesson_t{term}_{number:02d}_{order:02d}"
                    if not db.get(Lesson, lesson_id):
                        db.add(Lesson(id=lesson_id, unit_id=unit_id, grade=5, term=term, lesson_order=order, title_ar=lesson_ar, title_en=lesson_en, start_page=(number-3)*30 + (order-1)*10 + 8, status="content_pending"))
            for pdf_page, text in enumerate(load_pages(term), 1):
                page_id = (term * 1000) + pdf_page
                if not db.query(ScannedPage).filter(ScannedPage.id == page_id).first():
                    db.add(ScannedPage(id=page_id, book_edition_id=edition_id, pdf_page=pdf_page, printed_page=pdf_page, ocr_text_ar=text, confidence=0.95, review_status="automatic_unverified"))
        db.commit()
        print("Imported OCR pages, editions, units, and lesson outline for Terms 2 and 3.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
