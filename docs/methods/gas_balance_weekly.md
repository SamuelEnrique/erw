# The gas balance, weekly and monthly

Energy Research Warehouse (ERW), method note written in session 2956 (chain 157, 6 November 2026) for the table first
written that day.

Table: `gas_balance_weekly` (series, public). Builder: `warehouse/derived/gas_balance_weekly.py`.

## Sources

EIA's tables the warehouse holds: `eia_gas_storage_weekly` (working gas in underground storage by region, the Weekly
Natural Gas Storage Report, 2010 to 16 October 2026); and, monthly, `eia_gas_production_state_monthly` (U.S. dry
production, N9070US), `eia_gas_consumption_state_monthly` (U.S. total consumption and electric power consumption) and
`eia_gas_trade_monthly` (pipeline imports from Canada and Mexico, LNG imports; pipeline exports to Canada and Mexico,
LNG exports), to July 2026. No request is made.

## What a row is

- **Weekly, by EIA's region** (`gas_storage:<region>`: east, midwest, south_central, mountain, pacific, salt, nonsalt,
  lower48), at the report's week, in Bcf: `working_gas_bcf`; `net_change_bcf` (against the week exactly 7 days before);
  `five_year_min_bcf`, `_max_`, `_avg_` (the same ISO week in each of the five years before, written only when all five
  are held); `vs_five_year_avg_bcf`; `five_year_position_pct` (0 at the five-year low, 100 at the high).
- **Monthly, the U.S.** (`gas_balance:US`), in MMcf: `dry_production`, `imports`, `consumption`, `power_burn` (electric
  power consumption), `exports`, `lng_exports`, and `implied_balance` (dry production plus imports less consumption less
  exports: what went to storage, the losses and EIA's balancing item, written only when all four parts are held);
  `lng_share_pct` (LNG exports over dry production) and `power_share_pct` (power burn over consumption).

## What is not held

Weekly production, consumption and LNG feedgas are not in the warehouse, so a week has no implied balance of its own:
the weekly part is storage only, and the monthly part the balance.

## Checks

- **The five regions sum to the Lower 48** within 2 Bcf on all 877 weeks (EIA rounds each region).
- **The newest week** (16 October 2026): Lower 48 working gas 3,644 Bcf, 77 Bcf above the week before, 1.0 Bcf below the
  five-year average of 3,645 Bcf, at 61.9 percent of the five-year range (3,394 to 3,798 Bcf).
- **July 2026:** dry production 3,524,896 MMcf, consumption 2,775,752, LNG exports 518,777 (14.7 percent of dry
  production), power burn 55.2 percent of consumption.

## License

Public: EIA's data are works of the U.S. government.
