# Canada's electricity generation by province, class of producer and type, a month, January 2008 to July 2026 (Statistics Canada, table 25-10-0015-01)

Energy Research Warehouse (ERW), method note written in session 2185 (chain 097) for a table first written on 24 October 2026 (session 2176).

Tables: `statcan_electricity_generation_monthly`

## Publisher and address

Statistics Canada (StatCan), table 25-10-0015-01, "Electric power generation, monthly generation by type of electricity" (`https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001501`), read from the table's full CSV download, one zip holding `25100015.csv` and its metadata file:

`https://www150.statcan.gc.ca/n1/tbl/csv/25100015-eng.zip`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `statcan:25-10-0015-01`. Connector: `warehouse/connectors/statcan_electricity.py` (session 2176), its only table. www150.statcan.gc.ca's robots file (read 359) asks a crawl delay of 2 seconds and disallows its framework, error and some subject paths and files ending .csv, .xls and the like, not /n1/ or /t1/; www.statcan.gc.ca's (read 360) has the same rules.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `warehouse/scheduled.py`, `scripts/` or `.github/workflows/` names the connector (searched in session 2185), and `run_status.csv` holds no row for it. It was written once, by run `20261024T005122Z` on the data machine.

## Vintage and revision

January 2008 to July 2026 (`ts_utc`), 223 months. The zip was retrieved at 2026-10-24T00:49:55Z by the session's probe, and the write run read that copy (`retrieved_at` in every row). Its Last-Modified time, 2026-09-29T12:30:43Z, is every row's `vintage`. `coverage.csv` gives the same 58,361 rows, 458 nodes and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`), and the zip is asked again unless `--offline`, since StatCan revises the table at the same address. 698 rows carry StatCan's revision mark (`x_revised` r), all in months from December 2013 to November 2015.

## Shape and variables

Series, 58,361 rows, 458 series, one variable. `entity` `statcan_gen:<area>:<class>:<type>`: the area is `ca` or the province's or territory's postal code in lower case (14 areas: Canada, the ten provinces and the three territories); the class is `all` (158 series), `utilities` (158) or `industries` (142); the type is StatCan's type of generation as a slug. `variable` `generation`; `unit` MWh; `freq` P1M; `ts_utc` the month's first day at 00:00 UTC; `geo` CA or CA-<province>; `market` empty; `node` the area, class and type in StatCan's words ("Ontario: Total all classes of electricity producer: Hydraulic turbine"); `x_class`; `x_type`; `x_total` yes (35,051 rows, 270 series) where the class or the type is one of StatCan's totals, never to be summed with its parts; `x_vector` StatCan's vector id (one a series); `x_revised` r or blank.

| `x_type` | Series | Rows | First | Last |
|---|---|---|---|---|
| total_all_types_of_electricity_generation (total) | 42 | 8,989 | Jan 2008 | Jul 2026 |
| hydraulic_turbine | 40 | 7,405 | Jan 2008 | Jul 2026 |
| wind_power_turbine | 42 | 7,217 | Jan 2008 | Jul 2026 |
| solar | 42 | 5,435 | Jan 2010 | Jul 2026 |
| total_electricity_production_from_combustible_fuels (total) | 42 | 5,167 | Jan 2016 | Jul 2026 |
| other_types_of_electricity_generation | 35 | 4,507 | Aug 2012 | Jul 2026 |
| total_electricity_production_from_biomass (total) | 42 | 3,257 | Jan 2020 | Jul 2026 |
| total_electricity_production_from_non_renewable_combustible_fuels (total) | 42 | 3,257 | Jan 2020 | Jul 2026 |
| internal_combustion_turbine | 37 | 3,124 | Jan 2008 | Dec 2015 |
| conventional_steam_turbine | 34 | 3,006 | Jan 2008 | Dec 2015 |
| combustion_turbine | 34 | 2,855 | Jan 2008 | Dec 2015 |
| tidal_power_turbine | 18 | 2,660 | Jan 2008 | Jul 2026 |
| nuclear_steam_turbine | 8 | 1,482 | Jan 2008 | Jul 2026 |

StatCan changed its types of generation at the start of 2016. The three combustion types (conventional steam, combustion turbine, internal combustion) end in December 2015. From January 2016 combustion is given only as a total ("Total electricity production from combustible fuels"), and from January 2020 also as two totals within it, biomass and non-renewable combustible fuels. A sum of the rows that are not totals therefore leaves out all combustion from 2016 on. The last row of 112 series is earlier than July 2026 (85 of them in December 2015); 91 series hold all 223 months; 346 series reach July 2026.

652 values are negative and 12,658 are zero, as StatCan prints them; 651 of the negative values fall in 2008 to 2015 (combustion turbine 213, conventional steam 166, nuclear 154, internal combustion 70, tidal 48) and one in 2024 (solar). Figures StatCan marks ".." (not available, 17,843) or "x" (suppressed for confidentiality, 114) have no row, as the header counts them. Canada's total for all classes and types in 2025 is 625.2 TWh over 12 months. No (entity, variable, ts_utc) is given twice. The counts were computed in session 2185 from the rows, read past the 10 header lines with pandas (every column as text).

## Checks the connector makes

- Before any request, the connector and www150.statcan.gc.ca are checked against `warehouse/metadata/paused_sources.csv`; a paused publisher stops the run with no request. It is not paused.
- The zip must hold `25100015.csv` as its only data file (beside the metadata file), or the run stops.
- Each line must give the unit "Megawatt hours" and the scalar factor "units", an area in the map of 14 names, a class in the map of three, and a month in the form YYYY-MM, or the run stops. A status other than blank, "..", "x" or "F" stops it, and so does a key (entity and month) given twice or a file with no row.
- A figure marked "..", "x" or "F" has no row and is counted (no "F" in this run). Nothing is filled.
- Ceiling: one request a run, with a pause of 2 seconds after it, as the robots file asks.

## The cross-check

Session 2176 set the yearly totals (class all, type total_all_types_of_electricity_generation, years of 12 months) against two other ERW tables in `runs/c097/s2176/cross.py` (on the data machine, not in git), reading the trial copy of the table, which holds the same 58,361 rows:

- Ontario in 2025: StatCan's generation 169.7 TWh against IESO's Ontario demand 145.6 TWh (`ieso_ontario_demand_hourly`, `ontario_demand` summed over the local year), as Ontario's net exports and losses would make it.
- The CER's exports to the U.S. (`cer_electricity_trade`) as a share of a province's generation, the eight highest: New Brunswick 0.350 in 2023; Manitoba 0.280 (2020), 0.276 (2013 and 2022), 0.271 (2010), 0.269 (2011), 0.268 (2017) and 0.267 (2016).
- Canada's yearly generation runs from 566.8 TWh (2010) to 649.4 TWh (2017); 2025 is 625.2 TWh.

## License

The header: "License: may be public (the Statistics Canada Open Licence; see license_verdicts.csv). Source: Statistics Canada, Table 25-10-0015-01. This does not constitute an endorsement by Statistics Canada of this product." `license_verdicts.csv` gives Statistics Canada "may be public", the same if the ERW sells anything (read 361, the Open Licence, read in session 2176 and recorded in session 2181): "Statistics Canada grants you a worldwide, royalty-free, non-exclusive licence to: use, reproduce, publish, freely distribute, or sell the Information". A value-added product carries a source line and the statement that StatCan does not endorse it; the header carries both. `coverage.csv`: public.

## Found while writing this note

- The docstring and the header say a figure marked ".." or "x" has no row. The code also passes over a figure marked "F" and counts it. No "F" was met in this run.
- The docstring says "an area or label not in the maps" stops the run. The code maps areas and classes only; a type of generation it has not met becomes a new slug and a new series without stopping the run.
- The docstring says the robots file "disallows its framework and error paths, not /n1/". Read 359 also records files ending .csv, .xls and the like as disallowed. The zip the connector asks is not such a file.
- From January 2016 the combustion types are given only as totals (above), so a sum of the parts misses combustion; neither the docstring nor the header says so.

Acted on in session 2185: the docstring now names "F", says a class of producer (not a label) outside the maps stops the run and a new type becomes a new series, records the robots file's file-ending rules and says the parts leave combustion out from 2016; the header's license line reads public, as the oil and gas table's does. The table was written again (the same rows).

## What it does not hold

- Combustion by kind of turbine after December 2015, or by fuel before January 2020 (StatCan's table changed).
- Capacity, consumption, trade or prices: generation in MWh only.
- Months before January 2008 (StatCan's earlier tables are not read).
- Figures StatCan withholds (".." and "x"), which have no row.
