# The Solomon Islands' electricity production by station a year, 2017 to 2025 (Solomon Power's Annual Report 2025)

Energy Research Warehouse (ERW), method note written in session 2611 (chain 129) for a table first written on 25 October 2026 (session 2602).

Tables: `siea_solomon_electricity_annual`

## Publisher and address

The Solomon Islands Electricity Authority, trading as Solomon Power, Annual Report 2025, page 15's table "Energy Produced": `https://solomonpower.com.sb/wp-content/uploads/2026/09/2025-Annual-Report.pdf`, listed on its Annual Reports page (`https://solomonpower.com.sb/annual-reports/`, reports for 2010 to 2025). One GET, no key. Source id `siea_sb:annual_report_2025_energy_produced`. Connector: `warehouse/connectors/siea_solomon_electricity.py` (session 2602), whose raw store is `warehouse/raw/siea_sb/`. solomonpower.com.sb's robots file names `*` with a crawl delay of 10 seconds and closes only system paths (reads 1170 and 1172); the delay is kept. The National Statistics Office's host fails certificate verification (read 1169).

## Vintage and revision

Written by run `20261025T045248Z` (the write under the lock, offline), which read the report saved at 2026-10-25T04:47:18Z. `vintage` is its last-modified time, 2026-09-23T05:35:38Z. Each year's report has its own address and repeats the table's earlier years.

## Shape and variables

Series, 49 rows, 6 entities. `entity` `siea:sb:<station>`: lungga, honiara, outstations, henderson_solar (1 MW), ranadi_solar (50 kW) and total; `variable` `production`; `unit` MWh (the report's GWh times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` SB; `node` the report's label. Ranadi has 2022 to 2025 only: its years 2017 to 2021 are printed "Not Available" and not written.

The total grew from 93.34 GWh in 2017 to 118.00 GWh in 2025. In 2025 Lungga made 101.10 GWh, the outstations 12.67, Henderson solar 2.68, Honiara 1.41 and Ranadi solar 0.14.

## Reading the source

- The run stops at once, asking nothing, while `siea_sb` or solomonpower.com.sb is paused.
- One request a run; `--offline` reads the saved report.
- **The page** is found by its title line ("Energy produced in 2025 compared with ..."), once; its header ("Station 2017 ... 2025") gives the years, which must run without a gap.
- **Lungga, Honiara, the outstations and the total** each hold one figure a year on their line. **Henderson's** label stands alone, its figures on the next line, "Solar (1 MW)" after them. **Ranadi's** line prints "Not" for each year without a figure, its figures on the next line, and "(50kW) Available" after; the figures are the last years'.
- **Check:** each year's stations add to its total within 0.1 GWh. The gaps the table holds are 0.04 (2017), 0.02 (2018), 0.042 (2022) and 0.015 (2023); the last two equal Ranadi's figure, as if the printed total left Ranadi out in those years.
- The run stops, and no file is written, for: the title found other than once, a row missing or given twice, a line of the wrong count, a check missed.

Nothing is filled. Not taken: the page's peak demand (one figure for Honiara), the report's sales and financial tables.

## License

Internal. Solomon Power's home page (read 1171) carries only "© 2026 | Solomon Islands Electricity Authority"; the site links no terms page and the report states no terms of reuse. Verdict: needs written permission (a copyright line with no reuse statement, ZIMSTAT's precedent). Held from the live set and from Redivis.

## Cross-check

EIA's world table (`eia_world_electricity_annual`, read past its header lines) gives the Solomon Islands 106.0 GWh of generation in 2017 and 111.8 GWh in 2024, against Solomon Power's 93.34 and 110.92: EIA's figure is the country's, Solomon Power's its own grids. Within the report, its text's 102.51 GWh for Lungga and Honiara in 2025 is 101.10 plus 1.41, and its 2.82 GWh for Henderson and Ranadi is 2.68 plus 0.14.
