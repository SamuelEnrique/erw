# Session 2659 report: Tajikistan's electricity output, trade and consumption a year, 1991 to 2025 (the Agency on Statistics), public

25 October 2026, about 10:05 to 10:13 UTC, on lab-desktop (the data machine), chain 133, unattended. Precheck passed (`runs/c133/pre2659.out`). Model spend USD 0. Pulls: 8 requests of 15 (7 by the probe, 1 fetch of the workbook into the raw store, which the trial and the write read offline).

## Read these first

- **The ERW held Tajikistan only in EIA's world tables;** no source, read or queue file named the Agency or Barqi Tojik.
- **The host:** stat.tj sends to www.stat.tj, whose robots file closes only `/wp-admin/` to `*`, with no AI agent named (read 1343). Barqi Tojik's host was not asked: the Agency's table was enough.
- **The way in:**
  - The WordPress media searches gave nothing (reads 1344 and 1345).
  - The site search (read 1346) led to the Analytical tables page (read 1349). It lists "Electricity output, trade and consumption, 1991-2025", `table_11-1.xlsx`, last modified 26 September 2026.
- **The terms** (the site's footer, read 1349 and also on read 1348): "Все материалы сайта доступны по лицензии: Creative Commons Attribution 4.0 International", and "When using materials published on this site, a link to www.stat.tj is required".
  - A copyright line ("all rights reserved") stands beside the grant; the grant is read as the terms of reuse.
  - **Verdict: may be public.** The table is **public**, its header naming www.stat.tj.
- **A new table, `stat_tj_tajikistan_electricity_annual`** (series, 475 rows, 14 entities, `power`), 1991 to 2025, from the one sheet. The rows, with their variables:
  - output, hydro and thermal (`generation`);
  - imports and exports;
  - the total internal consumption and its six sectors (`consumption`);
  - losses (`distribution_losses`) and the discrepancy (`statistical_difference`).
- **Units and figures:** MWh is the table's billion kWh times 1,000,000. The output was 17.6 TWh in 1991 and 24.0 TWh in 2025, of it 22.3 hydro. Exports were 5.4 TWh in 2025.
- **The table's parts do not always add to its totals.** Every row is kept as published; a reader should not add them:
  - From 2015 the output exceeds hydro and thermal power by up to 0.9 TWh (2017: 18.1 against 17.2).
  - From 2016 the total internal consumption differs from its sectors and losses. In 2025 it is 18.2 TWh against 21.2, and the output, imports and exports balance to 21.3.
  - The run stops only if hydro and thermal miss the output by more than 1 TWh. A dash has no row (thermal in 2010; the discrepancy in 14 years).
- **Its record:** written by run `20261025T101039Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T101043Z-local`), held from the live set, and in the release package (public). Its method note and the Stanford draft are session 2667's.

## Cross-checks

Generation against `eia_world_electricity_annual`'s Tajikistan, in TWh (the Agency's first):
- 2018: 19.7 against 19.74; 2022: 21.4 against 21.49; 2024: 22.4 against 22.2.
- 2023: 21.9 against 21.23 (3 per cent apart).

Imports differ more. In 2024 the Agency gives 1.6 TWh and EIA 0.9; exports are 3.9 and 3.5.

## Requests (8 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | stat.tj's robots file (sent to www.stat.tj's) | 200 |
| 2, 3 | the media searches | 200, empty |
| 4, 5 | the site search and the sitemap index | 200 |
| 6, 7 | the industry yearbook's post and the Analytical tables page | 200 |
| 8 | `table_11-1.xlsx` (the fetch) | 200 |

Reads recorded: 1343 to 1349.

## Decisions made without you

- **Public,** under the footer's CC BY 4.0, beside its copyright line.
- **No sum check on consumption,** as the table's own parts disagree from 2016; the gaps are stated in the connector and here.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/stat_tj_tajikistan_electricity.py`, `tests/test_session2659.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (reads 1343 to 1349, the Agency's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c133/s2659/`, `runs/license_reads/s2659/`, `warehouse/raw/stat_tj/`, `warehouse/output/stat_tj_tajikistan_electricity_annual.csv`.
