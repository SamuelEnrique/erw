# Session 5003 report: the datacenter tool, and the owner's ruling on the foreseen load applied

Energy Research Warehouse (ERW). Chain 233, portable laptop window P1, 13 November 2026, about 10:20 to 10:50 UTC. Opus 5.5. Model spend USD 0.

- Branch `wip/5000-datacenter`, cut from `wip/5000-generator`.
- Read on session 5001's build at 1280 and 390: 249 keys, no error, no sideways scroll.
- Faults file `docs/reviews/datacenter-cost-faults-2026-11-13.md`: 3 rows (2 fixed, 1 not a fault).
- **The ruling of 12 October 2026 applied**: "if perfectly foreseen" takes the rule's hour budget in a partial year. It was in `docs/roadmap.md` but not in the code. `weights()` now takes `min(hours held, shedBudget(...))`.
  - No default figure moves (the default load is flat).
  - The note's worked flexible example, on its frozen inputs of 10 October: foreseen 29.72 to 29.29, "kept 57 percent" to 51, day-ahead 30.54 to 30.19; each old figure kept beside the new.
  - The decisions line "foreseen" and the note's line 7 state the ruling; section 10 item 15 closed.
- The note's item 4 (load zones stop on 3 October; no schedule) closed by session 204.
- Battery faults row 7 (data machine): the battery and generator pages hold no October 2026 while the datacenter page does.
- Tests: the 32 files that touch the datacenter library, note, decisions or cost note: 459 passed, 23 skipped (exit 0). New: `site/scripts/test-foreseen-5003.mjs` (8 assertions), `tests/test_session5003.py`.
- Not built after the change: the next build (session 5004's) carries it.

## Decisions made without you

- The ruling applied to both ways of turning off ("hours" and "share"), as finding 1's recommendation reads ("min(hours held, the rule's budget)").
- The faults file named `datacenter-cost-faults-2026-11-13.md` so that it is not confused with the datacenter tracker's file.

## For Samuel's ruling

- None new. The flexible figures that moved are listed above; check them on the page with "Turn off in 100 hours a year".
