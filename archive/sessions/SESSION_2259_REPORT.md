# Session 2259 report: four southeastern European grids a day (Energy-Charts: Hungary, Romania, Greece, Bulgaria)

24 October 2026, from 04:22 UTC, on lab-desktop (the data machine), a session of `queue/done/102-day-5-november-data-poland-belgium-new-zealand-columbia.md`, the second source of the session's own choosing. Model spend USD 0. Pulls: api.energy-charts.info, 4 requests of 20 (one a country, 2020 to 23 October 2026, 35 seconds apart; the robots address and the license were read in session 2253). The trial and the write ran offline.

## Why this source

None of the four grids was in the ERW: Hungary's (nuclear and gas), Romania's (hydro, nuclear and coal), Greece's (gas, sun and wind, its lignite closing) and Bulgaria's (nuclear and lignite). Energy-Charts publishes them under CC BY 4.0 (the verdict of session 2257). Austria, Switzerland and Czechia were left to chain 103, whose agent asked first; Italy is chain 104's fallback.

## Read these first

- **One series table, `energy_charts_southeast_europe_daily`:** 128,530 daily figures in 58 series, 1 January 2020 to 22 October 2026, in MWh:
  - each country's public net production by type;
  - its load and residual load;
  - its cross-border trading.
- **Summed to UTC days:** Energy-Charts gives Hungary in quarter hours, Romania in quarter hours then hours, and Greece and Bulgaria in hours. At the published grain, four countries would run to millions of rows, so each complete UTC day of mean power is summed to energy (MW times each period's length). Each row keeps the number of periods summed (`x_periods`). A day is summed for a type only when its periods cover all 86,400 seconds and none is blank.
- **Days not summed, counted in the header:**
  - each type's first and last UTC day, which the countries' local days cut short;
  - the days with a blank, most of them series that begin later (batteries, for one).
- **The cross-check** (`runs/c102/s2259/cross.py`):
  - **Against Eurostat's months** (73 to 80 each):
    - load is 0.97 (Greece) to 1.18 (Bulgaria) of the supply for the internal market;
    - wind is 0.88 to 1.00, and nuclear 1.00 to 1.09;
    - solar is 0.97 to 0.99 in Bulgaria and Greece, but 0.66 in Hungary and 0.75 in Romania. Energy-Charts' solar there seems to be the solar the grid operators see, without the rooftops Eurostat counts.
  - **Against Ember's yearly demand,** load is 0.98 to 1.04 for Bulgaria and Romania, 0.87 to 0.90 for Greece and 0.88 to 0.92 for Hungary.
- **Registered:**
  - the sector rule (`power`);
  - both holds;
  - the release package's rows;
  - the license tables (licenses check: 0 problems; release check: 0 differences).

  Only this table's metadata rows were added to the branch, since the write's patch carried other chains' rows again. The test is `tests/test_session2259.py` (5 tests).

## Errors

- None.

## Decisions made without you

- **This source chosen,** for the reason above.
- **Days, not quarter hours,** for the table's size; the method is in the header and the connector.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/energy_charts_southeast.py`, `tests/test_session2259.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c102/s2259/`.
