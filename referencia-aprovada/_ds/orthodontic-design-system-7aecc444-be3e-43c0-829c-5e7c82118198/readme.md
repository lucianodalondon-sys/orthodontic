# OrthoDontic — Design System

A brand-faithful design system for **OrthoDontic** (OrthoDontic Brasil), reconstructed from the official *Manual de Marca — OrthoDontic* (21-page brand book, 16:9). It ships the brand's colors, typography, logo assets, motifs, reusable UI components, and full-screen product recreations so designers and agents can produce on-brand interfaces and marketing without re-deriving the brand each time.

> **Everything here traces back to the manual.** Where the manual is silent (UI primitives, motion, status colors) the system makes brand-consistent decisions and flags them as *additions*. Nothing about the real logo or wordmark was drawn from memory — all logo assets were extracted directly from the source PDF.

---

## 1. Brand & product context

**OrthoDontic** is a large Brazilian orthodontics clinic network. Its promise is an accessible, caring, modern path to a better smile — *"Viva o seu **MELHOR SORRISO** com quem mais entende de ortodontia"* ("Live your best smile, with those who understand orthodontics most").

Signals pulled from the manual:
- **Category:** orthodontics / dental clinics (braces, retainers, treatment plans).
- **Market:** Brazil. Language is **Brazilian Portuguese**. Web: `orthodonticbrasil.com.br`. Social: `@orthodontic.br`.
- **Scale / proof:** *"Mais de 8 milhões de sorrisos conquistados"* (8M+ smiles).
- **Products & surfaces represented:**
  - **Marketing / campaign** — annual "Key Visual" (KV) campaigns built around the *MELHOR SORRISO / SORRINDO* idea, run as landing pages and out-of-home style hero visuals featuring a **celebrity ambassador** and real patients.
  - **Social media** (`@orthodontic.br`) — square/vertical educational + promotional posts.
  - **Mobile app** — *"Sua rotina ortodôntica na palma da mão"*: patients track their treatment, appointments and progress.
- **Personality:** confident, warm, encouraging, modern, trustworthy, a little playful.

### Sources
- `uploads/manual-marca-orthodontic-26 2.pdf` — the official 21-page brand manual (vector PDF, all artwork outlined). This is the sole source. Page references in this repo (e.g. "p.07") point to it.
- Page renders used during reconstruction are archived in `scraps/` (`01-pg.png` … `21-pg.png`) for reference; they are not shipped assets.
- No codebase, Figma file, or live site was provided. The manual does **not** define a UI component inventory — see §7.

---

## 2. Content fundamentals — how OrthoDontic writes

**Language.** Brazilian Portuguese. Marketing copy addresses the reader as **"você"** (informal, warm, direct) — it speaks *to* one person about *their* smile, never in corporate third person.

**Voice.** Encouraging, reassuring, aspirational, human. It sells confidence and care, not clinical detail. Recurring reassurance themes appear as short benefit chips:
- *Profissionais de confiança* · *Preço que cabe no seu bolso* · *Cuidado com carinho* · *Clínicas modernas* · *Tratamentos sob medida*

**Headlines.** Big, uppercase, emotional, short. The hero word is set huge and often in a campaign accent color, with a tooth glyph swapped into a letter:
- **"MELHOR SORRISO"**, **"SORRINDO"**, **"NA PALMA DA MÃO"**

**Body / support copy.** Sentence case, calm, benefit-led. Emphasis is created by **bolding a few words mid-sentence** rather than by punctuation or caps:
- *"cada mudança é cada versão de quem você se torna"* · *"podem **conter** o endereço do site"*

**Engagement devices.** Rhetorical questions (*"Você sabe a importância da contenção ortodôntica?"*) and friendly imperative CTAs: **Saiba Mais**, **Agende sua avaliação**, **Confira a legenda**.

**Reactions / emoji.** Used *sparingly and only in social/campaign* — 5-star ratings ★★★★★, hearts, thumbs-up, and smiley reactions attached to benefit bubbles. Never in the guideline/formal voice.

**The manual's own voice** (i.e. brand-guideline copy) is formal and instructional: *"Existe uma distância mínima entre a marca e qualquer elemento…"*, *"O uso dissociado destes elementos é proibido, exceto em casos especiais."* Use this register for documentation, not for customer-facing copy.

**Casing & punctuation quick-reference**
- Eyebrows / section labels: `UPPERCASE` with wide tracking (e.g. `CÓDIGO DE CORES`).
- Hero headlines: `UPPERCASE`, tight tracking, black weight.
- Buttons: Title Case or sentence case ("Saiba Mais", "Agende sua avaliação").
- Body: sentence case; bold for emphasis, not italics.

---

## 3. Visual foundations

### Color
A **blue-dominant** world. Two primaries carry the brand; secondaries and campaign accents add warmth and energy.
- **Primary cyan `#00B9FF`** (Pantone 298 C) — the signature. Fills the symbol disc, backgrounds, links, primary CTAs.
- **Primary navy `#001E78`** (Pantone 287 C) — the anchor. Headings, the "ORTHO" of the wordmark, dark surfaces, gradient ends.
- **Secondaries (p.07):** gray `#706F6E`, warm cream `#FEF6F2`, teal `#36767E`, pale sky `#DFEAF8`, orange `#F5A057`, soft pink `#E885B0`.
- **Campaign accents (sampled from KVs, approximate):** magenta `#E8408D`, golden yellow `#F8D65D`, bright teal `#46BBC2`, purple `#5B4B9A`. These power the *SORRISO* hero word and CTA buttons and rotate per campaign.
- Full tokens + exact CMYK/Pantone/RGB in `tokens/colors.css` and the Colors cards.

### Typography
- **Gotham** is the brand typeface (p.06): *Light, Book, Bold, Black*. The licensed Gotham files were supplied by the brand and ship with this system (`assets/fonts/`, weights 300/400/500/700/900).
- **Display / headlines:** Black (900), UPPERCASE, tight tracking, tight leading. Big and confident.
- **Body:** Book/Light (400/300), sentence case, comfortable leading, muted-navy or gray ink.
- **Labels / eyebrows:** Bold (700), UPPERCASE, wide letter-spacing.

### Spacing & layout
- 4px base grid; **generous, airy** spacing (the manual breathes — lots of whitespace around the mark and headlines).
- Content max ~1200px; narrow reading column ~760px.
- Logo rules: horizontal lock-up is **preferred**; vertical only for tall formats (≥3:1). Clear space = the cap-height "X" of the mark on all sides. Minimum size 2.2 cm (horizontal) / 1.5 cm (vertical). The website URL may sit under the mark.

### Backgrounds
- Solid **cyan** or **navy** blocks; white and **cream** for content.
- **Blue gradients** (cyan → navy) are the campaign signature (`--grad-hero`).
- The **concentric-ring motif** — echoing the symbol — decorates covers and closers as large white rings (solid + thin outline) bleeding off a cyan field (`--rings-white`).
- **Photography** in campaigns: real, diverse people mid-smile showing braces; bright, high-key, optimistic; cool blue tint; clean, modern clinic environments. Often overlaid with glassy benefit bubbles.

### Elevation, borders & glass
- **Shadows are navy-tinted**, never neutral gray — soft and diffuse (`--shadow-sm/md/lg`). Elevation feels like part of the blue world.
- **Cyan glow** (`--shadow-cyan`) is reserved for primary CTAs, focus and active states.
- **Borders:** hairline, cool `#DCE6F2`. Focus = 3px cyan ring.
- **Glass:** campaign benefit bubbles are translucent white (`rgba(255,255,255,.72)`) with backdrop blur and a soft border — they float over photography with a tiny "✕" affordance and, often, a star rating or emoji reaction row.

### Corner radii
Rounded and friendly throughout. **Pill** CTAs (`999px`), **16px** default cards, **22px** glassy bubbles / KV cards, **circle** for the symbol and avatars. Sharp corners are off-brand.

### Cards
White surface, `--radius-md` (16px), soft navy-tinted shadow, thin or no border. The **campaign "bubble"** variant is glassy, `--radius-lg` (22px), floats over imagery, and pairs with a rating or reaction.

### Motion (defined by this system — not in the manual)
- Friendly and energetic. Entrances **ease-out** and fade/slide up; playful elements (bubbles, reactions, CTAs) use a **light bounce** (`--ease-bounce`).
- **Hover:** cyan darkens to `--od-cyan-600`, surfaces lift (raise shadow); links go navy + underline.
- **Press:** gentle shrink (`scale(0.97)`).
- Durations 120–360ms. No harsh, robotic, or infinite decorative motion. Respect `prefers-reduced-motion`.

---

## 4. Iconography

The manual defines **no formal icon library**. What it *does* establish:
- **The brand symbol** — a cyan disc containing a stylized open smile with **braces** (bracket + wire on white teeth). This is the hero icon; it is an asset (`assets/logos/symbol*.png`), never re-drawn.
- **A tooth glyph** integrated into campaign headlines (swapped into a letter of *SORRISO / SORRINDO*).
- **Star ratings** (★★★★★), and **emoji reactions** (hearts, thumbs-up, smileys) in social/campaign only.
- **QR codes** and simple functional glyphs (search, close "✕", cursor) in mocked UI.

**Chosen UI icon set (addition, flagged):** **[Lucide](https://lucide.dev)** — rounded-cap, medium-stroke line icons that match the brand's friendly, modern feel. Load from CDN (`https://unpkg.com/lucide@latest`) and call `lucide.createIcons()`, or use the bundled **`Icon`** component, which embeds a common subset (search, check, x, chevrons, star, heart, calendar, phone, menu, arrow-right, plus, user, bell, camera…). Swap for a licensed/branded set if one is later provided. Emoji are acceptable **only** for social/campaign reactions, matching the source.

---

## 5. Logo & assets (`assets/`)

All logo files were extracted directly from the manual (vector PDF → high-res raster, backgrounds keyed to transparency). Do not redraw or recolor them.

`assets/logos/`
- `logo-horizontal.png` — full-color horizontal lock-up (symbol + wordmark). **Preferred.**
- `logo-vertical.png` — full-color vertical lock-up (symbol above wordmark).
- `symbol.png` — the braces-smile disc, full color, transparent corners.
- `logo-horizontal-white.png` — all-white lock-up for dark / photo backgrounds (transparent).
- `symbol-white.png` — all-white symbol for dark backgrounds (transparent).

`assets/fonts/` — Gotham (the brand typeface), weights 300 Light · 400 Book · 500 Medium · 700 Bold · 900 Black. Montserrat is retained only as a stack fallback.

> **Missing:** navy-monochrome and grayscale one-color lock-ups (shown on manual p.09/p.12–15) were not extracted — request if needed. The full-color + white set covers light, dark, and photographic surfaces.

---

## 6. Typography — Gotham (brand font shipped)

The brand typeface **Gotham** (manual p.06) ships with this system — the licensed files were supplied by the brand. `fonts.css` maps: **300** Light · **400** Book · **500** Medium · **700** Bold · **900** Black. Everything reads `var(--font-sans)` / `var(--font-display)`, so `900` powers display headlines and `400`/`300` handle body. **Montserrat** stays in the font stack as a graceful fallback only.

> Weights `600`/`800` referenced by tokens fall to the nearest shipped Gotham face. Add the matching Gotham files + `@font-face` rules if you need them exact.

---

## 7. Components — intentional additions

The manual is a **brand book, not a UI kit**: it defines no buttons, inputs, or components. Per design-system convention, this project therefore authors a **standard UI set**, styled entirely to OrthoDontic (pill CTAs, cyan/navy, Montserrat, navy-tinted elevation), plus a few **brand-observed** primitives. All of the following are additions, not source-defined:

- **Standard set:** Button, IconButton, Input, Select, Checkbox, Radio, Switch, Card, Badge, Tag, Tabs, Dialog, Toast, Tooltip.
- **Brand-observed:** **Rating** (5-star, from campaign proof), **Bubble** (glassy chat-callout, from KV benefit bubbles), **Logo** (utility wrapper over the extracted assets), **Icon** (Lucide wrapper).
- **Functional status colors** (`--color-success / warning / danger`) are added for real UI needs; only cyan/navy/secondaries are from the manual.

See each component's `.prompt.md` for usage. Components live under `components/<group>/` and compile into `window.OrthoDonticDesignSystem_7aecc4`.

---

## 8. Index / manifest

**Foundations**
- `styles.css` — global entry point (import list only). Consumers link this.
- `fonts.css` — `@font-face` (Gotham, the brand typeface).
- `tokens/` — `colors.css` · `typography.css` · `spacing.css` · `radii.css` · `shadows.css` · `motion.css` · `gradients.css` · `base.css`.
- `guidelines/*.card.html` — foundation specimen cards (Type, Colors, Spacing, Brand).

**Components** (`components/<group>/` — `.jsx` + `.d.ts` + `.prompt.md` + one `@dsCard` HTML each)
- `actions/` — Button, IconButton
- `forms/` — Input, Select, Checkbox, Radio, Switch
- `content/` — Card, Badge, Tag, Rating, Bubble
- `feedback/` — Dialog, Toast, Tooltip
- `navigation/` — Tabs
- `brand/` — Logo, Icon

**UI kits** (`ui_kits/<product>/` — `index.html` + screen `.jsx`)
- `marketing/` — campaign landing page (MELHOR SORRISO KV).
- `app/` — mobile treatment-tracking app.

**Meta**
- `readme.md` — this file. · `SKILL.md` — Agent-Skill wrapper.
- Generated (do not edit): `_ds_bundle.js`, `_ds_manifest.json`, `_adherence.oxlintrc.json`.

---

## 9. Caveats
- **Campaign accent hexes** (magenta/yellow/teal/purple) are sampled from KV pages and are approximate; the primary + secondary palette (p.07) is exact.
- Campaign **photography and the celebrity ambassador** are not shipped (likeness/rights). UI kits use styled placeholders; supply real approved imagery for production.
- Navy-mono / grayscale logo lock-ups not extracted (§5).
