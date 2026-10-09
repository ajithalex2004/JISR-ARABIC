# JISR Arabic (فهيم) — Graphic Assets & Screenshot Specifications
**Platform Targets:** Apple App Store (iOS / iPadOS) & Google Play Store (Android)  
**Brand Identity:** JISR EdTech / Fahim (فهيم)  
**Primary Brand Colors:**
- **Emerald Green (الأخضر الزمردي):** `#059669` (RGB: 5, 150, 105)
- **Golden Accent (الذهبي المعرفي):** `#D97706` (RGB: 217, 119, 6)
- **Deep Navy Background (كحلي داكن):** `#0F172A` (RGB: 15, 23, 42)
- **Soft Slate Card (رمادي أردوازي):** `#1E293B` (RGB: 30, 41, 59)
- **Clean White (أبيض ناصع):** `#FFFFFF` (RGB: 255, 255, 255)

---

## 1. App Icon Specifications

### 1.1 Google Play Store Icon
- **Dimensions:** `512 x 512` pixels
- **Format:** 32-bit PNG (RGB with no alpha / transparency)
- **Max File Size:** 1,024 KB
- **Corner Radius:** Square (Google Play automatically applies dynamic squircle masking with radius = 20% / ~102px).
- **Safe Zone:** Keep key logo elements within the central `384 x 384` pixel bounding box to avoid truncation by device masks.

### 1.2 Apple App Store Icon
- **Dimensions:** `1024 x 1024` pixels
- **Format:** PNG, 24-bit RGB (strictly **no alpha / transparency**)
- **Color Profile:** sRGB or Display P3
- **Corner Radius:** Square (Apple App Store automatically clips corners dynamically).
- **Target File:** `mobile/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png`

---

## 2. Google Play Feature Graphic (الصورة البارزة)

The Feature Graphic is displayed at the top of the store listing on Android devices and within Google Play recommendation carousels.

- **Exact Dimensions:** `1024 x 500` pixels (Landscape 2.048:1 aspect ratio)
- **Format:** JPEG or 24-bit PNG (strictly **no alpha / transparency**)
- **File Size Limit:** Up to 1 MB
- **Safe Zone:**
  - Margin: Keep all text, branding, and central character artwork at least **60px from the edges** (Safe area: `904 x 380 px`).
  - Bottom-right corner: Leave clear for the Google Play rating/install overlay.
- **Visual Composition Blueprint:**
  - **Background:** Deep Navy gradient (`#0F172A` to `#1E293B`) with subtle Islamic geometric / arched bridge arabesque motif at 8% opacity.
  - **Left Section (or Center-Left):** Glowing Golden Bridge logo icon (`assets/logos/jisr-logo-3-512.png`) with gentle emerald drop shadow.
  - **Right Section (or Center-Right):** 
    - Main Title: **جسر | JISR** in bold modern Arabic typography (`#FFFFFF`).
    - Sub-headline: **تعلم العربية مع فهيم • منهاج دولة الإمارات** (`#F59E0B`).
    - Badges: "ذكاء اصطناعي تفاعلي • خالٍ من الإعلانات" (`#10B981`).

---

## 3. Store Screenshot Storyboard & Copy Specifications

Both stores require screenshots demonstrating authentic in-app experiences. Below are the 6 core marketing screens with bilingual captions and visual directives.

### 3.1 Dimensions by Device Class

| Device Target | Store Requirement | Recommended Resolution | Aspect Ratio |
| :--- | :--- | :---: | :---: |
| **iPhone 6.7" Super Retina** | Apple Required (iPhone 15/14 Pro Max) | `1290 x 2796` px | 19.5:9 |
| **iPhone 6.5" / 5.5" Retina** | Apple Required (iPhone 11 / 8 Plus) | `1242 x 2688` px | 19.5:9 |
| **iPad Pro 12.9" (6th Gen)** | Apple iPad Target | `2048 x 2732` px | 4:3 |
| **Android Smartphone** | Google Play Phone Target | `1080 x 2400` px or `1080 x 1920` px | 20:9 / 16:9 |
| **Android 7" & 10" Tablets** | Google Play Tablet Target | `1200 x 1920` px & `1600 x 2560` px | 16:10 |

---

### 3.2 Six-Screen Marketing Storyboard

#### 📱 Screen 1: The AI Tutor & Welcome Screen (الترحيب ورفيق التعلم)
- **Arabic Headline:** **«رفيقك الذكي لتعلم لغة الضاد»**
- **Arabic Sub-caption:** دروس تفاعلية ومحادثات ذكية مع فهيم تحبب طفلك في اللغة العربية
- **English Headline:** **Your Smart Arabic AI Tutor**
- **English Sub-caption:** Interactive lessons and speaking practice designed for joyful learning
- **In-App Visual:** Fahim avatar welcoming student, daily streak counter (🔥 5 Days), personalized study path with Grade level badge.

#### 🎙️ Screen 2: Real-Time Pronunciation Coach (تقييم النطق ومخارج الحروف)
- **Arabic Headline:** **«تحدث مع فهيم وقوّم نطقك لحظياً»**
- **Arabic Sub-caption:** تقنية ذكاء اصطناعي صوتية تحلل مخارج الحروف الفصيحة بدقة تامة
- **English Headline:** **Speak with Fahim & Perfect Your Pronunciation**
- **English Sub-caption:** Real-time phonetic feedback for confident, articulate Arabic speech
- **In-App Visual:** Active microphone audio wave visualizer, phrase reading card with color-coded phonetic accuracy (Green = 100%, Amber = Repeat), star rating.

#### 📚 Screen 3: UAE National Curriculum Aligned (منهاج وزارة التربية والتعليم)
- **Arabic Headline:** **«تغطية شاملة لمنهاج دولة الإمارات»**
- **Arabic Sub-caption:** وحدات دراسية مطابقة لتوزيع الفصول المدرسية ونماذج الاختبارات
- **English Headline:** **100% Aligned with UAE MoE Curriculum**
- **English Sub-caption:** Structured textbook units, grammar rules, and reading comprehension
- **In-App Visual:** Curriculum chapter roadmap with UAE flag badge, Grade 4 & 5 units, reading comprehension and grammar (النحو والصرف) modules.

#### 📸 Screen 4: Smart Homework & Worksheet Scanner (الماسح الذكي للواجبات)
- **Arabic Headline:** **«صوّر واجبك وتدرّب بذكاء»**
- **Arabic Sub-caption:** التقط صورة ورقة العمل ليقدم لك فهيم شروحات وتلميحات تفاعلية
- **English Headline:** **Scan Worksheets & Homework Instantly**
- **English Sub-caption:** Snap a photo to receive intelligent step-by-step guidance
- **In-App Visual:** Camera scanning frame over an Arabic textbook page, bounding boxes highlighting exercise questions with AI hint popover.

#### 🎮 Screen 5: Gamified Quizzes & Challenges (التحديات والمنافسات التفاعلية)
- **Arabic Headline:** **«تحديات حماسية ومكافآت يومية»**
- **Arabic Sub-caption:** العب، تنافس، واجمع الأوسمة بينما تتقن مهارات القواعد والإملاء
- **English Headline:** **Engaging Quizzes & Rewarding Challenges**
- **English Sub-caption:** Master spelling and grammar through gamified quests and streak badges
- **In-App Visual:** Multiple-choice quiz screen with instant celebration confetti, score counter (+50 XP), progress bar, and achievement trophy.

#### 📊 Screen 6: Parent & Educator Mastery Dashboard (متابعة الإنجاز والتقدم)
- **Arabic Headline:** **«لوحة متابعة دقيقة لأولياء الأمور»**
- **Arabic Sub-caption:** تقارير فورية توضح ساعات الدراسة ومعدلات إتقان القراءة والنحو
- **English Headline:** **Comprehensive Student Analytics**
- **English Sub-caption:** Real-time visibility into study hours, vocabulary growth, and mastery
- **In-App Visual:** Clean analytics graph showing weekly study minutes, breakdown radar chart (المفردات 92%، النحو 88%، القراءة الجهرية 95%).

---

## 4. Typography & Framing Guidelines

1. **Font Family for Captions:**
   - Arabic: **Tajawal** or **Cairo** (Bold for headlines, Medium for subheadings).
   - English: **Inter** or **SF Pro Display** (SemiBold / Medium).
2. **Device Mockup Framing:**
   - Use clean, minimal device bezels (titanium / midnight frame) floating over the branded navy or emerald gradient background.
   - Maintain 80px padding between the phone frame and the top caption to prevent clutter.
3. **Legibility & Accessibility:**
   - Contrast ratio between text and background exceeds WCAG AAA (minimum 7:1).
   - Text size on screenshots must be comfortably readable on a 5.5-inch phone screen without zooming.
