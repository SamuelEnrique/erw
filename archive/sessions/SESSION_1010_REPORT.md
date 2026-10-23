# Session 1010 report: the release package proves the packages

23 October 2026, from about 03:25 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1010` on `wip/1010-packages` (cut from `wip/1009-packages`). Chain `queue/done/070-evening-22-october-code-packages.md`, session 1010. Model spend USD 0. No warehouse data written. **Nothing released on Redivis.** Requests: Redivis 11 outside the remote test (2 for the rows address, 9 for the draft's listing, run twice), plus the Stanford remote test's reads (five tables and the headers; the test counts none of them); all reads, within the 100 of the ceiling.

## Read these first

- **The dataset's README** (`docs/redivis/release-v1-stanford/README.md`, for Redivis's description) gains "Read it in Python, Stata or R": the three install lines, Henry Hub's 2025 in each language, and the specification's address.
- **The table list carries each table's fetch line in each package**: `fetch_python`, `fetch_stata`, `fetch_r`, from the specification's "One line a table", written by the new `release_v1.py --calls-only`. It reads the table list as it is, without reading the tables, so no list of this machine's older tables replaced the one built on the data machine.
- **The release note gains "After the click"**: each language's three commands that prove the released version, and what this session found.
- **The draft against the record** (one listing): 207 tables. Of the 203 in coverage, 160 have the record's row count. The 43 others have fewer rows than the record, each a table that grew after its upload; none has more.
- **The Stata and R packages' Redivis address**: `.../tables/<reference>/rows?format=csv`.
  - Redivis answered on it, but for the draft the answer was the token's 100 GB streaming cap (since 15 October), so the CSV form is still not proven.
  - The released v1.0 answered 404 for an ERW table, as it holds none until your click.
  - The Python package falls back to Redivis's export when the cap answers; the Stata and R packages do not yet (an open item for the second pass, session 1014).
- **The Stanford remote test, with the citation's new words: 8 passed, 3 failed.** The citation checks pass. The three failures are the draft's age and this machine's tables, not the package:
  - the current year's 114 peak-premium rows, recomputed since the upload;
  - 5 rows of `eia860m_retired_generators`, where an untyped number column reads "1200.0" from the CSV and "1200" from Redivis;
  - `eia_drilling_monthly`, which is not on this machine.
- **`release_v1.py --check` reports 13 tables the record now puts in version 1 that the table list lacks**: the data machine's new tables since session 664. This predates the session; the rebuild needs the tables and is the data machine's (the command is in the release note).

## What to review

1. `docs/redivis/release-v1-stanford/README.md`, "Read it in Python, Stata or R" (the text Redivis would show).
2. `docs/reviews/redivis-v1-release-note-2026-10-23.md`, "After the click".

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `release_v1.py --target stanford --calls-only` | 0 | 193 rows with their fetch lines |
| `release_v1.py --target stanford --check` | 1 | 13 tables new to the record, not in the list (see above) |
| `runs/redivis1010.py rows` (2 requests) | 0 | the cap's 400 on the draft; 404 on v1.0 |
| `runs/redivis1010.py counts` | 0 | 160 the same, 43 grown |
| `test_backends_stanford.py`, remote | 1 | 8 passed, 3 failed (above) |
| `tests.test_session1010` | 0 | 3 tests OK |

## The landing

With 1000 to 1010.

## Decisions made without you

1. **`--calls-only`** rather than a rebuild of the table list on this machine, whose tables are older than the data machine's.
2. **The remote test's three failures left as they are**: they compare the draft's age, not the package.

## For Samuel's ruling

- Nothing new. The release's number (the note's item 1) still stands, and the click is yours.

## Files

- Changed: `warehouse/redivis/release_v1.py` (the fetch columns, `--calls-only`, the README section); `docs/redivis/release-v1-stanford/README.md`, `tables.csv`; `docs/reviews/redivis-v1-release-note-2026-10-23.md`.
- New: `tests/test_session1010.py`; this report.
