# Session 2589 report: Mali's electricity, not taken (INSTAT's one energy table mislabels its units and holds EDM's figures; EDM's and CREE's hosts do not resolve)

25 October 2026, about 03:32 to 03:35 UTC, on lab-desktop (the data machine), chain 128, unattended. Precheck passed (`runs/c128/pre2589.out`). Model spend USD 0. Pulls: 7 requests of 15 (6 by the probe, 1 by a fetch). No table.

## Read these first

- **The ERW held no source for Mali** but EIA's international table.
- **EDM SA** (the utility) and **CREE** (the regulator): www.edm-sa.com.ml and www.creemali.ml do not resolve (reads 1148, 1149).
- **INSTAT:** its robots file closes its admin login only (read 1147); its home page reads "Copyright (c) 2020 / Institut National de la Statistique - INSTAT" and links an open data licence (reads 1150, 1151): a worldwide, free licence to use, copy, adapt and distribute its data, commercially or not, with the source named, which "ne s'etend pas aux donnees ... de tiers". Its verdict is session 2593's.
- **The Annuaire statistique du Mali 2024** (115 pages, last modified 29 June 2026, fetched once, from the list of annual publications, read 1152) has one energy table, table 92, "Statistiques de l'Energie de 2020 a 2024", every row sourced to EDM SA. Its labels correct their own units ("Production brute d'electricite EDM SA (Mwh) au lieu de (Millier de Kwh)"); its sales rows give one series in thousands of kWh and another, under a label of thousands of kWh or MWh, in kWh (1,976,227,536 for 2020); its subscriber counts run their thousands' spaces together with the next year's. **Not taken:** five production figures (2.60 TWh in 2020 to 2.84 in 2023, 1.84 in 2024) from a table whose units its own labels correct, and whose figures are EDM's, outside INSTAT's licence, would rest on readings a session should not make alone.

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | www.instat-mali.org's, www.edm-sa.com.ml's and www.creemali.ml's robots files | 200, no such name, no such name |
| 4 to 6 | INSTAT's home page, its open data licence, its annual publications | 200 |
| 7 | the Annuaire statistique 2024 (a fetch) | 200, 2.2 MB |

Reads recorded: 1147 to 1152.

## Decisions made without you

- **Mali not taken,** table 92's units and source as above.

## For Samuel's ruling

- None new. (Should a later chain take EDM's production from INSTAT's table 92 with its labels' corrected unit? The figures are EDM's.)

## Files

- Changed: the license record (reads 1147 to 1152) and `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c128/s2589/`, `warehouse/raw/instat_ml/`.
