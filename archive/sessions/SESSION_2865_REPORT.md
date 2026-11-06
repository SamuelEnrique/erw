# Session 2865 report: the periodicals fixes landed

5 November 2026, about 22:38 to 23:52 UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend USD 0. Pulls: none but the snapshots and GitHub reads.

## Read these first

- **`wip/2206-periodicals-fixes` landed as `a557483a7`.** It brings the Digest audit's five fixes and item 7: a stored issue keeps its figure, and the page says in a note when the warehouse holds a revised value.
  - Merged with main (`fcafee62`), task branch run 42125660114 passed at 23:12 UTC, deployed at 23:13.
  - Snapshots `s2865-before` and `s2865-after`: **0 differences**.
- **`wip/818-periodicals` landed as `f8853197b`.** Chains 801 to 817: the why line's rule, one topic one item, the outlet named, the numbers that moved, the chart of the day by relevance, the Roundup's five numbers, the emails' tables.
  - Merging main into it gave three conflicts, resolved in `8aff12b6`:
    - `warehouse/news/brief.py`: 818's seven hype words and 2206's `TERM` guard both kept; 2206's `window_rows` used, which is 818's filter plus the stamp's bounds.
    - `scripts/check_digest.py`: 2206's `compare()` for the fuel close; 818's demand line goes through `compare()` too.
    - `site/lib/digest.ts`: `Place` keeps both optional fields, `cell` and `label`.
  - `tests/test_session807.py` now reads the window's filter in `window_rows`, where it moved.
  - 190 periodicals tests pass.
  - Task branch run 42130421266 passed at 23:50 UTC, deployed at 23:51. Snapshots `s2865b-before` and `s2865b-after`: **0 differences**.
- **The gates** (`runs/land_check/ae005e24...`, `.../<818's sha>`):
  - Suite 7,351 and 7,488 tests OK; npm ci, build and serve passed.
  - check-values had 12 failures each, all main's own, none new.
  - **The WTI line passes on 2206's build:** "revised: page shows 101.91 as the issue printed it, its note says 96.34". That is the check-values proof on `/digest/2026-10-21` the laptop's session 2207 asked for; the page's other 8 figures read ok.
- **Branches on origin:** both are ancestors of main. Their deletion was refused by this machine's permission settings and is left for the owner: `wip/2206-periodicals-fixes`, `wip/818-periodicals`, and the `task/` branches of this chain.
- **Worktrees:** `erw-2206` and `erw-818-periodicals` are kept until session 2870.

## Decisions made without you

- **Landed with check-values' known failures** (session 2863's decision). The floors of `/digest` and `/learn/problems/know-your-grid` wait for the daily run's data.
- **The conflicts resolved by keeping both sides' rules** wherever they did not contradict.

## Files

- New: this report.
- On the data machine only: `runs/c147/resolve_818_*.py`, `runs/c147/t818.out`, the snapshots.
