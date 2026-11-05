# What is on an electricity bill

The learning page `/learn/bill`. Written by session 335 (20 October 2026) from the page's code (`site/app/learn/bill/`,
`site/lib/bill.ts`) and its rules file; until then the page's citations were its only note.

## The five bills

Five homes on five published tariffs: a PG&E home on time-of-use rate E-TOU-C, an SCE home on TOU-D-4-9PM and an
SDG&E home on TOU-DR1 in California; a home in Oncor's area and one in CenterPoint's area (Houston) of ERCOT. Every
rate, credit and fixed charge is in the site's own file, `site/data/bill_rules.json`, each with the tariff passage it
is read from (the schedule and its sheet), and each line of a bill opens to say what the charge is, why it exists and
that passage. A bill's defaults (its monthly use, its territory, its season) are in the same file, each with its own
words (every default home uses 600 kWh a month, an assumption the file says is one).

## The numbers

- **A default bill** is computed on the server from the file (`defaultBill` in `site/lib/bill.ts`), and every figure of
  it is a checked number: `check-values` computes it again from the same file (`bill|...` keys).
- **The wholesale share**: the load-weighted real-time price of the latest complete month in `cost_of_power_monthly`
  (the ERW's cost of power, `cost_of_power.md`), else the latest month held, said to be partial; the share is what that
  price, times the bill's kilowatt-hours, makes of the bill's total.
- **Build a bill**: the same rules in the reader's browser, with the reader's use and choices; "Reset this bill to its
  defaults" puts every input back to the file's.
- The words of the glossary and of each line are written for this site with their sources named, marked "written,
  cited" (not data).

## Downloads

At the foot of the page, `cost_of_power_monthly` as the live set's CSV with a Python and a Stata reader of that CSV
(session 328's shared line). The rates are the site's own file, not a table of the warehouse.

## The figures on the page and their keys

Each number `/learn/bill` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `cost_of_power_monthly`, `rt_load_weighted`: the wholesale price each default bill is set against, USD/MWh, the load-weighted real-time price of the bill's zone (`wholesale_entity` in `site/data/bill_rules.json`) in the latest complete month (one whose `rt_hours` equal its `hours_in_month`), else the latest month held, marked "a partial month". It stands beside the bill's wholesale energy in USD and its share of the bill.
