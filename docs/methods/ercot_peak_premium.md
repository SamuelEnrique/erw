# ERCOT peak premium: method

The metrics behind the ERCOT peak-premium chart (the human's thesis), as the Energy Research Warehouse (ERW) computes them. They are computed by `warehouse/derived/ercot_peak_premium.py` into two derived `series` tables:
- `ercot_peak_premium_annual`: one value per metric, hub and ERCOT operating year, freq `P1Y`;
- `ercot_peak_premium_monthly`: the same metrics per calendar month, freq `P1M`.

Tables: `ercot_peak_premium_monthly`, `ercot_peak_premium_annual`

## Input

- **Prices:** ERCOT real-time settlement point prices, 15-minute intervals, USD/MWh (variable `spp_rtm`). They come from ERCOT's NP6-785-ER yearly archives and NP6-905-CD live files, as stored in the ERW tables:
  - `ercot_rtm_hub_prices_<year>`: 2015 to the current year, the history;
  - `ercot_rtm_hub_prices`: the live window.
  These tables do not overlap; the script checks that no (hub, interval) appears twice.
- **Hubs:** every hub in those tables: HB_HUBAVG, HB_BUSAVG, HB_NORTH, HB_SOUTH, HB_WEST, HB_HOUSTON. The thesis uses HB_HUBAVG.
- **Periods:**
  - year: the ERCOT operating year in America/Chicago, from Jan 1 00:00 local to the next Jan 1 00:00 local;
  - month: the calendar month in America/Chicago.
  An interval belongs to the year or month in which it starts, in local time.

## Time-of-day blocks

Let `h` be the local (America/Chicago) clock hour in which a 15-minute interval starts: 0 to 23. The interval starting at 16:45 has h = 16.

| Block | Hours | Rule on h | Intervals per day |
|---|---|---|---|
| overnight | 21:00 to 12:00 the next day | h >= 21 or h < 12 | 60 (15 hours) |
| midday | 12:00 to 16:00 | 12 <= h < 16 | 16 (4 hours) |
| peak | 16:00 to 21:00 | 16 <= h < 21 | 20 (5 hours) |

The blocks do not overlap and together cover every interval.

**DST.** Interval starts are stored in UTC and converted to local time to find `h`.
- On the spring-forward day, local 02:00 to 02:59 does not exist, so that day's overnight block has 56 intervals.
- On the fall-back day, local 01:00 to 01:59 occurs twice (two distinct UTC hours), so that day's overnight block has 64 intervals.
- Midday and peak are never affected. A full year therefore has 21,900 overnight, 5,840 midday and 7,300 peak intervals (21,960, 5,856 and 7,320 in a leap year).

## Notation

For a set of prices `X` (one hub, one period, one block or all intervals):
- `P_p(X)` is the p-th percentile of `X` computed with numpy's default method (`numpy.percentile(X, p)`, method "linear"). For sorted values x_0 <= ... <= x_(n-1), `P_p` is interpolated linearly at position `(n - 1) * p / 100`.
- min and max are the smallest and largest values.
- Q1 = `P_25`, median = `P_50`, Q3 = `P_75`.

No cap, floor, winsorizing or exclusion is applied. Every interval the source publishes is used, including negative prices and prices at the offer cap.

## Metrics

For each hub and each period (year or month), with `A` = all intervals, `O` = overnight, `M` = midday and `K` = peak:

| Variable | Formula | Unit |
|---|---|---|
| `overnight_min`, `overnight_q1`, `overnight_median`, `overnight_q3`, `overnight_max` | min, P_25, P_50, P_75, max of O | USD/MWh |
| `midday_min`, `midday_q1`, `midday_median`, `midday_q3`, `midday_max` | the same over M | USD/MWh |
| `peak_min`, `peak_q1`, `peak_median`, `peak_q3`, `peak_max` | the same over K | USD/MWh |
| `all_min`, `all_q1`, `all_median`, `all_q3`, `all_max` | the same over A | USD/MWh |
| `all_p999` | P_99.9(A) | USD/MWh |
| `peak_iqr` | P_75(K) - P_25(K), the peak-block IQR | USD/MWh |
| `all_iqr` | P_75(A) - P_25(A), the all-intervals IQR | USD/MWh |
| `worst_interval_multiple` | P_99.9(A) / P_50(A), the worst-interval multiple | ratio |
| `peak_minus_midday_median` | P_50(K) - P_50(M), the peak-minus-midday median spread | USD/MWh |
| `n_scarcity` | number of intervals in A with price >= 1,000 USD/MWh | count |
| `n_negative` | number of intervals in A with price <= 0 USD/MWh (zero counts) | count |
| `n_intervals` | number of intervals in A | count |

Values are rounded to 6 decimals when written. The thesis quotes two decimals.

## Completeness

- A past year (or month) must have every interval: 35,040 quarter hours in a year (35,136 in a leap year), or the number of quarter hours in the month. Otherwise the script fails and writes nothing.
- The current year and month are partial and are written as such. Their `n_intervals` says how many intervals they cover, and the table header names the last interval used.
- The worst-interval multiple is undefined when the median is 0. The script then fails loudly rather than writing an infinite value.

## Timestamps in the tables

`ts_utc` labels the period, as the series standard requires for daily and longer frequencies:
- annual: `YYYY-01-01T00:00:00Z` for ERCOT operating year YYYY;
- monthly: `YYYY-MM-01T00:00:00Z`.

The periods themselves are the local (America/Chicago) year and month defined above, which start at 05:00 or 06:00 UTC.

## License

A derived table inherits the most restrictive license of its inputs (docs/datastandard.md, Decision 23). The ERCOT inputs are public, so these tables are public.

## Thesis reproduction (HB_HUBAVG)

| Metric | 2015 | 2025 |
|---|---|---|
| all_median | 20.49 | 25.68 |
| all_p999 | 583.96 | 311.80 |
| peak_iqr | 7.64 | 34.12 |
| midday_min | -3.98 | -18.25 |

These are the human's values. The package tests check that the annual table reproduces them to the cent.

## On the site (session 328, 20 October 2026)

The two tables are drawn on the ERCOT tab of `/prices` (the peak premium explorer; `/explorer/ercot-peak-premium`
redirects there). Since session 317 its box plot is drawn in SVG through the site's shared chart set: five numbers a
box on one scale, the median named with its value; no value moved. Since session 328 the tab offers both tables as the
live set's CSV with a Python and a Stata reader of that CSV. The catalogue,
read on 20 October 2026, gives both tables' last run as 29 September 2026; the monthly table's newest month is
September 2026.

## The explorer (session 403, 21 October 2026)

`/explore/ercot-peak-premium` (platform tool 5, the first signature explorer; in review, not in the menu) is the
thesis chart made live. Its one-line definition: the peak premium is how much higher and how much wider ERCOT's
real-time price runs from 16:00 to 21:00 than at midday, read as `peak_minus_midday_median` and `peak_iqr` above.

- **Filters**, in the address so that each view can be linked and checked: `hub` (the six hubs, default HB_HUBAVG),
  `month` (blank for the whole year, from `ercot_peak_premium_annual`; 1 to 12 for that calendar month in each year,
  from `ercot_peak_premium_monthly`), `from` and `to` (two years; default the first year held and the newest complete
  one, so the default view is the thesis's 2015 against 2025). A value the tables do not hold is replaced by the
  default, and the page says so in one line.
- **What it draws**, through the site's shared charts only (`components/BoxChart.tsx` over `svgchart.tsx`'s
  `BoxPlot`, and `LineChart`): the five numbers of each block, the two years side by side (the thesis chart); the
  table of those numbers; the thesis's figures (`all_median`, `all_p999`, `worst_interval_multiple`, `peak_iqr`,
  `peak_minus_midday_median`, `midday_min`, `n_scarcity`, `n_negative`, `n_intervals`) for both years; the peak-block
  IQR, the peak-minus-midday median and the median along the years (or along one month's years); the monthly medians
  of the three blocks. Every figure is one row of one table, with its check key
  (`series|<table>|<hub>|<variable>|<period>`); the page computes none.
- **Partial periods.** A year is partial when `n_intervals` is short of 35,040 (35,136 in a leap year); a month when
  it is short of its days times 96 less four (the four quarter hours the spring clock change removes). Only the newest
  year and month can be partial, as the completeness rule above says; the page marks them.
- **How old the tables are** is read, never written by hand: the catalogue's `last_run` and `ts_max` of each table,
  and the header's "Last input interval". A table not computed for more than three days is called stale on the page,
  with the date. On 21 October 2026 both tables' last run is 29 September 2026, the newest month September 2026 and
  the newest interval 28 September 2026 04:45 UTC.
- **The ERCOT tab of `/prices`** (where `/explorer/ercot-peak-premium` redirects) draws the same tables one hub and one
  year at a time; it is unchanged. The explorer sets two years side by side and reads one month across the years.
