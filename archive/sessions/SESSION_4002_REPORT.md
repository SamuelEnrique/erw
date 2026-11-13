# Session 4002 report: the landing desk, the portable laptop's row 18 (urgent)

Energy Research Warehouse (ERW). Chain 228, the desktop's second window, 13 November 2026 from 10:17 UTC. Opus 5.5. Model spend: USD 0.

## The requests read at the session's start (10:17 UTC)

- `landing_request_oldlaptop.md`: row 9 in flight (session 4000's landing).
- `landing_request_portable.md`: two new rows.
  - Row 17, `wip/5000-battery` (`abbcdeb71`, window P1).
  - Row 18, `wip/5100-security` (`e1f954c5`, window P2), **URGENT**: a visitor could read a page in review at its `.segments/...segment.rsc` addresses.

## Row 18: landed at `b1ea7427a`

- **What was gated:** `wip/w2-5100-security`, a copy of the branch's newest head `7fd58dfe3` (the row's head and the session's report), with `origin/main` merged as `197173eba`. P2 keeps stacking on its own branch, so no merge was pushed onto it.
- **The gate** (`gate_held.sh`, task `5101-curtain`, port 5100), 10:19 to 10:53 UTC:
  - the suite: 8,640 tests OK, 382 skipped;
  - `npm ci` and the build (94 s) passed;
  - check-routes passed; check-cross-checks passed all 92; check-csp ran 97 pages with 0 violations;
  - check-values had one failure, main's own `/digest` floor (`cv_diff`: 0 new);
  - `check-curtain.mjs` against the gate's own server: exit 0.
- **The landing:**
  - Freeze none. Snapshot `w2-s4002-sec-before` at 10:53.
  - `task/5101-curtain`: run 43412644633 passed and merged at 11:07 (`b1ea7427a`). The deploy succeeded at 11:08.
  - Snapshot after: **0 differences**.
- **The proof the gate cannot give:** `node site/scripts/check-curtain.mjs https://erw-flame.vercel.app` after the deploy: **exit 0**. No page in review is readable at a transport address (8 pages, 32 addresses). It was not run before the deploy, to keep production reads to the snapshots and this one command the row asks for.
- **Marked:** on main as `7f739ee68`, with snapshots before and after: 0 differences.

## Row 17 (and 19 to 22)

- **Row 17's gate was stopped** while it was still waiting for the build lock: window A's gate (`c226-gate`) had taken the lock 4 seconds after row 18's gate released it.
- **Rows 19 to 22 then arrived**, each stacked on the one before. Landing `wip/5000-grid` (`7f01f500d`) lands all five, so it goes in session 4003's combined gate.

## Decisions made without you

- **Row 18 went before row 17**, although row 17 was requested first: row 18 said a visitor could read pages in review that day.
- **A branch whose owner keeps committing is gated as a `wip/w2-*` copy**, so this desk never pushes a merge onto it.
- **A row 17 gate stuck behind the lock was stopped for the stack's top.** The stopped processes were this window's own (`w2-s4002b`), and no acquirer was left.

## For Samuel's ruling

- None.
