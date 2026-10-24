# Session 2418 report: Statistics Canada's installed generating capacity by type and class of producer, 2006 to 2025 (the third own choice); Hydro-Québec not taken

24 October 2026, from 11:01 UTC, on lab-desktop (the data machine), the thirteenth session of `queue/done/114-day-15-november-data-paraguay-panama-guatemala-namibia.md`, unattended. It ran before sessions 2415 to 2417, so that 2415's notes cover all three own choices. Precheck passed (`runs/c114/pre2418.out`). Model spend USD 0. Pulls: 3 of 20 (below).

## Read these first

- **Hydro-Québec's open data not taken:** `donnees.hydroquebec.com`'s robots file disallows `/api/` and every download path for every agent but Googlebot (read 693). Its demand and production data, which bear on New England's and New York's imports, are therefore closed to the reader.
- **The choice:** Statistics Canada's table 25-10-0022-01, installed plants and annual generating capacity by type of electricity generation. The ERW holds StatCan's generation (`statcan_electricity_generation_monthly`), trade and energy balance, but not its capacity. No chain has taken it.
- **One public table:** `statcan_generating_capacity_annual`, 5,952 rows, 55 series, 2006 to 2025. It is written, validated, archived, in coverage (sector power), held from the live set, and listed in the release's held tables:
  - by area (Canada, the provinces and territories), class of producer (all, public utilities, private utilities, industries) and type (total, hydro, wind, tidal, solar, geothermal, other non-combustibles, total thermal and its four kinds);
  - in MW (StatCan's kilowatts divided by 1,000);
  - each class's types add to its total, and the thermal kinds to total thermal, in all 1,915 cells compared;
  - 703 figures marked .. (not available) have no row.
- **License: public** (the Statistics Canada Open Licence, the record's verdict). The robots file asks a crawl delay of 2 seconds, kept, and disallows paths ending `.csv`, not the `/n1/tbl/csv/` zip (read 694).

## The cross-check (`runs/c114/s2418/cross.py`, `cross.out`; tables read past their header lines)

- **Capacity against `statcan_electricity_generation_monthly`'s generation, Canada, all producers** (each year's twelve months over the capacity times the year's hours):

| Type | 2019 | 2022 | 2024 |
|---|---|---|---|
| Hydro | 0.530 (81,400 MW, 377.6 TWh) | 0.540 | 0.469 (83,022 MW, 341.8 TWh) |
| Nuclear | 0.773 (14,101 MW, 95.5 TWh) | 0.648 | 0.719 |
| Wind | 0.288 | 0.288 | 0.294 (17,738 MW, 45.8 TWh) |
| Solar | 0.198 | 0.114 | 0.113 (5,288 MW, 5.2 TWh) |
| Total | 0.502 (145,538 MW, 640.4 TWh) | 0.482 | 0.445 (155,749 MW, 609.5 TWh) |

- The factors fall within the usual ranges for each type. Solar's 0.198 in 2019 is above its later values; this report does not explain it.
- 2024's hydro is the lowest of the three years (341.8 TWh).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| donnees.hydroquebec.com | 1 | robots |
| www150.statcan.gc.ca | 2 | robots, the table's zip (93,501 bytes); 2 s apart |
| total | 3 of 20 | |

## Errors

- **The cross-check's first run failed** on an index (a fault in the script), and was fixed.

## Decisions made without you

- **StatCan's capacity** as the third own choice, beside the ERW's StatCan generation and trade tables.
- **This session run before sessions 2415 to 2417,** so that the notes, the Stanford draft and the records take its table.

## For Samuel's ruling

- None.

## Files

- New:
  - `warehouse/connectors/statcan_generating_capacity.py`
  - `tests/test_session2418.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`
  - `warehouse/metadata/license_reads.csv` (693 to 695), `license_tables.csv`, `docs/licenses.md`
  - the coverage, sources and archive manifest files, and the release README's held line and lists
- On the data machine only: `runs/c114/s2418/`, `runs/license_reads/s2418/`.
