# Session 1905: the records and the clean-up of chain 217 (chain 219, 13 November 2026)

Energy Research Warehouse (ERW). Chain 219, session 1905, samueloldlaptop, unattended, Opus 5.5. About 03:45 to 03:50 UTC. Chain 217's unfinished step 4 (its session 1900).

## What it did, with commits

- **Branches:** chain 217's eleven branches and this chain's `wip/1903-stack`, `1907-periodicals`, `1908-periodicals` were deleted on origin by session 1903, each an ancestor of `origin/main` first; `wip/1899-digest` (session 1899, no commit of its own) deleted locally, never pushed. Its two scratch scripts kept in `runs/s1899/`.
- **Worktrees:** 4 before (the main copy, `erw-1425`, `erw-1600`, `erw-1899`), 3 after; `erw-1425` (`wip/1425-grid`) and `erw-1600` (`wip/1642-board`) are older chains' unlanded branches, left.
- **Every faults file's rows with a state:** the five tools' files, the periodicals file and the board audit, and the three paths' faults of session 1885 (session 1903 gave those their states).
- **The tests on main:** the second gate's whole suite on `2504ff817` (main's tree but for documents since): 8633 tests OK, 368 skipped.
- **`package/tools/build_tables.py --check`:** exit 1, "648 rows shipped, 648 in the record, 0 differ; the site's two files differ": the citations of `energy_deals` and `news_index` list outlets from this machine's local news tables, which are not the data machine's. This chain changed no table the records read, so nothing was rebuilt.
- **The five tools' table:** the counts unchanged after chains 217 and 219; a line says so (on `wip/1905-revert`, below).
- **One correction, `wip/1905-revert` (`211808fe4`, pushed, not landed):** reading the faults files for their states found that session 1898's lab fault 2 (the grids view printing each grid's peak, capacity and ERCOT's reserve margin, `a05a17e9b`) is the same cells as `datacenter-faults-2026-11-11.md` row 4, whose state is **ruling**: the owner decides whether a grid's public columns show while its facility counts are held (the state review's item 28). This chain's rules skip a ruling row, and session 1903 landed it in the stack. The branch puts the default back (every `dcgrid|` key the held facilities table's, the cells with footnote 1); `tests/test_session1898.py`'s fault 2 class pins the default; the lab path's fault 2 state now reads "ruling". It lands at session 1909.

## Decisions made without you

- The grids view's public columns are held again until you rule, rather than left printed: the row was reserved for you, and the default it named was footnote 1. No visitor saw either form (every page is in review).
- Session 1903's checker rule for those cells stays: it is right whenever the cells print.

## For Samuel's ruling

- Datacenter faults row 4 (the state review's item 28): whether the grids view shows each grid's peak, capacity and ERCOT's reserve margin while the facilities are held. The code to show them is `a05a17e9b` (revert `211808fe4` once it lands to show them again). Default kept: held.
