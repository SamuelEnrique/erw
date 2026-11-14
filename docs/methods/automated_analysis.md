# Automated Analysis: method

Platform tool 26, built in session 23. A library of chart templates runs on the Energy Research Warehouse (ERW) every week. A fixed rule, not a model, scores each result against its own history and picks the chart of the week, which the Energy Roundup and its email carry. The code is in `warehouse/analysis/`; its output is in `docs/analysis/` and on the site's `/research` (Research since session 238; `/analysis` redirects there).

## Templates

Each template is one Python module in `warehouse/analysis/templates/`. It has:
- a method in plain words;
- parameters with defaults and choices (ISO, hub, window and so on);
- a `compute` function that returns a tidy frame (one row per plotted value, naming its table), the citations of every table it read (`erw.cite`), a headline number with its history, and the sentences that hold every number a note may use;
- a `render` function that draws the house-style chart in three sizes:
  - **site:** an interactive ECharts option;
  - **email:** a PNG of 1200 by 750 pixels, shown at 600;
  - **social:** PNGs of 1200 by 627 and 1080 by 1080.

  The palette is Stanford's (cardinal first), titles are in Georgia, and the ERW mark sits at the top right. The source line is burned into every PNG.

| Template | Tables | Headline (its history) |
|---|---|---|
| `peak_premium_block`: peak premium by time-of-day block, any ISO with 15-minute prices | `<iso>_rtm_*_prices` (and ERCOT's yearly history tables) | peak minus midday median, latest 7 days (every earlier 7-day window) |
| `da_rt_spread_by_hour`: day-ahead minus real-time by hour | `<iso>_dam_*`, `<iso>_rtm_*` | mean spread, latest 7 days (earlier 7-day windows) |
| `forecast_error`: day-ahead demand forecast error by ISO | `eia930_<ba>_demand` | MAPE, latest 7 days (earlier 7-day windows) |
| `curtailment_midday`: CAISO curtailment against midday prices | `caiso_curtailment_daily`, `caiso_rtm_hub_prices` | wind and solar curtailed, latest 7 days (weekly since 2022) |
| `implied_heat_rate`: day-ahead price over Henry Hub | `<iso>_trader_daily` | mean, latest 7 operating days (earlier runs of 7) |
| `storage_evening_peak`: CAISO batteries against the evening peak | `caiso_battery_storage`, `eia930_ciso_demand` | mean battery output 17:00 to 21:00 Pacific, latest 7 days (weekly since 2025-08) |
| `negative_price_hours`: negative-price hours by month | `<iso>_rtm_*` (ERCOT with its yearly tables) | count in the latest complete month (every earlier complete month) |
| `deals_by_month`: deals by month and type | `energy_deals` | deals in the latest ended month (every earlier month) |
| `datacenters_by_state`: facilities by state and source | `datacenter_facilities` | facilities with a stated state (the values earlier weekly runs stored) |
| `chokepoint_transits`: tanker transits (internal) | `portwatch_chokepoint_transits` | mean daily transits, latest 7 days (weekly since 2019) |

Each template's own method, shown on `/analysis` and in `docs/analysis/templates.json`, defines its blocks, windows and completeness rules. The CAISO battery table, `caiso_battery_storage`, was added in session 23 for the storage template (`warehouse/connectors/caiso_outlook.py`), because EIA-930 returns no battery series.

## The engine (`warehouse/analysis/run.py`)

1. **Run every template** at its defaults. A template whose inputs are not in the warehouse on the machine is skipped, and the week's `results.json` names it with the reason.
2. **Score notability.** For each headline value `x`, the history is its earlier values from the tables, plus those earlier weekly runs stored in `docs/analysis/history.csv`. The score is:

   robust z = |x - median(history)| / (1.4826 x MAD(history)), capped at 10.

   When the MAD is 0 (a sparse history, mostly one value), the scale is 1.2533 times the mean absolute deviation instead. The percentile of `x` in its history is reported beside the z. A template is eligible when it has at least 8 earlier values and its headline period ended within the last 45 days.
3. **Pick the chart of the week:** the eligible public template with the highest robust z. Ties go to the earlier template in the order above. An internal template never leaves the warehouse's machines: it is not written under `docs/`, not in the gallery, and never picked.
4. **Write the note and the caption.** The model drafts a two-sentence note and a social caption of at most 240 characters from the template's own sentences and headline. The chat's literal-number check (`warehouse/chat/ask.py`) then requires every number in them to appear in those sentences as written. A failed draft gets one regeneration with the problems named. If that also fails, the note is the template's first two sentences as written.
5. **Write the outputs** to `docs/analysis/YYYY-Www/`:
   - `chart_of_the_week.json`, the three PNGs and `results.json` (every public template's headline, score and chart);
   - the social PNGs and caption, copied to `docs/analysis/social/` for posting by hand;
   - every template's headline, appended to `docs/analysis/history.csv`.
6. **Recompute the gallery.** Every public template runs over its grid of parameter choices (a hub's choices are the nodes of the ISO's tables). Each result is written to `docs/analysis/gallery/<template>/<params>.json`, and the list to `gallery/index.json`.

   The site's gallery serves these files. The charts are computed by the same Python templates from public tables, on the warehouse's side, so the site needs no second implementation. What the site cannot do is compute a parameter value outside the grid.

## The rule since session 119: the week's most notable real change

Steps 2 to 4 above are the rule of session 23, kept here as the record. On Sunday 4 October 2026 that rule chose "Energy deals in the news, by month": 59 deals in September, the most of any month. It was true and it was not news. The count is of what the ERW has read, and the ERW began reading in late September. A headline's level against its own history rewards anything that grows with the warehouse. The caption then said "with a robust z of 2.73 against its own history", which states a statistic and not a finding.

The rule now (`warehouse/analysis/run.py`, its docstring):

1. **Real.** Only a measurement of the energy system competes. A count of what the ERW itself has collected (deals in the news, facilities in the tracker) is still run and shown in the gallery, and is never the chart of the week. A template says which it is (`ABOUT`).
2. **A change, not a level.** The statistic is the headline's change from the period it is compared with: the week before, for a weekly figure; the same month a year earlier, for a monthly figure with a season in it. A template or a line says which (`COMPARE`).
3. **Notable against its own recent past.** The change is ranked by size among the same measure's own earlier changes: the last 104 for a weekly figure, the last 36 for a monthly one. The score is the share of those that were smaller, 0 to 100. At least 8 earlier changes are needed.
4. **This week's.** The headline period must be new: one this measure has not shown as its headline in an earlier week's run (`docs/analysis/history.csv`). It must also have ended within the last 100 days, because EIA's monthly figures arrive about two months late.
5. **The highest score is chosen.** Ties go to the higher robust z of the change over the same window, then to the order of the list.

If nothing new passes, the largest change among measures whose period is not new is chosen, and the chart says so. If no measure has 8 earlier changes, the level rule of session 23 is used, and the chart says so.

**Why a rank and not a z.** The first version scored a robust z of the change over the measure's whole history. On its first trial it chose US battery storage in operation: 743 MW added in August 2026, with a z of 9.32. Of the 138 earlier months, 29 had added as much. Most of that history is the years when almost nothing was added, so the median and the spread were near zero and any modern month looked extreme. A rank over a recent window says what the caption says.

**The caption states the finding, and code writes it.** Two sentences from the table's own numbers: what the measure was, in which period, how far it moved from the period it is compared with, and how that move ranks among the earlier ones. For the week of 4 October a trial of the rule (not published: that week's chart had gone out) gives: "CAISO Regulation Up day-ahead price, weekly mean: 5.04 USD/MW in the week of 2026-09-28 to 2026-10-04, up 1.73 from 3.31 the week before. Of the 104 week-to-week moves before it, 7 were as large." Second, with the same rank and a lower z: "WTI spot price at Cushing, weekly mean: 93.57 USD/bbl in the week of 2026-09-21 to 2026-09-27, down 9.97 from 103.54 the week before. Of the 104 week-to-week moves before it, 7 were as large." The model still drafts the two-sentence note, from the template's sentences and the finding, under the literal-number check; it is told to name no statistic. The model's own caption is kept beside the finding in `chart_of_the_week.json` (`model_caption`) and is not published.

`chart_of_the_week.json` also lists `also_moved`: the next five by the same rule, each with its finding.

**The chart shows the number the finding names (session 533).** The Roundup audit of 21 October (`docs/reviews/roundup-audit-2026-10-21.md`, fix 11) found that the chart of the week of 2026-W39 named 28.08 USD/MWh, the latest week's peak-minus-midday gap at ERCOT HB_NORTH, while its chart drew only the 30-day block quartiles: no bar held that number. Two changes. First, `peak_premium_block` now draws the spread the headline names, one bar for each of the latest 26 seven-day windows, the latest being the headline; the 30-day quartiles stay in its facts and its frame, and its title is unchanged, since the Roundup prints it. Second, wherever a chart holds its headline, the chart rings it in cardinal and labels it with the figure and its key (the week or the month): `templates/common.py` `headline_mark` finds the place (the headline's period on a category axis, and a series whose value there equals the headline's), and `style.py` draws it on the site's chart (an ECharts `markPoint`, which the site's SVG reader draws) and on every PNG. The mark is found, never supplied: a chart that does not hold its headline (a time axis of days under a weekly figure, a chart by hour or by state) shows no mark rather than a number it does not hold. W39 computed again from the tables, cut at 2026-09-26, gives the same 28.08 and the same 89 earlier windows; its before and after are in `docs/brand/review-533/`.

## The watch list (`warehouse/analysis/watch.py`, session 119)

The ten templates read 8 of the public tables. A measure on the watch list needs no module: one line names a public table, an entity, a variable, how a period is made of its rows, and what the period is compared with. The engine runs the lines beside the templates and chooses among all of them by the one rule. A line draws a plain line chart of its measure.

- A week is Monday to Sunday, UTC. It counts only with enough rows (4 of a business week for a daily price, 7 for a daily figure of the grid, 160 of 168 for an hourly one). The week under way, and the month under way, are not shown. Nothing is filled.
- A monthly line that says `whole` counts a month only when every day of it is held.
- A table behind a fix held for approval is not watched. The carbon intensity tables carry months the faults register calls wrong (`docs/methods/impossible_hours.md`), so no line reads them until that hold is lifted.

**Which public table is read, and which is not.** `docs/analysis/tables.json`, written on every run, lists every public table of `coverage.csv` with the templates and lines that read it, or the reason none does. The reasons are stated ones: a list of things or events and not a series; an input of a table that is read; a study of past events; yearly figures; figures by hour of the day; the latest values only; EIA's daily sums, which can hold a faulty hour. The last reason is the plain one: no template or line reads it yet. The count is in the file, not in this note.

**On GitHub's runner** the Roundup's job restores only the rolling-window tables. It now also restores the tables the lines read (`scripts/sync.py --tables`, the pattern from `watch.py --tables`). A line whose table could not be restored is skipped and named, like a template.

## Schedule

`.github/workflows/roundup.yml`, Sundays at 23:00 UTC:
1. restore the tables;
2. run `run.py`;
3. write the Roundup;
4. commit and push;
5. send the email, whose image links the pushed PNG.

On the runner, templates whose inputs are not restored skip with their reason. The ERCOT yearly history tables are not on the runner, so there `peak_premium_block` and `negative_price_hours` use the live tables only.

## Final form: what runs by itself, and what waits for a person (session 5004)

Roadmap item 2 asks for "Automated Analysis in its final form" ("fully automatic, on its schedule", the chain prompt of 13 November 2026). What runs with no person, read from the workflows and the data machine's registrations on 13 November 2026:

| Part of the page | What makes it | Clock | Last made, as held on 13 November 2026 |
|---|---|---|---|
| This week's chart and the week's results by the rule | `warehouse/analysis/run.py` in `.github/workflows/roundup.yml` | Sundays 23:00 UTC (started by pg_cron, the workflow's own schedule the fallback) | `docs/analysis/2026-W45/` |
| Today's chart (the Digest's chart of the day) | `warehouse/analysis/findings/daily_chart.py`, from the scanner's rows | the daily run | `docs/digest/charts/2026-11-12.json` |
| The scanner's findings and the weekly hunt | `warehouse/analysis/findings/`, the data machine's `register_weekly_hunt.ps1` (Saturdays) and `register_findings_worker.ps1` (at log-on and start-up) | weekly and on the data machine's start | the findings library's cards |
| The archive | the two above, listed by the page at build | every build | 13 daily, 6 weekly charts |

**The week, end to end, as a dry run (session 5075, 13 November 2026).** `python warehouse/analysis/run.py --out-dir <folder>` runs the whole weekly job (every template and watch line, the rule's choice, the three charts, the caption, `chart_of_the_week.json`, `results.json`, the history, `templates.json` and `tables.json`) into a folder outside the repository: no model is called, no status row is written, and nothing under `docs/` or `warehouse/` moves; the history starts as a copy of `docs/analysis/history.csv`, so each change is scored against the same earlier weeks as the Sunday run. With `ERW_BACKEND=live` the tables are the live set's public ones. Run on this laptop on 13 November 2026 for 2026-W46: 17 measures ran and 24 skipped with their reasons (a table held for its license, or not in the live set); the rule chose Brent's weekly mean (100.41 USD per barrel in the week of 2 to 8 November, down 20.76, the largest week-to-week move of the last 105), and the five files the site's build reads were made. The same run for 2026-W45 on 13 November chose Brent too, where the Sunday run had chosen the Lower 48's battery discharge: on 8 November Brent's week of 2 to 8 November was not yet held (its newest week was 26 October to 1 November, up 0.15), so the rule is the same and the data had moved. `tests/test_session5075.py` holds the dry run: the folder outside the repository, no status row, nothing else moved, and (with `ERW_LIVE_TESTS=1` and the anon key) the whole week on the live set with every field the last published week carries.

What waits for a person, by ruling, and stays so: a deeper finding is published only after Samuel approves it at `/internal/findings`, having run its Stata first, and nothing is posted to LinkedIn (the owner's rulings of 12 October 2026, night). A reader's own request ("Ask for an analysis", "Or choose a finding and its inputs") is run by the data machine's worker, with no person. No step of the page is made by hand. Whether this is the final form is the owner's word.

## Replication (session 3701)

Roadmap item 2 asks for a replication a reader can run. `replication/analysis/` is Research's, in the form of the three decision tools' packages (`replication/battery/`, `generator/`, `datacenter/`). It reads only what `/research` offers for download and this folder's own files:

- the finding cards' CSVs (`site/public/findings/<file>.csv`, served at `/findings/<file>.csv`);
- the week's chart file (`docs/analysis/<week>/chart_of_the_week.json`, served at `/analysis-files/<week>/`);
- `assumptions.json`: every assumption the figures rest on, its default, its source and how to change it (the section below);
- `page_figures.json` (and `.csv`): the figures the page prints, each with its check key, the text shown, its decimals and the tolerance, half of the last shown digit.

It prints each figure beside the page's with the difference.

| File | What it does |
|---|---|
| `replicate.py` | Standard library and pandas only (the regressions' algebra is written out: Gauss-Jordan on the cross-product matrices, robust HC1 errors, Newey-West errors). `python replication/analysis/replicate.py [CSV folder or URL] [chart folder or URL]`; the defaults are the repository's copies, else the site's. Exit 0 when every computed figure is inside its tolerance or a known difference, 1 when one is not, 2 when an input cannot be read |
| `replicate.do` | The same card figures in Stata, in the owner's rules: no line continuation, one empty line between commands outside a loop and none inside, every numeric column destringed with force. Run from its folder. Not yet run: no Stata on the machine that wrote it |
| `figures_of_the_page.py` | Writes `page_figures.json` and `.csv` from the cards' own files (`site/data/findings/<card>.json`, which `site/scripts/check-values.mjs` holds the page to) and the newest Roundup's chart; `--check` says whether the files are current. It refuses when a callout's text is not the card figure it names |
| `assumptions.json`, `assumptions.csv` | The assumptions (below); the CSV holds the numeric ones, with a short Stata name each |

**What it found on 6 November 2026** (`page_figures.json` written for that day, nine cards as computed on 31 October and the three siting cards on 5 November, the Roundup of 2026-W44):

- 78 figures; 66 computed, **65 inside the tolerance**.
- **1 known difference**: the weekly chart's score, 87.25 percent from the file against 87.5 on the page. The chart file holds 104 weeks, so 102 earlier changes; the rule ranked the change among 104 (`WINDOW["week"]` in `run.py`). The value, the week before and the change (107.17, 99.93, +7.24 USD per barrel) meet the page exactly.
- **10 "license needed"**: every callout whose words name NYISO or ISO-NE, as the page prints it (`site/lib/license.ts`, `licenseHeldGrids`).
- **2 not in a download**: `siting_gigawatt`'s months to connect, which the All grids tab reads from `interconnection_durations`.
- **Not replicated**: today's chart (the Digest's chart of the day, drawn from the scanner's rows; no download of `/research` holds them) and the five "also moved" sentences (their series are not in the week's file).
- **The test:** `tests/test_session3701.py` builds the figures afresh from the cards and holds every computed one to its tolerance, so a card the data machine recomputes is held to its new figures. It also checks that a held figure is printed "license needed", that the assumptions drive the figures (the hourly card's ceiling at 95 percent gives fewer hours), the imports (standard library and pandas), and the do-file's rules.

The earlier per-card files stay as they were: each card's `.py` and `.do` beside its CSV, and `site/public/findings/erw_2026_research_replication.py` (session 381, numpy), which reruns every figure of the ten cards' `numbers` against their files. The package above differs in two ways: it holds what the page prints, with the page's rounding, and the weekly chart is in it.

## Cross-checks

Roadmap item 2's cross-check table, in the three decision tools' form: our figure, the published figure, where it was read, the gap, the reason. The table of Research's cards against figures others publish is `docs/methods/crosschecks/automated_analysis.md` (chain 208, sessions 3708 to 3710).

- **Kept as they are:** the four rows of `automated_analysis_findings.md`, "Cross-checks" (session 381). Two set a card against the owner's thesis, one against CDC's FastStats (quoted on the queue card), one against an earlier edition of Berkeley Lab's queue data.
- **Not compared, the weekly chart:** its measures are the warehouse's own tables of a publisher's series (the WTI spot price at Cushing is EIA's daily series, weekly mean by the rule's week). A sum or mean of them reproduces the publisher's figure; it does not check it. The replication above holds the chart to its file.

## Decisions: every assumption, its default, its source, how to change it (session 3702)

Roadmap item 2's decisions block for Research. The table is `replication/analysis/assumptions.json`, word for word (`tests/test_session3702.py` holds the two to each other). Every figure on the page is at these values. A card's inputs are changed by a person in the page's request flow, and the data machine runs the card again; a constant of the rule or of a card's module is changed in its file, and the next run uses it.

| Assumption | Default | Source | How to change it |
|---|---|---|---|
| `batteries_lunch_grids_first_year` | 2019 (year) | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (the only choice offered is 2019) |
| `batteries_curtailment_curtailed` | solar_and_wind | site/data/findings/catalogue.json, the card's default input (curtailed_mwh is solar and wind) | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (solar_only) |
| `batteries_curtailment_first_month` | 2025-08 (month) | site/data/findings/catalogue.json, the card's default input (the first month CAISO's battery charging is held daily) | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (2026-01) |
| `batteries_curtailment_hourly_first_year` | 2019 (year) | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (2021, 2023) |
| `batteries_curtailment_hourly_ceiling_pct` | 90 (percent of the trailing 30-day maximum charging) | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (95); here, the value in this file and in assumptions.csv |
| `batteries_curtailment_hourly_curtailed_on_mw` | 1.0 (MW) | warehouse/analysis/findings/batteries_curtailment_hourly.py, CURTAILED_ON: curtailment counts as on in an hour from 1 MW | the constant in the card's module; here, this file and assumptions.csv |
| `batteries_curtailment_hourly_trail_days` | 30 (Pacific days) | warehouse/analysis/findings/batteries_curtailment_hourly.py, TRAIL_DAYS: the observed ceiling is the largest charging hour of the 30 days before the hour's day (the CSV's trail_max_charging_mw holds it) | the constant in the card's module; the CSV is then written again |
| `gas_sets_price_heat_rate` | 7.0 (MMBtu per MWh) | site/data/findings/catalogue.json, the card's default input (the share below Henry Hub times 6.5 and 8.0 is shown beside it) | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (6.5, 8.0) |
| `gas_sets_price_first_year` | 2019 (year) | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (2020, 2021) |
| `impact_study_series` | ercot_north_rt | site/data/findings/catalogue.json, the card's default input (ERCOT North Hub, real time) | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again |
| `impact_study_control` | nyiso_nyc_rt | site/data/findings/catalogue.json, the card's default input (NYISO New York City, real time; held under NYISO's terms since 21 October 2026, so the control's figures print "license needed") | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again |
| `impact_study_event` | uri_2021 | site/data/findings/catalogue.json, the card's default input (Winter Storm Uri, from 2021-02-07) | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again |
| `impact_study_window` | 14 (days before and from the event) | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (7, 28, 56) |
| `negative_prices_west_first_year` | 2019 (year) | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (2020, 2021) |
| `negative_prices_west_threshold` | 0 (USD per MWh: an hour counts below it) | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (-10, -20) |
| `peak_hour_grids_first_year` | 2019 (year) | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (the only choice offered is 2019) |
| `peak_hour_grids_min_hours` | 20 (hours a day must hold) | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (24) |
| `queue_divorce_first_year` | 2000 (request year) | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (2005, 2010) |
| `queue_divorce_last_year` | 2020 (request year) | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (2015, 2018) |
| `who_rescues_whom_event` | uri_2021 | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (elliott_2022, ercot_heat_2023, caiso_heat_2020) |
| `who_rescues_whom_min_mwh` | 1000 (MWh a day: a smaller flow on both sides is "small", not a flip) | site/data/findings/catalogue.json, the card's default input | a person picks another choice in /research's request flow ("Or choose a finding and its inputs"); the data machine runs the card again (0, 5000) |
| `siting_battery_swing_min_days` | 302 (days: a node holding fewer is left out) | site/scripts/siting-card.mjs: 90 percent of the 335 days node_basis_daily holds, rounded up | the card's script, site/scripts/siting-card.mjs, then the card is written again |
| `siting_flexible_mw` | 1000 (MW) | site/scripts/siting-card.mjs, MW | the card's script |
| `siting_flexible_strike` | 1000 (USD per MWh: the flexible load is off at or above it, and at the four summer peaks) | site/scripts/siting-card.mjs and the All grids tab's flexible profile (site/lib/siting.ts) | the card's script |
| `siting_flexible_hub_row` | ercot:HB_HUBAVG | site/scripts/siting-card.mjs: the row whose two all-in figures the third callout prints | the card's script |
| `siting_gigawatt_mw` | 1000 (MW) | site/scripts/siting-card.mjs, MW | the card's script |
| `siting_gigawatt_load_factor` | 0.9 (share of the size drawn in every hour) | the All grids tab's datacenter profile (site/lib/siting.ts): 0.90 in every hour, never curtails | the profile in site/lib/siting.ts |
| `siting_gigawatt_hours` | 8760 (hours a year) | the card's year_mwh, 7,884,000 MWh = 1,000 MW x 0.90 x 8,760 hours | a year of other length here |
| `rule_window_weekly` | 104 (earlier weekly changes a change is ranked among) | warehouse/analysis/run.py, WINDOW["week"] (session 119) | the constant in run.py; the next Sunday's run uses it |
| `rule_window_monthly` | 36 (earlier monthly changes) | warehouse/analysis/run.py, WINDOW["month"] (session 119) | the constant in run.py |
| `rule_min_earlier` | 8 (earlier changes at least) | docs/methods/automated_analysis.md, the rule's step 3 | warehouse/analysis/run.py |
| `rule_max_age_days` | 100 (days: a period new this week must have ended within them) | warehouse/analysis/run.py, MAX_AGE_NEW (EIA's monthly lag) | the constant in run.py |
| `errors_hc1` | n / (n - k) | the cards' regressions with robust errors, Stata's regress, vce(robust) | the card's module |
| `errors_newey_west_lags` | floor(4 (n / 100) ^ (2 / 9)) | warehouse/analysis/findings/impact_study.py, newey_lags; Bartlett weights, the factor n / (n - k) | the card's module |
| `held_grids` | isone, miso, nyiso | site/data/license_status.json, read by site/lib/license.ts licenseHeldGrids on 6 November 2026: a callout whose words name one prints "license needed" | a publisher's permission recorded in site/data/license_status.json |

The rule's own choices, each made by the session named and kept since (the sections above give the reasons):

1. Only a measurement of the energy system competes for the chart of the week; a count of what the ERW has collected is shown and never chosen. (session 119)
2. The statistic is a change from the period compared with, never a level: the week before, or the same month a year earlier for a monthly figure with a season. (session 119)
3. A change is ranked among the same measure's last 104 weekly or 36 monthly changes, with at least 8; the score is the share that were smaller. (session 119)
4. The headline period must be new this week and have ended within 100 days. (session 119)
5. Ties go to the higher robust z of the change, then to the order of the list. (session 119)
6. The caption is two sentences written by code from the table's numbers; the model's note is held to the literal-number check and names no statistic. (session 119)
7. A chart that holds its headline rings it and labels it; a chart that does not shows no mark. (session 533)
8. An internal template never leaves the warehouse's machines. (session 23)
9. A callout whose words name a grid held under its publisher's terms prints "license needed"; the card stays. (session 315; ruling 6a of the Research pack)

## Sign-off

Session 5004 (chain 233, 13 November 2026) added this block, which the note lacked; the three economics notes and the Grid tool's have one. Signing this note accepts, as the tool's rules:
- the templates and the engine as described above;
- the rule since session 119 for the week's most notable real change;
- the decisions of the section "Decisions", at their defaults;
- the final form as the section "Final form" lists it, with the findings published only after your approval.

It leaves open what `automated_analysis_findings.md` leaves open in its own sign-off block. `automated_analysis_scanner.md` (the daily scanner) has no sign-off block; this signature covers it as the section "Final form" names it.

- Signed off by:
- Date:
- Items left open, ruled, and how:
