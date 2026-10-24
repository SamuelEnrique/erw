# Czechia's electricity, a month in 2025 and a year from 2016 (ERU's annual report on the electricity system)

Energy Research Warehouse (ERW), method note written in session 2541 (chain 124) for a table first written on 24 October 2026 (session 2538).

Tables: `eru_czech_electricity`

## Publisher and address

The Energy Regulatory Office (Energeticky regulacni urad, ERU), its "Rocni zprava o provozu elektrizacni soustavy Ceske republiky 2025" (64 pages), tables 3.1, 3.2 and 3.3: `https://eru.gov.cz/sites/default/files/obsah/prilohy/eruelektro2025.pdf`. One GET, no key. Source id `eru:rocni_zprava_elektro_2025`. Connector: `warehouse/connectors/eru_czech_electricity.py` (session 2538). eru.gov.cz's robots file closes Drupal's own paths only (read 1003).

## Vintage and revision

Each month of 2025, and each year 2016 to 2025, written by run `20261024T213736Z` (the write under the lock, offline), which read the report saved at 2026-10-24T21:33:46Z. `vintage` is its last-modified time, 2026-07-01T12:46:52Z. Each year's report has its own address.

## Shape and variables

Series, 702 rows, 20 entities. `entity` `eru:cz:<item>`; `unit` MWh (ERU's GWh times 1,000); `ts_utc` the month's or year's first day; `freq` P1M or P1Y; `geo` CZ; `node` and `x_label` ERU's label.

| `variable` (P1M, 2025) | Items | 2025, TWh |
|---|---|---|
| `gross_generation`, `own_use_power`, `net_generation` | total and eight technologies (nuclear, steam, ccgt, gas_combustion, hydro, pumped_storage, wind, solar) | 76.368, 5.047, 71.321 |
| `own_use_heat` | total, nuclear, steam, ccgt, gas_combustion | 0.877 |
| `net_imports` | total (ERU's sign: import less export) | -7.433 |
| `imports`, `exports` | transmission, distribution (exports written positive) | 17.010 and 24.377 at the transmission level |
| `losses` | total, transmission, distribution | 3.162 |
| `consumption` | total; large_ehv, large_hv, small_business, households, grid_operators, local, pumping; gross_domestic, net_domestic | 58.233 (households 16.656); gross domestic 68.686 |
| `balance_difference` | total | 0.250 |

| `variable` (P1Y, 2016 to 2025) | Items |
|---|---|
| `annual_gross_generation` | total and the eight technologies |

The annual variable has its own name so that the year 2025 shares no key with January 2025. The totals hold their parts; `consumption`'s categories overlap (the gross and net domestic totals include the others), so a sum over entities takes one row.

## Reading the source

- The run stops at once, asking nothing, while `eru_reports` or eru.gov.cz is paused.
- One request a run (timeout 180 seconds); `--offline` reads the saved report. The first 20 pages are read.
- **The pages:** each found by its table's title (3.1 and 3.2 hold an en dash, matched by code).
- **Lines:** a label and 13 figures (12 months and "Celkem") or 10 years; figures with spaces between thousands and one decimal after a comma, negative with a minus. The own-use labels wrap: their figure line begins "(TVS )" or "elektriny na vyrobu tepla (TVS)".
- **Table 3.2** is read to its footnote ("*) zahrnuty"), after which a chart's figures run into its legend. Its two rows repeating table 3.1's own use are not taken twice.
- **Table 3.3:** its second block (the first holds whole GWh), nine rows.
- **Sums:** each row's months to its year within 1 GWh; each month's technologies to its total within 0.5 GWh; each year's technologies to its total within 0.5 GWh; table 3.3's 2025 equal to table 3.1's year within 0.1 GWh.
- The run stops, and no file is written, for: a page not found, a row not in the map, a row missing, a sum missed, a figure of another form, a key given twice.

Nothing is filled.

## License

Internal. ERU's home page states "2026 (c) Energeticky regulacni urad" and that its information is given under the Free Access to Information Act (106/1999); no terms of reuse are given (read 1004). No verdict yet. Held from the live set and from Redivis.

## Cross-checks (session 2538)

- `eia_world_electricity_annual`, Czechia, 2024: ERU's gross production 73.904 TWh against EIA's generation 73.664 TWh (99.7%); nuclear 29.696 TWh in both; the cross-border balance -6.659 TWh in both.

## What it does not hold

- Months before 2025 (earlier reports); the regions' and distribution systems' tables (chapter 4); installed capacity; prices (CZK). ERU's "Dataportal" is not read.
