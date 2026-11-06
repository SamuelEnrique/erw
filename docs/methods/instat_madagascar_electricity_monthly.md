# Madagascar's public grid a month (INSTAT's Tableau de Bord de l'Economie, table 21, JIRAMA's figures)

Energy Research Warehouse (ERW), method note written in session 2541 (chain 124) for a table first written on 24 October 2026 (session 2532).

Tables: `instat_madagascar_electricity_monthly`

## Publisher and address

The Institut National de la Statistique (INSTAT), Madagascar, the data workbook of its Tableau de Bord de l'Economie (TBE) no. 63, August 2026, sheet `SortieElec`, table 21, "Evolution mensuelle des production et consommation d'electricite" (source: JIRAMA, the national utility): `https://www.instat.mg/documents/upload/main/Donn%C3%A9es%20TBE63_25_08_2026.xlsx`, listed on the TBE's page. One GET, no key. Source id `instat_mg:tbe63_table21`. Connector: `warehouse/connectors/instat_madagascar_electricity.py` (session 2532). www.instat.mg's robots file allows every path with a crawl delay of 3 seconds, which is kept (read 971).

## Vintage and revision

July 2024 to June 2026, written by run `20261024T204203Z` (the write under the lock, offline), which read the workbook saved at 2026-10-24T20:38:34Z. `vintage` is its last-modified time, 2026-08-25T15:42:49Z. Each TBE gives the 24 months before it at its own address; the connector reads no. 63's.

## Shape and variables

Series, 168 rows, 6 entities. `entity` `jirama:mg:<item>`; `unit` MWh, as INSTAT gives them; `ts_utc` the month's first day (the sheet dates each month on the 15th); `freq` P1M; `geo` MG; `node` the variable and INSTAT's column label; `x_period` the month.

| `variable` | Items | 2025, TWh |
|---|---|---|
| `production` | total, hydro, thermal | 2.013 (hydro 0.971, thermal 1.042) |
| `consumption` | total, households, industry_services, public_lighting | 1.434 (households 0.685, industry and services 0.740) |

The totals hold their parts: a sum over entities takes one level.

## Reading the source

- The run stops at once, asking nothing, while `instat_mg_tbe` or www.instat.mg is paused.
- One request a run (timeout 180 seconds, a pause of 3 seconds); `--offline` reads the saved workbook. The workbook is opened read-only (its drawings point to a missing part).
- **The table:** found by its title's words; the columns by their headers, under "Production (MWh)" and "Consommation d'electricite (MWh)", accents dropped for the match.
- **Not taken:** the average price (Ar/kWh, a price in another currency) and the two rows of half-year totals and their change that follow the months.
- The run stops, and no file is written, for: no such sheet or table, a header not found, a month given twice, a gap between months, a figure that is not a number, a total that differs from its parts by more than 1 MWh.

Nothing is filled.

## License

Internal. INSTAT's home page states "Copyright INSTAT 2026. Tous les droits sont reserves" and links no terms of reuse (read 973). Verdict (session 2537): needs written permission. Held from the live set and from Redivis.

## Cross-checks (session 2532)

- Every month's totals equal their parts.
- `eia_world_electricity_annual`, Madagascar, 2024: EIA's hydro 0.900 TWh against JIRAMA's 0.877 TWh from July 2024 to June 2025; JIRAMA's production over those months, 1.964 TWh, is 81% of EIA's national 2.421 TWh, which counts producers off JIRAMA's grid.

## What it does not hold

- Months before July 2024 (earlier TBEs); generation off JIRAMA's grid; prices (MGA).
