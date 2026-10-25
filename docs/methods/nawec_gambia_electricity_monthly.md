# The Gambia's electricity a month in 2022 by source (NAWEC's Annual Activity Report 2022, Table 3)

Energy Research Warehouse (ERW), method note written in session 2625 (chain 130) for a table first written on 25 October 2026 (session 2617).

Tables: `nawec_gambia_electricity_monthly`

## Publisher and address

The National Water and Electricity Company (NAWEC), Annual Activity Report 2022, Table 3, "Electricity Month Production": `https://nawec.gm/wp-content/uploads/2026/08/NAWEC-Annual-Activity-Report-2022.pdf`, listed on its Annual Reports page (`https://nawec.gm/?page_id=196`). One GET, no key. Source id `nawec_gm:annual_activity_report_2022_table3`. Connector: `warehouse/connectors/nawec_gambia_electricity.py` (session 2617), whose raw store is `warehouse/raw/nawec_gm/`. nawec.gm has no robots file (HTTP 404, read 1231).

## Vintage and revision

Written by run `20261025T063711Z` (the write under the lock, offline), which read the report saved at 2026-10-25T06:34:00Z. `vintage` is its last-modified time, 2026-08-13T22:21:13Z. NAWEC's later activity reports were not on its page; PURA's 2024 report gives 2024's production (696,382.06 MWh) only in prose.

## Shape and variables

Series, 60 rows, 5 entities, each month of 2022. `entity` `nawec:gm:<source>`:
- `nawec` (NAWEC's own plants: Kotu, Brikama 1 to 3 and the provinces' stations) and `karpower` (Karpowership, an independent producer), `variable` `generation`;
- `senelec` (over SENELEC's lines) and `omvg` (through the OMVG 225 kV interconnection), `variable` `imports`;
- `total`, `variable` `supply`.

`unit` MWh; `ts_utc` the month's first day; `freq` P1M; `geo` GM; `node` the report's column. The report calls every column "production"; the variables say what each source is.

In 2022 (the months' sums): NAWEC 160,353.58 MWh, SENELEC 32,003.59 (the Total line prints 32,003.60), OMVG 165,553.79, Karpower 213,716.57, total 571,627.53 (printed 571,627.54). OMVG's imports begin in March; its January and February are printed 0 and written as 0.

## Reading the source

- The run stops at once, asking nothing, while `nawec_gm` or nawec.gm is paused.
- One request a run; `--offline` reads the saved report.
- **The table** is found by its title line, "2022 Monthly Production ( MWh)", once. The next line must name the columns (NAWEC, SENELEC, OMVG, Karpower, Total), read with the PDF's stray spaces removed. Then come twelve lines, January to December, each a month and five figures (thousands separators removed), then the "Total" line.
- **Checks:** each month's four sources add to its total within 0.1 MWh; each column's months add to the Total line within 0.5 MWh.
- The run stops, and no file is written, for: the title found other than once, a column line or a month line not as expected, a line of the wrong count, a check missed.

Nothing is filled. Not taken: the table's percentages; the plants' fuel, cost and availability tables.

## License

Internal. NAWEC's home page (read 1236): its footer reads "(c) 2026 NAWEC", a dash, then "National Water & Electricity Company, The Gambia. All rights reserved." Its Terms of Service link is an empty anchor. Verdict: needs written permission. The verdict's sentence is cut after the dash, as no ERW file may hold one. Held from the live set and from Redivis.

## Cross-check

EIA's world table (`eia_world_electricity_annual`, read past its header lines) gives the Gambia 511.5 GWh of generation and no imports in 2022. NAWEC's table gives 374.1 GWh generated in the country (NAWEC and Karpower) and 197.6 GWh imported (SENELEC and OMVG). The report's text gives 571,627.54 MWh for 2022 and 467,103.30 MWh for 2021.
