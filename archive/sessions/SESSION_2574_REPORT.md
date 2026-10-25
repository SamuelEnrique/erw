# Session 2574 report: the next file first; Samoa's electricity, production by source and EPC's sales by category (SBS's Electricity Statistics 2025), internal

25 October 2026, about 02:12 to 02:22 UTC, on lab-desktop (the data machine), the first session of `queue/done/127-day-27-november-data-samoa-algeria-gabon-bahamas.md`, unattended. Precheck passed (`runs/c127/pre2574.out`). Model spend USD 0. Pulls: 7 requests of 15 (6 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Chain 127 was taken at 02:09 UTC on 25 October by chain 126's agent** when chain 126 landed (`615d8249`), under the owner's instruction for this run. Its worktree is `erw-c127`, its branch `wip/2574-2587-data`.
- **The next file first:** `queue/next/128-day-28-november-data-mauritania-mali-papua-new-guinea-curacao.md`, sessions 2588 to 2601, machine data, written by `runs/c127/write_128.py` from file 127 (its rules word for word; the live site's line brought up to date: the site answers 200 again), committed alone in the queue worktree and pushed to main as `90bd168c` between two snapshots (`q128-before`, `q128-after`: 25 pages, all 200, 0 differences). Number 128 and sessions 2588 to 2601 were free on main and on every branch. Its sources: Mauritania, Mali, Papua New Guinea and Curacao, none held, planned or read.
- **The ERW held no source for Samoa** but EIA's international table.
- **The hosts:** www.sbs.gov.ws's robots file closes /wp-admin/ only (read 1093); www.epc.ws has no robots file (read 1094); library.sprep.org, where the Ministry of Works' Samoa Energy Review 2023 is kept, answers its robots address with a Cloudflare challenge (read 1095) and was not asked again.
- **SBS's terms:** every page's footer reads "(c) 2022 | Samoa Bureau of Statistics, All Right Reserved." (read 1097, the site search page); no terms of reuse found. **Verdict: needs written permission** (ZIMSTAT's precedent). The table is **internal**.
- **The source:** SBS's Environment page (read 1098) lists its Electricity Statistics workbooks; the 2025 edition (last modified 13 July 2026, from EPC) was fetched once: table E1, production by source 2008 to 2025, and table E3, EPC's sales by category 2008 to 2024, both in MWh.
- **A new table, `sbs_samoa_electricity_annual`** (series, 288 rows, 16 entities, `power`): `production` by source (total, diesel, hydro, coconut, solar, wind, biomass) and `sales` by category (commercial, domestic, government, hotels, industrial, religious, schools, local consumption, street lights, and the total). In 2025: production 226.6 GWh (diesel 156.3, hydro 43.0, solar 27.3); in 2024 sales 193.8 GWh. Each year's sources checked against the total within 1 MWh. Written by run `20261025T022051Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T022056Z-local`), held from the live set and from Redivis (internal). The trial ran from the main checkout under the data lock (`runs/c092/trial.sh`), as this chain's rules ask.
- **E3's total:** the workbook prints one figure, 153,987.5 MWh, as the total of every year 2008 to 2015, which its categories do not add to (96.5 GWh in 2008); those eight totals are not written. From 2016 the total equals its categories and is written.
- **Not taken:** E1's shares, table E2 (diesel against renewable, which repeats E1), the Energy Accounts.

## Cross-checks

- Against `eia_world_electricity_annual`'s Samoa, read past its header lines: 2019 generation, EIA 164.8 GWh against SBS's 169.3; hydro 45.0 against 49.8. For 2024, EIA's 162.5 GWh (an estimate) against SBS's 220.5.

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.sbs.gov.ws's and www.epc.ws's robots files | 200, 404 |
| 3 | library.sprep.org's robots file | 403 (Cloudflare) |
| 4 to 6 | SBS's media search, site search and Environment page | 200 |
| 7 | the Electricity Statistics 2025 workbook (the fetch) | 200, 29.9 kB |

Reads recorded: 1093 to 1098. Test 205's bound was raised by 40 for chain 127's reads (from 1093).

## Decisions made without you

- **E3's eight broken totals left out,** the categories kept, and the header says so.
- **Internal** under SBS's copyright line.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/sbs_samoa_electricity.py`, `tests/test_session2574.py`, this report; `queue/next/128-...md` (on main).
- Changed: the registration; the metadata files; the license record (reads 1093 to 1098, SBS's verdict) and `docs/licenses.md`; `tests/test_session205.py` (its bound).
- On the data machine only: `runs/c127/s2574/`, `runs/c127/write_128.py`, `runs/c127/eia_read.py`, `warehouse/raw/sbs_ws/`, `warehouse/output/sbs_samoa_electricity_annual.csv`.
