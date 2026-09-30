# SESSION 36A: Health, open items, and reopening the gate

## Read first
CLAUDE.md, PRIORITIES.md, archive/sessions/SESSION_34_REPORT.md and SESSION_35_REPORT.md
(open questions), the EIA-930 demand connector and its per-day rule for ERCO and NYIS,
warehouse/metadata/build_coverage.py, warehouse/supabase/load.py, the Thesis Builder,
docs/grids/, docs/grids/grids.json, the datacenter facilities table.

## Budget and rules
- Expected Anthropic API spend: USD 1.50. Hard cap: USD 3 (ERW_SPEND_CAP_USD=3,
  ERW_SESSION=36A). Model calls allowed: one Thesis Builder run (item 4) and one scoped
  chat question (item 5).
- No data pulls, re-pulls or backfills. Reading ISO and EIA web pages to verify dates in
  item 7 is allowed (text read, nothing stored in the warehouse).
- No redundant work. Pull and merge if the daily job lands, never force push.

## Items, in order, one commit each
1. eia930_swpp_demand: apply the per-day completeness rule that ERCO and NYIS demand use
   (session 13), so a day with missing forecast hours is a recorded gap, not a failed
   table. Confirm with the 2026-09-28 case. State in the report whether tomorrow's run
   would pass the gate with this and session 33's coverage fix.
2. build_coverage.py: stream large tables with pyarrow (only the needed columns), as the
   package tests now do. Report the build time before and after.
3. Supabase: load the six by-fuel and trade CO2 variables of eia930_all_emissions for the
   last 90 days. If the live set would pass 380 MB, use 30 days and say so. Vacuum and
   report size before and after.
4. Thesis Builder: widen the research prompt to name adjacent drillers, plant developers
   and technology providers in scope. Run once on the geothermal thesis (new research
   pass). Report companies found and the bill against session 30 (7 companies in the
   earlier per-sheet run, 2 since).
5. Scoped chat: ask CAISO its question from session 35 once more with the fixed loop.
   Report the answer, citation and cost.
6. Datacenters to grids: where a facility row names a utility, map it to its ISO; else
   fall back to the state lists. Record the mapping rule in docs/methods. Update the
   grid pages' counts and check keys.
7. Written layer dates: for every dated event in docs/grids/*.md, find a page on the
   ISO's, EIA's or FERC's site whose text states that date, and cite it inline. Check
   NYISO's start of operations specifically. Where no page states the date, say so in
   the report and soften the text to the year only.

## Part D: verify and ship, last
Validator on changed tables, coverage, archive, Supabase, Redivis draft counts equal to
CSVs, license check, llms.txt and the chat catalogue, tests/, check-routes and
check-values, deploy, live checks.

## Do not
No pulls, no new tables, no new pages, no model calls beyond items 4 and 5, no deletions
from Redivis, no gate code changes beyond item 1, no force push.

## Report: archive/sessions/SESSION_36A_REPORT.md
Each item done or not; the gate forecast for tomorrow's run; coverage time before and
after; Supabase size; Thesis Builder companies and bill; the CAISO answer; datacenter
counts per grid before and after; every date changed or confirmed with its source; spend
from the ledger; decisions without a human; open questions; skipped. Commit after every
item. Push at the end. Stop.