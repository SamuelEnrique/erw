# Session 688 report: the package's whole remote test, the draft reconciled, and the next file written first

23 October 2026, from 00:04 UTC, on lab-desktop (the data machine), the first session of `queue/done/045-evening-22-october-data-resumed.md` (chain 044 resumed from session 688). Model spend USD 0.

## Read these first

- **The next file was written first, as chain 045's added rule says:** `queue/next/046-night-22-october-data-sources-gaps.md` (sessions 850 to 864, machine: data), committed alone and pushed to main at 00:07 UTC (`19025484`), before any other work. It holds ERCOT's settlement point mapping, its CDR reserve margins and its transmission projects (three siting gaps a public ERCOT report fills), EIA-861's delivery-only rows (Texas wires utilities), a derived table of signed interconnection agreements, EIA-930's sub-regions for 2019 and their first months, a second try at substations and lines, the unsettled licenses a read can settle, two more sources, notes, the Stanford draft, and its own landing.
- **Session 687's report exists** on `wip/687-699-data` (written before chain 044 stopped), so none was written from the commits.
- **The package's remote test: 3 of 11 proven, 1 fault of the test fixed, 7 not run for the ceiling.** `ercot_peak_premium_annual`, `eia860m_retired_generators` and `ercot_grid_notices` fetch from the Stanford draft exactly as the local files (every row and the header). `eia_fuel_spot_prices` failed: the draft holds 27,754 rows and this machine 27,766, because the daily run rewrote the table (every row's `retrieved_at`) after the upload. That is the test's assumption, not the backend: `same_as_local` now asks, for a table rewritten since the upload, that every draft row is held here with the same values apart from the run's own columns (`retrieved_at`, `vintage`) and the same title; a table as uploaded still needs every row and the header. Offline test: `tests/test_session688.py` (4 tests).
- **The draft reconciled** (session 687 left it here): 147 of 194 match; 45 differ only because the daily run has grown them here since their upload (the CSV larger in every case, never smaller); chain 041's two new public tables (`eia930_subba_demand_hourly_2021`, `eia_coal_production_annual`) are not in the draft. The release note says so, and its click's step 1 names the choice (release the draft as of 21 and 22 October, or upload the 47 first).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| redivis.com | 100 of 100 | the reconcile (5), the first remote run (66: the fixture and four fetches through the export read), the second run (29, capped: `eia_fuel_spot_prices` again with the fixed comparison, refused at request 30 mid-fetch) |

Each fetch through the export read costs about 11 to 15 requests (the table's export, its polls, and `erw_headers`'s), and the fixture's coverage read as many. The 100 allow the fixture and about five fetches.

## Not run, for the ceiling

- `test_fetch_matches_local[eia_fuel_spot_prices]` with the fixed comparison, `[eia_drilling_monthly]`, the five `test_cite_names_the_table`, and `test_filter_and_coverage_match_local`. The command: `ERW_REMOTE_TESTS=1 python -m pytest package/tests/test_backends_stanford.py -v -m remote -k "eia_fuel_spot_prices or eia_drilling_monthly or cite or coverage"` (about 100 requests). Session 699 adds it to chain 046's Redivis session.

## Decisions made without you

- The remote test's comparison tolerates a daily run's rewrite after the upload, rather than pinning the test to tables no run touches: the draft will always lag the machine by a day or more.
- The second remote run was hard-capped at the 29 requests left (`runs/c045/s688/counted_pytest.py`, `ERW_CAP`), so the ceiling held exactly; the fetch it cut off proved nothing and is listed above.
- The click's step 1 now admits a table grown since its upload; the session uploaded nothing to refresh the 45 (about 235 requests).

## For Samuel's ruling

- Whether to release the Stanford draft as it stands (the warehouse of 21 and 22 October) or to have the 45 grown and 2 new public tables uploaded first (the release note, "The click", step 1).

## Files

- New: `tests/test_session688.py`, this report; `queue/next/046-night-22-october-data-sources-gaps.md` (on main). Changed: `package/tests/test_backends_stanford.py`, `docs/reviews/redivis-v1-release-note-2026-10-23.md`. On the data machine only: `runs/c045/` (the counters, the outputs, the reconcile list, `commit_status.py`, the queue snapshots `c045-queue-before` and `-after`: 0 differences in 25 pages).
