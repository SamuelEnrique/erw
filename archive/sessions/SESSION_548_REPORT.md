# Session 548 report: nuclear outages by reactor, 2015 on

21 October 2026, from 22:02 UTC, on lab-desktop (the data machine), the first session of `queue/done/030-night-22-october-sources.md` (its trial run while chain 029's landing waited for its checks). Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia_nuclear_outages_generator.py`: each reactor's capacity, outage and outage share, a day**, from EIA's API v2 (route `nuclear-outages/generator-nuclear-outages`), as `eia_nuclear_outages_generator_daily`.
  - 1,239,117 rows: 102 reactors at 62 plants, 4,312 days from 1 January 2015 to 21 October 2026, with no day missing.
  - The entity is `eia_nuclear_outages_gen:<plant>:<reactor>`.
  - The connector is session 516's by plant, with its two windows, its reading until a short page and its day checks.
- **Session 516's puzzle answered.** The reactor route's records from 2015 number 413,039: exactly the "total" EIA's plant route reported for its 247,167 plant rows. That total counts reactors, not plants.
- **Cross-check** (`runs/s548/crosscheck.py` on the data machine): the reactors' outage and capacity summed by plant and day against `eia_nuclear_outages_facility_daily`. They are equal on all 247,167 plant-days, with the largest gap 0.0 MW.
- **Written under the data lock** (22:20 UTC) with `--from 2015-01-01 --offline` (0 requests). The validator, coverage and archive exited 0 (1,239,117 rows). Session 549 adds 2007 to 2014.
- **Held** from `/data` and Redivis v1. Sector rule (`power;uranium`). Tests: `tests/test_session548.py`, 5.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 83 of 100 | 2015 on (83 pages, the last one short) |

## Files

- New: `warehouse/connectors/eia_nuclear_outages_generator.py`, `tests/test_session548.py`, this report. Changed: the shared metadata, holds and package.
