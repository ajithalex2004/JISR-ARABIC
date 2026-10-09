import os
import sys

def main():
    from backend.database import SessionLocal
    from backend.models import ScannedPage
    from backend.ocr_reader import GRADE_6_TEXTBOOK_PAGES_DATA

    db = SessionLocal()
    try:
        updated = 0
        for pdf_page, pdata in GRADE_6_TEXTBOOK_PAGES_DATA.items():
            sp = db.query(ScannedPage).filter(
                ScannedPage.book_edition_id == "moe_gr6_vol1_2023",
                ScannedPage.pdf_page == pdf_page
            ).first()

            paras_text = "\n\n".join(pdata["paragraphs"])
            if sp:
                sp.ocr_text_ar = paras_text
                sp.printed_page = pdata["printed_page"]
                sp.review_status = "reviewed"
                sp.confidence = 0.99
                updated += 1
            else:
                sp = ScannedPage(
                    book_edition_id="moe_gr6_vol1_2023",
                    pdf_page=pdf_page,
                    printed_page=pdata["printed_page"],
                    ocr_text_ar=paras_text,
                    review_status="reviewed",
                    confidence=0.99
                )
                db.add(sp)
                updated += 1
        db.commit()
        print(f"Successfully synced {updated} Grade 6 pages into ScannedPage table!")
    finally:
        db.close()

if __name__ == "__main__":
    main()
