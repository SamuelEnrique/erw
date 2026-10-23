# Session 864 report: the package's remote test, the rest

23 October 2026, from 02:31 UTC, on lab-desktop (the data machine), a session of `queue/done/046-night-22-october-data-sources-gaps.md`. Model spend USD 0.

## Read these first

- **The eight remote tests session 688's ceiling left were run against the Stanford draft: 4 passed, 4 failed, all four for one cause: the draft is an earlier run's copy, not a fault of the `erw` package.** Passed: `eia_drilling_monthly` fetched exactly as uploaded; the citations of `ercot_peak_premium_annual`, `ercot_grid_notices` and `eia_drilling_monthly`. Failed:
  - `eia_fuel_spot_prices`' fetch: every draft row is held here, but one value of 27,754 differs: EIA revised a recent price (98.73 in the draft, 94.99 here) between the upload's run and today's;
  - the citations of `eia860m_retired_generators` and `eia_fuel_spot_prices`: the same words with "Retrieved 2026-10-21" against "2026-10-22";
  - coverage of the five tables: `eia860m_retired_generators`' window (`ts_min`) moved with today's run.
- **The comparisons fixed, with their test** (`tests/test_session864.py`, 4 tests, offline): a table a daily run rewrote may differ from the draft by a publisher's revisions in under 0.1 percent of the rows in common (counted in the test's line); a citation is compared without its "Retrieved" date; coverage is compared on the columns a run does not move (not `ts_min`, `ts_max`, `n_rows`, `last_run`, `n_nodes`, `validator_status`).
- **Not run again:** the 13 requests left do not cover the fixture and one fetch (about 27). The four tests with the fixed comparisons go to chain 047's Redivis session (878); session 866 adds them to its file.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| redivis.com | 87 of 100 | the fixture, two fetches through the export read, five citations, coverage (capped at 100, `runs/c046/s864/counted_pytest.py`) |

## Decisions made without you

- A publisher's revision tolerated up to 0.1 percent of the rows in common, counted; more fails the test.

## For Samuel's ruling

- None new.

## Files

- New: `tests/test_session864.py`, this report. Changed: `package/tests/test_backends_stanford.py`. On the data machine only: `runs/c046/s864/`.
