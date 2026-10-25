# Session 2578 report: two more held tables described (ba_supply_monthly and ai_power_regions, each a note of its own pointing to its method)

25 October 2026, about 02:30 to 02:35 UTC, on lab-desktop (the data machine), chain 127, unattended. Precheck passed (`runs/c127/pre2578.out`). Model spend USD 0. Pulls: none.

## Read these first

- **Three held tables had no note** after chain 126 (session 2564's list), beside the eight the unlanded chains 118 to 120 describe (left alone) and this chain's own (session 2583's): `ai_power_regions`, `ba_supply_monthly` and `large_load_statements`.
- **Two described, each a note of its own:**
  - **`docs/methods/ba_supply_monthly.md`:** the method is the section "Who supplies a grid (session 68)" of `grid_network.md`, which chain 120's unlanded branch changes, so a note of its own points there rather than a `Tables:` line in that file. Checked against the table by code: 158,503 rows, January 2019 to September 2026, 473 entities (83 balancing authorities, 390 pairs), 630 thin months of 7,455. No scheduled job runs its builder (`warehouse/derived/ba_supply.py`, last run 2 October 2026); the note says so.
  - **`docs/methods/ai_power_regions.md`:** the method is the AI gigawatts report's appendix (`docs/reports/ai_gigawatts_methods.md`). Checked by code: 187 rows, 7 regions, 31 measures.
  - Their Method cells set in `docs/coverage.md` (`runs/c127/cells.py`).
- **Left (one):** `large_load_statements`, whose method is in `docs/accelerator/large_load_eighty.md`.
- **Tests:** the 1,760 tests that read the notes, the cells or `docs/methods` pass but for test 705, the worktree artifact (`runs/c127/s2578_tests.out`).

## Decisions made without you

- **A note of its own for `ba_supply_monthly`,** so that chain 120's landing meets no second change to `grid_network.md`.

## For Samuel's ruling

- None.

## Files

- New: `docs/methods/ba_supply_monthly.md`, `docs/methods/ai_power_regions.md`, this report.
- Changed: `docs/coverage.md` (two Method cells).
- On the data machine only: `runs/c127/cells.py`, `runs/c127/s2578_tests.out`.
