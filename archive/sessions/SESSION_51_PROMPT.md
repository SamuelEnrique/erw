# SESSION 51: Cost of power v2, the seller's side (a credit lens)

## Read first
CLAUDE.md, docs/datastandard.md, the /cost-of-power page, site/lib/cost.ts,
warehouse/derived/cost_of_power.py, docs/methods/cost_of_power.md,
iso_hub_prices_history, ercot_all_hub_prices_history, iso_rtm_hub_prices, the saved
EIA-930 per-BA extracts (check which hourly generation-by-fuel columns they hold),
eia930_all_generation, storage_capacity and the eia860m generator tables,
event_window_daily, Henry Hub series, lib/battery.ts.

## Who it is for
An investment director at a private credit fund deciding whether a power asset can
service its debt. He wants downside, not upside: the bad months, the stress days, and
coverage. Every number traceable, every assumption visible.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls. No data pulls.
- This extends the cost-of-power tool; it is not a new tool. Same methods file, same
  page family, same nav entry.
- History tables are not in Supabase (near its line): the builder writes a static JSON
  snapshot for the page, as /network does; derived tables go to the warehouse, Redivis
  and coverage, not Supabase. PJM is excluded (internal prices).
- No invented numbers: asset sizes, heat rate, variable cost and debt service are user
  inputs with labeled defaults; generation shapes come from EIA data.
- Pull and merge if the daily job lands, never force push, commit after every step.

## The work
1. Shapes (tier derived): hourly solar and wind output per MW of installed capacity
   for each ISO, from EIA-930 generation by fuel over the fuel's installed capacity in
   that footprint (EIA-860M), over the longest window held; document the method and
   its limits (curtailment, fleet average, not a site). Battery: the perfect-foresight
   DP of lib/battery.ts at asset scale with a daily cycle limit (an upper bound,
   labeled). Gas peaker: runs when the hub price exceeds Henry Hub times a heat-rate
   input plus a variable-cost input.
2. Table merchant_revenue_monthly (tier derived, public): per ISO hub, asset type and
   month: revenue per MW, energy per MW, capture price, capture rate against the flat
   price. ERCOT from 2018, the others over the year held.
3. /cost-of-power gets a second tab, "What a generator earns": pick ISO, asset, size
   (MW; MWh for batteries) and an annual debt service; show monthly revenue over the
   window, the median and 10th-percentile month, the worst three months, revenue on
   the stress days from event_window_daily (Uri, Elliott, the 2023 heat) against a
   normal week, and debt service coverage (monthly and trailing twelve months) with
   months under 1.0x and 1.25x flagged. Merchant only, labeled: no PPA, hedges,
   capacity payments or ancillary services, with a note on why real assets are rarely
   fully merchant. The buyer's tab is unchanged.
4. docs/methods/cost_of_power.md: a section for the seller's side; a short "how a
   lender should read this" on the page.
5. docs/reviews/nabihan-questions.md: ten questions for a private credit investor,
   each tied to a part of the tab, so his answers decide v3.

## Verify and ship
Hand-computed checks: one ERCOT solar month, one battery day against the DP, one
peaker month; check-values covers every number on the tab; check-routes; tests/;
deploy; live check.

## Report: archive/sessions/SESSION_51_REPORT.md
Shapes and their windows per ISO, the table's rows, the default tab's numbers (ERCOT
solar 100 MW, battery 100 MW / 400 MWh, peaker 100 MW) with their checks, the questions
file, decisions made without a human, open questions, wall time, spend USD 0
confirmed. Push.