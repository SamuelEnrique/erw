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

Session 10601, 19:25 UTC: the peak now chooses its own method by the same rule on the peak's error (the candidate whose day peaks missed least over the last two years; `peak.method` in each file). `regression_recent` is the peak's method in 23 places and the regression in 6. CENT goes back to 6.02 percent against the operator's 6.61, and the ERW's peak again beats the operator's in 5 places (CENT, NW, FPC, PSCO, SWPP).

## 16. A day forecast more than once (session 10000, chain 701)

The ledger keeps the first forecast made for a place and target day and never rewrites it. A second run on the same day
(three landings on 26 November 2026 rebuilt the place files at 12:00, 14:00 and 15:00 UTC, and from 14:05 most places
chose `regression_recent`) made a newer forecast for the same day, and the page drew it while its ledger kept the first:
696 place-hours for 27 November, 672 of them different (mean gap 1.69 percent; done-line request 577). From then on a
place file's forecast for tomorrow is the ledger's once the ledger holds that day: its values, band, method and the hour
it was made, with `tomorrow_from` saying so and naming the method chosen now. So the page and its ledger show one
forecast for each day, the one made first, and a past day drawn from the ledger is the one a reader saw.

## 17. The ledgers as warehouse tables (session 10000, chain 701)

Data requests 2 and 5 of `docs/state/data_requests_predict.md`: `warehouse/predict/predict_tables.py` writes the two
ledgers as `predict_demand_forecasts` and `predict_price_forecasts`, a daily step of the data machine right after
the forecast (`dm_predict_tables`, then each table's stores: the validator, its coverage row and the archive). One row
a place and UTC hour of a target day, in the series shape: entity `eia930:<code>` of the place (region-tex is
`eia930:TEX`, ba-erco is `eia930:ERCO`), variable `demand_forecast_mw` or `lmp_dam_forecast` (the price
names its hub in `market` and `node`), and `vintage` the hour the forecast was made. The tables keep their
revisions: the key is entity, variable, hour and vintage, so a second forecast of an hour already held would be a second
row, never a replacement. Each table is the whole ledger, rewritten from it each run; the ledger itself only grows
(section 16). First written 26 November 2026 at 23:35 UTC: 696 and 144 rows, one making (11:00 UTC) for 27 November.

The backtests and the scores (`predict_demand_backtest`, `predict_scores`, `predict_price_backtest`) are not
tables yet: as `run.py` writes them, the two regressions share every place, hour and making time (and in the price,
places of one grid share a hub), so the validator refuses them as duplicate keys, and the scores file is not in a
standard shape. Their shape is this method's choice to make first.

## 18. The operator's forecast as filed: a check of the comparator (session 10602)

The operator column is the day-ahead forecast each authority files on Form EIA-930, as `eia930_forecast_error_hourly`
holds it. In several places it is not the operator's own forecast. Sought as the cross-check's second place, a vendor's
figure (Enverus, found by web search, not fetched) puts SPP's own day-ahead error at 2.16 percent in January 2025 and
2.20 in September 2025; the filing scores 1.98 and 9.53 in those months. Read month by month (`runs/c730/opbias.py`,
the filed forecast's sum as a percent of the demand's over the hours both hold), the filing breaks in level:

| Place | The filed forecast as a percent of the demand | Its MAPE |
|---|---|---|
| SWPP and CENT | 99 to 100 until April 2025; 104 to 116 from May 2025 | 1.5 to 2.8; then 5.2 to 15.8 |
| FPC | 68 to 78 in every month read | 21 to 30 |
| PSCO | 90 to 95 to December 2025; 84 to 88 from January to April 2026; 71 to 77 from May 2026 | 5 to 10; then 12 to 29 |
| FMPP | 93 to 102; 70 to 72 from February to July 2026; 110 in November 2026 | 3 to 5 (9 in October 2025); then 28 to 30 |
| SRP | 96 to 99 to February 2026; 103 to 124 from March 2026 | 3 to 5; then 8 to 30 |
| CISO and CAL | 89 to 98, lower over the years | 6 to 11 |
| PJM and MIDA | 97 to 99 | 2.9 to 4.4 as stamped |

(The months read are July 2024 to November 2026; the full monthly record of every place is in its file.)

PJM's level is right, but its filing matches the demand of the hour after its stamp best: over the last two years
its MAPE is 3.47 as stamped and 2.54 moved one hour later (`runs/c730/opshift.py`, both periods alike). No other
place is mended by a shift. A level that far from the demand for a whole month is a break in the filing (a footprint or
a definition), not a forecaster's error. Data request 7 of `docs/state/data_requests_predict.md` asks window A to read
EIA's own files for each.

What the files carry (add, never change): each place's demand series has `operator_filing`, the month-by-month check
(a month is flagged when the filed forecast is more than 5 percent from 100), the filed forecast's error over the last
two years with its hours moved by -1, 0 and 1, and `sound_last_2_years`, the scores on the unflagged months only.
`scores.json` has the cuts `operator_sound` and `operator_sound_last_2_years` for every method. The check judges the
comparator only: no forecast of the ERW reads it, and the choice of method is unchanged (a test holds both). A month
can also be flagged for a true divergence, not a filing: Texas in February 2021 (Winter Storm Uri, load shed) is.

**On the page (ready branch of session 11408, not the default).** Where the filing breaks, `/forecast`'s table of the
check leads with the scores on the months that pass and puts every month second (`FilingCheck` in
`site/app/forecast/lines.tsx`); the figures are the same, and the report card above is unchanged.

From the first full build (27 November 2026, `runs/c730/table_g.py`): over the last two years the ERW's MAPE is below
the operator's in 8 of 29 places; on the sound months only, in 4 (California 2.98 against 6.74 on 1,536 hours, the
Northwest 2.65 against 3.77, PACE 3.71 against 4.00, PSCO 4.09 against 5.31 on 740 hours). The Central region and SWPP
turn: on their sound months the operator is at 2.58 and 2.67, the ERW at 4.61 and 4.57. CISO and FPC have no sound month
in the last two years (their rows are present and empty), and the Florida region has 53 of its 87 months flagged.
Replication: `replicate.py` recomputes the two cuts from the check's rule (21,930 of 21,930 score figures equal).

## 19. With the weather forecast as issued (session 10602)

Samuel's order of 27 November 2026: the demand model with the dated weather forecast window A keeps, wherever enough
days are held. `warehouse/predict/predict_weather.py` reads the National Weather Service's hourly temperature forecast
at one airport per ISO (KDFW, KLAX, KLGA, KBOS, KPHL, KIND, KOKC; 14 places: each ISO's region and its authority):
every issue kept in `weather_forecast_issued_hourly` (from 26 November 2026, data request 4), and the rows of the
latest-only `weather_forecast_hourly` whose issue (`vintage`, NWS's updateTime) came before the hour the demand
forecast is made. Nothing known early: a forecast hour enters target day D only from an issue no later than 20:00 UTC
on D-1, and of those the latest (a test holds it).

The model is the regression of section 13 with the airport's temperature: fitted on the airport's observed temperature
(`noaa_station_weather_hourly`, NOAA ISD-Lite and LCD v2, 2019 on; after its last hour `weather_obs_hourly`) over the
days held when the forecast is made, then applied to day D with the temperature forecast for it. Beside it,
`with_airport_weather_known` applies the same coefficients to the airport's observed temperature of day D (not a
forecast), so the cost of the weather forecast's own error is seen.

Days held: the forecast as issued reaches back only to late September 2026, and only on days the latest-only table
kept an early enough issue. 13 to 20 target days are scored in each place in the full build (13 to 21 in the trial):
too few to judge, and the files say so
(`with_weather_forecast.status` is `too_few_days` below 30 days). A separate line, never the ERW forecast, as the
line "with the weather known" is. On those days, in the trial of 27 November (`runs/c730/wx_trial.py`), it was below
`regression_recent` in 6 of the 7 airports' regions and above it in the Mid-Atlantic (PJM, PHL); in Texas, on 17 days,
the operator was at 1.18 percent, the line at 3.81 and the ERW forecast at 5.33.

The full build (MAPE % on each place's own days: the line, with the airport's weather known, the ERW forecast, the
operator):

| Place (airport, days) | Line | Weather known | ERW | Operator |
|---|---:|---:|---:|---:|
| California (KLAX, 17) | 3.70 | 4.88 | 4.37 | 7.64 |
| Central (KOKC, 18) | 2.49 | 2.40 | 3.73 | 7.85 |
| Mid-Atlantic (KPHL, 13) | 3.13 | 3.23 | 2.66 | 2.78 |
| Midwest (KIND, 16) | 2.59 | 2.68 | 2.93 | 2.30 |
| New England (KBOS, 16) | 4.96 | 4.91 | 5.33 | 3.39 |
| New York (KLGA, 20) | 3.55 | 3.60 | 3.84 | 2.70 |
| Texas (KDFW, 17) | 3.81 | 3.84 | 5.33 | 1.18 |

(Each authority beside its region reads the same airport: CISO 4.23, 5.18, 4.83, 8.64; SWPP 2.45, 2.33, 3.57, 8.02;
MISO 2.52, 2.56, 2.74, 2.83; ERCO, ISNE, NYIS and PJM as their regions.) The forecast as issued does about as well as
the airport's weather known, a sign that a day-ahead temperature forecast is close to the day's weather at one airport;
where the operator's filing is sound (Texas, New York, New England) the operator stays ahead.

## 20. Net demand (session 10602)

Net demand is the demand less the output of wind and solar. For the 13 regions and ERCO (Texas is ERCOT alone), each
place's demand series has `net_demand`: the ERW's is its demand forecast less its wind and solar forecasts
(`docs/methods/predict_wind_solar.md`), all made at 20:00 UTC the day before from data through two days before; the
actual is EIA-930's demand less EIA-930's wind and solar output of the region. Yesterday is the same hour of the latest
whole day read, net. The operator's net demand needs all three of its forecasts: only Texas holds them, from
27 September 2026 (the filed demand forecast less ERCOT's wind and solar forecasts published at least 24 hours ahead).
The error is given in MW and as the mean absolute error over the mean net demand of the same hours (`scores.json`
series `net_demand`, column `mape`): a percent of an hour's net demand, which can be near zero, means nothing. No band:
the three bands are not combined.

The full build, the last two years (ERW, yesterday): California 8.96, 12.36; Carolinas 8.26, 11.12; Central 20.76,
25.22; Florida 6.79, 8.41; Mid-Atlantic 5.98, 8.94; Midwest 8.66, 12.52; New England 8.75, 12.26; Northwest 7.84,
10.84; New York 6.67, 9.83; Southeast 6.87, 9.43; Southwest 9.25, 11.58; Tennessee 7.41, 9.74; Texas and ERCO 15.77,
19.43. With the operator, Texas only, 1,368 hours from 30 September 2026: ERCOT 5.46, the ERW 17.06, yesterday 20.56.
Where wind is a large share the ERW's net demand error is several times its demand error (Central 20.76 against a
demand MAPE of 5.03, Texas 15.77 against 4.91; the two measures differ in form, the first over the mean, the second hour
by hour), and its wind forecast, made without the weather, misses by 35 to 40 percent of the mean output there.

## 21. The share of past hours inside each band (session 10602)

The band is meant to hold eight hours in ten. Every series of every file (demand, the day-ahead and the real-time
price, wind, solar) now carries `band_coverage`: over the last two years, the share of hours inside the band, below its
low end and above its high end, the share inside by local hour, and by month. `band_coverage_pct` (unchanged) is its
`inside_pct`.

## 22. The cross-check's second place: NYISO (session 10602)

NYISO's market monitor, Potomac Economics, prints the day-ahead peak load forecast's error by quarter in its quarterly
report (Third Quarter of 2025, slide 26, "Load Forecast and Actual Load"; potomaceconomics.com, robots read first,
fetched once on 27 November 2026): the mean of each day's forecast peak less its real-time peak, and the mean absolute
value. `replication/predict/crosscheck_nyiso.py` computes the same from the operator's forecast as filed on EIA-930 for
NYIS and NYIS's demand, each local day's highest hour, on the days both hold every hour:

| Quarter | Potomac: mean, mean absolute (MW) | The EIA-930 filing, backtest: mean, mean absolute (MW) | Days |
|---|---|---|---:|
| 2024 Q3 | -180, 479 | -504, 645 | 92 |
| 2025 Q2 | -124, 375 | -436, 520 | 91 |
| 2025 Q3 | -124, 448 | -363, 535 | 91 |

The two agree in sign and order: both forecasts fall short of the peak, by a few hundred megawatts. But the filing as
the backtest reads it falls short by 240 to 320 MW more, and misses by 145 to 170 MW more on average. Either NYISO's
filing on EIA-930 is not quite the forecast its monitor scores, or EIA-930's demand is not quite NYISO's real-time load
(the monitor's actual); this note cannot tell which. Either way the operator's error in New York, as the files score
it, is somewhat larger than its monitor's figure: the comparison flatters the ERW a little there, and the operator still
wins (2.74 against 5.70 percent over the last two years). With ERCOT (section 15), where the filing agrees with ERCOT's
own chart to 0.02 point from February 2026, this is the second place checked. The vendor's SPP figure (section 18) is
not a monitor's and is not counted.

## 23. More places: every authority with two years of demand (session 10603)

Samuel's order of 27 November 2026 ("more places"). The 29 places of section 1 are EIA's thirteen regions and the
sixteen authorities of at least 5,000 MW. The forecast now also covers every other balancing authority whose EIA-930
demand runs to the latest day the warehouse holds and covers at least two years (read on 27 November 2026 in
`eia930_ba_demand_hourly`; `run.MORE_BAS`): 35 more, from SPA (about 22 MW) to NEVP (about 5,100 MW). Left out, and why:
SWPW and BHBA (filing only since April 2026), WACM and WAUW (no demand after 1 April 2026), and AEC, NSB and OVEC (their
filings end in 2021, 2020 and 2018). Each authority added has its own file, of the same shape as the 29 and built by the
same code: the same methods, backtest, choice, band, scores, operator filing check (section 18), peak and history. Its
price is held (no organised market whose hub prices are public), and it has no net demand or weather forecast line.
The forecast two to seven days ahead (`ahead.json`, section 12) keeps its 29 places: adding 35 would double a daily step
of about half an hour.

Nothing of the 29 changes: their files equal those on main but for `built`; `scores.json` and `index.json` only gain
rows and places (24,911 rows before, 52,030 after, none of the first changed).

From the build of 27 November 2026 (rebuild 16, made as at 18:00 UTC on 26 November; `runs/c730/table_more.py`), the last
two years. The mean MW is the ERW's MAE over its MAPE; "sound months" are those whose filing passes the check of section
18 (a dash where no month of the two years passes):

| Place | Mean MW (2 years) | Chosen | Hours | MAPE %: ERW, operator, yesterday | Months flagged / held | Sound months, MAPE %: ERW, operator | Band inside % |
|---|---:|---|---:|---|---|---|---:|
| AECI | 2,663 | regression_recent | 17,516 | 10.26, 1.985, 12.27 | 0 / 89 | 10.258, 1.985 | 78.9 |
| AVA | 1,499 | regression_recent | 17,492 | 4.34, 1.698, 6.74 | 0 / 89 | 4.339, 1.698 | 80.0 |
| AZPS | 4,580 | regression_recent | 17,519 | 6.36, 9.518, 7.87 | 10 / 89 | 6.64, 7.804 | 76.8 |
| BANC | 2,200 | regression_recent | 17,376 | 5.75, 2.437, 8.26 | 0 / 89 | 5.751, 2.437 | 79.2 |
| CHPD | 232 | regression_recent | 17,516 | 5.47, 2.964, 7.50 | 25 / 89 | 5.474, 2.964 | 79.7 |
| CPLW | 585 | regression_recent | 16,812 | 8.54, 4.25, 11.39 | 2 / 89 | 8.495, 4.216 | 79.2 |
| DOPD | 286 | regression_recent | 17,515 | 4.12, 5.428, 6.04 | 39 / 89 | 4.187, 4.311 | 79.5 |
| EPE | 1,134 | regression_recent | 17,472 | 6.01, 3.219, 8.66 | 0 / 89 | 6.012, 3.219 | 78.4 |
| FMPP | 2,209 | regression_recent | 16,936 | 6.43, 11.173, 8.39 | 9 / 89 | 6.365, 3.907 | 78.7 |
| GCPD | 765 | regression_recent | 17,477 | 2.66, 2.196, 4.31 | 1 / 89 | 2.661, 2.196 | 79.4 |
| GVL | 254 | regression_recent | 16,293 | 8.13, 10.992, 10.22 | 52 / 89 | - | 78.4 |
| HST | 73 | regression_recent | 17,395 | 7.81, 6.604, 9.78 | 13 / 89 | 7.813, 6.604 | 80.0 |
| IID | 489 | regression_recent | 16,206 | 7.40, 3.432, 10.14 | 0 / 89 | 7.397, 3.432 | 77.8 |
| IPCO | 2,274 | regression_recent | 17,516 | 4.55, 5.095, 6.78 | 4 / 89 | 4.493, 4.587 | 80.0 |
| JEA | 1,635 | regression_recent | 17,515 | 7.85, 4.629, 10.51 | 4 / 87 | 7.853, 4.629 | 78.9 |
| LDWP | 2,958 | regression | 17,291 | 8.57, 10.143, 10.19 | 63 / 89 | 8.883, 9.231 | 75.4 |
| LGEE | 4,584 | regression_recent | 17,419 | 7.56, 7.876, 11.09 | 66 / 89 | - | 78.7 |
| NEVP | 5,129 | regression_recent | 16,783 | 4.57, 7.771, 5.95 | 35 / 89 | 4.287, 5.608 | 78.6 |
| NWMT | 1,361 | regression_recent | 17,513 | 4.30, 2.197, 5.61 | 3 / 89 | 4.304, 2.197 | 78.3 |
| PACW | 2,312 | regression_recent | 17,516 | 4.87, 6.991, 7.72 | 7 / 89 | 4.04, 3.049 | 80.1 |
| PGE | 2,796 | regression_recent | 17,516 | 4.15, 1.497, 7.04 | 0 / 89 | 4.147, 1.497 | 81.1 |
| PNM | 1,735 | regression_recent | 17,496 | 4.09, 6.237, 5.35 | 55 / 89 | 4.289, 5.03 | 78.6 |
| PSEI | 2,871 | regression_recent | 16,562 | 4.45, 36.516, 7.13 | 78 / 79 | - | 79.2 |
| SC | 3,361 | regression_recent | 17,387 | 7.54, 3.694, 9.34 | 15 / 89 | 7.538, 3.694 | 78.1 |
| SCEG | 2,950 | regression_recent | 16,068 | 8.02, 4.861, 10.25 | 3 / 89 | 8.21, 4.74 | 77.5 |
| SCL | 1,092 | regression_recent | 17,515 | 4.20, 3.299, 7.24 | 6 / 89 | 4.195, 3.299 | 78.8 |
| SEC | 248 | regression_recent | 17,212 | 13.36, 12.405, 16.27 | 61 / 88 | 11.823, 6.972 | 77.5 |
| SPA | 22 | regression | 13,794 | 23.69, 54.577, 32.19 | 70 / 89 | 23.573, 27.08 | 79.0 |
| SRP | 3,898 | regression_recent | 17,519 | 9.20, 8.69, 11.31 | 9 / 89 | 5.613, 4.093 | 71.2 |
| TAL | 342 | regression_recent | 17,514 | 8.33, 4.164, 11.08 | 0 / 89 | 8.333, 4.164 | 78.6 |
| TEC | 2,586 | regression_recent | 17,514 | 7.14, 4.168, 9.14 | 4 / 89 | 7.145, 4.168 | 79.3 |
| TEPC | 1,743 | regression_recent | 17,496 | 5.50, 2.72, 6.61 | 37 / 88 | 5.5, 2.72 | 79.4 |
| TIDC | 350 | regression_recent | 16,967 | 5.21, 3.09, 10.41 | 1 / 89 | 5.211, 3.09 | 79.0 |
| TPWR | 528 | regression_recent | 17,516 | 4.96, 2.224, 8.12 | 1 / 89 | 4.965, 2.224 | 79.5 |
| WALC | 916 | regression_recent | 17,441 | 10.26, 14.833, 11.01 | 15 / 89 | 10.176, 14.609 | 72.2 |

What the table says, plainly:

- **The operator wins in most of the small authorities too.** Over the last two years the ERW's MAPE is below the filed
  forecast's in 13 of the 35; on the sound months, in 8 of the 32 that have any (AZPS, DOPD, IPCO, LDWP, NEVP, PNM, SPA,
  WALC), and in most of these by less than a point and a half. Where the operator has a forecast it trusts, it is two to
  five times closer (PGE 1.50 against 4.15 percent, AECI 1.99 against 10.26).
- **Many small authorities' filings fail the check.** PSEI's filed forecast fails it in 78 of its 79 months (36.5 percent
  MAPE over the two years: not a forecast of PSEI's demand as filed), SPA in 70 of 89, LGEE 66, LDWP 63, SEC 61, PNM 55, GVL
  52. For PSEI, LGEE and GVL no month of the last two years passes, so there is no sound comparison at all. Data request 7
  (EIA's own files for the seven breaks of section 18) covers the 29 places; these are named here, not asked again.
- **The method:** `regression_recent` is chosen in 33 of the 35, the plain regression in LDWP and SPA.
- **The band** holds 71 (SRP, WALC 72) to 81 percent (PGE) of the hours against the nominal 80: SRP's and WALC's summers
  swing more than a year of errors at the hour shows.
- **The smallest are the noisiest:** SPA's demand (about 22 MW) is missed by 24 percent, SEC's by 13; a percent of a small
  number moves with every pump and plant.

Replication: `replication/predict/replicate.py` covers the 64 places as it covered the 29 (its count is in the progress
file and landing row 9). A test (`test_the_places_added_follow_their_rule`) holds that every place of the run has its
file, that none added is one of the 29, and that each added runs to the last day the 29 reach and scores two years.

## 24. Longer backtests (session 10603)

Samuel's order of 27 November 2026 ("longer backtests"). What the warehouse's data allow, series by series:

| Series | Its backtest begins | What bounds it | Longer now? |
|---|---|---|---|
| Demand (every place) | 1 July 2019 | EIA-930 demand held from 1 July 2018 (`eia930_ba_demand_hourly`); the regression needs 300 days of its own rows | No: at most two months earlier with the data held. Data request 9 asks for EIA's six-month files from July 2015, which would start it on 1 July 2016 |
| Day-ahead price | March 2020 (ERCOT, SPP), May 2024 (CAISO) | it reads the demand forecast, so it inherits the demand's start; CAISO's hub prices are held from July 2023 | No, until request 9 |
| Real-time price | July 2019 to 2024 by hub | ERCOT's hub prices are held from January 2015, SPP's from July 2018, CAISO's real-time prices from July 2023 | Yes, at ERCOT: from 1 January 2016 (`predict_price.md` section 8) |
| Wind and solar | 1 July 2019 | EIA-930 output by region held from July 2018 | At most eight months earlier; not built |
| Net demand | as demand | demand, wind and solar | No |
| With the weather forecast as issued | late September 2026 | the NWS forecasts as issued are kept from then | No: it grows a day a day (13 to 21 days a place on 27 November; 30 are needed to score it) |

So the one longer backtest built is the real-time price at ERCOT's four hubs, from 2016: the day-ahead price beats the
ERW in nine or ten of the eleven years at each (sections 8 and 9 of `predict_price.md`). The demand backtest cannot be
longer until request 9 is answered; then `predict_data.py` would read `eia930_all_history` before the hourly extracts
begin, and the walk would start on 1 July 2016, with the operator's filed forecast scored from the same day. Nothing in
the backtests already published changes.

## 25. The longer backtest, from 2016 (session 10603)

Section 24 said the demand backtest could not start before 1 July 2019 until older demand was held. Window A answered
data request 9 the same day (landing 20, `f073726a2`): `eia930_all_history` now holds every authority's demand from
EIA's six-month files, July 2015 to June 2018, with its filed forecast. `warehouse/predict/long_backtest.py` walks the
same forecast from 1 July 2016 on that demand (`predict_data.demand_panel_long`: the history's hours before the hourly
table's, the hourly table winning an hour both hold; regions summed by the demand pages' rule) and writes
`site/data/predict/long_backtest.json`: for each of the 64 places, every year from 2016 scored on the hours every ERW
method holds, and the whole span.

What stays as it was: the place files' backtest, its cuts and the choice. The longer window changes the regressions'
fits of 2019 and 2020 (they now see up to 730 days before them where they saw only what was held since July 2018), so
the longer walk is a file of its own rather than a change to the published one. The ERW's method in every year is the
one chosen now on the last two years, and the longer walk leaves that choice unchanged at every place (the test holds
it). The operator is set beside the ERW only on the hours its screened filing holds (`eia930_forecast_error_hourly`,
from July 2018): the history's filed forecasts are not screened for filing errors and are not used.

A caution on the early years: the history's demand is EIA's published series as filed, before the warehouse's own
screens. Some early years carry filing errors that inflate the error: PACW's 2017 (145 percent MAPE), the Southeast's
and HST's 2017 (14.6 and 13.7), and CISO's span (6.7 over the span, 3.6 and 3.9 in 2017 and 2025). They are shown as
they come.

From the build of 27 November 2026 (`runs/c730/table_long_all.py`), MAPE in percent:

| Place | First day | Hours | MAPE % 2016 to 2026: ERW, regression, yesterday | ERW 2017 | ERW 2025 | Years the ERW beats the operator (of those it holds) |
|---|---|---:|---|---:|---:|---|
| region-cal | 2016-07-01 | 89,660 | 3.954, 4.028, 7.552 | 3.701 | 3.725 | 4 of 9: 2023, 2024, 2025, 2026 |
| region-car | 2016-07-01 | 86,646 | 6.84, 7.345, 9.91 | 7.091 | 7.229 | 0 of 9 |
| region-cent | 2016-07-01 | 90,605 | 4.726, 4.964, 6.972 | 4.485 | 5.271 | 2 of 9: 2025, 2026 |
| region-fla | 2016-09-23 | 81,973 | 6.151, 6.281, 7.957 | 6.621 | 5.679 | 4 of 9: 2018, 2019, 2021, 2026 |
| region-mida | 2016-10-23 | 84,567 | 4.904, 5.276, 8.167 | 4.987 | 4.726 | 0 of 9 |
| region-midw | 2016-07-01 | 90,930 | 3.886, 4.187, 7.111 | 3.958 | 3.857 | 0 of 9 |
| region-ne | 2016-07-01 | 91,181 | 6.551, 6.915, 9.806 | 5.948 | 7.821 | 0 of 9 |
| region-nw | 2016-09-05 | 72,909 | 2.649, 2.816, 4.824 | 2.586 | 2.681 | 8 of 8: 2018, 2019, 2021, 2022, 2023, 2024, 2025, 2026 |
| region-ny | 2016-07-01 | 90,971 | 4.965, 5.332, 8.162 | 4.753 | 5.577 | 0 of 9 |
| region-se | 2016-07-01 | 89,015 | 6.986, 7.314, 9.501 | 14.614 | 6.168 | 0 of 9 |
| region-sw | 2016-07-15 | 87,878 | 4.553, 4.696, 5.966 | 4.149 | 4.389 | 3 of 9: 2018, 2021, 2025 |
| region-ten | 2016-07-01 | 90,136 | 7.171, 7.312, 9.764 | 7.559 | 6.719 | 0 of 9 |
| region-tex | 2016-07-01 | 90,821 | 5.619, 6.002, 7.687 | 5.969 | 5.063 | 0 of 9 |
| ba-bpat | 2016-07-01 | 91,181 | 3.65, 3.888, 5.769 | 3.912 | 3.347 | 0 of 9 |
| ba-ciso | 2016-07-01 | 91,033 | 6.743, 6.779, 10.372 | 3.596 | 3.873 | 4 of 9: 2023, 2024, 2025, 2026 |
| ba-cple | 2016-07-01 | 91,098 | 9.148, 9.62, 12.432 | 9.192 | 9.485 | 0 of 9 |
| ba-duk | 2016-07-01 | 91,125 | 6.933, 7.399, 10.478 | 7.019 | 7.065 | 0 of 9 |
| ba-erco | 2016-07-01 | 90,821 | 5.619, 6.002, 7.687 | 5.969 | 5.063 | 0 of 9 |
| ba-fpc | 2016-07-01 | 90,641 | 7.576, 7.896, 9.791 | 7.646 | 7.245 | 9 of 9: 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 |
| ba-fpl | 2016-07-01 | 90,848 | 7.134, 7.172, 8.704 | 6.823 | 5.836 | 0 of 9 |
| ba-isne | 2016-07-01 | 91,181 | 6.551, 6.915, 9.806 | 5.948 | 7.821 | 0 of 9 |
| ba-miso | 2016-07-01 | 91,157 | 3.714, 3.998, 6.99 | 3.783 | 3.676 | 0 of 9 |
| ba-nyis | 2016-07-01 | 90,971 | 4.965, 5.332, 8.162 | 4.753 | 5.577 | 0 of 9 |
| ba-pace | 2016-07-01 | 91,148 | 3.907, 3.97, 5.82 | 3.595 | 3.536 | 9 of 9: 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 |
| ba-pjm | 2016-07-01 | 91,041 | 4.924, 5.315, 8.243 | 5.243 | 4.726 | 0 of 9 |
| ba-psco | 2016-07-01 | 91,128 | 8.44, 8.44, 10.061 | 4.056 | 6.395 | 2 of 9: 2025, 2026 |
| ba-soco | 2016-07-01 | 89,126 | 6.116, 6.511, 8.857 | 6.438 | 6.168 | 0 of 9 |
| ba-swpp | 2016-07-01 | 91,061 | 4.731, 4.969, 6.968 | 4.484 | 5.28 | 2 of 9: 2025, 2026 |
| ba-tva | 2016-07-01 | 90,136 | 7.171, 7.312, 9.764 | 7.559 | 6.719 | 0 of 9 |
| ba-aeci | 2016-07-01 | 91,181 | 9.433, 9.828, 11.675 | 9.787 | 9.938 | 0 of 9 |
| ba-ava | 2016-07-01 | 91,181 | 4.433, 4.709, 6.819 | 4.484 | 4.54 | 1 of 9: 2018 |
| ba-azps | 2016-07-01 | 91,143 | 5.624, 5.803, 7.204 | 5.16 | 6.186 | 2 of 9: 2025, 2026 |
| ba-banc | 2016-07-01 | 90,210 | 5.502, 5.793, 8.302 | 4.921 | 5.565 | 0 of 9 |
| ba-chpd | 2016-07-01 | 91,181 | 5.996, 6.491, 7.886 | 6.051 | 5.673 | 4 of 9: 2018, 2019, 2020, 2021 |
| ba-cplw | 2016-07-01 | 91,125 | 8.135, 8.5, 10.982 | 7.79 | 8.377 | 0 of 9 |
| ba-dopd | 2016-07-01 | 91,181 | 5.296, 5.629, 7.052 | 6.28 | 4.223 | 6 of 9: 2018, 2019, 2020, 2023, 2024, 2025 |
| ba-epe | 2016-07-01 | 90,748 | 5.434, 5.525, 8.744 | 5.151 | 5.929 | 0 of 9 |
| ba-fmpp | 2016-07-01 | 90,809 | 6.756, 6.865, 8.948 | 6.849 | 6.089 | 1 of 9: 2026 |
| ba-gcpd | 2016-07-01 | 91,181 | 3.127, 3.367, 4.649 | 3.338 | 2.593 | 0 of 9 |
| ba-gvl | 2016-08-23 | 86,919 | 8.49, 8.76, 10.863 | 8.189 | 7.608 | 4 of 9: 2023, 2024, 2025, 2026 |
| ba-hst | 2016-07-01 | 91,034 | 8.493, 8.831, 10.517 | 13.729 | 7.681 | 2 of 9: 2020, 2021 |
| ba-iid | 2016-07-01 | 88,539 | 10.745, 10.915, 13.65 | 7.42 | 7.191 | 0 of 9 |
| ba-ipco | 2016-07-01 | 91,153 | 4.827, 5.076, 6.926 | 6.027 | 4.59 | 4 of 9: 2018, 2019, 2025, 2026 |
| ba-jea | 2016-07-01 | 91,097 | 7.821, 8.109, 10.639 | 8.416 | 7.625 | 0 of 9 |
| ba-ldwp | 2016-07-01 | 90,364 | 8.848, 8.848, 11.567 | 4.678 | 8.927 | 9 of 9: 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 |
| ba-lgee | 2016-07-01 | 90,873 | 7.365, 7.674, 11.254 | 7.355 | 7.315 | 4 of 9: 2023, 2024, 2025, 2026 |
| ba-nevp | 2016-07-01 | 90,714 | 4.317, 4.492, 5.711 | 4.193 | 4.329 | 6 of 9: 2018, 2022, 2023, 2024, 2025, 2026 |
| ba-nwmt | 2016-07-01 | 90,917 | 4.139, 4.23, 5.496 | 3.47 | 4.577 | 1 of 9: 2018 |
| ba-pacw | 2016-07-01 | 91,181 | 18.197, 18.513, 21.236 | 144.746 | 5.67 | 2 of 9: 2018, 2025 |
| ba-pge | 2016-07-01 | 91,181 | 4.529, 4.786, 7.663 | 4.616 | 4.186 | 0 of 9 |
| ba-pnm | 2016-07-01 | 91,032 | 3.78, 3.836, 5.153 | 3.179 | 4.037 | 6 of 9: 2021, 2022, 2023, 2024, 2025, 2026 |
| ba-psei | 2016-07-01 | 76,830 | 5.014, 5.165, 7.263 | 4.788 | 4.453 | 8 of 8: 2018, 2019, 2021, 2022, 2023, 2024, 2025, 2026 |
| ba-sc | 2016-07-01 | 87,784 | 7.647, 8.061, 9.619 | 8.154 | 7.204 | 2 of 9: 2019, 2020 |
| ba-sceg | 2016-07-01 | 90,045 | 8.574, 8.943, 11.003 | 7.529 | 18.754 | 0 of 9 |
| ba-scl | 2016-07-01 | 90,965 | 4.354, 4.428, 7.44 | 4.452 | 4.081 | 2 of 9: 2021, 2022 |
| ba-sec | 2016-07-01 | 74,287 | 32.326, 32.554, 36.77 | 33.946 | 14.337 | 4 of 9: 2018, 2019, 2020, 2026 |
| ba-spa | 2016-07-01 | 90,415 | 17.764, 17.764, 23.739 | 11.13 | 30.786 | 9 of 9: 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 |
| ba-srp | 2016-07-01 | 89,901 | 6.179, 6.311, 7.765 | 5.438 | 5.775 | 1 of 9: 2026 |
| ba-tal | 2016-07-01 | 91,181 | 8.335, 8.655, 11.512 | 8.178 | 8.01 | 0 of 9 |
| ba-tec | 2016-07-01 | 90,983 | 7.237, 7.499, 9.478 | 6.981 | 6.901 | 0 of 9 |
| ba-tepc | 2016-07-05 | 88,920 | 8.537, 8.792, 9.815 | 4.859 | 5.517 | 6 of 9: 2018, 2019, 2020, 2021, 2022, 2023 |
| ba-tidc | 2016-07-01 | 88,399 | 4.872, 5.204, 10.909 | 4.536 | 5.154 | 0 of 9 |
| ba-tpwr | 2016-07-01 | 91,181 | 4.817, 5.116, 7.842 | 4.251 | 4.931 | 0 of 9 |
| ba-walc | 2016-07-01 | 91,200 | 7.26, 7.377, 7.822 | 5.965 | 8.54 | 9 of 9: 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 |

What the longer record says, plainly:

- **The ERW's error is steady across ten years.** Texas sits between 4.8 and 6.2 percent every year from 2016; the
  Midwest near 3.9; the Northwest near 2.6. The method chosen now (`regression_recent` almost everywhere) is at least as
  good as the plain regression and better than yesterday's hour over the whole span at every place.
- **The operator wins year after year where its filing is sound.** In 19 of the 29 large places the ERW beats the
  operator in no year it holds. Where it does, most are the filing breaks of section 18: FPC in every year, CAL and CISO
  from 2023, SWPP, CENT and PSCO in 2025 and 2026. The ERW is ahead outright in the Northwest (all eight years) and
  PACE (all nine), and in Florida and the Southwest in some years. Among the 35 authorities the ERW is ahead in more
  years, often where
  their filings fail the check (LDWP and SPA in every year).
- **A longer record does not change the verdict of the last two years;** it shows it was not a run of luck either way.

Replication (`replication/predict/replicate_long.py`, from this section's words; it builds the longer demand itself from
the two tables): its count on the 64 places is in the progress file and landing row 10.

## 26. Net demand for more places (session 10603)

Section 20 gave net demand to the 13 regions and ERCO, the places whose wind and solar the warehouse then held. With the
authorities' wind and solar held (data request 10; `predict_wind_solar.md` section 8), every place with a wind and solar
entry now carries it, by `run.net_place`: the five other authorities that are each a whole region read their region's
entry, as ERCO reads Texas's (ISNE, NYIS, PJM, SOCO, TVA, with the region's figures); CISO reads CAISO's own hubs
(`grid-caiso`), whose forecasts CAISO publishes, so CISO's net demand has an operator line; each of the 35 authorities of
the wind and solar file reads its own. 55 places in all; the other nine stay `null`.

**A fuel an authority never reports is taken as zero.** EIA-930 carries a wind column only for an authority that
reports wind (a utility with no wind plant files none). For net demand such a fuel counts as zero output, on every
hour, for the actual and every method, and the block names it in `fuels_taken_as_zero` (18 authorities, wind in 16 of
them, solar in AECI and CHPD). The wind and solar file itself keeps such a fuel `not held`: a forecast of nothing is not
shown as a forecast.

From rebuild 18 (made as at 18:00 UTC on 26 November; `runs/c730/table_net.py`), the last two years, the error over the
mean net demand of the same hours:

| Place | Wind and solar read | Hours | Error over mean net demand %: ERW, yesterday | Fuels taken as zero | With the operator: ERW, operator |
|---|---|---:|---|---|---|
| region-cal | region-cal | 16,897 | 8.96, 12.36 | - | - |
| region-car | region-car | 16,300 | 8.26, 11.12 | - | - |
| region-cent | region-cent | 17,160 | 20.76, 25.22 | - | - |
| region-fla | region-fla | 16,349 | 6.79, 8.41 | - | - |
| region-mida | region-mida | 17,208 | 5.98, 8.94 | - | - |
| region-midw | region-midw | 17,174 | 8.66, 12.52 | - | - |
| region-ne | region-ne | 17,477 | 8.75, 12.26 | - | - |
| region-nw | region-nw | 14,376 | 7.84, 10.84 | - | - |
| region-ny | region-ny | 17,291 | 6.67, 9.83 | - | - |
| region-se | region-se | 16,413 | 6.87, 9.43 | - | - |
| region-sw | region-sw | 17,045 | 9.25, 11.58 | - | - |
| region-ten | region-ten | 17,516 | 7.41, 9.74 | - | - |
| region-tex | region-tex | 17,172 | 15.77, 19.43 | - | 17.06, 5.46 (1,368 h) |
| ba-bpat | ba-bpat | 17,518 | 11.52, 14.93 | - | - |
| ba-ciso | grid-caiso | 17,263 | 9.27, 12.5 | - | 9.21, 14.09 (26,754 h) |
| ba-cple | ba-cple | 17,454 | 11.85, 15.09 | wind | - |
| ba-duk | ba-duk | 17,454 | 8.1, 11.08 | wind | - |
| ba-erco | region-tex | 17,172 | 15.77, 19.43 | - | 17.06, 5.46 (1,368 h) |
| ba-fpc | ba-fpc | 17,454 | 8.7, 10.64 | wind | - |
| ba-fpl | ba-fpl | 17,518 | 7.09, 8.42 | wind | - |
| ba-isne | region-ne | 17,477 | 8.75, 12.26 | - | - |
| ba-miso | ba-miso | 17,518 | 9.02, 13.01 | - | - |
| ba-nyis | region-ny | 17,291 | 6.67, 9.83 | - | - |
| ba-pace | ba-pace | 17,517 | 23.43, 29.12 | - | - |
| ba-pjm | region-mida | 17,208 | 5.98, 8.94 | - | - |
| ba-psco | ba-psco | 17,518 | 27.66, 34.81 | - | - |
| ba-soco | region-se | 16,413 | 6.87, 9.43 | - | - |
| ba-swpp | ba-swpp | 17,518 | 20.79, 25.25 | - | - |
| ba-tva | region-ten | 17,516 | 7.41, 9.74 | - | - |
| ba-aeci | ba-aeci | 17,518 | 13.84, 16.87 | solar | - |
| ba-ava | ba-ava | 17,518 | 6.78, 9.64 | - | - |
| ba-azps | ba-azps | 17,520 | 10.31, 12.63 | - | - |
| ba-banc | ba-banc | 17,518 | 7.05, 9.62 | wind | - |
| ba-chpd | ba-chpd | 17,487 | 5.82, 7.82 | solar | - |
| ba-cplw | ba-cplw | 17,462 | 9.43, 12.32 | wind | - |
| ba-epe | ba-epe | 17,520 | 8.86, 12.0 | wind | - |
| ba-fmpp | ba-fmpp | 17,416 | 6.73, 8.55 | wind | - |
| ba-iid | ba-iid | 16,454 | 24.0, 28.07 | wind | - |
| ba-ipco | ba-ipco | 17,518 | 10.88, 14.83 | - | - |
| ba-jea | ba-jea | 17,518 | 8.11, 10.53 | wind | - |
| ba-ldwp | ba-ldwp | 16,732 | 11.41, 12.86 | - | - |
| ba-lgee | ba-lgee | 17,437 | 8.01, 11.2 | wind | - |
| ba-nevp | ba-nevp | 17,047 | 8.77, 11.07 | - | - |
| ba-nwmt | ba-nwmt | 17,518 | 38.13, 46.83 | - | - |
| ba-pacw | ba-pacw | 17,518 | 12.44, 16.96 | - | - |
| ba-pnm | ba-pnm | 17,520 | 84.58, 104.0 | - | - |
| ba-psei | ba-psei | 17,518 | 6.39, 9.62 | - | - |
| ba-sc | ba-sc | 17,518 | 8.13, 9.78 | wind | - |
| ba-sceg | ba-sceg | 16,406 | 8.91, 11.0 | wind | - |
| ba-sec | ba-sec | 17,380 | 13.93, 16.38 | wind | - |
| ba-srp | ba-srp | 17,519 | 10.5, 12.74 | - | - |
| ba-tal | ba-tal | 17,518 | 8.82, 11.38 | wind | - |
| ba-tec | ba-tec | 17,518 | 8.66, 10.8 | wind | - |
| ba-tepc | ba-tepc | 17,520 | 8.91, 10.82 | - | - |
| ba-walc | ba-walc | 17,088 | 16.57, 19.2 | - | - |

What it says: the ERW's net demand beats yesterday's net demand at every place, by a tenth (LDWP) to a third. Where wind is a
large share of demand the error over the mean net demand is large because the mean is small (PNM 84.6 percent, NWMT
38.1, PSCO 27.7, PACE 23.4, the Central region 20.8): a percent of a small remainder. CISO is the one new place with an
operator line, and there the ERW is ahead (9.21 against 14.09 percent over 26,754 hours), but only because CISO's demand
forecast as filed on EIA-930 sits at 89 to 94 percent of its demand (section 18): the comparison inherits that filing
break. Texas, the other place with an operator line, stays as section 20 found it (ERCOT's 5.46 against the ERW's
17.06).

Replication (`replication/predict/replicate_net.py`, which now builds each place's wind and solar entry by the same rules,
zero fuels included): its count is in the progress file and landing row 10.

## 27. The filing breaks are EIA's own (data request 7 answered, session 10603)

Section 18 asked window A whether the seven breaks in the operator's filed forecast were EIA's published levels or a
fault of the warehouse's reading (data request 7). Window A read EIA's own six-month BALANCE files independently of the
table's code (`docs/reviews/answers-c701-2026-11-26/predict_row7.py` and its output) and found the same levels in all
seven cases, within half a point: SWPP 108 to 112 percent of the demand from May 2025, FPC about 76, PSCO 71 to 77 from
May 2026, FMPP about 71 from February to July 2026, SRP 115 to 124 in four months of 2026, CISO 89 to 93; and PJM's
filed forecast matches the next hour's demand in EIA's file too (MAPE 2.5 against 3.5 percent). So the levels are EIA's
as published (`docs/methods/forecast_error.md`, "Levels that are EIA's own"), and nothing is screened: that is the
table owner's choice. The forecast's files keep doing what section 18 set out: the headline compares with the filing as
published, and the sound months are scored beside it.

## 28. Further ahead for the 35 authorities, and the backtest tables' shape (session 10603)

**Further ahead.** Section 12's forecast two to seven days ahead (`ahead.json`) keeps its 29 places, which window A's
daily run rebuilds (about half an hour). The 35 authorities of section 23 have it in a file of their own,
`site/data/predict/ahead_more.json`, written by `python warehouse/predict/ahead.py --more`: the same horizons, methods,
rule and shape, meant for a weekly step (data request 18). Built as at 18:00 UTC on 26 November: every one of the 175
place-horizons beats the same hour a week ago and is shown; the error grows from three days to seven by 3 percent
(SPA) to 21 percent (WALC) of itself. The last two years, `runs/c730/table_ahead.py`:

| Authority | h3 method | MAPE % h3 | MAPE % h7 | Week-ago hour MAPE % | Shown |
|---|---|---:|---:|---:|---|
| AECI | regression_recent | 11.95 | 13.635 | 17.944 | 5 of 5 |
| AVA | regression_recent | 5.079 | 5.72 | 7.145 | 5 of 5 |
| AZPS | regression_recent | 7.257 | 8.035 | 9.783 | 5 of 5 |
| BANC | regression_recent | 6.498 | 7.208 | 9.195 | 5 of 5 |
| CHPD | regression_recent | 6.427 | 7.117 | 9.425 | 5 of 5 |
| CPLW | regression_recent | 10.106 | 11.317 | 14.863 | 5 of 5 |
| DOPD | regression_recent | 4.926 | 5.676 | 7.081 | 5 of 5 |
| EPE | regression_recent | 6.632 | 7.268 | 9.514 | 5 of 5 |
| FMPP | regression_recent | 7.394 | 7.911 | 10.642 | 5 of 5 |
| GCPD | regression_recent | 3.147 | 3.742 | 4.579 | 5 of 5 |
| GVL | regression_recent | 9.067 | 9.73 | 13.463 | 5 of 5 |
| HST | regression_recent | 8.789 | 9.345 | 12.443 | 5 of 5 |
| IID | regression_recent | 8.927 | 9.646 | 13.215 | 5 of 5 |
| IPCO | regression_recent | 5.314 | 5.986 | 7.826 | 5 of 5 |
| JEA | regression_recent | 8.789 | 9.581 | 13.02 | 5 of 5 |
| LDWP | regression | 22.462 | 24.832 | 27.608 | 5 of 5 |
| LGEE | regression | 8.653 | 9.478 | 13.262 | 5 of 5 |
| NEVP | regression_recent | 5.603 | 6.489 | 8.134 | 5 of 5 |
| NWMT | regression_recent | 4.97 | 5.66 | 6.645 | 5 of 5 |
| PACW | regression_recent | 5.678 | 6.705 | 7.818 | 5 of 5 |
| PGE | regression_recent | 4.612 | 5.017 | 6.533 | 5 of 5 |
| PNM | regression_recent | 4.499 | 5.144 | 6.352 | 5 of 5 |
| PSEI | regression_recent | 5.206 | 5.661 | 7.324 | 5 of 5 |
| SC | regression | 8.459 | 9.11 | 12.149 | 5 of 5 |
| SCEG | regression_recent | 15.428 | 16.049 | 19.802 | 5 of 5 |
| SCL | regression_recent | 4.743 | 5.14 | 6.809 | 5 of 5 |
| SEC | regression_recent | 15.499 | 17.001 | 21.654 | 5 of 5 |
| SPA | regression | 31.463 | 32.475 | 42.382 | 5 of 5 |
| SRP | regression_recent | 10.101 | 10.525 | 13.615 | 5 of 5 |
| TAL | regression_recent | 9.371 | 10.177 | 13.827 | 5 of 5 |
| TEC | regression_recent | 7.994 | 8.615 | 11.663 | 5 of 5 |
| TEPC | regression_recent | 6.305 | 6.881 | 9.247 | 5 of 5 |
| TIDC | regression_recent | 5.928 | 6.369 | 8.149 | 5 of 5 |
| TPWR | regression_recent | 5.738 | 6.39 | 8.121 | 5 of 5 |
| WALC | regression_recent | 11.928 | 14.428 | 15.546 | 5 of 5 |

Replication: `replication/predict/replicate_ahead.py` reads `ahead_more.json` as it reads `ahead.json`; its count is in
the progress file and the next landing row.

**The backtest tables' shape (data requests 3 and 5, left to this method).** `run.py --out-dir` writes
`predict_demand_backtest` with the method in the variable (`demand_forecast_regression_mw`,
`demand_forecast_regression_recent_mw`), and `predict_price_backtest` (and `price_hubs.py`'s
`predict_price_hubs_backtest`) keyed by place, the place's EIA-930 entity or the hub for a hub of section 10's file,
with the hub in `x_hub`, so neither repeats an (entity, variable, ts_utc) key; both pass the validator (a two-place
trial: 259,300 and 117,646 rows, 0 errors, 0 warnings). `predict_scores` stays a file: every score is a summary the
backtest table and the demand rebuild (`replicate.py`), and no standard shape holds a cut and its key without
contortion (data request 17).

## 29. The day's peak over the longer backtest (session 10603)

`long_backtest.json` now carries, for each place, the day's peak of section 11 over the longer walk (`peak`): the peak's
own choice as the place file makes it (the candidate whose day peaks missed least over the last two years, on the days
the operator also holds), then each year from 2016 scored on the days every ERW method holds every hour, and the
operator beside it on the days its screened filing holds (from July 2018). A day whose highest hour is zero or below is
left out: one such day in the Tennessee region's early files is a filing error, and its percent error would be
infinite. Built on the tables as window A's daily run refreshed them at 19:20 UTC on 27 November (through 26 November);
the place files of row 10 read the day before, which the files' tests allow (a weekly file beside daily ones, their
last days within a week). The 29 places, `runs/c730/table_long_peak.py`:

| Place | Peak method | Days | Peak MAPE % over the span: ERW, yesterday | ERW names the hour exactly % | Years the ERW's peak beats the operator's |
|---|---|---:|---|---:|---|
| region-cal | regression | 3,713 | 4.751, 7.272 | 60.2 | 0 of 9 |
| region-car | regression_recent | 3,575 | 8.222, 10.952 | 45.1 | 0 of 9 |
| region-cent | regression | 3,757 | 5.856, 7.543 | 47.4 | 2 of 9: 2025, 2026 |
| region-fla | regression | 3,384 | 7.086, 8.313 | 42.7 | 1 of 9: 2021 |
| region-mida | regression_recent | 3,489 | 5.752, 8.587 | 47.6 | 0 of 9 |
| region-midw | regression_recent | 3,768 | 4.412, 7.056 | 47.9 | 0 of 9 |
| region-ne | regression_recent | 3,781 | 5.993, 8.305 | 61.6 | 0 of 9 |
| region-nw | regression_recent | 3,005 | 3.101, 5.006 | 58.4 | 6 of 8: 2019, 2021, 2023, 2024, 2025, 2026 |
| region-ny | regression_recent | 3,753 | 5.324, 7.811 | 62.5 | 0 of 9 |
| region-se | regression_recent | 3,689 | 7.623, 9.722 | 40.7 | 0 of 9 |
| region-sw | regression_recent | 3,655 | 5.423, 6.429 | 59.8 | 2 of 9: 2018, 2021 |
| region-ten | regression_recent | 3,735 | 8.046, 10.196 | 35.8 | 0 of 9 |
| region-tex | regression_recent | 3,766 | 6.866, 8.105 | 48.0 | 0 of 9 |
| ba-bpat | regression_recent | 3,781 | 4.224, 6.555 | 50.2 | 0 of 9 |
| ba-ciso | regression | 3,772 | 4.558, 7.109 | 60.2 | 0 of 9 |
| ba-cple | regression_recent | 3,769 | 10.149, 12.903 | 37.7 | 0 of 9 |
| ba-duk | regression_recent | 3,773 | 8.446, 11.467 | 43.7 | 0 of 9 |
| ba-erco | regression_recent | 3,766 | 6.866, 8.105 | 48.0 | 0 of 9 |
| ba-fpc | regression_recent | 3,705 | 8.866, 10.567 | 41.1 | 9 of 9: 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 |
| ba-fpl | regression | 3,763 | 7.333, 8.312 | 38.1 | 0 of 9 |
| ba-isne | regression_recent | 3,781 | 5.993, 8.305 | 61.6 | 0 of 9 |
| ba-miso | regression_recent | 3,780 | 4.218, 6.91 | 47.1 | 0 of 9 |
| ba-nyis | regression_recent | 3,753 | 5.324, 7.811 | 62.5 | 0 of 9 |
| ba-pace | regression_recent | 3,777 | 4.654, 6.312 | 32.2 | 5 of 9: 2018, 2020, 2021, 2022, 2023 |
| ba-pjm | regression_recent | 3,761 | 5.763, 8.63 | 48.3 | 0 of 9 |
| ba-psco | regression_recent | 3,775 | 9.433, 8.502 | 44.8 | 1 of 9: 2026 |
| ba-soco | regression_recent | 3,692 | 7.412, 9.702 | 41.5 | 0 of 9 |
| ba-swpp | regression | 3,776 | 5.863, 7.542 | 47.5 | 2 of 9: 2025, 2026 |
| ba-tva | regression_recent | 3,735 | 8.046, 10.196 | 35.8 | 0 of 9 |

What it says: as for the hours, the operator's peak is ahead year after year where its filing is sound (in 21 of the 29
places the ERW's peak beats it in no year); the exceptions are again the filing breaks of section 18 (FPC in every year,
SWPP and CENT in 2025 and 2026) and the Northwest and PACE, where the ERW's peak is ahead in most years. The ERW names the
peak's hour exactly on a third to three fifths of days (32 percent at PACE to 63 at New York). Its peak beats yesterday's
peak over the span at every place but PSCO (9.43 against 8.50 percent); Florida, the Southwest and PSCO win a year or two.

Replication (`replicate_long.py`, which now rebuilds the peak by the same words): its count is in the progress file and
landing row 12.
