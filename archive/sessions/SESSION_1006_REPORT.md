# Session 1006 report: one test, three packages

23 October 2026, from 03:28 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1006` on `wip/1006-packages` (cut from `wip/1005-packages`). Chain `queue/done/070-evening-22-october-code-packages.md`, session 1006. Model spend USD 0. No warehouse data written. Requests: the live set 47 of 50 (26 to make the file, 21 for the Python runner); Redivis none.

## Read these first

- **`packages/conformance/conformance.json`: twenty calls with the answers the Python package gave**, made once by `make.py`. The calls:
  - ten fetches (rows, first and last time), the calls of session 1003's fixtures with two windows closed so the answers stay fixed: Henry Hub in 2025 is 247 rows from 2 January to 31 December;
  - four citations (the words before the clause naming where the rows came from);
  - three licenses (a public table, a "license needed" one and an internal one);
  - the refusal of `iso_rtm_hub_prices` on the live set, word for word;
  - the standard of an entities table;
  - the table list of the record (299 tables, 195 public).
- **The Python runner passes 20 of 20** (`run_python.py`, `results_python.json`).
- **The Stata and R runners are written from the same file** (`write_runners.py`: `run_stata.do` in your style, `run_r.R`); a test holds them in sync with it. Neither ran here (no Stata, no R).
- **`docs/methods/packages.md` gains "The conformance file"**: the table of which calls each package passes. Python passes all twenty. Stata and R wait on your runs; their ten fetch addresses already equal Python's.
- **One thing the file depends on**: the fetch of ERCOT's demand on 18 October is in the live set's 35 days until about 22 November; the note says how to make the file again.

## Your commands

In Stata, with the command installed and the two globals set (session 1003's report): `do packages/conformance/run_stata.do`. In R, with the package installed and the two variables set: `source("packages/conformance/run_r.R")`. Each prints a line a call and the count that pass.

## What to review

1. `docs/methods/packages.md`, "The conformance file (session 1006)".
2. `packages/conformance/conformance.json`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `make.py` (the live set, 26 requests) | 0 | 20 calls |
| `run_python.py` (the live set, 21 requests) | 0 | 20 of 20 pass |
| `write_runners.py` | 0 | the two runners |
| `tests.test_session1006`, `tests.test_session1000` | 0 | 10 tests OK |

## The landing

Sessions 1000 to 1006 land together from this branch (below, once done).

## Decisions made without you

1. **The table list is the record's** (coverage.csv, 299 tables), as the Stata and R packages read it; the live set's catalogue lists 134.
2. **Two windows closed** in the fetches, so the answers do not move as the tables grow.
3. **Stata's refusal is checked by its code (498)**, since a do-file cannot read an error's words.

## For Samuel's ruling

- Nothing new.

## Files

- New: `packages/conformance/` (`make.py`, `conformance.json`, `run_python.py`, `results_python.json`, `write_runners.py`, `run_stata.do`, `run_r.R`); `tests/test_session1006.py`; this report.
- Changed: `docs/methods/packages.md`.
