// Universal Audio & Speech Recognition Engine (Section 11 Compliance)
import { authenticatedFetch, API_BASE } from './api';

export type PlaybackSpeed = 1.0 | 0.6 | 0.3;
export type RepeatCount = 1 | 2 | 3;

class AudioManager {
  private currentUtterance: SpeechSynthesisUtterance | null = null;
  private currentAudio: HTMLAudioElement | null = null;
  private isPlaying: boolean = false;
  private pendingRepeats: number = 0;
  private currentText: string = "";
  // Normal (1.0x) is the default playback speed
  private speed: PlaybackSpeed = 1.0;
  private targetRepeats: RepeatCount = 1;
  private selectedVoice: SpeechSynthesisVoice | null = null;
  private availableVoices: SpeechSynthesisVoice[] = [];
  private listeners: Set<(state: { isPlaying: boolean; text: string; activeWord: string }) => void> = new Set();
  private activeWord: string = "";
  // Monotonically increasing playback token to cancel prior in-flight requests and avoid double voice
  private activePlaybackId: number = 0;

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.loadVoices();
      window.speechSynthesis.onvoiceschanged = () => this.loadVoices();
    }
  }

  private loadVoices() {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;
    const voices = window.speechSynthesis.getVoices();
    // Filter for Arabic voices across all browsers and operating systems
    this.availableVoices = voices.filter(v =>
      /^ar([_-]|$)/i.test(v.lang) ||
      /arabic|العربية|hoda|hamed|fatima|salma|naayf|shakir|maged|tarik|laila|mariam/i.test(v.name)
    );
    if (this.availableVoices.length > 0 && !this.selectedVoice) {
      // Prioritize Saudi, UAE, or Google Arabic voice
      const googleAr = this.availableVoices.find(v => /google/i.test(v.name) && /^ar/i.test(v.lang));
      const saudi = this.availableVoices.find(v => /ar[-_]SA/i.test(v.lang));
      const uae = this.availableVoices.find(v => /ar[-_]AE/i.test(v.lang));
      this.selectedVoice = googleAr || saudi || uae || this.availableVoices[0];
    }
  }

  public getVoices(): SpeechSynthesisVoice[] {
    return this.availableVoices;
  }

  public setVoice(voice: SpeechSynthesisVoice) {
    this.selectedVoice = voice;
  }

  public setSpeed(speed: PlaybackSpeed) {
    this.speed = speed;
  }

  public setRepeats(count: RepeatCount) {
    this.targetRepeats = count;
  }

  public subscribe(cb: (state: { isPlaying: boolean; text: string; activeWord: string }) => void) {
    this.listeners.add(cb);
    return () => {
      this.listeners.delete(cb);
    };
  }

  private notify() {
    for (const listener of this.listeners) {
      listener({
        isPlaying: this.isPlaying,
        text: this.currentText,
        activeWord: this.activeWord
      });
    }
  }

  public stop() {
    // Invalidate any in-flight async synthesize calls so they cannot start playing
    this.activePlaybackId++;

    if (this.currentAudio) {
      // Disconnect all event listeners before pausing to prevent ghost callbacks
      this.currentAudio.onended = null;
      this.currentAudio.onerror = null;
      this.currentAudio.onplay = null;
      try {
        this.currentAudio.pause();
        this.currentAudio.currentTime = 0;
        this.currentAudio.src = '';
      } catch (e) {
        // Ignore audio pause errors
      }
      this.currentAudio = null;
    }

    if (this.currentUtterance) {
      this.currentUtterance.onend = null;
      this.currentUtterance.onerror = null;
      this.currentUtterance.onboundary = null;
      this.currentUtterance = null;
    }

    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.pendingRepeats = 0;
      try {
        window.speechSynthesis.cancel();
      } catch (e) {}
    }

    this.isPlaying = false;
    this.activeWord = "";
    this.notify();
  }

  public async playArabic(text: string, options?: { speed?: PlaybackSpeed; repeats?: RepeatCount }) {
    if (!text || typeof text !== 'string' || !text.trim()) {
      return;
    }

    // Stop any currently playing audio completely
    this.stop();

    const playbackId = this.activePlaybackId;
    const speed = options?.speed ?? this.speed;
    const repeats = options?.repeats ?? this.targetRepeats;

    this.currentText = text;
    this.pendingRepeats = repeats;
    this.isPlaying = true;
    this.activeWord = text.split(/\s+/)[0] || text;
    this.notify();

    // Level 1/2: use a pre-generated or server-provided audio asset when available.
    try {
      const synthesizeUrl = `${API_BASE}/api/audio/synthesize?text=${encodeURIComponent(text)}&speed=${speed}&lang=${encodeURIComponent(this.selectedVoice?.lang || 'ar-SA')}`;
      const response = await authenticatedFetch(synthesizeUrl);

      // Discard if superseded while fetching
      if (playbackId !== this.activePlaybackId) {
        return;
      }

      if (response.ok) {
        const metadata = await response.json();

        // Discard if superseded while parsing JSON
        if (playbackId !== this.activePlaybackId) {
          return;
        }

        if (metadata.audio_url) {
          const fullAudioUrl = metadata.audio_url.startsWith('http')
            ? metadata.audio_url
            : `${API_BASE}${metadata.audio_url}`;
          const audio = new Audio(fullAudioUrl);
          this.currentAudio = audio;
          audio.playbackRate = speed;

          audio.onended = () => {
            if (playbackId !== this.activePlaybackId) return;
            this.pendingRepeats -= 1;
            if (this.pendingRepeats > 0 && this.isPlaying) {
              audio.currentTime = 0;
              audio.play().catch(() => {});
            } else {
              this.isPlaying = false;
              this.currentAudio = null;
              this.activeWord = "";
              this.notify();
            }
          };

          audio.onerror = () => {
            // Only fallback if this specific playback is still the active one
            if (playbackId !== this.activePlaybackId) return;
            this.fallbackToBrowserSpeech(text, speed, playbackId);
          };

          try {
            await audio.play();
            return;
          } catch (autoplayErr: any) {
            // An AbortError means the play was intentionally interrupted or stopped.
            // DO NOT fall back to browser speech on AbortError to prevent double-voice echo.
            if (autoplayErr?.name === 'AbortError' || playbackId !== this.activePlaybackId) {
              return;
            }
            console.warn("[AudioManager] Autoplay blocked, attempting browser speech fallback:", autoplayErr);
            if (playbackId === this.activePlaybackId) {
              this.fallbackToBrowserSpeech(text, speed, playbackId);
            }
            return;
          }
        }
      }
    } catch (err) {
      if (playbackId !== this.activePlaybackId) return;
      console.warn("[AudioManager] Server audio synthesis error, using fallback:", err);
    }

    if (playbackId === this.activePlaybackId) {
      this.fallbackToBrowserSpeech(text, speed, playbackId);
    }
  }

  private fallbackToBrowserSpeech(text: string, speed: number, playbackId: number) {
    if (playbackId !== this.activePlaybackId) return;

    // Verify an authentic Arabic voice is available before using SpeechSynthesis.
    const hasArabicVoice = Boolean(
      this.selectedVoice ||
      this.availableVoices.some(v => /^ar([_-]|$)/i.test(v.lang) || /arabic|العربية|hoda|hamed|fatima|salma|naayf|shakir/i.test(v.name))
    );

    if (!hasArabicVoice) {
      console.warn("[AudioManager] No Arabic voice installed in browser SpeechSynthesis. Suppressing English TTS to prevent reading only numbers.");
      this.isPlaying = false;
      this.activeWord = "";
      this.notify();
      return;
    }

    this.speakOnce(text, speed, playbackId);
  }

  private speakOnce(text: string, speed: number, playbackId: number) {
    if (playbackId !== this.activePlaybackId) return;

    if (!text || typeof text !== 'string') {
      this.isPlaying = false;
      this.activeWord = "";
      this.notify();
      return;
    }
    const fluentText = text.replace(/\s+/g, ' ').trim();
    if (!fluentText) {
      this.isPlaying = false;
      this.activeWord = "";
      this.notify();
      return;
    }

    // Cancel any active utterance before starting a new one
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
      } catch (e) {}
    }

    const utterance = new SpeechSynthesisUtterance(fluentText);
    utterance.rate = speed;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    utterance.lang = this.selectedVoice ? this.selectedVoice.lang : "ar-SA";
    if (this.selectedVoice) {
      utterance.voice = this.selectedVoice;
    }

    // Word boundary tracking for legitimate highlighting
    utterance.onboundary = (event) => {
      if (playbackId !== this.activePlaybackId) return;
      if (event.name === 'word') {
        const word = fluentText.substr(event.charIndex, event.charLength || 10).split(/\s+/)[0];
        this.activeWord = word;
        this.notify();
      }
    };

    utterance.onend = () => {
      if (playbackId !== this.activePlaybackId) return;
      this.pendingRepeats -= 1;
      if (this.pendingRepeats > 0) {
        setTimeout(() => {
          if (this.isPlaying && playbackId === this.activePlaybackId) {
            this.speakOnce(text, speed, playbackId);
          }
        }, 400);
      } else {
        this.isPlaying = false;
        this.activeWord = "";
        this.notify();
      }
    };

    utterance.onerror = (e) => {
      if (playbackId !== this.activePlaybackId) return;
      console.error("Audio playback error:", e);
      this.isPlaying = false;
      this.activeWord = "";
      this.notify();
    };

    this.currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
  }
}

export const audioManager = new AudioManager();

// Speech Recognition / STT Helper
export class SpeechRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private audioUrl: string | null = null;
  private recognition: any = null;

  constructor() {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.lang = 'ar-SA';
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
      }
    }
  }

  public async startRecording(onTranscript?: (transcript: string) => void): Promise<boolean> {
    try {
      this.audioChunks = [];
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);
      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) this.audioChunks.push(e.data);
      };
      this.mediaRecorder.start();

      if (this.recognition && onTranscript) {
        this.recognition.onresult = (event: any) => {
          const text = event.results[0][0].transcript;
          onTranscript(text);
        };
        try {
          this.recognition.start();
        } catch (e) {
          // Already active
        }
      }
      return true;
    } catch (err) {
      console.warn("Microphone access denied or unavailable", err);
      return false;
    }
  }

  public stopRecording(): Promise<string | null> {
    return new Promise((resolve) => {
      if (this.recognition) {
        try {
          this.recognition.stop();
        } catch (e) {}
      }

      if (!this.mediaRecorder) {
        resolve(null);
        return;
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        this.audioUrl = URL.createObjectURL(audioBlob);
        resolve(this.audioUrl);
      };

      this.mediaRecorder.stop();
    });
  }

  public getAudioUrl(): string | null {
    return this.audioUrl;
  }
}
