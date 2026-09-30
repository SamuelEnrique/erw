# SESSION 40: Severance tax engine v0 (Texas, Louisiana, New Mexico)

## Read first
CLAUDE.md, docs/datastandard.md, the WTI and Henry Hub series in the warehouse, the
/cost-of-power page and its lib as the calculator pattern.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- No data pulls. Reading statute and state agency pages as text is allowed; rates go
  in a versioned site data file, not a warehouse table and not Supabase.
- Target 45 minutes. Pull and merge if the daily job lands, never force push.
- Every rate, exemption, threshold and effective date carries a citation to a page
  whose text states it: the state statute (Texas Tax Code, Louisiana Revised Statutes,
  New Mexico statutes), the Texas Comptroller, the Louisiana Department of Revenue, the
  New Mexico Taxation and Revenue Department. Where no page states a figure, leave it
  out and list it in the report. No rate from memory.

## Part A: the rules
`site/data/severance_rules.json` plus `docs/methods/severance.md`, per state and
product (oil, gas, condensate where distinct):
- the base rate and its basis (percent of market value, or per unit), effective date;
- the reductions and exemptions a tax consultant works with: Texas high-cost gas,
  low-producing and marginal wells, enhanced oil recovery, and any others the
  Comptroller lists; Louisiana stripper and incapable wells, the gas rate set each
  July, horizontal and deep-well incentives as the state lists them; New Mexico's
  severance tax plus its other production taxes (conservation, emergency school,
  ad valorem production), each named as the state names it;
- for each exemption: who qualifies, what it reduces, how long, and its citation.

## Part B: the calculator
Page /severance (nav: a new "Tools" entry, or under Prices if no such group):
state, product, monthly volume (bbl or Mcf), price (default: the latest monthly WTI or
Henry Hub from the warehouse, labeled as a default and editable), and checkboxes for
the exemptions that apply. Output: tax due at the base rate, tax due with the chosen
exemptions, and the savings, with each line citing its rule. A clear note that this is
an estimate for education and planning, not tax advice, and that deductions such as
marketing costs vary by state and are listed, not computed, where the rule is not
explicit. Stanford palette, mobile-safe, method link.

## Part C: verify and ship
Unit tests of the calculator for each state and product against hand-computed cases
from the cited rules; check-routes covers /severance; tests/; deploy; live check.

## Do not
No pulls, no model calls, no Supabase table, no rate without a citation, no force push.

## Report: archive/sessions/SESSION_40_REPORT.md
Every rule with its citation; figures left out for lack of a source; the test cases;
wall time; spend USD 0 confirmed; open questions for Samuel (he worked these taxes at
Ryan LLC, so list the questions only he can answer). Commit. Push. Stop.