# Session 103 report: known data faults

**Built and on the live site, the new page in review.** A table of every fault found in source data (`known_data_faults`, 24 faults) and the review page `/data/faults`; one stated screening rule for impossible hours, applied where a review page's table reads them, with before and after; the January fault fixed in the general chat; the `comment="#"` question settled with a test. One deploy, with the 25-page snapshot before and after: **0 differences**. One load: **0 differences**, and one number that will move when the home page's cache turns (below).

## Read these first

1. **A number on the home page will move by 127, and this session moved it.** The home page counts the rows of every public table. `shoulder_hours_monthly` went from 27,328 rows to 27,201 (the screening rule, and a fault of the table's own, both below), so the total goes from 13,849,497 to 13,849,370. The database already says so with a visitor's key; the page had not yet turned its hour-long cache when the after-load snapshot was taken, so the snapshot shows 0 differences. The count of public tables stays 97. The total moves every day with the daily run; this move is this session's.
2. **New York's zero hours are not in 2019 and 2020.** You named "New York's zeros in 2019 and 2020". The reports recorded "12 hours of zero" with no dates. The rule gives the dates: one hour in 2019, three in 2024, two in 2025, six in February 2026. None in 2020. The register and the page say what the file holds.
3. **PJM has seven impossible hours, not two.** The two the reports name (155,276 MW on 12 December 2019; 224,345 MW on 13 July 2020) and five more: one in April 2020, two in July 2020, one in August 2020, one in November 2024.
4. **The rule is not applied in three tables a live page reads**, and I say so on the page and in the method note rather than apply it: `cost_of_power_monthly` and `cost_of_power_carbon` (the home page reads them), `ba_supply_monthly` (`/network` reads it) and `ai_power_regions`. Applying it is one line in each builder. It would change a table behind a live page, and your rule for the chain is that no live number moves unless a session names it. Yours to say.
5. **The rule took a whole month out of the shoulder table.** California's February 2019 is no longer written: with its impossible hours blank, fewer than 90 percent of its days are complete, which is that table's own rule for a month. That is the rule working, and it is visible on `/shoulder`.
6. **`/shoulder` on production still shows the table as it was before the load** (99 of 3,482 of its own checks differ, all California). The page keeps its reads for an hour. I will run the check again in session 104 and put the result in that report.

## The table and the page

`known_data_faults`, events shape, one row per fault, written by `warehouse/derived/data_faults.py` from a register a person or a session writes, `warehouse/faults/faults.yaml`. The builder computes nothing and requests nothing; it fails when an entry lacks a field, names a table that is not in the warehouse or a source that is not in the registry, or gives a date that is not one. Method: `docs/methods/known_data_faults.md`. Validator exit 0; in coverage (130 tables), the archive and the Redivis draft; public, loaded into Supabase under `review_hold`, its source held off `/terms`. Nothing released.

**Every figure in it is one a session measured and wrote down, or one the rule measured today.** Each row says where it is recorded. A date that is not recorded is left empty and said to be so.

| Fault | Dates | Status |
|---|---|---|
| EIA's California generation changed in one hour | from 2025-12-16, continuing | worked around (CAISO's own supply by fuel is read from that hour) |
| EIA's California hours sit one hour late | 2023-11-01 to 2025-12-02 | corrected in seven tables; held as stamped in six |
| EIA's file holds no hydro for California | October 2019 to mid August 2020 | screened in the energy mix; held as published in the carbon intensity tables |
| PJM's demand: seven impossible hours | 2019-12-12 to 2024-11-21 | screened |
| New York's demand: twelve hours of zero | 2019-04-18 to 2026-02-10 | screened |
| California's demand: runs of hours near half its level | 2019-02-13 to 2026-01-25 (38 hours) | screened |
| SPP's demand: two impossible hours | 2024-07-19, 2025-06-21 | screened |
| The Lower 48's demand is a sum with the faulty hours inside it | | held as published; no peak is given |
| Daily interchange: days no tie can carry (SPP to MISO, 2,159,056 MWh on 2026-07-21) | across the history | screened (10 median absolute deviations and 500 MWh) |
| Daily interchange missing for weeks of the year, most in SPP | | held as published |
| EIA's "other" for ERCOT repeats the batteries | 2025-12-06 to 2025-12-14 | screened |
| PJM's sources and total part by 5 to 15 percent in 2,689 hours | 2020 to 2024 | held as published (a looser test) |
| 24 hours of demand blank in the Uri window | February 2021 | held as published |
| Four of California's ties reported differently by the two sides | | held as published |
| EIA's California solar about 13 percent below CAISO's own | | held as published |
| ERCOT's solar output above installed capacity on two days | 2023-08-10, 2026-08-29 | held as published |
| CAISO's renewable report: 24 hours on the day the clocks went forward | 2026-03-08 | corrected |
| CAISO's curtailment file: no reason for 9,241 rows | 2022 | held as published |
| CAISO's two curtailment workbooks repeat January to May | 2025 | corrected (25,848 rows read once) |
| CAISO's supply by fuel empty or short on four days | 2025-11-02 to 2026-09-22 | held as published |
| CAISO's OASIS leaves out the last hour of the autumn clock-change day | 2024-11-03, 2025-11-02 | held as published |
| ISO-NE's and NYISO's real-time price files miss intervals | | held as published |
| Berkeley Lab's queue file: missing years, statuses and operation dates | the 2026 edition | screened |
| A contract rate in FERC's reports that cannot be a monthly price | 2026 Q2 | held as published |

8 screened, 3 corrected, 1 worked around, 12 held as published, touching 28 tables. 17 have something still open; each says what.

**The page**, `/data/faults`, in review: one sentence of counts, what each status means, the screening rule in words, a table of the faults, then each fault with its evidence, dates, the tables it touches, what the ERW does, what is still open and where it is recorded. It reads the site's copy of the table. On production in the internal view it renders with data (746 figures) and is closed to a visitor.

## The screening rule for impossible hours

`warehouse/derived/impossible_hours.py`, `docs/methods/impossible_hours.md`. It is session 97's rule, stated once:

> An hour of demand is used when it is held, above zero, and within 25 percent of the median of the four hours around it (the two before and the two after). An hour that fails is used for nothing. Nothing is filled.

For demand only. What it does not catch is in the note: a faulty hour inside a sum (the Lower 48), a run of faulty hours at a believable level, and good hours between two faulty ones, which are lost with them.

**What it leaves out, measured today** on each area's newest EIA-930 workbook: PJM 7 hours, California 38, New York 12, SPP 2, the Lower 48 1, Texas, MISO and New England none (each also has 24 to 96 blank hours).

**Before and after**, each table rebuilt in a trial folder and compared value by value with the table as it stood:

| Table | Before | After | What changed |
|---|---|---|---|
| `eia930_demand_growth` | 24,108 rows | 24,108 | Nothing: 0 values differ. It has used the rule since session 97; its code now calls the shared one |
| `generation_mix_hourly_profile` | 162,911 | 162,911 | 39 values, each an average demand of one local hour in one month: PJM 7 (largest, April 2020 hour 23: 75,077.4 to 70,229.0 MW), California 24, New York 6 (February 2026, up 650 to 760 MW each), SPP 2. No generation figure and no share changed |
| `generation_mix_records` | 306 | 306 | Nothing |
| `shoulder_hours_monthly` | 27,328 | 27,201 | 445 values of California's EIA-based rows changed (April, May and December 2019, July 2025, and the year figures of 2019 and 2025); February 2019 no longer written (123 rows). Texas: nothing. Not from the rule: 13 new rows and 13 changed values from a day's newer input, and 17 stale rows gone (next paragraph) |

**A fault of the shoulder table's own, found by this rebuild and fixed.** The table was merged into its earlier file, so a row a run no longer made stayed: a day that left a year's ten worst kept its rank. After one newer day of input California's 2026 held eleven ranked days, and session 80's own test failed on it. A grid rebuilt by a run is now written whole; a grid whose workbook is not on the machine keeps its rows as before.

## The January fault in the general chat

Session 92 fixed it for Ask ERCOT and left the general chat as it was. Now both `warehouse/chat/tools.py` and `site/lib/chat/tools.ts` group a row of a day or longer by its own label, whatever time zone is asked: read in Chicago time, a monthly row dated 1 January no longer falls in the year before. Tested on `carbon_intensity_monthly`: by year, Chicago and UTC give the same counts, and they add to the table's. Session 92's test, which held that the trap was still there, now holds that it is gone. No model call was made to try it.

## The `comment="#"` question, settled

- **What pandas does.** Given `comment="#"`, it cuts a row at a bare `#` and pads the lost columns with blanks without a word. A `#` inside a quoted field is spared (I had the opposite in a first draft of the note; the test corrected me).
- **Which tables hold one.** 26 of the tables on this machine hold a `#` in a data row: queue ids and project names, plant names ("Muscatine Plant #1"), auction names ("Auction #1"), buyer names, addresses with a fragment. The list is `runs/session103/tables_with_hash.json`.
- **Was any table being cut?** Not today: none of the tables the builders read with `comment="#"` is among the 26.
- **What changed.** 19 reads in 11 derived builders now skip the header's lines by count (`ip.header_rows`). A test fails if any builder, connector, loader, reader or script reads a table with `comment="#"` again; a second test demonstrates the cut; a third checks that the four one-off analyses that still use it (left as they were run) read only tables without a `#`.

## The deploy and the load

| Step | Result |
|---|---|
| `task/103-faults`, run 37229900793 | passed, merged (`df4bc73`), deployed; Vercel accepted it |
| Snapshot `before-103` against `after-103` | **0 differences** on the 25 live pages |
| Load of four tables under the lock | `known_data_faults` 24, `generation_mix_records` 306 and `shoulder_hours_monthly` 27,201 (140 deleted) matched. `generation_mix_hourly_profile` **failed once** (the database's API answered 500 while the load was checking it) and matched on a second run, 162,911 rows, nothing left to write |
| Database | 753.0 MB before, 807.0 MB after |
| Snapshot `after-103` against `after-103-load` | **0 differences**; the home page's row total is due to move by 127 (first point above) |
| `/data/faults`, `/mix/v2`, `/shoulder` on production, internal view | render with data, closed to a visitor. `/mix/v2`'s own check 56 of 56. `/shoulder`'s own check 3,383 of 3,482: the page's hour-long cache (sixth point above) |

Between the end of session 102 and this session's first snapshot, an hour apart: 37 differences, all the 15-minute prices on the home page and the hourly stamps on `/network`.

## Tests and checks

- `tests/test_session103.py`, 16 tests: the rule on made hours; it is the rule the demand table had, value for value; the three builders call it and the three live tables do not; the register is sound and the check catches a bad entry; the table is the register row for row; the site's copy agrees with the table; the page; the reader question (three tests); the year grouping (two).
- Every session's tests on this machine: 730 ran, **one fails and is not this session's**, as in session 102: `test_interchange_ceiling` (the daily run's `eia930_all_interchange` holds 159,144 rows against a ceiling of 150,000).
- Two older tests changed with their reason: session 92's (above), and session 78's list of files that may name the join's date now includes the register.
- The site: `tsc` exit 0, the build exit 0, the route check on this machine's build 0 failed.

## Errors and decisions

1. **The register is YAML that a person edits.** My first version did not parse (a colon inside a one-line value); every text value is now a folded block.
2. **The trial comparison hid the month the rule removed.** The shoulder builder's trial copies the earlier table in and merges, so "gone: 0" was true of the trial and not of the rule. The whole rewrite showed February 2019. The before and after above is from the table as written, checked row by row against the earlier file.
3. **No pull, no request to any publisher, no model call, no force push. MISO stays paused.** The data lock was taken for each write step and is free.
4. **Session 102's commit that had not reached main** (the hub price history's rule taken out of the live set, the load's record) went to main with this session's push.

## For Samuel

1. **Rule on the three live tables** (fourth point at the top): apply the screen in `cost_of_power`, `ba_supply` and `ai_power_regions`, or leave them. If you apply it, the affected hours are listed in the note: for the cost of power, SPP's hour of June 2025, two of California's, and New York's zeros from October 2024.
2. **The faults still held as published in the carbon intensity tables**: California without hydro for ten months of 2019 and 2020, and California's hours one hour late, are in `carbon_intensity_*` as EIA gave them. The register says so; nothing was changed.
3. **The register wants an owner.** A fault is worth an entry the day it is found. I would add "the register" to what a session's report must mention when it finds one.

Energy Research Warehouse (ERW), session 103, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 19:00 to 20:10 UTC, unattended. **Model spend: USD 0.00.**
