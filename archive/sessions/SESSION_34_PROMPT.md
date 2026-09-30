# SESSION 34: Carried items from sessions 30 to 33

## Read first
CLAUDE.md, PRIORITIES.md, docs/datastandard.md, archive/sessions/SESSION_30_REPORT.md
(sections 3 and 6), SESSION_31_REPORT.md (section 6), SESSION_32_REPORT.md (open
questions), SESSION_33_REPORT.md (open questions), warehouse/raw/eia930_emissions/,
the /storage and /emissions pages, the Thesis Builder, the package's filter code, the
daily workflow file.

## Budget and rules
- Expected Anthropic API spend: USD 2. Hard cap: USD 4 (ERW_SPEND_CAP_USD=4,
  ERW_SESSION=34). The only model calls allowed: one Thesis Builder run (item 3).
- No pulls of any kind. Every new row in this session comes from files already saved
  under warehouse/raw/ or from tables already in the warehouse. If an item would need
  a pull, skip it and say so.
- No redundant work: read the saved workbooks once, build every emissions variable
  from that one pass. One table in memory at a time; stream with pyarrow.
- The daily job may land while you work: pull and merge before pushing, never force
  push.
- Every number on a page comes from a warehouse table. No placeholders.

## Items, in order, one commit each
1. /storage: add CAISO's own battery series (caiso_battery_storage) beside the EIA-930
   series, labeled as CAISO's data with its own tier chip and citation, so CAISO is no
   longer blank. The daily cycle table gets CAISO rows from it, marked by source.
2. Battery energy capacity (MWh): check whether the EIA-860M generator file carries it.
   If it does, add the column to the three eia860m_*_generators tables and to
   storage_capacity (approved), and show fleet MWh on /storage. If it does not, say so
   and change nothing.
3. Thesis Builder: give the landscape (company list) its own call. Run it once on the
   geothermal thesis; report companies found and the bill against 2 companies at
   USD 1.23.
4. Emissions from the saved workbooks, no new download: add the by-fuel CO2 variables
   (coal, gas, oil, other) and imported and exported CO2 to eia930_all_emissions.
   Approved ceiling for the added rows: 4 million. Same completeness rule.
5. Carbon intensity back to 2018: rebuild carbon_intensity_hourly and _daily using the
   workbooks' own net generation and demand columns (saved), so intensity runs from
   2018-07 instead of 30 days; add carbon_intensity_monthly. Keep the warehouse-based
   version for the last 30 days as a check and report the difference. Extend /emissions
   with one block: monthly intensity since 2018 per ISO.
6. erw.filter and _table_facts: cache each local file's facts on disk (invalidated by
   file mtime) so filter(node=...) no longer scans the 0.7 GB history on every call.
   Report the before and after time of one call.
7. Package tests: the Redivis and Supabase backend tests run only with an explicit
   marker or env var; the default run skips them. The workflow keeps its 20-minute
   timeout.
8. The shadow emails: confirm the daily job sends the SHADOW HAIKU digest and Roundup
   to Samuel only, expiring 2026-10-06, and that the real Sonnet digest goes to the
   subscriber list. Fix anything that is not so.
9. Known gaps and run health: bring the known-gap list, PRIORITIES.md and the run
   status in line with everything that changed in sessions 29 to 33 (the CARB carry-
   forward, the storage and emissions steps, the test step). Report the gate state.

## Part D: verify and ship, last
Validator on every changed table, archive (new rows under existing names, append-
only), Supabase sizes before and after, Redivis draft counts equal to CSVs, license
check, coverage, llms.txt, the chat catalogue, package tests (default set) and
tests/, check-routes and check-values, deploy, live checks again.

## Do not
No pulls, no model calls beyond item 3, no deletions from Redivis, no gate changes,
no force push, no new pages.

## Report: archive/sessions/SESSION_34_REPORT.md
Each item done or not and what changed; rows added per table against the 4M ceiling;
the intensity comparison; the filter timing; Thesis Builder companies and bill; spend
from the ledger against the cap; decisions made without a human; run health and gate;
whether the daily job landed; open questions; skipped. Commit after every item. Push
at the end. Stop.