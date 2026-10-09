# Architectural implementation record

## Item 1 — Modular backend foundation

Status: implemented on 21 September 2026 following explicit approval.

### Previous status and current implementation

| Area | Previous status | Current implementation |
| --- | --- | --- |
| HTTP endpoints | Route handlers combined request handling, business rules, and database operations. | Existing route handlers parse requests, resolve dependencies, and delegate to domain services. |
| Identity | Authentication and child-profile operations lived in the authentication router. | `backend/modules/identity/service.py` owns those operations; `backend/api/dependencies.py` binds request credentials and database sessions. |
| Curriculum | Catalogue, authoring, audio, and learning-content operations lived in separate routers without a shared domain boundary. | `backend/modules/curriculum/` groups catalogue, authoring, audio, booklets, and capsule operations. |
| Assessment | Attempt grading and exam operations were embedded in HTTP handlers. | `backend/modules/assessment/` owns attempt and exam operations, using the existing scoring and question-bank helpers. |
| Progress | Mastery, parent reports, and rewards were implemented inside routers. | `backend/modules/progress/` groups mastery, reporting, and reward operations. |
| Tutoring | Tutor submissions/reviews and assistant operations were implemented inside routers. | `backend/modules/tutoring/` owns both areas. |
| Billing | Checkout, vouchers, invoices, and entitlements were implemented inside payment routes. | `backend/modules/billing/service.py` owns those operations. |
| Dependencies | Business operations used FastAPI dependency defaults. | Database sessions and actors are explicit service arguments; services do not import FastAPI or HTTP adapters. |
| Errors | Business operations raised FastAPI exceptions. | Services raise `ApplicationError`; the API translates it into the existing HTTP status, detail, and headers. |
| API assembly | `main.py` registered every router separately. | `backend/api/router.py` is the single API composition point. |
| Verification | The existing suite used the application's configured database. | A new isolated runner binds all tests to a disposable database before importing the app. |

### Structure and dependency direction

```text
React / Flutter
    -> backend/routes/              HTTP adapters; existing endpoints
    -> backend/modules/
         identity/service.py
         curriculum/service.py, authoring.py, audio.py, learning.py
         assessment/attempts.py, exams.py
         progress/mastery.py, reporting.py, rewards.py
         tutoring/service.py, assistant.py
         billing/service.py
    -> backend/models.py + backend/database.py
```

This remains one FastAPI application and one existing persistence layer. There
are no new network services. Shared schemas, models, content banks, scoring,
and cryptography helpers remain in their existing locations. Services never
call route handlers; HTTP-specific response streaming stays in the adapter.

### Visible behavior

Existing pages, endpoint URLs, request fields, response models, and successful
flows remain compatible. No frontend or Flutter files were changed. The
restructuring does not introduce a visual redesign or new educational features.

### Verification

- Before restructuring: all 18 existing backend tests passed on a temporary database.
- After restructuring: all 18 existing tests and six additional regression tests passed (24 total).
- Complete generated OpenAPI document matched the pre-change baseline exactly.
- Regression checks cover transport-independent services, explicit session
  dependencies, authentication error responses, scanned-page errors and file
  delivery, and query defaults/validation.
- SHA-256 comparison confirmed the application's `backend/fahim.db` was unchanged.

Use the isolated runner for subsequent verification:

```powershell
python -B -m backend.tests.run_isolated
```

The legacy test file remains unchanged. Running it directly still uses the
configured application database; use the isolated runner above instead.

### Approval boundary and remaining work

At completion of Item 1, only that restructuring was approved. Existing access-control weaknesses, reviewer bypass,
OTP disclosure, session-role behavior, simulated payments, grading weaknesses,
mutable seed versions, migration behavior, reporting placeholders, and release
configuration have deliberately not been corrected by this restructuring.
Passing compatibility tests does not establish production readiness.

Next proposal: consistent authentication and child/role authorization. Show
its proposed behavior in a browser preview and obtain explicit approval before
implementing it. Continue the same preview -> approval -> implementation ->
verification -> before/after report sequence for each subsequent item.

## Item 2 — Role and child access control

Status: implemented following the user's explicit instruction to implement Item 2.

| Previous status | Current functionality |
| --- | --- |
| Many personal-data and write APIs accepted anonymous requests. | They require a valid session; missing or invalid sessions return 401. |
| A caller could supply another family's child ID. | Shared ownership policy checks path, query, and body child IDs before personal reads or writes; denied access returns 403. |
| Student PIN sessions were treated as the parent account. | Immutable session principals retain the learner role and child scope. Learners cannot switch to siblings, edit profiles/PINs, buy access, or use parent/staff pages. |
| Profile restoration returned all siblings and their PINs. | Learner profile/children responses contain only the selected child and omit the PIN. Tutor profile responses contain assigned learners without PINs. |
| Tutor queues exposed all submissions. | Tutors see and review only explicitly assigned learners. Reviews record the acting tutor. |
| There was no tutor access-management workflow. | Administrators can assign and revoke tutor access in the admin page. Composite tutor/child keys prevent duplicate assignments. Revocation is checked on each request. |
| Administrative changes were anonymous. | Curriculum mutations and tutor assignment management require administrator role. |
| The reviewer flag granted privileged access by itself. | Reviewer requests require staff role; tutors additionally require an assigned learner context. Further paid-content and answer-key hardening remains a separate item. |
| Invoice identifiers exposed another family's billing data. | Receipt, invoice-number, and transaction-ID lookup all require parent ownership or administrator access. Tutors and learners cannot access billing APIs. |
| A common grade/school exposed unrelated children on leaderboards. | Leaderboard queries include only children visible to the session. School names do not grant access. |
| Clients could call the manual XP endpoint. | Manual XP awards now require an administrator; broader grading/reward integrity remains pending. |
| Many web API calls omitted credentials or displayed error JSON as successful data. | One request helper attaches the current token; 401/403 errors produce visible notices. Parent, tutor, and admin pages are role-gated. |

### Deployment and scope

- The additive `tutor_assignments` table is created by the existing startup
  `Base.metadata.create_all` step. Restart the backend when deploying; no
  existing child, payment, lesson, or progress records are rewritten by this change.
- No automatic tutor grants are created from school names or legacy submissions.
  An administrator must explicitly assign learners in the admin page.
- Shared public learning/reference endpoints (including legacy textbook read
  URLs under `/api/admin`) remain public. Personal data and administrative writes
  are protected. The authorization test suite keeps an explicit public-route list.
- OTP delivery/disclosure, signing-secret configuration, PIN hashing, payment
  verification, and full content entitlement enforcement remain pending their
  respective items. Item 2 is not a production-security sign-off.
- Flutter's existing demonstration tokens are not valid backend sessions.
  Mobile authentication integration remains a separate approved-work item; the
  protected API no longer accepts unauthenticated mobile requests.

### Validation

- 33 backend tests pass using disposable databases, including real-token
  authorization tests with foreign-key enforcement and no authentication mocks.
- Tests cover anonymous reads/writes, cross-family reads/writes, learner scope,
  expired/invalid/changed-role tokens, tutor filtering/review/revocation,
  administrator-only changes, reviewer privilege, invoice aliases, and scoped leaderboards.
- Existing happy-path tests now authenticate as the appropriate parent or admin.
- Web TypeScript and production build checks completed. Browser interaction
  testing was not performed for this item.

### Working preferences

Reuse the audit and this implementation record rather than repeatedly reading
unchanged files. Keep commentary and final reports brief. Read additional code
only where required to implement or verify the approved change.


## Item 3 — Reviewer and paid-content protection

Status: implemented after explicit Item 3 approval.

| Previous status | Current functionality |
| --- | --- |
| Lessons enforced payment separately; booklets and adaptive questions bypassed it. | One domain policy checks lesson identity, learner ownership, demo status and exact grade/term entitlement before returning any of these resources. |
| Reviewer privilege was checked only by the lesson HTTP adapter. | The shared domain policy requires an administrator or a tutor with a currently assigned child. Purchasing access never grants answer-key access. |
| Booklets/adaptive questions exposed keys; sentence builders exposed the target Arabic sentence. | Initial learner responses omit keys and answer explanations. Authorized reviewer responses retain them. Teaching explanations remain available. |
| Booklet and sentence feedback depended on browser-side keys. | The server checks submitted answers. Guests can still practice the demo; signed-in sentence attempts retain progress recording. Booklet feedback reveals only the submitted exercise's answer. |
| Attempts could bypass a locked lesson by submitting directly. | Attempt, booklet-check, sentence-check and exam submission paths enforce entitlement before evaluation or persistence. |
| Unknown booklet/assessment identifiers could return the demo under another lesson's identity. | Missing resources return 404. The current assessment bank is explicitly limited to Ball Games, Class 5 Term 1. |

### Scope and remaining limitations

- The existing exam bank contains Ball Games demo questions, so it retains demo access. It is not a newly authored full-term exam. Other grades/terms now return 404 rather than relabeling those questions.
- Paid booklet/adaptive content that has not been authored returns 404 after access checks. Tests exercise the same available bank under locked/unlocked lesson configuration.
- Post-submission learning feedback intentionally includes solutions. This is initial-response protection, not a secure high-stakes examination system.
- Standalone capsules and mastery drills are outside this lesson/booklet/assessment change; their existing client-side scoring remains part of the pending grading-integrity item.
- Verified payment processing, OTP/session hardening and immutable content versions remain separate items. No schema migration or application-data rewrite is required here.
- API tests use disposable databases. Frontend verification uses TypeScript and production build; live browser interaction has not been tested for this item.

Next: preview Item 4 (OTP/session hardening), then wait for approval before implementation.

Item 3 final validation: 37 isolated backend tests passed; frontend TypeScript and production build passed. The existing bundle-size warning remains.

## Item 4 — Approval preview only

No authentication implementation changes made. Proposed scope: email delivery without debug OTP responses; cryptographic OTP generation and hashed storage; 10-minute expiry and atomic single use; five attempts per challenge plus account/IP throttling; 60-second resend cooldown; hashed child PINs with no default or retrieval; configured signing secret; revocable server-tracked sessions and password-reset invalidation. Production mail credentials will be needed for live delivery; use a private test adapter for isolated verification. Preview: fahim-item-4-preview.html in the thread visualization directory. Await explicit Item 4 approval.

## Item 4 — OTP and session protection

Status: implemented after explicit approval.

Previous behavior returned OTPs in API responses, stored OTP plaintext, accepted unlimited guesses, used a shared signing-key fallback, stored child PINs plaintext, and issued tokens without revocation records.

Current behavior hashes OTPs and child PINs, limits OTP challenges to five attempts, expires them after ten minutes, applies a sixty-second resend cooldown, omits debug codes when `FAHIM_ENV=production`, generates a per-process secret when development configuration omits one, and records application-issued sessions for production revocation. `/api/auth/logout` revokes the current session; password reset revokes all sessions. Legacy plaintext PINs remain readable only through a one-time comparison path and are replaced when changed. Child profile and reporting responses no longer return PINs.

The backend must be deployed with a stable `FAHIM_SECRET_KEY` and a mail delivery adapter before production use. The current local development adapter retains `debug_otp` for existing isolated demo tests; production responses never include it. Existing compatibility tests that assert returned plaintext PINs fail by design (2 assertions); the security contract supersedes those expectations. Frontend TypeScript and production build pass.

## Item 5 — Verified payment and entitlement integrity

Status: implemented after explicit approval.

Checkout requests now accept an idempotency key and provider payment identifier. Repeated idempotent requests return the original transaction instead of creating another unlock. In production, checkout without provider confirmation is rejected. A signed provider webhook applies confirmed events once, leaves failed events locked, and rejects invalid signatures. Refund reconciliation marks the transaction refunded and locks only the entitlements linked to that receipt. Existing receipt and invoice lookups remain parent/admin scoped.

The payment provider secret is `FAHIM_PAYMENT_WEBHOOK_SECRET`; production must configure it. The local development checkout remains available for the existing demo flow. Frontend build and payment regression paths pass. Three legacy tests still expect plaintext PIN responses from Item 4 and are unrelated to Item 5.

## Item 6 — Grading and progress integrity

Status: implemented after explicit approval.

Capsule completion now resolves the capsule bank server-side and calculates score from submitted answers; client score is ignored. Drill correctness is derived from the pinned question rather than the request flag. Attempts, capsule completion, and exam submissions accept idempotency keys to prevent duplicate records or progress awards. Unknown questions and malformed selections are rejected. Exam submissions reject invalid or over-limit elapsed times. Tutor rubric scores are range-validated and remain separate from automatic grading.

Validation: Python compilation and frontend production build pass. The isolated suite has 34 passing tests; three older assertions still expect plaintext PINs from Item 4 and are intentionally incompatible with the new protected response contract.

## Item 7 — Immutable content versions

Status: implemented after explicit approval.

Lesson versions now carry lifecycle metadata and published versions are never edited in place. New imports receive a hash-qualified version ID, publication timestamp, and immutable content hash. Learner reads and grading verify the hash, and attempts continue to store the exact lesson version they used. Administrators can roll back by selecting an existing version; rollback changes only the active pointer and preserves historical attempts. Existing content remains published for compatibility.

Validation: Python compilation and frontend production build pass. The isolated suite retains the three intentional Item 4 plaintext-PIN assertion failures; content-version and regression paths pass.

## Item 8 — Database reliability and migration safety

Status: implemented after explicit approval.

Schema changes now use recorded, ordered migrations in `backend.migrations`. Production startup performs a read-only revision check and fails clearly when migrations are pending; run `python -m backend.migrations upgrade` during deployment. Production startup no longer creates tables or seeds demo/content records. Development setup remains available and can disable demo seeding with `FAHIM_SEED_DEMO=0`.

SQLite connections enable foreign keys, WAL mode, and a five-second busy timeout. Request-scoped database sessions roll back on exceptions. Database uniqueness now protects term entitlements, capsule progress, and concept mastery against concurrent duplicates; payment, attempt, and exam idempotency constraints remain in place. `python -m backend.backup [destination]` uses SQLite's online backup API and verifies the backup with `PRAGMA integrity_check`.

Validation: Python compilation, migration bootstrap through the disposable test database, and frontend production build pass. The isolated suite has 34 passing tests; the three known Item 4 failures still assert that plaintext PINs are returned.

## Item 9A — Flutter authentication integration

Status: implemented after explicit approval.

The mobile client no longer creates guest identities or accepts hardcoded demo credentials. It calls the backend authentication endpoints for password, OTP, signup, learner PIN, child switching, session restore, and logout. Access tokens are stored in platform secure storage, attached to protected requests, and cleared on logout or invalid-session responses. Android declares network access; the API base can be configured with `--dart-define=FAHIM_API_BASE=...` (the default targets the Android emulator host).

The add-learner shortcut now reports that web profile integration is required instead of silently creating a local demo child. Google sign-in also reports its unconfigured state instead of fabricating a successful login. Existing educational sample names in lesson/leaderboard content are static product content, not authentication identities.

Validation: source-level scan confirms demo auth credentials and guest session fallbacks were removed. Backend and web validations remain green from Item 8. Flutter dependency/analyzer commands could not complete in this environment (the toolchain hung without output), so a device build remains required before mobile release.

## Item 10 — Web/mobile API parity

Status: implemented after explicit approval.

Flutter now has a shared `ApiService` covering the web API contract for curriculum, lessons, attempts, capsules, adaptive/exam assessment, mastery, parent dashboards, gamification, AI, and payments-compatible HTTP semantics. It centralizes base URL configuration, bearer authentication, JSON encoding/decoding, query parameters, and consistent API error handling. This removes the previous pattern where mobile screens assembled a small subset of endpoints independently.

Payment and Ask Fahim screens now use `ApiService`; no direct HTTP endpoint calls remain in `main.dart`. The client does not change backend routes or response schemas. Broader mobile learning screens can now use the same client without introducing another transport implementation.

## Item 11 — Observability and security audit events

Status: implemented after explicit approval.

Backend requests now emit structured JSON logs with timestamps, method, path, status, duration, and an `X-Request-ID` correlation header. Unhandled failures are logged with exception type while application errors retain their stable response contract. Security audit events record successful password/PIN logins, logout, payment checkout, and voucher redemption without logging secrets or credentials. Monitoring agents can consume the JSON stream from stdout through `backend.observability`.

## Item 12 — Production CORS restriction

Status: implemented after explicit approval.

Wildcard CORS has been removed. Development uses localhost origins, while production requires the comma-separated `FAHIM_CORS_ORIGINS` environment variable and fails startup when it is missing. Origins are normalized before registration, and credentials remain enabled only for the explicit allowlist.

## Item 13 — Deployment configuration and secret validation

Status: implemented after explicit approval.

Production startup now validates `FAHIM_SECRET_KEY`, `FAHIM_PAYMENT_WEBHOOK_SECRET`, and `FAHIM_CORS_ORIGINS`; it enforces minimum secret lengths and rejects demo seeding. Missing or weak configuration fails closed with names only, never secret values. `backend/.env.example` documents the required deployment variables. Secrets must be supplied by the deployment secret manager or environment, not committed to source control.

## Item 14 — Continuous integration checks

Status: implemented after explicit approval.

`.github/workflows/ci.yml` gates pull requests and main/master pushes with backend compilation, migration status, isolated backend tests, frontend production build, and Flutter formatting, analysis, dependency resolution, and Android debug build. The existing release workflow remains responsible for Android release and unsigned iOS artifacts.

## Item 15 — Neon/PostgreSQL database configuration

Status: implemented after explicit approval.

The backend now loads `backend/.env` when `python-dotenv` is installed and reads `DATABASE_URL`, falling back to the local SQLite file only when it is absent. PostgreSQL engines use pre-ping and configurable pooling; SQLite-only PRAGMAs are no longer applied to Neon. Migration table and column inspection now use SQLAlchemy introspection instead of SQLite catalog queries, with PostgreSQL type normalization for legacy additions. Local validation could not connect to Neon because this execution environment blocks outbound PostgreSQL traffic; run migration commands from an allowed workstation or deployment runner.

## Item 16 — Legacy PIN test updates

Status: implemented after explicit approval.

Updated stale response assertions to expect `access_pin: null`, matching the protected API contract. The isolated runner now forces its disposable SQLite fixture into development mode so a local production `.env` cannot redirect tests to Neon or disable test seed data.

Validation: all 37 isolated backend tests pass.

## Item 17 — Mobile learning screen API migration

Status: implemented after explicit approval.

The mobile home/catalogue now loads lessons and practice capsules through `ApiService` after session restore and child changes, with bearer authentication and a safe static-content fallback when the API is unavailable. It displays the live API counts so the active learning surface is visibly backed by the same backend contract as web. No direct HTTP calls remain in the screen layer; authentication remains isolated in `AuthService`.

## Item 18 — Production curriculum content import

Status: implemented after explicit approval.

Added `python -m backend.content_import`, which imports the authored curriculum catalog, lessons, and immutable lesson versions without creating demo parent, learner, tutor, admin, gamification, or voucher records. It is safe to run after migrations with production seeding disabled. The existing development `seed_database` behavior remains unchanged for isolated tests.

## Item 19 — Secure super-admin bootstrap

Status: implemented after explicit approval.

Added `python -m backend.create_admin`, an interactive one-time command that creates or promotes an administrator in the configured database. It requires a 12-character password, hashes it with the existing password security, marks the account verified, and never prints or stores credentials in source. Production has no shared default administrator credentials.
