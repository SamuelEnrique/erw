# The UK's electricity storage a year, 1996 to 2025 (DESNZ's DUKES 5.16)

Energy Research Warehouse (ERW), method note written in session 2717 (chain 136) for a table first written on 25 October 2026 (session 2720).

Tables: `desnz_uk_storage_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Digest of UK Energy Statistics (DUKES) 2026, chapter 5 (`https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes`). The table reads the workbook "Energy storage overview (DUKES 5.16)", `https://assets.publishing.service.gov.uk/media/6a6a36a0bf4a7aca8f8976c6/DUKES_5.16.xlsx`, its sheet "5.16", which holds three tables one above another. No key. Source id `desnz:dukes_5_16_energy_storage`. Connector: `warehouse/connectors/desnz_dukes_storage.py` (session 2720), whose raw store is `warehouse/raw/desnz_dukes/`. www.gov.uk's robots file closes only print and search paths (read 1449); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T182559Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T17:17:29Z (last modified 2026-07-29T17:21:36Z), DUKES 2026's edition.

## Shape and variables

Series, 360 rows, four entities, each year from 1996 to 2025. `entity` `desnz_st:<type>`:
- `pumped_storage`;
- `battery_grid_scale`: grid-scale only, as DESNZ's note 2 leaves out batteries behind the meter in homes and businesses;
- `other_storage`;
- `total`.

`variable`:
- `output`, electricity out of storage (table 5.16.A), MWh (GWh times 1,000);
- `input`, electricity into storage (5.16.B), MWh;
- `power_capacity`, the rate at which the sites may supply their stored energy (5.16.C, DESNZ's note 1), MW.

`ts_utc` the year's first day; `freq` P1Y; `geo` GB; `node` the table and the type.

**Figures:**
- Grid-scale battery power capacity was 1,097 MW in 2020, 3,820 in 2023, 5,210 in 2024 and 7,512 in 2025. It passed pumped storage's 2,744 MW in 2023.
- In 2025:
  - batteries discharged 2,274 GWh against 2,688 GWh charged, about 85 per cent;
  - pumped storage gave 1,437 GWh for 1,767 GWh, about 81 per cent.
- Other storage is zero in every year.

## Reading the source

- The run stops at once, asking nothing, while `desnz_dukes` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- Each table is found by its title, its year row (each year from 1996 in turn) and its four type rows in order. The sheet's note marks are read off.
- A blank cell has no row; a zero stays a zero, as DESNZ writes it.
- **Checks:** the three types add to the total in each table and year, within 0.01.
- A title, year or type not in this form, or a value not a number, stops the run. Nothing is filled.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

Against `desnz_uk_power_stations` (session 2714), pumped hydro:
- 2,900 MW there, the installed capacity of its stations at the end of May 2026;
- 2,744 MW of power capacity here, every year since 2007.

DESNZ states storage's power capacity on another basis than installed capacity.
