# Session 2168 report: the UK's electricity by fuel (DESNZ's Energy Trends), a source of the session's own choosing

24 October 2026, from 00:35 UTC, on lab-desktop (the data machine), the seventh session of `queue/done/094-day-31-october-data-britain-imports-gas-use-waterways.md`, unattended. Model spend USD 0. Pulls: 2 requests of 20 (below; the page and its licence were read in session 2167).

## Read these first

- **Why this source:** the UK government's Energy Trends table 5.1 is the official quarterly record of the UK's electricity generated and supplied by fuel, from 1998, under the Open Government Licence; the ERW held none of it, no queue file of chains 057 to 097 plans it, and it sets beside session 2162's Great Britain demand the fuels that met it. The first choice, Hydro-Quebec's open data, is closed to the reader (session 2167).
- **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `desnz_uk_electricity_quarterly`, tables 5.1b (electricity generated) and 5.1c (electricity supplied, net imports a row of it) by generator type (major power producers, other generators, all generating companies) and fuel, the first quarter of 1998 to the second of 2026: 7,862 rows, 43 generator type and fuel rows, in MWh (DESNZ's TWh times 1,000,000). The latest quarter's total generated, 68.6 TWh, is the figure DESNZ's own commentary gives.
  - **84 rows of quarters DESNZ marks "[provisional]"** are kept with `x_provisional` yes; they are revised in a later issue.
  - "[x]" (no figure, as for offshore wind before it was counted apart) has no row. Totals are DESNZ's rows, never sums made here.
- **The cross-check** (`runs/c094/s2168/cross.py`):
  - DESNZ's arithmetic: in all 114 quarters the fuels of all generating companies sum to its total generated within 0.0003%.
  - The UK's electricity supplied a year, 304.1 to 308.9 TWh from 2023 to 2025, lies between Great Britain's transmission demand (INDO, 227.9 to 230.6 TWh, `elexon_gb_demand_daily`) and Ember's UK demand (315.8 to 321.4 TWh): INDO leaves out embedded generation and Northern Ireland; Ember's demand counts the losses and own use that "supplied" nets out.

## The pulls

1. `assets.publishing.service.gov.uk/robots.txt` (read 316): HTTP 404, no robots file.
2. Table ET 5.1, September 2026 issue (360 KB), seeded into the raw store with session 2167's copy of the page; the trial and the write read both offline.

## Errors

- **The first trial stopped on the header "Quarter 2 2026 [provisional]";** the provisional quarters are now kept and marked.
- **`tests/test_session205.py`'s bound was raised once more** for this chain's reads (290 to 304 on its branch).

## Decisions made without you

- **DESNZ's Energy Trends 5.1 as the session's own choice,** for the reasons above.
- **Generated and supplied taken, fuel used (Mtoe and million tonnes) and the shares not:** the standard holds no Mtoe, and the shares are DESNZ's ratios of the rows taken.
- **Provisional quarters kept and marked** rather than left out.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_energy_trends.py`, `tests/test_session2168.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `warehouse/metadata/license_reads.csv` (316), `tests/test_session205.py`, the coverage, sources, archive manifest and license files, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c094/s2168/`, `runs/license_reads/s2168/`, `runs/s2168_*`, `warehouse/raw/desnz_energy_trends/`.
