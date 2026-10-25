# Session 2567 report: Peru's crude oil, natural gas liquids and natural gas production a month, 2000 to August 2026 (BCRPData, INEI's and MINEM's figures), public, a second source of the session's own choosing

25 October 2026, about 00:58 to 01:06 UTC, on lab-desktop (the data machine), chain 126, unattended. Precheck passed (`runs/c126/pre2567.out`). Model spend USD 0. Pulls: 2 requests of 20 (1 by the probe, 1 by the fetch the connector reads offline).

## Why this source

- **Peru's oil and gas were held only in EIA's international tables.** Peru is an LNG exporter (Peru LNG, fed by Camisea's gas), and its monthly upstream figures are in the same BCRPData that session 2566 read, under the same terms (BCRP's verdict, read 1082: may be public). No chain had taken them.

## Read these first

- **The list** (read 1084): BCRPData's "Produccion minera e hidrocarburos (miles de unidades recuperables)", 11 monthly series from January 2000 to August 2026, updated 23 October 2026; three are hydrocarbons: crude oil (PN01882AM) and natural gas liquids (PN01883AM) in thousand barrels, natural gas (PN01884AM) in million cubic feet; the sources INEI and MINEM.
- **A new table, `bcrp_peru_hydrocarbons_monthly`** (series, 960 rows, 3 entities, `oil;gas`): `production` a month for `bcrp_pe:crude_oil` and `bcrp_pe:natural_gas_liquids` (unit `kbbl`) and `bcrp_pe:natural_gas` (unit `MMcf`), as BCRP gives them, `ts_utc` the month's first day. In 2025: crude oil 16.1 million barrels, natural gas liquids 26.8 million barrels, natural gas 493.8 bcf. Written by run `20261025T010114Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T010119Z-local`), public, its release rows added to `docs/redivis/release-v1/`.
- **Not taken:** the eight mining series of the same list (copper, gold, zinc, silver, molybdenum, lead, iron, tin).

## Cross-checks

- Against `eia_world_oil_gas_annual`'s Peru: crude oil with lease condensate, 2024, 40.631 thousand barrels a day, which over 366 days is 14,871 thousand barrels, BCRP's 14,871; 2019, 52.984 a day, 19,339 over the year, BCRP's 19,339. Natural gas: 2019, EIA 474.1 bcf against BCRP's 474.2; 2024, EIA 478.9 against BCRP's 510.7.

## Errors and fixes

- **The metadata patch conflicted, and I committed it.** The table's rows sort beside session 2566's `bcrp_peru_electricity_monthly` in `coverage.csv`, `sources.csv`, `archive_manifest.csv` and `docs/coverage.md`; `write_table.sh` reported "metadata to the branch exit=1, done, fail=1", and the next commands, chained after it, committed the files with their conflict markers (`3ed06379e`), and `finish_table.sh` failed on them (four problems in the license check). Fixed in the next commit (`1f54b3df5`): each file resolved as the union of both sides (`runs/c124/resolve_union.py`, one block a file, no line on both sides), no row doubled, `finish_table.sh` run again (license check: 563 tables, 0 problems; release check exit 0), tests 378, 2566 and 2567 passing. The table in the main checkout was written once and is not changed.

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | BCRPData's list of the mining and hydrocarbons series | 200 |
| 2 | the API request for the three series (the fetch) | 200, 23.1 kB |

Read recorded: 1084.

## Decisions made without you

- **A second table from BCRPData** rather than another country: the same open terms, figures EIA's agree with, and no chain had them.
- **Units as BCRP gives them** (`kbbl`, `MMcf`), both in the standard's vocabulary for national aggregates.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/bcrp_peru_hydrocarbons.py`, `tests/test_session2567.py`, this report.
- Changed: the registration; the metadata files; the release package (the table's rows); the license record (read 1084) and `docs/licenses.md`.
- On the data machine only: `runs/c126/s2567/`, `warehouse/raw/bcrp_pe/s2567-fetch-1/`, `warehouse/output/bcrp_peru_hydrocarbons_monthly.csv`.
