# The UK's de-rated plant capacity, 1996 to 2025 (DESNZ's DUKES 5.7)

Energy Research Warehouse (ERW), method note written in session 2731 (chain 137) for a table first written on 25 October 2026 (session 2734).

Tables: `desnz_uk_derated_capacity_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Digest of UK Energy Statistics (DUKES) 2026, chapter 5 (`https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes`). The table reads the workbook "Plant capacity: United Kingdom (DUKES 5.7)", `https://assets.publishing.service.gov.uk/media/6a6a3622cceb23e8678976bf/DUKES_5.7.xlsx`, its sheet "5.7", two tables one above another. No key. Source id `desnz:dukes_5_7_plant_capacity`. Connector: `warehouse/connectors/desnz_dukes_capacity.py` (session 2734), whose raw store is `warehouse/raw/desnz_dukes/`. www.gov.uk's robots file closes only print and search paths (read 1466); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T194323Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T19:40:40Z (last modified 2026-07-29T17:19:30Z), DUKES 2026's edition.

## Shape and variables

Series, 1,680 rows, 50 entities, each year from 1996 to 2025. `entity` `desnz_cap:<group>:<item>`:
- **Groups:**
  - `mpp`, the major power producers;
  - `other`, the other generators: autogenerators, domestic generation and smaller renewable generators;
  - `all`, all generating companies.
- **Items:** each row's fuel or technology as a slug (`gas_fired`, `nuclear_stations`, `onshore_wind`, `ccgt_stations`, ...). Each group's total is `total`; all companies' also have `total_renewables`, `total_low_carbon` and `total_fossil_fuels`. All companies' "Mixed or dual fuelled" is read as `mixed_or_dual_fired`, the other groups' name.

`variable` `derated_capacity` (table 5.7.A, capacity by fuel) or `thermal_capacity` (5.7.B, thermal stations by type); `unit` MW; `ts_utc` the year's first day; `freq` P1Y; `geo` GB; `node` the sheet's two labels.

**These are de-rated figures, not installed capacity:**
- Small-scale hydro, wind and solar are on a declared net capability basis, multiplied by 0.365, 0.43 and 0.17 for intermittency (DESNZ's note 4).
- Grid export capacity is used where known, else installed capacity (note 1).

They are not the installed capacity of `desnz_uk_power_stations`.

**Figures:**
- All companies' de-rated capacity was 73,270 MW in 1996, 90,393 in 2010 and 74,510 in 2025.
- Coal fell from 26,623 MW in 1996 to 0 in 2025; gas rose from 14,411 to 36,508 MW.
- De-rated renewables rose from 1,955 to 27,730 MW.

## Reading the source

- The run stops at once, asking nothing, while `desnz_dukes` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **DESNZ's notes:**
  - The other generators' data before 2006 are declared net capacity (note 6), and their falls in 2007, 2010 and 2012 are capacity re-classified to the major power producers (note 7).
  - Conventional steam stations leave out bioenergy and waste (note 8).
  - Renewables are wind, wave and tidal, solar, bioenergy and natural flow hydro, not pumped hydro (note 9).
  - Low carbon is renewables and nuclear (note 10).
  - Fossil fuels are coal, oil, gas, mixed or dual fired and other fossil fuels (note 11).
- Each table is found by its title and its year row; each row's two labels (note marks read off) are mapped to an entity. A group not in the map, or an item given twice, stops the run.
- A blank cell has no row; a zero stays a zero.
- **Checks,** within 0.5 MW in every year:
  - each group's parts add to its total;
  - the major power producers and the other generators add to all companies, item by item;
  - all companies' renewables, low carbon and fossil totals equal their parts, and fossil, low carbon and pumped hydro make the total.
- **DESNZ's sheet disagrees with itself in 2015 and 2016.** All companies' total and fossil fuels total are each 99 MW above their parts (79,539.65 MW against 79,440.65 in 2015), while every fuel row adds exactly. The four differences are named in the connector (`KNOWN`) and kept as published; any other difference stops the run.
- Nothing is filled.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

Against chain 136's DUKES tables, the major power producers in 2025:
- pumped hydro 2,744 MW here and in `desnz_uk_storage_annual`'s power capacity;
- nuclear 5,883 MW here and in `desnz_uk_power_stations` (May 2026);
- gas 33,616.9 MW here against the station list's 33,676 MW (export capacity against installed capacity).
