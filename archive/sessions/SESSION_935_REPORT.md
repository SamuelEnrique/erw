# Session 935 report: the package's and the site's records

23 October 2026, from 10:26 UTC, on lab-desktop (the data machine), a session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`. Model spend USD 0. Pulls: none. Run in the branch's worktree while session 933's upload ran (no file of the main checkout read or written).

## Read these first

- **Stale, as after chains 048 and 051:** `python package/tools/build_tables.py --check` exited 1. The package's `tables.csv` shipped 346 rows against 353 in the record, and the 7 that differ are this chain's new tables (`eia_world_oil_gas_annual`, `eia_world_oil_monthly`, `nrc_power_reactors`, `wb_commodity_prices_monthly`, `eia_power_fuel_stocks_monthly`, `ornl_hydropower_relicensing`, `ercot_node_planned_generation`); the site's two files differed with it.
- **Rebuilt:** `build_tables.py` wrote 353 tables (public 250, internal 54, unsettled 49); `--check` then exits 0.
- **The tests of sessions 1001, 1008 and 1009 pass** against the rebuilt files.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_verdicts.json`, `site/data/table_citations.json`.
