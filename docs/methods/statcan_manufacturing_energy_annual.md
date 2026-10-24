# Canada's manufacturing industries' energy use by fuel, a year (Statistics Canada, table 25-10-0025-01)

Energy Research Warehouse (ERW), method note written in session 2485 (chain 120) for a table first written on 24 October 2026 (session 2483).

Tables: `statcan_manufacturing_energy_annual`

## Publisher and address

Statistics Canada, table 25-10-0025-01, "Manufacturing industries, total annual energy fuel consumption in gigajoules, 31-33" (`https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002501`), read as the table's full CSV download, a zip: `https://www150.statcan.gc.ca/n1/tbl/csv/25100025-eng.zip`. Source id `statcan:25-10-0025-01`. Connector: `warehouse/connectors/statcan_manufacturing_energy.py` (session 2483). The host's robots file disallows paths ending in `.csv` for every agent, not a `.zip`, and names no AI agent (read 822).

## Vintage and revision

1995 to 2024, written by run `20261024T133902Z` (the write under the lock, offline), which read the zip saved at 2026-10-24T13:37:40Z (`retrieved_at`). `vintage` is the zip's last-modified time, 2025-10-29T12:30:22Z. Every run that is not `--offline` asks again and writes the table again (`write_snapshot`).

## Shape and variables

Series, 15,326 rows, 103 industries, 15 fuels, Canada only.

- `entity`: `statcan_mfg:ca:<NAICS code>`, the code in StatCan's brackets (`31-33` for all manufacturing, `3364` for aerospace, `31212` for breweries), or a slug of the name where it has none.
- `variable`: `consumption_<fuel>`.
  - Fuels: electricity, natural gas, heavy fuel oil, middle distillates, propane, butane, coal, coal coke, coke oven gas, petroleum coke, refinery fuel gas, spent pulping liquor, steam and wood.
  - Their total: `consumption_total_energy_consumed_as_fuel_higher_heating_value`.
- `unit` MWh: StatCan's gigajoules divided by 3.6, every fuel in one unit of energy.
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` CA.
- `x_naics` and `x_fuel`: StatCan's names. `x_quality`: StatCan's grade, A (excellent) to E (use with caution), or blank. `x_vector`.

2,330 values are 0; none is negative. Industries nest (all manufacturing, subsectors, groups): a sum takes one level. All manufacturing's electricity, TWh: 173.5 (1995), 201.3 (2005), 166.0 (2015), 172.4 (2024).

## Reading the source

- The run stops, asking nothing, while `statcan_manufacturing_energy` or the host is paused.
- One request a run (timeout 180 seconds, 2 seconds' pause); `--offline` reads the saved zip. Its raw files are in `warehouse/raw/statcan_manufacturing_energy/`: the folder was renamed from the fetch's working name, its manifest unchanged (session 2483).
- **Figures with no row,** each counted in the header:
  - ".." (not available, 272);
  - "x" (suppressed to meet the Statistics Act's confidentiality, 4,219);
  - "F" (too unreliable to be published, 977).
- The run stops, and no file is written, for any of these:
  - a zip that does not hold 25100025.csv alone;
  - a unit other than gigajoules, or a scalar factor other than units;
  - an area other than Canada;
  - a status not in the map;
  - a year that does not read;
  - a key given twice.

Nothing is filled.

## License

Public: the Statistics Canada Open Licence, StatCan's verdict on record in `license_verdicts.csv`. The header names the source and says the table does not constitute an endorsement by Statistics Canada.

## Cross-checks (session 2483)

- All manufacturing's electricity over `statcan_power_disposition_annual`'s sales to mining and manufacturing: 1.013 to 1.204, 2005 to 2024.
- Manufacturing's use exceeds the utilities' sales by industry's own generation, which the sales leave out. Mining, in the sales but not the use, works the other way, so the ratio is a bound, not an identity.

## What it does not hold

- Provinces; the industries' costs; years after 2024.
