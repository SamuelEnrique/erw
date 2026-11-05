# Session 2563 report: Suriname's electricity, EBS's demand, generation and capacity and Staatsolie's generation (ABS's Environment Statistics 2024), public

25 October 2026, about 00:26 to 00:39 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/126-day-26-november-data-eswatini-burkina-faso-maldives-suriname.md`, unattended. Precheck passed (`runs/c126/pre2563.out`). Model spend USD 0. Pulls: 5 requests of 15 (4 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **One request came early.** statistics-suriname.org's robots file asks a crawl delay of 30 seconds. The fetch of the publication went out at about 00:27:20 UTC, about 24 seconds after the request for ABS's home page (00:26:56), not 30. Three requests were made to the host in all (the robots file, the home page, the publication), the others spaced by more than 30 seconds. No further request was made to it; the connector reads the saved file.
- **The ERW held no source for Suriname** but EIA's international table.
- **The hosts:** statistics-suriname.org's robots file closes nothing and asks the crawl delay (read 1066); www.nvebs.com's (EBS) closes /admin and three other paths (read 1067); EBS's home page (read 1068) links its general terms and a disclaimer, not read, as ABS's publication carries EBS's figures.
- **ABS's terms** (read 1069, the home page's footer): "Except where otherwise noted, content on this site is licensed under a Creative Commons Attribution 4.0 International license." The publication notes no other license (its colophon: "Copyright December 2024 Algemeen Bureau voor de Statistiek (ABS)"). **Verdict: may be public.** The table is **public**; its release rows are added to `docs/redivis/release-v1/` (held from the dataset while the account's storage is full, as the other public tables of these chains).
- **The source:** ABS's eleventh Milieustatistieken Publicatie / Environment Statistics Publication (December 2024, 452 pages, 23.4 MB, last modified 31 December 2024), chapter 7: tables 7.1 (EBS's installed and available capacity, MW, 2019 to 2021), 7.4 (EBS's electricity demand by category, kWh, 2019 to 2023), 7.8 (EBS's net generation and net consumption, billion kWh, 2019 to 2023) and 7.9 (Staatsolie's generation: the Afobaka hydro plant and the Tout Lui Faut thermal plant for EBS, its back-up plant in Saramacca, 2019 to 2023).
- **A new table, `abs_suriname_electricity_annual`** (series, 56 rows, 9 entities, `power`). In 2023: EBS's net generation 1,470 GWh and net consumption 1,377; demand 1,408.1 GWh (residential 707.2, industrial 484.4, commercial 190.8, other 25.7); Afobaka 937 GWh, Tout Lui Faut 327 GWh, the back-up 218 MWh. Installed capacity 247.4 MW in 2021 (available 192.7). In MWh and MW, `ts_utc` 1 January. Written by run `20261025T003517Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T003649Z-local`).
- **Table 7.8's decimals:** its billions print a comma for 2019 to 2021 ("1,366") and a point for 2022 and 2023 ("1.377"). Both are read as the decimal: every figure must fall between 0.5 and 5 billion kWh, and net consumption below net generation, or the run stops.
- **Not taken:** the connections (tables 7.2 and 7.3), the sales by district (7.5: its total, 132.7 GWh in 2023, does not agree with table 7.4's 1,408.1 GWh, and its unit cannot be settled from the page), the prices (7.6, SRD), and 7.8's capacity in GW (7.1 gives it in MW).

## Cross-checks

- Against `eia_world_electricity_annual`'s Suriname for 2023: EIA's hydro generation 900 GWh against Afobaka's 937; EIA's total generation 1,731.5 GWh and consumption 1,486.3 against EBS's net generation 1,470 and net consumption 1,377 (EIA's country covers more than EBS's grid: the interior's diesel sets and the mines). EIA's capacity of 575.9 MW in 2023 against EBS's installed 247.4 MW in 2021 (EBS's figure excludes the plants it buys from).
- Within the table: Afobaka and Tout Lui Faut made 1,264 GWh of EBS's 1,470 GWh net generation in 2023.

## Requests (5 of 15)

| n | What | Outcome |
|---|---|---|
| 1, 2 | statistics-suriname.org's and www.nvebs.com's robots files | 200, 200 |
| 3 | EBS's home page | 200 |
| 4 | ABS's home page | 200 |
| 5 | the Environment Statistics publication (the fetch) | 200, 23.4 MB (about 24 seconds after request 4: see above) |

Reads recorded: 1066 to 1069.

## Errors and fixes

- The crawl delay was missed by about 6 seconds on the fetch: the probe and the fetch ran in one command without a wait between them. Every request to a host with a crawl delay now waits for it in the same command, before the request.

## Decisions made without you

- **Public under ABS's CC BY 4.0,** the publication noting no other license and the tables' sources (EBS, Staatsolie) cited.
- **Table 7.8's comma and point both read as the decimal,** with a range check.
- **Table 7.5 not taken,** its total disagreeing with table 7.4's.

## For Samuel's ruling

- None new. (Whether ABS's licence covers figures it republishes from EBS and Staatsolie is the same question as for the other statistics offices' tables of these chains; the table is public on ABS's licence, which names no exception.)

## Files

- New: `warehouse/connectors/abs_suriname_electricity.py`, `tests/test_session2563.py`, this report.
- Changed: the registration; the metadata files; the release package (`docs/redivis/release-v1/`: the table's rows); the license record (reads 1066 to 1069, ABS's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c126/s2563/`, `warehouse/raw/abs_sr/`, `warehouse/output/abs_suriname_electricity_annual.csv`.
