# The UK's installed capacity by connection, 2011 to 2025 (DESNZ's DUKES 5.12)

Energy Research Warehouse (ERW), method note written in session 2745 (chain 138) for a table first written on 25 October 2026 (session 2742).

Tables: `desnz_uk_capacity_by_connection_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Digest of UK Energy Statistics (DUKES) 2026, chapter 5 (`https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes`). The table reads the workbook "Plant installed capacity, by connection - United Kingdom (DUKES 5.12)", `https://assets.publishing.service.gov.uk/media/6a6a3668862aaf18d9c629ed/DUKES_5.12.xlsx`, its sheet "5.12", three tables one above another. No key. Source id `desnz:dukes_5_12_capacity_by_connection`. Connector: `warehouse/connectors/desnz_dukes_connection.py` (session 2742), whose raw store is `warehouse/raw/desnz_dukes/`. www.gov.uk's robots file closes only print and search paths (read 1478); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T205604Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T20:54:18Z, DUKES 2026's edition. DESNZ's note 7: pumped storage was revised up from earlier editions.

## Shape and variables

Series, 1,245 rows, 83 entities, each year from 2011 to 2025, at 31 December (note 2). `entity` `desnz_conn:<area>:<network>:<fuel>`:
- `area`: gb (5.12.A), ni (5.12.B) or uk (5.12.C);
- `network`: transmission, distribution, or all (the UK table only);
- `fuel`: the row as a slug, `total` for each network's total.

`variable` installed_capacity; `unit` MW; `ts_utc` the year's first day; `freq` P1Y; `geo` GB or GB-NIR; `node` the sheet's labels. These are installed capacities where known, else grid export capacity (note 1), not the de-rated capacity of `desnz_uk_derated_capacity_annual`.

**Figures:**
- The UK's transmission-connected capacity fell from 80,890 MW in 2011 to 68,667 in 2025, while distribution-connected capacity rose from 15,041 to 42,437 MW.
- Distribution held 21,331 of the UK's 21,915 MW of solar in 2025.
- The UK's total was 95,931 MW in 2011 and 111,103 in 2025.

## Reading the source

- The run stops at once, asking nothing, while `desnz_dukes` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **DESNZ's notes:**
  - coal includes mixed fuel and co-firing coal stations (note 4);
  - OCGT oil capacity is under oil (note 5);
  - other fuels are municipal solid waste for the major power producers, and coke oven gas, blast furnace gas and chemical waste for other generators (note 6).
- Each table is found by its title and its year row (each year from 2011 in turn). A blank network label carries the one above: the UK table's wave and tidal row has none. A network not in the map, or a row given twice, stops the run.
- A blank cell has no row; a zero stays a zero.
- **Checks,** within 0.5 MW, all passing:
  - each area's and network's fuels add to its total;
  - Great Britain and Northern Ireland add to the UK, network by network and fuel by fuel;
  - the UK's transmission and distribution add to its all.
- Nothing is filled.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

Against `desnz_uk_renewables_quarterly` (Energy Trends 6.1, the end of 2025), the UK's installed capacity, MW:

| | DUKES 5.12 (here) | Energy Trends 6.1 |
|---|---|---|
| Solar | 21,914.94 | 21,914.97 |
| Onshore wind | 16,430.23 | 16,430.69 |
| Offshore wind | 16,649.88 | 16,649.68 |
