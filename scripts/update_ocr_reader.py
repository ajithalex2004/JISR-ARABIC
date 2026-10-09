import os

def main():
    with open('backend/ocr_reader.py', 'r', encoding='utf-8') as f:
        orig = f.read()

    with open('scratch/gr6_dict_code.py', 'r', encoding='utf-8') as f:
        gr6_code = f.read()

    target = 'def get_textbook_coverage_report() -> Dict[str, Any]:'
    assert target in orig, 'target not found'

    new_get_page_ocr_data = '''def get_page_ocr_data(pdf_page: int, edition_id: str | None = None) -> Dict[str, Any]:
    """Returns OCR text, translation, confidence, and page metadata for a specific PDF page."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    is_gr6 = bool(edition_id and ('gr6' in edition_id.lower() or 'grade6' in edition_id.lower()))
    
    if is_gr6 and pdf_page in GRADE_6_TEXTBOOK_PAGES_DATA:
        data = GRADE_6_TEXTBOOK_PAGES_DATA[pdf_page]
        has_image = (
            (edition_id and os.path.exists(os.path.join(base_dir, 'pdf_pages_sample', edition_id, f'page_{pdf_page}.png'))) or
            os.path.exists(os.path.join(base_dir, 'pdf_pages_sample', 'moe_gr6_vol1_2023', f'page_{pdf_page}.png')) or
            os.path.exists(os.path.join(base_dir, 'pdf_pages_sample', f'page_{pdf_page}.png'))
        )
        return {
            "pdf_page": pdf_page,
            "printed_page": data["printed_page"],
            "unit": data["unit"],
            "lesson": data["lesson"],
            "title_ar": data["title_ar"],
            "title_en": data.get("title_en", ""),
            "paragraphs": data["paragraphs"],
            "paragraphs_en": data.get("paragraphs_en", []),
            "confidence": data["confidence"],
            "review_status": data["review_status"],
            "has_image": has_image,
            "is_available": True
        }

    if pdf_page in TEXTBOOK_PAGES_DATA and not is_gr6:
        data = TEXTBOOK_PAGES_DATA[pdf_page]
        has_image = (
            (edition_id and os.path.exists(os.path.join(base_dir, 'pdf_pages_sample', edition_id, f'page_{pdf_page}.png'))) or
            os.path.exists(os.path.join(base_dir, 'pdf_pages_sample', 'moe_gr5_vol1_2023', f'page_{pdf_page}.png')) or
            os.path.exists(os.path.join(base_dir, 'pdf_pages_sample', f'page_{pdf_page}.png'))
        )
        return {
            "pdf_page": pdf_page,
            "printed_page": data["printed_page"],
            "unit": data["unit"],
            "lesson": data["lesson"],
            "title_ar": data["title_ar"],
            "title_en": data.get("title_en", ""),
            "paragraphs": data["paragraphs"],
            "paragraphs_en": data.get("paragraphs_en", []),
            "confidence": data["confidence"],
            "review_status": data["review_status"],
            "has_image": has_image,
            "is_available": True
        }
    else:
        # Fallback for pages awaiting full review
        has_image = (
            (edition_id and os.path.exists(os.path.join(base_dir, 'pdf_pages_sample', edition_id, f'page_{pdf_page}.png'))) or
            os.path.exists(os.path.join(base_dir, 'pdf_pages_sample', f'page_{pdf_page}.png'))
        )
        return {
            "pdf_page": pdf_page,
            "printed_page": max(1, pdf_page - 2),
            "unit": "قيد المراجعة الفنية (Under Review)",
            "lesson": "نص المجلد الأول (Volume 1 Text)",
            "title_ar": f"صفحة {pdf_page} - قيد المراجعة",
            "title_en": f"Page {pdf_page} - Under Editorial Review",
            "paragraphs": [
                f"الصفحة رقم {pdf_page} من كتاب (العربية تجمعنا). الصورة الأصلية محفوظة، والنص العربي قيد المراجعة والتدقيق والتشكيل الكامل من المعلم."
            ],
            "paragraphs_en": [
                f"Page {pdf_page} from 'Arabic Brings Us Together'. Scanned image preserved; full transcription, vowels, and English translations are under editorial review."
            ],
            "confidence": 0.85,
            "review_status": "automatic_unverified",
            "has_image": has_image,
            "is_available": True
        }
'''

    part1 = orig[:orig.find(target)]
    part2_old_func = orig[orig.find(target):orig.find('def get_page_ocr_data')]
    new_content = part1 + gr6_code + '\n\n' + part2_old_func + new_get_page_ocr_data + '\n'

    with open('backend/ocr_reader.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print('Updated backend/ocr_reader.py successfully!')

if __name__ == '__main__':
    main()
