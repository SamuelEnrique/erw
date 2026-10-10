# Session 174 report: four more findings, landed

Run on 10 October 2026 (UTC), 02:58 to about 03:30, unattended, third of the chain 172 to 175 (`CHAIN_OCT9_PROMPT.md`).
Built in the main copy on `wip/173-land`. No pull, no model call (USD 0 of 0). Outputs under `runs/session174/`.

## Read these first

- **Four new finding cards are on production** (`task/174-findings`, merge `2476f6e`, deployed 03:25:49 UTC), each to
  session 170's standard: a title in capitals, the insight subtitle, an interactive comparison chart, three callouts,
  one paragraph, a method footnote, CSV, Python and Stata downloads, two renders in the bundled fonts, every number
  reproduced from the CSV by the finding's own code (the generic tests of session 170 now cover seven findings).
- **What the data said, in one line each.** The peak hour moved: in ERCOT the median peak-price hour went from 15 to 19
  and the share of days peaking in the evening from 24.9 to 71.0 percent as solar went from 2,592 to 30,018 MW. Who
  rescues whom (Uri): 6 authorities turned exporter, 5 turned importer; ERCOT itself went from 512 MWh a day exported to
  9,652 imported. Negative prices march west: ERCOT West had 637 negative hours in 2025 against Houston's 142 (308 and
  46 in 2019). Batteries and curtailment: **the data goes the other way**: each extra GWh a day of charging goes with
  1,081 MWh more curtailment, solar output and the month held fixed (SE 172, p under 0.001); the card says so.
- **Two data facts worth knowing.** EIA-930's daily interchange carries region rows (CAL, MIDA, TEX ...) beside the
  authorities, and its two sides of a pair disagree (on 2021-02-15 PJM reported 432,663 MWh sent to MISO, MISO 178,851
  received): the finding leaves the regions out and takes the mean of the two sides, and says how often they differ.
  CAISO's prices are held from 2024-09-01 only, so CAISO's "2019 to 2026" is 2025 and 2026 to date, said on the card.
- Snapshots `174_before` and `174_after`: 0 differences on the 25 pages. `check-analysis.mjs` against production:
  164 of 164. The whole suite in a clean copy: 2,746 tests OK.

## What to click (internal view first: `https://erw-flame.vercel.app/internal/unlock?token=...`)

1. `https://erw-flame.vercel.app/analysis`: seven cards now; the four new ones follow the three of session 170.
2. **THE PEAK HOUR MOVED** (`https://erw-flame.vercel.app/analysis/card/peak_hour_moved`): the chart has four lines
   over the 24 hours (ERCOT 2019, ERCOT 2025, CAISO 2025, CAISO 2026 to date), the percent of the year's days whose
   dearest hour fell in each hour; hover hour 19: ERCOT 2025 22.2 percent of 365 days. Callouts: median peak hour 15 to
   19, evening share 24.9 to 71.0 percent, solar 2,592 to 30,018 MW. Inputs: first year, hours a day must hold.
3. **WHO RESCUES WHOM** (`.../analysis/card/who_rescues_whom`): grouped bars, baseline against the event, for the 11
   authorities that flipped and ERCOT, largest swing first (Arizona Public Service, SPP, PacifiCorp East, ERCOT, ...);
   hover a bar: the flow and the flip. Inputs: the event (Uri, Elliott, the 2023 heat, the August 2020 heat) and the
   smallest flow counted. Ask for Elliott on the request form to see the December 2022 flips (the worker must run).
4. **NEGATIVE PRICES MARCH WEST** (`.../analysis/card/negative_prices_west`): five lines by year, negative hours at
   ERCOT West, Houston, North, South and SPP North (from 2024). West's worst year 2022 with 1,015 hours; 2026 to date
   West 903 of 6,719 held hours. Inputs: first year, the threshold (0, -10, -20 USD/MWh).
5. **BY HOW MUCH DO BATTERIES CUT CURTAILMENT** (`.../analysis/card/batteries_curtailment`): a scatter of 405 Pacific
   days (x charging GWh, y curtailed GWh) with the fitted line; hover a point: its date, charging, curtailment and
   solar. The effect table: three specifications, 699, 951 and 1,081 MWh curtailed per GWh charged, HC1 errors, p under
   0.001, R2 0.09, 0.10 and 0.65. The words under it state an association. Inputs: curtailment counted (solar and wind,
   or solar only), first month.
6. Each card: CSV, Python, Stata, the two renders (for example
   `https://erw-flame.vercel.app/findings/batteries_curtailment_1600x900.png`), "Use in Roundup".
7. `https://erw-flame.vercel.app/data/methods/automated_analysis_findings`: findings 4 to 7.

## The four findings

1. **The peak hour moved** (`peak_hour_moved`, visual). ERCOT HB_HUBAVG and CAISO TH_SP15_GEN-APND real-time 15-minute
   prices to hourly means; a day's peak hour is the local clock hour with the highest mean (first on a tie; at least 20
   held hours); per grid and year the percent of days by peak hour, the median, the evening (17:00 to 21:59) and midday
   (10:00 to 15:59) shares, the modal hour; solar MW at year end from EIA-860M's August 2026 inventory (operating units
   by operating year plus units retired since by retirement year), balancing authority ERCO and CISO. ERCOT 2,837 local
   days 2019-01-01 to 2026-10-07; CAISO 765 days from 2024-09-01. ERCOT: median 15 to 19, evening 24.9 to 71.0 percent,
   midday 32.9 to 3.8, modal hour 16 (15.3 percent) to 19 (22.2); CAISO 2025: median 17, evening 34.3 percent, solar
   24,009 MW. Subtitle: "In Texas the day's dearest hour walked into the evening as solar took the midday".
2. **Who rescues whom** (`who_rescues_whom`, visual). `eia930_daily_interchange` by pair; regions left out; a pair's
   flow is the mean of its two sides where both are held (Uri: 8,604 pair-days, 7,870 with both sides, 1,459 of those
   more than a tenth apart); an authority's day is exports minus imports; window from `event_window_daily`'s header,
   baseline the same calendar days 364 and 728 days earlier. Uri: 71 authorities with flows on both sides, 6 flipped to
   exporting (PacifiCorp East the largest, 357 imported to 11,611 exported), 5 to importing (SPP the largest, 6,239 to
   43,416 imported), 58 kept their sign, 2 small; PJM's swing the largest at 175,325 MWh a day. The other three events
   are inputs on the form.
3. **Negative prices march west** (`negative_prices_west`, visual). The four ERCOT hubs (2019 on) and SPP North (from
   2024-09-01), hourly means below the threshold (0 on the card; -10 and -20 as inputs): West 308 hours in 2019, 1,015
   in 2022 (its worst), 637 in 2025 (7.3 percent of held hours); Houston 46, 142; North 224 and South 235 in 2025; SPP
   North 1,044 in 2025 (11.9 percent); 2026 to date West 903, Houston 114, of 6,719 held hours.
4. **By how much do batteries cut curtailment** (`batteries_curtailment`, econometric). 405 Pacific days 2025-08-24 to
   2026-10-06 with CAISO's curtailment (solar plus wind), the batteries' charging (negative five-minute MW summed) and
   solar generation; three OLS fits with HC1 errors: charging alone 699 MWh curtailed per GWh charged (SE 74); with
   solar 951 (SE 148); with solar and month-of-sample dummies 1,081 (SE 172, p under 0.001, R2 0.65). Days with
   charging at or below the median (50,752 MWh) curtailed 8,281 MWh on average; above it 19,401. The subtitle follows
   the sign: "Days with more charging see more curtailment, even with solar and the month held fixed"; the words say
   the batteries charge on the days the grid has most to spare, and that dispatch and prices are not separated.

## What else changed

- `site/lib/findingchart.ts`: three chart kinds, `lines` (several series, one free axis, every bar's label shown),
  `bars_free` (grouped bars, negative values) and `scatter` (points with a fitted line, the day in the hover);
  `FindingCard.tsx` reads the effect table's headings from the card (session 170's were fixed words).
- `run_finding.FINDINGS` and `site/lib/findings.ts` ORDER list seven; `catalogue.json` regenerated; the method note
  gained findings 4 to 7; `tests/test_session174.py` (10 tests: the registration, the contract, the chart kinds the
  site draws, each card's parts, and one check per finding of what it must read from the data).
- Renders: eight PNGs (`<card>_1080x1350.png`, `_1600x900.png`) in the bundled fonts, exit 0; the four 1600 x 900
  copies in `docs/analysis/findings/` for the Roundup.

## Checks, each its own command, exit code read (outputs under `runs/session174/`)

| Check | Exit | File |
|---|---|---|
| `run_finding.py` for each of the four (final computation) | 0 each | `finding*_*.out` |
| tests 174, 170, 173 in one process (47) | 0 | `test_174_170.out` |
| `npm run build` (two: the cards; the bar labels) | 0, 0 | `build_1.out`, `build_2.out` |
| `npx tsc --noEmit`, `npx eslint` on the two site files | 0, 0 | `tsc2.out`, `eslint.out` |
| `render-cards.mjs` on 3174 (8 PNGs, no fallback face) | 0 | `render_cards.out`, `render_cards2.out` |
| `check-analysis.mjs` on 3174 (164 of 164) and against production (164 of 164) | 0, 0 | `check_analysis2.out`, `check_analysis_prod.out` |
| whole suite in the clean worktree at `a4ae1ab` (2,746, 228 skipped) | 0 | `suite_clean.out` |
| `snapshot-live.mjs take` 174_before, 174_after; `compare` (0 differences) | 0, 0, 0 | `snap_174_*.out`, `compare_174.out` |
| `gh_api.py wait task/174-findings` | 0 | `wait_174.out` |

- The server on 3174 was stopped; no process of this session is left running.

## Decisions made without you

1. **The interchange finding averages the two sides of each pair and leaves EIA's regions out.** The first computation
   summed each authority's own reports and listed MIDA and PJM with 267,840 MWh a day; the two sides' disagreement is
   now counted and said on the card. EIA's data are used as published otherwise.
2. **CAISO's partial first year (2024, from September) is a CSV row but not a chart line**, so no line stands for a
   third of a year; 2026 to date is drawn and labeled.
3. **The curtailment card reports the positive association as found.** The title asks how much batteries cut
   curtailment; the data cannot show a cut on these 405 days, and the subtitle, the words and the footnote say what the
   three fits found and what they cannot separate.
4. **Callouts print a flow without its sign** ("9,652 imported") because the callout check reads a number without its
   minus; the absolute values are card numbers.
5. **The p value is in the why and the effect table, not a callout** (the callout check knows 0, 1 and 2 decimals;
   p prints with 3); the third callout gives the standard error and R2.
6. The four 1600 x 900 renders went to `docs/analysis/findings/` beside the first three.

## To finish

- Nothing is held. This report reaches main with session 175's landing (`wip/173-land` is pushed).
- The worker is still not running on this machine (session 173's "To finish"): a request for Elliott, the 2023 heat
  or the August 2020 heat on the form waits as a queued row until it is.
