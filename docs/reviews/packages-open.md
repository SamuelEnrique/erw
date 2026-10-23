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
