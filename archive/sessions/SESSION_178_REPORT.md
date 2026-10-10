# Session 178 report: What a battery earns, correctness

10 October 2026. Branch `wip/178-battery-correct` (worktree `erw-144`). Not pushed. Model spend USD 0. No request to an outside host.

## At the top: what was found

- **No error in the model.** Its daily revenue equals an independent optimum on every one of 1,096 days (36 months, default case). Largest gap USD 0.00000003 per MW and day. Never above the optimum, never below.
- **No number on the page moved.** One line was added (three numbers). 1,808 of 1,808 values on the seven battery addresses equal the live set.
- **Stata is not installed on this machine** (`where stata`: not found; no Stata folder under `C:/Program Files`, `C:/Program Files (x86)` or `C:/`). **The do-file has never been run.** A test enforces each rule on its text; a Python mirror follows it step for step and reproduces the page.
- **Defects found outside this session's work, all on main before it:**
  - `site/scripts/check-values.mjs` stops with `unknown check datacenters|counted`. Session 166 F gave `/datacenters` three new keys (`counted`, `no_us_state`, `cancelled`) and the check has no reader for them. **The full value check cannot pass on main today.** Not fixed here (another tool). The battery pages were checked on their own (below).
  - `site/scripts/test-battery-stack.mjs` opens the page as a visitor. Since session 166 a visitor gets the in-review page, so it stops at its first assertion. Not rewritten here; `check-battery-face.mjs` (new) covers the page's face in the internal view. The contract's no-request assertions are not covered by anything that runs today.
  - `tests/test_session92.py` expected the battery page to be `live`. It failed on any machine with the site's packages (GitHub skips it). **Fixed**: one assertion.
  - The seven finding do-files in `site/public/findings/` read `varnames(1)`, and each CSV begins with four `#` lines. As written they would take a comment line for the column names. Not touched (their CSVs are hash-pinned, another session's tool). Ruling wanted.

## Read these first

- The ratio: the model's day-ahead ancillary revenue is **5.66 times** ERCOT's real storage awards (default case; January to July 2026; USD 2.25 against 0.40 per kW a month).
- Why: the model sells more megawatts, not at better prices. It holds 142 percent of its power in awards in the mean hour; the fleet held 21.6 percent of its MW.
- The optimizer check: largest absolute gap USD 0.00000003 per MW and day; largest relative gap 3.2e-10; 0 days above, 0 below.
- "What is left": 4 closed tonight, 1 partly, 23 report entries already closed by earlier sessions, 35 open, each with a recommendation or marked for your ruling.
- Two edge cases need your ruling (below): a month enters the last twelve months before it ends; the first hour of each day can hold no upward reserve.

## What to review

1. `https://erw-flame.vercel.app/cost-of-power/battery` (internal view)
   - Under the title: a second link, "Every number, step by step". Click it: the new note opens.
   - Scroll to "Income by stream". Under the table: one sentence, "Day-ahead ancillary services, January 2026 to July 2026: this model takes USD 2.25 per kW a month; ERCOT's storage resources were awarded USD 0.40 per kW of their power a month; the model is 5.66 times the awards."
   - Click "8 hours", then "Day-ahead schedule" and Show: the sentence reads 1.86, 0.40 and 4.69.
   - Click CAISO and Show: the sentence is gone (ERCOT only).
   - Bottom source line: three downloads, CSV, Stata do-file, Python mirror. Click CSV: a 4.3 MB file downloads.
   - Every other number: as before.
2. `https://erw-flame.vercel.app/data/methods/battery_earns_algorithm` (internal view)
   - Section 4: every number in page order. Section 5: edge cases. Section 9: the awards. Section 10: where the notes and the code differ. Section 11: for session 179.
3. `https://erw-flame.vercel.app/battery/erw_2026_battery_dispatch.csv`, `https://erw-flame.vercel.app/battery/erw_2026_battery_replication.do`, `https://erw-flame.vercel.app/battery/erw_2026_battery_replication.py`
   - With Stata: put the do-file and the CSV in one folder, `do erw_2026_battery_replication.do`. It should print 81.40, 33, 6,783,357, 0.88, 8,140,219 and December 2024 at 475,477. **Please run it once: nobody has.**
   - Without Stata: `python erw_2026_battery_replication.py` prints the same lines.

## What was built

- `docs/methods/battery_earns_algorithm.md`: the note for sign-off. Written from the code.
- `warehouse/derived/battery_dispatch_export.py`: the exporter. Solves each day with the model's own `solve_day`; refuses to write unless every month equals `battery_stack_monthly` to half a cent per MW.
- `site/public/battery/erw_2026_battery_dispatch.csv`: 26,304 hours, 1,096 days, 36 months (October 2023 to September 2026), 4,266,963 bytes, in git. 14 provenance lines. `in_last_twelve` marks October 2025 to September 2026.
- `site/public/battery/erw_2026_battery_replication.do` and `.py`: the do-file and its mirror.
- `warehouse/derived/battery_optimizer_check.py`: the independent check. Reads the CSV only; does not import the model.
- `warehouse/derived/battery_awards_compare.py`: the model beside the awards; `--snapshot` writes `site/data/battery_awards_beside.json`, which the page imports.
- `site/lib/batterystack.ts` (`awardsBeside`, `awardsStat`), `site/app/cost-of-power/battery/page.tsx` (the line, the link, the downloads), `site/lib/release.ts` (the note as `review`), `site/scripts/check-routes.mjs` (the note's address).
- `site/scripts/check-values.mjs`: keys `bsa|<strategy>_<N>h|<stat>`; and `CHECK_VALUES_PAGES=<prefix>` to run one tool's pages (the summary says "RESTRICTED RUN").
- `site/scripts/check-battery-face.mjs`: the page in the internal view at 1280 and 390 px.
- `tests/test_session178.py` (34 tests); `.gitattributes` (LF for the new files); `docs/methods/battery_stack.md` (a pointer, and the stale durations table marked superseded).

## The replication, in figures

- Why 36 months and not twelve: the "bad month" headline reads 36 months. One CSV rebuilds all three headline numbers.
- Reproduced from the CSV, equal to the page's library on the table: USD 81.40 per kW; USD 8,140,219; 33 percent; coverage 0.88; debt USD 6,783,357; bad month December 2024, USD 475,477 of 36; each stream of the last twelve months; 2024 and 2025 of the chart.
- Not in the CSV (they need years before October 2023): the last three full years, every year held, the column without February 2021, the stress days. `check-values` recomputes them.

## The optimizer check, in figures

- Method: the day written again from scratch in another form, solved by HiGHS interior point; then a ceiling by weak duality computed in plain arithmetic, which needs no trust in a solver. Both solves use HiGHS: scipy is the only solver in the venv.
- Stated sample, seed 178: 3 days a month of the last twelve, plus the highest-revenue day (26 January 2026), the most negative price (24 February 2026) and both clock-change days: 40 days. Largest gap USD 0.00000003; relative 2.9e-10; ceiling reached 40 of 40.
- Every day, 1,096: largest relative gap 3.2e-10; ceiling reached on 1,095.
- The other day, 4 January 2025, is the one day that needed the charge-or-discharge switch: the model's USD 129.841672 equals my own mixed-integer optimum and the best of all 4,096 switch patterns.

## The awards, in figures

- Window: January to July 2026, the months both tables hold whole. Unit: USD per kW of power and month.
- Fleet MW: the sum of each storage resource's highest HSL in the month, resources with no award included (17,180 MW in January, 21,365 in July).
- Ratios: foresight 2, 4, 8 hours 5.71, 5.66, 5.20; day-ahead 5.64, 5.48, 4.69.
- Megawatts in awards, mean hour: model 142 percent of rated power (regulation up 45, down 78); fleet 21.6 percent (regulation up 2.4, down 1.9).
- Caveats, in the note: price taker with perfect foresight; awards are day-ahead only, a floor; 216 to 252 of 306 to 332 resources held an award; durations of the fleet unknown; seven months.

## Numbers on the page, before and after

| Number | Before | After | Expected |
|---|---|---|---|
| Every existing number, seven battery addresses | as the live set | the same (1,796 values) | yes |
| The line: model, fleet, ratio (ERCOT, per strategy and duration) | absent | 2.25, 0.40, 5.66 at the default | yes, the one line allowed |
| Lead: link "Every number, step by step" | absent | present | yes |
| Source line: three downloads | absent | present | yes |

## Where the notes and the code differ

1. `battery_stack.md` said NYISO and SPP durations were all assumed. The code cites them since session 102; only NYISO regulation is assumed. Note amended.
2. Its day counts are session 67's (3,195 and 3,197); the table holds 3,198 and 3,199.
3. No note said the first hour of a day holds no upward reserve (at most 1.6 percent of the last twelve months, an understatement).
4. No note said a month enters the last twelve months on its 28th day of 31.
5. No note said the contract's end month changes no number.
6. `lib/batterystack.ts` still computes four statistics the page stopped showing in session 71.
7. The page's own words and the code agree.

## What is left, item by item

| Item | From | State |
|---|---|---|
| Durations table for NYISO and SPP out of date in the note | 86, 100 | Closed tonight: note amended (`f359587`) |
| Test expecting the battery page live | 92, 166 | Closed tonight: `tests/test_session92.py` (`f359587`) |
| California page showing the rebuilt numbers | 76 | Closed tonight: 3 CAISO addresses equal the live set (`check_values_battery_1.out`) |
| Regulation Down: model 5.36 against fleet 0.13, "a question about the model" | 116 | Closed tonight: answered in the note, section 9 (quantity, 78 percent against 1.9) |
| Browser test of the page | 67, 166 | Partly: `check-battery-face.mjs`. Open: rewrite `test-battery-stack.mjs` to unlock first. Recommend session 179 does it, it changes the page |
| Lead with the last twelve months; CAISO rules; unlock link; early-years wording; awards pull; offers; standing pull; loader timeout; SPP rules; daily refresh | 67 to 149 | Closed by sessions 71, 76, 79, 100, 102, 115, 116, 120, 166 (23 items) |
| ERCOT durations before December 2022 and December 2025 assumed one hour | 67, 101 | Open. Recommend one approved read of ERCOT's protocols of those years; until then the label stays |
| 8-hour cost an extrapolation; contract share earns nothing; average-year rule; 25 percent outlier; 36-month window; three-year rule | 67, 71 | Open. Each is now written in the note; signing the note closes them |
| A month enters the last twelve months before it ends | new | Open. Recommend whole months only for the headline; a small change, moves the headline's timing, not past values |
| First hour holds no upward reserve; energy at midnight lost | new | Open. Recommend leave: conservative, at most 1.6 percent |
| `ercot_as_quantities` not in the daily run; ERCOT API key | 74 | Open. Recommend adding the one line, so a fleet-limited year accrues |
| Fleet-limited as a strategy | 74 | Open. Recommend a third strategy when twelve months of quantities are held; tonight's 5.66 is the case for it |
| CAISO regulation energy management; resource adequacy omitted | 67, 74 | Open. Recommend no action |
| Called-reserves files and session 100's documents on one machine only | 79, 100 | Open. Recommend copying to the archive bucket |
| Deployed-regulation pull; Non-Spin offer floor | 79 | Open. Your approval |
| NYISO, SPP reserve prices, SPP quantities, the review table not in the daily run | 85, 86, 100 | Open. Recommend waiting until the grids are opened |
| `catalogue_hold` on `nyiso_as_prices`, `spp_as_prices` | 85 | Open. Your ruling |
| NYISO license; SPP "commercial publication"; ISO-NE and MISO internal | 85, 100, 149, 159 | Open. Your rulings |
| Open NYISO and SPP on the page | 86, 102 | Open. Your ruling |
| NYISO regulation duration assumed; its regulation targets not found | 86, 100 | Open |
| SPP ramp and uncertainty products, NYISO 30-minute reserve left out; SPP's 50 percent rule | 86, 100 | Open. Recommend no action (errs low) |
| A one-hour battery | 101 | Open. Changes what the tool is: your ruling |
| ERCOT's yearly file as a workbook: permanent? | 113 | Open. Watch |
| No duration class for ERCOT's resources (name match to EIA-860M) | 115 | Open. Recommend a session: it would set the awards beside each duration |
| Model beside awards for partial months | 115 | Open. Recommend whole months, as tonight's line |
| Awards page not linked from the battery page or the menu | 115 | Open. Recommend linking when both are approved (three tests pin the absence) |
| First disclosure day rests on three zips | 115 | Open. No action |
| A second zip a day after a missed run | 116 | Open. Your ruling |
| The allocation for "never offered" | 116 | Open. Your ruling |
| **1 November 2026, the repeated hour: the disclosure connectors will record the day failed and skip it** | 116, 120 | Open. Recommend a fix before that day's 60-day file arrives, about 31 December 2026 |
| Node prices from now on; real-time ancillary prices; 57 days of SCED | 120 | Open. Three pulls for your approval. Node prices cannot be had later |
| Awards page title and rewrite; what cannot be obtained; its decisions; the 96 files unchecked | 120 | Open |
| Redivis: the battery tables in the draft only | 67 | Open. Your click |
| The battery tab still reads "What power costs to buy" (`FROZEN_LABEL`) | 140 | Open. A person deletes its use; no freeze file exists |
| `release.ts` comment says three pages are open | 166 | Open. Trivial; with the next edit of that file |
| 19 tables refused as older than the live copy, `battery_stack_monthly` among them | 166 | Open. Look after the 10 October run |
| Result of the 10 October 14:00 UTC run | 172 | Open. Not yet run at hand-back |
| Four unused statistics in `lib/batterystack.ts` | new | Open. Remove with the next page change |
| The awards line's snapshot goes stale when the awards gain a whole month (August 2026, about 30 October) | new | Open. One command under "To finish" |
| `check-values` has no reader for `/datacenters`'s new keys | 166 | Open. Blocks the full value check |
| Finding do-files read `varnames(1)` over comment lines | 170 to 174 | Open. Your ruling |

## Pulls and spend

- Outside hosts: 0 requests. Ceiling: none approved, none used.
- Supabase: anon reads only, through the local build and `check-values`.
- Model spend: USD 0 of USD 0. No model call.

## Checks run

| Check | Exit | Output under `runs/session178/` |
|---|---|---|
| Site build, first | 0 | `build.out` |
| Site build of the final tree (after the last change to `docs/` and `site/`) | 0 | `build2.out`, `build2.exit` |
| `tests.test_session178`, worktree (tables absent) | 0, 31 run, 2 skipped | `test_session178_worktree.out` |
| `tests.test_session178`, main copy's tables read only | 0, 34 of 34 | `test_session178_tables.out` |
| Whole suite, before the session 92 fix | 1: 2,786 run, 1 failed (session 92's stale expectation) | `suite_worktree.out` |
| `tests.test_session92` after the fix | 0 | `test_session92.out` |
| Battery neighbours (67, 102, 103, 115, 116, 120 pages, 148, 178) | 0, 175 run | `tests_neighbours.out` |
| `check-values`, full | 1: `unknown check datacenters|counted` (on main before this session) | `check_values_1.out` |
| `check-values`, battery pages only | 0: 1,808 of 1,808 | `check_values_battery_1.out` |
| `check-routes`, local | 0: 0 failed | `check_routes_1.out` |
| `check-battery-face.mjs`, 1280 and 390 px | 0: 20 of 20; no sideways scroll at 390 | `check_battery_face.out`, `shots/` |
| `test-battery.mjs` | 0 | `test_battery.out` |
| `test-battery-stack.mjs` | 1: stops at the visitor's in-review page (since session 166) | `test_battery_stack.out` |
| Exporter | 0 | `export.out` |
| Optimizer check, sample and all | 0 and 0 | `optimizer_check_sample.out`, `optimizer_check_all.out`, and the two CSVs |
| Awards comparison, with quantities and snapshot | 0 | `awards_compare.out`, `awards_snapshot.out`, `battery_awards_compare.csv`, `battery_awards_quantities.csv` |
| Python mirror | 0 | `replication_mirror.out` |

- Not run again after the session 92 fix: the whole suite (the one failing test passes on its own; the fix is one assertion).

## Decisions made without you

- The CSV holds 36 months, not twelve, so that one file rebuilds every headline number. The twelve are marked. 4.3 MB, under the 5 MB line, in git.
- The awards line reads a committed snapshot, not the live set. Reason: four earlier tests hold the page to two reads and to naming nothing of the awards page. No old test of the page was changed. The line links the note, not the awards page.
- The line follows the reader's strategy and duration. Both strategies use day-ahead ancillary prices.
- The do-file destrings the 25 numeric columns; the four text columns (times, day, month) stay text, as in the finding do-files.
- The comment lines of the CSV hold no comma and no double quote, so Stata's import cannot miscount columns.
- The independent check uses HiGHS again (another form, another algorithm) because no other solver is in the venv; the weak-duality ceiling is the part that needs no solver. A discretized brute force was not used: with five products it gives only a lower bound.
- `CHECK_VALUES_PAGES` was added to `check-values.mjs` so the battery pages could be checked while the full run is broken. The full run is unchanged when the variable is unset.
- `tests/test_session92.py`: one stale assertion changed, with a comment.
- The note has its own line in `release.ts` (`review`), like `battery_stack`.
- Not done, to keep the tool what it is: no change to the model, to the 90 percent rule, or to any formula.

## For the coordinator

1. Nothing under the data lock. No migration. No table of the warehouse written. No load.
2. Merge `wip/178-battery-correct`. Files that other sessions may touch: `site/lib/release.ts` (one added line), `site/scripts/check-values.mjs`, `site/scripts/check-routes.mjs`, `.gitattributes`, `site/app/cost-of-power/battery/page.tsx` and `site/lib/batterystack.ts` (session 179 builds on both).
3. In the main copy after the merge, tables present: `python -m unittest tests.test_session178` (expect 34 run, 0 skipped).
4. If its class `TheCsvAndThePageAgree` fails (the daily run revised a month of the window): `python warehouse/derived/battery_dispatch_export.py`, then commit `site/public/battery/erw_2026_battery_dispatch.csv`. No lock: it reads `warehouse/output` and writes a site file.
5. Build, start, then: `node scripts/check-routes.mjs <base>`; `MSYS_NO_PATHCONV=1 CHECK_VALUES_PAGES=/cost-of-power/battery node scripts/check-values.mjs <base>`; `node scripts/check-battery-face.mjs <base> <dir>`.
6. The full `check-values` fails on `datacenters|counted` until that reader is written. It is not this branch's.
7. Snapshot before and after (rule 8). Expected for a visitor: no difference (the page is in review). Internal view: the one line, the lead's second link, the three downloads.

## To finish

- Run the do-file in Stata once (Samuel).
- When `ercot_storage_dam_awards_monthly` gains a whole month: `python warehouse/derived/battery_awards_compare.py --in-dir warehouse/output --out-dir runs/session178 --snapshot`, commit `site/data/battery_awards_beside.json`, and update the six figures in section 9 of the note (a test holds the note to the snapshot).
- Rewrite `site/scripts/test-battery-stack.mjs` for a page in review (session 179).
- A reader for `datacenters|counted`, `no_us_state`, `cancelled` in `check-values.mjs`.

## The landing

