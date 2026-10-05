# Automated Analysis: method

Platform tool 26, built in session 23. A library of chart templates runs on the Energy Research Warehouse (ERW) every week. A fixed rule, not a model, scores each result against its own history and picks the chart of the week, which the Energy Roundup and its email carry. The code is in `warehouse/analysis/`; its output is in `docs/analysis/` and on the site's `/analysis`.

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

**The caption states the finding, and code writes it.** Two sentences from the table's own numbers: what the measure was, in which period, how far it moved from the period it is compared with, and how that move ranks among the earlier ones. For the week of 4 October the trial gives: "WTI spot price at Cushing, weekly mean: 93.57 USD/bbl in the week of 2026-09-21 to 2026-09-27, down 9.97 from 103.54 the week before. Of the 104 week-to-week moves before it, 7 were as large." The model still drafts the two-sentence note, from the template's sentences and the finding, under the literal-number check; it is told to name no statistic. The model's own caption is kept beside the finding in `chart_of_the_week.json` (`model_caption`) and is not published.

`chart_of_the_week.json` also lists `also_moved`: the next five by the same rule, each with its finding.

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
