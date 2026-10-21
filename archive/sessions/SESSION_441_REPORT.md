# Session 441 report: the datacenter and deals tables, row by row, by what their sources allow

21 October 2026, about 07:16 to 07:30 UTC, unattended, on portable-laptop (the code role), in the main checkout `C:\Users\samen\Documents\erw` on `wip/441-450-third`. The chain of 21 October, night, third machine (`queue/done/017-night-21-october-third.md`, session 441). Model spend USD 0; no request to any publisher; no warehouse data written; no `site/` change, so no build.

## Read these first

- **The review is `docs/reviews/sources-by-row-2026-10-21.md`.** For `datacenter_facilities`, `datacenter_projects`, `datacenter_operator_sites` and `energy_deals`, every row's source publishers counted (the row's `source`, every story of its `story_ids` through `news_stories`, every member of a facility's `member_ids`), each publisher's verdict from `license_verdicts.csv` (the file `docs/licenses.md` is written from), and rows and MW by group.
- **11 of 1,330 rows rest only on public sources**: 2 facilities (ERCOT's queue; queue MW 133.0 and 58.26) and 9 deals (World Nuclear News alone). None states a MW figure. `datacenter_projects` and `datacenter_operator_sites` hold none. The list is `docs/reviews/sources-by-row-2026-10-21-public-rows.csv`.
- **The count turns on one ruling.** The chain prompt names "a company's own announcement page" as public; the nine operators' location pages are each company's own, but `docs/licenses.md` says "needs written permission" for all nine. Counted public (variant B), 275 operator sites and 276 facilities would be public, 15 rows with 4,799.0 MW.
- **The hold's publisher lists miss three publishers the rows rest on**: Data Center Knowledge and Heatmap News under `energy_deals`, OilPrice.com under `datacenter_facilities`, all three "needs written permission". The hold is whole-table, so no page changes; the words beside "license needed" are incomplete.
- **The split-table method is written for the code machine** (a `publishers` and a `license` column a row, recomputed at load, read by the page as the by-grid hold already is), with the tests it needs. Nothing of it is built.

## What to review

- The review: `https://github.com/SamuelEnrique/erw/blob/wip/441-450-third/docs/reviews/sources-by-row-2026-10-21.md`
- The public rows: `docs/reviews/sources-by-row-2026-10-21-public-rows.csv` (11 rows).
- The test: `tests/test_session441.py`.

## Checks

Every gate redirected to a file under `runs/chain_oct21_third/s441/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `count.py` (the count) | 0 | `count.out`, `figures.json`: 1,330 rows, 968 story ids, all found in `news_stories` |
| `count.py compare` | 0 | `compare.out`: the rows' publishers against `license_status.csv` |
| `tests.test_session441` | 0 | 8 tests OK: no em or en dash; every snake_case name in backticks a table of `coverage.csv` or a column of the files read; the four tables' rows, MW and classes, the headline, variant B, the World Nuclear News sentence and the story count each equal a recount by the test's own code; the public-rows CSV exactly the recount's public rows |
| The same tests against a copy with an em dash and "12 of 1,330" | 1 by design (the script exits 0 when exactly 2 fail) | 2 failures, as they should |
| The whole suite | not run | the parent runs it once for the chain; this session changed no code a test outside its own reads |
| Build, snapshot, browser checks | none | no `site/` change |

## Decisions made without you

1. **A row rests on every story of its cluster, not only on its `source` column** (variant A). The model that wrote a deals or projects row read every story of the cluster, and a field cannot be traced to one story. Variant C (the `source` column only) is shown beside it: 11 deals and 433.0 MW instead of 9 and 0.
2. **"Public" means the verdict "may be public" in `license_verdicts.csv`**, its column "As the ERW is today", and nothing else; a publisher not in the record makes its row "not settled", never public, as `docs/licenses.md` says.
3. **Source names were joined to publishers by `sources.csv` and `canon()` of `scripts/licenses.py`**, the same path `docs/licenses.md` is written by, rather than by a new mapping.
4. **The NYISO queue row counts as asking permission** (NYISO's verdict), though the chain prompt lists "an ISO queue" among public sources: the prompt's list names kinds, and the record's verdict for the publisher decides.
5. **Variant B is counted, not adopted.** The operators' pages are reported both ways so that the ruling has its numbers.
6. **The count script stays in `runs/`** (git ignores it); the test holds its own recount, so the figures can be checked without it.
7. **The counting tests skip once the tables move** (their row counts against 20 October's build), so the suite does not fail on the data machine's next run; the dash and name tests always run.

## For Samuel's ruling

- Whether a company's own page (the nine operators' location pages) counts as a public source for `datacenter_operator_sites` (variant B: 275 rows, 4,799.0 MW), against the verdicts of `docs/licenses.md`. Three of the nine (Digital Realty, Equinix, Switch) were never read.
- Whether to build the split table now (11 rows today, none with a stated MW) or after a ruling or a permission frees a publisher.
- Whether `license_status.csv`'s publisher lists should be written from the rows (adding Data Center Knowledge, Heatmap News, OilPrice.com where they are missing) rather than from `sources.csv`'s table lists.
- Energy-Storage.news and Electrek: read their terms (3 deals rest on them alone).

## To finish

- Land `docs/reviews/sources-by-row-2026-10-21.md`, its CSV and `tests/test_session441.py` with the next landing (docs and a test only; no build needed). The counting tests read the tables as they stood at 07:16 UTC on 21 October (420, 143, 275 and 492 rows) and skip once a build moves those counts, or where `warehouse/output` is absent (GitHub's check): the review is a record of that day.

## Files

- `docs/reviews/sources-by-row-2026-10-21.md` (new).
- `docs/reviews/sources-by-row-2026-10-21-public-rows.csv` (new, written by the count script).
- `tests/test_session441.py` (new).
- This report.
- Not in git: `runs/chain_oct21_third/s441/` (`count.py`, `tables_md.py`, `figures.json`, `count.out`, `compare.out`, `test.out`, `negative.out`, two peek scripts).
