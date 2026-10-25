# Session 2561 report: Burkina Faso's electricity, production by producer and imports, 2023 and 2024 (ARSE's activity report 2024), internal

25 October 2026, about 00:09 to 00:18 UTC, on lab-desktop (the data machine), the second session of `queue/done/126-day-26-november-data-eswatini-burkina-faso-maldives-suriname.md`, unattended. Precheck passed. Model spend USD 0. Pulls: 6 requests of 15 (5 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **The ERW held no source for Burkina Faso** but EIA's international table.
- **The hosts:** www.insd.bf's robots file is Drupal's default (read 1054); www.sonabel.bf did not answer (read 1055); www.arse.bf's robots file closes /wp-admin/ and one plugin file only (read 1056).
- **ARSE's conditions of use** (read 1058): "Toute reproduction, diffusion ou réutilisation, même partielle, est soumise à l'autorisation préalable écrite de l'ARSE, sauf mention contraire ou usage strictement personnel et non commercial." **Verdict: needs written permission.** The table is **internal**.
- **The source:** ARSE's Rapport d'activités 2024 (50.0 MB), fetched once; its table 15, "Données énergétiques du secteur en 2023 et 2024", runs over two pages. Its kWh figures print their thousands with spaces, so the text cannot split two cells: the pages' words are read by their place (the label left of x 300, the 2023 cell from x 300 to 390, the 2024 cell from x 400 to 490), and each page stops at the table's source line.
- **A new table, `arse_burkina_electricity_annual`** (series, 41 rows, 20 entities, `power`): production by producer and type (SONABEL's thermal, hydro and solar; FIESS, Faso Biogaz and seven solar plants; the totals), imports by interconnection (HTB from Côte d'Ivoire and Ghana, HTA from Ghana and Togo) and the supply. In 2024: national production 1,411.4 GWh (2023: 1,127.4), of which SONABEL 943.6 and private solar 227.4; imports 1,357.8 (2023: 1,582.2); supply 2,769.2 (2023: 2,709.6). In MWh (ARSE's kWh divided by 1,000), `ts_utc` 1 January. Every total but one checked against its parts within 1 MWh. Written by run `20261025T001605Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T001613Z-local`), held from the live set and from Redivis (internal).
- **Not taken:** COOPEL's row ("Non disponible" both years), Zina's 2023 cell ("-"), the yield and loss percentages, and the year's percentage changes.

## Cross-checks

- Against `eia_world_electricity_annual`'s Burkina Faso: EIA's 2023 imports, 1,582.7 GWh, against ARSE's 1,582.2 (the same figure); for 2024 EIA's 1,500.0 (a round estimate) against ARSE's 1,357.8.
- EIA's generation, 1,689.8 GWh in 2023 and 1,684.1 in 2024, is above ARSE's national production (1,127.4 and 1,411.4): EIA's 1,419.8 and 1,400.0 of fossil generation would include the mines' own plants, off ARSE's table.
- ARSE's private solar total (2024: 227.4 GWh) differs from the sum of its listed plants on the grid (246.1 GWh; 265.8 with Essakane's, off the grid): kept as ARSE gives it, not checked, said in the table's header.

## Requests (6 of 15)

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.insd.bf's and www.sonabel.bf's robots files | 200, a timeout |
| 3 | www.arse.bf's robots file | 200 |
| 4, 5 | ARSE's home page and conditions of use | 200 |
| 6 | the Rapport d'activités 2024 (the fetch) | 200, 50.0 MB |

Reads recorded: 1054 to 1058.

## Decisions made without you

- **The table read by its words' places,** as its figures cannot be split from the text.
- **The private solar total kept unchecked,** ARSE's own figure, with the difference written in the header.
- **Internal** under ARSE's conditions of use.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/arse_burkina_electricity.py`, `tests/test_session2561.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1054 to 1058, ARSE's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c126/s2561/`, `warehouse/raw/arse_bf/`, `warehouse/output/arse_burkina_electricity_annual.csv`.
