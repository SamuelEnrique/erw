# Canada's natural gas trade with the U.S. (Canada Energy Regulator)

Energy Research Warehouse (ERW), method note written in session 918 (chain 051) for a table first written on 23 October 2026.

Tables: `cer_gas_trade`

## Publisher and address

Canada Energy Regulator (CER), Natural Gas Trade Summary workbook, compiled from the CER's monthly Commodity Statistics reports, linked from `https://www.cer-rec.gc.ca/en/data-analysis/energy-commodities/natural-gas/statistics/natural-gas-trade-summary/index.html`. Workbook when written: `natural-gas-trades-summary-resume-echanges-commerciaux-gaz-naturel.xlsx` in the same folder. Connector: `warehouse/connectors/cer_gas_trade.py` (session 910).

## Vintage and revision

Pipeline exports January 2010 to December 2025 when written (run `20261023T080430Z`; the workbook retrieved 2026-10-23T08:01:13Z, last modified 1 April 2026, "updated March 2026" on the page). A snapshot: each run replaces the table whole. A run asks for the page again and reuses the saved workbook while its address is the same (ceiling: two requests); `--offline` asks nothing. The CER notes that the latest figures, with revisions, are on its Commodity Statistics pages (apps.cer-rec.gc.ca, whose host reset the connection to its robots file in session 910); this table holds the workbook as published.

## Shape and variables

Series. `ts_utc` the month's first day; `freq` `P1M`; `geo` `CA`; `node` in words.

| Entity | Variable | Unit | What it is |
|---|---|---|---|
| `cer_gas_trade:CA` | `exports` | `Mcf` | pipeline exports to the U.S. (sheet "Fig. 1(m) Fig. 4(m)") |
| `cer_gas_trade:CA:US_WEST`, `:US_MIDWEST`, `:US_EAST` | `exports` | `Mcf` | the same by the U.S. region of the border crossing ("Fig. 2(m)"); the three sum to CA's |
| `cer_gas_trade:CA:LNG` | `exports` | `Mcf` | LNG exports as their gaseous equivalent ("Fig. 3(m)", from 2013) |
| `cer_gas_trade:CA` | `export_price` | `USD/MMBtu` | the export price ("Fig. 5(m)") |
| `cer_gas_trade:CA` | `imports`, `import_price` | `Mcf`, `USD/MMBtu` | imports from the U.S. and their price ("ARCHIVED - Imports"), to December 2022 |

When written: 1,427 rows; 192 months of each pipeline export series and of the export price, 155 of LNG exports, 156 of imports and of their price. LNG exports were at most 2.6 Bcf a year to 2024 and 110.9 Bcf in 2025.

## Reading the workbook

- The page must link exactly one natural gas trade workbook, or the run stops; a file that is not a workbook stops it too.
- Each column is found by the start and the end of its heading. The CER's French words carry a broken character, so only the English start and the unit are matched. A heading matched by no column or by two stops the run, as does a date not on a month's first day.
- The imports are taken to December 2022 only. The page says "the import data after December 2022 has been removed from the website", yet the archived sheet runs to December 2024. Its later months fall away from EIA's record of the same flow (88 percent of it in 2023, 45 percent in 2024, 14 percent in December 2024). The 48 import and import price figures after December 2022 are left out and counted in the header.
- Not taken: the CER's cubic metres, its values in Canadian dollars and its prices in Canadian dollars per GJ (no such units in the data standard); the archived sheet's LNG import columns, which repeat its gas import columns figure for figure.
- A cell left empty has no row; nothing is filled. An (entity, variable, ts_utc) given twice stops the run.

## License

The CER's terms (read 96 of `license_reads.csv`) allow non-commercial reproduction with the title and author and a statement that the copy is not produced in affiliation with, or with the endorsement of, the CER; the header carries it. Commercial redistribution needs the CER's written permission.

## Cross-checks (sessions 910 and 918)

- The three regions summed equal total exports within 0.02 percent in all 192 months (exactly in 183); the months summed equal the workbook's annual sheet in 16 of 16 years.
- Against EIA's U.S. pipeline imports from Canada (`eia_gas_trade_country_monthly`, series `N9102CN2`, MMcf times 1,000): 144 of 192 months within 3 percent, median 1.7 percent above EIA's; in 2025, 3,200 and 3,149 Bcf.
- The imports against EIA's U.S. pipeline exports to Canada (`N9132CN2`): 156 months, median 3.0 percent below EIA's.
- The export price against EIA's price of U.S. imports from Canada (USD/Mcf): median ratio 0.986.
- Session 918, against the code: the cut is `IMPORTS_TO`, 2022-12-01, applied to both import variables; the header's counts are the run's.

## What it does not hold

- The border crossings (ports): the workbook groups them into three regions.
- Imports after December 2022, values, and Canadian dollar prices.
