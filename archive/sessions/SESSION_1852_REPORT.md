# Session 1852: the deal tracker's faults fixed, first batch (chain 213, 12 November 2026)

Energy Research Warehouse (ERW). Chain 213, session 1852, samueloldlaptop, unattended, Fable 5.1. About 11:05 UTC on. Long end 1:30. Precheck passed.

## What it did, with commits

- Worktree `C:\Users\lossa\Documents\erw-1852` on `wip/1852-deals`, cut from origin/main `2451e3fb6` (main had not moved since 1851's push).
- **`8d2db06b1`, the fixes of rows 2 to 6, 14 and 15 of `docs/reviews/deals-faults-2026-11-11.md`:**
  - row 2, `site/app/deals/v2/view.tsx`: `Choices` takes `held`; under the hold no bracket is drawn ("All types", "ERCOT", not "(0)"), and the panel's note says "no count is shown while every row is held" instead of "0 of the 0 deals name a US state";
  - row 3, `site/app/deals/ai/view.tsx`: the two top-ten lists are of the deals whose kind of supply is not capital (`supplyOf(d) !== "capital"`); the xAI acquisition at 1.25 trillion, the OpenAI rounds and the NextEra and Dominion merger leave the "Deals for AI power" lists and stay in the table's Capital and acquisitions row; each section's note says so;
  - row 4, the same file: a list line whose row has no buyer and no seller prints the other parties (GE Vernova, NRG; Brookfield, NextEra, DOE) before "parties not stated";
  - row 5, the tracker's headline: ", USD 3,929.79 billion in all" is gone; the count of deals that state a value stays, with what a value is;
  - row 6: the five tables of the tracker, the comparables, the prices and the AI view lose `bg-accent text-white` and take `/deals`'s own header style (`border-b border-rule text-left text-xs text-muted`), `docs/brand.md` section 5;
  - row 14, `comparables/view.tsx`: the group whose dimension is not stated is left out of the chart's bars and the "n of m" count; the table keeps it;
  - row 15: `usd()` in `DealsTable.tsx`, `usdWords` in the AI view and the formatter of `check-values.mjs` take a trillion step (1,250,000,000,000 is "1.25 trillion").
  - `tests/test_session1852.py`, 10 tests: the source rules above, `largest` run in Node on four fixture deals with the view's filter (the capital rows out, the PPA and the gas plant in), the formatter's words ("1.25 trillion", "2.17 trillion", "19 billion", "938 million").
- The deals tests in the worktree after the patch: 111 passed, 5 skipped, 1 failed, `test_session113.test_it_is_in_review_and_the_older_page_is_as_it_was`, which asserts `git status` is clean for `DealsTable.tsx`: it failed on the uncommitted change and passes once committed. The 10 new tests pass.
- The faults file's seven rows marked `fixed (8d2db06b1, wip/1852-deals)` on main.
- A junction of the main copy's `node_modules` into the worktree does not build (Turbopack: "Could not find the Next.js package"), so the worktree ran `npm ci` (541 MB) and then `npm run build`; the install passed and the build compiled in 41 s with 290 MB available during its TypeScript step. **The build was stopped by Claude Code for low memory** at "Generating static pages (546/729)", after the TypeScript step had passed, together with the background table sync (67 of 112 tables restored) and the waiter on the build's log; the machine had 290 MB available and the harness asks that a command it stopped for memory not be started again unattended. So the branch is proved by its tests, not by a build, until a landing session's gate builds it (or the owner says the builds may be retried); the worktree's partial `.next` is not served. After the kill 1,524 MB were available.

## Decisions made without you

- Row 5's headline note names what a value is (a purchase price, a financing or a valuation) rather than summing by kind in the headline: the sums by kind are on the AI-power view, and a headline figure that mixes them is what the fault was.
- Row 3 is fixed in the view, not in `lib/dealsai.ts`'s `largest` (session 2240's tests pin its behaviour on every AI deal); the view passes it the non-capital deals.
- The 1853 work (the hover cards) was prepared in the same worktree and waits for this build's result before its own branch and commit.

## For Samuel's ruling

- None new.
