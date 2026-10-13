# Session 245 report: a year of hourly carbon

13 October 2026, 07:02 to 07:15 UTC, unattended, on lab-desktop (the data machine), the third session of the chain of 12 to 13 October. Branch `task/245-hourly-carbon-year`. Model spend USD 0: no model call. No pull. One write under the data lock: the live set's copy of `carbon_intensity_hourly`.

## Read these first

- **The site's database now holds `carbon_intensity_hourly` for 430 days, hour by hour: 13 whole calendar months (September 2025 to September 2026) and the two months at the ends, for the seven ISOs and the US48, both variables.** It held 35 days.
- **155,911 rows, nothing left out to save space:** every hour, every balancing authority and both variables of the window that the warehouse holds. The smaller form was not needed.
- **The size:** the database went from 1,359.9 to 1,429.2 MB (69 MB more); the limit is 7,500. 143,521 rows were written; the 35 days already there were not rewritten.
- **Nothing a visitor sees changed.** Every page that reads the table asks for its last few days by date; none relied on the short window. Snapshot before and after the load: 0 differences on the 25 addresses.
- **Session 244 landed:** pushed 07:01:51 UTC (`60e5a548`), check run 38360149006 passed, merged into `main` as `e582594e` at 07:08:18. Before snapshot `s244-before` (07:01:44); after snapshot `s244-after` (07:10:38, 140 seconds after the merge); `compare`: 0 differences in all, as expected. The deployment's own time for sessions 243 and 244 is still to be read (GitHub's hourly allowance returns at 07:32 UTC) and is in session 246's report.

## What the site's database holds now

Read back with the site's own key (what a page can read), `runs/session245/verify.py`:

| Grid | First hour (UTC) | Last hour (UTC) | Hours in the span | Hours held, intensity of generation | Hours held, intensity of demand | Whole months |
|---|---|---|---|---|---|---|
| CAISO | 2025-08-09 08:00 | 2026-10-09 23:00 | 10,240 | 9,897 | 9,952 | 13 |
| ERCOT | the same | the same | 10,240 | 10,144 | 10,144 | 13 |
| ISO-NE | | | 10,240 | 10,239 | 10,239 | 13 |
| MISO | | | 10,240 | 10,168 | 10,168 | 13 |
| NYISO | | | 10,240 | 10,144 | 10,144 | 13 |
| PJM | | | 10,240 | 10,024 | 10,024 | 13 |
| SPP | | | 10,240 | 7,072 | 7,072 | 13 |
| US48 | | | 10,240 | 10,240 | 10,240 | 13 |

- **The hours not held are the warehouse's own, not the load's.** The table is never filled: an hour is written only when EIA's CO2 value and a denominator above zero are both there. SPP's file often leaves a CO2 column empty (3,168 hours of this window); California's are the hours the method holds out (`docs/methods/impossible_hours.md`).
- The table ends on 9 October: EIA's estimates are a few days behind the calendar.
- The whole history from July 2018 (1,123,797 rows) stays in the CSV, the archive and the Redivis draft.

## How

- `warehouse/supabase/live_set.yaml`: the table is out of the 35-day rule (`recent`) and has its own window (`full`, with `select: {days: 430}`), as the daily intensity has its 100 days. EIA's CO2 estimates (`eia930_all_emissions`) stay at 35 days.
- **Why 430 and not 396:** 13 months back from today would cut the first of the 13 months part-way, and EIA's lag takes a few more days. 430 days hold 13 whole calendar months on any day of the year (a test walks every day of three years, a leap year among them).
- The loader rolls the window by itself on every load: the daily run on GitHub keeps it at 430 days from now on.

## What to review

- `runs/session245/verify.out` on this machine: the table above.
- `/ask`: a question about a grid's hourly carbon in any month since September 2025 can now be answered from the site's database (before: the last 35 days).
- `runs/session245/timing.out`: the site's own reads after the load, with the site's key: 0.08 to 0.21 seconds each.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py` | 0 | six of six |
| `load.py --dry-run --only '^carbon_intensity_hourly$'` | 0 | 155,911 rows selected |
| `load.py --only '^carbon_intensity_hourly$'`, under `lock.py run` | 0 | match: CSV (filtered) 155,911, Supabase 155,911; written 143,521, deleted 0 |
| `runs/session245/verify.py` | 0 | 16 series, 13 whole months each |
| `python -m unittest tests.test_session245` | 0 | 6 tests |
| the 35 test modules that read `live_set.yaml`, and the new one | 1 | 763 tests, 1 failure: `test_session51`, the same as before this chain (a table on this machine against a committed file) |
| snapshot `s244-before` against `s245-after-load` | 0 | 0 differences; main had not moved between them, so the comparison is of the load alone |
| `python scripts/freeze.py status` | 0 | no freeze |

## Decisions made without you

1. **430 days, not exactly 13 months,** for the reason above. About 14 months of rows.
2. **The whole rows, not a smaller form.** The budget allowed it by a wide margin (1,429 of 7,500 MB), so nothing was cut: both variables, all eight balancing authorities, every column.
3. **PJM's rows are loaded with the others,** as they were in the 35-day window. They are EIA's estimates for PJM's balancing authority, from EIA; nothing was asked of PJM.
4. **The load ran before the landing,** from this machine's table (the same run as GitHub's of 12 October, 14:32 UTC). GitHub's daily load reads the same rule once this lands; until then a load there would cut the window back to 35 days. The daily run starts at 14:00 UTC; this lands hours before.
5. **I did not run the whole suite again for this session:** the change is one rule, one sentence in a method and one in a docstring. The 35 modules that read the rules were run; GitHub's check runs everything.
6. **One line of the site's chat text was left as it is:** `site/lib/chat/tools.ts` tells the model that "hourly emissions hold only their last 35 days". That is still true of EIA's CO2 estimates and says nothing of the intensity. It is under `site/`, which this chain does not edit; see the ruling below.

## For Samuel's ruling

1. **Tell `/ask` on the site that it has 14 months of hourly carbon?** One sentence in `site/lib/chat/tools.ts` (line 85), for the code machine: "the hourly carbon intensity (carbon_intensity_hourly) holds its last 430 days".
2. **Should `/emissions` or the grid pages show the year?** They read 3 to 4 days today. The data is there for a year-over-year chart of any hour.
3. **`CLAUDE.md` still says three pages are live** (`/cost-of-power/battery`, `/network`, `/storage`). `site/lib/release.ts` has every page in review since session 166 (8 October), so all 25 addresses of the snapshot show the in-review page and every comparison of this chain is of that page. Correct the line in `CLAUDE.md`?
4. **A first exact count of freshly loaded rows can pass the three seconds the site's key is allowed** (it answered at the second or third try). No page counts rows this way; noted in case Ask ever does.

## Files

- New: `tests/test_session245.py`.
- Changed: `warehouse/supabase/live_set.yaml` (the table's own window), `docs/methods/emissions.md` (what the site's database holds), `warehouse/chat/tools.py` (one sentence of the module's note).
- On this machine, not in git: `runs/session245/` (the load's output, the read-back, the timings, the snapshots' comparisons).

## The landing

- Freeze: `python scripts/freeze.py status` exit 0, no freeze. Main pulled and merged before the push. Before snapshot `s244-after` (07:10:38 UTC, 25 pages, 0 failed; taken after the load and after session 244's merge), then the push of `task/245-hourly-carbon-year`. The check run, the merge, the after snapshot and the comparison are in session 246's report. Expected: 0 differences on the 25 pages.
