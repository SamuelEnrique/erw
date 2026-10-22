# Session 675 report: method notes for the tables of 21 October, batch 2 of 5

22 October 2026, from about 09:28 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0. Pulls: none.

## Read these first

- **10 notes written** under `docs/methods/`, covering 36 tables, from the plan of session 674 ([`docs/reviews/method-notes-plan-2026-10-23.md`](../../docs/reviews/method-notes-plan-2026-10-23.md)). Each holds the publisher and report, the address, the vintage and revision rule, every column or variable with its unit, the shape, the license verdict, the connector's cross-check and what the table does not hold, and a `Tables:` line.
- **The five batches were written at once** by five helper agents of this Claude Code session, each reading only its connectors, the tables' headers and the license record, and writing only its own notes; each note was then checked here (it exists, names its tables, carries no em or en dash: `tests/test_session674.py`).

## Notes

- `docs/methods/eia930_subba_demand.md`: `eia930_subba_demand_hourly`, `eia930_subba_demand_hourly_2022`, `eia930_subba_demand_hourly_2023`, `eia930_subba_demand_hourly_2024`, `eia930_subba_demand_hourly_2025`
- `docs/methods/ferc714_area_demand.md`: `ferc714_area_demand_2006`, `ferc714_area_demand_2007`, `ferc714_area_demand_2008`, `ferc714_area_demand_2009`, `ferc714_area_demand_2010`, `ferc714_area_demand_2011`, `ferc714_area_demand_2012`, `ferc714_area_demand_2013`, `ferc714_area_demand_2014`, `ferc714_area_demand_2015`, `ferc714_area_demand_2016`, `ferc714_area_demand_2017`, `ferc714_area_demand_2018`, `ferc714_area_demand_2019`, `ferc714_area_demand_2020`, `ferc714_area_demand_2021`, `ferc714_area_demand_2022`, `ferc714_area_demand_2023`, `ferc714_area_demand_2024`, `ferc714_area_demand_2025`, `ferc714_respondents`
- `docs/methods/eia_nuclear_outages.md`: `eia_nuclear_outages_daily`, `eia_nuclear_outages_facility_daily`, `eia_nuclear_outages_generator_daily`
- `docs/methods/nlr_atb_electricity_costs.md`: `nlr_atb_electricity_costs`
- `docs/methods/uswtdb_wind_turbines.md`: `uswtdb_wind_turbines`
- `docs/methods/epa_ghgrp_power_co2.md`: `epa_ghgrp_power_co2`
- `docs/methods/eia_co2_state_annual.md`: `eia_co2_state_annual`
- `docs/methods/eia_seds_state_energy.md`: `eia_seds_state_energy`
- `docs/methods/eia_aeo_electricity.md`: `eia_aeo_electricity`
- `docs/methods/eia_steo_forecasts.md`: `eia_steo_forecasts`

## What the notes found

- `eia_steo_forecasts` is the one table of the batch that keeps earlier releases (merged on entity, variable, ts_utc and vintage).
- `eia_aeo_electricity` holds eight USD/kWh series twice, in 2025 dollars and nominal; the note says which is which.
- The nuclear outages' daily sum against EIA's U.S. total and FERC 714's ERCOT hour check are session reports' checks, not the connectors'; the notes say so.

## Decisions made without you

- The notes were written in parallel, out of the chain's order (while session 663's upload was processing), since they share no file with sessions 663 to 673.
- A table and a note were matched by the table's first appearance in `coverage.csv` (21 or 22 October), not by `last_run` alone: 162 tables were last run on 21 October, most of them daily tables with notes.

## For Samuel's ruling

- None new.

## Files

- New: the notes above, this report.
