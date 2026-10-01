# SESSION 57: Severance v1, the Texas refund finder and a Louisiana pilot

## Read first
CLAUDE.md, docs/datastandard.md, archive/sessions/SESSION_40_REPORT.md,
SESSION_41_REPORT.md, SESSION_45_REPORT.md and SESSION_49_REPORT.md (Part D),
warehouse/connectors/rrc_production.py, the saved dump under warehouse/raw/rrc_pdq/,
site/data/severance_rules.json, site/lib/severance.ts and lease.ts, /severance,
/severance/lease and the internal real-lease page (how it is served behind the token).

## Who it is for
A severance tax consultant at a firm that today pulls well data from a vendor and
works it by hand in Excel. The question is: which leases may be paying more severance
tax than the rules require, and how much might they save?

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- Texas: no new download. Read every county from the RRC dump already on disk
  (OG_COUNTY_LEASE_CYCLE and whatever lease, well and operator tables the dump holds),
  streamed, one county at a time, never the whole file in memory. License internal,
  as session 49 recorded.
- Louisiana: approved pull (Samuel, Oct 1): first read and record the terms of the
  Louisiana Department of Energy and Natural Resources' public production data
  (SONRIS); proceed only if public access allows reuse (internal if unclear). One
  major producing parish (state why), the latest 24 months of production by lease or
  well. Ceiling 300,000 rows.
- Internal data never goes into git, the public database, public Redivis or any
  committed JSON; serve it the way the session 49 real-lease page is served. Pages
  behind the internal token.
- Every rule from site/data/severance_rules.json with its citation. "May qualify" is
  never "qualifies": every flag states which test the data meets, what it cannot see
  (certification, filings already made), and that it is not tax advice.
- No time cap; no redundant work; pull and merge if the daily job lands, never force
  push; commit after every working step. If a part fails, record it and continue.

## Part A: Texas statewide
1. A statewide lease-month table (internal) from the dump: county, district, lease,
   operator, oil and gas and condensate volumes, the latest 24 months held.
2. The refund finder (warehouse/derived/severance_screen.py): for every lease-month,
   test the rules the data can test:
   - low-producing oil lease credit (Comptroller's per-well-per-day threshold over the
     90-day window, the certified price tier for that month);
   - low-producing gas well credit (the volume threshold, the certified price tier);
   - two-year inactive wells (a lease with no production for 24 months that resumes);
   recording, per flag, the test met, the months, and the estimated tax at the base
   rate against the tax with the credit at warehouse prices (WTI, Henry Hub, labeled).
   Where a rule needs facts the dump lacks (well counts per lease if absent, water
   cut, certification), say so in the flag and estimate only what the data supports.
3. Summaries: candidates and potential savings by county, by operator (top 50), and
   by rule; the largest single leases.
4. Page /severance/finder (internal): statewide totals, a map or ranked table by
   county, the operator table, a lease drill-down that opens the lease in the lease
   tool, and a plain method box. Download as CSV.

## Part B: Louisiana pilot
The pull above, a table (license per its terms), and the lease tool's "Load a real
lease" gains the Louisiana parish, with Louisiana's flags (stripper, incapable,
inactive) from the rules file.

## Part C: verify and ship
Hand-computed checks: one Texas oil lease and one gas lease through the finder,
against the lease tool's own calculation; one Louisiana lease; tests; check-routes;
deploy; live check that the finder answers 404 without the token.

## Report: archive/sessions/SESSION_57_REPORT.md
Counties and rows read; candidates and potential savings by rule, county and the top
operators (counts and totals only in the report, no lease names beyond the top ten
operators); what each flag can and cannot see; Louisiana terms, parish and rows
against the ceiling; decisions made without a human; questions only Samuel can answer
from his Ryan work; wall time; spend USD 0 confirmed. Push. Stop.