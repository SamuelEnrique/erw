# Session 358 report: the node

20 October 2026, from 09:26 UTC, unattended, on lab-desktop (the data machine), the second session of the chain of 20 October, night. Model spend USD 0. Pulls: ERCOT 113 of the ceiling of 400 requests (below); no other publisher.

## Read these first

- **Twelve months of ERCOT's real-time node prices cannot be had from ERCOT's public lists, and none were taken from anywhere else.** The prompt's path, the existing `ercot_rtm_node_prices` connector, reads ERCOT's list of real-time Settlement Point Prices, which keeps seven days; this machine has saved it daily since 28 September 2026. Real time at the nodes is therefore held for **28 September to 18 October 2026 (20 whole days)** only. ERCOT's history of the hourly reports sits behind its signed-in Data Access Portal (`api.ercot.com`), which the ERW holds no account for and never asks (as `ercot_wind_solar_history.py` already records).
- **Day-ahead at every resource node is held for the twelve months**, from ERCOT's 60-Day DAM Disclosure (the files `60d_DAM_Gen_Resource_Data` and `60d_DAM_ESR_Data` carry each resource's Settlement Point Name and its Energy Settlement Point Price), plus ERCOT's 31-day list of DAM Settlement Point Prices: 1 October 2025 to 20 October 2026, **except 21 August to 19 September 2026** (the disclosure, 60 days behind, reaches 20 August; the 31-day list starts 20 September; those days come in the disclosure between 21 October and 19 November) and the autumn clock-change day (2 November 2025).
- **`node_basis_daily` (949,995 rows, 888 points), `node_basis_summary` (1,260 rows) and the internal `ercot_node_prices_hourly` (498,360 rows, under the ceiling of 500,000)** are built, validated (0 errors, 0 warnings) and in coverage. The two public tables are in the live set (`review_hold`); the hourly table is internal and not loaded.
- **Redivis refused `node_basis_daily`: "This import would cause your account to exceed its free storage allotment of 10GB."** It is not in the draft. The summary, the hourly table (internal dataset) and session 359's table went in. Nothing was deleted from Redivis to make room. This is the cap session 363 is told to record and stop at: see "For Samuel's ruling".
- **The basis is taken against `HB_HUBAVG` for every point**, the hub every economics page prices ERCOT at. The ERW holds no list of each node's load zone and zonal hub (ERCOT's NP4-160-SG, a source not registered) or of node coordinates, so neither is written; the shape note says so.

## The year's figures (day-ahead, 1 October 2025 to 30 September 2026, 335 days)

Per point the mean over its days (points held at least 90 percent of the days), against `HB_HUBAVG`, USD per MWh:

| Points | Basis, 10th / median / 90th | Four-hour spread, median | Wider than the hub (47.26) |
|---|---|---|---|
| every resource node (786) | -5.63 / 0.18 / 5.38 | 50.97 | 65.4 percent |
| storage (195) | -4.07 / 1.31 / 5.78 | 49.31 | 57.4 percent |
| solar (125) | -5.22 / 0.09 / 5.40 | 52.74 | 80.0 percent |
| wind (165) | -7.88 / -3.79 / 4.06 | 53.18 | 74.5 percent |
| gas (195) | -2.70 / 1.36 / 4.77 | 47.62 | 52.3 percent |
| load zones (8) | `LZ_SOUTH` 0.07 to `LZ_CPS` 4.78; `LZ_NORTH` 0.98 | 51.09 | 6 of 8 |

Real time, 28 September to 18 October 2026: the hub's spread 50.75; storage median 62.08 (76.3 percent wider), median basis 3.14. Over the battery pack's week (28 September to 4 October) the storage points' median real-time spread is 44.11 against the pack's 44.29 (16 dearest and cheapest 15-minute intervals there, four hours of hourly means here): the two readings agree.

**The packs:** the battery's item 4, the generator's item 5 and the datacenter's item 6 (section 6) now carry these figures; each says the figure is applied to no number of its page.

## What to review

1. `docs/methods/node_basis.md`: the shape (landed first, 09:02 UTC), where the prices come from and what cannot be had, the computation, the first build.
2. `warehouse/derived/node_basis.py`; the day-ahead stage `--pull-dam` of `warehouse/connectors/ercot_rt_spp.py`.
3. `tests/test_session358.py` (9 tests: the day's statistics, the disclosure read, the summary, the hourly ceiling, the stage).

## Pulls against their ceilings

| Pull | Ceiling | Used |
|---|---|---|
| ERCOT, all requests of the session | 400 | 113: one probe of the DAM Settlement Point Prices list (in session 357), the 60-Day DAM Disclosure list and 79 zips (operating days 1 October to 3 December 2025 and 6 to 20 August 2026; 708,773,284 bytes; `ercot_dam_esr.py --pull --days`, the connector's probe mode, which saves the zips and writes no table; the connector's own 3 GB ceiling now stands at 2,658,430,030 bytes), the DAM list and 31 day files (`ercot_rt_spp.py --pull-dam`), at the connectors' pace (2 and 1.5 seconds) |
| Rows of the internal hourly table | 500,000 | 498,360 |

The first 60-day pull stopped at ERCOT's list on a name resolution failure (`www.ercot.com` did not resolve in that background run; 0 zips asked); the rerun a minute later took all 79.

## Checks

| What | Exit | Notes |
|---|---|---|
| `node_basis.py --from 2025-10-01 --to 2026-10-19` (data lock) | 0 | 949,995 / 1,260 / 498,360 rows; 0 days not read |
| `erw_validate.py` on the three tables | 0 | PASS, 0 errors, 0 warnings each |
| `build_coverage.py --only` the three tables (data lock) | 0 | 3 rows built, 205 carried over as they stood (session 357's lesson: never a whole rebuild here). The first try failed: an internal table marked derived is refused when its inputs are public, so the hourly table names what it reads ("Read from") and is given the derived tier by rule |
| `load.py --only '^node_basis_(daily|summary)$'` (data lock) | 1 | both match (949,995 and 1,260 written); exit 1 is the sources check only: Supabase holds 12 sources this machine's `sources.csv` lacks, registered by other machines (`erw:iso_queue_statistics` joined today). The database grew from 1,744.5 to 2,057.7 MB |
| page reads of the live set, timed before and after the load (memory note "Live-set growth") | 0 | best of three: battery 0.12 s before, 0.27 just after, 0.14 ten minutes later; the price board 0.12, 0.36, 0.11; ERCOT's hub prices 0.15, 0.58, 0.15. Back to their times once the vacuum's analyze had settled |
| `redivis/upload.py` the four new tables (data lock) | 0 | `node_basis_daily` refused by the 10 GB cap (above); the others count(*) equal |
| `release_v1.py --check` | 0 | the three public tables spliced into main's package (138 with the metadata tables) |
| tests 357, 358, 359, 262, 275, 299, 207, 248, `test_redivis_gates` | 0 | 103 tests |

## Decisions made without you

1. **The day-ahead prices at the nodes come from the 60-Day DAM Disclosure**, an existing ERCOT source with an existing connector, since the asked path keeps seven days. The real-time months are not filled from it or from anywhere: the disclosure holds no real-time price.
2. **The window is 1 October 2025 to the newest day held** (20 October 2026 day-ahead, 18 October real time), not cut at 30 September, so the 20 real-time days meet day-ahead days.
3. **The internal hourly table keeps the storage points' newest days** (13 July to 19 October 2026): storage alone over twelve months is about 2.5 million rows, five times the ceiling; every point's day is in `node_basis_daily`, every hour in the saved files.
4. **Classes of points from ERCOT's resource types**; a point with two classes (a solar and storage pair) is `mixed` and counts only under `all`.
5. **A point counts in a month with 90 percent of the hub's days**; the share wider than the hub compares each point with the hub over the point's own days.
6. **`node_basis_daily` is loaded whole into the live set** (+313 MB), since the code machine reads it tonight; the reads were timed.

## For Samuel's ruling

- **Redivis's free 10 GB is full**: `node_basis_daily` (950,000 rows) could not be drafted. Upgrade the Redivis account, or name tables to drop from the draft, or keep this table out of Redivis (it is in the live set and on this machine). Session 363 meets the same cap.
- **ERCOT's settlement point list** (NP4-160-SG: each node's load zone and hub) as a new source, so that each point's basis can be taken against its own zonal hub; and whether coordinates are wanted from any source.
- **ERCOT's Data Access Portal**: a signed-in account would give the history of real-time node prices; today the ERW keeps what the seven-day list shows, daily.

## Files

- New: `warehouse/derived/node_basis.py`, `tests/test_session358.py`, this report; `docs/methods/node_basis.md` (its shape landed in session 357's first push, its body here).
- Changed: `warehouse/connectors/ercot_rt_spp.py` (`--pull-dam`), `warehouse/metadata/build_coverage.py`, `coverage.csv`, `docs/coverage.md`, `warehouse/metadata/sources.csv` (`erw:node_basis`, `erw:node_basis_hourly`), `warehouse/supabase/live_set.yaml`, `docs/redivis/release-v1/` and `release-v1.md`, `warehouse/metadata/redivis_uploads.csv`, `docs/reviews/packs/battery.md`, `generator.md`, `datacenter.md`.
- Outside git: the three tables in `warehouse/output/`; 79 disclosure zips in `warehouse/raw/ercot_60d_dam/zips/`; 31 day files in `warehouse/raw/ercot_dam_spp/zips/`; `runs/s358/`.
