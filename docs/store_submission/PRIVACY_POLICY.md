# JISR Arabic (فهيم) — Privacy Policy (سياسة الخصوصية)
**Effective Date:** October 9, 2026  
**Last Updated:** October 9, 2026  
**Entity:** JISR EdTech FZ-LLC, Dubai / Abu Dhabi, United Arab Emirates  
**Compliance Standards:** 
- UAE Federal Decree-Law No. 45/2021 regarding Personal Data Protection (PDPL)
- UAE Federal Law No. 3/2016 on Child Rights (Wadeema's Law)
- Children's Online Privacy Protection Act (COPPA)
- Google Play Families Policy & Developer Distribution Agreement
- Apple App Store Review Guidelines (Section 5.1 Data Collection & Storage)

---

## 1. Introduction (مقدمة)

At **JISR EdTech FZ-LLC** ("JISR", "we", "us", or "our"), safeguarding the privacy of our students, children, parents, and educators is our utmost priority. This Privacy Policy outlines how we collect, process, store, and protect information when you use our mobile applications (iOS and Android), web portals, and educational tutoring services (collectively, the "Platform").

JISR operates under strict compliance with the **UAE Personal Data Protection Law (Federal Decree-Law No. 45/2021)** and adheres to global standards for children’s online safety. All user data is securely hosted within the United Arab Emirates (**AWS UAE me-central-1**).

---

## 2. Information We Collect (البيانات التي نجمعها)

We collect only the minimum personal data strictly necessary to deliver personalized educational tutoring and curriculum instruction:

### 2.1 Account and Profile Data
- **Student Profile:** First name or display nickname, grade level (e.g., Grade 4, Grade 5), language preference, and school curriculum track.
- **Parent / Guardian Account:** Email address, password (stored using salted cryptographic hashes), and optional phone number for verification and progress report notifications.
- **Educator / School Account:** Official school email, institutional affiliation, and assigned class identifiers.

### 2.2 Voice & Audio Data (Speaking Missions)
- **Audio Inputs:** When a student performs an oral reading or speaking exercise with our AI tutor "Fahim", their voice is captured via the device microphone.
- **Ephemeral Processing:** Audio recordings are processed **ephemerally in real-time** for phonetic analysis, pronunciation scoring, and speech-to-text transcription. Raw audio recordings are **not sold, not retained for commercial profiling**, and not shared with third-party advertisers.

### 2.3 Camera and Image Data (Worksheet Scanner)
- **Worksheet Scans:** When a student uses the camera to scan a homework question or textbook exercise, the image is transmitted securely via TLS 1.3 to our AI curriculum parser to generate hints and explanations.
- Images are strictly utilized for educational OCR analysis and are not associated with biometric facial identification.

### 2.4 Educational Progress & Activity Metrics
- Lesson completion history, quiz scores, time spent per unit, streak records, and concept mastery ratings.
- Technical logs: App version, device operating system, network performance, and crash diagnostics (collected in anonymized form to ensure platform stability).

---

## 3. What We Do NOT Collect (ما لا نقوم بجمعه)

- **Zero Advertising or Tracking SDKs:** We do NOT use third-party ad networks, advertising identifiers (IDFA or GAID), or cross-app tracking.
- **No Precise Geolocation:** We do NOT track GPS or fine location coordinates.
- **No Social Media Profiling:** We do NOT link accounts to third-party commercial social platforms.

---

## 4. Legal Basis & Child Privacy (COPPA & Wadeema's Law)

Because our Platform serves K-12 students and children:
1. **Verifiable Parental Consent:** Accounts for children under the age of 13 (or under 18 in accordance with UAE PDPL) require consent from a parent, guardian, or authorized educational institution.
2. **No Behavioral Profiling:** Student data is never commodified, auctioned, or used for targeted marketing.
3. **Parental Access & Erasure:** Parents and guardians have the unconditional right to inspect, correct, export, or permanently delete their child's account and historical progress records at any time.

---

## 5. Data Storage, Residency & Security (تخزين البيانات وأمنها)

- **UAE Data Residency:** All student profiles, school records, and learning histories are stored in managed data centers within the **United Arab Emirates (AWS UAE region `me-central-1`)** in full compliance with UAE sovereign data residency directives.
- **Encryption in Transit:** All communications between client applications and backend APIs are enforced via HTTPS / TLS 1.3 with strict Forward Secrecy. Cleartext traffic (`HTTP`) is completely disabled in application binaries.
- **Encryption at Rest:** Databases and storage volumes are encrypted using industry-standard **AES-256** encryption.
- **Network Isolation:** Database instances and processing workers reside in private, isolated Virtual Private Cloud (VPC) subnets protected by multi-tier firewalls and Web Application Firewalls (WAF).

---

## 6. Data Sharing & Third-Party Processors (مشاركة البيانات)

We do not sell, rent, or trade student personal data. Data is only shared with trusted infrastructure subprocessors strictly required to operate the Platform:
- **Cloud Infrastructure:** AWS UAE (`me-central-1`) for secure database and compute hosting.
- **Transactional Communication:** Enterprise transactional email delivery (e.g. Amazon SES / SendGrid) exclusively for account verification and parent reports.
- **Zero Third-Party Advertising:** No advertiser, data broker, or commercial partner has access to our systems.

---

## 7. User Rights under UAE PDPL (حقوق المستخدم)

Under the UAE Federal Decree-Law No. 45/2021, you possess the following rights:
1. **Right to Access:** Request a copy of all personal data held about you or your child.
2. **Right to Rectification:** Correct inaccurate or outdated academic or profile records.
3. **Right to Erasure (Right to be Forgotten):** Request immediate, permanent deletion of your account and associated data.
4. **Right to Restrict Processing:** Limit the processing of your data under specific conditions.
5. **Right to Data Portability:** Obtain your learning history in a structured, machine-readable format.

To exercise any of these rights, email our Data Protection Officer at: **privacy@jisr.ae**.

---

## 8. Account & Data Deletion Protocol (آلية حذف الحساب والبيانات)

In compliance with Google Play Store and Apple App Store mandates, users can delete their accounts and all associated data through two methods:
1. **In-App Deletion:**
   - Navigate to **الإعدادات (Settings) > الحساب (Account) > حذف الحساب والبيانات (Delete Account & Data)**.
   - Confirm deletion. The system immediately revokes JWT tokens, purges student profile records, and schedules database tombstones within 24 hours.
2. **Web Portal Deletion Request:**
   - Visit our dedicated self-service deletion portal: `https://jisr.ae/delete-account` or email `privacy@jisr.ae` with your registered email address.

---

## 9. Contact Information & Data Protection Officer

If you have questions, feedback, or concerns regarding this Privacy Policy or our child protection safeguards, please reach out to:

**Data Protection Officer (مسؤول حماية البيانات):**  
JISR EdTech FZ-LLC  
Dubai Internet City / Abu Dhabi Global Market  
United Arab Emirates  
Email: `privacy@jisr.ae` / `support@jisr.ae`  
Website: `https://jisr.ae`

---

## 10. النسخة العربية لسياسة الخصوصية (Arabic Summary)

### التزامنا بخصوصية أطفالنا وطلابنا
تلتزم منصة **«جسر» (JISR EdTech FZ-LLC)** بأعلى معايير حماية الخصوصية والأمان الرقمي للأطفال والطلاب وأولياء الأمور والمعلمين، بما يتماشى بالكامل مع **قانون حماية البيانات الشخصية الإماراتي (المرسوم بقانون اتحادي رقم 45 لسنة 2021)** و**قانون وديمة لحماية الطفل (القانون الاتحادي رقم 3 لسنة 2016)**، ومعايير متاجر التطبيقات (Apple و Google Play).

### النقاط الجوهرية:
1. **توطين البيانات:** تخزن جميع بيانات الطلاب والمعلمين داخل مراكز بيانات سحابية متطورة في دولة الإمارات العربية المتحدة.
2. **انعدام الإعلانات:** التطبيق خالٍ تماماً بنسبة 100% من أي إعلانات تجارية أو تتبع سلوكي خارجي.
3. **معالجة الصوت والصور:** تُعالج التسجيلات الصوتية في مهام التحدث وصور أوراق العمل بشكل فوري ومؤقت لأغراض التقييم التعليمي الذكي دون بيعها أو استغلالها تجارياً.
4. **حقوق الحذف:** يحق لولي الأمر أو الطالب في أي وقت طلب حذف الحساب وكافة البيانات المرتبطة به عبر التطبيق أو عبر مراسلتنا على `privacy@jisr.ae`.
