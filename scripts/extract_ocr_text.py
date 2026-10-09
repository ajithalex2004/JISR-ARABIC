import glob, json
from pathlib import Path

files = sorted(glob.glob(r"vision-output-new/**/*.json", recursive=True))
parts = []
page = 0
for filename in files:
    with open(filename, encoding="utf-8") as handle:
        for response in json.load(handle).get("responses", []):
            page += 1
            text = response.get("fullTextAnnotation", {}).get("text", "")
            parts.append(f"\n--- PAGE {page} ---\n{text}")
Path("curriculum-ocr-arabic.txt").write_text("".join(parts), encoding="utf-8")
print(f"Saved {page} pages")
