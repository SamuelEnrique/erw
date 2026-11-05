# Session 932 report: method notes for chain 052's tables

23 October 2026, from 10:22 UTC, on lab-desktop (the data machine), a session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`. Model spend USD 0. Pulls: none.

## Read these first

- **Notes for every table of the chain**, each linked from `docs/coverage.md`'s Method column:
  - `docs/methods/eia_world_oil_gas.md` (new; `eia_world_oil_gas_annual` and `eia_world_oil_monthly`);
  - `docs/methods/nrc_power_reactors.md` (new);
  - `docs/methods/wb_commodity_prices_monthly.md` (new);
  - `docs/methods/eia_power_fuel_stocks_monthly.md` (new);
  - `docs/methods/ornl_hydropower.md` (extended with `ornl_hydropower_relicensing`);
  - `docs/methods/ercot_node_planned_generation.md` (written by session 931).
- **Each note's checks against the code and the table, as session 918's:** every count computed again from the table read past its header lines, every rule read against its connector. Each series' first month in the Pink Sheet, each sector's and type's count of the reactors, the relicensing records' date kinds and statuses, the stocks' units and locations: all as the tables hold them.
- **One contradiction, in a report, acted on before this session:** session 930's report first said the relicenses whose capacity differs from the fleet table's "are relicenses with changed capacity"; it now says they differ "where the new license changes the capacity or ORNL counts the plant otherwise", which is what the check shows. No fault in a connector or a table was found; no table was written again.

## Decisions made without you

- **One note for the two oil and gas tables,** and the relicensing table added to the ORNL note, as session 918 did for ORNL's two.

## For Samuel's ruling

- None new.

## Files

- New: the four new notes above, this report.
- Changed: `docs/methods/ornl_hydropower.md`, `docs/coverage.md`, `warehouse/metadata/coverage.csv` (the Method cells).
