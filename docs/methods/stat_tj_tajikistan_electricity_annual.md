# Tajikistan's electricity output, trade and consumption a year, 1991 to 2025 (the Agency on Statistics' analytical table)

Energy Research Warehouse (ERW), method note written in session 2667 (chain 133) for a table first written on 25 October 2026 (session 2659).

Tables: `stat_tj_tajikistan_electricity_annual`

## Publisher and address

The Agency on Statistics under the President of the Republic of Tajikistan, analytical table "Electricity output, trade and consumption, 1991-2025", `https://www.stat.tj/wp-content/uploads/2026/09/table_11-1.xlsx`, listed on its Analytical tables page (`https://www.stat.tj/en/analytical-tables/`), no key. Source id `stat_tj:analytical_table_11`. Connector: `warehouse/connectors/stat_tj_tajikistan_electricity.py` (session 2659), whose raw store is `warehouse/raw/stat_tj/`. stat.tj sends to www.stat.tj, whose robots file closes only `/wp-admin/` (read 1343).

## Vintage and revision

Written by run `20261025T101039Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T10:07:12Z, last modified 26 September 2026. The Agency replaces the workbook as each year is added.

## Shape and variables

Series, 475 rows, 14 entities, each year from 1991 to 2025. `entity` `tajstat:tj:<item>`:
- `output`, `hydro` and `thermal` (`generation`);
- `imports` and `exports`;
- `consumption` (the total internal consumption), `industry`, `construction`, `agriculture`, `transport`, `other_sectors` and `households` (`consumption`);
- `losses` (`distribution_losses`) and `discrepancy` (`statistical_difference`).

`unit` MWh (the table's billion kWh times 1,000,000); `ts_utc` the year's first day; `freq` P1Y; `geo` TJ; `node` the row's label.

The output was 17.6 TWh in 1991, 14.3 in 2000, 16.4 in 2010, 19.8 in 2020 and 24.0 in 2025, of it 22.3 hydro. In 2025 exports were 5.4 TWh and imports 2.7.

## Reading the source

- The run stops at once, asking nothing, while `stat_tj` or www.stat.tj is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- The sheet is read by its title, its unit line ("in billions of kilowatt hours") and its header of years from 1991, each row by its label. A dash or a blank cell has no row (thermal power in 2010; the discrepancy in 14 years).
- **The parts do not always add to the totals,** and every row is kept as published:
  - From 2015 the output exceeds hydro and thermal power by up to 0.9 TWh (2017: 18.1 against 17.2).
  - From 2016 the total internal consumption differs from its sectors and losses. In 2025 it is 18.2 TWh against 21.2, while output, imports and exports balance to 21.3.
- The run stops for:
  - a title, unit line or year header not as above;
  - a row not in the map, given twice or missing;
  - a value not a number, or negative outside the discrepancy;
  - hydro and thermal missing the output by more than 1 TWh.

Nothing is filled.

## License

Public. The site's footer (read 1349): "Все материалы сайта доступны по лицензии: Creative Commons Attribution 4.0 International", and "When using materials published on this site, a link to www.stat.tj is required". Verdict: may be public. Cited as "Agency on Statistics under the President of the Republic of Tajikistan, www.stat.tj". In the release package; held from the live set.

## Cross-check

Generation against `eia_world_electricity_annual`'s Tajikistan, in TWh:
- 2018: 19.7 against 19.74; 2022: 21.4 against 21.49; 2024: 22.4 against 22.2.
- 2023: 21.9 against 21.23.

In 2024 the Agency gives imports of 1.6 TWh and exports of 3.9, where EIA gives 0.9 and 3.5.
