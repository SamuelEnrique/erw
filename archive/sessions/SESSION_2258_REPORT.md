# Session 2258 report: what the United States builds, data centers and power among it (the Census Bureau's C30)

24 October 2026, from 04:16 UTC, on lab-desktop (the data machine), a session of `queue/done/102-day-5-november-data-poland-belgium-new-zealand-columbia.md`, the first source of the session's own choosing. Model spend USD 0.

Pulls: 6 requests of 20:
- the C30 historical data page;
- the private seasonally adjusted and not adjusted time series;
- the private power detail, which answered HTTP 500;
- the public seasonally adjusted and not adjusted time series.

www.census.gov's robots address and the C30 data page were read in session 2257. The trial and the write ran offline.

## Why this source

The ERW tracks data centers' power demand but held no measure of what is spent building them. The Census Bureau's monthly construction spending gives it directly, with the spending on power plants and electric construction, private and public. It is a work of the U.S. government, and the Census Bureau's verdict is on record. No chain had taken it.

## Read these first

- **One series table, `census_c30_construction_monthly`:** 88,376 monthly figures, January 1993 to August 2026, in USD (the Census Bureau's millions times 1,000,000), each kept both ways:
  - the 67 private types of construction, data centers among them from January 2014;
  - the 43 public types (public in all, state and local, federal), power among them.

  Each month is given seasonally adjusted at an annual rate (`value_put_in_place_saar`) and not adjusted (`value_put_in_place`). The Census Bureau's p (preliminary) and r (revised) marks are kept in `x_status`.
- **What the figures show** (not seasonally adjusted, whole years):
  - private data center construction rose from 1.8 billion USD in 2014 to 6.9 billion in 2018, 12.6 billion in 2022, 34.8 billion in 2024 and 49.7 billion in 2025;
  - private power construction (gas and oil included) rose from 98 to 152 billion over the same years, and electric from 70 to 128 billion;
  - public power went from 12 to 20 billion.
- **The cross-check** (`runs/c102/s2258/cross.py`):
  - each year's unadjusted months sum to within 0.4 percent of the mean of its seasonally adjusted annual rates for total private construction, within 0.7 percent for data centers, and within 1 to 3 percent for power and electric;
  - private residential plus nonresidential equals the private total to 1 million USD in every month.
- **Not taken:** the private power detail (`privatepower.xlsx`, HTTP 500 at its listed address), and the state and regional tables (annual).
- **Registered:**
  - the sector rule (`power;datacenters`);
  - both holds;
  - the release package's rows;
  - the license tables (licenses check: 0 problems; release check: 0 differences).

  The test is `tests/test_session2258.py` (4 tests).

## Errors

- **The write's metadata patch carried other chains' rows** (Eurostat, Statistics Norway, DESNZ), which the main checkout's files hold. Only this table's rows were added to the branch (`runs/c102/add_own_rows.py`). This chain's earlier writes were checked against the branch's base: they added only their own tables.

## Decisions made without you

- **This source chosen,** for the reason above.
- **Every type kept,** not only the energy ones, since the totals and the data center line read best beside the rest.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/census_c30.py`, `tests/test_session2258.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c102/s2258/`, `runs/c102/add_own_rows.py`.
