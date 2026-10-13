# Two home page mockups (session 242, 13 October 2026)

Energy Research Warehouse (ERW). Screenshots only: nothing here is built into the site, and `site/app/page.tsx` is untouched. Each mockup is a standalone HTML page in the approved brand (`docs/brand.md`, the brand section of `site/app/tokens.css`), rendered full page by the headless Chrome of `site/scripts/browser.mjs` at 1280 and 390 px wide.

| File | What it is |
|---|---|
| `home_A_1280.png`, `home_A_390.png` | Mockup A, the owner's order: the one line, today's chart, the five tools, the latest Digest |
| `home_B_1280.png`, `home_B_390.png` | Mockup B, this session's proposal: the page asks whose question it is |

Rendered 13 October 2026, 09:49 UTC: A is 1280 x 1868 and 390 x 3882 px, B is 1280 x 1547 and 390 x 2870 px; each file is under 310 KB. The three families loaded from Google Fonts on every render (Source Serif 4 at 600, IBM Plex Sans at 400 and 500, IBM Plex Mono at 400; B holds no table, so it asks for no mono). No page scrolls sideways at either width and no text is under 12 px. One blemish left as it is: at 390 px the sentence under the second story breaks after "show", a short first line.

The sources of the pages (`home_A.html`, `home_B.html`, `brand.css`, `chart.js`, `chart_data.js`, `render.mjs`) are in `runs/session242/mockups/` on the code machine (not in git).

## What each holds

**Both:** the site's header as it is tonight (the E mark of `site/components/Wordmark.tsx` unchanged; the six menus Economics, Grid, Infrastructure, Analysis, Games, About and the three grey links Energy Digest, Roundup, Email of `site/lib/pages.ts`, menus closed) and the site's footer line (`site/app/layout.tsx`). White page, Source Serif 4 at 600 for display, IBM Plex Sans for text, IBM Plex Mono for figures in tables, six sizes (36, 24, 20, 16, 14, 12; the title is 24 on a phone, as the brand has it), cardinal only on links and on the chart's highlighted point, the three rules of section 4, square corners.

**A**, top to bottom: the one line as the page title; today's chart with its sentence and its five figures; the five tools side by side, each with its name, its line and one number; the Digest of 12 October, its first five stories with the Digest's own sentence for each, beside the Digest's numbers (day-ahead averages, the highest real-time price, the fuel closes). Nothing else.

**B**, top to bottom: the one line; "Which question is yours?", five rows, each a reader, the reader's question, the tool that answers it and the tool's one number; then, side by side and short, today's chart and the Digest's first three stories.

## What B bets on, and what it gives up against A

- B bets that a visitor from a link is one of five people and wants their tool: the first screen is the five readers, each with a question and an answer in a number, and nothing else competes with it.
- B says what the ERW is by what it answers (five questions, five numbers), not by what happened today.
- B gives up the chart as the page's opening image: the day's finding is half a row, lower down.
- B gives up the Digest's length: three stories and no table of the day's prices, so a returning reader sees less that changed since yesterday.
- B's rows are words that do not change day to day; A looks new every morning, B looks the same until a number moves.

## The two candidate one-liners

1. "The live, citable record of the US energy system." On mockup A. The site's own words: the first clause of the description in `site/app/layout.tsx` and of "What the ERW is" in `CLAUDE.md`.
2. "US energy in numbers you can cite, each traced to its source." On mockup B. Plain words for the same sentence and for rule 5 of `CLAUDE.md` ("Every number traces to its source").

## Where each number and each text came from

| On the mockup | Source (file and field) |
|---|---|
| Today's chart, 13 October 2026: the sentence, 1,028,747 MWh, 765,381 MWh (July 2024), 263,366 MWh, 9.86, 305 months from January 2001 | `docs/digest/charts/2026-10-13.json`: `fact`, `numbers.value`, `numbers.old_record` and `flag.compared.old_record_date`, `numbers.margin`, `numbers.margin_sigmas`, `numbers.history_points` and `flag.history.first`. The label "Record high" is its `title` in sentence case |
| The chart's line | **Redrawn**, not the PNG as drawn. The record holds no series, so the 307 monthly points (January 2001 to July 2026) were read from the table it names: `warehouse/output/eia_state_generation_monthly.csv`, `entity` `eia:generation:WY:NG`, `variable` `net_generation` (EIA, Form EIA-923; the connector run of 29 September 2026). Its July 2026 value, 1,028,747.26, and July 2024, 765,381.4, equal the record's. The Digest's PNG (`docs/digest/charts/2026-10-13.png`) plots the same series from 2011; the mockup shows the whole history the sentence speaks of |
| What a battery earns: USD 81.40 per kW, 100 MW, 4-hour, ERCOT, October 2025 to September 2026 | `docs/methods/battery_earns_algorithm.md`, "The default case" (the page's `l12_kw:total`). Read again on 13 October by the review: `docs/reviews/erw-review-2026-10-12.md`, the home page's "Checked" line (page 81.40, Supabase 81.4021896) |
| What a generator earns: USD 59.85 per kW, 100 MW of solar at ERCOT's hub average, October 2025 to September 2026 | `docs/methods/generator_earns_algorithm.md`, "The default case". Recomputed here from `site/data/merchant_snapshot.json`: the sum of `isos.ercot.months[2025-10 .. 2026-09].solar.revenue_per_mw` is 59,852.26 USD per MW |
| What a datacenter pays: USD 33.73 per MWh, a flat 100 MW load, ERCOT North load zone, real time, October 2025 to September 2026 | `docs/methods/datacenter_pays_algorithm.md`, "The default case". Recomputed here from `site/data/datacenter/ercot_2025.json` and `ercot_2026.json` (`regions.LZ_NORTH.rt.v`): the mean of the 8,760 hourly prices from 1 October 2025 to 30 September 2026, Central standard time, is 33.7289 |
| The Grid: 68,538 MW, ERCOT's demand at 23:00 UTC on 10 October 2026 | `site/data/grid_network.json` (built 12 October 2026 14:33 UTC): the node `ERCO`, `demand_mw` and `demand_ts`; the newest of its 168 hours |
| Research: 11 findings | `site/data/findings/catalogue.json`: its 11 entries |
| The Digest: the date, "the 24 hours to 15:35 UTC", 277 scored stories, the stories with their order, sector, sentence and publishers | `docs/digest/2026-10-12.md` (the newest file; `latest.md` is the same file): the opening line and "Top of the industry", items 1 to 5 (A) and 1 to 3 (B). The headlines are the publishers' own titles, as that Digest says |
| The Digest's numbers (A): day-ahead averages of 11 October, 107.29 USD/MWh at SPPSOUTH_HUB, Henry Hub 3.03, WTI 96.24, Brent 125.44 on 6 October | The same file, "ERW's Numbers Today": the table, "Highest real-time price, yesterday" and "Latest fuel spot closes". MISO and PJM carry the Digest's own words for a number not held |
| The tools' lines | Shortened from `site/lib/pages.ts`: `/cost-of-power/battery`, `/cost-of-power/seller`, `/cost-of-power` and `/network`. Research's line is the lead of `site/app/analysis/page.tsx` shortened ("Findings from the warehouse, on demand..."), since the line in `pages.ts` still describes the weekly templates |
| The tools' names | `docs/reviews/erw-review-2026-10-12.md`, section A, and `docs/roadmap.md` item 2; "Research" at `/research` is tonight's name for Automated Analysis |

**Not shown, and why.** The Digest file prints no score beside a story (only the count, "277 scored stories"), so the mockups show the order and the sector and no score. The three tool figures from the method notes are those of the default case as the notes date them (builds of 4, 7 and 10 October 2026); the two that can be recomputed from committed files were, and agree.

**Words written for the mockups** (not read from a file): the two section titles "Today's chart" and "The five tools", B's title "Which question is yours?" with its five readers and five questions, the chart's caption, and the notes under the tool numbers.

## What would have to be built

Both pages take the brand by wrapping in `<Brand>` (`site/components/Brand.tsx`); the home page is today outside the brand.

- **The one line, the header, the footer:** exist (`site/app/layout.tsx`); the line is a change of words in `site/app/page.tsx`.
- **Today's chart:** the record and the PNG exist (`docs/digest/charts/`, session 232, served at `/digest-charts/` by `site/lib/markdown.ts`). The sentence and the figures are one read of the newest JSON. A redrawn line needs the series: `eia_state_generation_monthly` is not in the live set (`warehouse/supabase/live_set.yaml`), so either the scanner writes the plotted points into the record, or the page shows the PNG as drawn (paper background, its own title and mark; a 1,200 px drawing shrunk to 358 px on a phone, so its axis text falls under the brand's 12 px). `components/LineChart.tsx` and `ChartFrame` (`components/tool/ToolPage.tsx`) exist; the dashed record line and the marked point are new.
- **The five tools:** `HeadlineRow` and `HeadlineNumber` exist, with `Num` for the check keys. Reads: the battery's number is already on the home page (`liveNumbers`, key `bs|...|l12_kw:total`); the grid's too (`series|eia930_all_demand|eia930:ERCO|demand_mw|newest`); the generator's last twelve months per kW is a new `stat` key in `site/lib/merchant.ts` over the snapshot the home page already opens (it shows the median month today); the datacenter's is the last-twelve-months span of `site/lib/datacenter.ts` over `site/data/datacenter/`, a new read for the home page; Research's count is `loadCatalogue()` in `site/lib/findings.ts`. Each new number needs its key in `scripts/check-values.mjs`.
- **The Digest:** `topItems(DOCS.latest, 5)` and `render` exist and the home page uses them. The numbers beside it (A) are the Digest's own markdown table: `render` of that section, or a small parser if the columns are to be the brand's table.
- **B only:** the five rows are static words plus the same five numbers; no read that A does not need. The page would drop the price cards, the three audiences, "Gas and oil", "In review" and the status strip of today's home page (A drops them too).
- **Either:** the home page is one of the 25 addresses of `site/scripts/snapshot-live.mjs`, and any test that pins a section of today's home page would move with it (not listed here: no test was read for this).
