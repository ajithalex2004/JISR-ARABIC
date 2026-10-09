import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
from backend.database import SessionLocal
from backend.models import ScannedPage
from sqlalchemy import func

db = SessionLocal()
editions = [
    'moe_gr1_vol1_2023', 'moe_gr1_vol2_2023', 'moe_gr1_vol3_2023',
    'moe_gr2_vol1_2023', 'moe_gr2_vol2_2023', 'moe_gr2_vol3_2023'
]

print("{:<22} | {:<6} | {:<16} | {:<6} | {:<6} | {:<8}".format("Edition", "Total", "Vision Verified", "Min Pg", "Max Pg", "Avg Len"))
print("-" * 75)

total_all = 0
verified_all = 0

for ed in editions:
    total = db.query(ScannedPage).filter(ScannedPage.book_edition_id == ed).count()
    verified = db.query(ScannedPage).filter(ScannedPage.book_edition_id == ed, ScannedPage.review_status == 'ocr_vision_verified').count()
    min_p = db.query(func.min(ScannedPage.pdf_page)).filter(ScannedPage.book_edition_id == ed).scalar()
    max_p = db.query(func.max(ScannedPage.pdf_page)).filter(ScannedPage.book_edition_id == ed).scalar()
    avg_l = db.query(func.avg(func.length(ScannedPage.ocr_text_ar))).filter(ScannedPage.book_edition_id == ed).scalar() or 0
    total_all += total
    verified_all += verified
    print("{:<22} | {:<6} | {:<16} | {:<6} | {:<6} | {:<8}".format(ed, total, verified, min_p, max_p, int(avg_l)))

print("-" * 75)
print(f"TOTAL: {total_all} pages, {verified_all} verified")
db.close()
