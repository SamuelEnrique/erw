# SESSION 43: Electricity bill explainer v0 (education)

## Read first
CLAUDE.md, the /cost-of-power page and cost_of_power_monthly (wholesale reference),
the /grid/<iso> template and docs/grids/*.md (the written-layer rules), the severance
rules file and its quote check (the citation pattern to copy).

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- No data pulls. Reading tariff and utility pages as text is allowed; rates go in a
  versioned site data file with the quoted passage behind each, checked against the
  page text as session 40 did. No rate from memory.
- No uploads, no user data stored.
- Target 50 minutes. Pull and merge if the daily job lands, never force push.

## The tool
1. `site/data/bill_rules.json` for two bills:
   a. California: PG&E residential time-of-use (E-TOU-C), current summer and winter
      rates, baseline credit, and the named line items on a PG&E bill (generation,
      delivery, and the named charges and credits PG&E lists), from PG&E's tariff
      pages.
   b. Texas: a home in the Oncor area of ERCOT. The retail energy charge is set by
      the retailer, so it is a user input with a labeled default; Oncor's delivery
      charges (monthly customer charge, per-kWh delivery) from Oncor's current tariff
      or rate summary; any state or ERCOT pass-through charges the tariff names.
   Each line: what it is, why it exists (one plain sentence for a student), its rate
   and basis, and its source with the quoted passage and effective date.
2. Page /learn/bill (nav: a new "Learn" entry, which also lists the seven grid pages
   and the events): choose California or Texas, enter monthly kWh (default 600,
   labeled as an assumption) and for California the share of use in peak hours;
   the page draws the bill line by line with totals, then a bar splitting the total
   into wholesale energy (from cost_of_power_monthly for the ISO's latest complete
   month, load-weighted) and everything else, with a plain sentence on why the rest
   exists (wires, poles, programs). Every number cited, a "written, cited" chip on the
   text, the calculator's defaults computed server-side.
3. A short glossary (ten terms) and links to /grid/caiso or /grid/ercot and
   /cost-of-power.

## Verify and ship
Hand-computed test cases for both bills at 600 and 1,000 kWh; a test that every line
has a quote, a date and an https source; check-routes and check-values cover the page;
tests/; deploy; live check.

## Do not
No pulls, no model calls, no uploads, no Supabase table, no rate without a quoted
source, no force push.

## Report: archive/sessions/SESSION_43_REPORT.md
Every line and rate with its source; figures left out for lack of a source; the test
cases; the wholesale share on each default bill; wall time; spend USD 0 confirmed;
open questions. Commit. Push. Stop.