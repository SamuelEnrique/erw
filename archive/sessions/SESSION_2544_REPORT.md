# Session 2544 report: Northern Ireland's electricity a month (DfE's Electricity Consumption and Renewable Generation), the third own choice, public

24 October 2026, about 21:55 to 22:03 UTC, on lab-desktop (the data machine), chain 124, unattended. Precheck passed (`runs/c124/pre2544.out`). Model spend USD 0. Pulls: 6 requests of 20 (5 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Why Northern Ireland:** a grid the ERW held only inside DESNZ's United Kingdom tables (and apart from Elexon's Great Britain), with a public licence. Two other own choices were looked at first and dropped: Romania's statistics institute publishes its electricity balance as year-to-date totals in a press release, not a month at a time; Greece's IPTO had no file a search could find.
- **This session ran before session 2541's upload,** so that its public table went into the same draft (the chain's order otherwise kept).
- **The hosts:** www.economy-ni.gov.uk's robots file closes Drupal's own paths and asks ClaudeBot by name for a crawl delay of 5 seconds, which was kept (read 1009). DfE's publication page (read 1010) gives one document, an HTML report on datavis.nisra.gov.uk, whose robots address serves an "Unavailable" page (read 1011).
- **DfE's terms** (read 1013, its Crown copyright page): "You may use and re-use the information featured on this website (not including logos) free of charge in any format or medium, under the terms of the Open Government Licence". **Verdict: may be public,** sold or not. The table is **public**, its header acknowledging DfE and the licence.
- **The source:** the report page (read 1012; 5.2 MB, fetched once for the connector, last modified 3 September 2026) writes each figure's data into the page as a base64 CSV link. Four monthly figures are taken, each found by its header: renewables by type (6), the two generation totals (7), fossil fuels (8), and imports, exports and net imports (9), January 2018 to June 2026. The CSVs are UTF-16 with one-byte line ends; their zero bytes are dropped.
- **A new table, `dfe_ni_electricity_monthly`** (series, 1,326 rows, 9 entities, `power`), in MWh. Each month's types sum to the renewable total and its fuels to the non-renewable total within 2 GWh, and imports less exports to net imports within 1 GWh. Exports are written positive. Written by run `20261024T215950Z` under the data lock, validated (exit 0), in coverage, archived (`20261024T215954Z-local`), held from the live set; public, so added to the release package and uploaded to the Stanford draft by session 2541.
- **A method note** (`docs/methods/dfe_ni_electricity_monthly.md`), checked against the table, with its Method cell; the package's tables and the site's records rebuilt for it (session 2543's check had run before it).

## Cross-checks

- April 2025 to March 2026 against DfE's headline for the year: renewable generation 4,264 GWh in both; non-renewable 3,938 GWh, the report's rolling figure for March 2026; net imports 615 GWh against the headline's 616 (each month rounded).

## Requests (6 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.economy-ni.gov.uk's robots file | 200 |
| 2 | DfE's publication page | 200 |
| 3 | datavis.nisra.gov.uk's robots address | 200, an "Unavailable" page |
| 4 | the report page | 200, 5.2 MB |
| 5 | DfE's Crown copyright page | 200 |
| 6 | the report page (the fetch) | 200, 5.2 MB |

Reads recorded: 1009 to 1013. Three web searches found the report and looked for Romania's and Greece's files; they reached no publisher's host.

## Decisions made without you

- **Northern Ireland as the third own choice; public** under the Open Government Licence.
- **The rolling twelve-month figures not taken;** the monthly figures sum to them.
- **This session before session 2541's upload.**

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/dfe_ni_electricity.py`, `tests/test_session2544.py`, `docs/methods/dfe_ni_electricity_monthly.md`, this report.
- Changed: the registration; the metadata files; the license record (reads 1009 to 1013, DfE's verdict) and `docs/licenses.md`; `docs/redivis/release-v1/`; the package's tables and the site's records.
- On the data machine only: `runs/c124/s2544/`, `warehouse/raw/dfe_ni_electricity/`, `warehouse/output/dfe_ni_electricity_monthly.csv`.
