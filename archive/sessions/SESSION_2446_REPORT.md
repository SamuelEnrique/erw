# Session 2446 report: a third source of the session's own choosing (Brazil's monthly electricity consumption by state, class and sector, EPE), public

24 October 2026, from 11:52 UTC to 11:59 UTC, on lab-desktop (the data machine), chain 117, unattended, before session 2443 so that 2443's notes and draft cover every table of the chain. Precheck passed (`runs/c117/pre2446.out`). Model spend USD 0. Pulls: 3 requests of 20 (2 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Why this source:** the ERW held Brazil's register of generation plants (ANEEL) and the grid's operation (ONS), but not its consumption. EPE's yearbook raw data give it by state, by class (captive customers of the distributors, or free customers of the open market) and by sector, month by month. No chain or connector named EPE (main and chains 114's and 115's branches searched).
- **www.epe.gov.br's robots file** closes its system paths, `.aspx` pages and restricted areas only, and names no AI agent (read 727).
- **A new table, `epe_brazil_consumption_monthly`** (series, 105,032 rows, 354 series, `power`): consumption (MWh) and consumers (count) by state, class and sector, January 2011 to December 2025.
  - It is summed from EPE's 423,751 leaf rows over system, the sector's lower levels (the low-income subclasses among them), voltage and consumption band. `x_rows` counts the rows summed.
  - Written, validated (0 errors, 0 warnings), archived, and held from the Redivis storage and the live set like the chain's other tables.
- **Public, under CC BY 4.0.** The open data page's footer (read 728): "Todo o conteúdo deste site está publicado sob a licença Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)". `license_verdicts.csv` gains EPE, "may be public".
- **Five negative sums** are EPE's own figures, kept as given. Four are consumption (the least, -4,093.6 MWh, Federal District captive industrial, January 2025) and one a consumer count (-71, Amapá captive public service, April 2024). They are likely corrections of earlier months; EPE does not say.

## Cross-checks

- Consumption, TWh a year: 433.0 in 2011, 475.7 in 2020, 561.6 in 2024 and 566.7 in 2025.
- Over `owid_ember_electricity_annual`'s demand for Brazil: 0.728 to 0.763. Ember's demand counts losses (high in Brazil) and self-supplied generation, which consumption billed by class does not.
- The free market's share of consumption rose from 0.26 (2011) to 0.448 (2025).

## Requests (3 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.epe.gov.br/robots.txt | 200 |
| 2 | the yearbook's open data page | 200: the raw data, its dictionary, CC BY 4.0 |
| 3 | Dados brutos.xlsx (the fetch) | 200, 24.6 MB, last modified 3 June 2026 |

Reads recorded: 727 and 728 (on this branch). One web search found the yearbook's pages; it reached no publisher's host.

## Decisions made without you

- **Public** under EPE's CC BY 4.0.
- **EPE's leaves summed** to state, class and sector, rather than written as 423,751 rows of voltage and band.
- **Negative figures kept** as EPE gives them.
- **This session run before session 2443,** so that one draft carries all of the chain's public tables.

## For Samuel's ruling

- None.

## Files

- New: `warehouse/connectors/epe_brazil_electricity.py`, `tests/test_session2446.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`;
  - the license record (reads 727 and 728, EPE's verdict) and `docs/redivis/release-v1/` (the table's rows).
- On the data machine only: `runs/c117/s2446/`, `warehouse/raw/epe_brazil_electricity/`, `warehouse/output/epe_brazil_consumption_monthly.csv`.
