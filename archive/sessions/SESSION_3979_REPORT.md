# Session 3979 report: the daily run of 15 November, the first with chain 278's four fixes

Energy Research Warehouse (ERW). Chain 279, data machine (lab-desktop), 15 November 2026, 14:53 to 17:40 UTC (waits polled, an empty commit every 20 minutes from 00:00 UTC). Opus 5.5. Model spend USD 0. No request to a publisher. The job's log read with the token (`runs/c278/daily_1115.log`, 4.9 MB).

## The daily run (run 43721915639, dispatched 14:00 UTC, main at `5859cde2d`)

- **Coverage passed** (both of 14 November's stops are gone), **`daily run` ok at 16:57 UTC**, and **the daily commit reached main through the guard**: `03a8a9216` "Daily prices 2026-11-15", the first since 12 November; the health summary of 14 November at `f8f6728cb`. Its line: "**Stale on main:** hourly network, 4.2 hours" (the hourly job skips while the daily run holds the lock).
- **The owner's API key's limit shows:** `news_score` failed ("calls 0 (16 failed); stories scored 0 of 400") and `policy_score` scored nothing new. Expected until 1 December; no other key tried.
- **Expected skips:** `eia_series` (EIA's budget of 15 minutes), `ercot_as_prices` (ruling 2), `carb_lcfs` (CARB 55 days old).
- **`supabase_load` failed on four tables**, the load's own guard each time:
  - `datacenter_projects`, `energy_deals`, `news_index`: "refused, older than the live copy". The run of 13 November loaded them, and its commit was refused, so the runner's copies (from main) are behind the live set: `news_index` 20,852 here, 21,252 live (400 only live); `energy_deals` 583 and 590; `datacenter_projects` retrieved 12 against 13 November. The model steps that would rebuild the first two are refused by the key's limit. The live copies stay as they are (newer); a ruling below.
  - `sources`: the stale IEA row with its en dash (session 3984's ruling: `load.py --prune`).
- **`package tests` failed on one table:** `test_fetch_types_and_provenance[datacenter_tracker_rollups]`, `assert meta["sources"]` an empty list.

## The fault, fixed

- **Cause:** the builder wrote "Sources: datacenter_projects (...)"; the package's provenance (`package/src/erw/provenance.py` `parse_header`) reads a "Source:" line, as every other derived builder writes it ("Source: <id> ERW derived table, ..., <method url>").
- **Fix:** `warehouse/derived/datacenter_tracker_rollups.py` writes "Source: erw:datacenter_projects ERW derived table, ... (docs/methods/datacenter_tracker_rollups.md), <its address>". Test (3 checks: the line in the builder, the package's parse of such a line, the builder run into a temporary folder and its header parsed as the package reads it): with test 3889, 14 passed.
- **Misnumbered:** committed as test and session "3999", a number of chain 285's file; renamed to 3979 in this chain's next gate. Gate g (`wip/c279-land-g`) started 17:32 UTC with the old name.

## Waiting

- **The data machine's run of 15 November**: holds the lock from 17:10 UTC (it waited for the daily run's).
- **The Roundup of 15 November** (Sunday evening); **the Digest of 16 November**.

## Decisions made without you

- **Gate g left to run under the wrong number** rather than stopped: the rename is a file name and three comments, landed in the next gate.

## For Samuel's ruling

- **Three live tables newer than main's copies** (`datacenter_projects`, `energy_deals`, `news_index`, from the refused commit of 13 November). Default: the load's guard stands and the live copies stay; `news_stories` on main lacks 13 November's 400 stories, which only the live `news_index` now holds. A person's `python scripts/sync.py --refresh` on the runner's side, or `--allow-older`, would decide otherwise.
