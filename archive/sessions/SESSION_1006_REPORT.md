# Session 1006 report: one test, three packages

23 October 2026, from about 03:10 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1006` on `wip/1006-packages` (cut from `wip/1005-packages`). Chain `queue/done/070-evening-22-october-code-packages.md`, session 1006. Model spend USD 0. No warehouse data written. Requests: **the live set 68, over this session's ceiling of 50** (26 to make the file, 21 for the Python runner, and 21 more when a failed patch left the runner to make all twenty calls again: see "Read these first"); Redivis none.

## Read these first

- **`packages/conformance/conformance.json`: twenty calls with the answers the Python package gave**, made once by `make.py`. The calls:
  - ten fetches (rows, first and last time), the calls of session 1003's fixtures with two windows closed so the answers stay fixed: Henry Hub in 2025 is 247 rows from 2 January to 31 December;
  - four citations (the words before the clause naming where the rows came from);
  - three licenses (a public table, a "license needed" one and an internal one);
  - the refusal of `iso_rtm_hub_prices` on the live set, word for word;
  - the standard of an entities table;
  - one table's row in the record's table list, and at least 299 tables (a count of the tables, the first form, failed as soon as main brought 8 new tables).
- **The Python runner passes 20 of 20** (`run_python.py`, `results_python.json`).
- **The Stata and R runners are written from the same file** (`write_runners.py`: `run_stata.do` in your style, `run_r.R`); a test holds them in sync with it. Neither ran here (no Stata, no R).
- **`docs/methods/packages.md` gains "The conformance file"**: the table of which calls each package passes. Python passes all twenty. Stata and R wait on your runs; their ten fetch addresses already equal Python's.
- **The ceiling was passed**: call 20 first expected the record's count of tables (299). After main brought 8 tables it failed, and its new form needed a patch that did not apply. The runner then ran all twenty calls again, 21 live requests the session did not need. The runner now takes `--only N`, and call 20 was run again alone with no request. Its result is marked `rerun_alone` in `results_python.json`.
- **One thing the file depends on**: the fetch of ERCOT's demand on 18 October is in the live set's 35 days until about 22 November; the note says how to make the file again.

## Your commands

In Stata, with the command installed and the two globals set (session 1003's report): `do packages/conformance/run_stata.do`. In R, with the package installed and the two variables set: `source("packages/conformance/run_r.R")`. Each prints a line a call and the count that pass.

- **After merging main** (the data machine's chain 046 landed 8 tables, `ercot_cdr_reserve_margins` and `ercot_transmission_projects` among them):
  - the shipped license record was written again: 307 tables, from 299;
  - the two remote tests that compare citations (`package/tests/test_backends.py`, `test_backends_stanford.py`) now cut at the release's words ("Via", and the table in backticks);
  - they run in session 1010, which has Redivis requests.

## What to review

1. `docs/methods/packages.md`, "The conformance file (session 1006)".
2. `packages/conformance/conformance.json`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `make.py` (the live set, 26 requests) | 0 | 20 calls |
| `run_python.py` (the live set, 21 requests; then 21 more, unneeded, at 19 of 20 before call 20's new form; then `--only 20`, no request) | 0 | 20 of 20 pass |
| `write_runners.py` | 0 | the two runners |
| `tests.test_session1006`, `tests.test_session1000` | 0 | 10 tests OK |

## The landing

Sessions 1000 to 1006 land together from this branch (below, once done).

## Decisions made without you

1. **The table list is the record's** (coverage.csv, 299 tables), as the Stata and R packages read it; the live set's catalogue lists 134.
2. **Two windows closed** in the fetches, so the answers do not move as the tables grow.
3. **Stata's refusal is checked by its code (498)**, since a do-file cannot read an error's words.
4. **The table list is checked by one table's row and a floor of 299 tables**, not by a count that moves with every new table.

## For Samuel's ruling

- Nothing new.

## Files

- New: `packages/conformance/` (`make.py`, `conformance.json`, `run_python.py`, `results_python.json`, `write_runners.py`, `run_stata.do`, `run_r.R`); `tests/test_session1006.py`; this report.
- Changed: `docs/methods/packages.md`; `package/src/erw/data/tables.csv` (307 tables); `package/tests/test_backends.py` and `test_backends_stanford.py` (the citation's cut).
