# Session 2533 report: Cameroon's electricity (ARSEL's activity report for 2025), internal

24 October 2026, about 20:44 to 20:56 UTC, on lab-desktop (the data machine), chain 124, unattended. Precheck passed (`runs/c124/pre2533.out`). Model spend USD 0. Pulls: 11 requests of 15 (7 by the probe, 4 by fetches, one of them answered 404).

## Read these first

- **The ERW held no Cameroonian source** (`sources.csv`, the connectors and the queue searched for Cameroon, Cameroun, ARSEL and ENEO): only EIA's and OWID's international tables name it.
- **The hosts:** arsel-cm.org's robots file allows every path with a crawl delay of 10 seconds, which was kept (read 976); ins-cameroun.cm's closes `/wp-admin/` only (read 977). Neither names an AI agent.
- **ARSEL's terms:** its home page states "Copyright 2025 ARSEL, All rights reserved"; its "Mentions legales" is a label, not a link, and no terms of reuse are given (read 978). The table is **internal** until a ruling; session 2537's round reads ARSEL.
- **What ARSEL publishes:** its activities page (read 979) leads to twelve monthly minutes validating 2025's transmission balances (read 980; one, December 2025, was fetched: a meter-by-meter balance of one month, 21 pages), to an "energies produites" PDF that is a Power BI export holding only an image (read 981; fetched), and to its annual reports (read 982). A first address for the 2024 activity report, taken from a web search, answered 404; the annual reports page gives the right ones.
- **The source:** ARSEL's "Rapport d'activites 2025" (181 pages, 26.9 MB, last modified 7 September 2026), fetched once. Three blocks are read from its text:
  - the energy produced in 2025 by source (page 14 of the report): hydro 7,272,387 MWh, thermal HFO 66,681, thermal LFO 153,942, gas 559,669, solar 67,237; total 8,119,916 MWh;
  - table 19, the energy bought from each independent producer in 2025, the realised column (3,394.30 GWh in all, Nachtigal's NHPC 2,070.68); three plants with none bought are not written;
  - table 21, the energy injected into and withdrawn from the transmission network in 2024 and 2025, for the Southern grid (RIS: injections by ENEO and by the independent producers; withdrawals by ENEO, by high-voltage customers and at the producers' own sites) and the Northern grid (RIN: ENEO only), with each grid's and the national totals: injections 6.915 TWh in 2024 and 7.312 TWh in 2025.
- **A new table, `arsel_cameroon_electricity_annual`** (series, 41 rows, `power`). Every total equals its parts: within 1 MWh for production, 20 MWh for table 19 (given to 10 MWh), 1.5 MWh for table 21, where ARSEL's own 2025 RIS injection total is 1 MWh above the sum of its two parts. Written by run `20261024T205410Z` under the data lock, validated (exit 0), in coverage, archived (`20261024T205440Z-local`), held from the live set and from Redivis (internal). Prices, tariffs and fuel costs (FCFA) are not taken.

## Cross-checks

- Against `eia_world_electricity_annual`'s Cameroon: EIA's 2024 generation is 7.27 TWh, and ARSEL's 2024 transmission injections are 6.92 TWh (95%; the isolated plants and the distribution-level producers are not on the transmission network). ARSEL's 2025 production, 8.12 TWh, is 12% above EIA's 2024; its hydro, 7.27 TWh, is above EIA's estimate of 5.23 TWh, which EIA holds flat for 2023 and 2024. The report's own words: the independent producers, Nachtigal's hydro plant the largest, now give nearly 47% of the RIS's injections, against 38% in 2024. `owid_ember_electricity_annual` holds Cameroon's demand only (7.32 TWh in 2024).
- No row twice in `sources.csv`, `coverage.csv`, `archive_manifest.csv` or `docs/coverage.md`.

## Requests (11 of 15)

| n | What | Outcome |
|---|---|---|
| 1, 2 | arsel-cm.org and ins-cameroun.cm robots files | 200, 200 |
| 3 | ARSEL's home page | 200 |
| 4 | the 2024 activity report at a searched address (a fetch) | 404 |
| 5 | the activities page | 200 |
| 6 | the monthly energy balances page | 200 |
| 7 | December 2025's balance minutes (a fetch) | 200, 2.2 MB |
| 8 | the energies produced page | 200 |
| 9 | the energies produced PDF (a fetch) | 200, an image |
| 10 | the annual reports page | 200 |
| 11 | the activity report for 2025 (the fetch) | 200, 26.9 MB |

Reads recorded: 976 to 982 (the probe's seven). Three web searches found ARSEL's reports; they reached no publisher's host.

## Decisions made without you

- **The annual report rather than the monthly minutes:** twelve minutes would pass the session's ceiling, and one or a few months would be a partial year.
- **Internal** under ARSEL's "All rights reserved", until a ruling.
- **Table 21's tolerance 1.5 MWh,** for ARSEL's own 1 MWh difference; the figures are as printed.

## For Samuel's ruling

- None new (ARSEL's terms go to session 2537's round).

## Files

- New: `warehouse/connectors/arsel_cameroon_electricity.py`, `tests/test_session2533.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 976 to 982) and `docs/licenses.md`.
- On the data machine only: `runs/c124/s2533/`, `warehouse/raw/arsel_reports/`, `warehouse/raw/arsel_bilan/`, `warehouse/output/arsel_cameroon_electricity_annual.csv`.
