# Session 674 report: method notes for the tables of 21 October, batch 1 of 5

22 October 2026, from about 09:28 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0. Pulls: none.

## Read these first

- **10 notes written** under `docs/methods/`, covering 10 tables, from the plan of session 674 ([`docs/reviews/method-notes-plan-2026-10-23.md`](../../docs/reviews/method-notes-plan-2026-10-23.md)). Each holds the publisher and report, the address, the vintage and revision rule, every column or variable with its unit, the shape, the license verdict, the connector's cross-check and what the table does not hold, and a `Tables:` line.
- **The five batches were written at once** by five helper agents of this Claude Code session, each reading only its connectors, the tables' headers and the license record, and writing only its own notes; each note was then checked here (it exists, names its tables, carries no em or en dash: `tests/test_session674.py`).
- **`docs/coverage.md` gains a last column, `Method`**, linking each table's note: a note named after the table, or one whose `Tables:` line names it (`build_coverage.py`). The page takes the column at its next build, a whole build or `--only` (session 673's).

## Notes

- `docs/methods/eia861_utility_sales.md`: `eia861_utility_sales`
- `docs/methods/eia861m_utility_sales_monthly.md`: `eia861m_utility_sales_monthly`
- `docs/methods/eia923_plant_fuel_annual.md`: `eia923_plant_fuel_annual`
- `docs/methods/egrid_power_plants.md`: `egrid_power_plants`
- `docs/methods/eia_state_capacity_annual.md`: `eia_state_capacity_annual`
- `docs/methods/eia_state_source_disposition_annual.md`: `eia_state_source_disposition_annual`
- `docs/methods/eia_energy_efficiency_state_annual.md`: `eia_energy_efficiency_state_annual`
- `docs/methods/eia_meters_state_annual.md`: `eia_meters_state_annual`
- `docs/methods/eia_net_metering_state_annual.md`: `eia_net_metering_state_annual`
- `docs/methods/eia_power_co2_state_annual.md`: `eia_power_co2_state_annual`

## What the notes found

- `eia861m_utility_sales_monthly` holds EIA's own aggregates for 2017 to 2021: the estimate "Adjustment <year>" (utility 0) and "Total EPM" (utility 88888), 9,360 rows of each a year; the connector's exclusion rule misses both names in those years' files. The note warns; the connector and table are unchanged (under "For Samuel's ruling").
- `eia861_utility_sales`: 111 rows of two entities (`eia861:19784:WA:A:BPAT`, `eia861:40355:AZ:A:AZPS`, 2015 to 2025) have an empty `source_url` and empty `x_*` fields; the header's "Years held" line names 2025 only while the file holds 2015 to 2025.
- `eia_net_metering_state_annual`: the docstring says all technologies in every year, but 2013 to 2019 hold photovoltaic, wind and other technologies; the note follows the table.
- `eia861m_sales.py`: the docstring's ceiling (6) and the code's (11) differ.

## Decisions made without you

- The notes were written in parallel, out of the chain's order (while session 663's upload was processing), since they share no file with sessions 663 to 673.
- A table and a note were matched by the table's first appearance in `coverage.csv` (21 or 22 October), not by `last_run` alone: 162 tables were last run on 21 October, most of them daily tables with notes.
- The coverage page links a note by its file name or its `Tables:` line only, not by any mention, so a note that discusses a table in passing is not taken for its method.

## For Samuel's ruling

- Whether `eia861m_sales.py` should leave out EIA's two aggregates in 2017 to 2021 and the table be rewritten (a data change; not made).

## Files

- New: the notes above, this report, `tests/test_session674.py`, `docs/reviews/method-notes-plan-2026-10-23.md`. Changed: `warehouse/metadata/build_coverage.py`.
