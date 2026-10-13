import os
import json
from sqlalchemy import create_engine, text

db_url = os.environ.get("DATABASE_URL", "postgresql+psycopg://jisr_user:jisr_secure_password_2026@postgres:5432/jisr_production")
engine = create_engine(db_url)

with engine.begin() as conn:
    rows = conn.execute(text("SELECT id, lesson_id, version_tag, content_json FROM lesson_versions")).fetchall()
    print(f"Total lesson_versions found: {len(rows)}")
    
    updated_count = 0
    for r in rows:
        row_id, lesson_id, version_tag, content_str = r
        if not content_str:
            continue
        try:
            data = json.loads(content_str) if isinstance(content_str, str) else content_str
        except Exception:
            continue
            
        old_pdf = data.get("pdf_start_page")
        start_page = data.get("start_page", 6)
        
        # Calculate correct pdf_start_page
        new_pdf = start_page + 2
        
        if old_pdf != new_pdf:
            data["pdf_start_page"] = new_pdf
            new_json_str = json.dumps(data, ensure_ascii=False)
            conn.execute(
                text("UPDATE lesson_versions SET content_json = :c WHERE id = :id"),
                {"c": new_json_str, "id": row_id}
            )
            print(f"Updated {lesson_id} (v {version_tag}): pdf_start_page {old_pdf} -> {new_pdf}")
            updated_count += 1
        else:
            print(f"Already aligned: {lesson_id} (v {version_tag}): pdf_start_page = {new_pdf}")
            
    print(f"Done! Updated {updated_count} rows.")
