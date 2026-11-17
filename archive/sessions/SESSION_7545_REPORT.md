# Session 7545 report: `/queues` read as the reader it is for (chain 304, part C, samueloldlaptop, 16 November 2026)

Energy Research Warehouse (ERW). Branch `wip/7545-queues-read`, worktree `C:\Users\lossa\Documents\erw-7545`, from origin/main `5c9b48a56`.

## What was done

- The reader: a developer choosing which grid's queue to file in (storage first, then solar with storage, wind, offshore wind), and a large load's energy lead reading the same page. Five cases: a 200 MW battery, ERCOT against CAISO; a solar-with-storage project, ERCOT against PJM; SPP's requests of 2018 beside the operators' own count; offshore wind in NYISO and ISO-NE; a 500 MW data center in ERCOT.
- The read: `docs/reviews/queues-read-2026-11-16.md`, 17 rows: 9 site fixed with a test, 2 data machine, 3 browser, 3 rulings.
- The page drawn to HTML by its own function, without a build: `site/scripts/queues-page.mjs` (new). The test: `site/scripts/test-queues-read.mjs` (new), 29 of 29.
- Site fixes (`site/app/queues/page.tsx`, `site/lib/queues.ts`): a table "[technology]: every grid" (the ten grids side by side); one operation year written as a sentence with its median (ERCOT's batteries: 2025, 3.94 years over 37) where the chart said "no line"; ERCOT's solar with storage "0.00 percent withdrawn" carries a hover wherever drawn (the file holds no withdrawn or suspended ERCOT hybrid); each year entered as counts in a fold; the lead names `/explore/interconnection` and `/map?tab=queues` as another source; the fold says the file holds no load and links `/datacenters` and the All grids tab; "1 request"; "the United States' queues"; ISO-NE's "not held" wait says why on hover.
- `site/scripts/check-queues.mjs` reads the new one-year sentence (`data-chart="years-one"`). `docs/methods/interconnection_queue_summary.md`: a new section "What the reader meets" (extended, nothing removed).
- Agreement: the All grids tab's count of plants online 2023 to 2025 equals this page's three operation years, grid by grid (ERCOT 227, CAISO 41, SPP 30, PJM 169, the Southeast 102); the cost of power's model reads the same file through the same `viewOf`. The explorer and the map's Queues tab are another source (the operators' lists, 19 October 2026); each page now names the other.
- License: the page reads only `queues.json` (Queued Up, CC BY 4.0, `interconnection_queue_summary` public). No row or figure of `iso_queue_statistics` or the NYISO, MISO or ISO-NE queue tables is drawn or committed; the test holds it.

**Files of the other machine's stack touched (lab desktop, chain 301):** `site/app/queues/page.tsx`, `site/lib/queues.ts`, `site/scripts/check-queues.mjs` (one check), `docs/methods/interconnection_queue_summary.md` (one section added). Not touched: `replication/queues/`, `site/lib/decisions.ts`, `site/data/queues.json`, the builder, any table.

**Tests run:** `site/scripts/test-queues-read.mjs` 29 of 29; pytest `test_session95, 241a, 7018_queues_done, 7518_interconnection_read, 105, 138, 3009, 3011`: 66 passed, 14 skipped by their rules; `tsc` on the page and its library (a temporary config extending the site's), exit 0. Not built here (memory); `check-queues`, `check-values` and `check-routes` not run.

## What to review

- `https://erw-flame.vercel.app/queues?grid=ercot&tech=battery` (with the review cookie): under "ERCOT: storage, solar with storage, and the rest", the new "Storage (batteries alone): every grid"; ERCOT's row reads 120,941, 660, 14.67, 26.67, 3.93 and CAISO's 47,499, 170, 10.63, 71.65, 6.84. "How long the built ones took" reads the 2025 sentence (3.94 years over 37).
- `https://erw-flame.vercel.app/queues?grid=ercot&tech=solar_battery`: hover the headline "Withdrawn" 0.00, and the 0.00 in both tables.
- `https://erw-flame.vercel.app/queues?grid=spp&tech=wind`: open "Every year entered, in requests and MW"; 2018 reads 41, 8,210, 1, 28, 12, 0, 1,893.
- `https://erw-flame.vercel.app/queues?grid=isone&tech=offshore_wind`: hover "not held" under "Request to operation".
- `https://erw-flame.vercel.app/queues`: the lead's last sentence and its two links; the fold "What the file does not hold", last line.

## Needs the key

Nothing.

## Decisions made without you

- The 0.00 of ERCOT's hybrids is kept as the table's figure and said on hover; nothing hidden or changed (the cause asked of the data machine, row 189).
- The new tables carry no grey note; their words are hovers or plain text.
- The grid table includes "All regions" as its first row, as the grid list does.

## For Samuel's ruling

- **The headline wait** (row 11): a median over every operation year. Default: unchanged. The other choice: add the last three operation years under it, as the All grids tab counts.
- **The grey notes** (row 12): shared components. Default: unchanged, as in every read today.
- **"0" or "none"** for a technology with no active request (row 14). Default: unchanged.

## Rows for the coordinator

### (a) The landing request

| 43 | `wip/7545-queues-read` | `<head>` | `7545-queues-read` | 7545 | 2026-11-16 | `site/scripts/test-queues-read.mjs` (29 of 29, the page drawn to HTML by its own function without a build, on the site's file); pytest `test_session95, 241a, 7018_queues_done, 7518_interconnection_read, 105, 138, 3009, 3011`: 66 passed, 14 skipped by their rules; `tsc` on `app/queues/page.tsx` and `lib/queues.ts`, exit 0; not built here (memory); `check-queues`, `check-values` and `check-routes` not run | requested |

## Row 43: what it holds (chain 304, part C, session 7545, `/queues` read as a developer choosing where to file)

- **Stacked on** origin/main `5c9b48a56`. Report: `archive/sessions/SESSION_7545_REPORT.md` on the branch.
- **What changes:** `site/app/queues/page.tsx` (a table "[technology]: every grid"; the fold "Every year entered, in requests and MW"; the one-year sentence of the waits chart, `data-chart="years-one"`; the hover on a share withdrawn the file labels none of, `data-none-withdrawn`; ISO-NE's "not held" wait hover, `data-dateless`; the lead's sentence on the operators' lists with two links; the fold's line on loads; "1 request"; "the United States' queues"), `site/lib/queues.ts` (new exports `queueOf`, `noneWithdrawn`, `withdrawnOf`, `onYears`), `site/scripts/check-queues.mjs` (the one-year sentence), `docs/methods/interconnection_queue_summary.md` (section "What the reader meets"). New: `site/scripts/queues-page.mjs`, `site/scripts/test-queues-read.mjs`, `docs/reviews/queues-read-2026-11-16.md`, this report.
- **What does not change:** any table, builder or site data file (`site/data/queues.json`), `replication/queues/`, `site/lib/decisions.ts`, `site/lib/license.ts`, `site/components/Num.tsx`, `site/lib/release.ts`, `check-values.mjs`. No figure moves; the old `data-n` keys are unchanged; new `data-n` keys: `grid|<grid>|<variable>`, `year|<year>|<variable>`, `on|<year>|<variable>`.
- **Before landing:** a site build on the landing machine; `node --import ./scripts/battery-awards-page-register.mjs scripts/test-queues-read.mjs`; `node --import ./scripts/alias-loader.mjs scripts/check-queues.mjs` against the built page; `check-values` on `/queues`.
- **Snapshot differences to expect:** none on the 25 addresses (`/queues` is in review; a visitor is shown the in-review page). **Tables:** none.
- **After the landing:** browser reads 216 to 218; data requests 189 and 190 are the data machine's and do not hold this row.

### (b) Browser reads

| 216 | 2026-11-16 | 7545 | `wip/7545-queues-read` (row 43) | `https://erw-flame.vercel.app/queues?grid=ercot&tech=battery`, at 1280 and at 390 px | The new table "Storage (batteries alone): every grid"; open the fold "Every year entered, in requests and MW" | Ten rows, ERCOT highlighted, ERCOT 120,941, 660, 14.67, 26.67, 3.93 and CAISO 47,499, 170, 10.63, 71.65, 6.84; the fold opens on a table of every year; both tables scroll inside their frames and the page does not scroll sideways at 390 px | wanted |
| 217 | 2026-11-16 | 7545 | `wip/7545-queues-read` (row 43) | `https://erw-flame.vercel.app/queues?grid=ercot&tech=solar_battery`, then `?grid=isone&tech=offshore_wind` | Hover the headline "Withdrawn" 0.00 and the dotted 0.00 in the two tables; on ISO-NE, hover "not held" under "Request to operation" | The hover begins "The file holds no withdrawn and no suspended solar-with-storage requests in ERCOT, in any year, while 1,100 ..."; ISO-NE's says its built requests carry no operation date; the dotted underline is visible | wanted |
| 218 | 2026-11-16 | 7545 | `wip/7545-queues-read` (row 43) | `https://erw-flame.vercel.app/queues` | The lead's links "the interconnection queue explorer" and "the map's Queues tab"; the fold "What the file does not hold", its last line's two links; the waits chart of `?grid=ercot&tech=battery` | The explorer and the map's Queues tab open; `/datacenters` shows ERCOT's large-load status; the All grids tab opens on its table; the waits chart's place holds the 2025 sentence (3.94 years over 37) | wanted |

### (c) Data requests

| 189 | 2026-11-16 | 7545 (chain 304, samueloldlaptop; branch `wip/7545-queues-read`) | `lbnl_interconnection_queue`, `interconnection_queue_summary` (`warehouse/derived/queue_summary.py`) | ERCOT in the 2026 edition: none of its 1,158 withdrawn and 190 suspended requests has a second part (`type_2` empty); all 558 ERCOT requests with one are active or operational. So `queue:ercot:solar_battery` has 66 past requests and `past_withdrawn_share_pct` 0, and the United States' solar-with-storage share counts them. Read Berkeley Lab's note on how ERCOT's withdrawn requests are typed; then mark ERCOT's solar-with-storage shares as not comparable in the builder (or write why they stand). No figure filled by estimate | Queued Up, 2026 edition data file; the read's rows 3 and 4 | requested |
| 190 | 2026-11-16 | 7545 (chain 304, samueloldlaptop; branch `wip/7545-queues-read`) | `interconnection_queue_summary` | Rows of active MW by part type (battery, solar, wind, gas, other storage) for each grid, from each request's `type_1` to `type_3` and `mw_1` to `mw_3`, as the method note's cross-check already sums (544.1 GW of battery parts active in the United States), so `/queues` can give storage with hybrids' batteries beside storage alone | Queued Up, 2026 edition data file; the read's row 13 | requested |

### (d) The progress line (part C)

| `/queues` | lab-desktop | done `<head>` on `wip/7545-queues-read` (landing row 43): the reader a developer choosing which grid's queue to file in (storage, solar with storage, wind, offshore wind), and a large load's energy lead; five cases (a 200 MW battery, ERCOT 120,941 MW active, 26.67 percent withdrawn, 3.93 years, against CAISO 47,499, 71.65, 6.84; solar with storage, ERCOT's 0.00 withdrawn against PJM's 83.33; SPP's requests of 2018, 135 here against the operators' 150 on the explorer; offshore wind, NYISO 4,371 MW and ISO-NE 6,027 MW, no wait held; a 500 MW data center in ERCOT, no load in the file); the All grids tab's counts agree grid by grid (5 of 5); rows: 17 (9 site fixed, 2 data machine, 3 browser, 3 rulings) | 7545 |
