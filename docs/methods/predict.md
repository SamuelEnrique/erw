# The ERW forecast of hourly demand (`site/data/predict/`, the page `/forecast`)

Session 10600, chain 730 (lab-desktop's second window), 26 November 2026. Code: `warehouse/predict/` (`predict_data.py` reads the tables, `predict_demand.py` holds the methods and the backtest, `predict_score.py` the report card, `run.py` the daily run and the page files; the first three were named without the prefix until their names were found to collide with other tools' modules in the test suite). Contract of the files: `docs/state/page_files_predict.md`. The ground this rests on: `docs/reviews/predict-ground-2026-11-26.md`. Tests: `tests/test_predict.py`. Replication in Stata: `replication/predict/`.

**What it is.** The ERW's own forecast of each place's demand for its next day, hour by hour, with a band, and its report card against what happened and against the operator's own day-ahead forecast for the same hours. Tier `derived` (`docs/datastandard.md`, "Provenance tiers"): a model's output, computed by ERW code from public EIA-930 data. Every file and the page call it "ERW forecast"; it is never a published or official figure, and it carries no advice.

## 1. The places

EIA's thirteen regions of the lower 48 and the sixteen balancing authorities whose mean demand over the last 365 days held is at least 5,000 MW: BPAT, CISO, CPLE, DUK, ERCO, FPC, FPL, ISNE, MISO, NYIS, PACE, PJM, PSCO, SOCO, SWPP, TVA. Six of these are each a whole region and appear under both names, as on `/demand` (ERCO is TEX, ISNE is NE, NYIS is NY, PJM is MIDA, SOCO is SE, TVA is TEN); their figures are the same.

The demand forecast is the demand the demand pages show: a balancing authority's `demand_mw` of `eia930_ba_demand_hourly`; a region's sum of its demand-filing authorities, written for an hour only when each active one holds it (`warehouse/derived/region_files.py`, `region_demand`, imported unchanged). Each place's day is the calendar day in its own clock (`region_files.REGION_TZ`, EIA's zone of the authority, Central for MISO), so a day holds 23, 24 or 25 hours.

## 2. What was known when

The forecast for a place's day T is taken as made at **20:00 UTC on day T-1**. At that hour the warehouse holds the place's demand through 23:00 local on day **T-2**: EIA's six-month files are updated daily (last modified 15:42 UTC on 25 November, holding each authority's hours through the end of its 24 November), and the warehouse's copy lands with the data machine's EIA-930 step (retrieved 18:31 UTC that day). So the forecast reads the place's demand **through day A = T-2**, and nothing later; the forecast's hours are 28 to 52 hours after its last hour read (the Pacific and Eastern clocks differ). No weather is read: the warehouse holds no dated weather forecast (the ground, section 2), and a forecast that used the weather as it turned out would not be a forecast.

The operator files its day-ahead forecast with EIA the day before, from its own demand of that morning and its own weather forecast. The ERW's forecast reads older demand and no weather. The comparison below is made on those terms.

The daily run (`run.py`) makes the forecast for each place's next local day after the hour it runs, from what the warehouse then holds: when the last whole day held is three or four days before the target day (tonight's first run, made at 11:00 UTC on 26 November, read demand through 24 November, and through 23 November for MISO, MIDW and NW, whose last day held lacks its last hour), the same method is fitted at that horizon (`h`, written in each file as `horizon_days`).

## 3. The methods, simplest first

Each method gives, for every hour of day T, a forecast in MW, from the place's demand through day A = T - h (h = 2 for the day-ahead forecast).

- **(a) yesterday:** the demand of the same local hour on day A, the latest whole day held. For the day-ahead forecast that is two days before the target day, because day T-1 is not yet held when the forecast is made. The page's word "yesterday" means this.
- **(b) week_ago:** the demand of the same local hour on day T-7.
- **(c) regression:** for each local hour k (0 to 23), an ordinary least-squares regression of the log of the hour's demand on: a constant; the log of the same hour on day A; the log of day A's mean demand; the log of the same hour on day T-7; the log of the mean demand of the seven days ending on day A (at least five of them held); six dummies for T's day of the week (Sunday the base) and six for A's; dummies for a US federal holiday (or its observed day) on T, on A and on T-7, and for a "bridge" day (the day after Thanksgiving, 24 December, 26 to 31 December) on T, on A and on T-7; and two yearly waves of T's day of the year (the sine and cosine of 2 pi times the day over 365.25, and of 4 pi times it). 27 coefficients an hour. The regression is **refit for every target day T**, on the 730 days before it whose demand was held when T's forecast was made (target days up to A; an expanding window from the first day held until 730 are held; no fit with fewer than 300). The forecast is the exponential of the fitted value. A single missing hour inside a day (the 23-hour day of the spring clock change, or a lone gap) is taken as the mean of its two neighbours for the regressors only, never for a target or a score; an hour at or below zero (a filing fault EIA prints now and then) is taken as not held, so a day holding one has no mean and an hour of it is neither a regressor nor a target; the repeated autumn hour enters day A's figures as the mean of its two hours, and both of the target day's repeated hours get the hour's forecast. The coefficients are solved from the window's normal equations (`numpy.linalg.lstsq`), in a fixed order: the same tables give the same forecast to the last digit on the same machine (`tests/test_predict.py`).
- **(d) a more flexible method:** not built tonight. It would be shown only if it beat (c) out of sample by at least 5 percent of (c)'s mean absolute error over the last two years, in most places, fit with a fixed seed. Without a dated weather forecast the inputs that would let a flexible method do better than (c) are missing; part F of chain 730 returns to it.

## 4. The backtest

Walking forward one day at a time from **1 July 2019** (a year after the first demand held) to **24 November 2026**, every day's forecast made by each method from a model fit only on days held before it, exactly as in section 2. Every hour of every day is kept; none is dropped because it scored badly.

## 5. The choice, by rule

For each place, the ERW's method (a, b or c) with the **lowest mean absolute error over the last two years of the backtest** (25 November 2024 to 24 November 2026), on the hours where every method and the operator's forecast are held, is the one the page shows as "ERW forecast" (`erw` in the files). On 26 November 2026 the regression is chosen in all 29 places. Because the choice is made on the same two years that are scored, the ERW's row in those two years is the best of three methods there; each method's own row is beside it, unchosen.

## 6. The band

Around each forecast, the band runs from the forecast times the exponential of the 10th percentile to the forecast times the exponential of the 90th percentile of **the chosen method's own out-of-sample errors** (the log of actual over forecast) **at the same local hour**, over the 365 days of target days held when the forecast is made (no band from fewer than 60). It says how far this method has missed at this hour in the last year, and nothing more: it is not a probability from a model of the weather. Each place's file prints the share of the last two years' hours whose demand fell inside the band (`band_coverage_pct`; 80.5 percent for TEX, 78.6 for CISO).

## 7. The scores

`site/data/predict/scores.json` holds, for every place and every method (`erw`, `operator`, `yesterday`, `week_ago`, `regression`), the mean absolute error (MW) and the mean absolute percent error (percent of the hour's demand): over the whole backtest (`all`), over the last two years (`last_2_years`), by month, by local hour (over the last two years), over the place's ten highest-demand days of the backtest (`top10`, by the day's peak hour), and over the days of each of the nine events of `/events` that fall in the backtest (`event`, every place scored on every event's days). An hour enters a place's comparison only when the actual demand and every method's forecast, the operator's included, are held: all five methods of a place are scored on the same hours, and each row gives the count. The operator's forecast is `x_forecast_mw` of `eia930_forecast_error_hourly`, the hours that table screens out as filing errors left out (`docs/methods/forecast_error.md`).

**The last two years, place by place, the ERW's losses to the operator first** (built 26 November 2026 at 11:15 UTC; `runs/c730/table.py` prints this table from `scores.json`):

| Place | Hours (2 years) | ERW MAPE % | Operator MAPE % | Yesterday's hour MAPE % | Week-ago hour MAPE % | ERW MAE MW | Operator MAE MW | ERW MAPE %, whole backtest | Operator MAPE %, whole backtest | Who wins (2 years) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| ba-cple | 16,935 | 9.94 | 4.03 | 12.65 | 15.81 | 741 | 294 | 9.47 | 4.08 | operator |
| region-car | 15,758 | 7.88 | 2.27 | 10.12 | 13.02 | 2,162 | 612 | 7.38 | 2.38 | operator |
| region-se | 17,514 | 6.81 | 1.27 | 9.12 | 11.15 | 1,948 | 360 | 6.52 | 2.01 | operator |
| ba-soco | 17,514 | 6.81 | 1.27 | 9.12 | 11.15 | 1,948 | 360 | 6.50 | 2.32 | operator |
| region-ne | 17,516 | 7.99 | 2.80 | 10.88 | 11.39 | 1,057 | 340 | 7.24 | 2.56 | operator |
| ba-isne | 17,516 | 7.99 | 2.80 | 10.88 | 11.39 | 1,057 | 340 | 7.24 | 2.56 | operator |
| region-ten | 17,516 | 7.31 | 2.34 | 9.56 | 12.46 | 1,494 | 473 | 7.16 | 2.26 | operator |
| ba-tva | 17,516 | 7.31 | 2.34 | 9.56 | 12.46 | 1,494 | 473 | 7.16 | 2.26 | operator |
| ba-duk | 17,392 | 7.99 | 3.04 | 10.74 | 12.87 | 1,052 | 407 | 7.38 | 2.84 | operator |
| region-ny | 17,337 | 6.12 | 2.73 | 8.69 | 9.08 | 1,072 | 479 | 5.46 | 2.63 | operator |
| ba-nyis | 17,337 | 6.12 | 2.73 | 8.69 | 9.08 | 1,072 | 479 | 5.46 | 2.63 | operator |
| region-tex | 17,420 | 5.22 | 2.08 | 6.33 | 8.13 | 3,013 | 1,178 | 5.86 | 2.39 | operator |
| ba-erco | 17,420 | 5.22 | 2.08 | 6.33 | 8.13 | 3,013 | 1,178 | 5.86 | 2.39 | operator |
| ba-fpl | 17,464 | 5.86 | 3.16 | 7.24 | 9.74 | 994 | 536 | 6.22 | 3.57 | operator |
| region-midw | 17,492 | 4.16 | 1.98 | 6.73 | 7.78 | 3,603 | 1,659 | 4.14 | 2.42 | operator |
| ba-bpat | 17,516 | 3.62 | 1.88 | 5.45 | 5.77 | 265 | 134 | 3.92 | 1.98 | operator |
| region-mida | 17,393 | 5.19 | 3.48 | 7.65 | 8.66 | 5,299 | 3,376 | 5.16 | 3.61 | operator |
| ba-pjm | 17,393 | 5.19 | 3.48 | 7.65 | 8.66 | 5,299 | 3,376 | 5.16 | 3.61 | operator |
| ba-miso | 17,492 | 3.94 | 2.42 | 6.55 | 7.35 | 3,125 | 1,856 | 3.94 | 2.77 | operator |
| region-sw | 17,382 | 5.09 | 4.51 | 6.41 | 8.24 | 740 | 605 | 4.74 | 3.50 | operator |
| region-fla | 15,835 | 6.00 | 5.50 | 7.58 | 10.30 | 1,858 | 1,730 | 6.10 | 5.57 | operator |
| ba-pace | 17,420 | 4.02 | 4.97 | 5.70 | 6.05 | 253 | 303 | 4.03 | 5.19 | ERW |
| region-nw | 14,880 | 2.74 | 5.10 | 4.50 | 4.75 | 1,215 | 2,221 | 2.86 | 4.01 | ERW |
| region-cent | 15,038 | 5.12 | 8.04 | 6.55 | 8.58 | 1,857 | 2,806 | 4.93 | 4.63 | ERW |
| ba-swpp | 16,965 | 5.08 | 8.25 | 6.40 | 8.47 | 1,824 | 2,844 | 4.93 | 4.79 | ERW |
| region-cal | 16,970 | 4.20 | 7.61 | 7.32 | 7.04 | 1,409 | 2,455 | 4.09 | 4.68 | ERW |
| ba-ciso | 17,420 | 4.27 | 8.50 | 7.48 | 6.82 | 1,168 | 2,274 | 4.16 | 5.09 | ERW |
| ba-psco | 17,510 | 6.67 | 13.64 | 8.77 | 9.04 | 362 | 749 | 6.61 | 6.44 | ERW |
| ba-fpc | 17,369 | 7.78 | 23.77 | 9.50 | 12.80 | 525 | 1,610 | 7.79 | 22.85 | ERW |

What the table says, plainly:

- **The operator wins in 21 of the 29 places**, often by a wide margin (the Southeast, New England, Tennessee, the Carolinas, Texas: the operator's error is a third or less of the ERW's). The operator has its own weather forecast and a later look at its demand; the ERW has neither.
- **The ERW wins in 8.** In six of them (CISO and CAL, CENT and SWPP, PSCO, NW) the operator's own error in the last two years is well above its error over the whole backtest (CISO 8.50 percent against 5.09; PSCO 13.64 against 6.44): the operator's filed forecast changed against the demand EIA prints, which can be a change in what it forecasts (for example a different treatment of rooftop solar or of a member's load) as much as a change in skill. FPC's filed forecast misses by more than 20 percent over the whole backtest. Where the ERW "wins" against such a filing, the win says that the ERW's forecast follows EIA's demand series more closely, not that it forecasts the weather better.
- **Both simple methods lose to the regression in every place,** and the regression is chosen everywhere.

## 8. The files and the tables

- `site/data/predict/index.json`, `<place>.json`, `scores.json`: the contract's files, written whole by `run.py`.
- `site/data/predict/ledger_demand.csv`: every forecast as made on its day, appended and never rewritten (`tests/test_predict.py`). Its first rows were made at 11:00 UTC on 26 November 2026, for 27 November. The track record from that day on is the real one; the history before it is the backtest's and is marked `backtest`.
- The tables asked of window A (`docs/state/data_requests_predict.md`): the backtest of the regression, the scores, and the ledger as a table, each with tier `derived`, and `run.py` as a step of the daily run after the EIA-930 refresh.

## 9. Replication

`python warehouse/predict/run.py` with `ERW_DATA_ROOT` naming a folder whose `warehouse/output` holds `eia930_ba_demand_hourly` and `eia930_forecast_error_hourly` rebuilds every file; `--now` sets the hour the forecast is taken as made. The regression for one place and one day is also a Stata do-file, `replication/predict/predict_demand.do`, with its README.

## 10. Part F (session 10601)

- **The replication, and a rule written down.** `replication/predict/replicate.py`, written from this note and not from the builder, recomputes every demand figure of `scores.json` from the public tables and the stored regression forecasts (17,995 of 17,995 equal), and refits the regression itself on four sample days and two hours of every place with ordinary least squares on the window's own rows (232 of 232 equal to the stored forecast's one decimal). Its first run disagreed on 22 sample hours, by up to 0.4 percent (NYIS on 20 November 2026 at 03:00: 13,396.9 MW stored, 13,445.3 MW refitted), in exactly the places whose demand holds hours at or below zero (NY 12 hours, TEN 360, FPL 48, CPLE, PSCO, FPC). The builder takes such an hour as not held when it takes a day's mean; this note did not say so, and the replication had counted it. The rule is now written in section 3, and the replication follows it. On the way, the builder's solver was changed from differences of running normal equations to a solve of each window's own rows (`numpy.linalg.lstsq`); it changed no score at the shown precision and is kept as the plainer method.
- **The flexible method (d), tried and not built.** A gradient-boosted model (scikit-learn's `HistGradientBoostingRegressor`, `random_state` 0, no early stopping, 300 rounds at a rate of 0.05) on the regression's own regressors and the local hour, refit at the start of each month on the 730 days held then, over the last two years (`runs/c730/trial_flexible.py`): its mean absolute error was 16.0 percent worse than the regression's in TEX (3,494 against 3,012 MW), 11.3 percent worse in CISO and 9.3 percent worse in SE. The note's rule asks a 5 percent gain: (d) is not shown.
- **Net demand** (demand less wind and solar) is not forecast: the wind and solar forecasts held carry no publication time (CAISO) or begin on 30 September 2026 (ERCOT), so a net demand forecast could not be shown to use only what was published before its hour (`docs/methods/predict_price.md`, section 2; data request 5).
- **The band, honestly.** Each file prints `band_coverage_pct`, the share of the last two years' hours whose demand fell inside the band; the band aims at 80 percent.
- **The cross-check** against an operator's own published forecast error: CAISO's market monitor's 2024 annual report prints none (`docs/state/progress_c730.md`).

## 11. The peak (session 10601)

For each place and day, the peak is the highest hourly demand and its local hour; a method's peak is the highest of its own hourly forecasts for the day, and the hour of it, scored on the days whose every hour every method holds. Each place file carries tomorrow's peak (`series.demand.peak.tomorrow`: the hour, the ERW forecast and its band there) and the record; `scores.json` has the `demand_peak` rows. The last two years (built 26 November 2026 at 12:27 UTC; `runs/c730/table_f.py` prints the table from the files):

| Place | Days | ERW peak MAPE % | Operator peak MAPE % | Yesterday's peak MAPE % | ERW peak hour exact % | Operator peak hour exact % | ERW within 1 hour % | Operator within 1 hour % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| region-cal | 702 | 4.96 | 2.37 | 7.34 | 45.7 | 29.5 | 71.5 | 72.4 |
| region-car | 649 | 9.15 | 2.40 | 11.25 | 40.2 | 63.8 | 69.5 | 91.4 |
| region-cent | 319 | 6.02 | 6.61 | 7.49 | 41.4 | 59.6 | 68.0 | 83.1 |
| region-fla | 651 | 6.50 | 5.80 | 7.70 | 43.3 | 47.6 | 74.7 | 89.2 |
| region-mida | 719 | 5.83 | 1.85 | 8.04 | 47.8 | 11.8 | 70.0 | 77.5 |
| region-midw | 725 | 4.58 | 1.98 | 6.71 | 45.8 | 69.1 | 73.9 | 91.3 |
| region-ne | 726 | 6.12 | 1.17 | 8.09 | 63.2 | 79.6 | 93.7 | 98.1 |
| region-nw | 608 | 3.14 | 4.93 | 4.76 | 56.6 | 54.1 | 78.6 | 82.1 |
| region-ny | 715 | 5.55 | 2.61 | 7.54 | 53.4 | 76.8 | 88.5 | 96.9 |
| region-se | 724 | 8.11 | 1.18 | 10.04 | 39.5 | 92.0 | 71.0 | 98.9 |
| region-sw | 697 | 5.75 | 3.48 | 6.70 | 53.7 | 47.2 | 85.4 | 89.4 |
| region-ten | 726 | 8.50 | 2.58 | 10.22 | 34.2 | 57.9 | 65.8 | 88.4 |
| region-tex | 722 | 6.30 | 2.19 | 6.73 | 44.2 | 59.0 | 73.8 | 88.6 |
| ba-bpat | 726 | 4.39 | 1.78 | 6.50 | 48.3 | 65.4 | 80.7 | 89.5 |
| ba-ciso | 722 | 4.82 | 2.55 | 7.33 | 42.7 | 25.6 | 66.2 | 64.0 |
| ba-cple | 699 | 10.66 | 4.10 | 13.10 | 35.8 | 53.2 | 65.5 | 84.8 |
| ba-duk | 719 | 9.68 | 3.27 | 12.04 | 38.7 | 58.1 | 69.4 | 89.2 |
| ba-erco | 722 | 6.30 | 2.19 | 6.73 | 44.2 | 59.0 | 73.8 | 88.6 |
| ba-fpc | 716 | 8.27 | 24.59 | 9.76 | 43.3 | 51.4 | 71.6 | 86.7 |
| ba-fpl | 718 | 6.82 | 2.92 | 7.61 | 37.7 | 35.4 | 71.7 | 79.1 |
| ba-isne | 726 | 6.12 | 1.17 | 8.09 | 63.2 | 79.6 | 93.7 | 98.1 |
| ba-miso | 725 | 4.31 | 2.40 | 6.47 | 45.1 | 64.1 | 74.2 | 89.5 |
| ba-nyis | 715 | 5.55 | 2.61 | 7.54 | 53.4 | 76.8 | 88.5 | 96.9 |
| ba-pace | 721 | 4.40 | 3.79 | 5.57 | 29.4 | 30.2 | 59.2 | 58.3 |
| ba-pjm | 719 | 5.83 | 1.85 | 8.04 | 47.8 | 11.8 | 70.0 | 77.5 |
| ba-psco | 721 | 7.37 | 13.71 | 8.77 | 27.2 | 23.9 | 58.9 | 49.1 |
| ba-soco | 724 | 8.11 | 1.18 | 10.04 | 39.5 | 92.0 | 71.0 | 98.9 |
| ba-swpp | 702 | 6.30 | 8.71 | 7.34 | 44.4 | 57.5 | 69.9 | 80.1 |
| ba-tva | 726 | 8.50 | 2.58 | 10.22 | 34.2 | 57.9 | 65.8 | 88.4 |

The ERW's peak is closer than the operator's in 5 of 29 places (CENT, NW, FPC, PSCO, SWPP); it names the peak hour exactly more often than the operator in 8 (CAL, MIDA, NW, SW, CISO, FPL, PJM, PSCO), most strikingly in MIDA and PJM, where the operator names the hour on 11.8 percent of days and the ERW on 47.8 percent. The CENT row covers 319 days: the operator's region forecast is missing on many SPP days, and a day enters only when every method holds every hour.

## 12. Further ahead (session 10601)

`warehouse/predict/ahead.py` writes `site/data/predict/ahead.json`: the demand forecast for the days two to six after tomorrow. A forecast made at 20:00 UTC on day D reads the demand through day D-1, so its day D+j is j+1 days after the last day read: horizon h = j+1 (h = 2 is the day-ahead forecast of the place files; this file holds h = 3 to 7). Each horizon is the regression of section 3 refit at its own horizon (day A = T-h; the hour of T-7 is still known at h = 7), backtested walking forward exactly as the day-ahead one, and scored over the last two years against the same hour a week ago. A horizon is shown only where its mean absolute error is below the week-ago hour's; otherwise its forecast is written null with the reason (`tests/test_predict.py` holds the rule).

Built at 12:10 UTC on 26 November 2026: **all 145 place-horizons beat the week-ago hour and are shown.** The error grows with the horizon and flattens after five days: TEX's mean absolute error is 3,013 MW the day ahead (h = 2), 3,461 at h = 3 and 4,087 at h = 7, against 4,517 for the week-ago hour; NE's is 1,057, 1,127 and 1,157 against 1,510. Every place and horizon, with the week-ago hour's error beside it and each horizon's band coverage, is in the file; `runs/c730/table_f.py` prints them as a table. No operator files a forecast further ahead than the next day, so there is no operator line here; the file gives the operator's day-ahead error on the same hours for scale only.

## 13. With the weather known (session 10601)

The chain allows one line that uses the weather as it turned out, labelled so and never the headline. `with_weather_known` is the regression of section 3 with three regressors added: the region's observed population-weighted temperature at the hour (`region_weather_hourly`), its square, and the day's mean temperature; an authority takes its EIA region's temperature. It reads the target day's own weather, so it is not a forecast: it measures how much of the regression's error a perfect weather forecast could remove. It is scored apart (`demand_weather_known` rows, and `series.demand.with_weather_known` in each file), on the hours where its weather, the regression, the operator and the actual are all held (the temperature table ends on 7 November 2026 and has gaps, hence the hour counts). It is never chosen and never shown as the ERW forecast (`tests/test_predict.py`).

The last two years (built 26 November 2026 at 12:58 UTC; `runs/c730/table_w.py`):

| Place | Region's weather | Hours | Regression MAPE % | With the weather known MAPE % | Operator MAPE % | Share of the regression's gap to the operator the weather closes % |
|---|---|---:|---:|---:|---:|---:|
| region-cal | CAL | 14,310 | 4.18 | 3.25 | 7.60 | the regression already beats the operator |
| region-car | CAR | 5,446 | 7.41 | 3.37 | 2.16 | 77 |
| region-cent | CENT | 10,186 | 5.27 | 3.81 | 7.86 | the regression already beats the operator |
| region-fla | FLA | 9,911 | 6.29 | 3.31 | 5.48 | 369 |
| region-mida | MIDA | 12,742 | 5.13 | 3.38 | 3.48 | 106 |
| region-midw | MIDW | 9,600 | 4.40 | 2.73 | 2.02 | 70 |
| region-ne | NE | 12,167 | 8.14 | 6.19 | 2.88 | 37 |
| region-nw | NW | 10,925 | 2.68 | 2.07 | 5.07 | the regression already beats the operator |
| region-ny | NY | 14,025 | 6.27 | 4.47 | 2.77 | 51 |
| region-se | SE | 11,567 | 6.73 | 3.32 | 1.27 | 63 |
| region-sw | SW | 16,356 | 5.04 | 3.85 | 4.52 | 228 |
| region-ten | TEN | 12,600 | 7.54 | 3.66 | 2.35 | 75 |
| region-tex | TEX | 9,935 | 5.26 | 3.90 | 2.06 | 43 |
| ba-bpat | NW | 12,646 | 3.50 | 3.35 | 1.89 | 9 |
| ba-ciso | CAL | 14,736 | 4.25 | 3.39 | 8.48 | the regression already beats the operator |
| ba-cple | CAR | 5,759 | 9.47 | 5.05 | 4.16 | 83 |
| ba-duk | CAR | 5,759 | 7.37 | 3.66 | 2.51 | 76 |
| ba-erco | TEX | 9,935 | 5.26 | 3.90 | 2.06 | 43 |
| ba-fpc | FLA | 10,372 | 8.25 | 4.56 | 23.96 | the regression already beats the operator |
| ba-fpl | FLA | 10,435 | 6.00 | 3.58 | 3.24 | 88 |
| ba-isne | NE | 12,167 | 8.14 | 6.19 | 2.88 | 37 |
| ba-miso | MIDW | 9,600 | 4.16 | 2.64 | 2.46 | 90 |
| ba-nyis | NY | 14,025 | 6.27 | 4.47 | 2.77 | 51 |
| ba-pace | NW | 12,598 | 3.96 | 3.60 | 4.86 | the regression already beats the operator |
| ba-pjm | MIDA | 12,742 | 5.13 | 3.38 | 3.48 | 106 |
| ba-psco | NW | 12,666 | 6.83 | 6.49 | 12.99 | the regression already beats the operator |
| ba-soco | SE | 11,567 | 6.73 | 3.32 | 1.27 | 63 |
| ba-swpp | CENT | 11,448 | 5.22 | 3.83 | 8.11 | the regression already beats the operator |
| ba-tva | TEN | 12,600 | 7.54 | 3.66 | 2.35 | 75 |

with the weather known beats the operator in 12 of 29

What it says: with the weather known the regression would close more than the whole gap to the operator in MIDA and PJM, FLA and SW, and 70 percent or more of it in CAR, MIDW, TEN, CPLE, DUK, FPL and MISO; it closes less than half in TEX (43 percent), NE (37) and BPAT (9), so there the operator's forecast holds something beyond the weather that this regression lacks. With the weather known, the line beats the operator in 12 places; the operator stays ahead in 17.

## 14. A fourth candidate: regression_recent (session 10601)

The regression of section 3 with three more regressors, all from days held when the forecast is made: the log of the last hour (23:00 local) of day A, the most recent demand read; the log of the same hour on day A-1; the log of the same hour on day T-14. Fitted and refit exactly as the regression (30 coefficients an hour). It was tried first on six places (`runs/c730/trial_reg2.py`): it lowered the mean absolute error of the last two years by 1.6 to 8.4 percent in all six. It was then added as a candidate of the choice rule, which picks it in 28 of 29 places (PSCO keeps the regression). Nothing else changed. `replication/predict/replicate.py` refits it from these words too.

The last two years with the four candidates (built 26 November 2026 at 14:05 UTC; the table of section 7 is the build of 11:15 UTC, kept as it was):

| Place | Hours (2 years) | ERW MAPE % | Operator MAPE % | Yesterday's hour MAPE % | Week-ago hour MAPE % | ERW MAE MW | Operator MAE MW | ERW MAPE %, whole backtest | Operator MAPE %, whole backtest | Who wins (2 years) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| ba-cple | 16,931 | 9.60 | 4.03 | 12.65 | 15.81 | 717 | 294 | 9.06 | 4.08 | operator |
| region-car | 15,490 | 7.42 | 2.27 | 10.17 | 12.99 | 2,055 | 614 | 6.89 | 2.39 | operator |
| region-se | 17,514 | 6.37 | 1.27 | 9.12 | 11.15 | 1,838 | 360 | 6.12 | 2.01 | operator |
| ba-soco | 17,514 | 6.37 | 1.27 | 9.12 | 11.15 | 1,838 | 360 | 6.11 | 2.32 | operator |
| region-ne | 17,516 | 7.57 | 2.80 | 10.88 | 11.39 | 995 | 340 | 6.86 | 2.56 | operator |
| ba-isne | 17,516 | 7.57 | 2.80 | 10.88 | 11.39 | 995 | 340 | 6.86 | 2.56 | operator |
| region-ten | 17,516 | 7.01 | 2.34 | 9.56 | 12.46 | 1,443 | 473 | 7.04 | 2.26 | operator |
| ba-tva | 17,516 | 7.01 | 2.34 | 9.56 | 12.46 | 1,443 | 473 | 7.04 | 2.26 | operator |
| ba-duk | 17,388 | 7.56 | 3.04 | 10.74 | 12.88 | 1,004 | 407 | 6.95 | 2.84 | operator |
| region-ny | 17,321 | 5.70 | 2.73 | 8.70 | 9.08 | 998 | 479 | 5.10 | 2.63 | operator |
| ba-nyis | 17,321 | 5.70 | 2.73 | 8.70 | 9.08 | 998 | 479 | 5.10 | 2.63 | operator |
| region-tex | 17,372 | 4.91 | 2.08 | 6.33 | 8.14 | 2,839 | 1,177 | 5.47 | 2.39 | operator |
| ba-erco | 17,372 | 4.91 | 2.08 | 6.33 | 8.14 | 2,839 | 1,177 | 5.47 | 2.39 | operator |
| ba-fpl | 17,464 | 5.84 | 3.16 | 7.24 | 9.74 | 993 | 536 | 6.19 | 3.57 | operator |
| region-midw | 17,492 | 3.86 | 1.98 | 6.73 | 7.78 | 3,350 | 1,659 | 3.86 | 2.42 | operator |
| ba-bpat | 17,516 | 3.32 | 1.88 | 5.45 | 5.77 | 243 | 134 | 3.61 | 1.98 | operator |
| region-mida | 17,389 | 4.76 | 3.48 | 7.65 | 8.66 | 4,854 | 3,376 | 4.86 | 3.61 | operator |
| ba-pjm | 17,389 | 4.76 | 3.48 | 7.65 | 8.66 | 4,854 | 3,376 | 4.86 | 3.61 | operator |
| ba-miso | 17,492 | 3.65 | 2.42 | 6.55 | 7.35 | 2,899 | 1,856 | 3.69 | 2.77 | operator |
| region-sw | 17,382 | 4.89 | 4.51 | 6.41 | 8.24 | 712 | 605 | 4.56 | 3.50 | operator |
| region-fla | 15,582 | 5.86 | 5.50 | 7.58 | 10.29 | 1,826 | 1,734 | 5.98 | 5.57 | operator |
| ba-pace | 17,420 | 3.95 | 4.97 | 5.70 | 6.05 | 248 | 303 | 3.95 | 5.19 | ERW |
| region-nw | 14,663 | 2.68 | 5.05 | 4.49 | 4.75 | 1,183 | 2,195 | 2.68 | 3.99 | ERW |
| region-cent | 15,038 | 5.03 | 8.04 | 6.55 | 8.58 | 1,819 | 2,806 | 4.75 | 4.63 | ERW |
| ba-swpp | 16,965 | 4.94 | 8.25 | 6.40 | 8.47 | 1,772 | 2,844 | 4.74 | 4.79 | ERW |
| region-cal | 16,922 | 4.15 | 7.61 | 7.32 | 7.04 | 1,395 | 2,455 | 4.00 | 4.68 | ERW |
| ba-ciso | 17,420 | 4.20 | 8.50 | 7.48 | 6.82 | 1,150 | 2,274 | 4.06 | 5.08 | ERW |
| ba-psco | 17,510 | 6.67 | 13.64 | 8.77 | 9.04 | 362 | 749 | 6.61 | 6.44 | ERW |
| ba-fpc | 17,365 | 7.49 | 23.77 | 9.50 | 12.80 | 508 | 1,610 | 7.49 | 22.85 | ERW |


The ERW's error falls in every place where the new candidate is chosen (TEX from 5.22 to 4.91 percent, SE from 6.81 to 6.37, MIDA from 5.19 to 4.76, NE from 7.99 to 7.57), but the operator still wins in the same 21 places and the ERW in the same 8.

Session 10601, after section 14: each horizon of `ahead.json` now uses the better of the regression and `regression_recent` by the same rule (lower mean absolute error over the last two years). `regression_recent` is chosen at 91 of 145 place-horizons; its advantage shrinks with the horizon (TEX: 3,417 against 3,464 MW at h = 3, 4,087 against 4,095 at h = 7), as the most recent hour read lies further from the day forecast. All 145 still beat the week-ago hour.

## 15. The cross-check: ERCOT's own figure beside the backtest (session 10601)

ERCOT prints a chart of its Mid-Term Load Forecast's monthly mean absolute percent error, including the day-ahead (RUC) forecast, on www.ercot.com/gridinfo/load/forecast (robots: `/gridinfo/` is not disallowed). The chart is an image, `www.ercot.com/files/assets/2026/11/05/load-backcast.png` (the page's file names are swapped: the file named for the MAPE chart, `load-mtlf-mape.png`, shows the backcast), fetched once on 26 November 2026. Its monthly values were read off the image to about 0.05 point (`runs/c730/crosscheck_ercot.py` holds the readings). Beside them, the backtest's monthly error of ERCOT's forecast as filed on Form EIA-930 (ba-erco, cut `month` of `scores.json`), on the hours the backtest scores:

| Month | ERCOT's chart, day-ahead RUC MAPE % (read off the image) | Operator's forecast as filed on EIA-930, MAPE % (backtest) | ERW forecast, MAPE % | Hours |
|---|---:|---:|---:|---:|
| 2024-10 | 1.55 | 1.51 | 5.32 | 744 |
| 2024-11 | 2.05 | 2.13 | 4.77 | 721 |
| 2024-12 | 1.82 | 1.81 | 4.13 | 744 |
| 2025-01 | 2.89 | 3.14 | 8.05 | 744 |
| 2025-02 | 2.72 | 3.17 | 7.48 | 672 |
| 2025-03 | 1.97 | 2.19 | 4.52 | 741 |
| 2025-04 | 2.06 | 2.14 | 4.54 | 720 |
| 2025-05 | 2.72 | 2.58 | 5.65 | 744 |
| 2025-06 | 2.42 | 2.25 | 4.72 | 720 |
| 2025-07 | 2.25 | 2.23 | 3.08 | 744 |
| 2025-08 | 2.13 | 2.15 | 3.10 | 744 |
| 2025-09 | 1.78 | 1.99 | 4.61 | 720 |
| 2025-10 | 1.72 | 2.45 | 5.16 | 744 |
| 2025-11 | 2.17 | 2.52 | 4.17 | 721 |
| 2025-12 | 2.21 | 2.56 | 5.91 | 600 |
| 2026-01 | 2.70 | 2.70 | 6.58 | 744 |
| 2026-02 | 1.50 | 1.46 | 4.49 | 672 |
| 2026-03 | 1.77 | 1.76 | 5.85 | 741 |
| 2026-04 | 1.60 | 1.60 | 5.88 | 720 |
| 2026-05 | 2.48 | 2.48 | 6.05 | 744 |
| 2026-06 | 1.85 | 1.86 | 4.53 | 720 |
| 2026-07 | 1.49 | 1.50 | 3.51 | 744 |
| 2026-08 | 1.46 | 1.44 | 3.59 | 744 |
| 2026-09 | 1.33 | 1.34 | 4.29 | 720 |
| 2026-10 | 1.51 | 1.51 | 4.75 | 744 |

What it says: from February 2026 the two agree to 0.02 point every month, so the operator series the ERW scores itself against is, in those months, the forecast ERCOT grades itself on. Before, the EIA-930 filing scores up to 0.73 point worse (October 2025: 2.45 against 1.72; January and February 2025, October to December 2025), which can come from the filing being a different vintage of the forecast or from a different demand basis; the backtest does not say which. Over the 25 months the chart averages 2.01 percent and the filings 2.10. The ERW's forecast is beside them for scale. A second place (CAISO: its market monitor's 2024 annual report prints no such figure; SPP: none found) is not yet read.

Session 10601, 19:00 UTC, after section 14: with `regression_recent` chosen in 28 places, the peak's record moved (the files of 16:27 UTC; `runs/c730/table_f.py`). The ERW's peak error falls in most places (TEX from 6.30 to 6.10 percent, SE from 8.11 to 7.80), but rises in CENT from 6.02 to 7.35, where it now trails the operator's 6.61: the method chosen on hourly error is not always the better one for the day's peak. The ERW's peak beats the operator's in 4 places (NW, FPC, PSCO, SWPP), not 5, and it still names the peak hour exactly more often in 8. The table above is the build of 12:27 UTC, kept as it was.
