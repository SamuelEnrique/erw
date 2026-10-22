# Session 679 report: the license record, regenerated

22 October 2026, from about 10:04 UTC, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0. Pulls: none.

## Read these first

- **The new publishers' records are in the three files** (session 666): OpenEI's verdict in `license_verdicts.csv` (record 88, "Creative Commons Zero", may be public); NERC's and HIFLD's reads in `license_reads.csv` (records 89 and 90, not read: a page whose text loads by script, and a 404), with no verdict, so a table of theirs would be unsettled. No table of theirs exists.
- **`scripts/licenses.py tables`, `write` and `check`** ran in the branch's worktree, each exit 0: 294 tables, 70 publishers with a verdict, 88 requests in the record, 0 problems. `docs/licenses.md` was already current (sessions 667 to 672's finish steps wrote it).
- **Every new table's flag agrees with its verdict:** `utility_service_territories`, `interconnection_durations`, `interconnection_durations_summary`, `grid_peak_vs_capacity`, each flagged `public` in `coverage.csv` and `public` by its ERW verdict. No disagreement to list.
- **`license_status.csv` is regenerated** (`licenses.py status`): still 42 tables "license needed" from 21 October, none with a permission. It changed only in two tables' publisher lists (`datacenter_facilities`, `datacenter_projects` now name OilPrice.com, from their headers on this machine).

## Decisions made without you

- `licenses.py status` also rewrites the site's copy (`site/data/license_status.json`) and the dated note `docs/state/licenses_2026-10-21.md`. Here that would have carried other chains' changes into what the site reads (pages added to two tables' lists, the date "written"), so both were put back as they were; only the record, `license_status.csv`, is kept. The site's copy is the landing's, with snapshots.

## For Samuel's ruling

- None new.

## Files

- Changed: `warehouse/metadata/license_status.csv`. New: this report.
