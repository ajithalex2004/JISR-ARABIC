# JISR Arabic UGC video templates

Overlays and an end card for the creator videos (9:16, 1080 x 1920).

| File (in `export/`) | Use | Background |
| --- | --- | --- |
| `jisr-endcard-1080x1920.png` | Last 2 s of every video | Solid |
| `jisr-hook-1080x1920.png` | Hook caption, top, 0 to 3 s | Transparent |
| `jisr-subtitle-1080x1920.png` | Spoken subtitle style, lower third | Transparent |
| `jisr-wordcard-1080x1920.png` | Arabic word with English letters and meaning | Transparent |
| `jisr-chip-emerald-1080x1920.png` / `jisr-chip-gold-1080x1920.png` | Feature label | Transparent |
| `jisr-tag-1080x1920.png` | Brand tag, top right, whole video | Transparent |
| `jisr-guide-1080x1920.png` | Safe zones, for editors only; never export into a video | Solid |

Place each overlay full-frame at 0,0; positions are already set.

## Changing the text

Edit `source/templates.html` (one `<section>` per template), then render:

```bash
node marketing/ugc/source/render.js
```

Rendering needs Playwright and Chromium. Fonts load from Google Fonts (Inter, Amiri).
