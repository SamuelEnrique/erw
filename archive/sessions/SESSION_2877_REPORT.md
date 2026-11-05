# Session 2877 report: a zone's own demand growth

5 November 2026, about 21:40 to 22:07 UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **`subregion_demand_growth` is written:**
  - 3,918 rows, 90 EIA-930 sub-regions, 2019 to 2026. 552 sub-region years have figures (at least 95 percent of their hours used).
  - Derived from `eia930_subba_demand_hourly_2019` to `_2025` and the rolling `eia930_subba_demand_hourly`, held here. No request.
  - The write ran under the data lock: validator PASS; coverage public, power, tier derived, with the Method cell; archived (run `20261105T220645Z-local`); licenses check 0 problems; release rows added.
- **What a row gives:** each sub-region year's peak hour and its time, the mean of the hours used, the energy, the hours used and due, and the growth of the mean and of the peak from the year before.
  - An hour is used by the grid table's rule (`impossible_hours.screen`).
  - Growth is written only between two years that have figures.
  - 2026 gets no figures: the rolling table holds only from 24 July.
- **The All grids tab already shows a zone's own growth** for the rows whose zone is a sub-region (session 728, `headroom.json` `zones`, the mean of 2025 against 2024 computed in the builder). This table was not substituted there: it screens hours, so its figures differ slightly, and that would move a tab figure. The siting gaps row stays "filled" for those rows. This table adds the peak, the earlier years and the method note.
- **Tests:** `tests/test_session2877.py` (6), on a fixture.

## Decisions made without you

- **UTC calendar years.** A sub-region's time zone is not in the source table.
- **The tab not rewired** to this table (above).

## Files

- On `wip/c147-data`: `warehouse/derived/subregion_demand_growth.py`, `docs/methods/subregion_demand_growth.md`, `tests/test_session2877.py`, `warehouse/metadata/build_coverage.py` (the two new tables' rules), the metadata rows.
- On the data machine only: `warehouse/output/subregion_demand_growth.csv`.
