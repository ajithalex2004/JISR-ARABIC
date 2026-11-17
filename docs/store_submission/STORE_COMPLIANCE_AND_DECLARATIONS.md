# JISR Arabic — store privacy forms (Google Play Data safety, Apple App Privacy)

Answers checked against the code on 17 November 2026. The public policy they must match is
`frontend/src/components/legal/LegalPage.tsx` (https://app.jisrarabic.com/privacy), and account
deletion is described at https://app.jisrarabic.com/delete-account.

Re-check these answers whenever a feature starts sending new data anywhere.

## What the app does with data (the facts behind every answer)

| Data | Where it goes | Kept? |
| --- | --- | --- |
| Parent name, email, optional phone, password hash | JISR servers | Until the account is deleted |
| Child name, age, class, school name, PIN | JISR servers | Until deleted |
| Learning progress (answers, scores, mistakes, exams) | JISR servers | Until deleted |
| Ask Fahim questions | JISR servers, Google Gemini (to answer) | Only questions escalated to a teacher are kept, until deleted |
| Homework photos | Google Gemini (to answer) | Not kept by JISR |
| Speaking recordings | Turned into text on the phone where possible; otherwise JISR server and Google Gemini (to transcribe) | Not kept |
| Purchases, receipts, tax invoices | JISR servers; card details only at Stripe (on the website) | Kept without names after deletion (UAE tax law) |
| Feedback | JISR servers | Kept without the name after deletion |
| Email messages | Email delivery service | — |
| Crash reports, analytics, ads, location, device IDs | Not collected (no such SDKs in the app) | — |

## Google Play: Data safety

- Does the app collect or share any of the required user data types? **Yes**
- Is all user data encrypted in transit? **Yes** (HTTPS only)
- Do you provide a way for users to request deletion? **Yes**: in the app (Profile, Delete Account Permanently), and https://app.jisrarabic.com/delete-account
- Shared with third parties? **No** for every type below: Google (Gemini), Stripe and the email service act as service providers on JISR's behalf, which Google Play does not count as sharing.

| Category: data type | Collected | Optional? | Ephemeral? | Purposes |
| --- | --- | --- | --- | --- |
| Personal info: Name | Yes | Required (child's name) | No | App functionality, Account management |
| Personal info: Email address | Yes | Required | No | App functionality, Account management, Developer communications |
| Personal info: Phone number | Yes | Optional | No | Account management |
| Personal info: User IDs | Yes | Required | No | App functionality, Account management |
| Financial info: Purchase history | Yes | Optional | No | App functionality |
| Photos and videos: Photos | Yes | Optional | Yes | App functionality |
| Audio: Voice or sound recordings | Yes | Optional | Yes | App functionality |
| App activity: App interactions | Yes | Required | No | App functionality, Personalization |
| App activity: Other user-generated content (tutor questions, feedback) | Yes | Optional | No | App functionality |

Not collected: location, contacts, calendar, web history, files and docs, health, messages (SMS/email),
app info and performance (crash logs, diagnostics), device or other IDs.

### Target audience and content

- Target age groups: **6–8, 9–12, 13–15, 16–17** (Classes 1–10). The Families policy applies.
- Ads: **No ads.**
- App access: provide the demo parent account and a child PIN for reviewers.
- Content rating questionnaire: no violence, fear, sexual content, drugs, gambling or profanity; users
  can't communicate with each other; no location sharing. Expected rating: **Everyone / PEGI 3**.
- Store builds have **no in-app purchases** (Buy opens the website).

## Apple App Store: App Privacy

- Do you or your partners use data to track users? **No.**

| Data type | Linked to the user | Used for tracking | Purposes |
| --- | --- | --- | --- |
| Contact info: Name | Yes | No | App functionality |
| Contact info: Email address | Yes | No | App functionality |
| Contact info: Phone number | Yes | No | App functionality |
| User content: Photos or videos | Yes | No | App functionality |
| User content: Audio data | Yes | No | App functionality |
| User content: Other user content (tutor questions, feedback) | Yes | No | App functionality |
| Identifiers: User ID | Yes | No | App functionality |
| Usage data: Product interaction | Yes | No | App functionality, Product personalization |
| Purchases: Purchase history | Yes | No | App functionality |

Not collected: location, health, financial info (card details are taken by Stripe on the website), contacts,
browsing or search history, sensitive info, diagnostics, other data.

Photos and audio are declared even though JISR doesn't keep them, because they leave the device and
reach Google's AI. That is the cautious reading of Apple's definition.

Other App Store answers: age rating **4+**; category **Education**; export compliance: **uses only
standard HTTPS encryption** (exempt); privacy policy URL https://app.jisrarabic.com/privacy.

## Before submitting

- Fill in `frontend/src/components/legal/legalFacts.ts`: hosting provider and region, and the contact email
  for privacy requests. The policy uses neutral wording until then.
- Confirm the company name shown on the pages (taken from the site footer).
