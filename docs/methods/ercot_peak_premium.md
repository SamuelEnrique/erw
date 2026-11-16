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

## Decisions of the explorer (each dated, and reversible unless said)

The choices made on `/explore/ercot-peak-premium` and on the ERCOT tab of `/prices`, one line each with its session; sessions 403's are gathered here from "The explorer" above.

1. 2026-10-21, session 403: the filters are the address (`hub`, `month`, `from`, `to`), so every figure is drawn on the server from one row and carries that row's check key; a value the tables do not hold falls back to the default and the page says so in one line.
2. 2026-10-21, 403: the default view is the thesis's, HB_HUBAVG for the whole year, the first year held against the newest complete one.
3. 2026-10-21, 403: a year is partial when `n_intervals` is short of 35,040 (35,136 in a leap year), a month when it is short of its days times 96 less four; the page marks them and computes nothing else.
4. 2026-10-21, 403: how old the tables are is read from the catalogue and the header, never written by hand; stale after three days.
5. 2026-10-23, session 2200: every figure carries its source in its hover, as the span's title (`site/components/Num.tsx`, `source`): the table, the hub, the variable, the period, the two ERCOT reports and this note's name, read from the figure's own key by `site/lib/explore/source.ts`; nothing typed per figure. The three headline numbers carry the same words in the brand's keyboard-reachable tip; the fifty-odd figures in the tables do not (a tip's button beside each would double the page's tab stops).
6. 2026-10-23, 2200: the thesis chart's and the line charts' hover cards (fog, a rule-colored edge, the period, every figure in mono) are the shared components' as they stood; `site/scripts/check-explorers.mjs` reads them in a browser with the tips and the page's width at 390 px.
7. 2026-10-23, session 2203: the tip mark's target is 24 px in both directions (WCAG 2.2's 2.5.8), its drawn size 16 px as before.
8. 2026-10-23, session 2204: the ERCOT tab's ten headline tiles take the headline number's size of the brand's scale (24 px in the serif); they stood at 18 px, which the scale does not hold. Nothing else of the two pages' type, color, tables or charts was outside `docs/brand.md` on reading: `site/app/tokens.css` sets the titles in ink, the labels in sentence case, the notes at 68 characters, the tables' figures in mono and the axis text at 12 px for every page in the brand.

## The tool as a reader meets it (session 7507, chain 304, 16 November 2026)

This section completes the note for `/explore/ercot-peak-premium` as a reader meets it: every view, every figure's table and rule, every choice with its default and source, what the tool does not hold, and what published figures stand beside it. Nothing above is rewritten; where a line above is amended, this section says so. The replication (`replication/ercot_peak_premium/`) was written from this note.

### 1. What the page shows, top to bottom

1. **The freshness line.** For each of the two tables: the day it was last computed and the newest period it holds, from the site's catalogue (`last_run` and `ts_max` of `warehouse/metadata/coverage.csv`, loaded with the live set), and "Stale since" that day when it is more than three days old. Under it, the newest 15-minute interval the tables were computed from, read from the tables' header ("Last input interval").
2. **The filters:** hub, period (the whole year or one calendar month), first year, second year. They are the address (`hub`, `month`, `from`, `to`).
3. **Three headline numbers** for the second year, each with the first year's value under it: the peak-block IQR (`peak_iqr`), the peak median minus the midday median (`peak_minus_midday_median`), the median of all intervals (`all_median`).
4. **The thesis chart:** one box a block and a year (overnight, midday, peak, all intervals), from Q1 to Q3 with the median marked and whiskers to the minimum and the maximum.
5. **The five numbers of each block:** minimum, Q1, median, Q3 and maximum of the four blocks for each of the two years: 40 figures.
6. **The thesis's figures** for each of the two years: `all_median`, `all_p999`, `worst_interval_multiple`, `peak_iqr`, `peak_minus_midday_median`, `midday_min`, `n_scarcity`, `n_negative`, `n_intervals`: 18 figures.
7. **Two line charts:** `peak_iqr`, `peak_minus_midday_median` and `all_median` along the years (or along one month's years), and the monthly medians of the three blocks for every month held. Their points are rows that the tables of items 5 and 6 also show in one view or another.
8. The link to the ERCOT tab of `/prices`, the decisions block (section 5), the method link, the download of the rows drawn and of the two tables, the source line.

A view of two years draws 64 figures (6 headline, 40 block, 18 thesis); a view of one year alone draws 32.

### 2. Every figure's table and rule

- **The table.** With the period "Whole year" a figure is a row of `ercot_peak_premium_annual` labelled `YYYY-01-01T00:00:00Z`; with a month it is a row of `ercot_peak_premium_monthly` labelled `YYYY-MM-01T00:00:00Z`. Its check key is `series|<table>|<hub>|<variable>|<label>`. The page computes nothing.
- **The hubs offered** are the entities that have an `n_intervals` row in the annual table, in alphabetical order: HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST. **The years offered** are the years in which the chosen hub has an annual `n_intervals` row.
- **Held and partial.** A year is held for the chosen period when the table has an `n_intervals` row for that hub and label. A held year is partial when its `n_intervals` is not 35,040 (35,136 in a leap year). A held month is partial when its `n_intervals` is below the quarter hours of the full month: its days times 96, four fewer in March and four more in November (the months of the clock changes in America/Chicago since 2007). This amends "The explorer" and decision 3 above, which said "short of its days times 96 less four" for every month: by that rule a month up to an hour short (two hours in November) was drawn as complete (fault 3 of `docs/reviews/ercot-peak-premium-faults-2026-11-16.md`). The filters mark a year "(partial)" or "(not held)".
- **The view a reader opens on.** With no hub named: HB_HUBAVG. With no period named: the whole year. With no first year named: the first year held. With no second year named: the newest year held that is not partial; if none is complete, the newest held. So the page opens on 2015 against 2025, and September opens on 2015 against 2025 while September 2026 is partial. A value of the address that the tables do not hold is replaced by the default, and the page says so in one line.
- **A figure not held** (December of a year whose December has not come) is drawn as the words "not held", with no unit beside it.
- **The text.** A count (`n_scarcity`, `n_negative`, `n_intervals`) is written whole; a price and a ratio with two decimals; thousands with commas. The tables hold six decimals, and a value exactly halfway at the third decimal is rounded away from zero: 37.035 is written 37.04. Such ties are common here (3,655 of the 25,704 rows end in a 5 at the third decimal), because ERCOT prices are in cents and a median or a quartile of an even count is often the midpoint of two prices a cent apart. A price that is a whole number of dollars is written with its two decimals (25.00).
- **The download of the rows drawn** is the hub's rows of the table from 1 January of the earlier year to 1 January after the later year; for a month it holds every month of those years.
- **Definitions that hold inside the table,** which the replication uses to recompute a figure from other rows: `peak_iqr` = `peak_q3` - `peak_q1`; `peak_minus_midday_median` = `peak_median` - `midday_median`; `worst_interval_multiple` = `all_p999` / `all_median`; `all_min` and `all_max` are the lowest block minimum and the highest block maximum; `n_intervals` of a complete period is the full count above.

### 3. Where the input is now, and rules stated in full

- **The input tables were consolidated in session 29.** "Input" above names `ercot_rtm_hub_prices_<year>` and `ercot_rtm_hub_prices`. Since then the yearly history is the rows of `ercot_all_hub_prices_history` whose `market` is `ercot_rtm` (each former table is a `year`), and the live window is the rows of `iso_rtm_hub_prices` whose `market` is `ercot_rtm`. The variable is `spp_rtm`, the frequency `PT15M`, `ts_utc` the interval's start.
- **The cut.** The tables are computed up to the newest interval the inputs held when the builder ran; the header's "Last input interval" names it. A recomputation uses no later interval.
- **The six hubs** are the four regional hubs (North, South, West, Houston), HB_HUBAVG (ERCOT's average of the four) and HB_BUSAVG (ERCOT's average over the hubs' buses); "Hubs" above lists them.
- **A full local year** has 35,040 quarter hours (35,136 in a leap year): the day the clocks go forward has 92 and the day they go back 100, so the year's count is unchanged.
- **`all_iqr`** is in both tables and is not drawn on the page.
- **Checked on 16 November 2026:** `replication/ercot_peak_premium/from_hourly.py`, written from this note alone, recomputed every row of both tables from the 15-minute prices on samueloldlaptop (2,469,864 hub-intervals up to 2026-09-28T04:45:00Z): 25,704 of 25,704 rows equal at six decimals (2,016 annual, 23,688 monthly). The copy there was built on 29 September 2026; the warehouse's copy is newer (section 7).

### 4. What the tool does not hold

- No mean: every central figure is a median. No load-weighted price.
- No day-ahead price, no forward or traded on-peak price, no ancillary service price, no load zone and no resource node (those are on `/prices` and on the battery pages).
- No hour-by-hour profile: three blocks only, the same hours on every day of the week. The industry's on-peak block (06:00 to 22:00 on weekdays) is not computed.
- No year before 2015. No adjustment for inflation or for the price of gas.
- No cause: the page shows that the evening runs higher and wider than midday, not why.

### 5. The decisions on the page

The page carries them in a fold, "Decisions on this page", each with its default and its source on hover (`site/app/explore/ercot-peak-premium/Decisions.tsx`; `tests/test_session7507_peak_premium.py` holds that list to this one). The page computes nothing, so none is editable in place: the hub, the period and the two years are the filters.

| Key | The choice | Default | Source |
|---|---|---|---|
| `blocks` | Three blocks by the local hour an interval starts | Overnight 21:00 to 12:00, midday 12:00 to 16:00, peak 16:00 to 21:00, every day of the year | The thesis; "Time-of-day blocks" above |
| `premium` | The premium is the peak median less the midday median, and the peak block's IQR | Medians and quartiles, never a mean | "Metrics" above |
| `percentile` | Linear interpolation at position (n - 1) * p / 100 | numpy's default | "Notation" above |
| `no-cap` | Every interval is used | No cap, floor or exclusion; February 2021 is in 2021 | "Notation" and "Completeness" above |
| `price` | ERCOT's real-time settlement point price, every 15 minutes, each interval counted once | Real time, time-weighted; not day-ahead, not load-weighted | NP6-785-ER, NP6-905-CD |
| `hub` | The hub the page opens on | HB_HUBAVG; six hubs offered | Session 403 |
| `local-time` | Years and months are local (America/Chicago), daylight saving included | Central time | "Input" above |
| `years` | The two years a view opens on, and what is partial | The first year held against the newest complete one | Session 403; the month's exact count since session 7507 |
| `thresholds` | Scarcity at or above 1,000 USD/MWh; negative at or below 0; the multiple is P99.9 over the median | 1,000 and 0 | "Metrics" above; the thesis's thresholds |
| `rounding` | Two decimals, a count whole, a tie away from zero | Six decimals in the tables | Session 7507 |
| `freshness` | Stale after three days | Three days | Session 403 |

### 6. Beside published figures (read on 16 November 2026)

Robots files and terms read first. `potomaceconomics.com`: its robots file disallows only `/wp-admin/`; its ERCOT page carries a copyright line and no terms; the two reports were read from its own `/wp-content/uploads/`. `eia.gov`: its robots file allows `/todayinenergy/` and `/electricity/` (it disallows `/archive/`, `/reports/` and others not asked). `ercot.com` was not asked for a document: its robots file disallows the paths its documents are served from. No figure of ours was adjusted.

"Ours, plain mean" is not a figure of the page or of a table: it is the mean of all 15-minute prices of the year at HB_HUBAVG, printed by `from_hourly.py --means` from the same prices, so that a published average has something of the same kind beside it. The page's own figure for the year is its median.

| What | Ours | Theirs | Publisher, document, date | Difference | Why |
|---|---|---|---|---|---|
| Real-time energy price, 2024, USD/MWh | plain mean 26.83 (the page's median: 19.60) | 31.91, ERCOT-wide, load-weighted | Potomac Economics (ERCOT's Independent Market Monitor), *2024 State of the Market Report for the ERCOT Electricity Markets*, May 2025, Table 1, page 5 | ours 5.08 lower (16 percent) | Theirs weights each interval by load, and load is highest when the price is; theirs is the load zones, ours the average of the four hubs, each interval counted once |
| The same, 2023 | 48.36 (median 21.37) | 65.13 | the same table | ours 16.77 lower (26 percent) | The same; the widest gap of the five years. 2023 has 236 intervals at or above 1,000 USD/MWh, more than any year held but 2021 |
| The same, 2022 | 62.30 (median 44.02) | 74.92 | the same table | ours 12.62 lower (17 percent) | The same |
| The same, 2021 | 148.19 (median 24.60) | 167.88 | the same table | ours 19.69 lower (12 percent) | The same; February 2021 is in both |
| The same, 2020 | 21.18 (median 16.56) | 25.73 | the same table | ours 4.55 lower (18 percent) | The same. The five years rank the same in both: 2021, 2022, 2023, 2024, 2020 |
| When the price peaks | The peak block is 16:00 to 21:00; the peak median less the midday median went from -0.16 in 2015 to 14.52 in 2025 (HB_HUBAVG) | "the period when system conditions are tightest has shifted from the firm peak load hour, usually around 4 to 5 p.m., to the later evening hours (7 to 9 p.m.)", May to September, 2021 to 2025 | Potomac Economics, *2025 State of the Market Report for the ERCOT Electricity Markets*, May 2026, page 5 (Figure 3) | none in direction | Both hours are inside the page's peak block. The page holds no hour-by-hour price, so the hour itself has nothing of ours beside it |
| Prices at or below zero, 2025 | 959 intervals at HB_HUBAVG, which is 239.75 hours (992 intervals, 248 hours, in 2024) | "hundreds of hours with prices at or below $0 per MWh" | the same report, page 4 | none: 240 hours is "hundreds" | Theirs gives no count and names no hub |
| The highest price, 2022 to 2024 | 5,101.55, 5,075.46 and 4,981.33 USD/MWh (`all_max`, HB_HUBAVG) | the system-wide offer cap is 5,000 USD per MWh | Potomac Economics, 2024 report, page 83 | within 2.1 percent of the cap | A settlement point price can pass the cap by a little; by how much and why is not established here |

**Nothing published stands against:** the peak-block IQR, the peak median minus the midday median, any block's quartiles or median, the 99.9th percentile, the worst-interval multiple, the count of intervals at or above 1,000 USD/MWh, and every monthly figure. They are this page's own measures: the market monitor's reports give load-weighted averages and charts by hour, not medians or quartiles by block. **Not read:** Table 1 of the 2025 report (the 2025 average) is drawn in a font the text reader of samueloldlaptop does not decode, and the machine has no PDF renderer, so 2025 has no average beside it. **The EIA:** its article "U.S. wholesale day-ahead electricity prices rose in 2025 with higher natural gas prices" (Today in Energy, 2 February 2026) names no ERCOT hub price in its words (its chart's values are not in the page's text). The EIA's wholesale market page republishes ICE's daily on-peak index for ERCOT North: trades for day-ahead delivery over the 16-hour weekday block, another market and another block than the page's; it was not set beside a figure. No published forward or settled series names the page's 16:00 to 21:00 block.

### 7. The replication

```
python replication/ercot_peak_premium/replicate.py              # every figure of every view, beside the page's own
python replication/ercot_peak_premium/replicate.py --headline   # the do-file's lines
python replication/ercot_peak_premium/from_hourly.py            # every row of both tables from the 15-minute prices
```

On the tables of samueloldlaptop (built 29 September 2026), 16 November 2026: 550 of 550 views open as this note says; 24,786 of 24,786 figures inside the tolerance (half the last digit shown), with the same text; 25,704 of 25,704 rows of the two tables recomputed from the 15-minute prices. `replicate.do` rebuilds the five headline figures in Stata (not run: no Stata on that machine). The page's figures are drawn by the page's own code (`site/scripts/peak-premium-figures.mjs`); the charts' points as a browser draws them are not read (a browser read). Since session 7516 the replication also covers the views with a second hub and the marks of a partial period: 674 views, the counts in section 10.

The warehouse's copy of the two tables is newer than that machine's (last computed 21 October 2026, the monthly table to October 2026), and on 16 November 2026 it was 26 days old, so the page calls both tables stale. The cloud's daily run does not compute them (it does not hold the 15-minute history: `warehouse/metadata/run_status.csv`, "inputs absent in CI"); the data machine does.

### 8. Rulings asked (each with the default taken)

1. **The page's one-line definition** says the price runs "how much higher and how much wider" from 16:00 to 21:00 "than at midday". Higher is measured against midday (the two medians). Wider is the peak block's own IQR: no midday IQR is in the tables or on the page (it can be read from the midday Q1 and Q3 in the table). Default: the sentence stays.
2. **Grey text.** The notes under the charts and the sections, the freshness detail, the block hours in the table and "not held" are grey, drawn by the frame every tool shares. The page standard asks for hover tips. Default: not changed here.
3. **The chart's own number format.** The thesis chart's median labels, its hover card and its table view write a value with at most two decimals and none at or above 100 (19.1 for 19.10, 3,553 for 3,553.10), by the shared chart set's rule. The page's tables write two decimals. Default: not changed (the chart set is every page's).
4. **A mean beside the median,** or the industry's on-peak block, so that a published average or a traded on-peak price could be set beside the page. Default: not built.
5. **How often the tables are computed.** They are stale 26 days on the day of this note. Default: a request to the data machine, no change to a schedule.

### 9. Since the read as a reader (session 7516, chain 304, part B, 16 November 2026)

The page was read as a fund analyst sizing the evening premium would read it, on five real cases (`docs/reviews/ercot-peak-premium-read-2026-11-16.md`, 14 rows). What it changed on the page, each held by `site/scripts/test-peak-premium-read.mjs`; no figure, table or rule above moved:

- **A second hub.** A fifth filter, "Beside hub" (`vs` in the address; none by default; the same hub twice is none; a hub the tables do not hold is replaced by none and the page says so). With it the page draws one more section, "Two hubs side by side": for each of the two hubs and each of the view's periods, `peak_median`, `peak_q1`, `peak_q3`, `peak_iqr`, `midday_median`, `peak_minus_midday_median`, `overnight_median`, `all_median`, `all_p999`, `all_max`, `n_scarcity`, `n_negative` and `n_intervals` (`SIDE` in `site/lib/explore/peakpremium.ts`): 13 figures a hub and a period, each one row of the table with its check key, written by the rule of section 2. The page takes no difference between the two hubs: the difference of two medians is not the median of the price difference between the hubs from interval to interval, which the tables do not hold. A view with no second hub draws the 64 (or 32) figures of section 1 and no more, so the replication's count is unchanged.
- **The mark of a period not yet over.** A partial year or month reads "2026 (partial)" or "September 2026 (partial)" wherever it heads a figure: the headline numbers' labels and the first year under them, the "Period" cells of the first table, the heads of the second and of the two-hub table. Until then the mark was in the filters and in the sentence under the thesis chart only.
- **Words.** The decisions block's line on thresholds says that the worst-interval multiple is of the 99.9th percentile, not of the highest interval: one interval in a thousand passes that price, about 35 of a full year's 35,040 and about 3 of a month's; the highest interval is `all_max`, and its day and hour are in no table. The hub line says what HB_BUSAVG is. One sentence beside the link to the ERCOT tab says the page holds no node and names the battery page, where ERCOT's storage nodes are set against the hub average (`node_basis_summary`).

### 10. The section of two hubs and the marks, for a second implementation (session 7516)

Everything a second implementation needs to write what section 9 added, from the two tables alone. `replication/ercot_peak_premium/replicate.py` was extended from these words, not from the page's library.

**The second hub.** The address may name one more hub, `vs`. It is none when the address names none, when it names the first hub again, and when it names a hub that has no `n_intervals` row in the annual table; in that last case the page also says, in its one line, that the address asked for something the tables do not hold. The filter "Beside hub" offers "None" and the other hubs offered (five of the six), so it has as many choices as the hub filter. The hub, the period and the two years of the view are chosen as section 2 says, from the first hub alone; the second hub changes none of them, nor any of the view's 64 (or 32) figures, nor the download of the rows drawn.

**The section** is drawn only when there is a second hub, after "The thesis's figures". Its title is "Two hubs side by side: A and B", the two hubs' names without the grid's prefix (HB_WEST, HB_NORTH), the first hub first. Its line reads "The same rows for each hub, P." where P is the view's periods joined by " and " (one period when the two years are the same), each written as below. Its table is drawn when the table of the period holds a row of the second hub for that period in any year offered.

**The 13 figures,** in the order drawn, each one row of `ercot_peak_premium_annual` (the whole year, labelled `YYYY-01-01T00:00:00Z`) or of `ercot_peak_premium_monthly` (a month, labelled `YYYY-MM-01T00:00:00Z`), entity the hub, with the check key `series|<table>|<hub>|<variable>|<label>`:

| # | Variable | What it is |
|---:|---|---|
| 1 | `peak_median` | the median of the 16:00 to 21:00 block |
| 2 | `peak_q1` | its first quartile |
| 3 | `peak_q3` | its third quartile |
| 4 | `peak_iqr` | `peak_q3` less `peak_q1` |
| 5 | `midday_median` | the median of the 12:00 to 16:00 block |
| 6 | `peak_minus_midday_median` | `peak_median` less `midday_median` |
| 7 | `overnight_median` | the median of the 21:00 to 12:00 block |
| 8 | `all_median` | the median of all intervals |
| 9 | `all_p999` | the 99.9th percentile of all intervals |
| 10 | `all_max` | the highest interval: the highest of the three blocks' maximums |
| 11 | `n_scarcity` | intervals at or above 1,000 USD/MWh |
| 12 | `n_negative` | intervals at or below 0 USD/MWh |
| 13 | `n_intervals` | intervals in the period |

For each variable, in that order, the cells run by period (the first year, then the second; one period when the two years are the same), and inside a period the first hub, then the second: 52 figures for two years, 26 for one. The table's head is "Figure", then for each period "A, P" and "B, P". A figure is written by the rule of section 2 (a count whole, a price with two decimals, a tie away from zero, thousands with commas); a row the table does not hold is the words "not held". The page takes no difference between the two hubs.

**The period that heads a figure, and its mark.** A period is written as the year ("2025") or as the month's English name and the year ("August 2025"). It is followed by " (partial)" when the first hub's `n_intervals` for it is held and short of the full period by the rule of section 2 (a year: not 35,040, or 35,136 in a leap year; a month: below its days times 96, four fewer in March and four more in November). A period the table does not hold carries no mark (its figures read "not held"). The second hub's columns carry the first hub's mark: the two hubs hold the same intervals. The period is written so in: the three headline labels, each ending ", A, P" for the second year; the line under each headline number, which opens "P:" for the first year when the two years differ; the "Period" cell of each of the eight (or four) rows of the first table; the head of the second table ("Figure", then each period); and the section's line and head above.

**Checked on 16 November 2026,** on the tables of samueloldlaptop (built 29 September 2026), `python replication/ercot_peak_premium/replicate.py --write`, as printed:

- `674 of 674 views open as the note says (the hub, the period, the two years, the years marked, the rows' download, the freshness line)`
- `24786 of 24786 figures inside the tolerance, with the same text; 0 drawn by the page and not expected; 0 drawn two ways`
- `6214 of 6214 figures of the section of two hubs, in 122 views with a second hub, are the rows the note names, in its order, inside the tolerance and with the same text`
- `12172 of 12172 periods that head a figure are written as the note says (the headline numbers, the first table's period cells, the tables' heads, the two-hub line; '(partial)' where the period is not over)`

The 674 views are section 7's 550 and 124 with `vs` in the address: every ordered pair of the six hubs for the view a reader opens on (30); HB_WEST beside HB_NORTH for each of the twelve months with no year named (12) and for the whole year and each month with every pair of years (78); and the same hub twice, a hub the tables do not hold, one year alone, and a month the newest year does not hold yet (4, two of them with no section). The distinct figures stay 24,786: the section draws rows that the hub's own views already draw, and the page writes each the same way wherever it draws it (0 drawn two ways).
