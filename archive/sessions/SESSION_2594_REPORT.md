# Session 2594 report: Jersey's electricity balance, 2023 to 2025 (the Government of Jersey's Energy Trends 2025), internal, a source of the session's own choosing

25 October 2026, about 03:46 to 03:52 UTC, on lab-desktop (the data machine), chain 128, unattended. Precheck passed (`runs/c128/pre2594.out`). Model spend USD 0. Pulls: 5 requests of 20 (4 by the probe, 1 by the fetch the connector reads offline).

## Why this source

- **The ERW held Jersey in no table** (EIA's world table has no Jersey), and its electricity is a cross-border case: 93% of its public supply comes by submarine cable from France. No chain had taken gov.je (the license record and the queue files read first).

## Read these first

- **The hosts:** www.gov.je's robots file names `*` with no rule (read 1163); opendata.gov.je's closes its API and asks a crawl delay of 10 seconds (read 1165), kept; its dataset search finds no energy dataset (read 1166), so the Open Government Licence - Jersey under which its datasets are published does not reach these figures.
- **The terms** (read 1164, gov.je's Terms and conditions): "Copyright protected material may be reproduced free of charge in any format or medium for research, private study or for internal circulation within an organisation." Public republication is not among those purposes. **Verdict: needs written permission** (the cautious reading). The table is **internal**.
- **The source:** Energy Trends 2025 (25 pages, last modified 12 August 2026, produced by the Cabinet Office since the 2024 report, Statistics Jersey before), its energy balances in tonnes of oil equivalent: Table 5 for 2025 and Appendix Tables A3 and A5 for 2023 and 2024 (updated). Only the electricity column is taken.
- **A new table, `je_jersey_electricity_annual`** (series, 45 rows, 15 entities, `power`): the electricity balance's 15 rows for each of the three years. In 2025: net imports 609.6 GWh, on-island production 51.6, primary supply 661.1, own use and losses 45.5, final consumption 616.5 (residential 344.7, commercial 260.3). In MWh at 11.63 MWh a toe, the factor the report itself uses ("2.4 GWh (209 toe)"); each figure carries its toe's rounding, at most 5.8 MWh, and `x_toe` keeps the toe as printed. Each balance's supply, demand and sectors checked within 1 toe. Written by run `20261025T035028Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T035034Z-local`), held from the live set and from Redivis (internal).
- **Not taken:** the liquid fuels', gas and total columns; the report's charts of longer trends.

## Cross-checks

- EIA's world table holds no Jersey. Within the report: 2025's net imports, 52,415 toe, are 93% of its primary supply (56,848 toe), as the report's text says.

## Requests (5 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.je's robots file | 200 |
| 2 | Energy Trends 2025 (the fetch) | 200, 684.8 kB |
| 3 | gov.je's Terms and conditions | 200 |
| 4, 5 | opendata.gov.je's robots file and dataset search (after the crawl delay) | 200 |

Reads recorded: 1163 to 1166.

## Decisions made without you

- **The toe stated in MWh** at the report's own factor, the toe kept beside it.
- **Internal** under gov.je's research-and-private-study clause.

## For Samuel's ruling

- **Whether gov.je's clause ("for research, private study or for internal circulation within an organisation") lets the ERW publish the table.** Held internal until then.

## Files

- New: `warehouse/connectors/je_jersey_electricity.py`, `tests/test_session2594.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1163 to 1166, the Government of Jersey's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c128/s2594/`, `warehouse/raw/statsje/`, `warehouse/output/je_jersey_electricity_annual.csv`.
