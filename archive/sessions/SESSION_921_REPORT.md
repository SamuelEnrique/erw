# Session 921 report: the package's and the site's records

23 October 2026, from 08:50 UTC, on lab-desktop (the data machine), a session of `queue/done/051-day-23-october-data-world-gas-hydro.md`. Model spend USD 0. Pulls: none. Run in the branch's worktree while session 919's upload was proving its tables (no file of the main checkout read or written).

## Read these first

- **Stale, as session 894 found after chain 048:** `python package/tools/build_tables.py --check` exited 1. The package's `tables.csv` shipped 339 rows against 346 in the record, and 8 differ: this chain's seven new tables, and `news_stories`, whose publishers needing permission now include T&D World (session 914's verdict). The site's two files (`site/data/table_verdicts.json`, `table_citations.json`) differed with it.
- **Rebuilt:** `build_tables.py` wrote 346 tables (public 243, internal 54, unsettled 49); `--check` then exits 0 ("0 differ; the site's two files agree").
- **The tests of sessions 1001, 1008 and 1009 pass** against the rebuilt files (22 tests).

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: `package/src/erw/data/tables.csv`, `site/data/table_verdicts.json`, `site/data/table_citations.json`.
