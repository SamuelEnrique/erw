# The Flex Alert scorecard: method

Energy Research Warehouse (ERW), session 60. The page is `/grid/caiso/alerts`; the code is `warehouse/derived/flex_alert_scorecard.py`; `notebooks/flex_alert_scorecard.ipynb` reproduces every number from the warehouse's inputs and asserts each equal to the tables `flex_alert_effects` and `flex_alert_model`. Tier: derived. License: public (EIA, NOAA, CAISO; credit the California ISO).

## 1. Question

How much did demand served in CAISO's balancing authority fall during the hours of a Flex Alert or grid emergency, relative to what the weather and the calendar predict, and what was that worth at the day-ahead price? The question is in public dispute: the state funds the alerts and the programs dispatched with them, and their load reduction is uncertain. No independent, replicable estimate across every alert day is published.

## 2. Data

| Input | ERW table | Source | Use |
|---|---|---|---|
| Alert days and hours | `caiso_grid_emergencies` | California ISO, Grid Emergencies History Report (1998 to 2025-04-30, revision 2026-07-06) | which days, which hours |
| Hourly demand | `eia930_all_demand` (the CISO workbook extract) | U.S. EIA, Form EIA-930, CISO balancing authority, sheet Published Hourly Data, column Demand | the outcome |
| Hourly weather | `noaa_isd_hourly` (SAC 72483023232, FAT 72389093193, LAX 72295023174) | NOAA NCEI Integrated Surface Database, global-hourly | temperature and dew point |
| Day-ahead prices | `caiso_dam_alert_day_hub_prices` | CAISO OASIS PRC_LMP, DAM, TH_SP15_GEN-APND and TH_NP15_GEN-APND | the value |

**Sample.** Local (Pacific) days of May to October from 2018-07-01 (the start of the EIA-930 extract) to 2025-10-31. Every hour in this window is daylight time, so a day has 24 hours.

**Demand.** EIA's hourly Demand as published, each value the hour's mean MW. It is the series `caiso_reliability_daily` and the event pages read, so the scorecard agrees with them. Hours are screened, and the screen's hours set missing, where demand is either:
- below 30 percent of the median hour; or
- more than 20 percent above or below both neighbouring hours.

This is the starter export's screen (`warehouse/exports/redivis_starter.py`); it removed 27 hours. A day enters the analysis only with all 24 hours of demand and weather.

**Weather.**
1. Each station's observations go to the nearest UTC hour, and each station-hour is the mean of its values.
2. Gaps of at most two hours are interpolated per station.
3. The three stations are weighted Los Angeles 0.50, Sacramento 0.30 and Fresno 0.20. The weights are a rounded statement of where CAISO's load lives: roughly half in Southern California (SCE and SDG&E), and half in the north, split between the Bay Area and Sacramento Valley and the Central Valley.
4. An hour is kept only when all three stations have a value.

The weather pull (session 60, approved pull a) returned 127,394 rows of its 150,000 ceiling. NCEI's 2025 data ends on 2025-08-27.

**Prices.** CAISO's OASIS serves about 39 months of history. Requests for September 2022 and earlier answered "No data returned for the specified selection" (ERR_CODE 1000) under report versions 1 and 12, while July 2023 answered with prices.

The pull (session 60, approved pull b) therefore holds 63 days, 3,024 rows of its 60,000 ceiling, from 2023-07-14 to 2025-08-24. The 160 wanted days older than that were not requested, and the table's header records them.

Of the 38 alert days, only the 4 since 2023-07 have prices.

## 3. Alert days and hours

**Alert days.** An alert day is a local day covered by an ISO-wide CAISO notice of one of these types:
- Flex Alert;
- EEA Watch;
- Energy Emergency Alert 1, 2 or 3;
- Alert, Warning, Stage 1, 2 or 3 emergency (CAISO's notices before May 2022);
- one-hour probable load interruption.

Restricted Maintenance Operations notices and transmission emergencies are not alert days: they are not calls on demand, and many are regional. They remain training days.

**Covered days.** A notice whose window spans several days covers each day with its daily clock window. The report writes time frames in five forms, all read (`window()`):
- parsed start and end;
- "MM/DD/YYYY HH:MM through MM/DD/YYYY HH:MM", with or without "at";
- "M/D/YYYY HH:MM:SS through HH:MM:SS", whose day is the text's, not the row's: the Flex Alert dated 2020-09-30 is for 2020-10-01;
- "YYYY-MM-DD HH:MM:SS through ...";
- "Month D at H:MM PM to Month D at H:MM PM".

**Alert hours.** A day's alert hours are the local hours its window covers for at least 30 minutes, with 23:59 read as midnight. The window comes from the first of these notices present that day:
1. the day's Flex Alerts;
2. else its emergency notices;
3. else its Warnings;
4. else the default, 16:00 to 21:00, labeled as assumed.

None of the 38 days needed the default.

**The result.** This gives 39 alert days from 2018-07-24 to 2024-07-24. One, 2021-07-12, lacks complete data and is left out, leaving **38 alert days and 204 alert hours**. The report ends 2025-04-30, so the 2025 season has no alert days.

## 4. The counterfactual model

**The regression.** For each local hour h (24 separate regressions), ordinary least squares on the training days:

    demand(d,h) = a_h + b1 CDH + b2 CDH^2 + b3 CDH24 + b4 CDH24^2 + b5 DEW + b6 CDH x DEW
                  + c1 Saturday + c2 Sunday + c3 holiday + sum_m month_m + sum_y year_y + e(d,h)

The terms:
- **CDH:** the cooling degree hour, max(T - 65 F, 0), of the weighted temperature in that hour.
- **CDH24:** the mean CDH over the 24 hours before (heat that builds over days).
- **DEW:** the weighted dew point.
- **Holiday:** US federal holidays.
- **Month and year effects:** month indicators with May as the base, year indicators with 2018 as the base. The year effects absorb load growth and the spread of rooftop solar behind the meter. Fitting each hour separately lets every coefficient, the day-type effects included, differ by hour.

**Training days.** The training days are the 1,276 complete non-alert days.

**Prediction.** An alert day's prediction for hour h is the model at that day's weather and calendar.

**The specification.** The prompt's minimal model was CDH, its square and the calendar. CDH24 and the dew point were added on physical grounds, and CDH24 squared and CDH x DEW because they lowered the cross-validated error on hot days (section 6).

Five specifications were named before the alert-day estimates were computed (`VARIANTS`). All five are fitted and reported, with their hot-day errors and pooled estimates, so a reader can judge the choice:
- **minimal:** CDH, CDH squared, the calendar;
- **base:** plus CDH24 and DEW;
- **base_prev24sq:** base plus CDH24 squared;
- **base_cdh_dew:** base plus CDH x DEW;
- **chosen:** base plus both.

## 5. Estimands and intervals

For alert day d with alert hours H(d):

- **reduction_mw(d):** the mean over H(d) of predicted minus actual demand (MW). Positive means demand ran below the model: a cut.
- **reduction_mwh(d):** the same, summed (MWh).
- **reduction_pct(d):** reduction_mwh over predicted MWh.
- **Pooled and yearly:** the mean over every alert hour of all days, or of one year's days, and the sum.

**Intervals: 90 percent, from 1,000 replicates** (seed 20261002). Each replicate combines:
1. **Parameter uncertainty.** A block bootstrap over calendar weeks: the training days' ISO weeks are resampled with replacement, and all 24 hourly regressions are refitted with the days weighted by their multiplicity.
2. **Prediction error.** One out-of-fold residual day per alert day: a whole 24-hour vector of actual minus predicted, from a hot non-alert day predicted by a model that did not see it (section 6), centred by hour so that it adds spread but no bias.

The interval is the 5th to 95th percentile of each estimand across replicates. The out-of-fold residuals already include parameter error, so the interval is somewhat conservative. The four robustness variants use 200 replicates each.

## 6. Out-of-sample check

Alert days are the hottest days, so the model's fit at extreme heat is the main risk to the estimate. The check:
1. The hottest tenth of training days (128 days, a weighted daily high of at least 87.0 F) is split at random into five folds.
2. Each fold is predicted by the model fitted on every other training day.
3. The error, actual less predicted, is summarised over the hours 16:00 to 21:00.

| Specification | Bias, MW | RMSE, MW | Pooled estimate, MW (90 percent) |
|---|---|---|---|
| minimal | -272.3 | 1,917.9 | -59.0 (-756.8 to 545.7) |
| base | -497.1 | 1,744.5 | 861.2 (197.2 to 1,478.8) |
| base_prev24sq | -273.0 | 1,635.2 | -460.3 (-1,189.5 to 227.7) |
| base_cdh_dew | -486.6 | 1,728.5 | 896.9 (234.0 to 1,510.5) |
| **chosen** | **-239.3** | **1,598.6** | **-503.2 (-1,274.9 to 247.4)** |

The chosen model's mean absolute percentage error on these days is 3.18 percent; in sample, over the same hours of every training day, its RMSE is 1,353.1 MW.

Two facts frame every result:
- **The model over-predicts hot days by 239 MW on average.** On an alert day, that error would read as a 239 MW cut.
- **The answer turns on the specification.** The two specifications that lack CDH24 squared over-predict hot days most (bias near -490 MW) and give a positive pooled estimate. The three that are best on hot days give a pooled estimate near zero or negative.

Alert days are hotter still: 34 of the 38 are at least as hot as the threshold, and three (2020-09-06, 2022-09-08 and 2022-09-09) are hotter than every training day. On those days the model extrapolates.

## 7. Value

**Formula.** Value(d) is the sum over the alert hours of reduction_mw(d,h) times the hour's day-ahead price, the mean of SP15 and NP15; an hour counts only with both hubs. Value is computed in each bootstrap replicate for its interval.

**What it means.** It is a **wholesale lower bound**: what the energy would have cost at prices set the day before. The value of avoided scarcity, of reserves kept and of outages not taken is larger and is not estimated. A negative value means demand ran above the model in hours with a price.

## 8. Results (run of 2026-10-02)

**Pooled.** Over 38 days and 204 alert hours, demand served was **above** the model's prediction by 503.2 MW on average: a pooled reduction of -503.2 MW, with a 90 percent interval of -1,274.9 to 247.4. That is -1.2 percent of predicted demand, -102,650 MWh in all.
- The interval includes zero.
- Netting the model's hot-day bias moves it further from a cut: -742.5 MW.

**By year.** No year shows a cut whose interval excludes zero. 2023 (three EEA Watch and EEA 1 evenings) and 2024 (one) show demand above the model.

**By day.** The largest estimated cuts are 2022-09-09 (4,379.7 MW, interval 1,122.4 to 7,742.5), 2020-09-07, 2021-07-09, 2022-09-08 and 2020-08-16. The two September 2022 days are hotter than any training day. On 2022-09-09 the remnants of Tropical Storm Kay brought clouds and rain to Southern California, which three airport stations need not register; the large estimate that day is more likely weather the model does not see than conservation.

**Value.** Prices exist for the 19 alert hours of four days (2023-07-20, 2023-07-25, 2023-07-26, 2024-07-24). On those days demand ran above the model, so the value is negative: USD -5.47 million (-8.04 to -2.60 million). The day-ahead price in the evening hours of the hottest non-alert days with a price averaged USD 137.07/MWh.

## 9. What the estimate can and cannot say

- **It is the combined demand-side effect of an alert day.** On alert days, the following move demand together, and the scorecard cannot separate them:
  - the Flex Alert's request;
  - paid programs: the Demand Side Grid Support program (DSGS) and the Emergency Load Reduction Program (ELRP);
  - the utilities' demand response, and the state's emergency text alerts;
  - rotating outages (2020-08-14 and 2020-08-15).
- **The fit at extreme heat is the main risk.** The out-of-sample check is on days up to the training data's hottest. Alert days are hotter, and three are outside the training range. A model that bends the wrong way at extreme heat produces a spurious cut, or hides a real one. The specification table shows how much the answer moves.
- **Hourly data blurs short responses.** A 20-minute drop after an emergency text is diluted in its hour.
- **Weather from three airports is coarse.** Coastal fog, tropical moisture and wildfire smoke can move load without moving the airports' readings.
- **The value covers four days.** OASIS's 39-month history means none of the 2020 or 2022 heat waves is valued.

## 10. Reproducing it

The pipeline, in order:

    python warehouse/connectors/noaa_isd.py --seasons          # weather (resumable; under the data lock)
    python warehouse/connectors/caiso_alert_prices.py          # prices (resumable; under the data lock)
    python warehouse/derived/flex_alert_scorecard.py           # the two tables (under the data lock)
    python -m unittest tests.test_session60                    # a synthetic panel's known effect is recovered

Then run `notebooks/flex_alert_scorecard.ipynb`. It re-implements the panel, the 24 regressions, the per-day, yearly and pooled estimates, the five-fold check for all five variants and the value. It asserts each equal to the tables, and re-runs the bootstrap with the published seed to reproduce the intervals.
