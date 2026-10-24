# Canada's annual electricity generation by class of producer and type (Statistics Canada, table 25-10-0020-01)

Energy Research Warehouse (ERW), method note written in session 2443 (chain 117) for a table first written on 24 October 2026 (session 2440).

Tables: `statcan_generation_class_annual`

## Publisher and address

Statistics Canada, table 25-10-0020-01, "Electric power, annual generation by class of producer" (`https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002001`), read as the table's full CSV download, a zip: `https://www150.statcan.gc.ca/n1/tbl/csv/25100020-eng.zip`. Source id `statcan:25-10-0020-01`. Connector: `warehouse/connectors/statcan_generation_class.py` (session 2440). The host's robots file disallows paths ending in `.csv` for every agent, not a `.zip`, and names no AI agent (read 806).

## Vintage and revision

2005 to 2025, written by run `20261024T114034Z` (the write under the lock, offline), which read the zip saved at 2026-10-24T11:38:34Z (`retrieved_at`). `vintage` is the zip's last-modified time, 2026-10-16T12:30:33Z. StatCan revises figures at the same address; 97 rows carry its revision mark, kept in `x_revised` (`r`). Every run that is not `--offline` asks again and writes the table again (`write_snapshot`).

## Shape and variables

Series, 5,937 rows, 42 entities (14 areas, three classes).

- `entity`: `statcan_gc:<area>:<class>`.
  - area: `ca`, or a province's or territory's postal code in lower case;
  - class: `all` ("Total all classes of electricity producer"), `utilities` or `industries`.
- `variable`: StatCan's type of generation as a slug, 14 of them. The totals are `total_all_types_of_electricity_generation`, `total_thermal_generation`, `total_electricity_production_from_combustible_fuels` and `total_hydro_tidal_wind_solar_and_other_generation`. The parts are hydraulic, wind, solar, tidal, geothermal, nuclear steam, conventional steam, combustion and internal combustion turbines, and other.
- `unit` MWh, as StatCan gives it. `ts_utc` the year's 1 January; `freq` P1Y; `geo` CA or CA-<province>.
- `node`: the area, class and type as StatCan names them; `x_class`, `x_type` StatCan's names; `x_vector` its vector.

395 values are 0. 18 are negative, all net generation of combustion turbines (Prince Edward Island 12, Newfoundland and Labrador 3) and of internal combustion turbines (New Brunswick 3): units whose own use exceeded their output, as StatCan gives them. Classes and types overlap: `all` holds `utilities` and `industries`, and the totals of type hold their parts. A sum takes one level. Canada's total generation, TWh: 2005 604.4, 2015 640.3, 2020 636.6, 2025 639.5.

## Reading the source

- The run stops, asking nothing, while `statcan_generation_class` or the host is paused.
- One request a run (timeout 180 seconds, 2 seconds' pause); `--offline` reads the saved zip.
- A figure StatCan marks ".." (not available, 1,316) or "x" (suppressed to meet the Statistics Act's confidentiality, 10) has no row and is counted in the header. Nothing is filled.
- The run stops, and no file is written, for any of these:
  - a zip that does not hold 25100020.csv alone;
  - a unit other than megawatt hours, or a scalar factor other than units;
  - an area, class or status not in the map;
  - a year that does not read;
  - a key given twice.

## License

Public: the Statistics Canada Open Licence, StatCan's verdict on record in `license_verdicts.csv`. The header names the source and says the table does not constitute an endorsement by Statistics Canada.

## Cross-checks (session 2440)

- For Canada, utilities plus industries equal all classes in every year.
- Canada's total over the twelve-month sums of `statcan_electricity_generation_monthly` (25-10-0015-01): 0.992 to 1.023 from 2016, and 1.028 to 1.080 from 2008 to 2015. Before 2016 the monthly survey covered fewer producers.
- Over `owid_ember_electricity_annual`'s demand for Canada: 0.990 to 1.072, Canada being a net exporter.
- Equal to `statcan_power_disposition_annual`'s total generation in every year (session 2441).

## What it does not hold

- Years before 2005; months (25-10-0015-01 holds them); capacity (25-10-0022-01); the producers' names.
