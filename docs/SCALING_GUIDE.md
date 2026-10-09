# Fahim (فهيم) Curriculum Scaling & Operations Guide

## 1. Overview & Architectural Principles
The Fahim platform is designed for scalable, multi-grade, multi-term deployment across UAE private and public schools following the Ministry of Education (MoE) / CBSE Arabic (Non-Arabs) framework.

### Core Non-Negotiable Rules
1. **Free Demo Guarantee**: Chapter 1 of every Class (Grade) is permanently available as a Free Demo. All other chapters and terms require payment verification ($50 / 185 AED per term) or unlocked `TermAccess` credentials.
2. **Deterministic Grading**: Client devices never submit self-calculated scores. All attempts must be graded server-side against pinned answer keys using the Arabic Normalizer (`scoring.py`).
3. **Synthetic Speech Tagging**: All browser/device audio synthesis must be explicitly marked: `Synthetic Pronunciation (نطق آلي اصطناعي)`.
4. **Zero Border Radius & Educational Dignity**: Visual interfaces must maintain crisp rectangular styling (`border-radius: 0px`), with UAE emerald (`#064e3b`), desert amber (`#d97706`), dark slate (`#0f172a`), and sand panels. No generic AI floating gradients or blue buttons.

---

## 2. Operational Workflows

### 2.1 Workflow: `ADD_CLASS`
Use this workflow to onboard a new Grade level (Classes 1 through 12).

1. **Database Registry**:
   Insert a new entry in `book_editions`:
   ```sql
   INSERT INTO book_editions (id, title, grade, curriculum_year, total_pages, publisher)
   VALUES ('edition_grade_06_2023_v1', 'Student Book - Grade 6 / Level 6 - Part 1', 6, 2023, 112, 'UAE Ministry of Education');
   ```

2. **Term Structure**:
   Register Term 1, 2, and 3 with the default $50.00 term unlock fee:
   ```json
   {
     "grade": 6,
     "term": 1,
     "price_usd": 50.00,
     "currency": "USD"
   }
   ```

3. **Demo Rule Enforcement**:
   - Create Unit 1, Lesson 1 with `is_demo: true`.
   - Create all subsequent lessons with `is_demo: false`.

---

### 2.2 Workflow: `ADD_TERM`
Use this workflow to register subsequent academic terms (Term 2 or Term 3) for an existing grade.

1. **API Endpoint**:
   `POST /api/v1/admin/terms`
   Headers: `Authorization: Bearer <ADMIN_JWT>`
   Payload:
   ```json
   {
     "edition_id": "edition_grade_05_2023_v1",
     "grade": 5,
     "term_number": 2,
     "title_ar": "الفصل الدراسي الثاني",
     "title_en": "Term 2: Sports & Cultural Life",
     "price_usd": 50.00,
     "is_demo_eligible": false,
     "units_count": 2,
     "lessons_count": 8
   }
   ```

2. **Paywall Verification**:
   Ensure `term_access` verification route checks:
   ```python
   def check_access(user_id: str, child_id: str, grade: int, term: int):
       if lesson.is_demo:
           return True
       access = db.query(TermAccess).filter_by(child_id=child_id, grade=grade, term=term, status="active").first()
       return access is not None
   ```

---

### 2.3 Workflow: `ADD_LESSON`
Every lesson must adhere to the 12-Feature Pedagogical Model.

1. **Authoring JSON Schema Requirements**:
   Each lesson version must provide structured data for:
   - `prep_check`: 3 vocabulary diagnostic questions.
   - `three_paths`:
     - Level A (Foundation): Slow speech, full transliteration, root-letter breakdown.
     - Level B (Core Grade): Standard sentence builder, grammar cues.
     - Level C (Enrichment): UAE real-world contextual dialogue.
   - `instruction_decoder`: Classroom imperative phrases with audio triggers.
   - `grammar_word_forms`: Root patterns, singular/plural, masculine/feminine.
   - `sentence_builder`: Token sequence puzzles with deterministic slot validation.
   - `listen_speak_studio`: Target phrases with pronunciation sandbox.
   - `mistake_notebook`: Common L1 transfer traps (e.g. Malayalam/Hindi/English learners confusing ح and ه, or ع and أ).
   - `uae_speaking_mission`: Authentic UAE scenario (e.g. Abu Dhabi Sports Club, school playground).
   - `parent_companion_card`: Non-Arabic speaking parent guide with phonetic hints.
   - `tutor_handover_card`: Specific rubric and teacher observation notes.
   - `exam_practice`: MoE-aligned assessment items.
   - `spaced_recall`: Leitner schedule intervals (Day 1, Day 3, Day 7).

2. **API Endpoint**:
   `POST /api/v1/admin/lessons`
   Payload:
   ```json
   {
     "unit_id": "unit_01_sports",
     "lesson_number": 2,
     "title_ar": "ركوب الخيل",
     "title_en": "Horse Riding",
     "page_start": 16,
     "page_end": 23,
     "is_demo": false,
     "authoring_payload": { ... }
   }
   ```

---

### 2.4 Workflow: `UPDATE_EDITION`
When the UAE Ministry of Education releases an updated textbook edition:

1. **Scan Ingestion & OCR**:
   Execute the PDF scanner to re-map scanned pages:
   ```bash
   python -m backend.ocr_reader --pdf-path "path/to/new_edition.pdf" --edition-id "edition_grade_05_2024_v1"
   ```

2. **Page Offset Re-alignment**:
   Run automated diff verification against existing lesson page ranges. Update `page_start` and `page_end` in the `lessons` table.

3. **Content Versioning**:
   Create a new entry in `lesson_versions` with `version_tag: "v0.3.0"`, preserving historical student attempts linked to previous edition versions.

4. **Regression Run**:
   Run full backend test suite to verify grading normalizer and answer key hashes:
   ```bash
   python -m unittest backend/tests/test_backend.py
   ```

---

## 3. Database Maintenance & Migration
- Database file: `backend/fahim.db` (SQLite in local dev, PostgreSQL in production).
- Backup procedure:
  ```bash
  sqlite3 backend/fahim.db ".backup 'backend/backups/fahim_$(date +%Y%m%d_%H%M%S).bak'"
  ```
