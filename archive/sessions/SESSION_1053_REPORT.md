# Session 1053 report: the package reads the new tables

23 October 2026, about 08:05 UTC, on samueloldlaptop, unattended, on `wip/1042-allgrids`. Chain `queue/done/072-day-23-october-code-allgrids-packages-2.md`, session 1053. Model spend USD 0. Requests: 0 to the live set, 0 to Redivis (ceilings 50 and 50). The script is `runs/chain_072/pkg1053.py` (not in git; its results below).

- **Neither table that 1047 and 1048 read is in the live set** (`live_window` none: chain 049 put them on `catalogue_hold`), and the Stanford dataset's release is your click. So the package reads them from a clone's tables (`set_backend(<dir>)`, the tables rebuilt from the archive).
- **1048's panel reproduced for 7RNCHSLR_ALL**: `fetch("ercot_node_places")` gives FAYETTE, SOUTH (the page's). From `fetch("ercot_transmission_projects")`, the phases with either end in Fayette: 7 future, 0 planned, 1 completed, equal to the page's three keyed figures. 569 nodes placed, the page's count.
- **1047's comparison reproduced**: `fetch("eia411_capacity_margins_annual", entity=["eia411:tre"], start="2027-06-01", end="2027-06-02")`, resources over net internal demand, less 1: 38.07%, the method note's figure.
- **`tables()` and `coverage()` list chain 049's public tables with their windows** (on this branch's record, main merged after chain 049 landed): `eia411_capacity_margins_annual` (1990 to 2027, 2,924 rows), `ercot_node_places` (one snapshot, 569), `eia923_fuel_receipts` (2025, 36,733), `eia_power_costs_annual` (2015 to 2025, 550), `eia_uranium_marketing_annual` (2003 to 2025, 763), `eia_gas_pipeline_projects` (1903 to 2031, 1,334); each `in_live` no. Chain 051's tables (world gas and hydro) have not landed: that chain was still running.
- **A table in no backend, named**: every one of these is in no backend a stranger can reach today (not in the live set; the Stanford release not clicked). Asked of the live set, the package now says so (session 1056).
- One finding for a clone whose tables sit outside the repository: with `ERW_DATA_DIR` set there, the record (`coverage.csv`, `sources.csv`, the license record) is looked for beside it, and the verdict column came back empty until `ERW_COVERAGE_CSV` and `ERW_SOURCES_CSV` were set. The error names the variable to set; left as it is (a clone's tables live in `warehouse/output`).

## The landing

Lands with the next landing of this chain.

## Decisions made without you

1. **Read from a clone's tables**, the only backend that holds them; said so.

## For Samuel's ruling

- None new (the Redivis click, packages-open item 5, is what puts these tables in a backend a researcher reaches).
