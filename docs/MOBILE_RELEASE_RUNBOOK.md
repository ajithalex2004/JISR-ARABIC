# JISR Arabic (فهيم) — Mobile Release Runbook
**Target Platforms:** Android (Google Play Store `.aab` / `.apk`) & iOS (Apple App Store / TestFlight `.ipa`)  
**Production API Base:** `https://api.jisrarabic.com` (AWS UAE `me-central-1`)  
**Flutter Framework:** Flutter 3.38+ / Dart 3.10+

---

## 1. Executive Summary & Security Baseline

This runbook defines the exact, end-to-end operational procedure for building, signing, and distributing the **JISR Arabic (فهيم)** mobile applications for production release.

### Core Security & Hardening Guarantees
1. **Strict Production Endpoint Pinning (`https://api.jisrarabic.com`):**
   - The application defaults to `https://api.jisrarabic.com` in release mode.
   - In release mode (`kReleaseMode == true`), any attempt to connect over unencrypted HTTP (`http://`) or loopback emulator addresses (`10.0.2.2`, `192.168.x.x`) is **strictly aborted** with an `AuthException`.
   - The internal developer server-switcher icon (`IconButton`) in `AuthDialog` is completely hidden and disabled in release mode.
2. **Cleartext Traffic Enforcement:**
   - **Android:** `android:usesCleartextTraffic="false"` is enforced in `mobile/android/app/src/main/AndroidManifest.xml`.
   - **iOS:** App Transport Security (`NSAppTransportSecurity -> NSAllowsArbitraryLoads = false`) is enforced in `mobile/ios/Runner/Info.plist`.
3. **Hardware & Privacy Permissions (App Store / Play Store Compliance):**
   - **Microphone (`RECORD_AUDIO` / `NSMicrophoneUsageDescription`):** Required for student speaking missions and Arabic speech evaluation.
   - **Speech Recognition (`NSSpeechRecognitionUsageDescription`):** Required for live Arabic speech transcription.
   - **Camera (`CAMERA` / `NSCameraUsageDescription`):** Required for worksheet and exam question paper scanning.
   - **Photo Library (`NSPhotoLibraryUsageDescription`):** Required for homework image uploads.
4. **Secure Credential Storage:**
   - JWT tokens are stored exclusively in hardware-backed secure storage via `flutter_secure_storage` (Android Keystore / iOS Keychain).

---

## 2. Automated Build Scripts

Two turnkey automation scripts are provided in the repository to eliminate manual build errors:
- **Windows (PowerShell):** [`mobile/scripts/build_release.ps1`](file:///c:/JISR%20ARABIC/mobile/scripts/build_release.ps1)
- **macOS / Linux / CI (Bash):** [`mobile/scripts/build_release.sh`](file:///c:/JISR%20ARABIC/mobile/scripts/build_release.sh)

### Running Automated Builds
```powershell
# From repository root or mobile folder:
cd "c:\JISR ARABIC\mobile"

# Build Google Play Android App Bundle (.aab) with obfuscation:
.\scripts\build_release.ps1 -Target appbundle

# Build Standalone APK (.apk) for QA testing or MDM distribution:
.\scripts\build_release.ps1 -Target apk

# Build all targets (Android + iOS on macOS):
.\scripts\build_release.ps1 -Target all
```

---

## 3. Android Release Packaging (Google Play Store)

### 3.1 Keystore Generation
For official Google Play deployment, generate an RSA 2048-bit release keystore:
```bash
keytool -genkey -v \
  -keystore mobile/android/app/upload-keystore.jks \
  -alias jisr_upload \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```
> [!CAUTION]
> Back up `upload-keystore.jks` in an enterprise password manager (e.g. AWS Secrets Manager or 1Password). If lost, app updates on Google Play will be blocked unless reset through Google Play Console support.

### 3.2 Keystore Configuration (`key.properties`)
Create `mobile/android/key.properties` (ignored by Git):
```properties
keyAlias=jisr_upload
keyPassword=YOUR_STRONG_KEY_PASSWORD
storeFile=upload-keystore.jks
storePassword=YOUR_STRONG_KEYSTORE_PASSWORD
```
> [!NOTE]
> If `key.properties` is absent, `build.gradle.kts` automatically falls back to the debug signing configuration so local developers can compile without errors.

### 3.3 ProGuard / R8 Rules
ProGuard/R8 optimization rules are defined in [`mobile/android/app/proguard-rules.pro`](file:///c:/JISR%20ARABIC/mobile/android/app/proguard-rules.pro), protecting:
- Flutter embedding & plugins (`io.flutter.**`)
- Secure Storage (`com.it_nomads.fluttersecurestorage.**`)
- Speech recognition (`com.csdcorp.speech_to_text.**`)
- Text-to-speech (`com.tundralabs.fluttertts.**`)

### 3.4 Build Artifacts
1. **Google Play App Bundle (`.aab`):**
   ```bash
   flutter build appbundle --release \
     --dart-define=FAHIM_API_BASE=https://api.jisrarabic.com \
     --obfuscate \
     --split-debug-info=build/app/outputs/symbols
   ```
   **Output:** `mobile/build/app/outputs/bundle/release/app-release.aab`

2. **Testing APK (`.apk`):**
   ```bash
   flutter build apk --release \
     --dart-define=FAHIM_API_BASE=https://api.jisrarabic.com
   ```
   **Output:** `mobile/build/app/outputs/flutter-apk/app-release.apk`

---

## 4. iOS Release Packaging (Apple App Store / TestFlight)

### 4.1 One-time setup (cloud builds via GitHub Actions)
1. **Apple Developer Program** membership (organization account for the company name on the App Store).
2. **App ID** `com.jisr.app.mobile` (same as Android). Create the app record in App Store Connect with this Bundle ID.
3. **App Store Connect API key**: Users and Access → Integrations → App Store Connect API → create a key with the
   *App Manager* role. Note the Issuer ID and Key ID and download the `.p8` file (it can be downloaded only once).
4. **Team ID**: developer.apple.com → Membership details.
5. Add four **repository secrets** (GitHub → Settings → Secrets and variables → Actions):

| Secret | Value |
|---|---|
| `APP_STORE_CONNECT_ISSUER_ID` | Issuer ID (UUID) |
| `APP_STORE_CONNECT_KEY_ID` | Key ID (10 characters) |
| `APP_STORE_CONNECT_KEY_P8` | Full contents of the `.p8` file, including the BEGIN/END lines |
| `APPLE_TEAM_ID` | Team ID (10 characters) |

Signing is automatic: Xcode creates or renews the distribution certificate and provisioning profile through the
API key on each build, so no certificates or profiles need to be stored in the repository.

### 4.2 Building and uploading to TestFlight
GitHub → Actions → **JISR Arabic Mobile Release** → *Run workflow* with target `ios` (or `all`) and
**Deploy .ipa to Apple TestFlight** ticked. The job archives and signs the app, then uploads it to App Store
Connect; it appears in TestFlight after Apple's processing (usually 5–30 minutes). Without the tick, the signed
`.ipa` is kept as the `JISR-iOS-IPA` artifact instead.

Every upload needs a new build number: bump `version:` in `mobile/pubspec.yaml` (e.g. `1.0.6+7` → `1.0.7+8`).

If the secrets are missing, the job warns and produces an **unsigned** archive (not installable on an iPhone);
requesting a TestFlight upload without them fails the job.

### 4.3 Manual build on a Mac (alternative)
```bash
cd mobile
flutter build ipa --release \
  --dart-define=FAHIM_API_BASE=https://api.jisrarabic.com \
  --obfuscate \
  --split-debug-info=build/app/outputs/symbols
```
Then upload `build/ios/ipa/*.ipa` with **Apple Transporter**, or open `mobile/ios/Runner.xcworkspace` in Xcode →
**Product > Archive** → **Distribute App > App Store Connect > Upload**.

---

## 5. Version Bumping Protocol

Before creating a new release, bump the version in [`mobile/pubspec.yaml`](file:///c:/JISR%20ARABIC/mobile/pubspec.yaml):
```yaml
# Format: <version>+<build_number>
version: 2.4.0+24
```
- **Android:** `versionName = 2.4.0`, `versionCode = 24` (Google Play rejects non-incrementing build codes).
- **iOS:** `CFBundleShortVersionString = 2.4.0`, `CFBundleVersion = 24`.

---

## 6. Pre-Flight Verification Checklist

Before submitting to app stores:
- [x] Strict HTTPS endpoint: `FAHIM_API_BASE=https://api.jisrarabic.com` enforced.
- [x] Zero cleartext fallback: `android:usesCleartextTraffic="false"` and `NSAllowsArbitraryLoads=false`.
- [x] Developer server switcher concealed in release mode.
- [x] Audio speaking permissions declared in both Arabic and English.
- [x] Static code analysis: `flutter analyze` passes with 0 errors and 0 warnings.
- [x] Symbols stripped and obfuscation map generated.
- [x] Store submission package prepared (bilingual metadata, screenshots, privacy policy, and graphic assets).

---

## 7. Store Submission Package & Compliance References

Complete store listing metadata, legal policies, and graphic assets are cataloged in `docs/store_submission/`:
1. **Bilingual Listing Metadata:** [`docs/store_submission/APP_STORE_METADATA.md`](file:///c:/JISR%20ARABIC/docs/store_submission/APP_STORE_METADATA.md)
   - Title, subtitle, short & full descriptions, keywords, categories, and reviewer test credentials.
2. **Graphic Asset Specs & Storyboards:** [`docs/store_submission/GRAPHIC_ASSETS_SPECIFICATION.md`](file:///c:/JISR%20ARABIC/docs/store_submission/GRAPHIC_ASSETS_SPECIFICATION.md)
   - 6 screenshot marketing copy blueprints, dimensions, color palettes, and safe zones.
3. **Turnkey Graphic Asset Generator:** [`mobile/scripts/generate_store_assets.ps1`](file:///c:/JISR%20ARABIC/mobile/scripts/generate_store_assets.ps1)
   - Automatically builds `icon_playstore_512.png`, `icon_appstore_1024.png`, and `feature_graphic_1024x500.png` in `mobile/assets/store/`.
4. **Privacy Policy (UAE PDPL & COPPA):** [`docs/store_submission/PRIVACY_POLICY.md`](file:///c:/JISR%20ARABIC/docs/store_submission/PRIVACY_POLICY.md)
   - Self-hosted at `https://jisrarabic.com/privacy` with UAE sovereign data hosting in AWS UAE (`me-central-1`).
5. **Terms of Service:** [`docs/store_submission/TERMS_OF_SERVICE.md`](file:///c:/JISR%20ARABIC/docs/store_submission/TERMS_OF_SERVICE.md)
   - Hosted at `https://jisrarabic.com/terms`.
6. **Store Compliance & Data Safety Declarations:** [`docs/store_submission/STORE_COMPLIANCE_AND_DECLARATIONS.md`](file:///c:/JISR%20ARABIC/docs/store_submission/STORE_COMPLIANCE_AND_DECLARATIONS.md)
   - Google Play Data Safety, Families policy questionnaire, Android permission justifications, Apple Nutrition Labels, and IARC ratings.

