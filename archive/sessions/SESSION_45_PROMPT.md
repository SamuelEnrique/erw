# SESSION 45: Loader vacuum, gate check, then 42 or severance v0.2

## Part 0 (first, 5 minutes)
1. Supabase loader: run VACUUM (ANALYZE) after each daily load instead of VACUUM FULL;
   keep FULL behind an explicit flag for manual use, documented in the runbook. The
   350 MB warning stays. Commit.
2. Read daily-prices run 12 (workflow_dispatch, commit 9fb7d93).
   - Passed: read SESSION_42_PROMPT.md and execute it end to end (its rules, its
     approved pull, its report), then stop; do not do Part B.
   - Failed: read its log, fix the failing step on main if under 15 minutes, trigger
     one workflow_dispatch (approved), do not wait. Then Part B.
   - Still running: say so and do Part B.

## Part B: severance v0.2, the lease tool
Read first: site/data/severance_rules.json, site/lib/severance.ts, /severance,
docs/methods/severance.md, archive/sessions/SESSION_41_REPORT.md.
Rules: USD 0, no model calls, no data pulls, no Supabase table, no rate without its
quoted source. Pull and merge if the daily job lands, never force push.

1. /severance/lease (linked from /severance): the user drops a CSV or pastes rows:
   state, well id, month, oil bbl, gas Mcf, condensate bbl (optional), price per
   product (optional; default the month's warehouse WTI or Henry Hub, labeled), well
   facts where a rule needs them (completion date, depth, horizontal, days produced,
   water cut, drilling cost ratio for Texas high-cost gas). The file is parsed in the
   browser and never sent to the server; say so on the page.
2. Output per well and month: base tax, tax with the exemptions the user ticks, and a
   "may qualify" flag for each rule whose thresholds the well's own numbers meet
   (Texas low-producing oil and gas using the certified price of that month,
   Louisiana stripper and incapable, inactive wells, New Mexico district rates), each
   flag citing its rule. A summary: totals per well and for the lease, and the
   largest potential savings first. Download as CSV.
3. A sample CSV (clearly fictional wells, labeled) to try it, and a template to fill.
4. Tests: a hand-computed three-well, two-month lease for each state; the flag logic
   against thresholds; a test that the page makes no network request with the data.
   check-routes, tests/, deploy, live check.

## Do not
No pulls beyond an approved Part 0 path, no model calls, no server upload of user data,
no Supabase table, no force push.

## Report: archive/sessions/SESSION_45_REPORT.md
Part 0 outcome (vacuum change and run 12); if Part B ran, what the tool does, the test
leases with hand results, which flags fire on the sample, wall time, spend confirmed,
questions for Samuel. Commit. Push. Stop.