# The UK's interconnector flows a year, 1998 to 2025 (DESNZ's DUKES 5.13)

Energy Research Warehouse (ERW), method note written in session 2717 (chain 136) for a table first written on 25 October 2026 (session 2715).

Tables: `desnz_uk_interconnector_flows_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ), Digest of UK Energy Statistics (DUKES) 2026, chapter 5 (`https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes`). The table reads the workbook "Capacity, net imports and utilisation of interconnectors (DUKES 5.13)", `https://assets.publishing.service.gov.uk/media/6a6a3675bf4a7aca8f8976c3/DUKES_5.13.xlsx`, its sheet "5.13". No key. Source id `desnz:dukes_5_13_interconnectors`. Connector: `warehouse/connectors/desnz_dukes_interconnectors.py` (session 2715), whose raw store is `warehouse/raw/desnz_dukes/`. www.gov.uk's robots file closes only print and search paths (read 1448); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T182339Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T17:13:14Z (last modified 2026-07-29T17:20:53Z). DESNZ's notes:
- the flows are from National Grid's demand data, except those between Ireland and Northern Ireland, which EirGrid supplies;
- utilisation is the year's imports and exports over the possible flow at the capacity of table 5.13A.

## Shape and variables

Series, 642 rows, ten entities, each year from 1998 to 2025 where given. `entity` `desnz_ic:<pair>`:
- **The seven interconnector borders:** `france` (IFA, IFA 2 and ElecLink together), `ireland_northern_ireland` (North-South, into Northern Ireland), `netherlands`, `ireland_wales`, `belgium`, `norway`, `denmark`.
- **`uk_total`,** the seven summed by DESNZ.
- **Two transfers within the UK:** `scotland_england` and `scotland_northern_ireland`, the latter over Moyle, which DESNZ counts as a transfer.

`variable` `imports`, `exports`, `net_imports` (MWh, the sheet's GWh times 1,000) and `utilisation` (ratio). For the transfers: `transfers_to_england` or `transfers_to_northern_ireland`, `transfers_to_scotland` and `net_transfers` (MWh). `ts_utc` the year's first day; `freq` P1Y; `geo` GB; `node` the sheet's heading.

**Figures:**
- The UK's net imports were 12.7 TWh in 1998, 2.7 in 2010, 17.9 in 2020, -5.3 in 2022 and 29.7 in 2025.
- In 2025:
  - net imports of 21.9 TWh from France, 9.0 from Norway and 2.5 from Denmark;
  - net exports of 4.5 TWh to Ireland from Wales and 1.6 from Northern Ireland;
  - Scotland sent England 18.5 TWh net.

## Reading the source

- The run stops at once, asking nothing, while `desnz_dukes` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- Each of the sheet's 38 headings is matched exactly to its pair and variable; a heading not in the map stops the run.
- "[x]" (not available) and a blank cell have no row. Belgium's zeros of 2017 and 2018, before Nemo Link opened in 2019, are kept as DESNZ writes them.
- **Checks,** within 0.01 GWh, all passing:
  - each pair's imports less exports equal its net, and each transfer's directions its net;
  - the seven interconnectors add to the UK's totals where all are given;
  - every utilisation lies in [0, 1].
- Table 5.13A (each interconnector's capacity) is not taken. Nothing is filled.

## License

Public. The Open Government Licence v3.0; DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

Against `eurostat_electricity_trade_annual`, each partner's own record of its trade with the UK, in TWh:

| Year | France's exports to the UK | DESNZ's UK imports from France | France's imports from the UK | DESNZ's UK exports to France | Norway's exports to the UK | DESNZ's UK imports from Norway |
|---|---|---|---|---|---|---|
| 2023 | 16.68 | 15.62 | 2.61 | 2.75 | 8.54 | 8.95 |
| 2024 | 21.62 | 20.27 | 0.79 | 0.82 | 10.26 | 9.90 |

The two sides meter at opposite ends of the cables.
