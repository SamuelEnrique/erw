# Automated Analysis: the scanner (session 181)

The scanner looks every day over every public table of the Energy Research Warehouse (ERW) that has a time axis, and
flags five kinds of news. Each flag becomes a draft finding card computed by code. A person rules on each draft at
`/internal/findings`; nothing reaches `/analysis` before it is approved there.

- Code: `warehouse/analysis/findings/findings_scanner.py`. Thresholds: `warehouse/config/scanner.yaml`, the one file
  every threshold lives in. Review list: `public.scanner_drafts` (migration `029_scanner_drafts.sql`).
- No model is called anywhere: the chart, the callouts and the footnote of a draft are written by code from the flag.
  A draft has no paragraph.
- The impact study ("impact of X on Y") is an analysis of the findings engine and is described in
  [`automated_analysis_findings.md`](automated_analysis_findings.md).

## What is scanned

- The tables are not listed by hand. A table is scanned when `warehouse/metadata/coverage.csv` gives its license as
  public, its file is on the machine, and its columns are the series shape (`entity, variable, ts_utc, value`).
- A series is one value of the key: `key_columns` (entity, variable, market, node, freq), completed by
  `key_extra_columns` where a table has them (the interchange pair, an event, a strategy).
- Sub-daily series (freq PT5M, PT15M, PT1H) are scanned by UTC day: the day's mean, minimum and maximum. Daily, weekly,
  monthly and yearly series are scanned as they are. A series without a freq value takes its grain from the spacing of
  its own days; one that fits no grain is not scanned and is counted.
- `exclude_tables` leaves out, each with its reason: forecasts, the price board's presentation tables, the tables about
  past events, average shapes by hour and month, the network's seven-day replay window, and a table of records.
- The first run (10 October 2026, the data machine's tables): 117 tables, 36,852 series seen, 6,797 scanned, 105 pairs
  tested, in 198 seconds. Not scanned: 19 tables by `exclude_tables` or the known gaps; 28 public tables that are
  entities or events (no series of values); the series of four tables that fit no grain (`ai_power_regions`,
  `census_metro_population`, `noaa_grid_weather_stations`, `noaa_isd_hourly`). Of the series seen, 20,516 were too short
  or nearly constant, 7,300 held no fresh point, 139 belonged to a paused publisher.

## The five rules

Every number below is a key of `scanner.yaml`.

1. **Record high or low** (`record`). The newest value is above (below) every earlier value of the series' whole held
   history. The series must hold `record_min_points` earlier points (three years of days, three years of weeks, five
   years of months, ten years), so a young series does not flag daily. The record it breaks must have stood for
   `record_stood_points` points, so a series that climbs every month (a fleet's capacity) does not flag every month.
   The new value must pass the old record by `record_min_margin_sigmas` robust standard deviations of the history
   (1.4826 times the median absolute deviation).
2. **A negative price where there was none** (`negative`). A price series (unit `price_unit`, variable `price_variable`
   and not `price_variable_not`) whose day's lowest interval is below zero, when no interval was below zero in the
   prior `negative_prior_days` days, of which at least `negative_min_days_held` are held.
3. **A spike beyond a multiple of the series' own history** (`spike`). The statistic: the newest value against the
   `spike_percentile`th percentile of the series' values in the prior `spike_history_years` years (at least
   `spike_min_points` held). Flagged above `spike_multiple` times that percentile. Only for positive series: the
   percentile and the median above zero and at most `spike_max_negative_share` of the prior values below zero.
4. **A weekly change outside its five-year range** (`weekly`). Daily series: the mean of the newest 7 days minus the
   mean of the 7 days before, each with at least `weekly_min_days` days. Weekly series: the newest week minus the week
   before. Flagged when the change is beyond the largest or smallest such change of the prior `weekly_range_years`
   years (at least `weekly_min_years` held), by at least `weekly_min_excess_share` of the range's width.
5. **A break between two series that normally move together** (`pair`). The pairs come from the rules under `pairs`:
   `same_table` pairs the series of a table that share a variable, market and grain within one grid (hub against hub,
   zone against zone; a group above `pair_max_group` series is left out); `against_gas` pairs each named price series
   with the Henry Hub spot price. The measure is the residual of a regression: over the `pair_fit_days` days before the
   newest 7 days, y is regressed on x by least squares (at least `pair_min_days` days both hold). The pair "normally
   moves together" when that fit's R2 is at least `pair_min_r2`; otherwise it is not tested. The break: the mean
   residual of the newest 7 days is beyond `pair_break_sigmas` standard deviations of the 7-day mean residuals of the
   fit window, and beyond every one of them.

## What is never flagged

- **A paused publisher** (`skip_paused`): a series whose entity or source matches a pattern of
  `warehouse/metadata/paused_sources.csv`. MISO's own series are never flagged; EIA's figures for the MISO balancing
  authority are EIA's and are scanned.
- **A known gap** (`skip_known_gaps`): a table of `warehouse/metadata/known_gaps.csv`.
- **A known fault** (`suppress_known_faults`): a flag whose dates fall inside the dates of a fault that names its table
  in `known_data_faults.csv`. A fault recorded without dates covers its tables whole; one with a first day and no last
  is open. A suppressed flag is kept, named, in the run's `suppressed.json` and never becomes a draft.
- **A revised or partial newest day**: a point is evaluated only when it is `settle_days_default` days older than the
  scan's date (`settle_days` gives seven days to the tables built from EIA-930, which EIA revises). A sub-daily day
  with fewer than `partial_day_min_share` of the series' usual intervals is left out. A month or a year still open is
  never evaluated: a partial month is not a record low.
- **An old point** (`fresh_days`): a flag is raised only on a point whose period ended recently.
- **A unit change** (`skip_on_unit_change`): a series whose unit column changed is not scanned.
- **A change of definition** (`history_from_last_source_change`): a series whose source column changed is compared only
  with its history since the change.
- **A constant or a flag** (`min_distinct_values`).
- **A repeat**: the same rule, date, direction and value in a derived table and in its source table is one flag, kept in
  the source table.

## A flag, and its draft card

- A flag stores: the table, the series key, the date and the window of days, the value and its unit, the statistic, the
  threshold crossed (its name, its value, and the keys of `scanner.yaml` behind it), what it was compared with, the
  history's first and last day and count, the strength, and the scanner's `version`. The id is `scan-<rule>-<12 hex>`,
  a hash of the rule, the table, the series key and the date: the same flag has the same id on every run.
- The draft card: a chart of the series with the flagged point marked and its record, threshold or band drawn (hover
  shows values; at most `chart_points` points); two or three callouts (the number, its comparison, the date); a method
  footnote (the data, the years, the observations, the rule and the threshold crossed). It is drawn by the same card
  component as the findings of session 170 and is marked as a draft everywhere.
- Strength ranks the day's flags: how far past its threshold a flag is, in robust standard deviations of the series.

## Volume

- At most `max_drafts_per_day` drafts a day reach the review list, the strongest first; at most `max_drafts_per_table`
  from one table, `max_drafts_per_rule` of one rule, and `max_drafts_per_entity_rule` of one rule for one entity (an
  entity's variables move together: one event is one draft). Every flag stays in the run's `flags.json`.
- A flag already raised for the same date is never raised twice, whatever was ruled; a series with an open draft of the
  same rule is not raised again until that draft is ruled on.

## Where it runs

- **The data machine.** The rules compare with years of history, which only the data machine holds. Its daily run
  (`warehouse/run_data_machine.sh`) has the soft step `dm_scanner` after the sync: the scan, the run kept under
  `runs/scanner/<date>/` (`flags.json`, `suppressed.json`, `drafts.json`, `scan_summary.json`), the drafts added to the
  review list. About four minutes; no table is written and the data lock is not needed by the scan.
- **GitHub's runner** holds rolling windows: every rule would lose its history there (a record over the whole history,
  the prior year of prices, the prior three and five years, the 365-day fit). So the runner's daily run
  (`warehouse/run_daily.sh`) does not scan. Its soft step `scanner_request` queues the day's scan as a row of
  `analysis_requests` (finding `scanner_daily`); the data machine's worker takes it and runs the same scan. Without a
  service key the step exits `ERW_SKIP_EXIT` with its reason.
- Both are soft steps under `warehouse/health.py`: a failure is recorded and never stops a daily run. Neither calls a
  model.

## The review list

- `/internal/findings` (internal view only; the page takes no token in its address) lists the drafts, newest and
  strongest first, each with its card and three buttons.
- **Approve**: the card appears on `/analysis` in the group "Found by the scanner", with the date it flagged and the
  day it was approved. **Dismiss**: it never appears. **Ask for a full card**: where the flagged series is one the
  impact study knows and has a control in its unit, the impact study on that series around the flagged date (14 days,
  the default control) is queued for the data machine; otherwise the draft is marked and a session writes the card.
  Code never writes a paragraph that stands for analysis.
- Each ruling is kept with its time (`state_at`, `state_history`).

## What this is not

- A flag is a statement about the table: this value against that history. It is not a statement about the world until
  a person has read the rows. The first run's 17 flags held one artifact (a retail price that is a ratio over a handful
  of customers) and three that a later revision must settle.
- A record of a monthly series is a record of what the publisher has released; EIA revises its newest months.
- The pair rule tests whether two series parted, not why.
