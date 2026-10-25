# Session 2572 report: Paraguay's electricity balance, 2023 and 2024 (VMME's Balance Energetico Nacional 2024), internal, a third source of the session's own choosing

25 October 2026, about 01:20 to 01:36 UTC, on lab-desktop (the data machine), chain 126, unattended; run before session 2571, so that the records check covers every table of the chain. Precheck passed (`runs/c126/pre2572.out`). Model spend USD 0. Pulls: 9 requests of 20 (8 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **One request broke a closing.** The probe asked ANDE's robots file (www.ande.gov.py, read 1090), though chain 114's session 2406 had closed ANDE (its pages answer with a browser challenge, "not asked again"). I had not read the license record for ANDE before asking. Only the robots file was asked, and it answered as before. From the next request on, each new host was looked up in `license_reads.csv` first.
- **Two hosts tried first, neither taken:**
  - **Chile's INE** (www.ine.gob.cl): no robots file (read 1085); its electricity, gas and water page gives a production index and lists its files by script, with no table address in the page (reads 1086, 1088); its terms are CC BY-SA 4.0 (read 1087). Session 2328 had stopped at its robots address for the same reason (no address known).
  - **Uruguay's www.gub.uy**, where INE Uruguay publishes, reset the connection at its robots file (read 1089); not asked again.
- **The source taken:** Paraguay's Viceministerio de Minas y Energia (VMME), whose robots file closes Joomla's system folders only (read 1091), and its Balance Energetico Nacional 2024 (August 2025, 64 pages, its 2024 figures preliminary), "Cuadro 3: Comparativo balance de electricidad". The ERW held Paraguay only in EIA's international table; ANDE is closed.
- **VMME's terms:** its home page (read 1092) states no terms of reuse, no copyright line and no terms page. **Verdict: needs written permission** (RGGI's precedent). The table is **internal**.
- **A new table, `vmme_paraguay_electricity_annual`** (series, 38 rows, 13 entities, `power`): gross generation by plant type, imports, exports, own use, losses, supply and final consumption by sector for 2023 and 2024. In 2024: gross generation 42,676.2 GWh (Paraguay's share of the binational plants 41,669.1, Acaray 767.7), exports 15,998.6, losses 6,940.1, final consumption 19,444.2 (residential 7,672.2). Exports, own use and losses, printed with a minus sign, are written positive. Every total checked against its parts within 0.2 GWh. Written by run `20261025T013116Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T013126Z-local`), held from the live set and from Redivis; its method note is `docs/methods/vmme_paraguay_electricity_annual.md`, its figures checked against the table, its Method cell set.
- **INE Chile's verdict** is recorded too (read 1087, CC BY-SA 4.0: may be public, as Statistics Estonia's); the ERW holds no table of it.

## Cross-checks

- Against `eia_world_electricity_annual`'s Paraguay: 2023 exports, EIA 30.390 TWh, VMME's 30.390; 2024, EIA's 30.000 (a round estimate) against VMME's 15.999, as final consumption rose 21.6%. EIA's 2023 generation (44.244 TWh) is below VMME's gross 53.042.

## Requests (9 of 20)

| n | What | Outcome |
|---|---|---|
| 1 to 4 | INE Chile's robots address, its index page twice (two addresses, one page), its terms | 200 (a 404 page), 200 |
| 5 | www.gub.uy's robots file | the connection reset |
| 6 | www.ande.gov.py's robots file (in error; see above) | 200 |
| 7, 8 | minasyenergia.mopc.gov.py's robots file and home page | 200 |
| 9 | the Balance Energetico Nacional 2024 (the fetch) | 200, 2.8 MB |

Reads recorded: 1085 to 1092. Tests 205, 207 and 378 pass.

## Decisions made without you

- **Session 2572 run before 2571,** as chain 125 ran its own-choice source before its records session.
- **The method note written here,** not left for a later chain.
- **Exports, own use and losses written positive,** as the ERW's other balances write them.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/vmme_paraguay_electricity.py`, `tests/test_session2572.py`, `docs/methods/vmme_paraguay_electricity_annual.md`, this report.
- Changed: the registration; the metadata files; `docs/coverage.md` (its Method cell); the license record (reads 1085 to 1092, INE Chile's and VMME's verdicts) and `docs/licenses.md`.
- On the data machine only: `runs/c126/s2572/`, `warehouse/raw/vmme_py/`, `warehouse/output/vmme_paraguay_electricity_annual.csv`.
