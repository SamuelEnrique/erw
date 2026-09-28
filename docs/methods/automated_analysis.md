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

## Schedule

`.github/workflows/roundup.yml`, Sundays at 23:00 UTC:
1. restore the tables;
2. run `run.py`;
3. write the Roundup;
4. commit and push;
5. send the email, whose image links the pushed PNG.

On the runner, templates whose inputs are not restored skip with their reason. The ERCOT yearly history tables are not on the runner, so there `peak_premium_block` and `negative_price_hours` use the live tables only.
