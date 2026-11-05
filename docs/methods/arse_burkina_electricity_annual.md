# Burkina Faso's electricity production by producer and imports, 2023 and 2024 (ARSE's activity report 2024, table 15)

Energy Research Warehouse (ERW), method note written in session 2569 (chain 126) for a table first written on 25 October 2026 (session 2561).

Tables: `arse_burkina_electricity_annual`

## Publisher and address

The Autorite de Regulation du Secteur de l'Energie (ARSE), its Rapport d'activites 2024, table 15, "Donnees energetiques du secteur en 2023 et 2024" (two pages): `https://www.arse.bf/wp-content/uploads/2025/08/Rapport-dactivite-2024.pdf` (50.0 MB). One GET, no key. Source id `arse_bf:rapport_activite_2024_tableau_15`. Connector: `warehouse/connectors/arse_burkina_electricity.py` (session 2561). www.arse.bf's robots file closes /wp-admin/ and one plugin file only (read 1056).

## Vintage and revision

The years 2023 and 2024, written by run `20261025T001605Z` (the write under the lock, offline), which read the report saved at 2026-10-25T00:11:07Z. `vintage` is its last-modified time, 2025-08-18T16:22:16Z. Each year's report has its own address.

## Shape and variables

Series, 41 rows, 20 entities. `entity` `arse:bf:<item>`; `unit` MWh (ARSE's kWh divided by 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` BF; `node` and `x_label` ARSE's label.

| `variable` | Items | 2024, GWh |
|---|---|---|
| `production` | SONABEL: `sonabel_thermal`, `sonabel_hydro`, `sonabel_solar`, `sonabel_total`; independent producers: `fiess_thermal`, `faso_biogaz`, `private_thermal` (their total), `nagreongo_solar`, `kodeni_solar`, `pa_solar`, `zano_solar`, `essakane_solar` (not on the grid), `zina_solar`, `private_solar` (ARSE's total); `national_total` | national 1,411.4 (SONABEL 943.6, private solar 227.4) |
| `imports` | `htb_cote_divoire`, `htb_ghana`, `hta_ghana`, `hta_togo`, `total` | 1,357.8 |
| `supply` | `total` (produced and imported) | 2,769.2 |

Zina's 2023 cell is "-" and is not written (41 rows, not 42). The totals hold their parts, so a sum over entities takes the parts or the total, not both.

## Reading the source

- The run stops at once, asking nothing, while `arse_bf` or www.arse.bf is paused.
- One request a run (timeout 300 seconds); `--offline` reads the saved report.
- **The pages:** the first holds "Tableau 15:" and "Energie produite", the second "Total imports (HTB+HTA)", the next page or the same.
- **Word positions:** the figures print their thousands with spaces ("688 243 400"), so the text cannot split two cells. A line's words left of x 300 are its label; those from x 300 to 390 its 2023 cell, from x 400 to 490 its 2024 cell; the percentage change beyond is not taken. Each page stops at its line beginning "Source" (the report's prose follows). A label's second line, with no figure, is passed over.
- **Rows** are found by their label's start; COOPEL's row ("Non disponible" both years) and the yield and loss percentages are passed over.
- **Sums** within 1 MWh: SONABEL's three types to its total; FIESS and Faso Biogaz to the private thermal total; SONABEL's, private thermal and private solar totals to the national total; the four interconnections to the imports; national production and imports to the supply. The private solar total is not checked: ARSE's (2024: 227.4 GWh) differs from its listed plants on the grid (246.1 GWh; 265.8 with Essakane's), and is kept as given.
- The run stops, and no file is written, for: a page not found, a mapped row missing or given twice, a row with figures not in the map, a figure of another form, a sum missed.

Nothing is filled.

## License

Internal. ARSE's conditions of use (read 1058): "Toute reproduction, diffusion ou reutilisation, meme partielle, est soumise a l'autorisation prealable ecrite de l'ARSE, sauf mention contraire ou usage strictement personnel et non commercial." (as printed, with its accents). Verdict: needs written permission. Held from the live set and from Redivis.

## Cross-check

EIA's 2023 imports for Burkina Faso (1.583 TWh, `eia_world_electricity_annual`) equal ARSE's 1.582; for 2024, EIA's 1.500 (a round estimate) against ARSE's 1.358. EIA's generation (1.690 and 1.684 TWh) is above ARSE's national production (1.127 and 1.411): EIA's fossil generation would include the mines' own plants, off ARSE's table.
