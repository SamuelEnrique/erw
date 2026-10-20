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

## Downloads

Under the view, the two tables as the live set's CSV with a Python and a Stata reader of that CSV (session 328's shared
line).
