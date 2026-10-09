#!/usr/bin/env bash
# ==============================================================================
# JISR Arabic (فهيم) Mobile Release Packaging Script (Linux / macOS / CI)
# ==============================================================================
set -euo pipefail

TARGET="${1:-appbundle}"
API_BASE="${2:-https://api.jisr.ae}"
OBFUSCATE="${3:-true}"

echo "=========================================================="
echo "  JISR Arabic Mobile Release Packaging Pipeline"
echo "=========================================================="

# 1. Enforce HTTPS
if [[ ! "$API_BASE" =~ ^https:// ]]; then
  echo "SECURITY ERROR: Release builds must use strict HTTPS. Received: '$API_BASE'" >&2
  exit 1
fi
echo "[1/6] Production API Base: $API_BASE"

# 2. Check Flutter Tooling
if ! command -v flutter &>/dev/null; then
  echo "ERROR: 'flutter' command not found on PATH." >&2
  exit 1
fi
echo "[2/6] Flutter Tooling: $(flutter --version | head -n 1)"

# 3. Android Keystore Verification
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MOBILE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$MOBILE_DIR"

if [[ -f "android/key.properties" ]]; then
  echo "[3/6] Android signing: 'key.properties' verified."
else
  echo "[3/6] WARNING: 'android/key.properties' not found. Falling back to debug signing."
fi

# 4. Clean & Dependencies
echo "[4/6] Resolving dependencies and running checks..."
flutter pub get
flutter analyze
flutter test

# 5. Build Artifacts
SYMBOLS_DIR="build/app/outputs/symbols"
OBFUSCATE_ARGS=()
if [[ "$OBFUSCATE" == "true" ]]; then
  mkdir -p "$SYMBOLS_DIR"
  OBFUSCATE_ARGS=("--obfuscate" "--split-debug-info=$SYMBOLS_DIR")
fi

DART_DEFINES=("--dart-define=FAHIM_API_BASE=$API_BASE")

if [[ "$TARGET" == "appbundle" || "$TARGET" == "all" ]]; then
  echo "[5/6] Building Android App Bundle (.aab) for Google Play..."
  flutter build appbundle --release "${DART_DEFINES[@]}" "${OBFUSCATE_ARGS[@]}"
  echo "[SUCCESS] Generated: build/app/outputs/bundle/release/app-release.aab"
fi

if [[ "$TARGET" == "apk" || "$TARGET" == "all" ]]; then
  echo "[5/6] Building Android APK (.apk)..."
  flutter build apk --release "${DART_DEFINES[@]}" "${OBFUSCATE_ARGS[@]}"
  echo "[SUCCESS] Generated: build/app/outputs/flutter-apk/app-release.apk"
fi

if [[ "$TARGET" == "ios" || "$TARGET" == "all" ]]; then
  if [[ "$(uname)" == "Darwin" ]]; then
    echo "[5/6] Building iOS Archive (.ipa) for App Store..."
    flutter build ipa --release "${DART_DEFINES[@]}" "${OBFUSCATE_ARGS[@]}"
    echo "[SUCCESS] iOS build completed."
  else
    echo "[NOTE] iOS builds require macOS. Skipped on $(uname)."
  fi
fi

echo "=========================================================="
echo "  Release Packaging Completed Successfully!"
echo "=========================================================="
