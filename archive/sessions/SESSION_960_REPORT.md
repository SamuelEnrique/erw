# Session 960 report: method notes for chain 054's tables

23 October 2026, from 12:58 UTC, on lab-desktop (the data machine), a session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`. Model spend USD 0. Pulls: none.

## Read these first

- **Every one of the chain's eleven tables has its note, linked from `docs/coverage.md`'s Method column:**
  - New: `docs/methods/onrr.md` (the three ONRR tables), `eia_primary_energy_monthly.md`, `usgs_mcs_critical_minerals.md`, `blm_ca_renewable_rows.md`, `eia_coal_distribution_quarterly.md`, `eia_uranium_production.md` (both uranium tables).
  - Extended: `docs/methods/lbnl_projects.md` (`lbnl_wind_costs`, `lbnl_wind_turbine_orders`, a section; its "What they do not hold" corrected, since the wind file's costs are now held).
- **Each note's checks against the code and the table, as session 946's:** every count computed again from the table read past its header lines; every rule read against its connector.
- **One contradiction found, acted on:** `eia_uranium_production.py`'s description gave its ceiling as five requests, "the page and the four workbooks"; it asks only for the four workbooks. The description is corrected (the table is not changed: the header does not state the ceiling). Session 957's one false header line (EIA's "truncations") had been found and removed in that session, the table written again.
- **The chain's tests pass together** (sessions 951 to 958, 34 tests).

## Decisions made without you

- **No note for `eia_sector_energy_consumption_monthly`,** which shares `eia:total-energy` with the new MER table but is not this chain's; its note is a later session's.

## For Samuel's ruling

- None new.

## Files

- New: the six notes above, this report.
- Changed: `docs/methods/lbnl_projects.md`, `warehouse/connectors/eia_uranium_production.py` (its description), `docs/coverage.md`, `warehouse/metadata/coverage.csv` (the Method cells).
- On the data machine only: `runs/c054/s960/`.
