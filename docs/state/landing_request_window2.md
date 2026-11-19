# Landing requests: the desktop's second window (chain 502, the findings hunt of 19 November)

Energy Research Warehouse (ERW). Written by chain 502 (`queue/done/502-day-19-november-desktop-window2-findings-industry.md`), lab-desktop's second window, which does not land. The first window's desk lands each row marked requested, in order, through `scripts/land_check.py`, and marks it landed with the commit. Each branch is code only: the drafts, reports and progress are already on main. No page changes what a visitor sees: the code writes findings drafts, read only at `/internal/findings`.

| # | Branch | Head | Task | Port | Requested (UTC) | Tests on this machine | State |
|---:|---|---|---|---:|---|---|---|
| 1 | `wip/8201-findings` | `84d106e33` | `8201-findings` | 3502 | 2026-11-19 11:12 | on the head (cut from `origin/main` at `27e616d3a`): the 36 test files that load the findings code (`findings_common`, `hunt`, `builder`, `check_do`, `deep`), with the new `tests/test_session8201.py`: 297 passed, 5 skipped, 0 failed, in 164 s. The whole suite not run here (the window runs no gate). Changes: `warehouse/analysis/findings/deep/hourly930.py` and `trade.py` (new), `builder.py` (chain number and plan settable, default 164 unchanged), `check_do.py` (a loop is one block; a folder may be named) | requested |
