import sys, os
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import vision

client = vision.ImageAnnotatorClient()
check_editions = {
    'moe_gr1_vol1_2023': [6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 22, 30],
    'moe_gr1_vol3_2023': [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 25],
    'moe_gr2_vol2_2023': [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 25, 30],
    'moe_gr2_vol3_2023': [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 25, 30]
}

def check_one(args):
    ed, p = args
    img_path = f'pdf_pages_sample/{ed}/page_{p}.png'
    if not os.path.exists(img_path):
        return ed, p, "missing"
    with open(img_path, 'rb') as f:
        content = f.read()
    res = client.text_detection(image=vision.Image(content=content))
    txt = res.text_annotations[0].description if res.text_annotations else ''
    lines = [l.strip() for l in txt.strip().split('\n') if l.strip()]
    first = lines[0] if lines else ''
    # Find all small numbers that could be page folios
    all_nums = [l for l in lines if l.isdigit() and int(l) < 150]
    last_3 = lines[-3:] if len(lines) >= 3 else lines
    return ed, p, f"first=[{first[:25]}] | all_nums={all_nums} | last_3={last_3}"

tasks = []
for ed, pages in check_editions.items():
    for p in pages:
        tasks.append((ed, p))

with ThreadPoolExecutor(max_workers=12) as executor:
    results = list(executor.map(check_one, tasks))

for ed in check_editions:
    print('====================================')
    print('EDITION:', ed)
    print('====================================')
    ed_res = sorted([r for r in results if r[0] == ed], key=lambda x: x[1])
    for _, p, info in ed_res:
        print(f"pdf {p:2d}: {info}")
