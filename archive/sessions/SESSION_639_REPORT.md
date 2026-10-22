# Session 639 report: the early years of crude imports (from 2009) and of natural gas liquids (from 1973)

22 October 2026, from 06:50 UTC, on lab-desktop (the data machine), a session of `queue/done/041-morning-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia_crude_imports_detail_monthly` now runs from January 2009**: 183,393 rows (28,614 new), 8,538 series.
  - 2009 and 2010 are a window of their own (`SPLIT`, `EARLY_END`), so sessions 632 and 636's pages of 2011 on answered again.
  - As in session 636, EIA counts more than its pages hold: 31,150 against 28,614 for the early window. Every month from 2009-01 to 2026-07 is there; the header gives both numbers.
- **`eia_ngl_production_monthly` now runs from January 1973**: 110,896 rows (78,940 new), 284 series.
  - 1973 to 2014 is a window of its own (session 635's form), the 2015 on pages reused. The whole history fit (16 pages).
- **Cross-checks**:
  - Both tables' later rows are unchanged (154,779 and 31,956).
  - **Crude imports, 2009 and 2010, against `eia_crude_imports_by_country`'s U.S. total** (MCRIMUS2): the detail runs 1.017 to 1.049 times it (median 1.036) in all 24 months, where 2011 on matched at the median. The two tables come from different EIA forms (EIA-814 company level, and the country table); the difference is not looked into.
  - **NGLs, 1973 to 2014, the PADDs against the U.S.**: 6,450 of 6,528 keys within 1 kbbl. 54 of the 78 others are one product, EPLL, in 1981 and 1982 (up to 9,856 kbbl a month, 329 kbbl a day as late as 2008); the rest differ by 2 kbbl a day or less. Kept as EIA gives them.
- **Both written under the data lock** (06:54 and 06:55 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 each time (28,614 and 78,940 rows archived). Both tables' release rows were replaced; the release check exited 0.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 23 of 25 | the NGL route's count to 2014, crude imports' early window (6), the NGL route's early window (16) |

## Files

- New: this report. Changed: `warehouse/connectors/eia_crude_imports_detail.py` and `warehouse/connectors/eia_ngl_production.py` (each an early window and its ceiling), `docs/redivis/release-v1/{tables,variables}.csv`, coverage and the archive manifest.
