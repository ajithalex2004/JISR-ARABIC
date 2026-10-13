# AI lesson drafts

Grade 5 has hand-written lesson content; other grades showed template text. The AI drafting
job uses Gemini to read the scanned textbook pages for each chapter and write a full lesson
package for teacher review (vocabulary, grammar, listening and speaking, practice, exam
practice, spaced recall, parent and tutor notes). It follows the same structure as the Grade 5
"Ball Games" lesson.

## Running it

Admin → **Curriculum Review** → pick the grade and term → **Draft Grade N Term N**.
The job runs in the background, at about one minute per lesson. When it finishes, the panel
shows how many lessons were drafted, skipped or failed.

- A lesson that already has a draft waiting for review is skipped. Use **Redraft this lesson**
  to replace it; the old draft is marked `superseded`.
- One lesson failing (for example, missing page scans or a model error) doesn't stop the others.
  The reason is shown in the panel.

## Reviewing

Each lesson lists its versions. AI drafts are labelled with the textbook pages they came from.

1. **Preview**: check the vocabulary, the exam questions and the full package.
2. **Approve**: a second person must approve. The draft's author is recorded as `ai-drafter`,
   so any admin can approve it.
3. **Publish**: the version goes live for learners.

Nothing an AI draft contains reaches learners until a person approves and publishes it.

## Checks before a draft is saved

- Every section of the lesson package is present and has the right shape.
- Every multiple-choice answer key points to one of that question's options.
- The existing lesson quality gate passes (no placeholder text, no duplicate activity ids).

## Requirements

- `GEMINI_API_KEY` on the api service. Optional: `FAHIM_DRAFT_MODEL` sets the model (the
  default is `GEMINI_MODEL`).
- Textbook page images on the content volume at
  `pdf_pages_sample/moe_gr{grade}_vol{term}_2023/page_{n}.png` (already uploaded).
- Each chapter uses the pages from its own start page up to the next chapter's start page.
  The last chapter in a term uses 10 pages. A chapter never uses more than 14 pages.
