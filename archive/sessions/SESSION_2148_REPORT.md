# Session 2148 report: the Northwest's federal grid (BPA's balancing authority), and chain 094's file

23 October 2026, from 23:22 UTC, on lab-desktop (the data machine), the first session of `queue/done/092-day-30-october-data-bpa-snowpack-access-outlook-permits.md`, run by chain 057's agent after chain 069 (the owner's instruction for that run: run the file the queue step prints). Model spend USD 0. Pulls: 14 requests of 15. On transmission.bpa.gov: its robots address (sent on to www.bpa.gov's transmission page; the host has no robots file), the old 2024 address (404), the VER page, the balancing authority page and seven yearly files. On www.bpa.gov: its robots file in a call of its own, the sitemap and the operations page. Also 3 to Supabase for the lock.

## Read these first

- **The next file first:** `queue/next/094-day-31-october-data-britain-imports-gas-use-waterways.md` (sessions 2162 to 2175, machine: data), committed alone in the detached worktree `erw-c069q` and pushed with `HEAD:main` (`6db684bc`, 23:23 UTC); `git status -sb` showed nothing ahead. 094 was the next free number, and 2162 to 2175 were free. Its sources: Great Britain's grid (NESO's open data), EIA's company-level crude imports, EIA's Natural Gas Annual by end use and state, the Corps of Engineers' waterborne commerce, three of the sessions' own choosing. Snapshots `q094-before` and `q094-after`: **0 differences**. The queue move of 092 itself (`388d41d1`) was pushed between `q092-before` and `q092-after`: 0 differences. Vercel is still rate limited, so neither deployed.
- **This chain was taken from chain 090's agent's queue:** 092 was written by chain 090's session 2134 as its continuation, and the queue step handed it to this machine at chain 069's end. That agent was told, and agreed: its session 2147 will not touch 092, Decisions 67 is chain 090's, and this chain numbers from 68.
- **One series table, `bpa_ba_hourly`:** 400,261 rows, 1 January 2020 to 23 October 2026. It holds the BPA balancing authority's load, wind, solar (2022 on), hydro, thermal (BPA's fossil and biomass), nuclear and net interchange, the hour's mean of BPA's five-minute values (MW, the hour's MWh), from its yearly workbooks. From 2022 BPA's files carry a UTC column. The 2020 and 2021 files keep Pacific local time; the connector puts them into UTC by their order across the clock changes, so November's repeated hour is the second time through. 84 hourly rows hold fewer than 12 five-minute values. The forecasts (base schedules and basepoints) are not taken.
- **The cross-checks** (`runs/c092/s2148/cross.py`):
  - BPA's load summed to the day against EIA-930's BPAT daily demand (`eia930_daily_demand`), 2,477 full days: median ratio 0.987, 5th and 95th percentiles 0.97 and 1.02, under Pacific days and UTC days alike. BPA's own load runs about 1.3 percent below EIA's BPAT demand.
  - BPA's balance closes: in 2024, generation (hydro 56.19 TWh, nuclear 9.94, thermal 6.67, wind 6.84, solar 0.33) less load (58.22) is 21.75 TWh, and the net interchange is 21.76. BPA's area is a net exporter, as its page says.
- **Registered:** the sector rule (`power`), the live set's hold and the release's storage hold, the release package's rows (1 table, 7 variables), the license tables (BPA, read 54, may be public; licenses check 0 problems, release check 0 differences); no row twice. The test: `tests/test_session2148.py` (5 tests).

## Errors

- **BPA's old address for the yearly files is gone** (one 404); the VER page gives the new ones (`OPITabularReports/`).
- **The page's links are unquoted,** which the first look missed; read again with an unquoted pattern.

## Decisions made without you

- **Chain 092 taken** although chain 090's agent wrote it, under the owner's instruction for this run, with that agent's agreement.
- **Hourly means, not five-minute values,** as the file allowed (the five-minute rows would be about 4.8 million).
- **The branch cut from chain 069's** (`wip/2106-2119-data`, its landing in progress), so this chain's records follow chain 069's.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/bpa_ba.py`, `tests/test_session2148.py`, this report; on main, `queue/next/094-day-31-october-data-britain-imports-gas-use-waterways.md`.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c092/`.
