# Page files of the ERW forecast (contract)

Written by session 10600 (chain 730, lab-desktop's second window, part A) on 26 November 2026, before any of these files is built, so that window E (chain 720) can build the page `/forecast` ("ERW forecast") against it tonight. A shape that later has to change is changed here first, with a dated line at the foot saying what moved, and one line in `docs/state/landing_request_portable.md` for window E.

The word "forecast" in paths and tables belongs to the Economic impact tool (`/impact`). This build's name in every path, table and file is `predict`. The page is `/forecast` and calls the figures "ERW forecast": a model's output, tier `derived` (`docs/datastandard.md`, "Provenance tiers"), never a published or official figure.

Builder: `warehouse/predict/run.py` (daily: tomorrow's forecast, never overwriting one already written) and `warehouse/predict/backtest.py` (the walk-forward backtest and the scores). Method notes: `docs/methods/predict.md` (demand) and `docs/methods/predict_price.md` (price). Every file is written whole by its builder, from warehouse tables only; no builder makes a request to any publisher.

## 0. Rules that hold in every file

- **Times.** Every `ts_utc` is the START of an hour, in UTC, written `YYYY-MM-DDTHH:00:00Z`. A place's day (`target_day`, `local_day`) is the calendar day in the place's own clock (`time`, an IANA zone such as `America/Chicago`), so a day holds 23, 24 or 25 hours at the clock changes. `local_hour` is the hour of that day in the place's clock, 0 to 23 (the repeated hour of the autumn change is written twice, with its two `ts_utc`).
- **When written.** `built`: the moment the file was written (UTC, to the second). `made_utc`: the hour the forecast was made. Every input a forecast used was published before `made_utc` (the rule and each input's publication hour: `docs/methods/predict.md`, "What was known when"). `inputs_through_utc`: the last hour of the place's own demand the forecast read.
- **Units.** Demand in `MW` (the hour's mean, as EIA-930 prints it). Price in `USD/MWh`. Errors in the series' own unit; percent errors in percent (`3.4` means 3.4 %).
- **Held or missing.** A value that cannot be shown is never left out and never zero: the field is present, its value is `null`, and a `held` field beside it (or the series' own `held`) says why in plain words. The reasons used: `license needed` (the input is not public-licensed, `docs/licenses.md`); `paused` (the publisher is paused, `warehouse/metadata/paused_sources.csv`); `too short` (fewer whole days of history than the method needs); `not published` (the operator prints no forecast of its own for this series); `no data` (the hour is missing in the source). A held series holds no number anywhere: its `tomorrow`, `history` and score cells are `null`.
- **Tier and label.** Every file carries `"tier": "derived"` and `"label": "ERW forecast"`. No file holds advice, a view, or a word on what a reader should do.
- **Weather.** The headline forecast uses only weather forecasts issued before `made_utc`. A line made with the weather as it turned out, if one is ever written, is a separate method named `with_weather_known` and is never `erw`.

## 1. `site/data/predict/index.json`: the places and what is forecast for each

| Key | Type | Unit | What |
|---|---|---|---|
| `contract` | string | | `docs/state/page_files_predict.md` |
| `built` | string (UTC time) | | when written |
| `tier`, `label` | string | | `derived`, `ERW forecast` |
| `method_notes` | object | | `{"demand": "docs/methods/predict.md", "price": "docs/methods/predict_price.md"}` |
| `made_rule` | string | | the hour the forecast is made each day, in words (one sentence) |
| `band_rule` | string | | what the band is, in words (one sentence) |
| `choice_rule` | string | | how a place's method is chosen, in words (one sentence) |
| `places[]` | array | | one entry a place, regions first then balancing authorities, each in EIA-930's code order |
| `places[].place` | string | | the place id: `region-<code>` or `ba-<code>`, the code being EIA-930's in lower case, as in `site/data/regions/forecast/` (`region-cal`, `ba-erco`) |
| `places[].name` | string | | the place's name as EIA prints it (`California`, `Electric Reliability Council of Texas, Inc.`) |
| `places[].kind` | string | | `region` or `ba` |
| `places[].eia930` | string | | EIA-930's code (`CAL`, `ERCO`) |
| `places[].time` | string | | the place's clock, an IANA zone |
| `places[].file` | string | | the place's file, relative to `site/data/predict/` (`region-cal.json`) |
| `places[].series` | object | | keyed `demand` and `price` |
| `places[].series.<s>.status` | string | | `shown`, `license needed`, `paused`, `too short`, `not built` |
| `places[].series.<s>.held` | string or null | | the reason when not `shown`, else `null` |
| `places[].series.<s>.method` | string or null | | the method the page shows as the ERW forecast (`yesterday`, `week_ago`, `regression`, `flexible`), `null` when held |
| `places[].series.<s>.fit_day` | string (date) or null | | the day the method was last fit (UTC date) |
| `places[].series.<s>.target_day` | string (date) or null | | the place's day the latest forecast is for |
| `places[].series.<s>.hub` | string or null | | price only: the hub forecast (`ercot:HB_NORTH`), `null` for demand |
| `places[].series.<s>.market` | string or null | | price only: `day-ahead`; `null` for demand |

Example row:

```json
{"place": "region-tex", "name": "Texas", "kind": "region", "eia930": "TEX", "time": "America/Chicago", "file": "region-tex.json", "series": {"demand": {"status": "shown", "held": null, "method": "regression", "fit_day": "2026-11-26", "target_day": "2026-11-27", "hub": null, "market": null}, "price": {"status": "shown", "held": null, "method": "regression", "fit_day": "2026-11-26", "target_day": "2026-11-27", "hub": "ercot:HB_NORTH", "market": "day-ahead"}}}
```

## 2. `site/data/predict/<place>.json`: one file a place

| Key | Type | Unit | What |
|---|---|---|---|
| `contract`, `built`, `tier`, `label` | | | as in the index |
| `place`, `name`, `kind`, `eia930`, `time` | | | as in the index |
| `tables` | array of strings | | the warehouse tables the file was built from |
| `series` | object | | keyed `demand` and `price`; both keys always present |
| `series.<s>.status`, `.held`, `.method`, `.fit_day`, `.target_day`, `.hub`, `.market` | | | as in the index |
| `series.<s>.unit` | string | | `MW` or `USD/MWh` |
| `series.<s>.method_note` | string | | the method note |
| `series.<s>.made_utc` | string (UTC hour) or null | | the hour the latest forecast was made |
| `series.<s>.inputs_through_utc` | string (UTC hour) or null | | the last hour of the place's own series the forecast read |
| `series.<s>.band` | string | | the band in words: which past errors, which percentiles, over which days |
| `series.<s>.band_coverage_pct` | number or null | percent | the share of past hours whose actual value fell inside the band (part F; `null` until computed) |
| `series.<s>.tomorrow_columns` | array | | `["ts_utc", "local_hour", "erw", "lo", "hi", "operator"]` |
| `series.<s>.tomorrow[]` | array of rows | MW or USD/MWh | one row an hour of `target_day`: the hour, its local hour, the ERW forecast, the band's low and high, and the operator's own forecast for the hour where the warehouse holds it (`null` where not yet published or `not published`) |
| `series.<s>.operator_held` | string or null | | why `operator` is `null` throughout (`not published` for every price; `null` when the operator's forecast is held) |
| `series.<s>.history_columns` | array | | `["ts_utc", "local_day", "local_hour", "made_utc", "kind", "erw", "lo", "hi", "operator", "actual", "yesterday", "week_ago"]` |
| `series.<s>.history[]` | array of rows | MW or USD/MWh | one row an hour of each past day held (the last 35 days of the place's clock): the forecast made for that hour, `kind` being `backtest` (made by the walk-forward backtest, from a model fit only on days before it) or `live` (made on the day by `run.py` and never overwritten), what happened (`actual`), the operator's forecast, and the two simple methods' forecasts for the hour |
| `series.<s>.summary` | object | | `{"last_30_days": {...}, "backtest": {...}}`, each `{"first_day", "last_day", "hours", "mae": {"erw", "operator", "yesterday", "week_ago"}, "mape": {...}}` (the same metrics as the score file, for this place and series) |

Example rows (`series.demand`):

```json
{"tomorrow": [["2026-11-27T06:00:00Z", 0, null, null, null, null]], "history": [["2026-11-25T06:00:00Z", "2026-11-25", 0, "2026-11-24T13:00:00Z", "live", null, null, null, null, null, null, null]]}
```

(The numbers are left `null` here because no forecast exists yet as this is written: the ERW writes no invented figure, even in an example. A real sample from the first build replaces these lines, with a dated line at the foot.)

## 3. `site/data/predict/scores.json`: the report card

Every place, every method, every series: no place and no period is left out because it scored badly.

| Key | Type | Unit | What |
|---|---|---|---|
| `contract`, `built`, `tier`, `label`, `method_notes` | | | as in the index |
| `span` | object | | `{"demand": {"first_day", "last_day"}, "price": {...}}`: the backtest's days |
| `methods` | array | | every method scored: `erw` (the chosen method, place by place), `operator`, `yesterday`, `week_ago`, `regression`, `flexible` (when built), each with a one-line `what` |
| `metrics` | object | | `{"mae": "mean absolute error, in the series' unit", "mape": "mean absolute percent error, in percent"}` |
| `mape_rule` | string | | when a percent error is not defined (a price at or near zero) and what is written then (`null`) |
| `cuts` | object | | `all`, `month` (key `YYYY-MM`), `hour` (key `0` to `23`, the place's clock), `top10` (the place's ten highest-demand days of the backtest), `event` (key: the event id of `/events`), `spike` (price only: the hours above the grid's 99th percentile) |
| `rows_columns` | array | | `["place", "series", "method", "cut", "key", "hours", "mae", "mape", "held"]` |
| `rows[]` | array of rows | | one row a place, series, method, cut and key; `key` is `""` for `all`, `top10` and `spike`; `hours` is the count of hours scored; `mae` and `mape` `null` with `held` filled when the series is held or the method has no forecast for those hours (the operator's price) |

Example row:

```json
["region-tex", "demand", "operator", "hour", "17", null, null, null, null]
```

The score of a method and the score of the operator for one place and cut are always made on the same hours: an hour enters a comparison only when every method in it has a forecast and the actual value is held. The hour count is in each row.

## 4. Where the methods are written

`index.json` names each place's method and the day it was last fit; the method note gives each method in words a reader can run, the rule that chose it, and every method's score. The regression is also a Stata do-file under `replication/predict/`.

## 5. The example files

One small example of each kind, its values `null`, marked `"example": true`, is in `docs/state/page_files_predict_examples/` (`index.json`, `region-tex.json`, `scores.json`). They are kept outside `site/` so that pushing them to main changes no page; the real files land at `site/data/predict/` through the landing desk. A page must read `example` and show nothing as a forecast when it is `true`.

## Changes to this contract

- 2026-11-26, session 10600: written.
- 2026-11-26, session 10600, after the first build (11:15 UTC): fields added, none moved or removed. In each place file's series: `horizon_days` (integer: days between the last whole day read and the target day; 2 for the day-ahead forecast as the method note defines it, 3 or 4 when the warehouse's demand is a day or two behind), `tomorrow_held` (string or null: why `tomorrow` is empty, `null` when it is filled), `method_mae_last_2_years` (object: each ERW method's mean absolute error over the last two years, the numbers the choice was made on). In `scores.json`: the cut `last_2_years` (the 730 days the method is chosen on); the cut `hour` is over those two years. A new file, `site/data/predict/ledger_demand.csv`: every forecast as made on its day, appended and never rewritten (columns `series, place, target_day, ts_utc, local_hour, made_utc, inputs_through_utc, horizon_days, method, erw, lo, hi`; three `#` lines of provenance first, to be skipped by count). Real samples from that build (`region-tex`): `tomorrow` `["2026-11-27T06:00:00Z", 0, 47363.3, 44529.4, 52297.5, null]`; `history` `["2026-11-25T05:00:00Z", "2026-11-24", 23, "2026-11-23T20:00:00Z", "backtest", 47724.6, 44962.8, 52405.8, 53419.0, 53725.0, 47157.0, 47872.0]`; a score row `["region-tex", "demand", "operator", "hour", "17", 726, 1395.2, 2.187, null]`; the index row of TEX shows demand `shown` (method `regression`) and price `not built` (part E).
- 2026-11-26, session 10000 (chain 701, done-line request 577): one field added, none moved. In a place file's demand and price series, `tomorrow_from` (string, present only when the ledger already held the target day): the forecast for tomorrow is then the ledger's making, its `made_utc` and `method` the ledger's, and the words name the method chosen now.
- 2026-11-26, session 10600, part E (11:45 UTC build): the price is built for ten places (TEX, ERCO, CENT, SWPP, CAL, CISO, NE, ISNE, NY, NYIS) and their `series.price` is `shown`, with `hub` filled and two fields added: `horizon_days` (days between the last whole day of prices read and the target day) and `demand_horizon_days` (the same for the demand it reads). In a shown price series `operator` is `null` in every row and `operator_held` reads "not published: ..."; the summary's `operator` cells are `null`. A second ledger, `site/data/predict/ledger_price.csv`, has the demand ledger's columns (prices in USD/MWh). In `scores.json`, `span.price` is filled, the price rows carry the cut `spike`, and each price place has one `operator` row whose numbers are `null` and whose `held` says why. MIDW and MISO stay `paused`, MIDA and PJM `license needed`, the rest `not built`.
- 2026-11-26, session 10600, about 12:00 UTC: a correction of the line above. The price is shown for six places, not ten: TEX, ERCO, CENT, SWPP, CAL, CISO. NE, ISNE, NY and NYIS are `license needed` (ISO-NE's and NYISO's terms ask for written permission, `warehouse/metadata/license_verdicts.csv`); their price series hold no number, as section 0 says of every held series. The modules behind the files were renamed (`warehouse/predict/predict_data.py`, `predict_demand.py`, `predict_price.py`, `predict_score.py`; `run.py` keeps its name); no field moved.
- 2026-11-26, session 10601 (part F): fields and a file added, none moved. Each place file's `series.demand` gains `peak`: `what` (words), `tomorrow` (`{local_hour, ts_utc, erw, lo, hi}`: the hour of the highest ERW forecast of the target day, the forecast and its band there; `null` when tomorrow is held), `last_2_years` and `backtest` (`{days, first_day, last_day, methods: {erw, operator, yesterday, week_ago: {mae (MW), mape (percent), hour_exact_pct, hour_within_1_pct}}}`, over days whose every hour every method holds). `scores.json` gains rows of the series `demand_peak` (cuts `all` and `last_2_years`; in these rows `hours` holds the count of days). A new file `site/data/predict/ahead.json`: `contract`, `built`, `tier`, `label`, `method_notes`, `made_utc`, `what`, `places[]` each `{place, time, last_whole_day, horizons[]}`, a horizon being `{horizon_days (3 to 7), days_after_tomorrow, target_day, shown (true only where the regression beat the same hour a week ago over the last two years), held (the reason when not shown), last_2_years: {hours, mae: {regression, week_ago, yesterday}, mape: {...}, operator_day_ahead_mae_same_hours}, band_coverage_pct, forecast_columns: [ts_utc, local_hour, erw, lo, hi], forecast (rows, or null when not shown)}`.
- 2026-11-26, session 10601 (part F, the separate line "with the weather known"): each place file's `series.demand` gains `with_weather_known` (`null` where the region's temperature is not held; else `{what, region, all, last_2_years}`, each a summary of `with_weather_known`, `regression` and `operator` on the hours all three and the actual hold: `{first_day, last_day, hours, mae, mape}`). `scores.json` gains `separate_lines` (words) and rows of the series `demand_weather_known` (methods `with_weather_known`, `regression`, `operator`; cuts `all` and `last_2_years`). The line reads the target day's own observed weather: it is not a forecast, is never `erw`, never in `tomorrow` or `history`, and a page that shows it must label it "with the weather known" (the chain's rule).
- 2026-11-26, session 10601 (part F, a fourth candidate): the demand methods gain `regression_recent` (the regression with three more recent regressors; `docs/methods/predict.md`, section 14). It is a candidate of the choice rule like the others, so `method` in the index and the place files may now read `regression_recent`; `scores.json`'s `methods` and every demand cut gain its rows; `method_mae_last_2_years` gains its key. The history's columns are unchanged (`erw` is the chosen method's forecast, whichever it is).
- 2026-11-26, session 10601: in `ahead.json` each horizon gains `method` (`regression` or `regression_recent`, the lower error of the two over the last two years, the place files' rule); `last_2_years.mae` and `.mape` gain `regression_recent`; `shown` compares the horizon's `method` with the week-ago hour; `forecast` is that method's.
