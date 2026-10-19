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
  tested, in about four minutes (198 to 251 seconds). Not scanned: 19 tables by `exclude_tables` or the known gaps; 28 public tables that are
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
  the source table. Since version 1.1.0 (`repeat_follows_lineage`) a flag is also a repeat when a table its own table is
  derived from has a flag of the same rule, date and direction in the same place: a derived sum that holds the flagged
  series is the same event in another number. The lineage is the header line `# Derived from:` that a derived table
  carries, followed through the tables between; the place is the series' `geo` value, and a series without one place
  is never dropped this way. Each such repeat is kept, with the flag it repeats, in the run's `scan_summary.json`.

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

## The review of the first run (session 191)

The 17 flags of the first run were read again against their rows on the data machine on 11 October 2026
(`runs/session191/`). The 13 that session 181 judged real stand. The other four, each with what its rows say and
whether a threshold of `scanner.yaml` raised it:

| Flag of the first run | What the rows say | Raised by a threshold? | Change |
|---|---|---|---|
| District of Columbia, industrial retail price, record high (the artifact) | The class has one customer (`eia:customers:DC:IND` is 1 in every month held, 0 in a few). The price is one customer's bill over its sales: 38.4 to 321.5 USD per MWh inside 26 months, and a change of 159.4 in one month. The national industrial price never moved more than 14.3 in a month | No. The record passed the old one by 1.84 robust standard deviations of the levels and 3.2 of the yearly changes; a margin that drops it drops every record of the run but one | None. It is a draft to dismiss |
| Utah, residential sales, record high (uncertain) | July 2026 is 11.7 percent above the old record (July 2024). Customers grew 0.8 percent between the two; use per customer was 1,292 kWh against 1,204 in the highest earlier July (2022). Colorado's residential sales set their own record the same month; Idaho, Wyoming and Montana had their highest July; Nevada, Arizona and New Mexico did not. Growth explains under a tenth of it. No temperature for Utah is held, so heat is not shown, only that the customers did not cause it | No | None |
| Indiana, generation from other gases, record low (uncertain) | Not one low month: 269,327 MWh in March, 268,928 in April, 125,902 in May, 65,787 in June, 133,037 in July. June is the second month under 100,000 in the 25 years held (May 2009: 88,633). The table still holds June at that value after July was published | No. It passed the old record by 0.61 where 0.5 is asked; the real records of the run stand between 0.52 and 0.80 | None |
| Indiana, oil and other gases, record low (uncertain) | The derived sum that holds the row above: the rest of the sum was 42,979 MWh that month, as in other months. One event, flagged twice | Yes. The repeat guard asked for the same value in the two tables, and a sum is another number | `repeat_follows_lineage`, version 1.1.0 |

- **What changed:** version 1.1.0 adds one guard and changes no number. On the same tables and the same scan date the
  run raises one flag fewer (Indiana's sum) and the same drafts. The week of Winter Storm Uri (`--date 2021-02-22`,
  every table): 275 flags and 12 drafts under both versions.
- **A one-customer class is not guarded against.** The customers table says which classes are one bill
  (`eia_retail_sales_monthly`, variable `customers`): the District's industrial class is the only one under 200
  customers. A guard for it would be a rule about one publisher's tables, and is left for a ruling.
- **A flag depends on the day it is scanned.** The weekly rule looks at the newest settled week only. The first run
  flagged the week to 29 September in `cftc_cot_positions`; a scan of the same date on tables that already hold the week
  to 6 October does not. A daily scan sees each week once, when it is the newest.

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
- Session 231: a draft approved here can be chosen for the Roundup. `roundup_pick.py` reads its card from the review
  list, and only while its state is approved.

## The daily chart in the Digest

Session 232, Samuel's ruling of 12 October 2026: every weekday Digest carries one chart, a fact and its picture, chosen
and drawn by code with no model and no approval (`warehouse/analysis/findings/daily_chart.py`). It is separate from the
review list: a flag needs no ruling to be the day's chart, and being the day's chart does not approve its draft.

- **The rule.** (1) The day's strongest scanner flag: records and first negative prices first, then by how far past
  its threshold (the flag's strength, in robust standard deviations of the series' own history), ties by the flag's id.
  (2) A flag a Digest has already shown is never shown again: a monthly record stays fresh to the scanner for 130 days
  (`fresh_days`), and without this the Digest would print one chart every day. The memory is
  `docs/digest/charts/<date>.json`, one file a chart shown. (3) If the scanner flagged nothing that day, or nothing a
  Digest has not shown: the watch list's largest change of the latest period (`warehouse/analysis/watch.py`), in the
  same form. "Largest" is the share of the measure's own earlier changes that the newest one exceeds
  (`warehouse/analysis/run.py`, `change`), ties by the change in robust standard deviations of the earlier ones; the
  newest period must have ended within 14 days (a week) or 100 days (a month, EIA's lag), and a change already shown is
  not shown again. (4) If neither: no section, and the reason is in the run's log, as for the fun fact.
- **A record that jumps waits a day** (session 267, the brief of 14 October 2026). A record more than 25 percent past
  the old one (`RECORD_JUMP`; `record_jump`, `must_wait` and `choose` in `daily_chart.py`) is not shown on the run that
  first sees it: it is kept in `docs/digest/charts/held.json` (`keep_held`, with the day it was held, the value, the old
  record and the jump) and the rule goes on to the next candidate. On a later day's run (`held_before`) it may be shown,
  if the scan raises it again; if the scan no longer raises it (a revision, a unit, a missing month), it is never shown.
  A jump that large is as often an error as a record: the Digest of 13 October 2026 showed Wyoming's natural gas
  generation 34 percent past its old record, and the proof of 7 October one 103 percent past. A proof holds nothing; a
  check run (`brief.py --out`) reads the real file and writes beside its own output.
- **Only public-licensed tables.** A table whose license in `coverage.csv` is not public, or that
  `license_status.csv` marks "license needed", is never a candidate; nor is a table or a series of NYISO or SPP, which the
  ruling of 12 October 2026 holds until their licenses are answered (`HELD` in `daily_chart.py`; a person lifts it by
  editing that line). A paused publisher's series is never flagged at all.
- **Two machines.** The histories are on the data machine and the Digest is written on GitHub's runner. After each
  daily scan the data machine ranks the day's flags, computes each one's card, adds the watch list's changes, keeps them
  in `runs/scanner/<date>/daily_chart.json` and writes one row for the day to the internal table
  `daily_chart_candidates` (migration 030; no page reads it). `brief.py` asks for the day's row, waits up to seven
  minutes for it (the worker takes the runner's request within a minute and scans for about three), and uses the day
  before's when it is not there. With no row at all it tries the watch list on the runner's own tables.
- **The fact** is written by code from the flag's numbers (`fact_from_flag`) or from the watch line's
  (`run.py`'s `finding`). A series is named in plain words only where its codes are ones the file knows (states, EIA's
  fuels and sectors, CAISO's reserve products); any other series keeps the name the table gives it. The exact table
  and series key are printed under the fact, with a link to the table.
- **The picture** is the flag's finding card drawn by matplotlib in the house style
  (`warehouse/analysis/findings/card_image.py`): the title, the fact, the series with the flagged point and its record
  or threshold marked, the card's three callouts and its source line. 1200 by 880 pixels, shown at 600 in the email.
  The site's Digest shows the same file (`/digest-charts/<date>.png`, copied at build).
- **What it does not do.** It never writes a sentence that explains the number. It never shows a draft's approval
  state. A scan as of a past day over today's tables (the proofs of 6 to 12 October 2026 in `docs/digest/charts/`,
  each marked `"proof": true` and never counted as shown) can differ from what that day would have computed, because
  publishers revise.

## What this is not

- A flag is a statement about the table: this value against that history. It is not a statement about the world until
  a person has read the rows. The first run's 17 flags held one artifact (a retail price that is a ratio over a handful
  of customers) and three that a later revision must settle.
- A record of a monthly series is a record of what the publisher has released; EIA revises its newest months.
- The pair rule tests whether two series parted, not why.

## The publisher's figure beside a record (session 316, 19 October 2026)

The owner's ruling of 19 October 2026 on the Research pack's question 4 (option b). A draft the scanner raised as a record of EIA's newest month (rule `record` on a table EIA's API answers for, `eia_*`) carries, before it can be approved, the figure EIA's own data service holds for that series and month: `warehouse/analysis/findings/publisher_figure.py`, run on the data machine after the daily scan, asks `api.eia.gov/v2` once per draft and month (the series' route and facets as the connector `eia_series.py` reads them: the state and sector of a retail price, the location and energy source of generation; the series id for the petroleum routes), records the value as EIA writes it and in the ERW's unit by the connector's conversion, the address without the key and the time of the read, and writes them into the draft's card (`card.publisher`). `/internal/findings` shows the figure beside ours with whether the two agree; the approval route (`site/app/internal/findings/state/route.ts`) refuses "approved" for such a draft while the figure is missing. A read that fails leaves the draft without a figure (none is made up) and the script exits 1. A record on any other table is approved as before.

