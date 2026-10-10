# Session 183 report: What a generator earns, correctness

10 October 2026, 20:10 to 21:30 UTC, unattended. Branch `wip/183-generator-correct`, landed as merge `38d108ae`. Model spend USD 0, no model call. No pull: no request to any publisher.

## At the top: what was found

- **The inconsistency is fixed and it was real money on the page.** ERCOT solar at the West hub showed USD 59.85 per kW and coverage 0.67 (the hub average's). It now shows USD 47.51 and 0.49.
- **No number of a default page moved.** The main hub keeps its snapshot. Snapshot comparison of the landing: 0 differences on 25 pages.
- **No error found in the model.** The new per-hub builder, run at the main hubs, gives the snapshot to its last decimal for solar, wind and both batteries in ERCOT (99 months), CAISO (25), ISO-NE (20) and SPP (25).
- **A data gap found:** New York's real-time zone history holds 288 of the 744 hours of July 2026, at every zone. New York's "price received" therefore ends June 2026 (as before this session), and so does a New York zone's revenue now. Not fixed: it needs a NYISO pull.
- **The do-file has never been run.** Stata is not on this machine. A test enforces each rule on its text and a Python mirror follows it step for step.
- **Two assertions of `check-seller.mjs` had been failing since session 166** (it read the battery page as a visitor; the page is in review). Fixed.

## Read these first

- The note for your sign-off: `docs/methods/generator_earns_algorithm.md`. Sections 4 (every number), 6 (20 edge cases), 9 (where notes and code differ), 10 (20 items, each with a recommendation).
- The fix: `warehouse/derived/merchant_hubs.py` runs the model's own function with each hub's price; 34 hubs and zones of five grids, 12.6 MB in `site/data/seller/hubs/`.
- The replication reproduces every headline number of the default page from one CSV, to the cent.
- "What is left": 6 closed, 14 open with a recommendation (table below).
- Three things want your ruling soonest: the hub files' upkeep (item 3), the New York gap (item 19), running the do-file (item 18).

## What to review

All in the internal view.

1. `https://erw-flame.vercel.app/cost-of-power/seller`
   - Under the title: a second link, "Every number, step by step". Click it: the new note opens.
   - First headline: "59.85 USD/kW", and under it "Oct 2025 to Sep 2026, priced at the hub average". Third headline: 0.67 times. Both as before.
   - Bottom source line: three downloads, CSV, Stata do-file, Python mirror. Click CSV: a 4.4 MB file downloads.
2. The fix. On the same page, in "Hub or zone" choose "West hub (HB_WEST)", click Show.
   - The sentence now reads "priced at the West hub (real-time prices) earned USD 47.51 per kW".
   - First headline 47.51, with "priced at the West hub (real-time prices)" under it. Third headline 0.49 times.
   - Second headline (price received) 18.47, as before the fix.
   - Scroll to "Month by month": its title ends "at ERCOT HB_WEST, real-time prices".
   - Scroll to "With a battery beside it": one new line, "Both rows are priced at the hub average, ERCOT's main hub, whatever hub is chosen."
   - Open the fold "Stress days": the three events, with the West hub's figures.
3. Day-ahead. Choose "AEN load zone (LZ_AEN)" and asset Wind, Show.
   - First headline 103.23, "priced at the AEN load zone (day-ahead prices)". Coverage 0.63. (The hub average: 83.57 and 0.46.)
4. A peaker at a hub. Choose "West hub", asset Gas peaker, Show: 59.58 (the hub average: 48.15). Set heat rate 9 and variable O&M 3, Show: 77.19.
5. A battery at a hub. Asset Battery at the West hub: 70.75 (the hub average: 58.53).
6. New York. Grid NYISO, asset Wind, hub "WEST zone (WEST)", Show: 120.26, "Jul 2025 to Jun 2026" (the gap above). New York City: 158.47, "Oct 2025 to Sep 2026".
7. Nothing filled. Grid ISO-NE, hub "Maine zone": "ISO-NE holds no twelve months of solar in a row".
8. `https://erw-flame.vercel.app/data/methods/generator_earns_algorithm`
   - Section 5.1: the table of ERCOT's 14 hubs and zones, solar and wind.
   - Section 10: the 20 items.
9. `https://erw-flame.vercel.app/seller/erw_2026_generator_hourly.csv`, `https://erw-flame.vercel.app/seller/erw_2026_generator_replication.do`, `https://erw-flame.vercel.app/seller/erw_2026_generator_replication.py`
   - With Stata: put the do-file and the CSV in one folder, `do erw_2026_generator_replication.do`. It should print 29 lines, among them 59.85, 102.24, 130.80, 23.27, 32.17, -8.90, -27.7, 7,078,769 and 0.67. **Please run it once: nobody has.**
   - Without Stata: `python erw_2026_generator_replication.py` prints the same lines.

## What was built

- **(1) The note.** `docs/methods/generator_earns_algorithm.md`: the order of computation, the inputs, the model hour by hour, every number in page order (18 blocks), another hub, 20 edge cases, the assumptions with sources, the replication, 9 differences between notes and code, 20 items for ruling. Covers the capture price, the fleet shape, the hybrid's co-optimization and both upper bounds, the contract, the debt default.
- **(2) The replication** (built by an agent to a written brief; I checked its tests and its files).
  - `warehouse/derived/generator_hourly_export.py`: refuses to write unless the rows give the snapshot's months (100 of 100) and the capture file's months (94 of 94).
  - `site/public/seller/erw_2026_generator_hourly.csv`: 72,384 hours, July 2018 to 3 October 2026, 4,366,876 bytes.
  - `site/public/seller/erw_2026_generator_replication.do` and `.py`.
  - `tests/test_session183_replication.py`: 36 tests.
  - Reproduced, equal to the page: 59.85; 102.24; 130.80; 23.27, 32.17, -8.90, -27.7 percent; 7,078,769; 0.67; 99 months; median 550,484.85; 10th percentile 240,213.49; the year's average 12,216,826.39; the worst three; 62 and 71 months; 88 windows, lowest 0.65, 33 and 36.
  - One CSV serves both capture prices: for ERCOT's hub average the capture file's price and generation equal the model's on all 67,943 hours.
- **(4) The fix.**
  - `warehouse/derived/merchant_hubs.py` (new), `merchant_revenue.py` (`build_iso` takes a hub's price when given one; unchanged otherwise).
  - `site/lib/sellerhubs.ts` (new), `site/app/cost-of-power/seller/page.tsx`, `site/lib/seller2.ts` (the sentence names the hub), `site/next.config.ts` (the hub files reach the server).
  - One market for each hub: the market its capture price is shown in. Day-ahead for ERCOT's AEN, CPS, LCRA and RAYBN load zones and for SPP South.
  - The battery beside the plant and the pasted profile stay at the main hub, and the page says so.
  - Tests: `tests/test_session183.py` (18), `site/scripts/test-seller-hubs.mjs` (2,636 checks), `site/scripts/check-seller-face.mjs` (24, at 1280 and 390 px).

## (3) What is left, item by item

| # | Item | From | State |
|---|---|---|---|
| 1 | Hours rule for the capture price | 145 | Closed: you ruled, 7 October |
| 2 | SPP South and New York's zones had no year | 145 | Closed by session 149 |
| 4 | ISO-NE's zones hold weeks | 145, 149 | Closed as ruled (internal) |
| 14 | The page on a phone | 162 | Closed tonight: 390 px, no sideways scroll, three addresses |
| 15 | Status documents naming the old address | 145, 162 | Closed tonight: `docs/tools.md` updated; `platform-tools.md` names none; `state_2026-10-04.md` is a dated record, left |
| 20 | `check-seller.mjs` failing since session 166 | 166 | Closed tonight |
| 3 | No builder of this page is scheduled | 145, 149, 162 | Open. Recommend adding the snapshot, hybrid and hub files to `run_data_machine.sh`, monthly, when you register it |
| 5 | A month enters the last twelve months at 90 percent | new | Open. Recommend whole months only. Moves nothing today |
| 6 | "Price of every hour" weighs months, not hours | new | Open. Recommend hours (32.10 becomes about 32.17) |
| 7 | A battery over four hours is priced as four | new | Open. Recommend limiting the field to 4 hours |
| 8 | Two capture prices on one page (23.27 and 23.20) | 145 | Open. Recommend one, or the label "model" |
| 9 | The hybrid's two rows and "upper bound" on row 2 | 162 | Open, your word. Recommend keeping both |
| 10 | 17 yearly price files are public addresses | 162 | Open, your word. Recommend leaving them |
| 11 | The hybrid has no chart | 162 | Open. Recommend one chart of a day; a session |
| 12 | The pair is built for ERCOT and CAISO only | 162 | Open. Row 1 needs no reserve prices: recommend NYISO, ISO-NE, SPP |
| 13 | The pair and the profile are at the main hub | 145, 162 | Open. Recommend the hub chosen, with item 12 |
| 16 | New York City's model begins September 2024; its zones' in 2019 | new | Open. Recommend rebuilding the snapshot from the histories (moves default pages of four grids) |
| 17 | ISO-NE Internal hub: revenue real time, price received day-ahead | new | Open. With item 16 |
| 18 | The do-file has never been run | new | Open. Yours |
| 19 | New York's real-time history: 288 of 744 hours of July 2026 | new | Open. A NYISO pull: your approval, after your ruling on NYISO's terms |

## Numbers on the page, before and after

| Number | Before | After | Expected |
|---|---|---|---|
| Every number at a main hub (default pages) | as the snapshot | the same; 1,398 of 1,398 checked values | yes |
| Revenue, months, coverage, stress days at another hub | the main hub's | the hub's own (34 hubs) | yes, the fix |
| ERCOT solar, West hub: revenue, coverage | 59.85, 0.67 | 47.51, 0.49 | yes |
| ERCOT wind, AEN load zone | 83.57, 0.46 | 103.23, 0.63 (day-ahead) | yes |
| Capture price, contract price, hybrid, profile | | unchanged | yes |
| Lead: link "Every number, step by step"; three downloads | absent | present | yes |
| Hybrid section at another hub: one line naming the main hub | absent | present | yes |

## Pulls and spend

- Outside hosts: 0 requests. No MISO, no PJM, no NYISO request.
- Supabase: anon reads only, through the builds and checks.
- Model spend: USD 0 of 0. No model call.
- Nothing under the data lock: no warehouse table written, no load, no migration.

## Checks run

Outputs under `runs/session183/`.

| Check | Exit | Result |
|---|---|---|
| Per-hub builder (`hubs_trial.out`, `hubs_check.out`) | 0, 0 | 34 hubs; main hubs equal the snapshot |
| `test-seller-hubs.mjs` | 0 | 2,636 checks |
| `tests.test_session183`, `_replication`, and sessions 51, 107, 145, 162, 178 | 0 | 137 tests |
| Site build, first; and of the committed tree | 0, 0 | `build1.out`, `build2.out` |
| `check-seller.mjs`, local | 1, then 0 | first run: 4 failed (2 expected the old behavior, 2 failing since session 166); after the fix 43 of 43 |
| `check-seller-deeper.mjs`, local | 0 | 51 of 51 |
| `check-seller-face.mjs`, local | 0 | 24 of 24 |
| `check-routes`, local | 0 | 0 failed |
| `check-values`, full, twice (first build) | 0, 0 | 6,957 of 6,957 both times |
| `check-values`, seller pages (final build) | 0 | 1,398 of 1,398 |
| Whole suite, clean copy at `47dca2f4` | 1 | 1 failed: session 138's test pinned the old tracing line |
| Whole suite, clean copy at `5d76eeeb` | 0 | 3,062 tests, 233 skipped |

- Not run again on the final build: the full `check-values` (the final build differs from the first by the note's text and a check script).

## The landing

- No freeze (`freeze.py status` exit 0). `origin/main` had not moved.
- `183_before` at 20:56:53 UTC, its own command, exit 0, 25 pages.
- Pushed `task/183-generator-correct` (`5d76eeeb`) at 20:57:04. "code branch" run 38085741988: success. Merge `38d108ae`.
- Vercel production: "Deployment has completed" at 21:07:42 UTC.
- `183_after` at 21:07:55 UTC. Comparison: **0 differences on the 25 pages** (`compare_183.out`, exit 0). Expected: every page is in review, so a visitor sees the in-review page before and after.
- On production, internal view: `check-seller-face` 24 of 24, `check-seller` 43 of 43, `check-seller-deeper` 51 of 51 (`prod_check_*.out`). The hub files are read on Vercel.
- The task branch was removed by the workflow. `wip/183-generator-correct` is deleted once this report is on main.

## Decisions made without you

- **One market for each hub, the capture price's.** So revenue and the price received beside it are on one market. The other choice (always real time) would leave five hubs with no figure.
- **The main hub keeps the snapshot.** The reversible choice: no default number moves. The cost: New York City and its zones read different real-time tables (item 16).
- **The battery and the peaker follow the hub too.** The form offers the hub for all four assets.
- **12.6 MB of hub files in git**, one file a hub (each under 0.6 MB), read one at a time by the server. Needed for the peaker at the reader's heat rate. Not added to any schedule.
- **The hub files were built once and copied from the trial folder**, then their main-hub check was run again with the stricter rule (compare a month only when both hold the same hours).
- **The peaker differs from the snapshot in September 2026** at ERCOT, CAISO and SPP (0.2 to 0.4 percent): Henry Hub's prices of 30 September onward arrived after the snapshot was built. Left as it is, and said in the note.
- **`check-seller.mjs` changed**: two expectations followed the fix; one read of the battery page now carries the internal cookie.
- **`tests/test_session138.py`: one assertion loosened**, with a comment (it pinned a line of `next.config.ts` that gained an entry).
- **The replication CSV holds the whole history**, not twelve months, so the long-run averages and the bad months rebuild from it. 4.4 MB.
- **Not done, to keep the tool what it is:** no change to the model, to the 90 and 95 percent rules, to the capture price or to the hybrid. Items 5 to 8 are recommendations only.
- **This report reaches main by a second push** (`task/183-report`) with its own before and after snapshot. It changes this file only. If that comparison shows any difference, a line is added at the very top of this report; no such line means 0 differences.

## To finish

- Run the do-file in Stata once (Samuel).
- When the snapshot or the capture file is rebuilt: `python warehouse/derived/generator_hourly_export.py`, commit the CSV; then `python warehouse/derived/merchant_hubs.py --cache-dir runs/hub_cache` (about 10 minutes), commit `site/data/seller/hubs`. No lock: both read `warehouse/output` and write site files.
- Rule on items 3, 16 and 19.

## The prompt

"Session 183 (long end 3:00): What a generator earns (/cost-of-power/seller), correctness, exactly as session 178 did for the battery: (1) docs/methods/generator_earns_algorithm.md written for Samuel to read and sign off, every number on the page, how it is computed, from which tables and rows, every assumption and edge case, including the capture price, the fleet shape, the hybrid's co-optimization and its upper bound, the contract, the debt default. (2) A replication: export the default case's hourly prices and fleet output as CSV; a Stata do-file to Samuel's rules that reproduces every headline number from it; a Python test that the CSV and the page agree. (3) Every "what is left" item from this tool's reports (145, 149, 162) closed or listed with your recommendation. (4) The known inconsistency fixed: choosing another hub must change revenue and debt coverage too, not only the capture price and the contract. Land, report in short bullets with click-by-click steps, stop." Unattended; the rules of CHAIN_OCT8_PROMPT.md and CHAIN_OCT10_PROMPT.md; model spend USD 0; no pull; deploys allowed.
