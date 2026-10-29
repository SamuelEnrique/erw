# The ERW brand, version 0

Energy Research Warehouse (ERW), session 203 (12 October 2026). Direction A of the roadmap's ruling of 12 October 2026 (`docs/roadmap.md`, "This week", item 3): a white page with fog panels, Source Serif 4 for display, IBM Plex Sans for text, IBM Plex Mono for numbers in tables, cardinal as the only accent, charts in the manner of the Financial Times.

**Status: approved 12 October 2026; the battery page is the reference.** Samuel approved the battery page restyled with these rules on the night of 12 October 2026, and session 234 landed it on `main` (`/cost-of-power/battery`, sessions 203 to 211). Every other page is brought to it through `site/app/tokens.css` and the shared components, so that a change of brand is one file to change. (Until session 234 this line read "a proposal for review".)

What each rule is for is written beside it. Where a rule answers something a tool measured on the battery page in session 201, the measurement is given (`archive/sessions/SESSION_201_REPORT.md`).

## 1. Type

Three families, two voices: a serif for what the page says, a sans for everything a reader uses, and the sans's own mono for figures in tables.

| Role | Family | Weights | Where |
|---|---|---|---|
| Display | Source Serif 4 | 600 | The page title, section titles, the summary sentence, a headline number |
| Text | IBM Plex Sans | 400, 500, 600 | Body, labels, notes, the menu, buttons, table text |
| Numbers in tables | IBM Plex Mono | 400, 500 | Figures in table cells and in a chart's hover card. Never a label, a caption or axis text |

- Fallbacks: `Georgia, "Times New Roman", serif`; `system-ui, "Segoe UI", sans-serif`; `ui-monospace, Consolas, monospace`. The three are loaded as the site loads its font today (`next/font`), each with a fallback of matched metrics, so text does not move when a font arrives (the battery page's layout shift was 0.31 on a phone profile with one web font; three would raise it).
- IBM Plex Mono has no variable file: each weight is a file. Two weights only.
- **Figures are lining and tabular everywhere**: `font-variant-numeric: lining-nums tabular-nums`, set on the display face too. Georgia's figures rise and fall; the headline numbers looked uneven.

### The scale

Six sizes. The battery page had ten (10, 11, 12, 14, 16, 18, 20, 22, 30 and 36 px), 1,035 of its 1,281 text elements at 14 px.

| Size | Line height | Family and weight | Use |
|---|---|---|---|
| 36 px | 1.15 | Serif 600 | The page title |
| 24 px | 1.25 | Serif 600 | A headline number; the summary sentence at 20 px is the next row |
| 20 px | 1.35 | Serif 600 | A section title; the summary sentence (Serif 400 is not used: one weight) |
| 16 px | 1.5 | Sans 400 | The lead paragraph; text inside a field on a phone (a smaller field makes a phone zoom) |
| 14 px | 1.5 | Sans 400; 500 for a label; 600 for a table's total | Body, tables, the menu, controls |
| 12 px | 1.5 | Sans 400 | Captions, notes, sources, axis text. Nothing on the site is smaller |

- A section title is ink, not cardinal (section 2). It is told from the summary sentence by weight and a rule above it, not by color.
- **Measure:** a paragraph of notes or captions runs at most 68 characters a line (`max-width: 68ch`). The battery page's notes ran 115 to 135.
- Labels are in sentence case. No capitals by style, no letter-spacing.
- Terms that must not break carry `white-space: nowrap`: "ISO-NE", "4-hour", "kW-month", "USD/kW".

## 2. Color

| Token | Value | Use | Contrast |
|---|---|---|---|
| page | `#FFFFFF` | The page | |
| fog | `#F7F3EA` | A panel the reader types into; a hover card; a highlighted table row | against the page 1.11 to 1: a panel is told by its edge or its place, not by its tint |
| rule | `#E3DED1` | Row rules, grid lines, a panel's edge | 1.34 to 1 on the page: decoration only, never the edge of a control |
| captions | `#6B675F` | Captions, notes, axis text, the edge of a field | 5.63 to 1 on the page, 5.08 on fog: passes AA for text on both, not AAA |
| ink | `#2E2D29` | Text, titles, a table header's rule, the zero line of a chart | 13.78 to 1 on the page, 12.45 on fog |
| cardinal | `#8C1515` | The only accent | 9.40 to 1 on the page, 8.49 on fog; white on cardinal 9.40 |

**Cardinal has three jobs and no other:** a link, a control in its active state (the one action of a form, the selected segment), and the highlighted series of a chart. It is not the color of a title, a section heading or a table header. On the battery page it did nine jobs (93 text elements and six full-width table bands), so it marked nothing.

- **A link in running text is underlined.** Cardinal against ink is 1.47 to 1 and against captions 1.67: color alone cannot carry a link (the one finding every scanner of session 201 reported, 13 links).
- **A field's edge is the captions grey**, not the rule color: 5.63 to 1 against a white field where the rule color gave 1.5.
- **Focus:** a 2 px ink outline, offset 2 px, on `:focus-visible`, for every link and control. No focus style existed.
- Up and down are never colored as good and bad. A page states; it does not judge.

### Chart series

In this order: ink `#2E2D29`, cardinal `#8C1515`, blue `#3C6E9E`, grey `#6B675F`, light grey `#8F8A80`.

| Pair | Contrast | So |
|---|---|---|
| blue on the page, on fog | 5.36, 4.84 | passes as a line and as a label |
| light grey on the page, on fog | 3.43, 3.10 | passes the 3 to 1 a mark needs; not used for text |
| cardinal against ink | 1.47 | two fills that touch are parted by a 1 px white line, and each is named on the chart |
| cardinal against blue, ink against blue | 1.75, 2.57 | the same: a series is never told by its color alone |

The fuel colors of the generation mix (`site/app/tokens.css`, `--color-fuel-*`) are a subject's own palette and are not replaced by these five.

### Many series (session 268)

The owner's instruction of 14 October 2026: a chart of more than five series takes these eight, in this order (Paul Tol's colorblind-safe set), as `--chart-series-1` to `--chart-series-8` in `site/app/tokens.css`. **Cardinal stays the highlight:** the one series a chart marks is drawn in cardinal and the others take the eight; cardinal is not among them.

| Token | Value | On the page | On fog | Against cardinal |
|---|---|---|---|---|
| `--chart-series-1` | `#4477AA` | 4.70 | 4.25 | 2.00 |
| `--chart-series-2` | `#66CCEE` | 1.84 | 1.66 | 5.12 |
| `--chart-series-3` | `#228833` | 4.53 | 4.09 | 2.08 |
| `--chart-series-4` | `#CCBB44` | 1.95 | 1.76 | 4.82 |
| `--chart-series-5` | `#EE6677` | 3.09 | 2.79 | 3.05 |
| `--chart-series-6` | `#AA3377` | 6.09 | 5.50 | 1.54 |
| `--chart-series-7` | `#BBBBBB` | 1.92 | 1.73 | 4.90 |
| `--chart-series-8` | `#EEAA44` | 2.01 | 1.81 | 4.69 |

- Contrast is WCAG's ratio, computed for this table. Five of the eight are below the 3 to 1 a mark needs on the page: they are fills (bars, areas, wide lines), never text, and every series is named on the chart, in its hover card or in its table, so no series is told by its color alone.
- `#AA3377` sits 1.54 from cardinal: a chart that highlights in cardinal leaves the sixth slot out, or parts the two with a white line and names both.
- No page was moved to these colors by session 268: a chart takes them when it is next drawn with more than five series.

## 3. Space and shape

- Steps: 4, 8, 12, 16, 24, 32, 48 px. Inside a panel 16; between a title and its content 12; between sections 48; between a control and its note 8.
- Corners are square. The one radius is the mark's.
- No shadow, no gradient, no texture. A panel is fog with a rule-colored edge.
- No motion. A change the reader makes is shown at once.
- A target a finger presses is at least 24 px in both directions with its label (the battery page's radios were 13 px); 44 px tall on a phone.

## 4. Rules, and what a rule means

A rule is information. There are three, and nothing else is ruled:

1. **One dark rule (ink, 1 px) under a table's header.**
2. **A light rule (the rule color, 1 px) between rows**, and as a chart's grid line.
3. **A light rule above a section title.**

## 5. Tables

- No colored header band. The header is 12 px captions grey sans, sentence case, with rule 1 under it. The unit is in the header, once, not in every cell.
- Numbers are right-aligned IBM Plex Mono, 14 px, tabular. Text is left-aligned sans.
- One unit and one magnitude a column: a column does not hold "5.46 million" above "664,224". (How the battery page writes its numbers is a ruling of its own; the restyle does not change a number.)
- A total is sans 600 for its label, mono 500 for its figures, with rule 1 above it. A highlighted row sits on fog.
- Rows are 32 to 36 px tall. A table wider than its frame scrolls inside it, keeps its first column in place, and shows a fade at the edge it continues past.
- A cell that holds nothing says so in captions grey ("not held"), never a dash.

## 6. Charts

- Lines are 1.5 px. Bars are flat fills. No area fill under a line unless the area is the quantity.
- **Direct labels:** a series is named at the end of its line, or on its bar, in its own color. No legend box.
- Grid lines are the rule color, horizontal only; the zero line is ink. No frame around the plot.
- Axis text is 12 px captions grey and does not scale down with the chart: a chart drawn for a wide screen is drawn again for a phone, not shrunk (the year chart's labels were about 6 px at 390 px).
- A value off the scale is broken and written, as the battery page's 2021 is. An incomplete period is hatched and says how much of it is held.
- **The hover card** is fog with a rule-colored edge: the period in sans 12 px, each series named in sans with its figure in mono. Whatever the card says is also reachable by keyboard and as a table under the chart.
- Colors are tokens. No hex value is written in a component (session 201 found them in five files of the battery page).
- **Heat maps** (the owner's ruling of 20 October 2026): one color, the accent, for a magnitude; where the figure is signed, a two-hue ramp, the accent above zero and the blue (`--chart-blue`) below, each cell as strong as its distance from zero. No range slider on any chart (the same ruling). The one exception is carbon intensity on the grid network (the owner's instruction of 29 October 2026): clean to dirty is read as a signed scale, so it runs green (`--color-intensity-low`) through fog (`--color-intensity-mid`, the middle of the held range) to cardinal (`--color-intensity-high`).

## 7. Assumptions

Every assumption a reader may change:

- shows its **default in grey with its source** beside the field ("Default 1,110. Lazard, Levelized Cost of Energy+, June 2025"), in 12 px captions grey;
- is **editable in place**: the field holds the value, in ink once the reader has changed it;
- can be put back with one press, named for its field ("Reset capital cost").

## 8. The mark

The E in the cardinal square is kept (`docs/brand/README.md`, session 25: a white stem and three bars of 14, 11 and 17 units, an E that is also a small bar chart). The files in use are untouched: `docs/brand/erw-mark.svg`, `docs/brand/erw-wordmark.svg`, `site/app/icon.svg`, `site/components/Wordmark.tsx`.

**Proposed, for review, in `site/public/brand/`** (served at `/brand/erw-mark-proposed.svg` and `/brand/erw-wordmark-proposed.svg`; linked from no page):

- The same square, stem and three bars, redrawn on one grid: every stroke 4 units of a 40-unit square, the three gaps equal, the bars' lengths in the same order (middle shortest, bottom longest) at 18, 14 and 22 units, the corner radius 2.
- The wordmark sets "ERW" in Source Serif 4 at weight 600 beside it, in ink, so that cardinal stays the square's.

What changes against today's mark: the bars are slightly heavier against the square (4 of 40 units where they were 3 of 32), the gaps are even (they were 4 and 5 units), and the word beside it is ink.

## 9. What this version does not decide

- The Grid and price board mockups (the roadmap holds the Grid merge's design for them).
- Dark mode. None is proposed.
- The emails and the weekly charts (`warehouse/news/`, `warehouse/analysis/style.py`), which draw the mark and the palette themselves.
- The base link color's place in the stylesheet: `site/app/globals.css` sets it outside a cascade layer, so it wins over every color class a link carries. Moving it changes links across the site and is its own landing.
