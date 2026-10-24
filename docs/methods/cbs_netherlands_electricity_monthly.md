# The Netherlands' electricity balance, a month (Statistics Netherlands table 84575NED)

Energy Research Warehouse (ERW), method note written in session 2233 (chain 099) for a table first written on 24 October 2026 (session 2231).

Tables: `cbs_netherlands_electricity_monthly`

## Publisher and address

Statistics Netherlands (CBS), table 84575NED, "Elektriciteitsbalans; aanbod en verbruik" (the electricity balance; supply and consumption), `https://dataportal.cbs.nl/detail/CBS/84575NED`. The connector reads the dataset download `https://datasets.cbs.nl/csv/CBS/nl/84575NED`, a zip of semicolon-separated files, of which it uses Observations.csv (Measure, Perioden, Value), MeasureCodes.csv (the 30 measures, all "mln kWh"), PeriodenCodes.csv (the periods and their status) and Properties.csv (the License). Source id `cbs:84575NED`. Connector: `warehouse/connectors/cbs_electricity.py` (session 2231). opendata.cbs.nl's robots file disallows its OData paths, which the connector does not use; datasets.cbs.nl has no robots file (HTTP 404, session 2231).

## Vintage and revision

January 1976 to July 2026, written by run `20261024T025350Z` (24 October 2026), which read the saved zip (its log). The zip, 144,901 bytes, was retrieved at 2026-10-24T02:51:52Z (`retrieved_at` in every row); `vintage` is its Last-Modified, 2026-09-29T18:03:10Z, in every row. The header's "Retrieved: 20261024T025350Z" is the write's run id; it also states the zip's time.

`x_status` is the period's status in PeriodenCodes.csv:

| `x_status` | Rows | Months |
|---|---|---|
| Definitief (final) | 7,951 | January 1976 to December 2023 (576) |
| NaderVoorlopig (revised provisional) | 719 | January 2024 to December 2025 (24) |
| Voorlopig (provisional) | 210 | January to July 2026 (7) |

Every run that is not `--offline` asks for the zip again and writes the table again (`write_snapshot`): CBS's revisions of provisional months replace the rows held.

## Shape and variables

Series, 8,880 rows: 30 measures, 607 months. `entity` cbs:nl; `variable` the measure's English name from the connector's map `NAMES` of CBS's 30 codes; `node` CBS's Dutch title for the measure; `unit` MWh (CBS's million kWh times 1,000); `ts_utc` the month's first day; `freq` P1M; `geo` NL; `market` blank; extra columns `x_measure` (CBS's code) and `x_status`. For the ten country measures CBS's title is the country alone ("België", "Duitsland" and so on), the same for an import and an export; `x_measure` ends in `_1` for the import and `_2` for the export. Totals are CBS's measures, never sums made here. 272 values are 0; none is negative.

The measures' spans: gross_production, own_use, net_production, import, export, distribution_losses and net_consumption from January 1976 (607 months); import_belgium and import_germany from February 1976 (340 rows), export_belgium and export_germany from August 1982 (376); import_norway and export_norway from May 2008 (219); the United Kingdom from May 2011 (183); Denmark from January 2019 (91); net_wind and net_wind_onshore from January 2002 (295), net_wind_offshore from October 2006 (238); net_nuclear, net_fuels, net_coal, net_oil_products, net_natural_gas, net_biomass, net_other_fuels, net_hydro, net_solar and net_other_sources from January 2015 (139 rows each, but net_nuclear 134: May and June 2017, June 2021, April 2023 and May 2024 are empty).

TWh a year (the twelve months summed here for this note):

| `variable` | 1976 | 2015 | 2025 |
|---|---|---|---|
| gross_production | 58.14 | 110.21 | 135.36 |
| own_use | 2.45 | 4.46 | 3.82 |
| net_production | 55.69 | 105.75 | 131.54 |
| net_natural_gas | | 44.57 | 47.93 |
| net_coal | | 40.20 | 11.96 |
| net_nuclear | | 3.86 | 3.80 |
| net_biomass | | 4.34 | 6.30 |
| net_wind | | 7.55 | 32.04 |
| net_wind_offshore | | 1.13 | 15.61 |
| net_solar | | 1.11 | 25.88 |
| import | 0.02 | 30.76 | 16.31 |
| export | 0.32 | 22.01 | 30.35 |
| distribution_losses | 2.48 | 5.26 | 4.71 |
| net_consumption | 52.90 | 109.24 | 112.78 |

CBS's description, quoted in the connector: "Volledige gegevens per maand zijn beschikbaar vanaf 2015. Vanaf 1936 per jaar en vanaf 1976 per maand zijn alleen de totale productie, invoer en uitvoer bekend" (complete monthly figures from 2015; from 1976 a month only the total production, imports and exports). The file holds more than that before 2015: own use, net production, distribution losses, net consumption and the imports from Belgium and Germany a month from 1976, as listed above. The description, quoted in the connector's docstring (lines 21 to 24) and in session 2231's report (line 18), is narrower than the rows.

## Reading the source

- The run stops at once, asking nothing, while `cbs_electricity` or the host datasets.cbs.nl is paused.
- One request a run: the zip, fetched fresh unless `--offline` (timeout 120 seconds, 1 second's pause after it). HTTP 404 stops the run; any other failure is tried up to `RETRIES` (4) times, 5, 10 and 15 seconds apart. `--offline` reads the saved zip in `warehouse/raw/cbs_electricity/` and stops if it is missing.
- A zip without Observations.csv, MeasureCodes.csv or PeriodenCodes.csv, a measure in MeasureCodes.csv not in `NAMES`, a unit other than "mln kWh", Observations.csv without the columns Measure, Perioden and Value, a monthly period code not four digits, "MM" and two digits (as 2025MM01), an observation of a measure not in `NAMES`, a value that is not a number, no monthly value, or a measure and month given twice stops the run; no file is written.
- Only periods whose code contains "MM" are read: CBS's years and quarters are not taken. An empty Value has no row; nothing is filled.
- The code counts no row ceiling.

## License

Public. `license_verdicts.csv` records Statistics Netherlands, read 376 (session 2229): "may be public", for public and for commercial use. The table's own License property: "https://creativecommons.org/licenses/by/4.0/", the same as CBS's catalog entry in the download. The header gives the source as "CBS". `sources.csv` flags `cbs:84575NED` public; `license_tables.csv` lists the table under Statistics Netherlands.

## Cross-checks (session 2233)

- The written table and session 2231's trial copy hold the same 8,880 keys with every column equal, so the session's results (`runs/c099/s2231/cross.out`) hold for the written rows:
  - net production plus imports less exports less distribution losses equals net consumption within 1,000 MWh (CBS's rounding of a million kWh) in all 607 months;
  - against `eurostat_electricity_monthly` (the Netherlands), full years 2016 to 2025: net production 0.985 (2018) to 1.017 (2017); imports and exports 1.000 in every year from 2017 but 2018, where Eurostat lacks a month; in 2016 imports 1.002 and exports 0.974;
  - net consumption over `owid_ember_electricity_annual`'s Dutch demand: 0.930 to 0.942.
- Computed from the rows here: gross production less own use equals net production within 1,000 MWh in all 607 months; from 2015, net production equals nuclear, fuels, hydro, wind, solar and other sources within 2,000 MWh, and the fuels equal their five parts within 2,000 MWh; total imports equal the five countries' within 2,000 MWh from 2019, when Denmark's begin (before it, by up to 1,343,000 MWh, as some countries are not given).

## What it does not hold

- CBS's years and quarters, among them the years from 1936 that its description names.
- Production by source before 2015, but wind from 2002.
- Trade with countries other than the five CBS names, and the five before their first months above.
- Prices, capacity and consumption by sector: the table is the national balance.
