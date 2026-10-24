# Luxembourg's electricity sector statistics (ILR, on data.public.lu)

Energy Research Warehouse (ERW), method note written in session 2394 (chain 113) for a table first written on 24 October 2026 (session 2392).

Tables: `ilr_luxembourg_electricity`

## Publisher and address

The Institut Luxembourgeois de Regulation (ILR, the regulator), its data set "Données statistiques du secteur d'électricité (ILR)" on the national open data portal (`https://data.public.lu/fr/datasets/donnees-statistiques-du-secteur-delectricite-ilr/`). Two GETs a run, no key: the data set's record, `https://data.public.lu/api/1/datasets/667bbcc61ceeb0f9faecfd4b/`, which gives the address of its one xlsx resource (it changes with each update), then the workbook itself, on download.data.public.lu (in session 2392, `.../20260901-135330/donnees-statistiques-du-secteur-delectricite.xlsx`, 104,406 bytes). Source id `ilr:donnees-statistiques-electricite`. Connector: `warehouse/connectors/ilr_luxembourg_electricity.py` (session 2392). data.public.lu has no robots file (HTTP 404, read 684); download.data.public.lu's allows every path (read 689).

## Vintage and revision

Written by run `20261024T095143Z` (the write under the lock, offline), which read the workbook saved at 2026-10-24T09:35:06Z (`retrieved_at`). `vintage` is the workbook's last modified time, 2026-09-01T13:53:32Z, in every row. The record gives the data set an annual frequency, and sheet 1 says "dernière mise à jour le 01.09.2026"; the months of the current year are provisional in ILR's words and are marked `provisional` in `x_status` (18 rows, January to June 2026). Every run that is not `--offline` asks for the record and the workbook again and writes the table again (`write_snapshot`).

## Shape and variables

Series, 668 rows (342 monthly, 326 annual), 15 entities. The workbook ("Tableau de bord du secteur d'électricité") has a sheet a subject; the connector reads eleven blocks of four sheets (`BLOCKS`).

- `entity`: `ilr:lu:<the class, source or neighbour as a slug>`; ILR's own totals are `ilr:lu:total`. `node` is ILR's label.
- `variable`:
  - `withdrawal` (sheet 1, monthly, MWh, 342 rows): the electricity withdrawn by industrial customers (more than 2 GWh a year), professional customers (2 GWh or less) and residential customers, January 2017 to June 2026.
  - `customers` (sheet 1, count, 36 rows): customers at 31 December by class and in all, 2017 to 2025, written on the year's first day with `freq` P1Y.
  - Sheet 2, by source of energy (biogas, biomass, natural gas cogeneration, wind, hydro, solar, the incineration plant, and the total), 2022 to 2025: `capacity` (MW), `injection` (the volume injected into the grid, MWh), `generation` (national production, MWh) and `connections` (installations connected, count; for wind, the number of towers).
  - Sheet 3, the self-consumers and sharing groups by source, 2022 to 2025: `self_consumers` (count), `self_consumption_capacity` (MW), `self_consumption` (the volume self-consumed or shared, MWh), `self_consumer_injection` (MWh).
  - `import` and `export` (sheet 7, annual, MWh, 27 rows each): with Germany, Belgium and France, 2017 to 2025.
- `unit`: MWh (ILR's kWh / 1,000), MW (kW / 1,000) or count.
- `ts_utc` the month's or the year's first day; `freq` P1M or P1Y; `geo` LU.
- `x_block`: the sheet's number and the block's title.

13 values are 0; none is negative. National production in all, TWh: 2022 1.160, 2023 1.388, 2024 1.511, 2025 1.826. Withdrawals, TWh a year: 2017 6.454, 2020 6.095, 2024 5.997, 2025 5.953. Totals and parts are ILR's: a sum takes one level.

## Reading the source

- The run stops at once, asking nothing, while `ilr_electricity`, data.public.lu or download.data.public.lu is paused.
- Two requests a run (timeouts 60 and 120 seconds); `--offline` reads the saved record and workbook.
- The run stops before the workbook if the record lists other than one xlsx resource, or if its licence is no longer `cc-by`.
- Each block is found by the beginning of its title in the first column, then its header row of years (or of months, for the withdrawals), then its rows to the first blank row.
- The run stops, and no file is written, for any of these:
  - a sheet missing, or a block's title found other than once;
  - a block without a header of years or months;
  - a withdrawal row before its year's row;
  - a customer row that is not a year, or a neighbour before "Import" or "Export";
  - a value that is not a number;
  - a workbook with no value;
  - a row given twice (entity, variable and date).
- A blank cell has no row. Nothing is filled.
- Not taken, and said in the header:
  - sheet 7's monthly import and export: from October to December 2025 they run the other way from the annual totals (the annual import from Germany, 2,627.26 GWh, equals the monthly imports to September plus the monthly exports from October, 2,626.49 GWh);
  - the battery sheet (its power in kVA), the market shares, the switching rates, the clients sheet, the charging points, the market organisation, prices and the capacity planning sheet.

## License

Public. `license_verdicts.csv` records the Institut Luxembourgeois de Regulation (ILR), read 690 (session 2392): "may be public", for public and for commercial use. The data set's record gives licence `cc-by` (read 688), and the portal's licence list names it "Creative Commons Attribution 4.0" with `https://creativecommons.org/licenses/by/4.0/` (read 690). The header names ILR.

## Cross-checks (session 2392, against `eurostat_electricity_monthly`'s Luxembourg, 2022 to 2025)

- Wind 0.905 to 0.996; hydro 0.924 to 0.976.
- Solar 0.923 to 0.939 in 2022 and 2023, 0.693 in 2024 and 1.445 in 2025: the two publishers' solar figures diverge (not explained here).
- Withdrawals plus self-consumption over Eurostat's electricity available for the market: 0.992 to 1.027, and 1.092 in 2025.
- Imports 0.735 to 0.835 of Eurostat's; with Eurostat's energy used for pumped storage added, 0.933 to 1.004. Exports 0.033 to 0.093 of Eurostat's. The difference matches the pumping, so Luxembourg's pumped-storage plant at Vianden appears to be outside ILR's trade.
- Withdrawals over `owid_ember_electricity_annual`'s demand: 0.887 to 0.928, 2017 to 2025.

## What it does not hold

- Monthly trade (see above); production, capacity and self-consumption before 2022; the "Cross-Border Physical Flows" data set on the same portal (daily, not read here); prices.
