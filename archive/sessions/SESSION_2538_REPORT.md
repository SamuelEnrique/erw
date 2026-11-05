# Session 2538 report: Czechia's electricity, a month in 2025 and a year from 2016 (ERU's annual report on the electricity system), the session's own choice, internal

24 October 2026, about 21:32 to 21:40 UTC, on lab-desktop (the data machine), chain 124, unattended. Precheck passed (`runs/c124/pre2538.out`). Model spend USD 0. Pulls: 3 requests of 20 (2 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Why Czechia:** a large European grid the ERW held only in Eurostat's, EIA's and Energy-Charts' international tables; its grid operator's site (www.ceps.cz) is closed (its robots file disallows every path, chain 122). No chain had taken the Energy Regulatory Office (Energeticky regulacni urad, ERU).
- **The host:** eru.gov.cz's robots file closes Drupal's own paths only (read 1003); `/sites/default/files/` is open.
- **ERU's terms:** its home page states "2026 (c) Energeticky regulacni urad" and that its information is given under the Free Access to Information Act (106/1999); no terms of reuse are given (read 1004). The table is **internal** until a ruling. The page also links a "Dataportal", which a later session may read.
- **The source:** ERU's "Rocni zprava o provozu elektrizacni soustavy Ceske republiky 2025" (64 pages, last modified 1 July 2026), fetched once. Three tables are read from its text:
  - 3.1, the sources' balance a month in 2025: gross production by technology (76.368 TWh; nuclear 32.067, steam 30.656, solar 4.375), the plants' own use for electricity and for heat, and net production (71.321 TWh);
  - 3.2, the consumption balance a month: cross-border balance (net imports -7.433 TWh), imports and exports at the transmission and distribution levels, losses (3.162 TWh), consumption by category (households 16.656 TWh), gross and net domestic consumption and the balance difference;
  - 3.3, gross production by technology a year, 2016 to 2025.
- **A new table, `eru_czech_electricity`** (series, 702 rows, 20 entities, P1M and P1Y, `power`), in MWh. Every row's months sum to its year within 1 GWh, every month's technologies to its total within 0.5 GWh, and table 3.3's 2025 equals table 3.1's year. Exports, printed negative, are written positive; net imports keep ERU's sign. The annual rows are named `annual_gross_generation`, so that the year 2025 does not share a key with January 2025. Written by run `20261024T213736Z` under the data lock, validated (exit 0), in coverage, archived (`20261024T213742Z-local`), held from the live set and from Redivis (internal).
- **The report's text after table 3.2's footnote** is a chart's figures run into its legend; the connector stops at the footnote.

## Cross-checks

- Against `eia_world_electricity_annual`'s Czechia for 2024: ERU's gross production 73.904 TWh against EIA's generation 73.664 TWh (99.7%); nuclear 29.696 TWh in both; the cross-border balance -6.659 TWh in both (EIA's net imports). ERU's wind, 0.717 TWh, is EIA's 0.696; ERU's solar, 3.613 TWh, is below EIA's 4.715 (ERU's licensed plants).

## Requests (3 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | eru.gov.cz's robots file | 200 |
| 2 | the annual report 2025 (the fetch) | 200, 0.95 MB |
| 3 | ERU's home page | 200 |

Reads recorded: 1003 and 1004. One web search found the report; it reached no publisher's host.

## Decisions made without you

- **Czechia's regulator as the own choice; internal** until ERU's terms of reuse are known.
- **Exports written positive,** the sign stated in the header.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eru_czech_electricity.py`, `tests/test_session2538.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1003, 1004) and `docs/licenses.md`.
- On the data machine only: `runs/c124/s2538/`, `warehouse/raw/eru_reports/`, `warehouse/output/eru_czech_electricity.csv`.
