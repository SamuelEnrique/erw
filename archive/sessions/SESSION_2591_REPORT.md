# Session 2591 report: Curacao's electricity production a year, 2022 to 2024 (CBS Curacao, Aqualectra's figures), public

25 October 2026, about 03:36 to 03:41 UTC, on lab-desktop (the data machine), chain 128, unattended. Precheck passed (`runs/c128/pre2591.out`). Model spend USD 0. Pulls: 5 requests of 15 (4 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **The ERW held no source for Curacao;** EIA keeps it inside "NLDA", the former Netherlands Antilles.
- **The hosts:** www.cbs.cw's robots file closes `/` to a list of named SEO agents only, none an AI agent's, and sets no rule for `*` (read 1159); www.aqualectra.com's certificate fails verification (read 1160).
- **CBS's terms** (read 1162, its Disclaimer): "The statistical data & publications provided by the Central Bureau of Statistics Curacao and published on this website are available free of charge, which means that they may be used, downloaded for personal use or communicated to the public, simply on condition that the source (Central Bureau of Statistics Curacao or CBS Curacao) be mentioned accurately and clearly." (with its cedilla in the record). **Verdict: may be public.** The table is **public**; its release rows are added to `docs/redivis/release-v1/`.
- **The source:** CBS's statistics page "Manufacturing" (read 1161), a table of water and electricity production a year, 2022 to 2024, from Aqualectra; fetched once more through the raw store.
- **A new table, `cbs_curacao_electricity_annual`** (series, 3 rows, `power`): Aqualectra's production 866.9, 916.3 and 982.8 GWh for 2022, 2023 and 2024, in MWh. The water column is not taken. Written by run `20261025T033828Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T033833Z-local`); held from the live set.
- **Small, and said so:** three figures; CBS's page points to "our main website" for earlier years, which a later chain may look for.

## Cross-checks

- Against `eia_world_electricity_annual`'s NLDA (the former Netherlands Antilles, Curacao the largest part), read past its header lines: 910.0, 1,029.7 and 1,006.4 GWh for 2022 to 2024, against Curacao's 866.9, 916.3 and 982.8.

## Requests (5 of 15)

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.cbs.cw's and www.aqualectra.com's robots files | 200, a certificate failure |
| 3, 4 | CBS's Manufacturing page and Disclaimer | 200 |
| 5 | the Manufacturing page again, through the raw store (the fetch) | 200 |

Reads recorded: 1159 to 1162.

## Decisions made without you

- **A three-row table taken,** the only official figures found, public under CBS's terms with Aqualectra cited.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/cbs_curacao_electricity.py`, `tests/test_session2591.py`, this report.
- Changed: the registration; the metadata files; the release package (the table's rows); the license record (reads 1159 to 1162, CBS's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c128/s2591/`, `warehouse/raw/cbs_cw/`, `warehouse/output/cbs_curacao_electricity_annual.csv`.
