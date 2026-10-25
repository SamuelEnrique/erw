# Session 2725 report: Nunavut's electricity not taken (Qulliq Energy publishes its figures only in annual reports)

25 October 2026, about 19:24 to 19:26 UTC, on lab-desktop (the data machine), chain 137, unattended. Precheck passed (`runs/c137/pre2725.out`). Model spend USD 0. Pulls: 2 requests of 15, both by the probe; one web search.

## Read these first

- **The ERW held Nunavut only in Statistics Canada's tables;** no source or read named Qulliq Energy.
- **Qulliq Energy** (www.qec.nu.ca):
  - Its robots file holds Drupal's standard rules and names no Claude agent (read 1460).
  - Its home page links its annual reports, its terms of service and a legal page, and no data file (read 1461).
  - The search found its figures only in the Canada Energy Regulator's summaries: 237 GWh generated in 2018, all diesel, from 26 plants in 25 communities. The Regulator says these are modelled from Statistics Canada's data.
- **No table.** The Nunavut Bureau of Statistics was not asked: the search found no energy table of it, and the requests left were kept.
- **With this, none of the chain's four planned territories gave a table:**
  - Prince Edward Island: a bot challenge;
  - Yukon: a workbook with no stated time base, for a ruling;
  - the Northwest Territories: no electricity table;
  - Nunavut: annual reports only.

  The session's own choices follow in sessions 2728, 2729 and 2734.

## Requests (2 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.qec.nu.ca's robots file (its own request) | 200 |
| 2 | the home page | 200 |

Reads recorded: 1460 and 1461.

## Decisions made without you

- **Qulliq's annual reports not read:** a PDF's figures would not make a series within the ceiling.

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: the license record (reads 1460 and 1461) and `docs/licenses.md`.
- On the data machine only: `runs/c137/s2725/`, `runs/license_reads/s2725/`.
