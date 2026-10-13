"""Upload textbook page images and OCR output from this PC to a hosted JISR API.

Packs pdf_pages_sample/ and vision-output-new/ into ~200 MB .tar.gz parts and sends
each to POST /api/admin/content-archive (admin account required). Finished parts are
recorded in .content-upload-progress.json, so re-running resumes after a failure.

Usage (from the project folder):
    python scripts/upload_content.py --api https://<api-host>
"""
import argparse
import getpass
import io
import json
import sys
import tarfile
from pathlib import Path

import requests

ROOTS = ("pdf_pages_sample", "vision-output-new")
PART_BYTES = 200 * 1024 * 1024
PROGRESS_FILE = Path(".content-upload-progress.json")
ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".json", ".txt"}


def login(api: str) -> str:
    email = input("Admin email: ").strip()
    password = getpass.getpass("Admin password: ")
    res = requests.post(f"{api}/api/auth/login", json={"email": email, "password": password}, timeout=30)
    if res.status_code != 200:
        sys.exit(f"Login failed ({res.status_code}): {res.text[:200]}")
    if res.json().get("user", {}).get("role") != "admin":
        sys.exit("This account is not an admin.")
    return res.json()["access_token"]


def plan_parts(root: Path):
    """Group files into parts of at most PART_BYTES, keeping paths relative to root."""
    part, size = [], 0
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in ALLOWED_SUFFIXES):
        file_size = path.stat().st_size
        if part and size + file_size > PART_BYTES:
            yield part
            part, size = [], 0
        part.append(path)
        size += file_size
    if part:
        yield part


def build_archive(root: Path, files) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz", compresslevel=3) as archive:
        for path in files:
            archive.add(path, arcname=path.relative_to(root).as_posix())
    return buffer.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--api", required=True, help="API base URL, e.g. https://jisr-api.up.railway.app")
    args = parser.parse_args()
    api = args.api.rstrip("/")
    if not api.startswith("https://"):
        sys.exit("--api must be an https:// address")

    done = set(json.loads(PROGRESS_FILE.read_text())) if PROGRESS_FILE.exists() else set()
    token = login(api)

    for root_name in ROOTS:
        root = Path(root_name)
        if not root.is_dir():
            print(f"Skipping {root_name}: folder not found")
            continue
        parts = list(plan_parts(root))
        for index, files in enumerate(parts, start=1):
            key = f"{root_name}:{index}:{len(files)}:{files[0].as_posix()}"
            if key in done:
                print(f"{root_name} part {index}/{len(parts)} already uploaded")
                continue
            data = build_archive(root, files)
            print(f"{root_name} part {index}/{len(parts)}: {len(files)} files, {len(data) // (1024 * 1024)} MB ...", flush=True)
            res = requests.post(
                f"{api}/api/admin/content-archive",
                params={"root": root_name},
                headers={"Authorization": f"Bearer {token}"},
                files={"file": (f"{root_name}-{index}.tar.gz", data, "application/gzip")},
                timeout=900,
            )
            if res.status_code != 200:
                sys.exit(f"Upload failed ({res.status_code}): {res.text[:300]}\nRe-run the script to resume.")
            print(f"   installed {res.json()['files_installed']} files, {res.json()['volume_free_mb']} MB free on volume")
            done.add(key)
            PROGRESS_FILE.write_text(json.dumps(sorted(done)))

    print("All content uploaded.")


if __name__ == "__main__":
    main()
