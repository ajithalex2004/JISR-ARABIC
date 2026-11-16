#!/usr/bin/env python3
"""Add one class's approved chapter titles to approved_chapter_titles.json.

Copy the class's table from the "Chapter Titles for Approval" doc (after the teacher has corrected
and ticked it) into a text file, then run:

    python scripts/approved_titles_from_table.py --class 3 --approved-by "Ms Fatima" class3.md

The table's columns are: Term | Ch | App shows now | Textbook (Arabic) | Proposed English.
Rows whose titles still hold a "?" are skipped and listed, so a class can be applied in part;
summary rows such as "1–10" are skipped. The file is validated before it is written, and the
titles go live on the next deploy.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.modules.curriculum.approved_titles import DATA_FILE, validate  # noqa: E402


def parse_rows(text: str):
    """(term, chapter, arabic, english) for each data row of a markdown pipe table."""
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not cells[0].isdigit() or not cells[1].isdigit():
            continue  # header, separator, summary ("1–10") or non-table line
        yield int(cells[0]), int(cells[1]), cells[3], cells[4]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--class", dest="grade", type=int, required=True, help="class number, 1-12")
    ap.add_argument("--approved-by", default="", help="the teacher who approved the titles")
    ap.add_argument("--file", type=Path, default=DATA_FILE, help=argparse.SUPPRESS)
    ap.add_argument("table", type=Path, help="text file holding the class's table")
    args = ap.parse_args(argv)

    data = json.loads(args.file.read_text(encoding="utf-8")) if args.file.exists() else {"titles": {}}
    titles = data.setdefault("titles", {})
    added, skipped = [], []
    for term, chapter, arabic, english in parse_rows(args.table.read_text(encoding="utf-8")):
        key = f"{args.grade}-{term}-{chapter}"
        if "?" in arabic or "?" in english or arabic in ("", "—") or english in ("", "—"):
            skipped.append(key)
            continue
        entry = {"title_ar": arabic, "title_en": english}
        if args.approved_by:
            entry["approved_by"] = args.approved_by
        titles[key] = entry
        added.append(key)
    validate(data)  # raises on a bad entry; nothing is written then
    args.file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Class {args.grade}: {len(added)} title(s) added or updated" + (f"; skipped (still '?'): {', '.join(skipped)}" if skipped else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
