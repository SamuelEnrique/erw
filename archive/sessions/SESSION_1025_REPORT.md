# Session 1025 report: the tables as they land

23 October 2026, on samueloldlaptop, unattended, in the worktree `C:/Users/lossa/Documents/erw-1022` on `wip/1025-allgrids` (cut from `wip/1024-allgrids`). Chain `queue/done/071-night-23-october-code-allgrids-packages.md`, session 1025. Model spend USD 0. No request; no warehouse data written; no build. Read only: the repository on main.

## Read these first

- **Two of the tab's awaited tables have landed, both public**: `ercot_cdr_reserve_margins` (series, 1,600 rows, 1 March 2026 to 1 December 2030, ERCOT's Capacity, Demand and Reserves report of December 2025, written 01:40 UTC on 23 October, in the live set) and `ercot_transmission_projects` (events, 2,122 rows, 25 May 2023 to 15 December 2033, written 01:45 UTC, in the live set). License word for both: "public" (`docs/licenses.md`, the record agrees). Session 1027 wires the first; session 1028 reads the second.
- **Not landed**: `ercot_settlement_points` (1026's), `hifld_substations` and `hifld_transmission_lines` (1028's), `utility_large_load_tariffs` (it waits on the owner's OpenEI key, rulings 18), a 2026 sub-region year (`eia930_subba_demand_hourly_2026`; the rolling `eia930_subba_demand_hourly` holds 24 July to 21 October 2026, not a year), and the data machine's chain 049 tables (reserve margins by NERC assessment area, session 895; an ERCOT node's county and zone, session 901), whose chain began about 06:00 UTC.
- **Two tables 901 will join are on main** since this night: `ercot_cdr_units` (1,772 rows, public) and `eia860_plants_annual` (17,349 rows, public).

## What was read

`warehouse/metadata/coverage.csv` on main at about 06:55 UTC (pulled first), `docs/licenses.md`'s table, `warehouse/supabase/live_set.yaml`, the method note `docs/methods/ercot_cdr_reserve_margins.md`. Neither table is in this machine's `warehouse/output/` (a code machine's): 1027 reads the reserve margins from the live set with the anon key (1,600 rows, two requests).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |

## The landing

Lands with the next landing of this chain.

## Decisions made without you

1. None beyond the chain's rule for a session that finds nothing to do (a few lines, no build).

## For Samuel's ruling

- None new.

## Files

- New: this report.
