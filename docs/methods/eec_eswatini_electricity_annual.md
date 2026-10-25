# Eswatini's public grid a financial year (EEC's Integrated Annual Report 2025)

Energy Research Warehouse (ERW), method note written in session 2569 (chain 126) for a table first written on 25 October 2026 (session 2560).

Tables: `eec_eswatini_electricity_annual`

## Publisher and address

The Eswatini Electricity Company (EEC), its Integrated Annual Report 2025 (157 pages), the page "Highlights and at-a-glance metrics": `https://eec.co.sz/aboutus/reports/docs/EEC_IAR25.pdf`. One GET, no key. Source id `eec:integrated_annual_report_2025`. Connector: `warehouse/connectors/eec_eswatini_electricity.py` (session 2560). eec.co.sz and www.eec.co.sz have no robots file (reads 1048 and 1051).

## Vintage and revision

The financial years ended 31 March 2025 and 2024, written by run `20261025T000805Z` (the write under the lock, offline), which read the report saved at 2026-10-25T00:05:06Z. `vintage` is its last-modified time, 2025-12-01T09:40:19Z. Each year's report has its own address.

## Shape and variables

Series, 10 rows, 1 entity. `entity` `eec:sz:total` (EEC's system); `unit` MWh (EEC's GWh times 1,000); `ts_utc` the financial year's first day (1 April); `freq` P1Y; `geo` SZ; `node` EEC's label; `x_fiscal_year` the year (2024/25, 2023/24).

| `variable` | EEC's label | 2024/25, GWh | 2023/24, GWh |
|---|---|---|---|
| `sold` | Energy Sold | 1,181 | 1,173 |
| `sent_out` | Units Sent Out (Total Supply) | 1,366 | 1,356 |
| `internal_generation` | Internal Generation | 281 | 319 |
| `imports` | Electricity Imports | 978.6 | 962.1 |
| `purchases_ubombo_sugar` | Local Generation from Ubombo Sugar Ltd (USL) | 65.9 | 61.4 |

## Reading the source

- The run stops at once, asking nothing, while `eec_sz` or eec.co.sz is paused.
- One request a run; `--offline` reads the saved report.
- **The page** is found by its title; its text runs its columns together, so its five figures ("<figure> GWh") and their five figures for the year before ("(2024: <figure> GWh)") are read in the order of their labels, which must stand on the page in that order. Any other count or order stops the run.
- The percentages (system losses 13.54%, the shares of supply) and the financial figures are not taken.

Nothing is filled.

## License

Internal. EEC's terms of use (read 1053): "Reproduction is prohibited other than in accordance with the copyright notice, which forms part of these terms and conditions"; the notice reads "(c) 2026 Eswatini Electricity Company. All rights reserved." (read 1052). Verdict: needs written permission. Held from the live set and from Redivis.

## Cross-check

EIA's 2024 imports for Eswatini (1.044 TWh, `eia_world_electricity_annual`) against EEC's 0.979 TWh for 2024/25; EIA's generation (0.604 TWh) counts the sugar mills' own generation.
