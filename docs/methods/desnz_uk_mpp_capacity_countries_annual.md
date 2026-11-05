# The major power producers' capacity by UK country, 1999 to 2025 (DESNZ's DUKES 5.8)

Energy Research Warehouse (ERW), method note written in session 2745 (chain 138) for a table first written on 25 October 2026 (session 2743).

Tables: `desnz_uk_mpp_capacity_countries_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Digest of UK Energy Statistics (DUKES) 2026, chapter 5 (`https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes`). The table reads the workbook "Major Power Producers Plant capacity: England and Wales, Scotland, and Northern Ireland (DUKES 5.8)", `https://assets.publishing.service.gov.uk/media/6a6a3631862aaf18d9c629ec/DUKES_5.8.xlsx`, its sheet "5.8", three tables one above another. No key. Source id `desnz:dukes_5_8_mpp_capacity_countries`. Connector: `warehouse/connectors/desnz_dukes_mpp_countries.py` (session 2743), whose raw store is `warehouse/raw/desnz_dukes/`. www.gov.uk's robots file closes only print and search paths (read 1479); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T210025Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T20:58:43Z, DUKES 2026's edition.

## Shape and variables

Series, 1,539 rows, 51 entities, each year from 1999 to 2025; DESNZ has no data for 1996 to 1998 (note 1), which the sheet keeps as "[x]". `entity` `desnz_mppr:<country>:<item>`, for england_wales, scotland and northern_ireland:
- `derated_capacity` (5.8.A, by fuel, MW), with `total`;
- `thermal_capacity` (5.8.C, by thermal plant type, MW), with `total_thermal`;
- `capacity_share` (5.8.B, the country's share of the major power producers' capacity), on `total`, as a ratio. The sheet's heading says per cent; its cells hold fractions such as 0.7977.

`ts_utc` the year's first day; `freq` P1Y; `geo` GB-ENG,GB-WLS, GB-SCT or GB-NIR; `node` the sheet's labels.

These are de-rated figures, as in DUKES 5.7:
- small-scale hydro, wind and solar are on a declared net capability basis, de-rated by 0.365, 0.43 and 0.17 (note 5);
- grid export capacity is used where known;
- figures before 2006 are declared net capacity (note 3).

**Figures:**
- In 2025: England and Wales 49,400 MW (a share of 0.798), Scotland 10,256 (0.166), Northern Ireland 2,276 (0.037).
- In 1999 Scotland's share was 0.139.

## Reading the source

- The run stops at once, asking nothing, while `desnz_dukes` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **DESNZ's notes:** major wind and solar companies are counted as major power producers from 2007 and 2015 (note 6); conventional steam stations leave out bioenergy (note 7).
- Each table is found by its title and its year row. A country not in the map, or an item given twice, stops the run.
- "[x]" and a blank cell have no row; a zero stays a zero.
- **Checks,** all passing:
  - each country's fuels add to its total and its plant types to its thermal total, within 0.5 MW;
  - the three shares add to 1, each equal to the country's total over the three, within 0.001.
- Nothing is filled.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

Against `desnz_uk_derated_capacity_annual` (DUKES 5.7, chain 137): the three countries' totals add exactly to its major power producers' total.

| Year | The three countries (MW) | DUKES 5.7 (MW) |
|---|---|---|
| 2015 | 70,321.67 | 70,321.67 |
| 2016 | 67,964.93 | 67,964.93 |
| 2025 | 61,931.21 | 61,931.21 |
