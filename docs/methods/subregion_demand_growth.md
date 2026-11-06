# A zone's own demand growth (`subregion_demand_growth`)

Energy Research Warehouse (ERW). Started by session 2877 (chain 147, 5 November 2026). The table gives, for every
EIA-930 sub-region, each year's peak hour, average demand and energy, and the growth of the peak and the average from
the year before. The All grids tab has shown a grid's demand growth for every row (`eia930_demand_growth`). For a row
whose zone is an EIA-930 sub-region (an ERCOT weather zone, a MISO local resource zone, a PJM transmission zone, a
NYISO zone, an ISO-NE load zone, CAISO's three utility areas, SPP's members), this table is the zone's own growth.

Tables: `subregion_demand_growth` (named here by session 2960).

## Inputs

`eia930_subba_demand_hourly_<year>` (2019 to 2025, the data machine's sessions 609 to 612) and the rolling
`eia930_subba_demand_hourly` (the last 90 days). EIA's Hourly Electric Grid Monitor, demand by sub-region, public
domain. No request is made.

## Rules

- **An hour is used as the grid-level table uses one** (`warehouse/derived/demand_growth.py`, through
  `impossible_hours.screen`): held, above zero, within 25 percent of the median of the two hours on each side, and
  within a third to three times the sub-region's median hour. Before the test, each year's hours are placed on the
  year's full hourly grid, so a missing hour is a gap and not a neighbour. An hour not used is used for nothing, and
  nothing is filled.
- **A year's figures are written only when at least 95 percent of its hours are used.** A year below that gets its
  `hours_used` and `hours_in_year` rows and no figure.
- **Growth is written only when both years have figures.** `avg_growth_pct` compares the mean of the hours used, so a
  missing hour does not read as lower demand. `peak_growth_pct` compares the two peaks.
- **Years are UTC calendar years.** EIA dates the hours in UTC, and a sub-region's time zone is not in the table.
  A year's first and last few hours therefore fall on the neighbouring local days.
- **Weather is not removed.** As in the grid table, a year's demand is what was metered.
- **A year held by a yearly table is never taken from the rolling one.** The rolling table covers 2026 only from late
  July, so 2026 gets no figures: the year to date is not written.

## Rows

`entity` is the source table's (`eia930_subba:<parent>:<subba>`), with `x_parent` and `x_subba`. `ts_utc` is the
year's first hour, `freq` `P1Y`. The variables are `peak_mw` (with `x_at`, the peak hour's start in UTC), `avg_mw`,
`energy_mwh`, `hours_used`, `hours_in_year`, `avg_growth_pct` and `peak_growth_pct`.

## Limits

- A sub-region's boundary is EIA's and can change. EIA lists some sub-regions only from a later year, so their first
  year has no growth.
- The tab can use a sub-region's growth only for a row whose zone the source names as a sub-region. A hub that spans
  zones keeps its grid's growth.
