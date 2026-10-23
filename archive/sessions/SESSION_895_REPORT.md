# Session 895 report: chain 051 written first; reserve margins by NERC assessment area (EIA-411)

23 October 2026, from 06:09 UTC, on lab-desktop (the data machine), the first session of `queue/done/049-day-23-october-data-margins-schedules-emissions.md`. Model spend USD 0. Pulls: EIA, 9 requests of 10 (its robots file, the Electric Power Annual's page, the EIA-411 page, the three workbooks, and the connector's three).

## Read these first

- **Chain 051 written and pushed first:** `queue/next/051-day-23-october-data-world-gas-hydro.md` (sessions 909 to 922, machine: data), committed alone and pushed to main (`c8a0e557`) with a snapshot pair (0 differences), before any other work. Chain 049's file asked for `050-<slug>.md`, but the code machine's chain already holds 050.
- **The Electric Power Annual no longer carries the tables the queue file named:** its current page has no NERC peak demand or capacity margin table. Those figures came from Form EIA-411, whose page still links the program's last release (November 2016).
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `eia411_capacity_margins_annual`, 2,924 rows, 17 assessment areas. It holds summer and winter peak load, net internal demand and capacity resources (MW) and capacity margin (percent), 1990 to 2016 actual and 2017 to 2027 projected (winter resources and margins from 2001/2002). It covers every NERC area of the time, the dissolved ones (ECAR, MAAC, MAIN, MAPP) and EIA's Balance of Eastern Region and contiguous U.S. This fills the siting gaps' "Reserve margins: open" with the only federal series for every region, ending in 2016 actual.
- **The cross-check: each margin against its own row's resources and demand.**
  - Before 2015, when EIA calculated the margins: 284 of 285 summer rows and 151 of 153 winter rows equal (resources less demand) over resources, the capacity margin EIA's heading names.
  - From 2015, when NERC sent them: 75 of 130 a season match that, and 55 instead equal (resources less demand) over demand, a reserve margin. They are FRCC, MISO, PJM, SPP and TRE, every projected year 2017 to 2027 in both seasons (110 values).
  - The table keeps EIA's values as given. The header counts and names those rows, computed by the connector on every run.
  - ERCOT's own CDR margins (`ercot_cdr_reserve_margins`) start in 2026 and do not overlap. EIA-930's demand table holds no 2015 or 2016 hours, so the peak loads could not be checked against it.

## Decisions made without you

- **EIA-411's 2016 release taken in place of the Electric Power Annual's tables,** which no longer exist. It is dated, and the header says so.
- **Peak periods as EIA defines them:** `ts_utc` is the summer peak period's first day (1 June) and the winter's (1 October of the season's first year).
- **The release package's README regenerated whole.** The old laptop's sessions (1001 on) had added a paragraph on the packages to `release_v1.py` without writing the README again. `finish_table.sh` refused the difference as more than the held-tables sentence; the generator's output was taken, and `release_v1.py --check` passes.

## For Samuel's ruling

- Whether the ERW should read NERC's Long-Term Reliability Assessment for current margins (NERC's terms are among the standing questions).

## Files

- New: `warehouse/connectors/eia411.py`, `tests/test_session895.py` (4 tests), this report, `queue/next/051-day-23-october-data-world-gas-hydro.md` (on main).
- Changed:
  - `build_coverage.py`, `release_v1.py`, `live_set.yaml`
  - `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`
  - `license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/` (the README regenerated)
- On the data machine only: `runs/c049/`, `runs/license_reads/s895/`, `runs/s895*`.

## Corrected by session 905

The method notes' checks (session 905) found these against the code and the tables:

- EIA's winter file names RFC with a footnote mark (`RFC[5]`), which the first write kept: RFC's winter figures for 2005 to 2009 stood under a second entity, and "17 assessment areas" were 16. Session 905 strips the mark and wrote the table again; its header now counts 16 areas. The contiguous U.S. is `eia411:contiguous_u_s`, as the slug writes it.
