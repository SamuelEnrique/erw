# The packages' open items

Energy Research Warehouse (ERW), written by session 1039 (chain 071, `queue/done/071-night-23-october-code-allgrids-packages.md`) on 23 October 2026, from chain 070's note (`docs/state/review_2026-10-25_code_chain070.md`, "Waiting for you"), chain 070's reports and chain 071's sessions 1032 to 1037. One line an item: what it is, who it waits on, and what is done once it is answered. The specification is `docs/methods/packages.md` (version 1). To answer an item, write "Answer: ..." under it; chain 072's sessions 1043 and 1058 read this file.

## Waiting on you

| # | Item | From | What follows the answer |
|---|---|---|---|
| 1 | **The Stata and R runs**: the three commands in Stata and R on your laptop, and the conformance runners `packages/conformance/run_stata.do` and `run_r.R` (the commands are in `archive/sessions/SESSION_1033_REPORT.md`). Whatever differs goes in `docs/reviews/packages-owner-run.md` | 1003, 1005, 1006, 1033 | every finding fixed in the package it concerns, with its test or conformance line (chain 072, session 1054). Until then the Stata and R packages' Redivis export path (1014) is unproven |
| 2 | **The Python package's license** (the `pyproject.toml` reads `LicenseRef-Not-Yet-Chosen`) | 1002 | the license file and the classifier written; the wheel rebuilt |
| 3 | **The R package's license and maintainer** (`R CMD check` warns on both) | 1005 | the `DESCRIPTION` fields written |
| 4 | **The PyPI upload** (the distribution `erw-energy`; nothing is uploaded by a session) | 1002 | yours to run; the README's install lines then name PyPI first |
| 5 | **The Redivis click**: releasing the Stanford draft, and the release's number (the release note's item 1, `docs/reviews/redivis-v1-release-note-2026-10-23.md`) | 1010, 1017 | the researcher's path (1017) walked on the released version; the packages' `auto` reads history from it |
| 6 | **Whether the downloads are public** (`/api/download`, the internal view only) | 1009, 1037 | the route's internal check removed and the links shown, the license filter kept (chain 072, session 1058) |
| 7 | **Whether `/llms.txt` may be public** (the internal view only) | 1013, 1037 | its internal check removed (session 1058) |
| 8 | **The guide's account of the downloads** (`docs/guide.md`) | 1009 | the guide's paragraph written as ruled |
| 9 | **The price board tables' ERCOT figures** on the Grid tool, while the record holds `price_board_latest` and `price_board_peak_offpeak` whole for their ISO-NE, MISO and NYISO rows | 1012 | the package's refusal and the page's figures made to agree as ruled |

## Waiting on time or another machine

| # | Item | From | When |
|---|---|---|---|
| 10 | **The conformance file made again**: call 7 (ERCOT's demand on 18 October) leaves the live set's 35 days about 22 November | 1006, 1034 | chain 072, session 1055 (`make.py`, `write_runners.py`) |
| 11 | **`ferc_eqr_contracts_history`'s partition test** stops on "Column 'market' ... does not exist" on this code machine's 5 October copy | 1035 | read on the data machine's current file (chain 072, session 1056) |
| 12 | **`node_basis_daily` for researchers**: out of the live set (session 483) and not in the released Stanford dataset, so the package reads it only from a clone's tables until the release | 1032 | with item 5 |

## Housekeeping for you

| # | Item | From |
|---|---|---|
| 13 | **A folder outside Temp**: `C:\Users\lossa\AppData\Local\Temperw1002` (session 1002's scratch: a venv and five tables, 26 MB; a path joined without its separator). Nothing in it is needed; delete it when you like | 1035 |

## Closed

- The six calls in three packages, the conformance file, `/data`'s panels and lines, the download route and `/llms.txt` behind the internal cookie, the release package's three languages (chain 070).
- The package reproduces the All grids tab's figures (1032); the install from a clean venv (1035); the data pages' accessibility and 390 (1036).

## State (session 1043, chain 072, 23 October 2026 at about 07:50 UTC)

No item answered: no "Answer:" line under items 1 to 9, and no `docs/reviews/packages-owner-run.md`. Sessions 1054 and 1058 read this file again.

## State (session 1060, chain 072, 23 October 2026 at about 08:10 UTC)

- Items 1 to 9: none answered.
- Item 10 (the conformance file before 22 November): **closed** by session 1055 (call 7 on a table the live set keeps 430 days; the next call leaves the window about 9 January 2027).
- Item 11 (`ferc_eqr_contracts_history`'s partition test): open; not read by this chain.
- Item 12 (`node_basis_daily` for researchers): open, with item 5. Chain 049's new public tables (`ercot_node_places`, `eia411_capacity_margins_annual` and four more) are in the same state: not in the live set, in the Stanford draft only (1053).
- New: the package's three new error sentences (1056) are in the Stata and R packages too, unproven there until item 1's run.

## State (session 1076, chain 073, 23 October 2026 at about 09:45 UTC)

The conformance file's version 2: 20 of 20 against today's live set. The earliest call to leave the live set's window is call 10 (the daily intensity of 1 to 7 October), about 9 January 2027; the file is made again before then. Items 1 to 9: none answered.

## State (session 1505, chain 158, 6 November 2026 at about 10:55 UTC)

**Items 1 to 9, yours, in plain words, each with a recommendation.** None has an "Answer:" line, and there is no `docs/reviews/packages-owner-run.md`.

1. **Run the Stata and R packages once on your laptop.** No machine of the project has Stata or R, so the two packages and their conformance runners have never run. *Recommendation*: run `packages/conformance/run_stata.do` and `run_r.R` once (the commands are in session 1033's report), and the three replication do-files of chain 158 (`replication/<tool>/replicate.do`) in the same sitting. Write what differs in `docs/reviews/packages-owner-run.md`. This is the one item that unblocks the most.
2. **Choose the Python package's license.** `pyproject.toml` says "not yet chosen". *Recommendation*: the license the repository's code will carry (MIT is the usual choice for a research client); the data keep their own licenses, which `docs/licenses.md` records per table.
3. **The R package's license and maintainer.** *Recommendation*: the same license as the Python package, and you as maintainer with the project's address, not a personal one.
4. **The PyPI upload of `erw-energy`.** *Recommendation*: after items 1 and 2, and not before; the wheel is built and its example runs (state below).
5. **The Redivis click** that releases the Stanford draft. *Recommendation*: release version 1 after reading the release note's diff (`docs/reviews/redivis-v1-release-note-2026-10-23.md`); nothing in the packages waits on anything else.
6. **Whether the downloads are public.** `/api/download` answers the internal view only. *Recommendation*: public for the tables whose license verdict is public, the license filter kept (the route already refuses a held table by name, session 1502). The explorers' and the tools' download lines then work for every reader.
7. **Whether `/llms.txt` may be public.** *Recommendation*: public with the downloads (6): it describes them.
8. **The guide's account of the downloads.** *Recommendation*: write it once 6 is ruled; a session can draft it from the route's own words.
9. **The price board's ERCOT figures in the package while the record holds the board's tables whole for the held grids.** *Recommendation*: hold the held grids' rows by row, as the live set's hold does since session 499, so the package and the page agree.

**The items that are not yours:**

- **The README's local test line.** `python -m pytest package/tests` on this code machine's clone: 150 failed, 597 passed, 54 skipped (801 tests, 7 min 18 s). Every failure compares the clone's older files with the record: 87 row counts against `docs/coverage.md`, 30 partition tests (a partitioned table missing or behind), 10 entities tables, 8 citations naming the commit, 6 types, and five that read the record's newer license verdicts and source registry. None is a fault of the package. The README's line now says so with today's count. The fix is `python scripts/sync.py` on this machine, a warehouse write this chain does not make, for a session that may.
- **The wheel's example.** **Runs.** `pip wheel ./package --no-deps` builds `erw_energy-0.1.0-py3-none-any.whl`. Installed into a folder of its own and run from inside the clone, the README's six calls each answer: 633 tables; Henry Hub's 2025 closes, 247 rows, the version line naming local files and the ERW commit; the citation; the verdict `public`; the standard's 13 columns; no request made.
- **The conformance file on today's live set.** **Made again, version 3, and 20 of 20.** On today's live set, call 06 (`eia860m_retired_generators`, the generators retired by month) had grown from 249 to 260 rows, now to September 2026, so version 2 passed 19 of 20. `packages/conformance/make.py` wrote version 3 (call 06's expectation and the file's date the only changes), `write_runners.py` wrote the Stata and R runners from it, and `run_python.py` passes 20 of 20 (21 reads of the live set). The Stata and R runners wait for item 1.
- Item 11 (`ferc_eqr_contracts_history`'s partition test) is the data machine's copy of that table, and item 12 (`node_basis_daily`) waits on item 5. Both are unchanged.
