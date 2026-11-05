# Saint Lucia's electricity output and consumption, a year (CSO Saint Lucia, LUCELEC's figures)

Energy Research Warehouse (ERW), method note written in session 2499 (chain 121) for a table first written on 24 October 2026 (session 2497).

Tables: `slu_cso_electricity_annual`

## Publisher and address

The Central Statistical Office of Saint Lucia (CSO), its table "Electricity Output and Consumption in Kilowatt Hours (KWh) Thousands, 2010 to 2023" (last updated 28 May 2024), from St. Lucia Electricity Services Limited's (LUCELEC) figures: `https://stats.gov.lc/subjects/sectors/water-and-electricity/electricity-output-and-consumption-in-kilowatt-hours-kwh-thousands-2010-to-2023/`. One GET of the web page, no key. Source ids `slu_cso:electricity_output_consumption` (the CSO) and `lucelec:electricity_output_consumption` (LUCELEC), both naming the table. Connector: `warehouse/connectors/slu_cso_electricity.py` (session 2497). stats.gov.lc's robots file disallows nothing (read 847); www.lucelec.com's asks a crawl delay of 10 seconds, kept (read 853).

## Vintage and revision

2010 to 2023, written by run `20261024T163001Z` (the write under the lock, offline), which read the page saved at 2026-10-24T15:16:36Z. The CSO's earlier pages (1966 to 1980, 1981 to 1995, 1996 to 2010, 2011 to 2017) hold the years before; not taken.

## Shape and variables

Series, 139 rows, 7 entities. `entity` `slu_cso:lc:<item>`; `ts_utc` the year's 1 January; `freq` P1Y; `geo` LC; `node` and `x_label` the CSO's row label, with " *" where the CSO marks a commercial figure that includes hotels.

| Row (as the CSO labels it) | `variable` | Items | Unit |
|---|---|---|---|
| Total Generated (Units generated/purchases) | `generation` | total | MWh |
| Commercial Use (including Hotels) | `sales` | `commercial_excl_hotels` (2010 to 2012, no "*"), `commercial_incl_hotels` (2013 on, "*") | MWh |
| Domestic Use, Hotel Use, Industrial Use, Street Lighting, Total Sales | `sales` | domestic, hotels, industrial, street_lighting, total | MWh |
| Internal Use | `own_use` | total | MWh |
| Loss of transmission | `losses` | total | MWh |
| Available Capacity (kW) | `available_capacity` | total | MW |

- Thousands of kWh are MWh. The commercial row's "*" ("* Includes hotels") marks the years from 2013: before, the hotels' use is outside it and the classes sum to the total (2010: 310,091); from 2013, the hotel row is inside it and the classes without hotels sum to the total (2013: 334,479). The two are two entities, so a sum over classes never counts hotels twice by accident.
- The available capacity is in kW, as the CSO's 2011 to 2017 table heads it ("Maximum Installed Capacity of Plants (KW)"), divided by 1,000: 76.0 MW in 2010 and 2011, 88.6 MW in 2012, 88.4 MW from 2013.

| GWh | 2010 | 2019 | 2020 | 2023 |
|---|---|---|---|---|
| Generated or purchased | 360.3 | 407.9 | 371.6 | 423.5 |
| Sold | 310.1 | 368.9 | 336.5 | 387.0 |

## Reading the source

- The run stops at once, asking nothing, while `slu_cso_electricity` or stats.gov.lc is paused.
- One request a run (timeout 120 seconds); `--offline` reads the saved page.
- **The table:** the page's HTML table, row by row, a label and fourteen years. The section "Average Annual Consumption Per Customer" repeats the commercial row's label; its rows are not taken.
- **Cells without a row:** ".." (not available); a cell out of form, counted in the header (one: 2016's commercial, printed "194,66*").
- The run stops, and no file is written, for: no table, a header other than the years 2010 to 2023, a row of another width, no generation or sales row, a key given twice.

Nothing is filled. Not taken: the consumers' numbers, the growth and loss percentages, the averages per customer, the diesel burned (imperial gallons).

## License

Internal. The CSO's Open Licence Agreement (read 852) grants "a worldwide, royalty-free, non-exclusive licence to freely use the information, copy, modify, translate, publish, adapt, distribute ... for commercial and non-commercial purposes", but "is limited solely to CSO data and shall not extend to any third party data". The figures are LUCELEC's ("Source: St. Lucia Electricity Services Limited (LUCELEC)"). LUCELEC's home page (read 854): "Copyright © 2025 St. Lucia Electricity Services Limited. All Rights Reserved."; its website terms (read 855) grant no reuse. Verdicts (session 2497): the CSO may be public; LUCELEC needs written permission. The table rests on both, so it is internal. Held from the Redivis storage and the live set.

## Cross-checks (session 2497)

- Units generated or purchased over `owid_ember_electricity_annual`'s demand for Saint Lucia: 0.95 to 1.06 (2010 to 2023).
- The CSO's 2011 to 2017 page (read 848) gives the same domestic and industrial figures and the same generation within 1 MWh (2014: 379,432 there, 379,431 here). Its commercial row includes hotels in every year (2011: 190,846, against this page's 122,098 without hotels plus 68,749 for hotels; 2013: 193,199 on both pages), which bears out the reading of the "*".

## What it does not hold

- Generation by source (the table gives the diesel burned, not taken); years before 2010; monthly figures; revenue (EC$).
