"""
Batch render high-resolution (2x scale) PNG page images for all UAE Ministry textbook PDFs.
Organizes output into dedicated subfolders: pdf_pages_sample/{edition_id}/page_{n}.png.
Supports multi-core parallel processing across CPUs.
"""
import os
import sys
import re
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse

sys.stdout.reconfigure(encoding="utf-8")


def render_single_book(pdf_path_str: str, edition_id: str, output_base_str: str, force: bool = False, scale: float = 2.0):
    """Worker function to render all pages of a single PDF textbook into its edition folder."""
    pdf_path = Path(pdf_path_str)
    output_base = Path(output_base_str)
    edition_dir = output_base / edition_id
    edition_dir.mkdir(parents=True, exist_ok=True)
    
    t0 = time.time()
    rendered_count = 0
    skipped_count = 0
    error_count = 0
    
    try:
        try:
            import pymupdf
            use_pymupdf = True
        except ImportError:
            import pypdfium2 as pdfium
            use_pymupdf = False
            
        if use_pymupdf:
            doc = pymupdf.open(str(pdf_path))
            total_pages = len(doc)
            dpi = int(72 * scale)
            
            for idx in range(total_pages):
                page_num = idx + 1
                dest_file = edition_dir / f"page_{page_num}.png"
                
                legacy_file = None
                if edition_id == "moe_gr5_vol1_2023":
                    legacy_file = output_base / f"page_{page_num}.png"
                    
                if not force and dest_file.exists() and dest_file.stat().st_size > 1024:
                    if legacy_file and not legacy_file.exists():
                        import shutil
                        shutil.copy2(dest_file, legacy_file)
                    skipped_count += 1
                    continue
                    
                try:
                    page = doc[idx]
                    pix = page.get_pixmap(dpi=dpi)
                    pix.save(str(dest_file))
                    if legacy_file and not legacy_file.exists():
                        import shutil
                        shutil.copy2(dest_file, legacy_file)
                    rendered_count += 1
                except Exception:
                    error_count += 1
            doc.close()
        else:
            doc = pdfium.PdfDocument(str(pdf_path))
            total_pages = len(doc)
            
            for idx in range(total_pages):
                page_num = idx + 1
                dest_file = edition_dir / f"page_{page_num}.png"
                
                legacy_file = None
                if edition_id == "moe_gr5_vol1_2023":
                    legacy_file = output_base / f"page_{page_num}.png"
                    
                if not force and dest_file.exists() and dest_file.stat().st_size > 1024:
                    if legacy_file and not legacy_file.exists():
                        import shutil
                        shutil.copy2(dest_file, legacy_file)
                    skipped_count += 1
                    continue
                    
                try:
                    page = doc.get_page(idx)
                    bmp = page.render(scale=scale)
                    img = bmp.to_pil()
                    img.save(str(dest_file), format="PNG")
                    if legacy_file and not legacy_file.exists():
                        img.save(str(legacy_file), format="PNG")
                    rendered_count += 1
                except Exception:
                    error_count += 1
            doc.close()
            
        elapsed = time.time() - t0
        return {
            "edition_id": edition_id,
            "filename": pdf_path.name,
            "total_pages": total_pages,
            "rendered": rendered_count,
            "skipped": skipped_count,
            "errors": error_count,
            "elapsed_seconds": elapsed,
            "dest_dir": str(edition_dir)
        }
    except Exception as e:
        return {
            "edition_id": edition_id,
            "filename": pdf_path.name,
            "error": str(e),
            "rendered": 0,
            "total_pages": 0,
            "elapsed_seconds": time.time() - t0
        }


def find_pdf_textbooks(upload_dir: Path):
    """Identify all textbook PDFs and map them to their standard edition_id."""
    books = []
    
    # 1. Search tmp/admin_curriculum_uploads
    if upload_dir.exists():
        for p in sorted(upload_dir.glob("*.pdf")):
            fname = p.name
            m = re.search(r"Grade[_\s]?(\d+)[_\s]?(?:Vol|Term)[_\s]?(\d+)", fname, re.IGNORECASE)
            if m:
                grade = int(m.group(1))
                term = int(m.group(2))
                edition_id = f"moe_gr{grade}_vol{term}_2023"
                books.append((str(p.resolve()), edition_id, grade, term))
                
    # 2. Check root Grade 5 Vol 1 sample if present
    root_sample = Path("1693219092.pdf")
    has_g5v1 = any(b[1] == "moe_gr5_vol1_2023" for b in books)
    if not has_g5v1 and root_sample.exists():
        books.append((str(root_sample.resolve()), "moe_gr5_vol1_2023", 5, 1))
        
    return sorted(books, key=lambda x: (x[2], x[3]))


def main():
    parser = argparse.ArgumentParser(description="Render high-res 2x page images for textbook PDFs")
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 4, help="Number of parallel worker processes")
    parser.add_argument("--grade", type=int, default=None, help="Optional: render only specific grade")
    parser.add_argument("--term", type=int, default=None, help="Optional: render only specific term")
    parser.add_argument("--scale", type=float, default=2.0, help="Render scale (default 2.0 for high-res crisp text)")
    parser.add_argument("--force", action="store_true", help="Force re-rendering even if PNG already exists")
    parser.add_argument("--dry-run", action="store_true", help="Show files that would be rendered without executing")
    args = parser.parse_args()

    upload_dir = Path("tmp/admin_curriculum_uploads")
    output_base = Path("pdf_pages_sample")
    output_base.mkdir(parents=True, exist_ok=True)

    all_books = find_pdf_textbooks(upload_dir)

    # Filter if requested
    if args.grade is not None:
        all_books = [b for b in all_books if b[2] == args.grade]
    if args.term is not None:
        all_books = [b for b in all_books if b[3] == args.term]

    print("=" * 80)
    print("🎨 BATCH HIGH-RES 2X TEXTBOOK PAGE IMAGE RENDERER")
    print(f"Output Base Directory : {output_base.resolve()}")
    print(f"Parallel Worker Cores : {args.workers}")
    print(f"Resolution Scale      : {args.scale}x DPI")
    print(f"Target Textbooks      : {len(all_books)} books")
    print("=" * 80)

    if args.dry_run:
        print("[DRY-RUN] Found textbooks to process:")
        for path_str, ed_id, g, t in all_books:
            print(f" - Grade {g:2d} Term {t} -> {ed_id} | Path: {path_str}")
        return

    start_total = time.time()
    results = []

    # Use ProcessPoolExecutor to distribute PDFs across available CPU cores
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        future_to_book = {
            executor.submit(
                render_single_book, 
                path_str, 
                ed_id, 
                str(output_base.resolve()), 
                force=args.force, 
                scale=args.scale
            ): (ed_id, g, t, path_str)
            for path_str, ed_id, g, t in all_books
        }

        completed_count = 0
        total_books = len(future_to_book)

        for future in as_completed(future_to_book):
            completed_count += 1
            meta = future_to_book[future]
            ed_id, g, t, path_str = meta
            try:
                res = future.result()
                results.append(res)
                if "error" in res:
                    print(f"[{completed_count:02d}/{total_books:02d}] ❌ {ed_id} (Grade {g} Term {t}): Error - {res['error']}")
                else:
                    status_str = f"Rendered: {res['rendered']} | Skipped: {res['skipped']}"
                    if res['errors'] > 0:
                        status_str += f" | Errors: {res['errors']}"
                    print(f"[{completed_count:02d}/{total_books:02d}] ✓ {ed_id:<18} (Grade {g:2d} Term {t}): {res['total_pages']:3d} pages in {res['elapsed_seconds']:.1f}s ({status_str})")
            except Exception as exc:
                print(f"[{completed_count:02d}/{total_books:02d}] ❌ {ed_id}: Exception: {exc}")

    total_time = time.time() - start_total
    total_rendered = sum(r.get("rendered", 0) for r in results)
    total_skipped = sum(r.get("skipped", 0) for r in results)
    total_pages = sum(r.get("total_pages", 0) for r in results)

    # Calculate disk usage
    total_bytes = 0
    for p in output_base.rglob("*.png"):
        total_bytes += p.stat().st_size
    total_mb = total_bytes / (1024 * 1024)

    print("\n" + "=" * 80)
    print("✨ BATCH RENDERING COMPLETE")
    print(f"Total Textbooks Processed : {len(results)} books")
    print(f"Total Pages Checked       : {total_pages} pages")
    print(f"Pages Newly Rendered      : {total_rendered} PNGs")
    print(f"Pages Skipped (Existed)   : {total_skipped} PNGs")
    print(f"Total PNG Images on Disk  : {len(list(output_base.rglob('*.png')))} images")
    print(f"Total Image Storage       : {total_mb:.2f} MB")
    print(f"Total Wallclock Time      : {total_time:.1f} seconds (avg {total_time/max(1, len(results)):.1f}s / book)")
    print("=" * 80)


if __name__ == "__main__":
    main()
