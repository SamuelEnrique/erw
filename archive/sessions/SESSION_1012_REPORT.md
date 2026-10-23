# Session 1012 report: the package reads what the pages read

23 October 2026, from about 03:42 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1012` on `wip/1012-packages` (cut from `wip/1011-packages`). Chain `queue/done/070-evening-22-october-code-packages.md`, session 1012. Model spend USD 0. No warehouse data written. Requests: the live set 10 or fewer (the remote test's fetches of six tables).

## Read these first

- **Ten figures of the site, recomputed by the Python package from the same table and window.** Each has the check key the page writes; check-values reads the same keys.
  - The pages: the Grid tool's ERCOT page (five of its own, two of the price board's tables it shows, one of the generation mix) and the battery page (two). `/board` itself writes no keys; it is drawn from a built file.
  - The figures were recorded from a build of `wip/1011-packages` in the internal view (`package/tests/page_figures.json`).
- **Eight of ten reproduce exactly** (`package/tests/test_page_figures.py`, remote: 8 passed, 2 skipped). No fault in the package or in the pages' library.
- **The two skipped are the price board's tables** (`price_board_latest`, `price_board_peak_offpeak`).
  - Their license verdict is `unsettled`: held whole for their ISO-NE, MISO and NYISO rows.
  - The package refuses them on the live set, as the specification says, and this machine's own copies predate 22 October.
  - **The Grid tool shows their ERCOT figures.** Session 505's list of held figures that still show does not name them. This is listed for your ruling.
- The method note lists the ten keys with their results ("The package reads what the pages read").

## What to review

1. `docs/methods/packages.md`, "The package reads what the pages read".

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `runs/keys1012.py` on the build | 0 | 77 keys on `/grid/ercot`, 184 on the battery page, 0 on `/board` |
| `test_page_figures.py`, remote | 0 | 8 passed, 2 skipped |
| `tests.test_session1012` | 0 | 3 tests OK |

## The landing

With 1000 to 1012.

## Decisions made without you

1. **The local build, not production**, for the page values (no other host).
2. **Local files for the tables the live set does not hold**, and for the held price board tables, which the live set must refuse.

## For Samuel's ruling

- **The Grid tool shows figures of `price_board_latest` and `price_board_peak_offpeak`**, tables the license record holds whole. Their ERCOT rows are public by ERCOT's terms. Either the page's figures are held too, or the record holds those tables row by row (session 499's `hold: row`).

## Files

- New: `package/tests/test_page_figures.py`, `page_figures.json`; `tests/test_session1012.py`; this report.
- Changed: `docs/methods/packages.md`.
