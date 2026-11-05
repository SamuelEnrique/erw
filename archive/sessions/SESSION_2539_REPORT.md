# Session 2539 report: Bulgaria's electricity a month (NSI's time-series workbook), the second own choice, internal; Hungary's MEKH not taken

24 October 2026, about 21:39 to 21:46 UTC, on lab-desktop (the data machine), chain 124, unattended. Precheck passed (`runs/c124/pre2539.out`). Model spend USD 0. Pulls: 5 requests of 20 (4 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Hungary first, not taken:** the regulator MEKH publishes monthly electricity statistics (press reports of its figures were found by search), but www.mekh.hu serves its script shell at the robots address and draws every page by script (read 1005), so no figure can be read. MEKH's host is not asked again until its data are published as files.
- **Why Bulgaria:** a grid the ERW held only in Eurostat's, EIA's and Energy-Charts' international tables; no chain had taken its statistics institute.
- **The host:** www.nsi.bg's robots file closes `/admin/` only (read 1006). The electricity statistics page (read 1007) links the time-series workbook "Production and deliveries of electricity" and NSI's licence.
- **NSI's licence** (read 1008), section 2.1.1: "Reproduce, disseminate and use the statistical information ..., including for commercial purposes, without requiring the consent of a third party, but provided that you indicate the name ... of the author with each use. You may not disseminate derivative or collective works." **Verdict: needs written permission** (sold or not), as other no-derivatives terms were read: a reshaped table in a warehouse may be both. The table is **internal**.
- **The source:** `Energy-1.4.Electricity_en.xlsx` (14 KB, last modified 24 August 2026), fetched once. It holds two sheets: "2019" (twelve months: gross and net production, imports, exports, total net consumption) and "2026" (January to July, with net production by source as well: nuclear 1,398 GWh and solar 1,021 GWh in July). It holds no other year; the header says so.
- **A new table, `nsi_bulgaria_electricity_monthly`** (series, 157 rows, 10 entities, `power`), in MWh. Each 2026 month's sources sum to its net production within 5 GWh (nine figures, each a whole GWh; May's differ by 3). Written by run `20261024T214340Z` under the data lock, validated (exit 0), in coverage, archived (`20261024T214344Z-local`), held from the live set and from Redivis (internal).

## Cross-checks

- Against `eia_world_electricity_annual`'s Bulgaria for 2019: NSI's exports 8.854 TWh against EIA's 8.855, imports 3.043 against 3.045; EIA's generation, 42.809 TWh, lies between NSI's net (40.296) and gross (44.161) production.

## Requests (5 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.mekh.hu's robots address | 200, the site's script shell |
| 2 | www.nsi.bg's robots file | 200 |
| 3 | NSI's electricity statistics page | 200 |
| 4 | NSI's licence page | 200 |
| 5 | the workbook (the fetch) | 200, 14 KB |

Reads recorded: 1005 to 1008. Two web searches found MEKH's statistics and NSI's page; they reached no publisher's host.

## A mistake, undone

- After the first verdict script failed (its quoted start did not match the page's non-breaking space), a command line went on in the main checkout instead of the chain's worktree: `licenses.py write` failed there (exit 1, nothing written) and a commit took the main checkout's untracked files (the findings files and `warehouse/output/retired/`, present before the chain began). It was never pushed. `git reset --mixed HEAD~1` put the files back as they were, untracked; the main checkout was then pulled (fast-forward) and shows only its earlier untracked files. Every later command names its directory and stops if it cannot enter it.

## Decisions made without you

- **Bulgaria as the second own choice; internal** under NSI's no-derivatives clause, until a ruling.
- **Both sheets taken as published,** the gap between 2019 and 2026 stated, not filled.

## For Samuel's ruling

- **NSI's licence:** whether the ERW's reshaped table is a "derivative or collective work" under its section 2.1.1. If not, the table could be public with NSI named.

## Files

- New: `warehouse/connectors/nsi_bulgaria_electricity.py`, `tests/test_session2539.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1005 to 1008, NSI's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c124/s2539/`, `warehouse/raw/nsi_bg_energy/`, `warehouse/output/nsi_bulgaria_electricity_monthly.csv`.
