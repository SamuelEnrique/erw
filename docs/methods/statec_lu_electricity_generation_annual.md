# Luxembourg's electricity generation and trade, 1928 to 2024 (STATEC's LUSTAT)

Energy Research Warehouse (ERW), method note written in session 2773 (chain 140) for two tables first written on 26 October 2026 (sessions 2771 and 2776).

Tables: `statec_lu_electricity_generation_annual`, `statec_lu_electricity_trade_annual`

## Publisher and address

STATEC, Luxembourg's national statistics institute, through LUSTAT, its .Stat Suite SDMX service (`https://lustat.statec.lu/`). No key. Each table reads one dataflow, every key, as CSV with labels:
- `statec_lu_electricity_generation_annual`: DF_A4203 "Electricity generation", `https://lustat.statec.lu/rest/data/LU1,DF_A4203,1.0/all?format=csvfilewithlabels`; source id `statec:lustat_df_a4203`; connector `warehouse/connectors/statec_electricity_generation.py` (session 2771).
- `statec_lu_electricity_trade_annual`: DF_A4208 "Electricity imports and exports by country", `https://lustat.statec.lu/rest/data/LU1,DF_A4208,1.0/all?format=csvfilewithlabels`; source id `statec:lustat_df_a4208`; connector `warehouse/connectors/statec_electricity_trade.py` (session 2776).

Both store their raw files in `warehouse/raw/statec/`. lustat.statec.lu has no robots file: its address answers the data explorer's page (reads 1560 and 1565). statistiques.public.lu's robots file closes query strings and search to `*` and names no Claude agent (read 1561).

## Vintage and revision

- The generation table was written by run `20261026T001326Z`, reading the file retrieved at 2026-10-26T00:09:49Z.
- The trade table was written by run `20261026T001929Z`, reading the file retrieved at 2026-10-26T00:17:03Z.
- STATEC adds a year each year and may revise earlier ones.

## Shape and variables

Both are series, MWh (the dataflows' GWh rows times 1,000; the same figures in TJ and ktep are not written). `ts_utc` the year's first day; `freq` P1Y; `geo` LU; `node` STATEC's code and label. A missing observation (STATEC's "not available", "not applicable" and the like) has no row.

**`statec_lu_electricity_generation_annual`** (942 rows, 19 entities, 1928 to 2024): `entity` `statec_elec:lu:<code>`, `variable` `electricity_generation`. The codes are:
- l01 total gross generation and l02 net generation;
- sl01 gross primary and sl02 gross secondary generation;
- sl03 to sl07 net generation by plant type (hydro, wind, solar, thermal, combined heat and power);
- ssl01 to ssl05 the same under primary and secondary generation;
- sssl01 of which pumping, and sssl02 to sssl05 siderurgy, biogas, wood wastes and pellets.

Net generation was 428,000 MWh in 1928, 1,322,035 in 1990 and 2,708,833 in 2024.

**`statec_lu_electricity_trade_annual`** (584 rows, 10 entities, 1933 to 2024): `entity` `statec_trade:lu:<code>`, `variable` `electricity_imports` or `electricity_exports`. The codes are:
- l01 imports, from sl01 Belgium, sl02 France and sl03 Germany; Germany's split into ssl01, the Société électrique de l'Our (SEO), and ssl02, others;
- l02 exports, to sl04 Belgium, sl05 France and sl06 Germany's RWE grid.

Imports and exports were 4,665,464 and 754,921 MWh in 1990, and 6,571,238 and 1,321,776 in 2024.

## Reading the source

- Each run stops at once, asking nothing, while `statec` or lustat.statec.lu is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **How the generation codes relate,** as the data show it:
  - sl01 is ssl01 to ssl03 and sl02 is ssl04 and ssl05, within 0.5 GWh every year (a miss stops the run);
  - l01 is sl01 plus sl02;
  - l02 is sl03 to sl07, except 1933 (4.5 GWh), which is counted and kept as published.
- **Trade:** imports equal their three countries and exports theirs, within 0.5 GWh every year (a stop). Germany's split differs in 1963 (623.6 GWh) and 1969 (45.0 GWh), counted and kept as published.
- A header not the service's, a unit, frequency or code not expected, a key given twice or a value not a number stops either run. Nothing is filled.

## License

Public. STATEC's legal notice, linked from LUSTAT's footer (read 1564): the portal's information is published "without restriction, under the terms of the Universal Transfer in the Public Domain Creative Commons CC0 1.0". Goodwill guidelines ask for the source and the links, which the headers keep. The verdict, may be public, was given in session 2771. Both tables are in the release package and held from the live set.

## Cross-check

Against `eurostat_electricity_production_annual` and `eurostat_electricity_trade_annual` (Luxembourg), GWh:

| Year | Gross generation l01 | Eurostat TOTAL | Wind sl04 | Eurostat RA300 | Imports l01 | Eurostat imports | Exports l02 | Eurostat exports |
|---|---|---|---|---|---|---|---|---|
| 2010 | 4,591.5 | 4,591.3 | 55.1 | 55.1 | 7,279.5 | 7,279.5 | 3,216.1 | 3,216.1 |
| 2020 | 2,234.3 | 2,234.3 | 351.1 | 351.1 | 6,543.5 | 6,543.5 | 1,078.6 | 1,078.6 |
| 2024 | 2,738.1 | 2,742.3 | 466.8 | 466.8 | 6,571.2 | 6,571.2 | 1,321.8 | 1,321.8 |

Pumping (sssl01) against Eurostat's pumped hydro (RA130) agrees within 7.7 GWh (2010: 1,368.0 against 1,360.3).
