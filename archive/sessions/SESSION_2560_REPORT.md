# Session 2560 report: the next file first; Eswatini's electricity, two financial years (EEC's Integrated Annual Report 2025), internal

24 October 2026, 23:59 UTC (chain 126's start), to 25 October, about 00:09 UTC, on lab-desktop (the data machine), the first session of `queue/done/126-day-26-november-data-eswatini-burkina-faso-maldives-suriname.md`, unattended. Precheck passed (`runs/c126/pre2560.out`). Model spend USD 0. Pulls: 7 requests of 15 (6 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Chain 126 was taken at 23:59 UTC on 24 October by chain 125's agent** when chain 125 landed (`af9c6c24`), under the owner's instruction for this run.
- **The next file first:** `queue/next/127-day-27-november-data-samoa-algeria-gabon-bahamas.md`, sessions 2574 to 2587, machine data, written by `runs/c126/write_127.py` from file 126 (its rules word for word), committed alone in the queue worktree and pushed to main as `e28021e7` between two snapshots (`q127-before`, `q127-after`: 25 pages, all 200, 0 differences). Number 127 and sessions 2574 to 2587 were free on main and on every branch. Its sources: Samoa, Algeria, Gabon and the Bahamas, none held (only American Samoa appears, in US tables).
- **The ERW held no source for Eswatini** but EIA's international table.
- **The hosts:** www.eec.co.sz and eec.co.sz have no robots file (reads 1048, 1051); www.esera.co.sz (the regulator) does not resolve (read 1049); www.gov.sz did not answer (read 1050).
- **EEC's terms** (read 1053): "Reproduction is prohibited other than in accordance with the copyright notice, which forms part of these terms and conditions"; the notice reads "(c) 2026 Eswatini Electricity Company. All rights reserved." (read 1052). **Verdict: needs written permission.** The table is **internal**.
- **The source:** EEC's Integrated Annual Report 2025 (157 pages, 6.0 MB, last modified 1 December 2025), fetched once; its page "Highlights and at-a-glance metrics" gives five figures in GWh with their figures for the year before. The page's text runs its columns together, so the figures are read in their labels' order (energy sold, units sent out, internal generation, imports, the generation bought from Ubombo Sugar), counts and order checked.
- **A new table, `eec_eswatini_electricity_annual`** (series, 10 rows, `power`): for the years ended 31 March 2025 and 2024, sold 1,181 and 1,173 GWh, sent out 1,366 and 1,356, internal generation 281 and 319 (drought), imports 978.6 and 962.1, bought from Ubombo Sugar 65.9 and 61.4; in MWh, `ts_utc` the financial year's first day (1 April), `x_fiscal_year` the year. Written by run `20261025T000805Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T000811Z-local`), held from the live set and from Redivis (internal).
- **Not taken:** the percentages (system losses 13.54%), the money, and the report's charts (its five years of internal generation are a chart's labels).

## Cross-checks

- Against `eia_world_electricity_annual`'s Eswatini for 2024: EIA's imports 1.044 TWh against EEC's 0.979 for 2024/25 (94%); EIA's generation 0.604 TWh against EEC's internal 0.281 plus Ubombo's 0.066 (EIA counts the sugar mills' own generation).

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | www.eec.co.sz, www.esera.co.sz and www.gov.sz robots files | 404, does not resolve, a timeout |
| 4 | eec.co.sz's robots file | 404 |
| 5 | the Integrated Annual Report 2025 (the fetch) | 200, 6.0 MB |
| 6, 7 | EEC's home page and terms of use | 200 |

Reads recorded: 1048 to 1053 (on this branch, after chain 125's 1014 to 1047). Test 205's bound was raised by 40 for chain 126's reads. One web search found the report; it reached no publisher's host.

## Decisions made without you

- **The highlights read by order,** with every count and order checked, as the page's text gives no columns.
- **A financial year dated from its first day,** the year named beside it.
- **Internal** under EEC's terms.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eec_eswatini_electricity.py`, `tests/test_session2560.py`, this report; `queue/next/127-...md` (on main).
- Changed: the registration; the metadata files; the license record (reads 1048 to 1053, EEC's verdict) and `docs/licenses.md`; `tests/test_session205.py` (its bound).
- On the data machine only: `runs/c126/s2560/`, `runs/c126/write_127.py`, `warehouse/raw/eec_sz/`, `warehouse/output/eec_eswatini_electricity_annual.csv`.
