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

## Version 2: new voiceover

`jisr-script1-v2-homework-1080x1920.mp4`: 49 s, 1080 x 1920, 30 fps, H.264 + AAC, -14.6 LUFS.
The same app recordings as version 1, re-timed to a longer, warmer voiceover.

| Time | Section (delivery) | Scene | Voiceover | Caption |
| --- | --- | --- | --- | --- |
| 0:00 | Hook (frustrated, humorous) | Arabic worksheet, slow zoom | Arabic homework again? Oh no… I can barely read Arabic myself! | Arabic homework again? Oh no… |
| 0:05 | Problem (genuine parental frustration) | Worksheet | We've been living in the UAE for eight years, and helping with Arabic homework is still a challenge. | 8 years in the UAE. Still a challenge. |
| 0:10 | Discovery (pleasantly surprised) | Class 5 "Ball Games" lesson opens | Then I discovered JISR Arabic. / It's designed around CBSE Arabic lessons. | Then I discovered JISR Arabic / Designed around CBSE Arabic lessons |
| 0:16 | Features (clear, confident) | Tap الكُرَةُ: meaning and the app's audio | Just tap any word to discover its English meaning. | Tap any word for its English meaning |
| 0:21 | Features | Slow 0.6x replay | Need help with pronunciation? It reads the words aloud, and you can slow it down. | It reads words aloud. You can slow it down |
| 0:28 | Features | Sentence drill with English beneath | And the best part? Every sentence comes with an English translation. | Every sentence comes with an English translation |
| 0:38 | Payoff (relieved, happy) | Lesson screen | Now my child's Arabic homework doesn't feel like a daily struggle anymore! | No more daily homework struggle |
| 0:43 | Call to action (friendly) | End card: Only 10 USD, app.jisrarabic.com | All this for just $10. / Give JISR Arabic a try. Link in bio! | (end card) |

Voiceover: Piper TTS, en_GB-cori-high. Each line's delivery is set in `source/lines_v3.json`:
speaking rate, then expressiveness (`[text, length_scale, noise_scale, noise_w]`). It's a
computer voice, so the emotion is mild. A creator's recording can replace the audio track
without re-timing, because every line keeps its start time (the table above).

Rebuilding: render the captions with `source/render_ov_v3.js` (from `overlays_v3.html`),
generate each line of `lines_v3.json` with Piper into `vo3/`, then run `python3 build_v3.py`
next to the version 1 recordings (`shots2/`, `aud/`).
