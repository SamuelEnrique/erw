# Session 2451 report: Uzbekistan's electricity production by region (2010 to 2024), solar and wind (2015 to 2024) and gross consumption by region (2016 to 2025), from SIAT

24 October 2026, from 12:44 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/118-day-18-november-data-rwanda-senegal-azerbaijan-uzbekistan.md`, unattended. Precheck passed (`runs/c118/pre2451.out`). Model spend USD 0. Pulls: 12 of 15 (below).

## Read these first

- **One public table:** `siat_uzbekistan_electricity_annual`, 395 rows, 15 entities (the republic and its 14 regions, Tashkent city among them). It is written, validated, archived, in coverage (sector power), held from the live set, and listed in the release's held tables. It comes from four indicator files of SIAT, the statistics committee's open data portal (reads 816 to 819 on this branch's numbering):
  - 1.02.02.0004, electricity production, by region, 2010 to 2024 (`generation`);
  - 1.02.02.0006 and 0007, production by solar and by wind plants, the republic, 2015 to 2024 (`generation_solar`, `generation_wind`);
  - 1.02.02.0019, gross electricity consumption by subscribers, by region, 2016 to 2025 (`consumption`);
  - in MWh. The files' unit, "Million kWt hour", is million kWh, times 1,000.
- **The files' notes,** carried into the header: production is final for 2010 to 2022 and preliminary for 2023, and the republic includes data not allocated to a region. Solar and wind are collected since 2015 and consumption since 2016, each preliminary for 2023.
- **The checks:**
  - the regions never add to more than the republic (within 1 GWh);
  - the republic's excess is the unallocated part, at most 34.1 GWh, 19.8 GWh in 2016 and 0.6 GWh in 2022 to 2024.
  - The first check, an equality within 1 GWh, stopped at 2016's 19.8 GWh. The note's "including unallocated data by region" explains the gap, so the check now allows it.
- **The wind file has a column keyed "2022.1"** besides "2022", both 0.0; it is not taken. Zeros are kept as published (wind is 0.0 in most years to 2022, and 789.6 million kWh in 2024).
- **License: public, CC BY 4.0.** Each indicator page reads "Litsenziya: CC BY 4.0" and names it in its dataset record (read 810). New verdict: may be public.
- **Robots:** stat.uz disallows only Joomla's system paths (read 808). siat.stat.uz and api.siat.stat.uz allow every path, with ClaudeBot, Claude-Web and anthropic-ai named among the allowed (reads 809 and 811).
- **The indicator files were found by a web search,** which pointed to SIAT's indicator pages, rather than by browsing stat.uz.
- **Not taken into the repository:** the download pointers name a staff member's email; it is not copied anywhere.

## The cross-check (`runs/c118/s2451/cross.py`, `cross.out`; tables read past their header lines)

- **Production against `owid_ember_electricity_annual`'s Uzbekistan demand:** within 4.0 per cent in every year shown, 3.3 above in 2016 and 2.0 below in 2024 (82.74 against 84.43 TWh).
- **Consumption runs 15 to 24 per cent below production from 2016 to 2024,** except in 2018 (60.74 against 62.90 TWh). 2018's consumption is out of line with 2017's 46.75 and 2019's 54.17 TWh, as SIAT prints it; this report does not explain it.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| stat.uz | 1 | robots |
| siat.stat.uz | 2 | robots, indicator 440's page |
| api.siat.stat.uz | 9 | robots, four download pointers, four files (13 to 19 KB), a second or two apart (no crawl delay is asked) |
| total | 12 of 15 | |

## Errors

- **The first parse stopped at 2016's unallocated part.** The check now allows the republic to exceed its regions, as the file's note says it does.

## Decisions made without you

- **The table public,** under SIAT's CC BY 4.0.
- **Wind's "2022.1" column left out.**

## For Samuel's ruling

- None.

## Files

- New:
  - `warehouse/connectors/siat_uzbekistan.py`
  - `tests/test_session2451.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`
  - `warehouse/metadata/license_reads.csv` (808 to 819), `license_verdicts.csv` (the committee), `license_tables.csv`, `docs/licenses.md`
  - the coverage, sources and archive manifest files, and the release lists
- On the data machine only: `runs/c118/s2451/`, `runs/license_reads/s2451/`.
