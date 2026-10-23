# ERCOT's resources, unit by unit, from the Capacity, Demand and Reserves report

Energy Research Warehouse (ERW), method note written in session 877 (chain 047) for a table first written on 23 October 2026.

Tables: `ercot_cdr_units`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), Capacity, Demand and Reserves Report (CDR), sheet "Unit Details". The
connector reads ERCOT's resource adequacy page, `https://www.ercot.com/gridinfo/resource`, and takes the newest CDR
workbook it links, the same page and workbook as `ercot_cdr_reserve_margins`. When written:
`https://www.ercot.com/files/docs/2025/12/19/CapacityDemandandReservesReport_December2025.xlsx`. Connector:
`warehouse/connectors/ercot_cdr_units.py` (session 872).

ERCOT's robots file disallows `/misapp` and `/misdownload`. ERCOT posts its resource lists there, so they were not read,
and none was asked for. The CDR is posted under `/files/docs/`, which the robots file allows, and its "Unit Details"
sheet gives each unit's code, county and zone. That sheet was used in place of the resource lists.

## Vintage and revision

The December 2025 report, posted 19 December 2025 (`vintage` 2025-12-19, the date in the file's address). The workbook
is the one session 851 saved in `warehouse/raw/ercot_cdr/`, retrieved 2026-10-23T01:40:30Z; the table was written
2026-10-23T03:30:49Z. Session 872 made no request. A snapshot: each run replaces the table whole with the newest report
the page links, so an earlier edition is not kept. Ceiling two requests a run (the page and the workbook), none when both
are saved.

## Shape and variables

Entities, one row a unit. Key `entity_id` `ercot_cdr_unit:<unit code, else interconnection request number, else the
unit's name>:<fuel>`. A unit ERCOT lists twice with every field the same is kept once; two different rows under one key
would both be left out and counted in the header (none were). A heading the connector does not know stops the run.

Columns:

- `entity_type` `generator`; `name` ERCOT's unit name; `geo` `US-TX`; `lat`, `lon` and `operator` empty (the sheet does
  not give them).
- `capacity_mw`: the installed capacity, MW.
- `status`: `operating`, `planned` or `suspended`, mapped from ERCOT's CDR status code by its first part: OPER and RMR to
  operating, PLAN to planned, MOTH and EXT to suspended. ERCOT's own code is kept in `x_cdr_status`. A code not in the
  map stops the run.
- `status_date`: the in-service date, as ERCOT gives it.
- `source`, `source_url`, `retrieved_at` (the workbook's retrieval), `vintage` (the report's posting date).
- `x_unit_code`: ERCOT's unit code. `x_inr`: the interconnection request number (INR), where ERCOT gives one.
- `x_technology`, `x_fuel`, `x_cdr_status`, `x_attribute` (ERCOT's CDR resource attribute), `x_county`, `x_zone`: as
  ERCOT prints them.
- 20 seasonal capability columns, MW, the capability ERCOT lists for each unit at each season's start:
  `x_summer_2026` to `x_summer_2030`, `x_winter_2026_2027` to `x_winter_2030_2031`, `x_spring_2026` to `x_spring_2030`,
  `x_fall_2026` to `x_fall_2030`. No cell is empty.

When written: 1,772 units, every key unique; 1,460 with a unit code and 312 keyed by their INR (all planned). 503
give an INR (312 planned, 191 operating).
Status: operating 1,442, planned 313, suspended 17. ERCOT's codes: OPER 1,256, PLAN 295, OPER-SYN 169, PLAN-SLF 17,
MOTH-IND 11, OPER-SYN-SLF 6, OPER-UNFC 4, EXT-OUT 3, OPER-SLF 3, MOTH-SEA 3, OPER-UNR 3, PLAN-RPR 1, RMR 1.
Technology: PV 441, BA 413, WT 403, CC 202, GT 172, ST 74, IC 37, HY 26, MWH 4. Fuel: GAS 435, STORAGE 413, WIND-O 316,
SOLAR-O 303, SOLAR-W 83, SOLAR-FW 55, WIND-C 46, WIND-P 41, HYDRO 26, COAL 21, DIESEL 18, BIOMASS 7, NUCLEAR 4, MWH 4.
Zone: WEST 495, NORTH 442, SOUTH 408, COASTAL 175, HOUSTON 166, PANHANDLE 85, none 1. 184 county names (one of them
ERCOT's "HILL & LIMESTONE"); the header's count of 185 includes the one unit with no county. Installed capacity
233,872.23 MW: operating 171,187.99, planned 60,615.99, suspended 2,068.25. In-service dates 1928-01-01 to 2029-07-01;
5 units give none (the four DC ties, technology and fuel MWH, attribute DC-TIE, and the planned group row below).

## License

Public: ERCOT's terms (record 2 of the license reads, `docs/licenses.md`) let raw data from public portions of the site be
used, reproduced and redistributed in compilations, charts and analyses. Verdict in `docs/licenses.md`: public. Cite
"ERCOT, Capacity, Demand and Reserves Report".

## Cross-check (session 872)

- Every county is a Texas county of `utility_service_territories`, except ERCOT's "HILL & LIMESTONE", which names the
  line between two counties (the four Aquilla Lake wind rows).
- A node's county, by station prefix (the part of a node's name before its first "_"): 65 percent of the 888 nodes of
  `node_basis_daily` and 78 percent of the 339 storage resources of `ercot_dam_esr_awards` find a CDR unit. This match is
  a cross-check only. No node is given a county in any table.

## What it does not hold

- ERCOT's resource lists posted under `/misapp` and `/misdownload`, which the robots file keeps from the ERW.
- A unit's wires utility (TSP): the CDR does not name it. "A node's wires utility" stays open.
- Coordinates and owners or operators: the sheet does not give them.
- A link from a unit to an ERCOT settlement point or node.
- The capacity the Seasonal Summary counts toward the reserve margin: summed, `x_summer_2026` is 170,770.3 MW, while the
  summary counts 104,850 MW for summer 2026 at ERCOT's ELCCs for wind, solar and storage (`ercot_cdr_reserve_margins`).
- One planned row, "SMALL GENERATORS WITH SIGNED IAs AND 'MODEL READY DATES' PENDING", names a group of small
  generators rather than one unit; it has no county, zone or in-service date.
- Only the newest edition: earlier CDR reports are not kept.
