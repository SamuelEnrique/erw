# EIA-930 hourly demand, the seven US ISOs, 2019 to 2025

A starter table for Redivis: the hourly electricity demand in the seven US independent system operators' balancing authorities, from the U.S. Energy Information Administration's Form EIA-930 (the Hourly Electric Grid Monitor), every hour of 2019 to 2025.

- **File:** `eia930_iso_hourly_demand_2019_2025.csv`. One row per ISO and hour, 429,525 rows; a plain CSV with one header row; sha256 `b24c7376a7cff43a2216801c554262dea91bc6cf1416a68e71036bac7b71dacd`.
- **Columns:** `codebook.csv` (below too).
- **Built:** 2026-10-02 by `warehouse/connectors/eia930_emissions.py` (download) and `warehouse/exports/redivis_starter.py` (this table), Energy Research Warehouse (ERW), https://github.com/SamuelEnrique/erw

## Codebook

| Column | Type | Unit | Description |
|---|---|---|---|
| `ba` | string |  | EIA's balancing authority code (CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP) |
| `iso` | string |  | The ISO's short name (CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP) |
| `utc_hour_start` | datetime (ISO 8601, UTC) |  | The start of the hour, UTC. EIA labels each hour by its end; one hour is subtracted |
| `local_hour_start` | datetime (ISO 8601 with offset) |  | The same instant in the ISO's own time zone (Pacific for CAISO; Central for ERCOT, MISO and SPP; Eastern for ISO-NE, NYISO and PJM), with its UTC offset |
| `demand_mw` | integer | MW | Demand in the balancing authority's area during the hour: EIA-930's Adjusted demand (the reported value, with the hours EIA found anomalous or missing replaced by its imputation), in MWh per hour, which is the hour's mean MW |
| `demand_reported_mw` | integer | MW | EIA-930's Demand as the balancing authority reported it; empty where it reported none |
| `imputed` | boolean |  | true where EIA imputed the hour's demand (its Imputed demand column holds a value), so demand_mw is EIA's estimate, not the reported value |
| `suspect` | boolean |  | true where demand_mw is implausible by the rule in the README (below 30% of the ISO's median hour, or a single hour more than 20% above or below both the hour before and the hour after); the value is EIA's, unchanged |

## Rows, imputed hours, suspect hours and gaps

Each ISO has 61,368 hours in 2019 to 2025. `demand_mw` is EIA's Adjusted demand: where a balancing authority reported nothing, or a value EIA found anomalous (EIA's raw Demand column holds, for example, 2,147,480,000 MW in one PJM hour and 0 MW in NYISO hours), EIA replaced it with its own imputation, and `imputed` is true. The reported value stays in `demand_reported_mw`. An hour with no adjusted demand at all is left out, never filled by us.

EIA's adjusted demand still holds a few hours no grid can have: PJM above 170,000 MW in 2020 (PJM's all-time peak is about 166,000 MW), NYISO at 0 MW, CAISO at 14 MW. They are EIA's published values and are kept unchanged; `suspect` is true for them, by one stated rule: below 30% of the ISO's median hour in 2019 to 2025, or a single hour more than 20% above both the hour before and the hour after, or more than 20% below both (a grid's demand does not jump and fall back within an hour). Filter `suspect = false` to drop them. The rule is a screen, not EIA's: it can miss a bad hour that changes slowly, and it may mark a real sudden change.

| ISO | Balancing authority | Rows | Hours EIA imputed | Hours suspect | Hours left out | Lowest hour, MW | Highest hour, MW | Lowest and highest, not suspect, MW |
|---|---|---|---|---|---|---|---|---|
| CAISO | California Independent System Operator | 61,344 | 94 | 27 | 24 | 14 | 51,104 | 12,655 to 51,104 |
| ERCOT | Electric Reliability Council of Texas | 61,344 | 24 | 0 | 24 | 27,449 | 85,544 | 27,449 to 85,544 |
| ISO-NE | ISO New England | 61,368 | 2 | 0 | 0 | 6,032 | 25,898 | 6,032 to 25,898 |
| MISO | Midcontinent Independent System Operator | 61,368 | 58 | 0 | 0 | 48,878 | 120,781 | 48,878 to 120,781 |
| NYISO | New York Independent System Operator | 61,368 | 0 | 6 | 0 | 0 | 31,857 | 11,061 to 31,857 |
| PJM | PJM Interconnection | 61,365 | 171 | 7 | 3 | 56,260 | 224,345 | 58,480 to 160,560 |
| SPP | Southwest Power Pool | 61,368 | 2 | 2 | 0 | 1,505 | 56,010 | 20,351 to 56,010 |

## Source

U.S. Energy Information Administration, Form EIA-930, Hourly Electric Grid Monitor (https://www.eia.gov/electricity/gridmonitor/about): each balancing authority's workbook, sheet Published Hourly Data, columns Adjusted demand, Demand and Imputed demand. The workbooks used:

- CISO: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/CISO.xlsx (last modified Tue, 29 Sep 2026 16:02:04 GMT; downloaded 2026-09-29T18:19:52Z)
- ERCO: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/ERCO.xlsx (last modified Tue, 29 Sep 2026 16:04:35 GMT; downloaded 2026-09-29T18:23:12Z)
- ISNE: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/ISNE.xlsx (last modified Tue, 29 Sep 2026 16:08:56 GMT; downloaded 2026-09-29T18:25:06Z)
- MISO: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/MISO.xlsx (last modified Tue, 29 Sep 2026 16:10:30 GMT; downloaded 2026-09-29T18:27:13Z)
- NYIS: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/NYIS.xlsx (last modified Tue, 29 Sep 2026 16:11:53 GMT; downloaded 2026-09-29T18:29:31Z)
- PJM: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/PJM.xlsx (last modified Tue, 29 Sep 2026 16:13:39 GMT; downloaded 2026-09-29T18:31:37Z)
- SWPP: https://www.eia.gov/electricity/gridmonitor/knownissues/xls/SWPP.xlsx (last modified Tue, 29 Sep 2026 16:18:20 GMT; downloaded 2026-09-29T18:33:59Z)

Notes: EIA labels each hour by its end; `utc_hour_start` is that label less one hour. EIA's demand is in MWh for the hour, which is the hour's mean MW. EIA revises recent data; 2019 to 2025 is past its usual revision window, but values can still change in a later workbook.

## License

Public domain. EIA's Copyrights and Reuse page (https://www.eia.gov/about/copyrights_reuse.php): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products ... if you use or reproduce any of our information products, you should use an acknowledgment, which includes the publication date".

## Suggested citation

U.S. Energy Information Administration, Form EIA-930 Hourly Electric Grid Monitor, balancing authority workbooks (accessed 2026-09-29). Hourly demand for the seven US ISOs, 2019 to 2025, prepared by the Energy Research Warehouse (ERW), 2026-10-02, https://github.com/SamuelEnrique/erw.
