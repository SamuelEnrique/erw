# The UK's maximum load, plant load factors and thermal efficiency, 1996 to 2025 (DESNZ's DUKES 5.10)

Energy Research Warehouse (ERW), method note written in session 2731 (chain 137) for a table first written on 25 October 2026 (session 2728).

Tables: `desnz_uk_plant_loads_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Digest of UK Energy Statistics (DUKES) 2026, chapter 5 (`https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes`). The table reads the workbook "Plant loads, demand and efficiency (DUKES 5.10)", `https://assets.publishing.service.gov.uk/media/6a6a364b0ddb7e4831c629f2/DUKES_5.10.xlsx`, its sheets "5.10.A" and "5.10.B and 5.10.C". No key. Source id `desnz:dukes_5_10_plant_loads`. Connector: `warehouse/connectors/desnz_dukes_plant_loads.py` (session 2728), whose raw store is `warehouse/raw/desnz_dukes/`. www.gov.uk's robots file closes only print and search paths (read 1464); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T193019Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T19:27:58Z (last modified 2026-07-29T17:20:11Z), DUKES 2026's edition.

## Shape and variables

Series, 425 rows, 11 entities, each year from 1996 to 2025, all for the major power producers. `entity` `desnz_pl:<area or plant type>`:
- **`max_load`** (5.10.A, the simultaneous maximum load met, MW): the load met by the transmission network, net of demand met by embedded generation (DESNZ's note 2). It is given for `uk`, `great_britain` and `northern_ireland`, and for `england_wales` and `scotland` where given (six years).
- **On `uk`:**
  - `max_demand_share_of_capacity` (5.10.A, maximum demand as a percentage of the major power producers' capacity, pct);
  - `system_load_factor` (5.10.B, average electricity available as a percentage of maximum demand, note 9, pct).
- **`load_factor`** (5.10.B, pct) for `ccgt`, `nuclear`, `pumped_storage`, `conventional_thermal`, `coal` and `all_plant`.
- **`thermal_efficiency`** (5.10.C, electricity generated as a percentage of the fuel used, gross calorific value, pct) for `ccgt`, `coal` and `nuclear`.

`ts_utc` the first day of DESNZ's year; `freq` P1Y; `geo` GB, GB-SCT or GB-NIR; `node` the sheet's row.

**Figures:**
- The UK's maximum load was 56,815 MW in 1996, 60,893 in 2010, 48,945 in 2020, 47,361 in 2024 and 51,538 in 2025.
- CCGT's load factor fell from 71.2 per cent in 1996 to 29.7 in 2025, and its thermal efficiency rose from 45.3 to 48.0 per cent.
- Nuclear's load factor was 64.0 per cent in 2025. Coal's figures are zero in 2025.

## Reading the source

- The run stops at once, asking nothing, while `desnz_dukes` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **A maximum load's year runs to March of the next** (DESNZ's note 3: 2017 is the year ending March 2018), so a winter's peak falls in the year it starts.
- **Regional demands before 2008** (note 11): before 2005, Scotland's and Northern Ireland's are those at England and Wales's maximum; from 2005 to 2007, Northern Ireland's is that at Great Britain's.
- **Load factors:** conventional thermal and all plant use the major power producers' supply and capacity, revised back to 2010 (note 6). All plant includes wind from 2008, solar from 2015 and natural flow hydro, at capacity not de-rated (note 8).
- Each table is found by its title and its year row (each year from 1996 in turn). Each row label, with note marks read off, is matched exactly; a label not in the map stops the run.
- "[x]" and a blank cell have no row; a zero stays a zero.
- **Checks,** all passing:
  - England and Wales and Scotland add to Great Britain, and Great Britain and Northern Ireland to the total, within 1 MW;
  - every percentage lies in [0, 100].
- Nothing is filled.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

No other ERW table holds the UK's peak. A plausibility check against `elexon_gb_demand_daily` (Elexon's daily national demand), April to March: each year's GB maximum load sits 8,150 to 12,550 MW above that winter's highest daily mean.

| DESNZ's year | GB maximum load (MW) | Elexon's highest day | That day's mean (MW) |
|---|---|---|---|
| 2022 | 47,117 | 15 December 2022 | 37,488 |
| 2023 | 46,854 | 17 January 2024 | 36,917 |
| 2024 | 46,045 | 10 January 2025 | 37,888 |
| 2025 | 50,101 | 6 January 2026 | 37,550 |
