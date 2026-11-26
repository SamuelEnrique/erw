# Session 10219 report: grid conditions (`/conditions`) audited as a hostile expert would

Chain 710, part D, the old laptop, 26 November 2026, worktree `erw-c710-a`, branch `wip/audit-conditions-doc`. Model spend USD 0; no live service asked; no table written; no lock taken.

## What was done

- `docs/reviews/conditions-model-audit-2026-11-26.md` and its evidence folder: the ground, every figure of the default view and each operator's opening view restated to the digit from the page files, the scarcity strip restated from ERCOT's adder table (5,428 of 5,428), the alerts list from its two inputs, seven rules measured one at a time, each claim set against the code, eleven numbered findings.
- **The arithmetic is right.** 15,921 daily figures checked against the files' hours; the only differences are the rounding of the hours the file keeps (74 outage means 0.1 MW apart; 143 ERCOT days with adders above zero kept as 0.0, finding 6).
- Findings: 2 major (1: an impossible hour printed as PJM's peak, 215,682 MW against 108,513 screened; 2: the alerts count is rows, not notices), 4 moderate (3, 5, 6, 8), 5 minor (4, 7, 9, 10, 11).
- Branches: words for landing 2, 5, 6, 8, 9, 10, 11 and their merge `wip/audit-conditions-words`; tests only, for the owner, 1, 3, 4, 7. Each words branch drawn to HTML with the site's components and its words read (pass); every drawn figure unchanged.
- Window F's finding (alerts cut at 40) still stands on main; its branch `wip/c750-conditions` conflicts with these words branches on `page.tsx`.

## Decisions made without you

- The scope is `/conditions`. It prints no reserve margin, peak against capacity, stress score or scarcity-hour count; the headroom cell of `/cost-of-power` (capacity over peak, ERCOT's reserve margin) was restated as the nearest such figure, and `grid_stress_yearly` and `scarcity_hours_by_grid` were described, not re-done.
- Finding 11's words replace window F's `clockWords` line, because F's words still say hours run on the local clock; the desk takes F's `alerts.map` with this line when both land.
- Finding 5's words say ERCOT's notices are read "when a session reads them, not each day"; scheduling the connector is left to you (a chain installs no schedule).
- The note's figures of finding 6 (5,799 of 10,492 hours under 5 cents) are written into the page's hover: the adder ended in 2025, so they will not move.

## For Samuel's ruling

- Finding 1: apply the ERW's rule for impossible hours to `/conditions`' demand? PJM's COVID-window peak 215,682 MW becomes 108,513. Default: left as it is.
- Finding 3: count alerts by notice, without ERCOT's updates and statements? CAISO's 2020 heat wave 79 becomes 23. Default: left as it is.
- Finding 4: read CAISO's three other time formats? 15 rows since 2018 get a start and end (two Stage 3 outages of August 2020). Default: left as it is.
- Finding 7: count the adder at USD 1 (or 100)? The COVID window's 20 hours become 6 (or 3). Default: left as it is.

## Needs the key

- Nothing. Data requests (constraint counts by contingency, CAISO's outages by kind, the screen over all EIA-930 demand) are in the audit's last section.

## Problems

- One test run (finding 2's, with `test_session147.py` among the note readers) let that test write its own temporary files to the system temp folder before TMP was pointed inside the worktree: a write outside the worktree, against the brief. From finding 5 on every python run had TMP, TEMP and TMPDIR under `runs/c10219/tmp`.
