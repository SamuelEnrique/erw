# Population-weighted heating and cooling degree days, a day (NOAA's Climate Prediction Center)

Energy Research Warehouse (ERW), method note written in session 2009 (chain 056) for a table first written on 23 October 2026.

Tables: `noaa_cpc_degree_days_daily`

## Publisher and address

NOAA, National Weather Service, Climate Prediction Center (CPC), Degree Days Statistics: `https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/<YEAR>/StatesCONUS.Heating.txt` (and `.Cooling.txt`), and `.../<YEAR>/Population.Heating.txt` (and `.Cooling.txt`). Connector: `warehouse/connectors/noaa_cpc_degree_days.py` (session 2006). The host has no robots file (HTTP 404).

## Vintage and revision

2024, 2025 and 2026 to 21 October (the files of 23 October 2026, 08:07 UTC). The current year's files grow each day and are fetched again on each run; earlier years' are kept. Ceiling four requests a year.

## Shape and variables

Series, 118,900 rows, 58 regions, 116 series. `entity` `cpc_dd:<state>` for the 48 contiguous states (StatesCONUS: 98,400 rows), `cpc_dd:division_<n>` for the nine census divisions as CPC's Population files number them (1 to 9), and `cpc_dd:conus` (Population: 20,500 rows); variables hdd and cdd (59,450 rows each); `unit` degF-day (degree days at 65 F, weighted by population as CPC computes them); `ts_utc` the day CPC labels; `freq` P1D; `geo` US-<state>, US for CONUS, empty for a division; `x_regions` StatesCONUS or Population.

## Reading the files

- Each file's first three lines must name the product ("Daily Heating Degree Days" or "Daily Cooling Degree Days"), the region set ("CPC::Regions::StatesCONUS", or "CPC::Regions::CensusDivisions" in the Population files) and the weights ("Population"); the fourth is "Region|YYYYMMDD|...".
- A region twice, a date not YYYYMMDD, a value not a whole number of at least zero, a state not in the map, or an (entity, variable, ts_utc) given twice stops the run. An empty cell has no row. Nothing is filled.
- The division numbers are written as the files write them; the files do not name the divisions, and none is named here.

## License

Public: the National Weather Service's pages (read 8 of `license_reads.csv`): "in the public domain, unless specifically noted otherwise". CPC is part of the NWS's National Centers for Environmental Prediction.

## Cross-checks (sessions 2006 and 2009)

- Against the ERW's own grid weather (`noaa_grid_weather_daily`, 2025, the grid's stations against the state's population weights): ERCOT and Texas, heating 1,590 and 1,624 (daily correlation 0.990), cooling 3,619 and 2,926 (0.980); CAISO and California, heating 1,739 and 2,355 (0.930), cooling 746 and 753 (0.840); NYISO and New York, heating 4,956 and 5,989 (0.989), cooling 1,220 and 638 (0.943). The days move together; the totals differ by weighting (a grid's stations against a state's people).
- The contiguous states' population-weighted totals for 2025: 4,175 heating and 1,326 cooling degree days.
- Session 2009, against the code: `SETS`, `REGION_SETS` and `KINDS` are as above; the counts computed from the rows.

## What it does not hold

- Years before 2024 (CPC's daily files run from 1981), the climate divisions, the fuel-weighted heating degree days (utility gas, electricity and the rest), and CPC's normals.
