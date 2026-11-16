# Session 7538 report: the price board (`/board`) read as its reader (chain 304, part C, samueloldlaptop, 16 November 2026)

Branch `wip/7538-board-read` (worktree `C:\Users\lossa\Documents\erw-7538`, from origin/main `836daf204`). The read: `docs/reviews/board-read-2026-11-16.md` (20 rows). Model spend USD 0.

## What was done

- **The reader and five cases**, written first: a power trader or fund analyst on 16 November 2026 checking ERCOT Hub average against yesterday and a year ago; three hubs side by side (ERCOT North, CAISO SP15, SPP North); Henry Hub and the ERCOT spark spread; California's carbon (August 2026 auction, LCFS week of 2 November) against a year before, with RGGI and the EUA; New York City and ISO-NE.
- **How:** the board drawn whole to HTML with its own components on `site/data/board.json` (built `2026-11-16T19:08:45Z`) after the page's own hold; the figures shared with `/grid` read in the live set with the public key, the three public grids only, printed and not saved (no held row written anywhere).
- **Site, fixed (6), held by `site/scripts/test-board-read.mjs` (31 of 31):** the headline strip marks a stale close (Henry Hub's 3 November close read as current); the strip's lowest and highest grid say "of 3 grids" and name the grids compared and those not on the board; the strip's range cells give their date; the week table says the sign of "RT minus DA" against the group "Day-ahead minus real time"; a stale 30-day volatility is marked (ERCOT's six hubs, 6 November); the "f" mark says what it is.
- **Data machine (5 rows, 4 requests 119 to 122):** the board's gas set (Henry Hub with every spark spread and implied heat rate) has been kept since the build that ended on 3 November while the table holds 11 November; a heat-rate disagreement on the page from the same cause; repeated closes on US holidays (WTI, New York Harbor gasoline and diesel, Henry Hub on 11 November and 7 September 2026); ERCOT day-ahead missing 7 and 8 November; SPP North real time missing 10 of 45 days.
- **The method note** `docs/methods/price_board.md`: one dated section added before "What waits for the owner", nothing removed.
- **Files of the other machine's stack touched:** `site/components/board/BoardView.tsx` (the strip, the week table's header and volatility cell, the formula mark), `site/lib/board.ts` (three pure exports added, `gridExtremes` returns one more field, nothing else changed), `docs/methods/price_board.md` (a section added). Not touched: `site/components/Num.tsx`, `site/lib/release.ts`, the builder, `page_keep.py`, any table.
- **What went wrong:** the first commit's message was given to git through a heredoc, against the brief's rule (no permission prompt came; every later commit used `-m`).
- **Tests run:** `test-board-read.mjs` 31 of 31; `test-board-1116`, `1137`, `1193`, `1311` pass; `check-board.mjs --file` exit 0; 28 Python test files naming the changed modules, 194 passed and 52 subtests; the six naming the note, 78 passed. `test-board.mjs` fails at its line 87 (ERCOT's day-ahead rows under "every hub and zone": 19, it expects 6, the load zones of session 1601): the same on a clean copy of origin/main (stashed and run), not this change.

## What to review

- `https://erw-flame.vercel.app/board` (in review: a visitor sees the in-review page). Under the twelve tiles, the strip: it reads "Lowest of 3 grids, day-ahead" and "Highest of 3 grids, day-ahead"; hover the second: the grids compared (CAISO, ERCOT, SPP) and the four not on the board. The "Henry Hub gas" cell reads its date with "(stale)" while the close is past 10 days. The two range cells end with their month ("Oct 2026"). Click "Real time": the same labels with "real time".
- Same page, "Jump to", "The week, by hub": hover the header "RT minus DA, week": it says real time less day-ahead and that the group's 7-day avg is the same figure with its sign turned. ERCOT's six hubs show "stale" beside the 30-day volatility while it stops on 6 November.
- Same page, "Spark and dark spreads, by grid": hover the small "f" beside a name.

## Needs the key

- "Ask the board" (the form at the foot): answering the five board questions would cost about USD 0.10 to 0.50. Not asked.

## Decisions made without you

- The strip counts its grids in the label ("Lowest of 3 grids") rather than only in a hover: a label that misleads is fixed in place.
- The week table's volatility takes the power groups' 3 days as its stale threshold (the week's figures are a market's daily figures).
- The read file's rows are numbered 1 to 20 and its data rows cite request numbers 119 to 122 (four of the ten reserved); browser rows 146 to 148 (three of ten).

## For Samuel's ruling

- A stale row still draws its 7-day avg, 30-day avg and 30-day low to high (their window's end on hover). Default: drawn as now. The other choice: blank them as the moves are.
- The strip's "Highest in its year's range" may name a monthly average (the IMF's uranium, October 2026). Default: kept, now dated. The other choice: daily series only.
- An on-peak row's "Day" on a Monday is measured from the Friday (no weekend peak hours). Default: unchanged, the base's date on hover.

## Rows for the coordinator

### (a) The landing request row (row 36)

| 36 | `wip/7538-board-read` | `<head>` | `7538-board-read` | 7538 | 2026-11-16 | `site/scripts/test-board-read.mjs` (31 of 31, the board drawn whole on the site's file after the day's hold); `test-board-1116`, `1137`, `1193`, `1311` and `check-board.mjs --file` pass; 28 Python files naming `lib/board.ts` or `BoardView` (194 passed, 52 subtests) and the 6 naming the note (78 passed); `test-board.mjs` fails at line 87 on origin/main as well (19 ERCOT day-ahead rows, 6 expected: the load zones of session 1601), not this branch | requested |

## Row 36: what it holds (chain 304, part C, session 7538, the price board read as a trader)

- **Stacked on** origin/main `836daf204`. Report: `archive/sessions/SESSION_7538_REPORT.md` on the branch.
- **What changes:** `site/components/board/BoardView.tsx` (the headline strip: a stale close says "(stale)" with its age on hover, the lowest and highest grid say "of N grids" with the grids named on hover, the range cells carry their date; the week table: the "RT minus DA" header's hover, a "stale" mark on a volatility older than 3 days; the formula mark's hover), `site/lib/board.ts` (new pure exports `gridExtremesWords`, `headDate`, `weekStale`; `gridExtremes` returns `priced` beside its fields), `docs/methods/price_board.md` (one dated section added). New: `site/scripts/test-board-read.mjs`, `docs/reviews/board-read-2026-11-16.md`.
- **What does not change:** `site/components/Num.tsx`, `site/lib/release.ts`, `site/app/board/page.tsx`, the rows' CSV and its readers, `check-values.mjs`, `check-board.mjs`, the builder (`warehouse/derived/board_page.py`), `page_keep.py`, any table or page file. No figure changes; no `data-n` mark is added, removed or renamed.
- **Before landing:** a site build on the landing machine; `node --import ./scripts/alias-register.mjs scripts/check-board.mjs <served address>` on the build.
- **Snapshot differences to expect:** none on the 25 addresses (`/board` is in review; a visitor is shown the in-review page). **Tables:** none.
- **After the landing:** rows 146 to 148 of `docs/state/browser_reads_wanted.md`; rows 119 to 122 of `docs/state/data_requests_done_line.md` are the data machine's and do not hold this row.

### (b) Browser reads

| 146 | 2026-11-16 | 7538 | `wip/7538-board-read` (row 36) | `https://erw-flame.vercel.app/board` | The strip under the twelve tiles, at 1280 and 390 px; hover "Highest of 3 grids"; click "Real time" | "Lowest of 3 grids, day-ahead" and "Highest of 3 grids, day-ahead"; the hover names CAISO, ERCOT, SPP and the four grids not on the board; the Henry Hub cell's date ends "(stale)" while its close is past 10 days; each range cell ends with its month; no word cut so a reader cannot read it in the hover; no sideways scroll | wanted |
| 147 | 2026-11-16 | 7538 | `wip/7538-board-read` (row 36) | `https://erw-flame.vercel.app/board#week` | Hover the header "RT minus DA, week"; ERCOT's rows' "30-day volatility"; the page at 390 px | The hover says real time less day-ahead and that the group's 7-day avg is the same figure with its sign turned; "stale" beside each ERCOT volatility dated more than 3 days before the build, its age on hover; the table scrolls in its own frame and the page does not | wanted |
| 148 | 2026-11-16 | 7538 | `wip/7538-board-read` (row 36) | `https://erw-flame.vercel.app/board#spark` | Hover the small "f" beside "ERCOT Hub average, spark spread" | "A formula of other rows of the board: the formula is in the name's hover." shows over the name's own hover | wanted |

### (c) Data requests

| 119 | 2026-11-16 | 7538 (chain 304, samueloldlaptop; branch `wip/7538-board-read`) | `site/data/board.json` (`warehouse/derived/page_keep.py board`, `BOARD_TOGETHER`) | On the board built 2026-11-16T19:08:45Z Henry Hub (`eia-henry-hub-spot`) ends 3 Nov 2026 and every `-spark` and `-heat` row ends 6 Nov, while `eia_fuel_spot_prices` holds Henry Hub on 4, 5, 6, 9, 10 and 11 Nov (this machine's copy, the run of 13 Nov: 2.63, 2.61, 2.60, 2.89, 3.00, 3.00) and WTI reaches 11 Nov on the same board. `hold_together` keeps the whole set when one member is kept: find in `page_keep`'s log the member it was "kept with" since the build that ended on 3 Nov, rebuild the set from one build, and say why that member was kept. The week table's heat rate (13.13 to 15 Nov) and the spark group's (15.45 on 6 Nov) then agree | `docs/reviews/board-read-2026-11-16.md`, rows 2 and 3 | requested |
| 120 | 2026-11-16 | 7538 (chain 304, samueloldlaptop; branch `wip/7538-board-read`) | `eia_fuel_spot_prices`, `eia_product_spot_prices` | Repeated closes on US holidays: 11 Nov 2026 (Veterans Day) WTI 89.62, New York Harbor conventional gasoline 2.415, New York Harbor ULSD 4.204 and Henry Hub 3.00 each equal the 10 Nov close (Brent moved +1.98); 7 Sep 2026 (Labor Day) WTI 92.69 and Henry Hub 2.92 equal 4 Sep; 11 Nov 2025 holds no value for the same series. Check EIA's own series (RWTC, RNGWHHD, EER_EPMRU_PF4_Y35NY_DPG, EER_EPD2DXL0_PF4_Y35NY_DPG) for those days: if EIA publishes the repeat, say so in `docs/methods/price_board.md` (the board draws "Day 0.00"); if the connector writes it, drop the day | EIA, daily spot prices (API v2); the read's row 6 | requested |
| 121 | 2026-11-16 | 7538 (chain 304, samueloldlaptop; branch `wip/7538-board-read`) | `ercot_all_hub_prices_history`, `iso_dam_hub_prices` (ERCOT), the board's series | ERCOT's day-ahead daily means of operating days 7 and 8 November 2026 are in no board series file (every ERCOT hub; ERCOT North's 30-day avg is of 28 days; the week table's 30-day volatility stopped on 6 Nov). Pull ERCOT's DAM settlement point prices for those two days and rebuild | ERCOT, DAM Settlement Point Prices; the read's rows 7 and 9 | requested |
| 122 | 2026-11-16 | 7538 (chain 304, samueloldlaptop; branch `wip/7538-board-read`) | `iso_rtm_hub_prices` (SPP) | SPP North hub's real-time daily mean is missing on 7, 10, 12, 14, 15, 19, 21 and 22 Oct and 1 and 11 Nov 2026 (10 of the last 45 days; a day is drawn only when every interval is held). Check whether SPP's real-time LMP files for those days are whole now; if so, pull and rebuild; if not, the days stay out and nothing is to do | SPP, real-time LMP by settlement location; the read's row 11 | requested |

### (d) The progress line (part C of `docs/state/progress_c304.md`)

| `/board` | lab-desktop | done `<head>` on `wip/7538-board-read` (landing row 36): the reader a power trader or fund analyst on 16 November 2026 checking the morning's prices against the day before and a year before; five cases (ERCOT Hub average against yesterday and a year ago; ERCOT North, CAISO SP15 and SPP North side by side; Henry Hub and the ERCOT spark spread; California's carbon against a year before, RGGI and the EUA; New York City and ISO-NE); the figures shared with `/grid` agree to the fourth decimal (eight daily means, four 30-day means, six peak and off-peak means); rows: 20 (6 site fixed, 5 data machine with requests 119 to 122, 3 browser 146 to 148, 3 rulings, 2 license, 1 key) | 7538 |
