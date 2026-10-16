# JISR Arabic — Experience Concept & Journey Map

## 1. Audit of the current entry experience (before)

| Area | Finding | Impact |
|---|---|---|
| First impression | Cold visitors land inside the student dashboard as "Guest Student", with no story or value proposition | Parents can't tell what JISR is, who it is for, or why to pay |
| Hierarchy | Eight competing badges and toggles above the fold (CBSE badge, audio toggle, Ask Fahim, Arab-English switch, version tag) | No single primary action |
| Responsiveness | 114px of horizontal scroll at 390px; the audio dock covers a third of the mobile screen | Feels unfinished on the device parents use most |
| Typography | Arabic and Latin set at similar weights, transliteration rendered as underlined links | Arabic, the product's hero, doesn't lead |
| Colour | Saturated purple gradients on every card | Nothing stands out because everything does |
| SEO | One generic `<title>`/description, no social cards, no structured data, no sitemap | Invisible in search and in WhatsApp/Instagram shares, which is how UAE parents discover schools' tools |

## 2. Concept: "The Bridge" (جِسْر)

*JISR* means **bridge**. The whole site is built on that one idea: a bridge from the
language a child thinks in to the Arabic they're learning, and from a parent's worry to a
child's confidence.

- **Visual metaphor:** a single hand-drawn arch that draws itself across the hero, joining
  an English word to its Arabic meaning. The same arch is reused as section dividers and
  in the progress journey.
- **Tone:** calm, editorial, premium, closer to a museum catalogue than an ed-tech ad.
  Arabic is always the largest thing on screen.
- **Edges:** square corners and hairline rules, matching the product's existing sharp
  design system so the site and the app feel like one brand.

### Design tokens (landing scope, `.jl`)

| Token | Value | Use |
|---|---|---|
| `--ink` | `#140B22` | Night background, primary text on paper |
| `--plum` | `#58337E` | Brand, matches the app and logo |
| `--violet` | `#8B5CF6` | Glow, focus, interactive accents |
| `--emerald` | `#10B981` | "Learned / success / go" |
| `--gold` | `#E0B04B` | The bridge line, highlights (one accent per screen) |
| `--paper` | `#FBF8F3` | Light section background |
| Display Latin | Inter 800, tracking −0.04em, `clamp(2.6rem, 7vw, 6.5rem)` | Headlines |
| Display Arabic | Amiri 700 | Arabic hero words |
| Body | Inter 400/500, 1.05–1.15rem, line-height 1.6 | Copy |
| Spacing | 8-pt scale; sections `clamp(88px, 12vw, 168px)` vertical | Rhythm |
| Motion | `cubic-bezier(.16,1,.3,1)`; reveals 800ms, micro-interactions 180ms; all disabled under `prefers-reduced-motion` | |

## 3. Journey map: landing → mastery

| # | Stage | Visitor's question | What they see/do | Success signal |
|---|---|---|---|---|
| 1 | **Arrive** (`/`, signed-out) | "What is this?" | Hero: "Arabic, finally understood." The bridge draws from *bridge* to **جِسْر**. Primary CTA *Start free*, secondary *Try a free lesson* | Scrolls or clicks within 5s |
| 2 | **Feel it** | "Does it actually help my child?" | Live word demo: tap any Arabic word to hear it, see transliteration and meaning; the real product interaction | Taps ≥1 word |
| 3 | **Understand** | "How does it work?" | Scroll story (sticky): *The textbook page* → *Line by line, in English* → *Practise until it sticks* | Reaches step 3 |
| 4 | **Trust** | "Is it aligned with school?" | CBSE curriculum, Classes 1–10, three terms; parent dashboard; receipts & UAE tax invoices | Opens curriculum or parent section |
| 5 | **Decide** | "What does it cost?" | Transparent pricing: $10/term, $25.50 full year (15% off), first chapter free, cancel auto-renew anytime | Clicks a plan |
| 6 | **Reassure** | "What if…?" | FAQ (accessible disclosure) | — |
| 7 | **Commit** | — | Final CTA → app opens with sign-up already on screen (`/?auth=signup`) | Account created |
| 8 | **Onboard** (app) | "Where do I start?" | Child profile, class, PIN → catalogue at the right grade | First lesson opened |
| 9 | **Learn** (app) | — | Scanned textbook with line-by-line translation, word audio, Ask Fahim, mindmaps, capsules | Lesson completed |
| 10 | **Unlock** (app) | — | Paywall on chapter 2 → Stripe checkout → receipt + tax invoice | Paid term |
| 11 | **Master** (app) | "Is my child improving?" | Mastery heatmap, ranks & badges, exam simulation, parent progress | Weekly return |

Returning learners and anyone with a session skip stages 1–7 and go straight to the app.
The landing stays available at `/welcome`.

## 4. Build stages (each verified before the next)

1. **Inspect**: framework, hosting, constraints (this document).
2. **Architecture**: a lazy entry gate (`src/entry/Root.tsx`) chooses landing or app, so
   neither bundle pays for the other; deep links, `?payment=`, `#admin` and sessions bypass
   the landing.
3. **Components & sections**: `src/components/landing/*`, one file per section, plain CSS
   in `landing.css` scoped under `.jl`.
4. **Motion system**: `useReveal` (IntersectionObserver), CSS keyframes, the SVG bridge
   stroke-draw, pointer parallax (fine pointers only), sticky scroll story; everything
   honours `prefers-reduced-motion`.
5. **SEO**: titles, description, canonical, Open Graph/Twitter cards, JSON-LD
   (`EducationalOrganization` + `Course` with offers), `robots.txt`, `sitemap.xml`,
   `<noscript>` summary.
6. **Accessibility**: landmarks, skip link, one `h1`, ordered headings, `lang="ar"` on
   Arabic, visible focus rings, ≥44px targets, WCAG AA contrast, keyboard-operable demo,
   native `<details>` FAQ.
7. **Performance**: code-split chunks, font preconnect, SVG/CSS art instead of images,
   no animation library, no raster images.
8. **Test**: Playwright at 375/768/1440, no console errors, no horizontal overflow, CTA
   flows into the app, reduced-motion pass.
9. **Deploy**: PR → CI (5 checks) → merge → Railway → verify the live bundle.
