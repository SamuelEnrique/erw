# Consumption: who buys the power, by state and sector

The third view of `/demand` ("Consumption", `/demand?view=consumption`; `/consumption` redirects there). Written by
session 331 (20 October 2026) from the view's own code (`site/app/consumption/view.tsx`) and its connector; until then
the view's citations were its only note.

## The two tables

| Table | Source (EIA API v2 route) | What the view reads |
|---|---|---|
| `eia_retail_sales_monthly` | `electricity/retail-sales`, monthly | the electricity sold to each sector in each state, in MWh (EIA publishes million kWh: times 1,000), variable `retail_sales` |
| `eia_sector_energy_consumption_monthly` | `total-energy`, the Monthly Energy Review's tables 2.3 and 2.4, monthly | the energy the industrial and commercial sectors consume, in trillion British thermal units, as EIA publishes it |

Both are written by `warehouse/connectors/eia_series.py` (session 18). EIA's data are public domain.

## The rules

- **Twelve months against twelve.** The newest month the retail sales table holds ends the latest twelve months; the
  twelve before them are the comparison. A state's or a sector's total is written only when every one of its twelve
  months is held; otherwise there is no total, never a partial one.
- **The fastest growing states** are ranked among the states that sold at least 1,000,000 MWh (1 TWh) to the sector in
  the earlier twelve months, so that a small base does not lead.
- **The sectors' energy** (the Monthly Energy Review) lags the retail sales by a few months: its twelve months are its
  own newest, said beside it.
- Every figure the view shows is a checked number: `check-values` reads it again from the same rows.

## What a sector's change is and is not (session 10214)

- **A sector is a billing class.** EIA's residential, commercial, industrial and transportation sales are the classes the
  sellers bill their customers under; customers move between classes, and a state's sellers do not all class a large
  customer alike. "Where industrial and commercial load is growing fastest" ranks a class's sales. On the main copy's
  table (built 5 November 2026), September 2025 to August 2026 against the twelve months before: Texas's commercial
  sales +13,653,363 MWh (+8.0 percent, sixth of the commercial list) while its industrial sales fell 7,672,895 MWh and
  all sectors rose 9,358,908 MWh; Texas's industrial sales ran above the same month a year before in every month of
  2024 and 2025 but October 2025 (22 GWh below), and below it in every month from January 2026. Whether customers moved between the classes, or EIA's sample or estimates changed
  with the year, cannot be told from these rows. The view's note says to read a sector beside the state's other sectors
  and all-sector change.
- **The months are estimates.** Form EIA-861M is a monthly sample of sellers; EIA estimates the rest and revises the
  months when the annual Form EIA-861 is in. The size of those revisions is not measured here (it needs the archive's
  earlier vintages of the table: a data request of the audit).
- **"Total energy consumed" holds losses.** The Monthly Energy Review's sector totals hold the sector's share of the
  electrical system's losses: over the twelve months to July 2026 the industrial losses (`LOICBUS`) are 15.8 percent of
  the industrial total (`TEICBUS`), and the commercial total less its end use is 42.4 percent of `TECCBUS`. The view's
  note says so.

## Downloads

Under the view, the two tables as the live set's CSV with a Python and a Stata reader of that CSV (session 328's shared
line).

## The figures on the page and their keys

Each number `/demand?view=consumption` shows carries its key (`site/components/Num.tsx`), which `site/scripts/check-values.mjs` checks against the live set and `site/scripts/check-methods.mjs` against this note (session 409). The keys the sections above do not name:

- `eia_sector_energy_consumption_monthly`, `energy_consumption`: the sectors' energy in trillion British thermal units, for each of the five Monthly Energy Review series the view lists (`TEICBUS`, `ESICBUS`, `NNICBUS`, `TECCBUS`, `ESCCBUS`, entity `eia:<series>`), summed over the table's latest twelve months and written only when all twelve are held. Its key is a `series_esum` key: the table, the series, the variable and the window. The change beside it, against the twelve months before, is not a checked number.
