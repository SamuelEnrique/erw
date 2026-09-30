# SESSION 37: Cost-of-power model v0 (tool 16), market-based

## Read first
CLAUDE.md, PRIORITIES.md, docs/datastandard.md, archive/sessions/SESSION_36C_REPORT.md,
the price board tables (price_board_*), iso_dam_hub_prices, iso_rtm_hub_prices,
ercot_all_hub_prices_history, eia930_all_demand, the saved per-BA extracts under
warehouse/raw/eia930_emissions/20260930T000657Z/, carbon_intensity_* tables, Henry Hub
series, datacenter facilities, /board and /grid/<iso> as the page pattern.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- No pulls. The gate is closed; everything comes from tables held and saved files.
- No redundant work; one table in memory at a time; stream large tables with pyarrow.
- Supabase is at 337 MB: load only this session's derived tables; if the live set would
  pass 350 MB, skip the largest new table's load, keep it in Redivis, and say so.
- The daily job may land: pull and merge before pushing, never force push.
- No invented numbers. Every figure is a warehouse value or a user input the page labels
  as an assumption with its default stated. v0 is market-based: what power costs to buy
  at wholesale, not what it costs to build (LCOE needs cost inputs we do not hold yet;
  say so on the page).

## Part A: tables (tier derived, public)
A1. `cost_of_power_monthly`: per ISO hub and month, the load-weighted average real-time
    and day-ahead price (hourly price x hourly BA demand / total demand), the simple
    average, and the difference (the "shape premium" a flat load pays or saves).
    ERCOT from 2018-07 (history prices, extract demand); the other ISOs over the
    months both series are held. PJM excluded (internal license).
A2. `cost_of_power_hourly_profile`: per ISO, the average real-time price by hour of day
    and by month of the last 12 months held, for the "when is power cheap" view.
A3. `cost_of_power_carbon`: per ISO and month, load-weighted price next to carbon
    intensity, so the page can plot cost against cleanliness.
Method in docs/methods/cost_of_power.md: formulas, which months each ISO has, what is
excluded (transmission, distribution, capacity charges, taxes) and why wholesale
understates what an end user pays.

## Part B: the calculator
Page /cost-of-power (nav under Markets):
1. A ranked bar per ISO: last complete month's load-weighted real-time price.
2. ERCOT since 2018: monthly load-weighted price, the ERCOT history strip.
3. The hour-of-day heat grid per ISO (A2).
4. Cost against carbon, one point per ISO for the latest month (A3).
5. The compute calculator: inputs a facility size (MW, default 100), a load factor
   (default 0.9), and a period (month, year, or a training run of N days, default 90);
   output the wholesale energy cost per ISO from the last 12 months of A1, flat load,
   and the same with a "run only the cheapest 80 percent of hours" option from A2.
   Defaults labeled as assumptions, results labeled as wholesale energy only.
Tier chips, citations, method link, Stanford palette, mobile-safe. The datacenter
tracker and each /grid/<iso> page link to it.

## Part C: verify and ship
Validator, coverage, archive, Supabase (Part A only, within the 350 MB rule), Redivis
draft upload (public), llms.txt and the chat catalogue (a question row: "what does a
100 MW datacenter pay for energy in ERCOT"), check-routes and check-values (every
number on the page, the calculator's defaults computed server-side and checked),
tests/, deploy, live checks.

## Do not
No pulls, no model calls, no LCOE, no PJM prices, no deletions from Redivis, no force
push.

## Report: archive/sessions/SESSION_37_REPORT.md
Rows per table and months per ISO; the page's headline figures with their rows; the
calculator's default outputs per ISO; Supabase before and after; decisions made without
a human; open questions; skipped; wall time; spend USD 0 confirmed. Commit after every
working step. Push at the end.

## Chain
When the report is written and pushed, read SESSION_38_PROMPT.md and execute it. If it
is absent, stop.