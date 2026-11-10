# Script 1: The 9pm Arabic homework panic (screen-only version)

`jisr-script1-homework-panic-1080x1920.mp4`: 35 s, 1080 x 1920, 30 fps, H.264 + AAC, -14 LUFS.

| Time | Scene | Voiceover |
| --- | --- | --- |
| 0:00 | Arabic worksheet (designed, not a textbook scan) | When the homework is in Arabic... and you're not. / Eight years in the UAE, and I still can't read this. |
| 0:07 | Class 5 "Ball Games" lesson opens | Then I found JISR Arabic, with his CBSE lessons. |
| 0:11 | Tap الكُرَةُ: meaning popup and the app's own audio | Tap any word, and it tells you what it means. |
| 0:16 | Slow 0.6x, word replayed slowly | It reads it out, and you can slow it down. |
| 0:22 | Sentence drill, words highlight as it plays, English beneath | Every sentence comes with the English. / Homework time is calm again. |
| 0:32 | End card | Only ten dollars. Link in bio. |

App scenes are real recordings of the free Class 5 lesson as a guest. Three internal labels
("INTERACTIVE DEMO ACTIVE", the version tag, the "Term 1" line) are hidden on screen.
Voiceover: Piper TTS, voice en_GB-cori-high. No music, so an editor can add a platform sound.

## Rebuilding (source/)

1. Run the backend and `npm run dev` in `frontend/`; `record_v2.js` records the local app and
   answers its `/api` calls from the production API once, caching them in `apicache/`.
2. `render_ov.js` renders the worksheet and captions from `overlays.html`.
3. Generate the voiceover from `lines.json` with Piper, then `python3 build_v2.py`.
