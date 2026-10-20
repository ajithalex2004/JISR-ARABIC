/**
 * First sign-in on a device: check the device can type and speak Arabic, and guide the student
 * to turn it on in the device settings when it can't.
 *
 * - Arabic voice: detected from the browser's speech voices (the app falls back to the online
 *   voice, so this is recommended rather than required).
 * - Arabic keyboard: browsers can't list installed keyboards, so the student types a letter in a
 *   test box; Arabic characters arriving there prove the keyboard works.
 * Mirrors mobile/lib/arabic_setup.dart.
 */
import { audioManager } from './audio';

export type Platform = 'windows' | 'mac' | 'chromeos' | 'android' | 'ios' | 'linux' | 'other';

/** Dispatched on window to open the setup again (Profile → Arabic keyboard & voice). */
export const OPEN_ARABIC_SETUP_EVENT = 'jisr:open-arabic-setup';

const DONE_KEY = 'jisr_arabic_setup_done';
const SNOOZE_KEY = 'jisr_arabic_setup_snooze_until';
const SNOOZE_DAYS = 3;
const ARABIC_LETTER = /[ء-ي]/;

export const typedArabic = (text: string) => ARABIC_LETTER.test(text);

export function detectPlatform(ua = navigator.userAgent, maxTouchPoints = navigator.maxTouchPoints || 0): Platform {
  if (/android/i.test(ua)) return 'android';
  // iPadOS reports itself as a Mac with a touch screen.
  if (/iphone|ipad|ipod/i.test(ua) || (/macintosh/i.test(ua) && maxTouchPoints > 1)) return 'ios';
  if (/cros/i.test(ua)) return 'chromeos';
  if (/windows/i.test(ua)) return 'windows';
  if (/macintosh|mac os x/i.test(ua)) return 'mac';
  if (/linux/i.test(ua)) return 'linux';
  return 'other';
}

/** Whether the device has an Arabic speech voice; voices load late in some browsers, so wait a little. */
export async function hasArabicVoice(waitMs = 1500): Promise<boolean> {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return false;
  const deadline = Date.now() + waitMs;
  while (Date.now() < deadline) {
    if (audioManager.getVoices().length) return true;
    await new Promise(resolve => setTimeout(resolve, 150));
  }
  return audioManager.getVoices().length > 0;
}

const storage = {
  get: (key: string) => { try { return localStorage.getItem(key); } catch { return null; } },
  set: (key: string, value: string) => { try { localStorage.setItem(key, value); } catch { /* private mode */ } },
};

/** Show the check on this device: never finished here, and not put off recently. */
export function shouldOfferArabicSetup(now = Date.now()): boolean {
  if (storage.get(DONE_KEY)) return false;
  const snoozed = Number(storage.get(SNOOZE_KEY) || 0);
  return !(snoozed && now < snoozed);
}

export const markArabicSetupDone = () => storage.set(DONE_KEY, new Date().toISOString());
export const snoozeArabicSetup = (now = Date.now()) => storage.set(SNOOZE_KEY, String(now + SNOOZE_DAYS * 86400000));

export type Guide = { name: string; keyboard: string[]; switchKeys: string; voice: string[] };

export const GUIDES: Record<Platform, Guide> = {
  windows: {
    name: 'Windows',
    keyboard: [
      'Open Start → Settings → Time & language → Language & region.',
      'Next to "Preferred languages", click Add a language.',
      'Search for Arabic, pick a country (e.g. Arabic (United Arab Emirates)), then Next → Install.',
    ],
    switchKeys: 'Press Windows key + Space to switch between English and Arabic (ENG / عربي shows on the taskbar).',
    voice: [
      'Open Start → Settings → Time & language → Language & region, click ⋯ next to Arabic → Language options.',
      'Under "Speech", click Download, then restart your browser.',
    ],
  },
  mac: {
    name: 'Mac',
    keyboard: [
      'Open Apple menu → System Settings → Keyboard.',
      'Under "Text Input", click Edit… then the + button.',
      'Choose Arabic → Arabic (or Arabic – PC) and click Add.',
    ],
    switchKeys: 'Press Control + Space, or the 🌐 globe key, to switch to Arabic.',
    voice: [
      'Open System Settings → Accessibility → Spoken Content.',
      'Click the ⓘ next to System voice → Voices, find Arabic and download a voice (e.g. Majed).',
    ],
  },
  chromeos: {
    name: 'Chromebook',
    keyboard: [
      'Open Settings → Device → Keyboard and inputs → Input methods (or Advanced → Languages and inputs → Inputs).',
      'Click Add input methods, search for Arabic, tick it and click Add.',
    ],
    switchKeys: 'Press Ctrl + Space to switch to the Arabic keyboard.',
    voice: [
      'Open Settings → Accessibility → Text-to-Speech → Text-to-Speech voice settings.',
      'Set the preferred voice for Arabic (Google voices download automatically).',
    ],
  },
  android: {
    name: 'Android',
    keyboard: [
      'Open Settings → System → Languages & input → On-screen keyboard → Gboard → Languages.',
      'Tap Add keyboard, choose Arabic, then Done.',
    ],
    switchKeys: 'On the keyboard, tap the 🌐 globe key (or hold the space bar) to switch to Arabic.',
    voice: [
      'Open Settings → System → Languages & input → Text-to-speech output.',
      'Tap ⚙ next to Speech Services by Google → Install voice data → Arabic, and download it.',
    ],
  },
  ios: {
    name: 'iPhone / iPad',
    keyboard: [
      'Open Settings → General → Keyboard → Keyboards.',
      'Tap Add New Keyboard… and choose Arabic.',
    ],
    switchKeys: 'On the keyboard, tap the 🌐 globe key to switch to Arabic.',
    voice: [
      'Open Settings → Accessibility → Spoken Content → Voices.',
      'Tap Arabic and download a voice (e.g. Majed).',
    ],
  },
  linux: {
    name: 'Linux',
    keyboard: [
      'Open Settings → Keyboard → Input Sources.',
      'Click + (Add Input Source), choose Arabic and click Add.',
    ],
    switchKeys: 'Press Super + Space to switch to Arabic.',
    voice: ['Install an Arabic voice for your speech engine (e.g. espeak-ng with Arabic), then restart your browser.'],
  },
  other: {
    name: 'your device',
    keyboard: ["Open your device's settings → Language / Keyboard, and add the Arabic keyboard."],
    switchKeys: 'Use the keyboard switch key (often 🌐 or Ctrl/Win + Space) to change to Arabic.',
    voice: ["Open your device's settings → Text-to-speech or Spoken content, and add an Arabic voice."],
  },
};
