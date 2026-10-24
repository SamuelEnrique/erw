# Session 2491 report: Zimbabwe's electricity generation a month, January 2019 to March 2026 (ZIMSTAT's Index of Electricity Generation), internal

24 October 2026, from about 14:56 UTC to 14:59 UTC for the reads and the connector; the table written under the data lock at 16:28 UTC. On lab-desktop (the data machine), chain 121, unattended. Precheck passed (`runs/c121/pre2491.out`). Model spend USD 0. Pulls: 8 requests of 15 (7 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **The ERW held no Zimbabwean source** (`sources.csv`, the connectors and the license record on main and on chains 118's to 120's branches searched for Zimbabwe, ZERA, ZESA, ZimStat, ZETDC and ZPC).
- **The hosts:**
  - the regulator ZERA's robots file disallows nothing (read 819), and its site's search finds no statistics page (read 823);
  - the Zimbabwe Power Company's closes `/wp-admin/` only (read 821);
  - ZIMSTAT's www.zimstat.co.zw redirects to zimstat.co.zw, whose robots file disallows nothing (read 820). Its site search finds no electricity table among its pages (read 822): the Index of Electricity Generation is a quarterly PDF.
- **A new table, `zimstat_zimbabwe_generation_monthly`** (series, 85 rows, one entity, `power`), from Appendix A of the "Index of Electricity Generation, 1st Quarter 2026" (last modified 14 August 2026): the volume generated a month, January 2019 to March 2026, compiled from ZESA's administrative data (Hwange, Kariba and the independent producers together).
  - GWh times 1,000 to MWh; `ts_utc` the month's first day.
  - Not written: two figures out of form (January and February 2026, printed "971,5" and "916,3" with a comma for the decimal point), counted.
  - The quarter rows are not written: 26 of 28 agree with their months' sum within 0.15 GWh (2022's first quarter and 2023's third do not, by 0.3 and 1.4 GWh).
  - Written by run `20261024T162831Z`, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set.
- **Internal.** ZIMSTAT's copyright page: "Unless otherwise stated, the material or information published within the Zimbabwe National Statistics Agency Website is ZIMSTAT copyright" (read 825). Session 2495's verdict: needs written permission.
- Not taken: the station split, given only as the quarter's shares in the text (Hwange 56.3 percent, Kariba 31.7 percent, the independent producers 12.0 percent in the first quarter of 2026); imports, exports and distribution, drawn as charts. The plan's peak demand is not in the publication.

## Cross-checks

- Twelve months' generation, TWh: 7.54 in 2019, 6.29 in 2020, 8.84 in 2022, 9.76 in 2024, 11.23 in 2025.
- Over `owid_ember_electricity_annual`'s demand for Zimbabwe: 0.71 to 0.82 (2019 to 2024); imports make up the rest (371.4 GWh in the first quarter of 2026 by the text).

## Requests (8 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.zera.co.zw/robots.txt | 200: nothing closed |
| 2 | www.zimstat.co.zw/robots.txt | 200 (at zimstat.co.zw): nothing closed |
| 3 | www.zpc.co.zw/robots.txt | 200 (at zpc.co.zw): `/wp-admin/` closed |
| 4 | ZIMSTAT's site search for electricity | 200 |
| 5 | ZERA's site search for electricity statistics | 200: a privacy page only |
| 6 | ZIMSTAT's site search for copyright | 200 |
| 7 | ZIMSTAT's copyright, disclaimer and privacy page | 200 |
| 8 | the publication (the fetch) | 200, 0.9 MB |

Reads recorded: 819 to 825 (on this branch). Two web searches found ZIMSTAT's publications; they reached no publisher's host.

## Decisions made without you

- **The monthly table rather than a yearly one:** the appendix gives months, and the quarter rows are kept as a check.
- **The two comma-decimal figures of 2026 left out** and counted, not read as 971.5 and 916.3.
- **The trial** as session 2490's: the connector run offline from the worktree, its table validated in `runs/c121/trial/2491/`.

## For Samuel's ruling

- **ZIMSTAT's consent,** if Zimbabwe's table is wanted public.

## Files

- New: `warehouse/connectors/zimstat_zimbabwe_generation.py`, `tests/test_session2491.py`, this report.
- Changed: the registration (`build_coverage.py`, `release_v1.py`, `live_set.yaml`); `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`; the license record (reads 819 to 825).
- On the data machine only: `runs/c121/s2491/`, `warehouse/raw/zimstat_electricity_index/`, `warehouse/output/zimstat_zimbabwe_generation_monthly.csv`.
