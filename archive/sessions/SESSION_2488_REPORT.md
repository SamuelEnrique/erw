# Session 2488 report: a third source of the session's own choosing, not taken (Statistics Canada 25-10-0017-01 holds fuel quantities only, in units the standard lacks)

24 October 2026, about 13:45 UTC, on lab-desktop (the data machine), chain 120, unattended. Precheck passed (`runs/c120/pre2488.out`). Model spend USD 0. Pulls: 2 requests of 20 (the robots file, and one fetch).

## Read these first

- **The aim:** the years before 2020 of session 2482's fuel table. Statistics Canada's 25-10-0017-01, "Electric power generation, annual fuel consumed by electric utility thermal plants, inactive" (archived, no longer updated), covers 2005 to 2021 by province and fuel. No chain holds it (main and chains 118's and 119's branches searched).
- **www150.statcan.gc.ca's robots file**, asked in this session's own call, disallows paths ending in `.csv` and names no AI agent (read 823).
- **Not taken.** The table holds only the fuel consumed, in cubic metres, kilolitres, metric tonnes and kilograms, with no electricity generated. None of those units is in the data standard. A new unit needs a Decision agreed with the chains beside this one, more than a session's own choice should add. The zip is kept in `warehouse/raw/statcan_thermal_fuel_history/` for a later session.

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www150.statcan.gc.ca/robots.txt | 200: `.csv` closed |
| 2 | 25100017-eng.zip (the fetch) | 200, 26,436 bytes, last modified 23 January 2024; 3,084 rows of fuel quantities |

Reads recorded: 823 (on this branch).

## Decisions made without you

- **No new unit added** for an archived table of fuel quantities.

## For Samuel's ruling

- None.

## Files

- New: this report. Changed: `warehouse/metadata/license_reads.csv` (read 823). On the data machine only: `runs/c120/s2488/`, `warehouse/raw/statcan_thermal_fuel_history/`.
