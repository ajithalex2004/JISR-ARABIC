# Script 3: Tap. Hear. Understand. (screen-only, for paid ads)

The real app in a phone frame on the brand background; captions sit above the phone so they
never cover the Arabic. The soundtrack is the app's own word and sentence audio; there is no
voiceover or music (add the platform's sound in the ad editor if wanted).

| File | Class | Length |
| --- | --- | --- |
| `jisr-script3-class2-1080x1920.mp4` / `-short-` | Class 2, free lesson "My Friend and I at School" | 20 s / 9 s |
| `jisr-script3-class5-1080x1920.mp4` / `-short-` | Class 5, free lesson "Ball Games" | 23 s / 11 s |
| `jisr-script3-class8-1080x1920.mp4` / `-short-` | Class 8, free lesson "Al-Mutanabbi" | 24 s / 11 s |

| Scene | Caption |
| --- | --- |
| Tap the first vocabulary word: meaning popup and its audio | Can you read this? / Now you can. |
| Tap two words of the example sentence | Tap any word. Hear it. |
| Play the example sentence: each word lights up, English underneath | Your Class N child's CBSE Arabic, in English. |
| Slow 0.6x, the word replayed slowly | Slow it down. |
| Sentence builder: tiles in order, Check, "Great job!" | Build the sentence. |
| End card | Only 10 USD · app.jisrarabic.com |

The short cuts are the first scene, the sentence scene and the end card.

## Rebuilding (source/)

1. Run `npm run dev` in `frontend/`. `record.js <grade>` records the local app; its `/api` calls
   are answered from the production API once and cached (`common.js`).
2. `node cap/render.js` renders the backdrop, phone mask and captions from `cap/s3.html`.
3. `python3 build.py 2 5 8` places the app audio by the logged tap times and builds every version.
