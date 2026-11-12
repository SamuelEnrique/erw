# Session 3804 report, with 3805: the findings, and the Stanford draft

Energy Research Warehouse (ERW). Chain 215, data machine (lab-desktop), 12 November 2026 18:50 UTC. Opus 5.5. Model spend USD 0. Requests: none.

## 3804, the findings

- **The landing requests:** every row of `docs/state/landing_request_portable.md` (1 to 16) and `docs/state/landing_request_oldlaptop.md` (1 to 8) is an ancestor of main and marked landed, as chain 212's session 3786 found today. Nothing to land.
- **The drafts:** 185 of 185 reproduce (`check.py`, session 3794, on the tables as the data machine's run left them). The cards and do-files were checked today by chain 212's session 3787 (185 of 185 each) and no draft has changed since. The count by family is unchanged.
- **Nothing approved, nothing published.**

## 3805, the Stanford draft

- **Not uploaded: the data lock was held.**
  - This chain's one new public table, `iso_reserve_margin_reports`, is ready (verdict public, in the license record and the release list, held from v1 until the owner adds it).
  - The lock passed from the data machine's run (to 18:17 UTC) to the dispatched daily run (43276079255, from 18:17), which keeps it for about two and a half hours.
  - The upload goes to the next file's first unfinished steps.
- **`--reconcile` was not run** (several hundred count requests, beyond the cap).
- **The records:**
  - `package/tools/build_tables.py --check` passes;
  - the tests of sessions 1001, 1008 and 1009 pass (session 3798);
  - `scripts/build_llms.py` was run after the last coverage row on the branch.

## Decisions made without you

- **The upload waits for the lock** rather than holding the daily run's lock past its own 60-minute wait.

## For Samuel's ruling

- None new.
