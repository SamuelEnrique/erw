# New Zealand's grid generation and demand a month, for the country and each island, January 2015 to September 2026 (Electricity Authority, EMI reports Generation trends W_GG_C and Demand trends W_GD_C)

Energy Research Warehouse (ERW), method note written in session 2261 (chain 102) for a table first written on 24 October 2026 (session 2254).

Tables: `emi_nz_generation_demand_monthly`

## Publisher and address

The Electricity Authority (New Zealand), its Electricity Market Information site (EMI, `https://www.emi.ea.govt.nz/Wholesale/Reports`), two reports in their CSV downloads, each for New Zealand and for its two islands, monthly from 1 January 2015 to the last day of the last month ended in New Zealand (`--to`; 30 September 2026 in this run):

- Generation trends: `https://www.emi.ea.govt.nz/Wholesale/Download/DataReport/CSV/W_GG_C?DateFrom=20150101&DateTo=<end>&RegionType=<NZ|ISLAND>&TimeScale=MONTH&Show=Gwh&_si=v|3`
- Demand trends: `https://www.emi.ea.govt.nz/Wholesale/Download/DataReport/CSV/W_GD_C?DateFrom=20150101&DateTo=<end>&RegionType=<NZ|ISLAND>&TimeScale=MONTH&_si=v|3`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `emi:generation_demand_trends`. Connector: `warehouse/connectors/emi_nz.py` (session 2254), its only table. www.emi.ea.govt.nz has no robots file (HTTP 404, read 443); www.ea.govt.nz's allows every path (read 449). The reports were found through EMI's Wholesale reports page and the Generation trends report's page (reads 446 and 447).

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2261), and `run_status.csv` holds no row for it. It was written once, by run `20261024T035846Z` on the data machine, offline from the session's probe copies.

## Vintage and revision

January 2015 to September 2026 (`ts_utc`), 141 months, none missing. The four CSVs were retrieved by session 2254's probe at 2026-10-24T03:54:31Z (generation, New Zealand), 03:55:34Z (generation, islands), 03:55:38Z (demand, New Zealand) and 03:55:42Z (demand, islands); each row's `retrieved_at` is its file's time as the probe's manifest records it. `vintage` is empty: EMI sends no Last-Modified. `coverage.csv` gives the same 846 rows, 3 nodes and the same first and last `ts_utc`.

EMI revises its figures. Each run writes the whole table again (`ip.write_snapshot`), and the four files are asked again unless `--offline`.

## Shape and variables

Series, 846 rows, 3 entities, 2 variables, 6 series, each of 141 months.

- `entity` `emi:nz` (New Zealand), `emi:ni` (North Island) or `emi:si` (South Island); `variable` `generation` (report W_GG_C) or `demand` (W_GD_C); `unit` MWh, EMI's GWh times 1,000 (every value a whole MWh, as EMI gives GWh to three decimals); `freq` P1M; `ts_utc` the month's first day at 00:00 UTC; `geo` NZ for all three; `market` empty; `node` EMI's region name; `x_region_id` EMI's id (NZ, NI, SI); `x_report` the report's code.

| Entity | Variable | Lowest month, GWh | Highest month, GWh | Mean, GWh |
|---|---|---|---|---|
| emi:nz | generation | 2,929.7 | 4,136.6 | 3,564.2 |
| emi:nz | demand | 2,834.6 | 3,993.6 | 3,447.7 |
| emi:ni | generation | 1,541.3 | 2,785.1 | 2,016.5 |
| emi:ni | demand | 1,723.8 | 2,563.0 | 2,160.5 |
| emi:si | generation | 1,182.2 | 1,999.9 | 1,547.5 |
| emi:si | demand | 1,088.0 | 1,444.3 | 1,287.2 |

No value is zero or negative; no series is constant. No (entity, variable, ts_utc) is given twice.

New Zealand less the two islands: for demand, within 1 MWh in every month (36 months differ by exactly 1 MWh, rounding). For generation, 35 months differ, and four by more than 1 GWh, as the header names them: June 2026 +1.6 GWh (0.04 percent of New Zealand's), July +9.9 (0.24 percent), August +8.3 (0.20) and September +7.8 (0.21). These are EMI's own figures, kept as given.

The counts were computed in session 2261 from the rows, read past the 10 header lines with pandas (every column as text).

Not taken: the reports' dollar columns (NZD). Generation by fuel is not in these reports, whose only dimension is the region; EMI's half-hourly files by unit (`Generation_MD`, 350 monthly files from August 1997, read 445) are more files than the ceiling allows.

## Checks the connector makes

- Before any request, the connector and www.emi.ea.govt.nz are checked against `warehouse/metadata/paused_sources.csv`; a paused publisher stops the run with no request. It is not paused.
- Each CSV must open on its report's title ("Generation trends" or "Demand trends"), and state the region type asked, the time scale "Month" and "Show" GWh, and hold the columns read (`Period start`, `Region ID` and the GWh column), or the run stops.
- A period that is not a calendar month, a region not in the map, a month given twice for a region, or a figure that does not read stops the run.
- For each variable, a month where New Zealand less the islands is more than 1 percent of New Zealand's figure stops the run; a difference above 1 GWh is named in the header.
- Nothing is filled. Ceiling: four requests, a pause of 2 seconds after each, timeout 120 seconds; each asked again unless `--offline`.

## The cross-check

Session 2254 summed the months to whole years in `runs/c102/s2254/cross.py` (on the data machine, not in git), reading the trial copy of the table (the same rows as the table), beside Ember's yearly demand for New Zealand (`owid_ember_electricity_annual`, NZL):

| Year | EMI generation, TWh | EMI demand, TWh | Ember demand, TWh | Generation over demand | EMI demand to Ember's |
|---|---|---|---|---|---|
| 2015 | 42.592 | 41.344 | 43.57 | 1.030 | 0.949 |
| 2016 | 42.149 | 40.747 | 43.15 | 1.034 | 0.944 |
| 2017 | 42.555 | 41.170 | 43.66 | 1.034 | 0.943 |
| 2018 | 42.567 | 41.173 | 43.73 | 1.034 | 0.942 |
| 2019 | 43.112 | 41.702 | 43.75 | 1.034 | 0.953 |
| 2020 | 42.514 | 41.162 | 43.35 | 1.033 | 0.950 |
| 2021 | 42.651 | 41.288 | 43.55 | 1.033 | 0.948 |
| 2022 | 42.654 | 41.190 | 43.25 | 1.036 | 0.952 |
| 2023 | 42.702 | 41.295 | 42.89 | 1.034 | 0.963 |
| 2024 | 43.025 | 41.631 | 44.01 | 1.033 | 0.946 |
| 2025 | 43.068 | 41.639 | 43.34 | 1.034 | 0.961 |

The South Island's generation less its demand, sent north over the HVDC link: 3,040 GWh in 2015, 4,357 in 2016, 1,558 in 2017, 3,516 in 2018, 4,106 in 2019, 3,150 in 2020, 3,268 in 2021, 3,158 in 2022, 3,442 in 2023, 2,105 in 2024, 2,025 in 2025 and 2,976 in 2026 to September.

## License

The header: "License: public (CC BY 4.0, the Authority's copyright statement; see license_verdicts.csv). Source: Electricity Authority, EMI." `license_verdicts.csv` gives the Electricity Authority (New Zealand) "may be public", the same if the ERW sells anything (read 450, the copyright statement on www.ea.govt.nz, recorded in session 2257): "Unless indicated otherwise for specific items or collections of content (either below or within specific items or collections), this copyright material is licensed for re-use under the Creative Commons Attribution (CC-BY) 4.0 international licence." Attribution is to the Electricity Authority; logos, design and third-party works are excluded. `docs/licenses.md` and `coverage.csv`: public.

## Found while writing this note

- Session 2254's report says grid generation "runs 3.3 to 3.6 percent above grid demand every year". Its cross-check gives 1.030 for 2015 (42.592 against 41.344 TWh), so the range is 3.0 to 3.6 percent.
- `vintage` is empty, so a revised month in a later run shows only as a changed value.

Acted on in session 2261: session 2254's report now gives 3.0 to 3.6 percent. The table is unchanged; its `vintage` stays empty.

## What it does not hold

- Generation by fuel or by station, and EMI's half-hourly figures.
- The reports' dollar columns (NZD), and prices.
- Months before January 2015, and the month in progress.
- Regions below the islands.
