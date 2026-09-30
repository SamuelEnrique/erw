# SESSION 46: Gate check, the 3D network, and a year of hub prices

## Part 0 (first)
1. /severance/lease: turn off Next.js link prefetch on that page so no request fires
   after a file is loaded. Commit.
2. Read daily-prices run 13 (workflow_dispatch, commit 5c00e9d).
   - Passed: the gate is open. Do Part A, then Part B.
   - Still running: check every 10 minutes, up to 60 minutes, then decide as above; if
     still running after 60 minutes, do the fallback.
   - Failed: read its log, fix the failing step on main, trigger one workflow_dispatch
     (approved), then do the fallback without waiting.

## Part A (gate open): session 42
Read SESSION_42_PROMPT.md and execute it end to end: its rules, its approved
interchange pull, the 3D network at /network. Write its report as
SESSION_42_REPORT.md, replacing the stub.

## Part B (gate open): a year of hub prices
Rules: USD 0, no model calls. Approved pull (Samuel, Sept 30): 2025-09-01 to the
latest day of main-hub day-ahead and real-time prices for CAISO (SP15 and the NP15
zone), MISO (Indiana Hub), NYISO (N.Y.C.), ISO-NE (.H.INTERNAL_HUB) and SPP
(SPPNORTH_HUB), at the ISO's native interval, kept as history tables past the rolling
window. Ceiling 1.5 million rows. License checked before loading; raw files saved;
resumable. History tables stay out of Supabase (live set about 343 MB, warning 350).
1. Connectors, validator, archive, coverage, Redivis draft upload, run_status, source
   registry. The daily run appends to the histories, never trims.
2. Rebuild cost_of_power_* with twelve months for every ISO; the ranked bar and the
   calculator use the latest complete month every ISO holds. Report old and new
   defaults side by side.
3. /learn/bill: PG&E's wholesale reference switches to NP15, labeled.
4. Problem sets: answers the new data changes recompute; check.
5. check-values, check-routes, tests/, deploy, live checks.

## Fallback (gate not open)
USD 0, no pulls, no model calls.
1. Battery game v1.1: flag 100-percent-of-perfect scores on the leaderboard; a fleet
   panel showing ERCOT's real battery fleet from storage_capacity beside the fictional
   10,000 homes; a share card generated in the page (no upload); famous days link to
   their /events page where one exists.
2. Problem set D, "Storage and taxes", five questions, answers computed, never typed,
   from storage_daily_cycle, cost_of_power_hourly_profile, lib/battery.ts and the
   severance rules.
3. check-values, check-routes, tests/, deploy, live checks.

## Always
Pull and merge if the daily job lands, never force push. Commit after every working
step.

## Report: archive/sessions/SESSION_46_REPORT.md
Part 0 outcome and which path ran; rows pulled against each ceiling; cost of power old
against new; what shipped; Supabase before and after; decisions made without a human;
open questions; wall time; spend USD 0 confirmed. Push. Stop.