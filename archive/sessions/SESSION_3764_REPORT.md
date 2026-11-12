# Session 3764 report: the All grids tab reads the tariffs and the connection rules

Energy Research Warehouse (ERW). Chain 211, session 15 of 24, data machine (lab-desktop), 12 November 2026. Opus 5.5. Model spend USD 0. Requests: none.

- **`warehouse/derived/siting_page.py`** writes two new files (`1578466fe` on `wip/c211-code`):
  - `site/data/siting/tariffs.json` from `utility_large_load_tariffs`: each utility's filed schedules by EIA id, every figure with its page and printed words, the filing, the status, the notes. Session 730's fields are kept, so its rate picker still reads it. `held` lists the EIA ids of schedules held for a license: 14006, AEP Ohio.
  - `site/data/siting/conn_rules.json` from `large_load_connection_rules`, by grid: CAISO 7 steps, ERCOT 27, PJM 12, SPP 13.
- **`site/lib/siting.ts`**:
  - Outside ERCOT, a row whose utility (the tab's Utility column) files a held schedule shows that schedule's per-kW month figure in words in the Transmission and 4CP cell, with the whole filing on hover (`tariffWords`).
  - A held schedule reads "licensed source needed".
  - The cell draws no USD per MWh, so **the all-in is unchanged**.
  - Time to connect adds "filed steps": a hover with the grid's stated steps, durations first (`filedSteps`).
  - The two column tips name the new tables.
- **`site/app/cost-of-power/AllGridsView.tsx`**: one hover link beside the load line. Inputs stay left, results right; no layout change.
- **Records:**
  - `docs/methods/siting.md`: a dated decision.
  - `docs/reviews/siting-gaps.md`: a state section of 12 November (two rows filled in part; FERC-714 held, not yet drawn; what stays open).
- **Tests:**
  - `test_session730`'s "not wired" test became "wired as words, not into the all-in" (the chain asks for the wiring).
  - `tests/test_session3764.py` (4).
  - The 39 test files that read the siting code: 155 tests, OK after the change.
  - Type check: no error in the edited files.
- **The tab read at 390 and 1280:** on the gate's kept build, with the landing (see session 3773's report).

## Decisions made without you

- **Words, not a figure in USD per MWh.** A demand charge per kW-month becomes per MWh only through a load factor and the schedule's other parts (generation, riders), which the tab would have to invent. The cell shows the printed figure and its filing; the all-in stays as it was, so no default figure moves.
- **The row's utility is the tab's own Utility column's.** Rows without a known utility (PJM's hubs, no one state) still read "not held".
- **The FERC-714 revision is not drawn in Headroom yet:** carried to chain 212 with the tab's next pass.

## For Samuel's ruling

- None new.
