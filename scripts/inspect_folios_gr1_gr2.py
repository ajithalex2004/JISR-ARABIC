import sys, os
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8')
from google.cloud import vision

client = vision.ImageAnnotatorClient()
editions = [
    'moe_gr1_vol1_2023', 'moe_gr1_vol2_2023', 'moe_gr1_vol3_2023',
    'moe_gr2_vol1_2023', 'moe_gr2_vol2_2023', 'moe_gr2_vol3_2023'
]

def check_page(args):
    ed, p = args
    img_path = f'pdf_pages_sample/{ed}/page_{p}.png'
    if not os.path.exists(img_path):
        return ed, p, "missing", ""
    with open(img_path, 'rb') as f:
        content = f.read()
    res = client.text_detection(image=vision.Image(content=content))
    txt = res.text_annotations[0].description if res.text_annotations else ''
    lines = [l.strip() for l in txt.strip().split('\n') if l.strip()]
    first = lines[0] if lines else ''
    last_3 = lines[-3:] if len(lines) >= 3 else lines
    digits = [x for x in last_3 if x.isdigit() or (len(x) <= 3 and any(c.isdigit() for c in x))]
    last_l = lines[-1] if lines else ''
    return ed, p, f"first=[{first[:30]}] | digits_end={digits} | last=[{last_l[:30]}]"

tasks = []
for ed in editions:
    for p in [5, 6, 7, 8, 9, 10, 11, 12, 15, 20]:
        tasks.append((ed, p))

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(check_page, tasks))

# Group by edition
for ed in editions:
    print('====================================')
    print('EDITION:', ed)
    print('====================================')
    ed_res = sorted([r for r in results if r[0] == ed], key=lambda x: x[1])
    for _, p, info in ed_res:
        print(f"pdf {p:2d}: {info}")
