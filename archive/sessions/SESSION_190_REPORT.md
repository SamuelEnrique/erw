# Session 190 report: What a datacenter pays, correctness

11 October 2026, 07:05 to 08:25 UTC, unattended, one agent of a chain. Branch `wip/190-datacenter-correct` (worktree `erw-190`), not pushed: the orchestrating session lands it. Model spend USD 0, no model call. No pull: no request to any publisher. Follows session 183's shape (the later precedent) where 178 and 183 differ: two test modules, the note's sections, a face check on the shared browser helper.

## Read these first

- **No error found in the default case, and no number of the page moved.** Each of its 103,055 hours equals the price tables to half a cent; the page, the CSV, the Python mirror and a second implementation of the rule agree. The page gained one link and three downloads.
- **Finding 1, for your ruling: in a year held in part, "if perfectly foreseen" gets fewer hours than the rule** (at the North load zone 76 against 100 for 2026). On the page today, New York City, real time, 100 hours, the year 2026: the rule 63.93 against "if perfectly foreseen" 63.97. At the North load zone "the rule kept 57 percent" would read 51. Not changed: it moves numbers and there are two ways to align.
- **Finding 2: New York's real-time "last twelve months" are stuck at July 2025 to June 2026**, and will stay there until July 2027 is held, because July 2026 lacks 19 days and the window needs twelve months in a row. Day-ahead is whole.
- **The do-file has never been run.** Stata is not on this machine. A test enforces each rule on its text; a Python mirror follows it step for step and prints the same 30 lines.
- **"What is left": 31 items of the three reports. 18 closed (2 of them in this session), 11 open, each with a recommendation, 1 your own step, 1 not this tool's**; and 6 new ones. The note for your sign-off: `docs/methods/datacenter_pays_algorithm.md`, sections 4 (every number), 6 (20 edge cases), 10 and 11.

## What to review

All in the internal view.

1. `https://erw-flame.vercel.app/cost-of-power`
   - Under the title: a second link, "Every number, step by step". Click it: the new note opens.
   - The sentence: "A flat 100 MW load at LZ_NORTH in ERCOT, buying real time, paid USD 33.73 per MWh over the last twelve months, USD 29.55 million in all: USD 0.0684 per GPU-hour for power alone." As before.
   - Three headlines, as before: "USD 33.73 per MWh" (USD 29.55 million for 876,000 MWh, Oct 2025 to Sep 2026); "USD 37.88 per MWh" (August 2026; one month in ten of the 36 held from October 2023 to September 2026); "USD 0.0684" (100 MW powers 49,310 GPUs).
   - In "What will it cost": "The hub beside it, HB_NORTH, a flat load" reads 32.51, "the load zone is 1.22 per MWh above its hub". As before.
   - Bottom source line: "The default case hour by hour: CSV, Stata do-file, Python mirror." Click CSV: a 5.0 MB file downloads.
   - The first tab reads "What a datacenter pays". Click "What a battery earns": the first tab still reads "What a datacenter pays" (it read "What power costs to buy" there until now).
2. Finding 1. `https://erw-flame.vercel.app/cost-of-power?grid=nyiso&region=N.Y.C.&mw=100&run=hours&n=100&buy=rt`
   - Open the fold "Every year". The row 2026: "This load" 63.93, "If perfectly foreseen" 63.97. The foreseen figure is the dearer one.
   - Then `https://erw-flame.vercel.app/cost-of-power?grid=ercot&region=LZ_NORTH&mw=100&run=hours&n=100&buy=rt`: the sentence reads 31.46, "USD 2.27 per MWh less than a flat load (USD 4.01 if perfectly foreseen)"; in the table, "the rule kept 57 percent of it". With the foreseen load given the rule's hours it would read 4.44 and 51 percent.
3. Finding 2. `https://erw-flame.vercel.app/cost-of-power?grid=nyiso`
   - The first headline reads "USD 68.49 per MWh", "Jul 2025 to Jun 2026". Choose "Day-ahead", Show: 73.10, "Oct 2025 to Sep 2026".
4. `https://erw-flame.vercel.app/data/methods/datacenter_pays_algorithm`
   - Section 4.2: the twelve months by hand. Section 5.3: one day of the rule by hand (20 January 2026). Section 10: the 16 items. Section 11: the findings. Then the sign-off block.
5. `https://erw-flame.vercel.app/datacenter/erw_2026_datacenter_hourly.csv`, `https://erw-flame.vercel.app/datacenter/erw_2026_datacenter_replication.do`, `https://erw-flame.vercel.app/datacenter/erw_2026_datacenter_replication.py`
   - With Stata: put the do-file and the CSV in one folder, `do erw_2026_datacenter_replication.do`. It should print 30 lines, among them 33.73, 29,546,505, 876,000, 0.0684, 49,310, 32.51, 1.22, 35.33, twelve years from 24.04 (2015) to 34.02 (2026) with 150.61 for 2021, and "a bad month, nearest rank 4: 2026-08, USD per MWh: 37.88". **Please run it once: nobody has.**
   - Without Stata: `python erw_2026_datacenter_replication.py` prints the same lines.

## What was built

- **The note.** `docs/methods/datacenter_pays_algorithm.md`: the order of computation, the inputs, the price of an hour (tables, columns, filters), every number in page order with its formula and a worked example, the flexible load with one day by hand, 20 edge cases, the assumptions with sources, the replication, 9 differences between notes and code, 16 items for ruling, 4 findings, the sign-off block.
- **The replication.**
  - `warehouse/derived/datacenter_hourly_export.py`: reads the page's own files (standard library only, no table, no lock); refuses to write unless the rows give back every hour and every month the page computes; `--tables DIR` sets every hour against the price tables.
  - `site/public/datacenter/erw_2026_datacenter_hourly.csv`: 103,055 hours, 1 January 2015 to 3 October 2026, 5,001,368 bytes. Columns: the zone's real-time and day-ahead price, the hub's real-time price, the flag of the twelve months.
  - `site/public/datacenter/erw_2026_datacenter_replication.do` and `.py`.
  - `tests/test_session190_replication.py` (36 tests) and `tests/test_session190.py` (10 tests).
  - Reproduced, equal to the page: 33.73; USD 29,546,505 (shown 29.55 million); 876,000 MWh; 0.0684; 49,310 GPUs; the hub 32.51 and 1.22; day-ahead 35.33; the twelve years; the bad month, August 2026 at 37.88, rank 4 of 36.
  - Beyond the do-file: the rule and the foreseen load written a second time in Python from the note, on the CSV alone, equal to the page's library for eight loads (hours off, and price to 1e-9).
- **The page.** `site/app/cost-of-power/page.tsx` (the link, the three downloads), `site/lib/release.ts` (the note's line, `review`; a stale comment corrected), `site/scripts/check-routes.mjs` (the note's address), `site/scripts/check-datacenter-face.mjs` (new: 23 assertions at 1280 and 390 px).
- **Closed items.** `site/app/cost-of-power/Tabs.tsx` (the three tabs read alike), `warehouse/run_data_machine.sh` (the export follows the rebuild of the page's files).
- **Older documents.** `docs/methods/datacenter_cost.md` (a pointer, and three statements brought up to date), `docs/tools.md`.

## What is left, item by item

In the reports' words. "Closed" names who closed it and the evidence.

| # | Item, in the report's words | From | State |
|---|---|---|---|
| 1 | "Your ruling on the Texas tariffs' terms (item 2), and on ISO-NE's demand (item 4, with session 136's row)" | 138 | Closed by session 140 ("Rulings applied"). Today: 41 charges of four utilities in the page's file; ISO-NE's demand `withheld` in the index |
| 2 | "ERCOT's regions are its six trading hubs ... A pull of ERCOT's load zone prices ... needs your approval" | 138 | Closed by session 140 (a): `ercot_zone_prices_history`; the default region is `LZ_NORTH` |
| 3 | "The zones of NYISO and ISO-NE, CAISO's ZP26 and SPP South have six weeks of prices ... A history pull for them needs your approval" | 138 | Closed by sessions 140 (b) and 149: NYISO from 2019; ZP26 day-ahead from 26 June 2023; SPP South day-ahead from 2019; ISO-NE's zones internal by your ruling |
| 4 | "The Commission's transmission cost matrix (item 3)" | 138 | Closed by session 140 (c): 45 figures in the page's file |
| 5 | "The two labels after the freeze (item 5)": the tab on the battery page | 138, 140 | **Closed in this session** (`6835d806`): the three tabs read alike; `tests/test_session138.py` follows |
| 6 | The same: "the menu still says 'Cost of power'"; "The page's `/learn`, home and menu texts that name the old tab are unchanged" | 138 | Open. One line of `site/lib/pages.ts`, one of `site/app/page.tsx`, two of `site/lib/problems.ts`. A visitor sees the menu on every page: recommend a landing of its own, with 25 expected snapshot differences |
| 7 | "A flexible load judged on a forecast, not on hindsight. Not built"; "Say how a flexible load's upper bound should be said" | 138 | Closed by session 140 (d): the rule is the figure, "if perfectly foreseen" beside it with a hover |
| 8 | "The reader's own hours against clean generation ... and NYISO's load queue (published, not read)" | 138 | Closed by session 140 (f), (e); the queue rows then held by your ruling (session 149) |
| 9 | "The first Saturday run on the runner (10 October) is the first there ... that rule is tested here and not yet seen on the runner" | 138, 140 | **Closed in this session**, by the commit of that run (`2cb3fe5c`) against its parent: 2,376 hours added to the five 2026 files, 0 removed, 0 changed, no region gone (`runs/session190/saturday_run.out`) |
| 10 | "A full `build_coverage.py` fails on this machine: `census_metro_population` names a source that is only on the branch" | 138 | Closed by a later session: `census:popest_cbsa` is in `sources.csv` and the table in `coverage.csv` on main. The full build was not run here (no tables in the worktree) |
| 11 | "`check-values`, locally ... 8 values elsewhere do not ... I did not find their cause" | 138 | Not this tool's. Today's full run: see "Checks run" |
| 12 | "Texas-New Mexico Power's tariff file is dated 29 December 2025 and may be superseded"; "probably superseded" | 138, 140 | Open. A pull of its current tariff: your approval. Its site refused the request once |
| 13 | "ISO-NE's hour convention is not confirmed" | 138 | Closed by session 140's hour check (hour ending, Eastern prevailing time) |
| 14 | "Oncor's energy efficiency factor as the model read it is the wrong column" | 138 | Closed as built: not shown; session 140 left out CenterPoint's too |
| 15 | "Your ruling on ISO-NE's zone prices (show, or keep internal)" | 140 | Closed: ruled 7 October 2026, internal; applied in session 149 |
| 16 | "SPP South's year: when the background pull ends ..." | 140 | Closed by session 149: day-ahead from 1 January 2019 (68,159 hours in the index) |
| 17 | "Your ruling on the budget of hours (keep, or the threshold alone)" | 140 | Closed: ruled 7 October 2026, the budget stays. See new item 32 |
| 18 | "Your ruling on refreshing ERCOT's load zones (the ceiling)"; "Their hours stop at 3 October 2026 until you rule" | 140 | Ruled 7 October and written by session 149. **Open in effect:** `run_data_machine.sh` is registered nowhere, so the hours still stop at 3 October. Recommend registering it. Until then the default page's twelve months do not move |
| 19 | "Confirm NYISO's terms for the queue rows" | 140 | Closed: ruled 7 October, applied in session 149 (the rows are held) |
| 20 | "the 2026 matrix needs its order"; "The 2026 transmission matrices are not approved" | 140 | Open. Marked "filed, not approved" on the page. A pull of Docket 59080's list: your approval |
| 21 | "The check on production (below): passed in the internal view" | 140 | Closed then |
| 22 | "CAISO serves ZP26's day-ahead only from 26 June 2023" | 140 | Closed as it stands: the source holds nothing earlier |
| 23 | "NYISO's own archive of hourly real-time prices lacks 19 days of July 2026" | 140 | Open, and larger than it read: finding 2. A NYISO pull after your ruling on NYISO's terms; or, with no pull, show day-ahead first for New York |
| 24 | "ERCOT's load zones: day-ahead for all eight, real time for four" | 140 | Open as built: real time for the four municipal and cooperative zones would pass the ceiling. Recommend leaving it |
| 25 | "Open `/cost-of-power` in the internal view and try ..." | 138, 140 | Yours. The steps above |
| 26 | "Your ruling on the two-request figure" | 163 | Open, yours. Recommend keeping it: the count and the group's two ends |
| 27 | "Bonneville and Alberta (session 165) are on none of the page's grids ... A line of `ENTITY_GRID` would place a new entity" | 163 | Open. Recommend leaving them off: the page's grids are the seven markets, and both entities' terms wait for your word (session 165) |
| 28 | "Stated waits are also held for CAISO (2), ISO-NE (4), SPP (2) and PJM (4, from PJM's own site): not shown" | 163 | Open. Recommend showing them as Texas's are, each labeled whose it is: a page change, a session |
| 29 | "The time spent in each status, in NYISO's own words (156 rows), is not on the page" | 163 | Open. Recommend leaving it off while NYISO's terms hold the rows |
| 30 | "One page check failed on the merged build, and the fault was the check's" | 163 | Closed then. Today `check-how-soon` passes 41 of 41 |
| 31 | "No sentence of any entity is shown" (`SHOW_SENTENCE_REGULATORS`, empty) | 163, 154 | Open, yours: each regulator's terms. No recommendation beyond session 154's |
| 32 | New: a year held in part gives the rule 100 hours and the foreseen load 76 (finding 1) | 190 | Open. Recommend the foreseen load take the rule's budget in such a year. Moves the foreseen figures of the current year and the last twelve months, for every load that turns off; no headline of a flat load |
| 33 | New: a month enters the last twelve months at 95 percent (its 30th day of 31) | 190 | Open. Recommend whole months only for the headline, as for the battery and generator pages. Moves nothing today |
| 34 | New: the do-file has never been run | 190 | Open. Yours |
| 35 | New: "How clean" reads 2024 for ERCOT while the tight hours read 2025 (the mix tool's table holds eleven months of 2025) | 190 | Open. Each row names its year. Recommend looking at the mix tool's missing month, not at this page |
| 36 | New: `datacenter_page.py --in-dir` moves the price tables only; demand, clean hours and delivery are read from the machine's own `warehouse/output` | 190 | Open. No number affected. Recommend one line each when the builder is next changed |
| 37 | New: `check-routes` fails on `/prices` on the unchanged tree (28 "no data" blocks against production's 25) | 190 | Not this tool's. The daily load of 10 October failed (`supabase_load: connector exit 1`); a local build reads the live set as it is now |

## Decisions made without you

- **The CSV holds the whole history, 2015 on, and three price columns**, so that the by-year figures, the hub beside the zone and a flexible load can all be rebuilt from one file. 5.0 MB.
- **The exporter reads the page's files, not the tables.** So it runs on any machine and the CSV is the page's own data by construction; the tables were checked once here, read only from the main copy (`--tables`), and a test repeats that check wherever the tables are.
- **Hours are given as `hour_utc` and `std_month`**, not as a local day: the page counts in standard time.
- **The do-file covers the flat default case.** The flexible load is rebuilt by the test, not in Stata: 80 lines of unrun Stata for a rule with a rolling window seemed worse than none.
- **No figure is pinned in the tests but under the window October 2025 to September 2026.** When the page's files move on, the tests still hold the CSV, the mirror and the library to each other; the note's worked examples become a dated record and their test skips, saying so.
- **The data machine's run now exports the CSV after it rebuilds the page's files** (`run_data_machine.sh`, one step, one path). Without it the test would fail the day that run is registered. No workflow was touched: the runner's Saturday build adds no hour of the default case.
- **The tab on the battery page was changed** (item 5). The freeze ended on 7 October and that page is in review; a visitor sees no difference.
- **The menu label was not changed** (item 6): it is what a visitor sees on every page.
- **Finding 1 was not fixed.** The pro-rating is session 138's stated decision and the whole-year budget session 140's.
- **`release.ts`: one comment corrected** ("Three pages are open" stood since session 166 made them review). No status changed.
- **The older Method note was amended in four places**, each marked with its session; nothing was removed.
- **`tests/test_session138.py`: one test follows the tab** (it pinned the frozen label).
- **The do-file names the delimiter** (`delimiter(comma)`). The battery's and the generator's do-files do not, and their CSVs also begin with comment lines that hold no comma, so Stata is left to find the delimiter. Not touched (other tools); worth a look when one of them is first run.

Rulings that wait for you: items 6, 12, 18, 20, 23, 26 to 29, 31 to 34.

## What surprised me

- The route check failed on the unchanged tree and passed an hour later on the final one: `/prices` counts "no data" blocks against production, and the live set moved between the two (the load of 10 October had failed).
- The foreseen load is not a bound of the rule in a year held in part (finding 1): the page's own label is contradicted in one row of one fold.
- One incomplete month freezes a "last twelve months" for a year (finding 2).
- "How clean" stands on 2024 for ERCOT; session 140's report quoted 2025.
- The full value check passes today (6,937 of 6,937): the reader session 178 found missing is there.
- The whole suite leaves `warehouse/output/raw/madeup_as_prices/` behind in the copy it runs in (`tests/test_session85.py` writes a manifest there). Untracked; removed from the worktree; the main copy shows the same folder.

## Pulls and spend

- Outside hosts: 0 requests. No MISO, no PJM, no NYISO, no ERCOT request.
- Supabase: anon reads only, through the local builds and the page checks.
- Model spend: USD 0 of 0. No model call.
- Nothing under the data lock: no warehouse table written, no load, no archive, no Redivis. The main copy's `warehouse/output` was read only.
- Nothing for the data machine to run: the export needs no table.

## Checks run

Outputs under `runs/session190/` in the worktree. The site was built three times under the build mutex (`npm ci` once).

| Check | Exit | Result |
|---|---|---|
| Exporter (`export.out`) | 0 | 103,055 rows, 142 months, 5,001,368 bytes |
| Exporter with `--tables`, the main copy's tables read only (`export_tables.out`, `tables_check.out`) | 0 | 103,055 hours in each of three series; 0 differ by more than half a cent; 0 held on one side only |
| Python mirror (`replication_mirror.out`) | 0 | 30 lines |
| `tests.test_session190_replication`, `tests.test_session190`, worktree, no tables | 0 | 46 run, 1 skipped (the tables) |
| The same with `ERW_TABLES_DIR` on the main copy's tables (`tests_190_tables.out`) | 0 | 46 run, 0 skipped; the table test takes 18 seconds |
| With sessions 138, 140, 149, 163, 178, 183 (`tests_neighbours.out`) | 0 | 247 run, 9 skipped |
| Whole suite, worktree, `ERW_LOCK_EXEMPT=1` (`suite.out`) | 0 | 3,131 tests, 221 skipped, on commit `09961c4e` (this report's last lines were filled in after it) |
| Site build: unchanged tree (after `npm ci`, exit 0); changed tree; final tree twice | 0, 0, 0, 0 | `build_before.out`, `build_after.out`, `build_final.out`, `build_final2.out` |
| **Before any change:** `check-datacenter` | 0 | 58 of 58 |
| `check-how-soon` | 0 | 41 of 41 |
| `check-values`, pages under `/cost-of-power`, twice | 0, 0 | 3,289 of 3,289 both times |
| `check-routes` | 1 | 1 failed, not this tool's: `/prices` showed 28 "no data" blocks against production's 25 |
| **Final build:** `check-datacenter-face` (new), 1280 and 390 px | 0 | 23 of 23 |
| `check-datacenter` | 0 | 58 of 58 |
| `check-how-soon` | 0 | 41 of 41 |
| `check-values`, pages under `/cost-of-power`, twice | 0, 0 | 3,289 of 3,289 both times |
| `check-routes`, internal view and visitor view | 0 | 160 of 160 pages; 159 in review asked as a visitor, 0 failed |
| The page as text, 17 addresses and the visitor's (`before/`, `final/`) | 0 | only the lines listed below differ |
| **On the build before the last** (it differs by the do-file's import line and the CSV's last header line): `check-values`, full, twice | 0, 0 | 6,937 of 6,937; then 6,906 with 31 latest prices superseded within 45 minutes, which the check allows |
| `check-battery-face`, `check-seller-face` (the tab) | 0, 0 | all passed |

- At 390 px the lead reads "Method note. Every number, step by step." over two lines, the second link breaking after "Every"; the source line ends "The default case hour by hour: CSV, Stata do-file, Python mirror. Method note." Nothing passes the page's width (`shots/`).

## Numbers on the page, before and after

Captured as text from 17 addresses of the page in the internal view and one as a visitor, on the unchanged build and on the final build (`runs/session190/before/`, `after/`).

| Number | Before | After | Expected |
|---|---|---|---|
| Every number of the 17 addresses (flat, off in hours, a share, shifting; ERCOT, New York, California, ISO-NE, SPP; MISO, PJM; "Grid by grid") | as captured | the same: no line with a figure differs | yes |
| The visitor's page | the in-review page | the same, 0 lines differ | yes |

Visible lines that changed, internal view only:

- `/cost-of-power`, every address of the view "Your load" (16 captured): the lead gains " Every number, step by step." after "Method note."; the source line gains "The default case hour by hour: CSV, Stata do-file, Python mirror." before "Method note."
- `/cost-of-power?view=grids`: the lead gains the same link. Its source line is its own and did not change.
- `/cost-of-power/battery`: the first tab reads "What a datacenter pays" (was "What power costs to buy").
- `/data/methods/datacenter_cost`: one new paragraph under the opening, and three amended sentences.
- New addresses: `/data/methods/datacenter_pays_algorithm` (in review) and the three files under `/datacenter/` (public files, as the battery's and the generator's are).
- For a visitor: no page differs. The three files under `/datacenter/` answer a visitor too.

## To finish

- Run the do-file in Stata once (Samuel).
- When the page's files gain or change an hour of the default case and `tests/test_session190_replication.py` fails: `python warehouse/derived/datacenter_hourly_export.py`, commit `site/public/datacenter/erw_2026_datacenter_hourly.csv`. No table, no lock, any machine. The data machine's run does it itself once registered.
- When the twelve months move on: the note's worked examples (sections 4.2, 4.4, 5.3) are of 11 October 2026; their test skips and says so.

## Landing

LANDING: filled in by the orchestrating session

## The prompt

"Session 190 (long end 3:00): What a datacenter pays (/cost-of-power), correctness, exactly as sessions 178 and 183 did: the algorithm note for Samuel's sign-off, the CSV export and Stata replication of every headline number with a test, and every "what is left" item from sessions 138, 140 and 163 closed or listed with a recommendation. Land each." Unattended; the rules of CHAIN_OCT8_PROMPT.md; model spend USD 0; no pull; built in a worktree by one agent of a chain, landed by the orchestrating session.
