# EIA-930 hourly demand, the seven US ISOs, 2019 to 2025

A starter table for Redivis: the hourly electricity demand served in the seven US independent system operators' balancing authorities, from the U.S. Energy Information Administration's Form EIA-930 (the Hourly Electric Grid Monitor), every hour of 2019 to 2025, as EIA publishes it.

- **File:** `eia930_iso_hourly_demand_2019_2025.csv`. One row per ISO and hour, 429,182 rows; a plain CSV with one header row; sha256 `6098ba37bc8161be5f5e2076bd4bdad2ea7e0b861b5d33fcc0df37f178d6c3f3`.
- **Columns:** `codebook.csv` (below too).
- **Built:** 2026-10-02 by `warehouse/connectors/eia930_emissions.py` (download) and `warehouse/exports/redivis_starter.py` (this table), Energy Research Warehouse (ERW), https://github.com/SamuelEnrique/erw

## Codebook

| Column | Type | Unit | Description |
|---|---|---|---|
| `ba` | string |  | EIA's balancing authority code (CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP) |
| `iso` | string |  | The ISO's short name (CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP) |
| `utc_hour_start` | datetime (ISO 8601, UTC) |  | The start of the hour, UTC. EIA labels each hour by its end; one hour is subtracted |
| `local_hour_start` | datetime (ISO 8601 with offset) |  | The same instant in the ISO's own time zone (Pacific for CAISO; Central for ERCOT, MISO and SPP; Eastern for ISO-NE, NYISO and PJM), with its UTC offset |
| `demand_mw` | integer | MW | Demand served in the balancing authority's area during the hour: EIA-930's Demand, in MWh per hour, which is the hour's mean MW |

## Rows and gaps

Each ISO has 61,368 hours in 2019 to 2025. An hour EIA left empty is left out, never filled.

| ISO | Balancing authority | Rows | Hours EIA left empty | Lowest hour, MW | Highest hour, MW |
|---|---|---|---|---|---|
| CAISO | California Independent System Operator | 61,250 | 118 | 14 | 51,104 |
| ERCOT | Electric Reliability Council of Texas | 61,320 | 48 | 27,449 | 85,544 |
| ISO-NE | ISO New England | 61,366 | 2 | 6,032 | 25,898 |
| MISO | Midcontinent Independent System Operator | 61,310 | 58 | 48,878 | 120,781 |
| NYISO | New York Independent System Operator | 61,368 | 0 | 0 | 31,857 |
| PJM | PJM Interconnection | 61,201 | 167 | 56,260 | 2,147,480,000 |
| SPP | Southwest Power Pool | 61,367 | 1 | 1,505 | 3,621,097 |

## Source

U.S. Energy Information Administration, Form EIA-930, Hourly Electric Grid Monitor (https://www.eia.gov/electricity/gridmonitor/about): each balancing authority's workbook, sheet Published Hourly Data, column Demand. The workbooks used:

- CISO: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/CISO.xlsx (last modified Tue, 29 Sep 2026 16:02:04 GMT; downloaded 2026-09-29T18:19:52Z)
- ERCO: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/ERCO.xlsx (last modified Tue, 29 Sep 2026 16:04:35 GMT; downloaded 2026-09-29T18:23:12Z)
- ISNE: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/ISNE.xlsx (last modified Tue, 29 Sep 2026 16:08:56 GMT; downloaded 2026-09-29T18:25:06Z)
- MISO: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/MISO.xlsx (last modified Tue, 29 Sep 2026 16:10:30 GMT; downloaded 2026-09-29T18:27:13Z)
- NYIS: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/NYIS.xlsx (last modified Tue, 29 Sep 2026 16:11:53 GMT; downloaded 2026-09-29T18:29:31Z)
- PJM: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/PJM.xlsx (last modified Tue, 29 Sep 2026 16:13:39 GMT; downloaded 2026-09-29T18:31:37Z)
- SWPP: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/SWPP.xlsx (last modified Tue, 29 Sep 2026 16:18:20 GMT; downloaded 2026-09-29T18:33:59Z)

Notes: EIA labels each hour by its end; `utc_hour_start` is that label less one hour. EIA's Demand is in MWh for the hour, which is the hour's mean MW. EIA revises recent data; 2019 to 2025 is past its usual revision window, but values can still change in a later workbook.

## License

Public domain. EIA's Copyrights and Reuse page (https://www.eia.gov/about/copyrights_reuse.php): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products ... if you use or reproduce any of our information products, you should use an acknowledgment, which includes the publication date".

## Suggested citation

U.S. Energy Information Administration, Form EIA-930 Hourly Electric Grid Monitor, balancing authority workbooks (accessed 2026-09-29). Hourly demand for the seven US ISOs, 2019 to 2025, prepared by the Energy Research Warehouse (ERW), 2026-10-02, https://github.com/SamuelEnrique/erw.
