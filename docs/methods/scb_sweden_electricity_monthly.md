# Sweden's electricity supply by type of production, a month (Statistics Sweden table TAB1011)

Energy Research Warehouse (ERW), method note written in session 2233 (chain 099) for a table first written on 24 October 2026 (session 2236).

Tables: `scb_sweden_electricity_monthly`

## Publisher and address

Statistics Sweden (SCB), table TAB1011, "Electricity supply in Sweden by type of production", monthly, the Swedish Energy Agency's statistics (`https://www.statistikdatabasen.scb.se/pxweb/en/ssd/START__EN__EN0108/`), through SCB's PxWebApi v2 (no key), two GETs: `https://statistikdatabasen.scb.se/api/v2/tables/TAB1011/metadata?lang=en` (the dimensions and their labels) and `https://statistikdatabasen.scb.se/api/v2/tables/TAB1011/data?lang=en&valueCodes[Prodslag]=*&valueCodes[ContentsCode]=*&valueCodes[Tid]=*&outputFormat=json-stat2` (every cell as JSON-stat 2.0). Source id `scb:TAB1011`. Connector: `warehouse/connectors/scb_electricity.py` (session 2236). SCB's older API (api.scb.se, v1) closed the connection without an answer (session 2236's report). statistikdatabasen.scb.se has no robots file (HTTP 404); www.scb.se's has no Disallow rule.

## Vintage and revision

January 1974 to August 2026, written by run `20261024T030141Z` (24 October 2026), which read the saved metadata and data (its log). The data were retrieved at 2026-10-24T03:00:52Z (`retrieved_at` in every row); `vintage` is the answer's "updated", 2026-10-09T06:00:00Z, in every row. The header's "Retrieved: 20261024T030141Z" is the write's run id; it also states the data's time and SCB's update.

Every run that is not `--offline` asks for both documents again and writes the table again (`write_snapshot`): SCB's revisions replace the rows held.

## Shape and variables

Series, 6,059 rows: 11 lines over 632 months; 893 of the answer's 6,952 cells are empty (null) and have no row. `entity` scb:se; `variable` SCB's English label in snake case, its bracketed words and a closing ", net" dropped; `node` the label as SCB writes it; `unit` MWh (the table's GWh times 1,000); `ts_utc` the month's first day; `freq` P1M; `geo` SE; `market` blank; extra column `x_code`, SCB's code. Totals are SCB's lines, never sums made here. 133 values are 0 (108 gas turbine months, 25 condensation months); none is negative.

The header carries SCB's note: "In the table, import includes transit through Sweden from abroad. Loop force is excluded." The table is supply: production plus imports. It has no line for exports or consumption.

| `variable` | `node` | `x_code` | Rows | TWh 1974 | TWh 2000 | TWh 2025 |
|---|---|---|---|---|---|---|
| sum_of_supply | sum of supply | Tot | 632 | 80.16 | 160.20 | 173.05 |
| hydro_power | hydro power (including pump power), net | Vatten | 632 | 56.62 | 77.85 | 68.08 |
| nuclear_power | nuclear power (condensation), net | Karn | 629 | | 54.76 | 44.79 |
| wind | wind | Vind | 356 | | 0.44 | 38.97 |
| solar_power | solar power (on-grid) | Solkraft | 92 | | | 4.43 |
| conventional_thermal_power | conventional thermal power, net | SumVarmeKraft | 632 | 14.95 | 8.85 | 11.62 |
| of_which_back_pressure_industrial | - of which back pressure, industrial | Mottri | 608 | | 4.33 | 6.52 |
| of_which_back_pressure_district_heating_work | - of which back-pressure, district heating work | Mottrk | 608 | | 4.23 | 5.05 |
| of_which_condensation | - of which condensation | Kondens | 630 | 8.08 | 0.26 | 0.05 |
| of_which_gas_turbine_etc | - of which gas turbine etc. | Gast | 610 | | 0.03 | 0.00 |
| import | import | Imp | 630 | 6.68 | 18.31 | 5.17 |

TWh a year are the twelve months summed here for this note, shown only for a line with all twelve months; 1974's nuclear lacks June, July and September. Spans: wind from January 1997, solar from January 2019, the two back-pressure lines from January 1976; imports lack July and September 1997. January to August 2026: the sum of supply 113.1 TWh.

## Reading the source

- The run stops at once, asking nothing, while `scb_electricity` or the host statistikdatabasen.scb.se is paused.
- Two requests a run, the metadata then the data, each fetched fresh unless `--offline` (timeouts 60 and 120 seconds, 2 seconds' pause after each). HTTP 404 stops the run; any other failure is tried up to `RETRIES` (4) times, 5, 10 and 15 seconds apart. `--offline` reads the saved files in `warehouse/raw/scb_electricity/` and stops if one is missing. SCB allows ten calls in ten seconds and 100,000 values a table; this table has 6,952.
- Dimensions other than Prodslag, ContentsCode and Tid (in any order), a content label other than "GWh", a value array not the size of the dimensions, a month not of the form YYYYMmm, no value at all, or a line and month given twice stops the run; no file is written. A null cell has no row; nothing is filled.
- The code counts no row ceiling.

## License

Public. `license_verdicts.csv` records Statistics Sweden, read 381 (session 2236): "may be public", for public and for commercial use. The sentence, on SCB's Open data API page: "We use the licence CC0 for this data, which means that you may use and disseminate or provide such data without any requirement to state the source." The same page asks that statistics with another agency as their source state it, and the header does: "Source: Swedish Energy Agency, via Statistics Sweden." `sources.csv` flags `scb:TAB1011` public; `license_tables.csv` lists the table under Statistics Sweden.

## Cross-checks (session 2233)

- The written table and session 2236's trial copy hold the same 6,059 keys with every column equal, so the session's results (`runs/c099/s2236/cross.out`, full years 2016 to 2025) hold for the written rows, against `eurostat_electricity_monthly` (Sweden):
  - the sum of supply less imports over Eurostat's net production TOTAL: 0.999 (2022) to 1.006 (2020);
  - imports over Eurostat's IMP: 1.000 in every year (to three decimals);
  - hydro over RA100: 0.999 to 1.005; nuclear over N9000: 0.999 to 1.001.
- Computed from the rows here: the sum of supply equals hydro, wind, nuclear, solar, conventional thermal and imports (a missing line as 0) within 2,000 MWh in every month from 1998. Before, 68 months differ by more than 1,000 MWh, 60 of them in the 1990s; the largest is August 1984, where the sum is 7,503,000 MWh and its parts 8,629,000. Conventional thermal equals its four kinds (a missing kind as 0) within 2,000 MWh in every month from 2000; 29 months differ by more than 1,000 MWh, 24 of them in the 1970s. Both are as SCB publishes them.
- The connector's docstring, the table's header and session 2236's report were read against the code and the rows; no claim of theirs was found contradicted.

## What it does not hold

- Exports, consumption and losses: TAB1011 is supply only.
- Sweden's bidding zones, prices and capacity.
- Months before January 1974; wind before 1997 and solar before 2019, where SCB leaves the cells empty.
