# Method: the Flex Alert scorecard, the tool as a reader meets it

Energy Research Warehouse (ERW), session 7532 (chain 304), 16 November 2026. Page: `/grid/caiso/alerts` (in review).
Code: `site/app/grid/caiso/alerts/` (`page.tsx`, `Decisions.tsx`), `site/lib/flexalerts.ts`, `site/lib/reliability.ts`.
Replication: `replication/caiso_alerts/`. Faults found:
[`docs/reviews/caiso-alerts-faults-2026-11-16.md`](../reviews/caiso-alerts-faults-2026-11-16.md). Cross-check:
[`docs/reviews/caiso-alerts-crosscheck-2026-11-16.md`](../reviews/caiso-alerts-crosscheck-2026-11-16.md).

Before this note was written, the check asked for in the brief was made: no note of the page as a reader meets it
existed. [`flex_alert_scorecard.md`](flex_alert_scorecard.md) is the method of the analysis behind the page (the data,
the alert days, the regressions, the intervals, the value, the results) and its section 11 names the page's keys. This
note does not repeat it. It says what each view of the page shows, from which rows and by which rule, the choices with
their defaults, and what the page does not hold.

| Table (all public) | Its note | What the page reads from it |
|---|---|---|
| `flex_alert_effects` | [`flex_alert_scorecard.md`](flex_alert_scorecard.md), sections 3, 5 and 7 | every alert day (P1D), its evening hours (PT1H), each year (P1Y) |
| `flex_alert_model` | [`flex_alert_scorecard.md`](flex_alert_scorecard.md), sections 4 to 6 | the pooled figures, the model's check, the five specifications, the held-out hot days (not the coefficients) |
| `caiso_grid_emergencies` | [`caiso_grid_emergencies.md`](caiso_grid_emergencies.md), [`california_reliability.md`](california_reliability.md) | CAISO's notices: each alert day's kinds of notice, and how far the report runs |
| `caiso_dam_alert_day_hub_prices` | [`caiso_dam_alert_day_hub_prices.md`](caiso_dam_alert_day_hub_prices.md) | not read by the page; behind every value figure, and read by the replication |
| `noaa_isd_hourly`, `eia930_all_demand` | [`flex_alert_scorecard.md`](flex_alert_scorecard.md), section 2 | not read by the page; behind every prediction |

This note carries no tables line of its own: each table's note above stays the one the coverage page links.

## 1. What the tool is, and what it is not

For every day from July 2018 on that CAISO called a Flex Alert or a grid emergency for its whole area, it sets the demand
CAISO served in the alert hours beside what a weather-and-calendar model predicted for those hours, and puts the
day-ahead price on the difference. One page, no input: a reader chooses nothing. Every figure is a row of the two
derived tables, drawn with its check key (`series|<table>|<entity>|<variable>|<ts_utc>`), except the few words and
counts section 5 names.

It is not the effect of the Flex Alert message alone. On the same evenings paid programs, utilities' demand response,
the state's text alerts and, on 2020-08-14 and 2020-08-15, rotating outages all move demand; the page says so in its
last section. It is not a forecast, and it values no avoided outage.

## 2. The views, top to bottom

- **The title** names the first and last year of the alert days held (since session 7532 from the rows; it was a fixed
  "2018 to 2024").
- **"The answer, pooled"** (`flex_alert_model`, ts 2018-07-01, entity `erw:flex_alert_model`): `pooled_days`,
  `pooled_hours`, `pooled_reduction_mw` with `_lo` and `_hi`, `pooled_reduction_pct`, `pooled_reduction_mwh` with `_lo`
  and `_hi`. The words "below" or "above" follow the sign of `pooled_reduction_mw` (zero reads "below"); "includes zero"
  is printed when `_lo` < 0 < `_hi`, else "excludes zero". Under "How to read it": `oos_bias_mw`, `oos_rmse_mw`,
  `oos_mape_pct`, `oos_days`. The table of models: for each of the five specifications, `variant_<id>_oos_bias_mw`,
  `variant_<id>_oos_rmse_mw`, `variant_<id>_pooled_reduction_mw` with `_lo` and `_hi`. Under it:
  `heldout_threshold_temp_f`, `alert_days_hotter_than_threshold`.
- **"Every alert day, ranked"**: the P1D rows of `flex_alert_effects`, one row a day, sorted by `reduction_mw`, largest
  cut first. Columns: the day (a link to its panel); CAISO's notices (below); the alert hours, `alert_first_hour` to
  `alert_last_hour` (the window's end, so "16:00 to 21:00" is five hours), "(assumed)" where `hours_assumed` is 1;
  `temp_max_f`; `train_days_as_hot`; `reduction_mw` with its interval; `reduction_pct`; `value_usd`, or "no price".
  A hover beside the lead names the one alert day of CAISO's notices that is not scored (2021-07-12, since session 7532).
- **CAISO's notices** (the second column): every kind of notice in `caiso_grid_emergencies` whose `event_date` is that
  day, in any region, Restricted Maintenance Operations and transmission emergencies left out, named Flex Alert, EEA
  Watch, EEA 1 to 3, Alert, Warning, Stage 1 to 3, Load interruption. The notices are read from 2018-07-01 to the day
  the page is drawn (since session 7532; it read to 2025-10-31).
- **"Year by year"**: the P1Y rows, `year_days`, `year_hours`, `year_reduction_mw` with `_lo` and `_hi`,
  `year_reduction_mwh`. The chart draws a bar a year (green where the cut is positive, cardinal where negative) and the
  interval as a whisker; its axis ticks are the smaller of zero and the lowest `_lo`, half of it, zero, half the larger
  of zero and the highest `_hi`, and that value, each rounded to a whole MW.
- **"Each alert day through the evening"**: a panel a day with `reduction_mw` in its caption and a chart of the PT1H rows
  from 12:00 to 23:00 Pacific: `actual_mw` (cardinal), `predicted_mw` (dashed), the band `predicted_mw_lo` to
  `predicted_mw_hi`, and a box on each hour with `alert_hour` 1. The axis labels are the lowest and highest of actual and
  the band, in whole GW. Since session 7546 each hour carries a hover over a full-height strip of the hour, in whole MW
  (JavaScript's rounding): "H:00 to H+1:00: served `actual_mw` MW, model `predicted_mw` (band `predicted_mw_lo` to
  `predicted_mw_hi`), predicted less served `predicted_mw` less `actual_mw`", with ", alert hour" where `alert_hour` is 1,
  and "not held" for a value the rows lack. The strips are not alert-hour boxes.
- **"What it was worth, at the day-ahead price"**: `pooled_value_hours`, `pooled_value_usd` with `_lo` and `_hi`,
  `heldout_price_mean_usd_mwh`; the count of alert days with a `value_usd` row, of all alert days. A figure in dollars
  of a million or more is printed in millions or billions to two decimals; under a million, in whole dollars (since
  session 7532; it printed thousandths of a dollar).
- **"The model's check"**: a dot for each held-out day of `flex_alert_model` (P1D rows): `heldout_error_mw` against
  `heldout_temp_max_f`; the axis runs from minus to plus the largest absolute error, and from the coolest to the hottest
  held-out day's high, one decimal.
- **"What the estimate can and cannot say"**: words, and one sentence from the rows (since session 7532): how far CAISO's
  notices run as the warehouse holds them (the latest `event_date`), and whether any day after the last scored alert day
  carries a notice of an alert kind, which the scorecard would not yet hold. On the tables of 16 November 2026: the
  notices run to 2026-10-08 and none follows 2024-07-24. Since session 7546 (the read,
  [`caiso-alerts-read-2026-11-16.md`](../reviews/caiso-alerts-read-2026-11-16.md)): the first point adds the years the
  two paid programs began (ELRP 2021, DSGS 2022) and what ran in August 2020; a point sets two published figures beside
  the page's rows, CAISO's day-ahead peak forecast against the peak on 2020-08-17 (Final Root Cause Analysis, Table 5.1)
  beside the model's highest `predicted_mw` hour of that day, and the EIA's drop of 2,100 MW on 2022-09-06 beside that
  day's `reduction_mw`; and the sentence linking the two heat-wave pages says their day estimate is another measure.
- **The decisions** (since session 7532): section 6, at the foot.

## 3. The rules a second implementation needs

All in [`flex_alert_scorecard.md`](flex_alert_scorecard.md), and as the replication applies them:

- **An alert day** is a local day covered by a whole-area notice (region `ISO`, or `CAISO Grid` from 2024) of the eleven
  kinds of section 6, row 1. A single-day time frame whose text names another day than the row's date is the text's day
  (the one case: the Flex Alert dated 2020-09-30 is for 2020-10-01). Over the sample, 2018-07-01 to 2025-10-31, the rule
  gives 39 days; the scored 38 are those with all 24 hours of demand and weather.
- **The alert hours** are the local hours covered for at least 30 minutes by the day's Flex Alert windows, else its
  emergency notices' (EEA Watch, EEA 1 to 3, Alert, Stage 1 to 3, load interruption), else its Warnings'; a window over
  several days covers each with its clock window; 23:59 is midnight. In the table: the PT1H rows with `alert_hour` 1.
- **A day's cut** is the mean over its alert hours of `predicted_mw` less `actual_mw`; MWh the sum; percent the sum over
  the sum of `predicted_mw`, times 100. **A year's and the pooled** are the same over every alert hour of the year or of
  all days.
- **The value** is the sum over alert hours of the cut times the mean of the SP15 and NP15 day-ahead prices
  (`caiso_dam_alert_day_hub_prices`, `lmp_dam`, an hour only with both hubs).
- **The model's check**: `oos_days` is the count of held-out days; `oos_bias_mw` their mean `heldout_error_mw` (each day
  is the mean of the same five hours, so the mean of days is the mean of hours); `heldout_threshold_temp_f` the coolest
  held-out day's high; `alert_days_hotter_than_threshold` the alert days whose `temp_max_f` is at least that.
- **Training days as hot**, for an alert day at or above the threshold, is the count of held-out days whose high is at
  least the day's: every training day that hot is in the held-out tenth. Below the threshold the training days' highs
  are not in the tables.
- **What only the panel can rebuild:** each interval (1,000 bootstrap replicates, seed 20261002), the four other
  specifications, the error over hours (`oos_rmse_mw`, `oos_mape_pct`), each day's high (`temp_max_f`, from
  `noaa_isd_hourly`), and the predictions themselves. `notebooks/flex_alert_scorecard.ipynb` rebuilds them from the
  inputs and asserts each equal to the tables.

## 4. What is recomputed, and what was found

`replication/caiso_alerts/replicate.py` (Python, standard library), written from this note, the scorecard's method and
the tables. `site/scripts/caiso-alerts-figures.mjs` draws the page with its own function, its reads answered from the
tables' files, and writes every figure it drew to `page_figures.json`.

On 16 November 2026, on `flex_alert_effects` and `flex_alert_model` as retrieved on 2 October 2026 and
`caiso_grid_emergencies` as retrieved on 13 October 2026 (the report revised 10/09/2026): **634 figures of the page.
471 rebuilt from the public tables: 467 agree inside half the page's last shown digit, 4 differ and are named. 163 are
figures only the panel can rebuild, each named with its reason.** The 471 are 433 checked numbers less the 163 (270),
the 38 days' alert hours from the notices' own windows, the 38 days' kinds of notice, the 38 day charts' two axis
labels and their alert-hour boxes (152), the two other charts' labels and dots (3), and eight words and counts.

The four named differences (faults file, rows 3, 6 and 7):

- 2021-07-29, percent: the page prints -0.18; from the hours, -0.17497, which is -0.17. The table holds -0.175 (three
  decimals) and the page rounds it again.
- 2024, MWh: the page prints -16,893.33; from the hours, -16,893.3249. The same double rounding.
- 2023-07-26, training days as hot: 77 on the page, 78 from the held-out rows: two held-out days share the day's own
  high, 87.926 F, at the table's three decimals; the builder compared unrounded highs.
- 2020-10-01, CAISO's notices: the page prints "Alert"; by the rule, "Alert, Flex Alert". The table dates that day's
  Flex Alert 2020-09-30, the day it was issued.

Since session 7546 the page draws 1,092 figures: the 634 above, 456 hours' hovers and two checked numbers in the
cautions (the model's highest hour of 2020-08-17 and the cut of 2022-09-06). **929 rebuilt: 925 agree, the same 4
differ and are named; 163 named as panel-only.**

`python replication/caiso_alerts/replicate.py` runs on `public_rows.csv` and `notices_rows.csv`, the rows the page reads,
copied beside it, and prints the same counts. `replicate.do` rebuilds the five headline figures in Stata from
`public_rows.csv`, the expected values at its top; Stata is not on the machine that wrote it, so it has not been run.

## 5. The cross-check against published figures

In [`docs/reviews/caiso-alerts-crosscheck-2026-11-16.md`](../reviews/caiso-alerts-crosscheck-2026-11-16.md): the
notices table's days by year and kind against CAISO's own yearly counts (66 of 71 equal; the five that differ named),
the page's alert days by year against CAISO's Flex Alert days, and the page's estimate for 2022-09-06 against the U.S.
EIA's account of that evening.

## 6. The decisions on the page

The page has no input, so no choice is editable. Each choice below is fixed when the tables are built, moves a figure,
and is drawn at the foot of the page with its default and its source on hover
(`site/app/grid/caiso/alerts/Decisions.tsx`; `site/scripts/test-caiso-alerts-render.mjs` holds this table and that list to
the same keys in the same order).

| # | Key | The choice | Default | Source |
|---|---|---|---|---|
| 1 | `alert-day` | Which notices make an alert day | Flex Alert, EEA Watch, EEA 1 to 3, Alert, Warning, Stage 1 to 3, load interruption; the whole area only. 39 days | CAISO, Grid Emergencies History Report; `flex_alert_scorecard.md`, section 3 |
| 2 | `alert-hours` | Which hours of the day are alert hours | the Flex Alert's window, else the emergency's, else the Warning's; 30 minutes covered; 204 hours | the notices' time frames; section 3 |
| 3 | `complete-day` | A day enters only with all 24 hours of demand and weather; the demand screen | complete days only; 27 hours screened; 2021-07-12 left out | EIA-930, CISO; section 2 |
| 4 | `weather` | Three airports, weighted | Los Angeles 0.50, Sacramento 0.30, Fresno 0.20 | NOAA NCEI, Integrated Surface Database |
| 5 | `sample` | The days the model learns from | the non-alert days of May to October, 2018-07-01 to 2025-10-31: 1,276 | section 2 and 4 |
| 6 | `model` | The specification | every term ("chosen"): -503.2 MW pooled; "base" gives +861.2 | sections 4 and 6 |
| 7 | `sign` | The cut is predicted less actual, the mean over hours | positive is a cut; MWh the sum; percent over predicted MWh | section 5 |
| 8 | `interval` | The interval | 90 percent, 1,000 replicates, seed 20261002 | section 5 |
| 9 | `bias` | The hot-day error is shown, not taken off | not netted (-239.3 MW; netted, -742.5) | section 6 |
| 10 | `price` | The value's price | the mean of the SP15 and NP15 day-ahead prices, both hubs; 4 days | CAISO OASIS PRC_LMP |
| 11 | `notices` | The notices cell | every kind dated that day, any region, RMO and transmission left out | `caiso_grid_emergencies` |

## 7. What the tool does not hold

- **An alert day after 2024-07-24.** CAISO's report, revised 9 October 2026 and read again on 16 November 2026, lists no
  Flex Alert or emergency notice from 2024-07-25 to 2026-10-08, so the 2025 and 2026 seasons have none: a true zero, not
  a gap. The scorecard's sample ends 2025-10-31 and the tables were built on 2 October 2026 from the report then held;
  an alert day after that would need the builder run again with a longer sample.
- **A value before July 2023.** OASIS serves about 39 months of prices; the 2020 and 2022 heat waves have no value.
- **The effect of the message alone,** of each program, of the text alert, or of a minute: hours only.
- **The predictions' inputs** (demand and weather hour by hour) are not on the page; the notebook holds them.
- **Restricted Maintenance Operations and transmission emergencies** are not counted here; the Reliability section of
  `/grid?grid=caiso` counts them.

## 8. Added to the scorecard's method by this session

[`flex_alert_scorecard.md`](flex_alert_scorecard.md) says in section 3 that the report ends 2025-04-30. A dated line
added there says what the report revised on 9 October 2026 holds (see section 7 above).
