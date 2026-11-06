# Cameroon's electricity a year (ARSEL's activity report for 2025)

Energy Research Warehouse (ERW), method note written in session 2541 (chain 124) for a table first written on 24 October 2026 (session 2533).

Tables: `arsel_cameroon_electricity_annual`

## Publisher and address

The Agence de Regulation du Secteur de l'Electricite (ARSEL), Cameroon's electricity regulator, its "Rapport d'activites 2025" (181 pages): `https://arsel-cm.org/wp-content/uploads/2026/09/Rapport-ARSEL-2025.pdf`, listed on its annual reports page. One GET, no key. Source id `arsel:rapport_activites_2025`. Connector: `warehouse/connectors/arsel_cameroon_electricity.py` (session 2533). arsel-cm.org's robots file allows every path with a crawl delay of 10 seconds, which is kept (read 976).

## Vintage and revision

2025 (production and purchases) and 2024 and 2025 (transmission flows), written by run `20261024T205410Z` (the write under the lock, offline), which read the report saved at 2026-10-24T20:48:51Z. `vintage` is its last-modified time, 2026-09-07T14:24:01Z. Each year's report has its own address.

## Shape and variables

Series, 41 rows, 21 entities. `entity` `arsel:cm:<item>`; `unit` MWh (table 19's GWh times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` CM; `node` and `x_label` ARSEL's label.

| `variable` | Items | Figures |
|---|---|---|
| `production` (2025) | hydro, thermal_hfo, thermal_lfo, gas, solar, total | 8.120 TWh (hydro 7.272) |
| `ipp_purchases` (2025, realised) | nhpc, kpdc, dpdc, memve_ele, lom_pangar, aggreko, scatec_solar, mbakaou, total | 3.394 TWh (NHPC 2.071) |
| `transmission_injection` (2024, 2025) | ris_eneo, ris_ipp, ris_total, rin_eneo, rin_total, total | 6.915 and 7.312 TWh |
| `transmission_withdrawal` (2024, 2025) | ris_eneo, ris_hv_clients, ris_ipps, ris_total, rin_eneo, rin_total, total | 6.535 and 6.916 TWh |

RIS and RIN are the Southern and Northern interconnected grids. Totals hold their parts: a sum over entities takes one level.

## Reading the source

- The run stops at once, asking nothing, while `arsel_reports` or arsel-cm.org is paused.
- One request a run (timeout 300 seconds, a pause of 10 seconds); `--offline` reads the saved report.
- **Three blocks, each found by its words and taken from its last place** (the report's list of tables names each table first): "Total energies produites en MWh" to the page's footer; "Tableau 19" to "Tableau 20", its realised column (a plant with "-" realised is not written); "Tableau 21" to the sentence after it ("- Le secteur"), whose figure rows come in a fixed order, a pair of years at a time.
- **Figures:** spaces between thousands, a decimal comma (production, table 19) or point (table 21).
- **Sums:** within 1 MWh for production, 20 MWh for table 19 (given to 10 MWh), 1.5 MWh for table 21, whose own 2025 RIS injection total is 1 MWh above its two parts.
- The run stops, and no file is written, for: a block not found, a row of another form, a label not in the map, a row missing, a key given twice, a total that misses its parts.

Prices, tariffs and fuel costs (FCFA) are not taken. Nothing is filled.

## License

Internal. ARSEL's home page states, after "Copyright 2025 ARSEL", "All rights reserved", and links no terms of reuse (read 978). Verdict (session 2537): needs written permission. Held from the live set and from Redivis.

## Cross-checks (session 2533)

- `eia_world_electricity_annual`, Cameroon, 2024: EIA's generation 7.27 TWh against ARSEL's transmission injections 6.92 TWh (95%); ARSEL's 2025 hydro, 7.27 TWh, is above EIA's estimate of 5.23 TWh, held flat for 2023 and 2024. The report: the independent producers, Nachtigal's hydro plant the largest, gave nearly 47% of the RIS's injections in 2025, against 38% in 2024.

## What it does not hold

- Months (ARSEL's monthly balance minutes, one file a month, are not read); the isolated plants by plant; prices (XAF).
