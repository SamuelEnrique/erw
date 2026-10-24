# Mozambique's electricity balance, a year (MIREME's Energy Statistical Report, table 3.2.2)

Energy Research Warehouse (ERW), method note written in session 2485 (chain 120) for a table first written on 24 October 2026 (session 2477).

Tables: `mireme_mozambique_electricity_annual`

## Publisher and address

The Ministry of Mineral Resources and Energy of Mozambique (MIREME), its "Relatório Estatístico de Energia 2023 - 2024" (5th edition, 89 pages), table "Quadro 3.2.2 Balanço de Electricidade (MWh), 2020-2024": `https://mireme.gov.mz/wp-content/uploads/2026/02/Relatorio-Estatistico-de-Energia_2024-1.pdf`. One GET, no key. Source id `mireme:relatorio_estatistico_energia`. Connector: `warehouse/connectors/mireme_mozambique_electricity.py` (session 2477). mireme.gov.mz's robots file disallows nothing (read 815). The report gathers the figures of EDM and the other producers (EDM's own site closes `/novo/` only, read 814).

## Vintage and revision

2020 to 2024, written by run `20261024T132540Z` (the write under the lock, offline), which read the report saved at 2026-10-24T13:21:47Z (`retrieved_at`). `vintage` is its last-modified time, 2026-02-04T11:13:49Z. A saved report is reused unless `--fresh`; the next edition will have its own address.

## Shape and variables

Series, 107 rows, 12 entities.

- `variable`: the balance's section.
  - `generation`: total and by source: hydro, natural gas, diesel, bagasse and solar.
  - `imports`, `exports` and `primary_supply`: totals.
  - `own_use`: total and by source.
  - `losses`: total, transport and distribution.
  - `final_consumption`: total, industry, residential, commerce and public services, and agriculture and forest.
- `entity`: `mireme:mz:<item>` (`total` for a section's own row).
- `unit` MWh, as MIREME gives it. The table's parentheses mark a quantity subtracted in the balance and are not a sign: every value is a quantity, and none is negative. `ts_utc` the year's 1 January; `freq` P1Y; `geo` MZ.
- `node` and `x_label`: the row as MIREME labels it (Portuguese / English).

A section's total holds its items: a sum takes one level.

| TWh | 2020 | 2022 | 2024 |
|---|---|---|---|
| Generation | 18.94 | 19.40 | 19.46 |
| Imports | 8.11 | 8.25 | 7.59 |
| Exports | 11.49 | 11.46 | 10.68 |
| Final consumption | 11.75 | 12.34 | 13.32 |

## Reading the source

- The run stops at once, asking nothing, while `mireme_mozambique_energy` or mireme.gov.mz is paused.
- One request a run (timeout 180 seconds); `--offline` reads the saved report.
- **Finding the table:** the page that names "Quadro 3.2.2" and holds the row of the five years. The report's list of tables names it too, without the header.
- **Reading the figures:** by their position. The five years' headings give the columns, and each figure's digit groups (thousands written with spaces) are joined within their column, so a figure is never split or merged by its spaces. The variation column (2024/2020) is not taken.
- **Cells without a row:**
  - a cell marked "..." (not available);
  - a cell out of the form of thousands, counted in the header (one: 2022's solar, printed "69 7017").
- The run stops, and no file is written, for any of these:
  - no page with the table and its header;
  - a row not in the map (`SECTIONS`, `SINGLE`, `ITEMS`);
  - an item before its section;
  - a key given twice.

Nothing is filled.

## License

Internal, not settled. The report's technical sheet is headed "Copyright" and grants no reuse. The site states no terms (read 816). No verdict is written: the sheet is not a page in the record. The table is held from the Redivis storage and the live set until a ruling or MIREME's consent.

## Cross-checks (session 2477)

- Generation's sources over its total: 0.9999 to 1.000, and 0.9964 in 2022 (the solar cell left out).
- Primary supply over `owid_ember_electricity_annual`'s demand for Mozambique: 0.989 to 0.997 in 2020 to 2022, 1.069 in 2023, 1.099 in 2024.

## What it does not hold

- Years before 2020 (earlier reports, other addresses); the report's monthly and quarterly tables (generation by source a month, imports by country a quarter); capacity; prices (MZN).
