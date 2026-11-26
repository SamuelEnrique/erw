# The ERW forecast of hourly demand (`site/data/predict/`, the page `/forecast`)

Session 10600, chain 730 (lab-desktop's second window), 26 November 2026. Code: `warehouse/predict/` (`data.py` reads the tables, `demand.py` holds the methods and the backtest, `score.py` the report card, `run.py` the daily run and the page files). Contract of the files: `docs/state/page_files_predict.md`. The ground this rests on: `docs/reviews/predict-ground-2026-11-26.md`. Tests: `tests/test_predict.py`. Replication in Stata: `replication/predict/`.

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
- **(c) regression:** for each local hour k (0 to 23), an ordinary least-squares regression of the log of the hour's demand on: a constant; the log of the same hour on day A; the log of day A's mean demand; the log of the same hour on day T-7; the log of the mean demand of the seven days ending on day A (at least five of them held); six dummies for T's day of the week (Sunday the base) and six for A's; dummies for a US federal holiday (or its observed day) on T, on A and on T-7, and for a "bridge" day (the day after Thanksgiving, 24 December, 26 to 31 December) on T, on A and on T-7; and two yearly waves of T's day of the year (the sine and cosine of 2 pi times the day over 365.25, and of 4 pi times it). 27 coefficients an hour. The regression is **refit for every target day T**, on the 730 days before it whose demand was held when T's forecast was made (target days up to A; an expanding window from the first day held until 730 are held; no fit with fewer than 300). The forecast is the exponential of the fitted value. A single missing hour inside a day (the 23-hour day of the spring clock change, or a lone gap) is taken as the mean of its two neighbours for the regressors only, never for a target or a score; the repeated autumn hour enters day A's figures as the mean of its two hours, and both of the target day's repeated hours get the hour's forecast. The coefficients are solved from the window's normal equations (`numpy.linalg.lstsq`), in a fixed order: the same tables give the same forecast to the last digit on the same machine (`tests/test_predict.py`).
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
