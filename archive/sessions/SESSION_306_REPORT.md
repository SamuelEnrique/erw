# Session 306 report: the battery's inputs

19 October 2026, 09:06 to about 09:20 UTC, unattended, on lab-desktop (the data machine), the second session of the chain of 19 October. Model spend USD 0. The workbook and the terms page were read earlier this morning (06:12 UTC), while session 305's run held the data lock; the tables were built once the lock was free.

## Read these first

- **Two tables, validated, in coverage, in the Redivis draft and in the live set:** `battery_sourced_ranges` (90 rows: NLR's ATB 2025, three cases each for 10 assumptions) and `grid_stress_days` (226 rows: six grids, session 297's rule). Loader: `match battery_sourced_ranges ... 90`, `match grid_stress_days ... 226`, `match sources: CSV 317, Supabase 317`. The page file is `site/data/sourced_ranges.json`.
- **The names differ from the prompt's** (decision 1): a series table's name has three parts, and `sourced_ranges` and `stress_days` were refused by the validator. The JSON keeps the prompt's name.
- **Lazard's LCOE+ (June 2025) is not held in `warehouse/raw`, so none of its cases is written and no request was made.** Without it the table has no debt share, no hurdle beyond the ATB's return on equity, and no cycles, degradation, fade or augmentation case. The ATB states none of these for a utility-scale battery.
- **The cross-check holds for Uri, but only half holds for Elliott:** 15 to 19 February 2021 are stress days (11 to 19 February all are), and 23 December 2022 is one. **24 December 2022 is not:** its mean of USD 63.2 is under the threshold of 225.6, which the summer of 2022 raised. The ERW holds no ERCOT notices, so the notice test cannot add the day. No row was added by hand.
- **PJM has no row:** the ERW holds neither a PJM hub price nor a PJM notice.

## What to review

1. `warehouse/derived/stress_days.py` against `docs/methods/battery_stress_days.md` (session 297): the price test, "a day with any hour missing is not tested", the notice kinds, and the events (days at most three apart; `uri_2021`, `elliott_2022` and `ercot_heat_2023` keep their names).
2. `docs/methods/stress_days.md`: the counts by grid, and the cross-check.
3. `warehouse/connectors/sourced_ranges.py`: every row names its sheet, row and column (`x_page`). **The workbook's values are in 2023 dollars**, while `site/lib/battery/finance.ts` says the ATB figures are "2024 dollars". The code machine should check this when it reads the JSON.
4. Decision 47 in `docs/datastandard.md`: three units join the vocabulary (`USD/kW`, `USD/kWh`, `USD/kW-year`).

## Pulls against their ceilings

- NLR ATB 2025: **3 requests of 3**: the data page (atb.nlr.gov/electricity/2025/data), the disclaimer agreement (kept, SHA-256 420e6270...) and the workbook (data.openei.org, 8,509,204 bytes, SHA-256 fa0a2b95..., 06:12:19 UTC). The two hosts' robots files were read first, and neither forbids the requests. The terms allow use and copy without fee, with the notice kept and DOE/NLR credited.
- Lazard: none (no copy held; the prompt allows only a held copy).
- No other publisher.

## The tables

| Table | Rows | What | Live set |
|---|---|---|---|
| `battery_sourced_ranges` | 90 | ATB 2025, sheet "Utility-Scale Battery - R&D", year 2025: capital cost, overnight capital cost, fixed O&M, grid connection cost and round-trip efficiency at 2, 4, 6, 8 and 10 hours; energy and power capital cost; nominal interest rate (0.065) and return on equity (0.085); technical life (15 years). Advanced = low, Moderate = mid, Conservative = high. The 4-hour Moderate capital cost is USD 1,396.73 per kW (row 74) | whole, under `review_hold` (no page reads it yet) |
| `grid_stress_days` | 226 | ERCOT 113 (64 events), CAISO 58 (24 by price, 36 by notice; 25 events), NYISO 10, MISO 16, SPP 17, ISO-NE 12. MISO's prices are the ones already held; nothing was asked of MISO | whole, under `review_hold` |

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 306"` | 0 | six of six |
| `erw_validate.py` on the first build (`sourced_ranges`, `stress_days`) | 1 | name pattern; units `USD/kWh`, `USD/kW`, `fraction`, `USD/kW-yr`, `years`; vintage and retrieved_at format warnings |
| `erw_validate.py` on `battery_sourced_ranges` and `grid_stress_days` | 0 | PASS, 0 errors, 0 warnings |
| `table_stores.py` (first) | 1 | coverage: "no sector rule ... matches; add one" |
| `table_stores.py` after the sector rules | 0 | validate, coverage, archive, Redivis draft for both; `erw_headers` skipped for the export cap (session 305) |
| `load.py --no-vacuum --only '^(battery_sourced_ranges\|grid_stress_days)$'` under the lock | 0 | match 90, 226; sources 317 |
| `tests.test_session306` | 0 | 6 tests |
| the 42 test files that read the validator's units, the sector rules, the live set or the standard | 1 | 870 tests, 1 failure: `test_session51` (pre-existing, session 305's report) |

## The landing

- freeze 0; before `s306-before` 09:16:47 UTC; merged origin/main (nothing new); pushed 09:16:58 (`5d389ad6`, with session 305's report); deployment 7170048532 success 09:18:20; after `s306-after` 09:18:39; compare: **0 differences on 25 pages** (expected: no page reads either table).
- No live page reads either table, so the load needed no snapshot of its own.

## Decisions made without you

1. **`battery_sourced_ranges` and `grid_stress_days`, not the prompt's names** (Decision 19's precedent: a series name has three parts). The JSON keeps `site/data/sourced_ranges.json`, which `site/lib/battery/finance.ts` names. Reversible: a rename.
2. **Units as the ATB prints them**, three of them new to the vocabulary (Decision 47), rather than converted. A share is `ratio` and a lifetime `year`.
3. **Session 297's rule, as written:** every hour must be held for a day to be tested (the first build took 95 percent of intervals; the counts were the same), and events with the named events' ids. No ERCOT notice is held, so ERCOT is judged by price alone.
4. **The license is recorded in `sources.csv` (`nlr:atb-2025-v1`, public) and in each table's header,** and is not yet in `docs/licenses.md`, which `scripts/licenses.py` writes; session 311's sweep adds both tables.
5. **Both tables are loaded whole and held for review** (`review_hold`; the ATB under `sources_hold`) until a page reads them.

## For Samuel's ruling

- 24 December 2022 is not an ERCOT stress day under the rule: accept it, or add a table of ERCOT's notices (EEA, Watches, Advisories) so the notice test can count it.
- Lazard's LCOE+ June 2025 is not held: place a copy in `warehouse/raw`, or keep the ATB alone in the table.

## Files

- New: `warehouse/connectors/sourced_ranges.py`, `warehouse/derived/stress_days.py`, `docs/methods/stress_days.md`, `tests/test_session306.py`, `site/data/sourced_ranges.json`, this report.
- Changed: `warehouse/validate/erw_validate.py` (three units), `docs/datastandard.md` (Decision 47), `warehouse/metadata/build_coverage.py` (a sector rule and a tier rule), `warehouse/supabase/live_set.yaml`, `warehouse/metadata/sources.csv`, `coverage.csv`, `docs/coverage.md`, `archive_manifest.csv`, `redivis_uploads.csv`.
