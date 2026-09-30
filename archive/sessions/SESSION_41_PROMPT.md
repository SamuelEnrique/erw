# SESSION 41: The daily job, then severance v0.1

## Read first
CLAUDE.md, .github/workflows/daily-prices.yml, archive/sessions/SESSION_40_REPORT.md,
site/data/severance_rules.json, site/lib/severance.ts, docs/methods/severance.md.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- No data pulls from this machine. One workflow_dispatch of daily-prices.yml is approved
  (it is the normal daily pull). Reading statute and agency pages as text is allowed.
- Target 40 minutes. Pull and merge if the daily job lands, never force push.

## Part 1, first: the daily job
Run #10 (workflow_dispatch, commit 0f94942, 2026-09-30 18:24 UTC) failed in about 70
seconds. Today's scheduled run started 18:40 UTC. Read both job logs through the GitHub
API. If the scheduled run passed, say so and do not change the workflow. If either
failed, find the failing step and its cause, fix it on main, trigger one
workflow_dispatch run, and watch it until it passes the step that failed (do not wait
for the whole run). Report the gate state.

## Part 2: severance v0.1, the gaps session 40 listed
1. Texas Tax Code chapters 201 and 202: read them from statutes.capitol.texas.gov's
   plain document pages (Docs/TX/htm/TX.201.htm and TX.202.htm) and cite the sections
   behind each Texas rule next to the Comptroller's page; add EOR's duration where the
   code states it.
2. New Mexico current rates: find the rates in force in 2026 for the four production
   taxes and the reduced rates (stripper, enhanced recovery, workovers) in a readable
   source that states them: TRD's current rate tables or publications, or the statute
   text on law.justia.com or the Legislature's site. Replace the 2021-22 table only with
   a source that states the current figures; otherwise keep the dated label.
3. Texas certified prices: find the Comptroller's current certified average prices for
   the low-producing oil and gas credits, explain the date inconsistency session 40
   saw, and if the table is clear, store it in the rules file with its date so the
   calculator picks the credit tier from the price instead of asking.
4. Tests: new hand-computed cases for anything that changed; check-routes and live
   check after deploy.

## Do not
No pulls from this machine beyond the one approved workflow run, no model calls, no
Supabase table, no rate without a quoted source, no force push.

## Report: archive/sessions/SESSION_41_REPORT.md
Part 1 in five lines: failing step, cause, fix, commit, whether the new run got past it
and the gate state. Part 2: every rule changed with its source, what is still missing.
Wall time, spend USD 0 confirmed. Commit after each part. Push. Stop.