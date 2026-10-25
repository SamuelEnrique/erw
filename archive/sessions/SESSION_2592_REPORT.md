# Session 2592 report: the last held table described (large_load_statements, a note of its own pointing to its method)

25 October 2026, about 03:41 to 03:45 UTC, on lab-desktop (the data machine), chain 128, unattended. Precheck passed (`runs/c128/pre2592.out`). Model spend USD 0. Pulls: none.

## Read these first

- **One held table had no note** after chain 127 (session 2578's list), beside the eight the unlanded chains 118 to 120 describe (left alone) and this chain's own (session 2597's): `large_load_statements`.
- **Described:** `docs/methods/large_load_statements.md`, pointing to its method in `docs/accelerator/large_load_eighty.md` (with the pilot and forty notes before it) and to `datacenter_cost.md`'s "How long a large load waits" for the site's use of its aggregates. Checked against the table by code: 798 rows, 113 entities in 83 groups, 763 from the eighty chosen entities and 35 outside them, 598 `mw` rows and 200 `wait` rows, 171 distinct wait figures, documents dated 2024-05-01 to 2026-10-08. Its Method cell set (`runs/c128/cells.py`).
- **With it, every held table outside the unlanded chains' eight has a note** (this chain's own get theirs in session 2597).
- **Tests:** the tests that read the notes, the cells or `docs/methods` pass but for test 705, the worktree artifact (`runs/c128/s2592_tests.out`).

## Decisions made without you

- **A note of its own** rather than a `Tables:` line in an accelerator page, as `docs/methods` is where the coverage cells point.

## For Samuel's ruling

- None.

## Files

- New: `docs/methods/large_load_statements.md`, this report.
- Changed: `docs/coverage.md` (one Method cell).
- On the data machine only: `runs/c128/cells.py`, `runs/c128/s2592_tests.out`.
