# Session 5160 report: the fresh pass, part 2: input limits and rate limits, route by route

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5150-security`, worktree `erw-p2-5150`. Model spend USD 0. Pulls: one read-only transaction on the database (counts only). Nothing built, nothing landed, no warehouse data written.

Clock: precheck 19:32 UTC, the tests by 19:38 UTC. Inside the long end of 1:00.

## Read these first

- **Nothing to fix.** All 41 route handlers read: every word a handler takes from the address is bounded before it is used.
- **Now a test holds that.** A handler that starts to read the address, or loses its bound, fails the suite until someone reads it and lists it (`tests/test_session5160.py`).
- **Two things noted, not changed:**
  - Row 29. A download writes a text value into its CSV as the source wrote it. A value beginning with `=`, `+` or `@` would be read as a formula by a spreadsheet. **No such value exists in the public live set today** (2.85 million rows, every text column read).
  - Row 30. A failed read answers with what failed (the table's name, the status, the database's short answer). No address, key or row is in those words.

## What to review

1. `docs/reviews/security-faults-2026-11-13.md`: rows 29 and 30, and the paragraph "Session 5160".
2. `tests/test_session5160.py`: `READS_THE_ADDRESS`, the list of 16 handlers with the line that bounds each.
3. `docs/security.md`: the 13 limits by name.

## What was done

- **The table** (`runs/s5160/routes.py`, output beside it): for each handler its methods, what it reads from the address, its body, its limits, what it touches, its size checks, its origin check, its release or internal check.
- **The ones that showed no size check and no limit were read in full**: the board's, the map's and the resource layers' rows are built once (`force-static`); `/companies/rows` answers from memory through `queryOf`, which keeps 80 characters of the search and looks every other word up; the problem sets' CSV and the companies' CSV look their path segment up in a list; `/api/play/top` takes a preset the game writes and a date in the form of a date.
- **The read of the live set** (`runs/s5160/formula_cells.py`, read-only): `entities` 105,619 rows, `events` 57,864, `series` 2,684,962, `latest_prices` 39, `catalogue` 184, `sources` 735, `headers` 1,534. In no text column does a value begin with `=`, `+`, `@`, or a minus followed by something that is not a digit.
- **The test**, 9 tests: the 16 handlers and their bounds; the bound before the database is asked; the filters the download and the companies' list lean on; the 13 limits, each name one the database's function takes and each with one pair of numbers.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5160 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged |
| `runs/s5160/routes.py` | 0 | 41 route handlers |
| `runs/s5160/formula_cells.py` (read-only) | 0 | none in seven tables |
| `pytest` on `test_session5160`, `5159`, `5102` | 0 | 41 passed |

- **Not run:** the build, the whole suite, any request of a route.
- **Not verified:** the five CSV routes of the cost-of-power tools line by line (window P1's files, changing today); they are in the list without a pinned line.

## Decisions made without you

- **Row 29 left to the data side.** Changing a cell in a download changes data a reader's code reads. A rule in the validator would stop such a value before it is loaded; that file is the data machine's.
- **Row 30 left as it is.** The ERW says what failed, on its pages and in its answers.
- **The tools' CSV routes listed without a pinned line**, so this test does not break window P1's work on them.

## For Samuel's ruling

1. Row 29. Default: no change. Alternative: the validator refuses a text value that begins as a formula would (a session on the data machine).
2. Row 30. Default: no change. Alternative: an API's failure says only "the read failed" and logs the rest.

## The prompt

`queue/done/237-day-14-november-portable-p2-security-continued.md`, "Sessions 5159 to 5162: a fresh pass".
