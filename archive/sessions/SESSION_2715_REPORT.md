# Session 2715 report: the UK's interconnector flows a year, 1998 to 2025 (DESNZ's DUKES 5.13), public, a second source of the session's own choosing

25 October 2026, about 17:12 to 17:15 UTC, with the write at 18:23 UTC after this machine's daily task released the data lock, on lab-desktop (the data machine), chain 136, unattended. Precheck passed (`runs/c136/pre2715.out`). Model spend USD 0. Pulls: 2 requests of 20 (1 by the probe, 1 fetch of the workbook, read offline by the trial and the write).

## Why this source

- **The companion of session 2714's stations:** DUKES 5.13 gives each interconnector's imports, exports and use, the UK's cross-border side, from the same chapter, host and licence. The ERW held the UK's trade only inside national totals.

## Read these first

- **The host:** www.gov.uk's robots file closes only print and search paths and names no Claude agent (read 1448). The chapter page was read in session 2714 (read 1447). The terms are the Open Government Licence v3.0 (read 315), so the table is **public**.
- **A new table, `desnz_uk_interconnector_flows_annual`** (series, 642 rows, `power`), 1998 to 2025:
  - Entity `desnz_ic:<pair>`, ten of them:
    - the seven interconnector borders: France, Ireland and Northern Ireland (North-South), the Netherlands, Ireland and Wales, Belgium, Norway, Denmark;
    - `uk_total`;
    - the two transfers within the UK, Scotland and England, and Scotland and Northern Ireland (Moyle, which DESNZ counts as a transfer).
  - Variables: `imports`, `exports` and `net_imports` in MWh (the sheet's GWh times 1,000), and `utilisation` as a ratio. For the transfers, each direction and the net.
  - Each of the sheet's 38 headings is matched exactly; a new one stops the run. "[x]" and blank cells have no row. Belgium's zeros of 2017 and 2018, before Nemo Link opened, are kept as DESNZ writes them.
- **Figures:**
  - The UK's net imports were 12.7 TWh in 1998, 2.7 in 2010 and 17.9 in 2020, then -5.3 in 2022 (net exports, chiefly to France, 10.0 TWh) and 29.7 in 2025.
  - In 2025: France 21.9 TWh net in, Norway 9.0, Denmark 2.5; Ireland and Wales 4.5 net out.
  - Scotland sent England 18.5 TWh net.
- **Checks, all passing,** within 0.01 GWh:
  - every pair's imports less exports equal its net;
  - each transfer's two directions equal its net;
  - the seven interconnectors add to the UK's totals;
  - every utilisation lies in [0, 1].
- **Not taken:** table 5.13A, each interconnector's capacity (eleven rows), also listed in session 2714's workbook summary.
- **Its record:** written by run `20261025T182339Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T182344Z-local`), held from the live set, and in the release package (public).
- **The write's patch conflicted in `sources.csv`,** whose rows sort beside session 2714's. It was resolved as a union in the worktree, with no marker and no row twice, and committed before the finish.

## Cross-check

Against `eurostat_electricity_trade_annual` (each partner's own reported trade with the UK), in TWh:

| Year | France's exports to the UK | DESNZ's UK imports from France | France's imports from the UK | DESNZ's UK exports to France | Norway's exports to the UK | DESNZ's UK imports from Norway |
|---|---|---|---|---|---|---|
| 2023 | 16.68 | 15.62 | 2.61 | 2.75 | 8.54 | 8.95 |
| 2024 | 21.62 | 20.27 | 0.79 | 0.82 | 10.26 | 9.90 |

The two sides meter at opposite ends of the cables, so the gaps include the cables' losses.

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk's robots file (its own request) | 200 |
| 2 | DUKES_5.13.xlsx (the fetch) | 200 |

Read recorded: 1448.

## Decisions made without you

- **DUKES 5.13 as the second own choice; public.**
- **Moyle kept as a transfer within the UK,** as DESNZ counts it, not as an interconnector.
- **Utilisation stated as a ratio,** as the sheet gives it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_dukes_interconnectors.py`, `tests/test_session2715.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (read 1448) and `docs/licenses.md`.
- On the data machine only: `runs/c136/s2715/`, `runs/license_reads/s2715/`, `warehouse/raw/desnz_dukes/s2715probe1/`, `warehouse/output/desnz_uk_interconnector_flows_annual.csv`.
