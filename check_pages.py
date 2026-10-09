import pymupdf
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = pymupdf.open('tmp/admin_curriculum_uploads/Grade7_Vol1.pdf')
for p in range(6, 12):
    page = doc[p]
    text = page.get_text()
    print(f"=== PDF Page {p+1} ===")
    print(text)
    print("-" * 30)
