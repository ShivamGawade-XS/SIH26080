# Design System & Cartographic Guidelines: Project Varsha

**Document Reference:** Varsha Visual Language & Cartography Specification  
**Version:** 1.0.0 (v0 Foundation)

---

## 1. Design Principles & Anti-Template Constraints

Varsha is designed as a **quiet, precise meteorological instrument**, inspired by national weather service operational charts and Swiss data-journalism cartography. Data is the primary visual element.

### Strict Anti-Template Rules (N9 Compliance)
- ❌ **No SaaS gradients:** No purple/indigo background blobs, no gradient text, no glassmorphism, no glow.
- ❌ **No generic cards:** No uniform 2xl rounded cards with soft drop-shadows. Grouping is achieved via 1px hairline borders (`#D8D4CA` / `#2A323A`) and typographic whitespace.
- ❌ **No emoji or decorative iconography:** Text labels are preferred. Any technical glyphs are strictly paired with descriptive text.
- ❌ **No marketing fluff or unearned logos:** No generic hero sections, no fake partner emblems, no fabricated testimonials.
- ❌ **Tabular numbers mandatory:** All numerical metrics and coordinates use `font-variant-numeric: tabular-nums`.

---

## 2. Core Color Tokens

| Token Role | Light Mode (Warm Paper) | Dark Mode (Deep Slate) | Purpose / Context |
|---|---|---|---|
| **Ground (Canvas)** | `#F4F2ED` | `#0F1418` | Base window background |
| **Surface** | `#FBFAF7` | `#151B21` | Panel and table background |
| **Ink (Primary Text)** | `#16191D` | `#E6E3DA` | High-contrast headings and values |
| **Ink-2 (Secondary Text)** | `#555B63` | `#A5ABB2` | Labels, axis annotations, units |
| **Hairline (Borders)** | `#D8D4CA` | `#2A323A` | Crisp 1px structural separators |
| **Accent (Interactive)** | `#0F5C6E` | `#5FB3C4` | Focus rings, selections, active tabs |

*Note: Accent color is reserved exclusively for user interaction state. Data values (rainfall, alerts, regimes) use independent, semantically dedicated palettes.*

---

## 3. Meteorological Color Palettes

### 3.1 IMD Precipitation Scale (Lightness-Monotonic, CVD-Safe)
Classed at official IMD operational precipitation thresholds:

| Rain Category | Range (mm/day) | Hex Code | Lightness / Meaning |
|---|---|---|---|
| **Dry / Trace** | $< 2.5$ | `#EBE8E0` (light) / `#182026` (dark) | Near-background to keep dry areas visually calm |
| **Light Rain** | $2.5 - 15.6$ | `#B5D3CE` | Pale seafoam |
| **Moderate Rain** | $15.6 - 35.5$ | `#6CA2B3` | Muted slate blue |
| **Rather Heavy** | $35.5 - 64.5$ | `#367794` | Medium oceanic blue |
| **Heavy Rain** | $64.5 - 115.6$ | `#1B4B74` | Deep navy |
| **Very Heavy** | $115.6 - 204.5$ | `#102652` | Dark midnight blue |
| **Extremely Heavy**| $\ge 204.5$ | `#380C3D` | Saturated deep plum |

### 3.2 Indicative Alert Level Palette & Glyph Shapes
To ensure accessibility for color-vision-deficient users, color is never the sole carrier of alert meaning:

| Alert Level | Distinct Glyph | Color Hex (Light) | Color Hex (Dark) | Operational Meaning |
|---|---|---|---|---|
| **Green** | Circle `●` | `#2E7D32` | `#4CAF50` | No Warning (Normal conditions) |
| **Yellow** | Square `■` | `#9A6A00` | `#FBC02D` | Watch (Be Updated) |
| **Orange** | Triangle `▲` | `#C75100` | `#FF9800` | Alert (Be Prepared) |
| **Red** | Diamond `◆` | `#B71C1C` | `#EF5350` | Warning (Take Action) |

### 3.3 Synoptic Regime Palette & Map Hatching
- **Active:** `#1B4B74` (Solid Navy / Horizontal Hatch)
- **Break:** `#B85D19` (Rust Orange / Stippled Dot)
- **Depression / Low:** `#6B2D5C` (Deep Magenta / Diagonal Cross-hatch)
- **Normal / Transition:** `#555B63` (Neutral Slate / Plain)

---

## 4. Typography Scale & Hierarchy

- **UI Sans:** Humanist Sans (`Public Sans` / `@fontsource/public-sans`), weights 400, 500, 600.
- **Editorial Headings:** Refined Text Serif (`Newsreader` / `@fontsource/newsreader`), weights 400 italic, 600.
- **Code & Run IDs:** Monospace (`JetBrains Mono`), weight 400.
- **Scale:**
  - Display 1: 32px / line-height 38px
  - Heading 2: 22px / line-height 28px
  - Section Title: 16px / line-height 22px
  - Body Text: 14px / line-height 20px
  - Dense Table & Microcopy: 12px / line-height 16px
  - Annotation & Units: 11px / line-height 14px

---

## 5. Token Export Files

Design tokens are machine-readable in:
- `web/src/styles/tokens.css`
- `web/src/styles/tokens.json`
