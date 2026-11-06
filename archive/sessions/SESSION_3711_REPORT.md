# Session 3711 report: why main was red

Energy Research Warehouse (ERW). Chain 208, session 12 of 20, portable laptop, 6 November 2026, about 22:49 to 23:10 UTC (while session 3706's gate ran). Commit on main: `docs/state/main_red_2026-11-06.md`.

- **Spell 1, 30 October 18:31 to 5 November 22:17 UTC:**
  - The data machine's "Page files 2026-10-30" (`137e9dfb7`) rewrote page files that tests held to dated figures.
  - Reproduced: tests 701, 709 and 720 passed at the parent (15 tests) and failed at the commit (2 failures, 1 error).
  - The calendar added `test_session174` on 1 November and three more on 2 November.
  - It was invisible because the daily run's "merge tests" step recorded a NumPy warning as its reason, and the job stayed green.
- **Spell 2, 6 November 01:32 to 02:59 UTC:**
  - The runner's catch-up commit (`e2794ff06`).
  - Reproduced: 8 modules passed at the parent (87 tests) and failed at the commit (8 failures, 4 errors).
  - Causes: a new table without its license row, and the thin rebuild. The thin rebuild is root-caused in `warehouse/scheduled.py`: `mix_profile`'s inputs did not name `caiso_fuel_supply_history`, so its absence on the runner went unseen.
- Neither commit had the suite run on it. The merge gate tested branch heads, not branches merged with main.

## Decisions made without you

- The causes are written from the commits and reproduced, not from the earlier notes alone; each named test was run at the commit and its parent in clean worktrees (since removed).
- GitHub answered two pushes to main with "Internal Server Error" at 23:09 UTC; the third, a minute later, went through.

## For Samuel's ruling

- None new.
