# JISR Arabic (فهيم) — Store Compliance, Data Safety & Declarations
**Platform Targets:** Google Play Console & Apple App Store Connect  
**Package / Bundle ID:** `com.jisr.app.mobile`  
**Classification:** K-12 Educational AI Platform  

---

## 1. Google Play Console: Data Safety Form (نموذج أمان البيانات)

Google Play mandates an explicit disclosure of all data collected, shared, and encrypted. Use the exact answers below when completing the **Data Safety** section in Google Play Console.

### 1.1 Data Collection & Security Overview
- **Does your app collect or share any of the required user data types?**  
  👉 **Yes**
- **Is all of the user data collected by your app encrypted in transit?**  
  👉 **Yes** (All network traffic is encrypted via HTTPS / TLS 1.3).
- **Do you provide a way for users to request that their data be deleted?**  
  👉 **Yes** (In-app deletion under Settings > Account, and web deletion portal at `https://jisr.ae/delete-account`).

---

### 1.2 Data Type Breakdown & Disclosures

#### A. Personal Info (معلومات شخصية)
| Sub-Type | Collected? | Shared? | Ephemeral? | Required or Optional? | Purpose |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Name** | **Yes** | **No** | No | Optional (Student nickname) | App functionality, Personalization |
| **Email address** | **Yes** | **No** | No | Required for parent/teacher accounts | App functionality, Account management |
| **User IDs** | **Yes** | **No** | No | Required | App functionality, Account management |

#### B. Audio Files (ملفات الصوت)
| Sub-Type | Collected? | Shared? | Ephemeral? | Required or Optional? | Purpose |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Voice or sound recordings** | **Yes** | **No** | **Yes** | Optional (Used during speaking tasks) | App functionality (Real-time speech & pronunciation evaluation with AI tutor Fahim) |

> [!NOTE]
> Mark **Ephemeral processing = Yes** for Voice recordings. Audio buffers are evaluated in memory for pronunciation scoring and discarded immediately after scoring.

#### C. Photos and Videos (الصور ومقاطع الفيديو)
| Sub-Type | Collected? | Shared? | Ephemeral? | Required or Optional? | Purpose |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Photos** | **Yes** | **No** | No | Optional | App functionality (Homework & worksheet scanner OCR) |

#### D. App Activity & Performance (النشاط والأداء)
| Sub-Type | Collected? | Shared? | Ephemeral? | Required or Optional? | Purpose |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **App interactions** | **Yes** | **No** | No | Required | Analytics, Progress tracking, Curriculum mastery |
| **Crash logs & Diagnostics** | **Yes** | **No** | No | Required | Analytics, Bug fixing, Performance monitoring |

#### E. Data Sharing Declaration
- **Is any collected data shared with third parties or data brokers?**  
  👉 **Strictly NO**. All data remains within JISR's sovereign AWS UAE infrastructure (`me-central-1`).

---

## 2. Google Play Target Audience and Families Policy

### 2.1 Target Age Group Selection
- **Target Ages:** Select **6-8**, **9-12**, and **13-17**.
- **Could your app appeal to children?**  
  👉 **Yes** (The app is intentionally designed for K-12 students).

### 2.2 Google Play Families Policy Certification
1. **Ads Declaration:**
   - "Does your app contain ads?" 👉 **No, my app does not contain ads.**
2. **Neutral Age Screen:**
   - Implemented during student onboarding to ensure appropriate curriculum level assignment.
3. **SDK Compliance:**
   - JISR uses **zero ad networks** and **zero behavioral tracking SDKs**.
   - All networking is handled directly by standard Flutter HTTP and secure platform channels.

### 2.3 Android Dangerous Permission Justification

| Permission | Technical Name | User-Facing Justification |
| :--- | :--- | :--- |
| **Microphone** | `android.permission.RECORD_AUDIO` | **Arabic Speaking Missions:** Allows students to read Arabic phrases aloud and receive real-time pronunciation scoring from Fahim. |
| **Camera** | `android.permission.CAMERA` | **Worksheet Scanner:** Allows students to photograph physical worksheets and textbook questions for AI-guided tutoring. |
| **Media Images** | `android.permission.READ_MEDIA_IMAGES` | **Homework Upload:** Allows students to upload pre-existing textbook or worksheet images from their device gallery. |

---

## 3. Apple App Store: App Privacy Details (Nutrition Labels)

When completing the **App Privacy** questionnaire in App Store Connect:

### 3.1 Tracking Declaration
- **Do you or your third-party partners track users across apps and websites owned by other companies?**  
  👉 **NO**

### 3.2 Data Collected by Type

#### 1. Contact Info: Email Address
- **Data Used to Track You?** No
- **Linked to the User?** Yes
- **Purpose:** App Functionality (Account Management, Login authentication)

#### 2. User Content: Audio Data
- **Data Used to Track You?** No
- **Linked to the User?** No (or Yes if associated with student exercise score history)
- **Purpose:** App Functionality (Speech pronunciation evaluation)

#### 3. User Content: Photos or Videos
- **Data Used to Track You?** No
- **Linked to the User?** Yes
- **Purpose:** App Functionality (Worksheet analysis)

#### 4. Identifiers: User ID
- **Data Used to Track You?** No
- **Linked to the User?** Yes
- **Purpose:** App Functionality (Profile identification, Progress persistence)

#### 5. Usage Data: Product Interaction
- **Data Used to Track You?** No
- **Linked to the User?** Yes
- **Purpose:** Analytics & App Functionality (Curriculum mastery metrics, daily streaks)

#### 6. Diagnostics: Crash Data & Performance Data
- **Data Used to Track You?** No
- **Linked to the User?** No
- **Purpose:** Analytics (App health, runtime stability)

---

## 4. IARC & Content Rating Questionnaire

The International Age Rating Coalition (IARC) questionnaire determines the app's global age rating.

| Category / Question | Response | Notes |
| :--- | :---: | :--- |
| **Violence:** Does the app contain violence? | **NO** | Zero violent imagery or references. |
| **Fear:** Does the app contain scary elements? | **NO** | Child-friendly educational content. |
| **Sexuality:** Does the app contain sexual content or nudity? | **NO** | Entirely educational. |
| **Controlled Substances:** References to alcohol, tobacco, drugs? | **NO** | Strictly absent. |
| **Language / Profanity:** Does the app contain crude humor or profanity? | **NO** | Pure classical Modern Standard Arabic (فصحى). |
| **Miscellaneous: User-to-User Communication?** | **NO** | No unmoderated open chat or public messaging. |
| **Physical Location Sharing?** | **NO** | No location broadcasting. |
| **Digital Purchases?** | **Optional / No** | Subscription management occurs via provider or school licensing. |

### Resulting Global Ratings
- **Google Play:** Rated for **3+** / **Everyone**
- **Apple App Store:** Rated **4+**
- **PEGI:** **PEGI 3**
- **USK:** **USK 0**
- **ESRB:** **Everyone (E)**
- **ClassInd:** **L** (General Audience)

---

## 5. UAE MoE & Sovereign Compliance Statement

```text
DECLARATION OF CURRICULUM INTEGRITY & SOVEREIGN DATA HOSTING:

JISR EdTech FZ-LLC certifies that:
1. The curriculum content provided within JISR Arabic (فهيم) is modeled upon the official United Arab Emirates Ministry of Education (MoE) national Arabic language learning outcomes for K-12 stages.
2. The platform respects UAE cultural heritage, values, and pedagogical frameworks.
3. In accordance with the UAE National Data Strategy and Federal Decree-Law No. 45/2021 (PDPL), all backend production APIs and databases are deployed in AWS UAE (me-central-1), ensuring student data remains within the UAE sovereign territory.
```
