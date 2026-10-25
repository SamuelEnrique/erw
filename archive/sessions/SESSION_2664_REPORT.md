# Session 2664 report: Kazakhstan's electricity a year, 2022 to 2025, from the Bureau of National Statistics' fuel and energy balances, public, a source of the session's own choosing

25 October 2026, about 10:24 to 10:36 UTC, on lab-desktop (the data machine), chain 133, unattended. Precheck passed (`runs/c133/pre2664.out`). Model spend USD 0. Pulls: 11 requests of 20, all to stat.gov.kz:
- 3 by the probe;
- 4 fetches of the balances into the raw store;
- 1 by the first trial, for the 2021 edition;
- 3 by the third trial, which asked again three workbooks the fetches had saved.

## First: conflict markers committed, and three requests made twice

- **Conflict markers in a commit.** The write's last step failed: its metadata patch met sessions 2659 and 2661's rows and applied with conflicts (`runs/s2664_apply.out`).
  - I committed before reading that exit, so commit `0dc3dd0c` put conflict markers in `docs/coverage.md`, `coverage.csv`, `sources.csv` and `archive_manifest.csv`.
  - The next commit, `72a0d117`, resolved the four as the union of both sides (`runs/c124/resolve_union.py`). Each new table's row is there once and coverage holds 581 tables. The finish step then passed, with 0 license problems.
  - No push came between; the branch is not landed.
- **Three workbooks asked twice.** The connector's online trial asked for three workbooks the session's fetch script had saved minutes before. `fetch_raw` reused only one of the four saved copies.
  - So 3 of the 11 requests repeat earlier ones. The ceiling was kept.
  - The write and every later run read the saved files offline.

## Why this source

- **The ERW held Kazakhstan only in EIA's world tables.** Session 2360 tried KEGOC and found its figures only in prose; the Bureau's site had not been asked.
- **Others checked first:**
  - Uzbekistan and Azerbaijan are the unlanded chain 118's.
  - Kyrgyzstan is the unlanded chain 119's.

## Read these first

- **The host:** stat.gov.kz's robots file closes Bitrix's system paths and some query parameters, not `/api/` or `/upload/`, and names no AI agent (read 1362).
- **The way in:** the Energy Statistics page (read 1363) gives the fuel and energy balance for each year from 2021 to 2025, each an English workbook.
- **The terms** (read 1364, "About using the data"):
  - "Users may use official statistical information for any purposes (including reusing it in full) freely, free of charge, perpetually, and without territorial restrictions, including copying, publishing, distributing with a reference to the source".
  - **Verdict: may be public.** The table is **public**.
- **A new table, `stat_kz_kazakhstan_electricity_annual`** (series, 84 rows, 21 entities, `power`), from the electricity column of each balance's sheet "1" (in physical terms), 2022 to 2025:
  - **Generation:** the output, its four plant classes, and the hydro, solar, wind and biogas production.
  - **Trade and use:** imports, exports (stored positive), the energy sector's own use, losses, the statistical difference, and final consumption with six of its sectors.
  - **Units:** MWh is the balance's million kWh times 1,000.
- **Figures:**
  - The output was 113.6 TWh in 2022 and 123.8 TWh in 2025.
  - Wind grew from 2.3 to 5.2 TWh. In 2025 hydro gave 10.4 and solar 2.3.
  - In 2025 imports were 5.1 TWh, exports 3.5 and final consumption 87.1.
- **The editions name the same rows differently:**
  - 2025 uses "Imports (+)", "Statistical differences" and "Electricity plants (TPP)".
  - 2022 to 2024 use "import", "Statistical discrepancies" and "Power plants (TPP) ... - electricity generation".
  - Each row is found under its names within its section; a row found under none stops the run.
  - The 2021 edition, in GWh and with the IEA's row names, is not read.
- **Checks,** each within 1 million kWh and passing in every year:
  - the plant classes add to the output;
  - the output, trade, own use and losses make the energy available;
  - available less the statistical difference is the final consumption;
  - the sectors add to it.
- **The plant classes are not comparable across 2024 and 2025.** The 2025 edition puts most output under electricity plants of main activity (71.5 TWh), the earlier ones under CHP plants (82.3 TWh in 2024). The connector and its note say so.
- **Its record:** written by run `20261025T103039Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T103044Z-local`), held from the live set, and in the release package (public). Its method note and the Stanford draft are session 2667's.

## Cross-checks

Against `eia_world_electricity_annual`'s Kazakhstan, in TWh (the Bureau's first):
- **Generation:** 2022 113.6 against 113.6; 2023 113.6 against 113.2; 2024 118.7 against 122.8 (3 per cent apart).
- **Trade:** imports and exports agree to 0.01 TWh in 2022 and 2023 (3.69 and 2.24; 4.78 and 2.71).

## Requests (11 of 20)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | the robots file, the Energy Statistics page, About using the data | 200 |
| 4 to 7 | the 2025, 2022, 2023 and 2024 balances (the fetch) | 200 |
| 8 | the 2021 balance (the first trial) | 200 |
| 9 to 11 | the 2022, 2023 and 2025 balances again (the third trial) | 200 |

Reads recorded: 1362 to 1364.

## Decisions made without you

- **Kazakhstan's Bureau as the own choice; public** under its conditions of use.
- **2022 to 2025 only;** the 2021 edition's layout is left for a later chain.
- **Exports stored as a positive quantity,** the balance printing them negative.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/stat_kz_kazakhstan_electricity.py`, `tests/test_session2664.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (reads 1362 to 1364, the Bureau's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c133/s2664/`, `runs/license_reads/s2664/`, `warehouse/raw/stat_kz/`, `warehouse/output/stat_kz_kazakhstan_electricity_annual.csv`.
