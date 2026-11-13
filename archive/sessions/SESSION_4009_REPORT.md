# Session 4009 report: window 4's row 4 (Wisconsin), and a revised demand figure that failed every gate

Energy Research Warehouse (ERW). Chain 228, the desktop's second window, 13 November 2026 from 16:15 UTC. Opus 5.5. Model spend: USD 0.

## Land-e: window 4's row 4 to `ea34a1ea8`

- **`wip/w2-land-e`** is land-d's commit `15c54b483` with `wip/4250-forecast` (`37c92a6b4`; past `ea34a1ea8` only the request file) merged: `96489ad29`.
- **Before the gate:** `build_llms.py --check` exit 0; the forecast's tests with 1903 and 412: OK.
- **The gate**, 16:16 to 16:48 UTC:
  - the suite, the build, check-routes, check-cross-checks and check-csp passed;
  - check-values failed on two lines:
    - `/policy`'s floor: the license hold's, shown as "license needed";
    - **`/digest/2026-11-12`, `digest_demand|eia930_all_demand|eia930:US48|demand_mw|2026-11-11T23:00:00Z`: the page printed 488,034, and the live set held 488,341.**
- **The demand line:** EIA revised its hourly demand after the issue was written. The stored issue keeps its figure, as Samuel's ruling of 23 October (item 7) asks. But only fuel closes had the revision note (session 2207), so every gate on main failed on that page from 13 November. It is main's state, not the forecast's, so land-e was landed on its hand checks.
- **The landing:**
  - Snapshot `before-96489ad2`, then the push to `task/4009-landing` at 16:48.
  - (the merge and the after snapshot: written when they come)

## The fix, on this window's branch (in land-f, session 4010)

- **`site/lib/digestLive.ts`**: `digestRevisions` also reads each US48 demand peak hour from the live set, whole MW.
- **`site/lib/digest.ts`**: the note reads "The publisher revised the US48 demand peak hour for <day> after this issue was written: the warehouse now holds 488,341 MW; the issue printed 488,034 MW and keeps it as its record."
- **`site/scripts/check-values.mjs`**: `digest_demand`'s note is read as a pass, as `digest_dam`, `digest_rt` and `digest_fuel` are.
- **Tests:** test 2207's two pins were brought to the new lines. The digest tests (2207, periodicals_1973, periodicals, 804, 3823, 402) pass.

## Decisions made without you

- **A failure that is main's own state lands with its row on the hand checks.** Here that was a publisher's revision of a stored issue's figure. It is written down, and fixed in the next gate.
- **Window 4's commits past `ea34a1ea8`** (`93a66d4ee`, code) wait for a new row.

## For Samuel's ruling

- None.
