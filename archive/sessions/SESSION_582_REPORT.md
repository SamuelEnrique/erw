# Session 582 report: the five tools' replications, run in a clean environment

22 October 2026, from about 00:00 UTC, unattended, on samueloldlaptop (the code machine), chain 034 (`queue/done/034-night-22-october-code.md`, part "Session 582"), branch `wip/582-s` cut from `origin/wip/506-combined` and merged with `origin/main`. Precheck 0. Model spend USD 0. No warehouse data written. Requests: the live set with the public (anon) key (the Grid tool's file and the datacenter's carbon file, as their writers read it), production's own pages (`erw-flame.vercel.app`, opened with the internal cookie as `check-values.mjs` opens them) and PyPI (the scratch environment's packages, from the repository's `requirements-py314.txt`). Not landed: session 589 lands the chain.

## Summary

Each of the five tools' replications ran in a new virtual environment outside the repository (`C:/Users/lossa/Documents/erw-582-venv`, removed at the end), from a folder holding only the files its page links, and every figure it prints that the page also shows was set beside the page's figure on production. Battery 23 of 23 equal, generator 16 of 16, datacenter 36 of 36 after one fix (33 of 36 before), Research 363 of 363 against the cards' JSON and the page's 110 of 110 against the same JSON, the Grid tool 59 of 60 (the one, the Network view's lag, a page served from the previous hour's snapshot: 44 hours against the mirror's 45 on the new one, and 44 on a file written from the old). Two things were mended: the datacenter tool's carbon file was a copy of 14 October and had fallen behind the page (now rewritten, and rewritten every day by the data machine's run), and Research's mirror rebuilt nine of the ten cards `/research` shows (the tenth, `peak_hour_moved`, added). The table: `docs/reviews/replications-2026-10-22.md`.

## What was done

1. The environment: `Python314/python.exe -m venv erw-582-venv/venv` (exit 0, pip only). The battery, generator, datacenter and Grid mirrors ran in it bare (each exit 0): they need nothing beyond the standard library, as they say. Research's mirror exited 1 bare (`No module named 'numpy'`, as its docstring warns), then 0 after `pip install --no-deps -r requirements-py314.txt` (exit 0).
2. The pages: production's `/cost-of-power/battery`, `/cost-of-power/seller`, `/cost-of-power`, `/cost-of-power?buy=da`, `/grid?grid=us48&view=network` and `/research`, read at 00:11 to 00:15 UTC with the internal cookie; every `data-check` key with its raw value, and the scenario cells (`data-cell`, `data-stat`), set beside the mirrors' lines by a scratch script (equal: the mirror's printed number is the page's raw value rounded half up to the mirror's decimals).
3. **The datacenter's carbon file** (`site/public/datacenter/erw_2026_datacenter_carbon.csv`): the first run gave 265,548 tonnes a year (page 265,549), 10,160 hours in the hourly window (page 10,141) and 313.01 kg per MWh over them (page 311.74). Cause: the file was written by session 265 on 14 October; since then the monthly table's September 2026 moved (340.6896 to 340.6904, its days complete) and the 430-day window moved eight days. Rewritten from the live set with `site/scripts/write-datacenter-carbon.py` (public key, exit 0), the mirror then gave all three of the page's figures. So that it does not fall behind again, `warehouse/run_data_machine.sh` runs the writer after the hourly CSV (`soft_step dm_datacenter_carbon`) and commits the file with the page files. `datacenter_pays_algorithm.md` section 8 says the file goes stale and how (and 4.16's dated tonnes figure gains the new one).
4. **Research's tenth card**: `/research` shows six callouts of `peak_hour_moved` and no mirror rebuilt them. `peak_hour_moved()` added to `site/public/findings/erw_2026_research_replication.py` from the card's own `numbers_from_rows`: 59 figures, all equal to its JSON (363 of 363 in all). `tests/test_session422.py`'s pinned count follows (304 to 363); `docs/guide.md` says ten.
5. The Grid tool: `write-grid-replication.mjs` (public key) wrote a file of the hour 2026-10-20 03:00 UTC from the snapshot built 00:05:36 UTC, and `check-grid-replication.mjs` set the mirror's 60 figures beside production's pages (Now, Network, and the gravity shape in a headless browser, under the build lock; no browser left running): 59 equal. The Network view's lag read 44 where the mirror read 45: that view's check key names the previous snapshot (23:05:39 UTC), the Now views the new one, so the page's caches differed by view; the mirror on a file of the previous snapshot (written 00:09 UTC) printed 44. Nothing mended. The committed file (14 October) still runs (exit 0) and was left as it is: it is a dated example, and the pack says so.
6. Tests: `tests/test_session582.py`: the four standard-library mirrors run with `python -I -S` (no site-packages) from a temporary folder holding only their own files and print the lines the review compares; the datacenter mirror still runs without its carbon file; Research's mirror rebuilds `peak_hour_moved` equal to its JSON; the carbon file's header counts its own rows; the data machine's run rewrites and commits it after the hourly CSV, with the public key, writing nothing when a read fails; the method note says so; the review has a row for each tool; no em dash.
7. The datacenter and Research packs point to the review.

## Checks

| Command | Exit |
|---|---|
| `scripts/precheck.py --what "session 582"` | 0 |
| `scripts/db_probe.py` (00:09 UTC) | 0 |
| the four standard-library mirrors, bare environment, from their own folders | 0, 0, 0, 0 |
| Research's mirror, bare | 1 (numpy, expected) |
| `pip install --no-deps -r requirements-py314.txt` (scratch environment) | 0 |
| Research's mirror `--json site/data/findings` | 0 (304, then 363 figures, 0 different) |
| `node site/scripts/write-grid-replication.mjs <scratch>.csv` | 0 |
| the Grid mirror on the committed file and on the fresh one | 0, 0 |
| `site/scripts/write-datacenter-carbon.py --out <scratch>` | 0 |
| the cards' own `.py` downloads from the folder | 1, 11 of 11 (`findings_common`, waiting for Samuel since session 381) |
| the comparison against production (battery, generator, datacenter) | 1 before the carbon file (72 of 75), 0 after (75 of 75) |
| `/research`'s 110 checked figures against the cards' JSON | 0 |
| `scripts/buildlock.py acquire s582` (waited for s578, s580, s587), `release s582` | 0, 0 |
| `check-grid-replication.mjs https://erw-flame.vercel.app <fresh file>` (PYTHON the scratch environment's), twice | 1, 1 (59 of 60: the Network view's lag, the page's cache) |
| `ERW_LOCK_EXEMPT=1 python -m unittest tests.test_session582 tests.test_session381 tests.test_session422` | 0 (23 tests) |
| the session tests that read `run_data_machine.sh` or the carbon file (21 modules with 582) | 0 but `test_session244` in one process (a duplicate module name, `build_coverage`, as the memory warns); `tests.test_session244` alone: 0 |

## Decisions made without you

- The pages were read on production (main) with the internal cookie rather than on a local build: production is what a reader compares with, and the branch's changes move no page figure.
- The datacenter carbon file was rewritten from the live set (the third such rewrite, after sessions 228 and 265), and the data machine's run now rewrites it every day as a soft step; remove the step to undo.
- `peak_hour_moved` was added to Research's mirror; `batteries_lunch`, also with a JSON and a CSV, was not, since `/research` does not show it.
- A first guess that the carbon file's four decimals caused the difference was tested and was wrong (the live set holds four decimals); that change was reverted before any commit.

## For Samuel's ruling

None new. Session 381's item stands: the cards' own `.py` downloads do not run for a reader (`findings_common`).

## To finish

Nothing for this session; session 589 lands `wip/582-s` with the chain.

## Files changed

- `site/public/datacenter/erw_2026_datacenter_carbon.csv` (rewritten from the live set)
- `site/public/findings/erw_2026_research_replication.py` (the tenth card)
- `warehouse/run_data_machine.sh` (`dm_datacenter_carbon`, the file committed)
- `docs/methods/datacenter_pays_algorithm.md`, `docs/reviews/packs/datacenter.md`, `docs/reviews/packs/research.md`, `docs/guide.md`
- `docs/reviews/replications-2026-10-22.md` (new)
- `tests/test_session582.py` (new), `tests/test_session422.py` (the count)
- `archive/sessions/SESSION_582_REPORT.md`
