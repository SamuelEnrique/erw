# Energy jobs by sector, technology, industry and state (the Department of Energy's U.S. Energy and Employment Report)

Energy Research Warehouse (ERW), method note written in session 2009 (chain 056) for a table first written on 23 October 2026.

Tables: `doe_useer_employment`

## Publisher and address

U.S. Department of Energy (DOE), Office of Energy Jobs, the 2026 U.S. Energy and Employment Report (USEER), its public data workbook `https://www.energy.gov/documents/2026-useer-public-data` (the address serves the workbook itself), listed on `https://www.energy.gov/policy/us-energy-employment-jobs-report-useer`. Connector: `warehouse/connectors/doe_useer.py` (session 2000). energy.gov's robots file allows `/documents/` and `/policy/`.

## Vintage and revision

The 2026 USEER (employment in 2025, with 2024's totals), the workbook last modified 2 September 2026. A snapshot (ceiling one request). DOE publishes a new report each year at a new address.

## Shape and variables

Series, 3,311 rows: 572 national and 2,739 state rows, 3,229 series. `entity` `useer2026:<geo>:<sector>:<subsector>:<industry>`; `variable` employment; `unit` count (USEER's survey estimate of workers, as published, not rounded); `ts_utc` the year's 1 January (2025, and 2024 for the national totals); `freq` P1Y; `geo` US, US-<state> (the 50 states and DC), or empty for USEER's one row of Puerto Rico and the U.S. Virgin Islands (entity `useer2026:PR_VI:...`, 36 rows).

| x_sector | What | National rows | State rows |
|---|---|---|---|
| fuels | Fuels | 109 | 520 |
| epg | Electric power generation | 117 | 624 |
| td | Transmission and distribution | 55 | |
| storage | Storage | 106 | |
| tds | Transmission, distribution and storage (the state sheet's) | | 364 |
| ee | Energy efficiency | 166 | 312 |
| mvcp | Motor vehicles and component parts | 19 | 460 |
| all | Employment by industry (the state sheet's) | | 459 |

`x_subsector` USEER's technology (solar, land_based_wind, battery, ...) or total; `x_industry` USEER's industry column (agriculture, mining, utilities, construction, manufacturing, trade, pipeline, professional_services, other_services, commodity_flows; the state sheet's pipeline_and_commodity_flows) or total. A total holds its parts: a sum takes one level.

## Reading the workbook

- The sheet "Industry Detail by Sector" gives the nation's blocks; each block's title and headings must be as read. The change column (2025 less 2024) is not taken. Of the 82 national rows with a 2025 total, all 82 equal the sum of their industries within one worker (the connector counts this in the header).
- The block "2025 TDS Employment" is not taken: its one row, "TDS Total", repeats the "Pumped Hydro" storage row figure for figure (the publisher's error); the T&D and storage blocks hold the same workers.
- The sheet "State Data" gives six blocks side by side; their titles must be as read and each state in the map. The five workforce characteristics sheets (sex, ethnicity, race and the rest, as shares) are not taken.
- A cell USEER leaves empty has no row; an (entity, ts_utc) given twice stops the run. Nothing is filled.

## License

Public: DOE's web policies (read 54 of `license_reads.csv`): "Government information at DOE websites is in the public domain."

## Cross-checks (sessions 2000 and 2009)

- Against the report's own summary (the national report's highlights and executive summary): 8,380,422 workers in 2025 (the report: 8.4 million), a change of -86,277 from 2024 (the report: -86,000); electric power generation 919,031 (919,000, -15,000), fuels 1,025,930 (one million, -28,000), energy efficiency 2,360,303 (2.4 million, -21,000), motor vehicles 2,582,820 (2.6 million), transmission, distribution and storage 1,492,338, +28,679 (1.5 million, +28,000).
- The states' sector totals, summed, are within 0.06 to 0.80 percent of the nation's (USEER's state and national estimates are separate).
- Session 2009, against the code: `NATIONAL`, `INDUSTRIES`, `STATE_BLOCKS` and `STATE_INDUSTRIES` give the blocks and columns above; the counts computed from the rows.

## What it does not hold

- Earlier reports (2016 to 2025), the county data, wages, and the workforce characteristics.
