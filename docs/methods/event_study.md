# Event studies: method

Energy Research Warehouse (ERW), session 47; session 49 restored COVID-19's second baseline year and added a temperature-controlled estimate and a linear-trend robustness row. The table `event_study_estimates` (tier derived, public) holds, for each event of the Historical Event Analyzer and each grid in it, the estimated effect of the event on:

- the grid's daily demand served;
- for ERCOT, its daily mean real-time hub price.

How it is built and checked:

- **The table:** built by `warehouse/derived/event_study.py` from `event_window_daily` (the events method, `docs/methods/events.md`).
- **The pages:** each `/events` page computes the same estimates with `site/lib/eventstudy.ts`, a second implementation held equal to the first by a test.
- **Replication:** the notebook `notebooks/event_study.ipynb` reproduces every estimate on the pages from the `erw` package.

## Data

- **Unit of observation:** a grid's local operating day (`event_window_daily`, `freq` P1D). Daily rows only; the weekly rows of COVID-19 are not used.
- **Outcomes:**
  - `demand_mwh`: the day's demand served (the sum of EIA-930's hourly demand), MWh.
  - `rt_mean`: the day's mean of ERCOT's 15-minute real-time price at the hub average (HB_HUBAVG), USD/MWh.
- **Event days:** the days of the event window, local dates inclusive:

| Event | Window | Baseline days |
|---|---|---|
| `uri_2021` | 2021-02-07 to 2021-02-24 | the same calendar days of 2019 and 2020 |
| `covid_2020` | 2020-03-01 to 2020-05-31 | the same weekday 364 and 728 days earlier (session 49: the 728-day baseline, 2018-03-04 to 2018-06-03, comes from EIA's six-month file in `eia930_all_history`; the Lower 48 is not in that file and keeps 364 only) |
| `caiso_heat_2020` | 2020-08-10 to 2020-08-24 | the same weekday 364 and 728 days earlier |
| `elliott_2022` | 2022-12-19 to 2022-12-29 | the same weekday 364 and 728 days earlier |
| `ercot_heat_2023` | 2023-08-01 to 2023-09-10 | the same weekday 364 and 728 days earlier |

- **Hourly profile:** demand from the EIA-930 hourly extracts the event builder read (`warehouse/raw/eia930_emissions/<run>/<ba>_hours.csv`), on the same days, by local hour.

## Specification (`dow_year_mean_v1`)

For one event, grid and outcome, over the event days and the baseline days:

y_d = a + sum over event days k of b_k 1[d = k] + sum over weekdays w of g_w 1[weekday(d) = w] + sum over baseline years t of c_t z_t(d) + e_d

- **Day of the week:** Monday is the reference; six indicators.
- **Year effects:** coded to sum to zero over the baseline years, z_t(d) = 1[year(d) = t] - 1[year(d) = T] for the last baseline year T. The event year takes none.
  - The intercept and the weekday effects describe the average baseline year, and the event year's counterfactual is that average.
  - With one baseline year (COVID-19) there is no year contrast, and the counterfactual is that year.
- **Each event day's effect b_k:** the day's value less its counterfactual, which is the fit of the baseline days alone evaluated at that day. This is exactly the coefficient of the day's indicator in the full regression.
- **The pooled effect:** one indicator for every event day, in place of the day indicators, in the same regression. It is a weekday-weighted mean of the day effects, MWh (or USD/MWh) per day.
- **`counterfactual_mean`:** the mean counterfactual over the event days. The pages give the pooled effect as a percent of it.

## Temperature-controlled specification (`dow_year_temp_v1`, session 49)

The same regression with four more terms: the grid's heating and cooling degree days that day and their squares,

y_d = ... (as above) + h1 HDD_d + h2 HDD_d^2 + k1 CDD_d + k2 CDD_d^2 + e_d

- **Degree days:** per station and local day in `event_window_daily` (entity `noaa:<station>`), from NOAA ISD's hourly temperatures (`noaa_isd_hourly`): the day's mean is (max + min) / 2, the National Weather Service's convention; HDD = max(0, 65 - mean), CDD = max(0, mean - 65), degF-day. A station-day needs at least 20 clock hours with a reading.
- **The grid's value:** the mean over its stations that day (ERCOT DFW and IAH, CAISO SAC and LAX, PJM PHL and ORD where held; MISO MSP, NYISO JFK, ISO-NE BOS, SPP OKC). The ERCOT hub price uses ERCOT's stations.
- **Days without weather** are left out of this specification only. The Lower 48 has no station: no temperature-controlled estimate.
- **Variables:** `<outcome>_effect_day_temp`, `<outcome>_effect_pooled_temp`, `<outcome>_counterfactual_mean_temp`, `x_spec` `dow_year_temp_v1`.
- **Dependent columns** (a degree-day term that is zero on every day, such as HDD in an August window): both estimators drop a column whose part not explained by the columns before it is below 1e-9 of its length (greedy Gram-Schmidt), in the same order in Python, TypeScript and the notebook.
- **What the pages say:** each `/events` page gives both pooled estimates for the lead grid. When the two have the same sign and the temperature-controlled one is no larger in size, the page says the weather terms account for 1 - (controlled / original) of the original, in percent. Otherwise it says no share can be put down to weather, and gives no percent.

## Linear-trend robustness row (`dow_trend_v1`, session 49)

The original specification with a linear trend in days in place of the year effects (`<outcome>_effect_pooled_trend`, pooled only). With two baseline years the trend line runs through them and is extrapolated to the event year, so growth between the baseline years is carried forward rather than averaged. With one baseline year there is no trend to fit and no row.

## Inference

- **Robust covariance:** heteroskedasticity-robust (HC1), (X'X)^-1 X' diag(e^2) X (X'X)^-1 times n / (n - k).
- **A single day's effect:** its standard error is sqrt(s2 + x'Vx).
  - s2 is the residual variance of the baseline fit: the day's own noise.
  - x'Vx is the HC1 variance of the fitted counterfactual.
  - A one-day indicator's residual is zero, so a robust covariance of the full regression would leave the day's own noise out and understate the error.
- **The pooled effect:** the HC1 standard error of its coefficient.
- **Intervals:** 95 percent, estimate plus or minus 1.96 standard errors (normal). The baseline samples are small (22 days for Elliott, 92 for COVID-19), so a t interval would be somewhat wider.

## Identification and what it assumes

The estimate is the event days' departure from what the same days of earlier years, aligned by weekday, predict. It reads as the effect of the event under these assumptions:

1. **No trend:** absent the event, the event year would have looked like the average baseline year.
   - Demand grows: ERCOT's grew several percent a year between 2021 and 2023, and growth since the baseline years is counted as effect.
   - This matters most for ERCOT's summer 2023 heat, whose baselines are 2021 and 2022, and for Elliott.
2. **The weekday pattern** is the same in the event year and the baseline years.
3. **Nothing else** moved the outcome on the event days that did not on the baseline days.

**What it cannot rule out:**

- **Weather, in the original specification.** It does not control for temperature. A heat wave's effect on demand is then mostly the effect of heat; a cold snap's is the cold's plus the load shed's (Uri). Session 49's `dow_year_temp_v1` controls for degree days at one or two airports per grid, which is a partial control: humidity, wind, cloud and the weather away from those airports are not in it, and a quadratic in degree days is a fixed shape that need not fit an extreme day (Uri's cold was beyond any baseline day's).
- **Concurrent events.**
  - COVID-19's spring 2020 also had its own weather.
  - Uri's window holds both the cold days of high demand and the days of rotating outages, when demand served fell because load was shed, not because customers wanted less.
- **Reporting changes** in EIA-930 between the baseline years and the event year.

## Results, session 49

Run 20261001T041542Z of `warehouse/derived/event_study.py`: pooled effects per day of the window, the original specification beside the temperature-controlled one and the trend row. Weather share: 1 - (controlled / original), in percent, given only when the two share a sign and the controlled estimate is no larger in size.

**covid_2020**

| Grid | Outcome | Pooled effect | 95 percent interval | Days | Controlling for temperature | 95 percent interval | Days | Weather share, percent | Linear trend in place of year effects |
|---|---|---|---|---|---|---|---|---|---|
| CAISO | demand served, MWh a day | -11,271.57 | -21,302.65 to -1,240.50 | 275 | -20,589.34 | -27,828.67 to -13,350.02 | 275 | none (see text) | 67,251.62 (49,030.61 to 85,472.62) |
| ERCOT | demand served, MWh a day | -9,454.21 | -34,623.53 to 15,715.12 | 276 | 11,029.02 | -1,102.22 to 23,160.26 | 276 | none (see text) | -3,982.73 (-62,365.99 to 54,400.53) |
| ISO-NE | demand served, MWh a day | -23,722.18 | -29,321.30 to -18,123.07 | 276 | -22,762.58 | -26,401.55 to -19,123.60 | 276 | 4.0 | -4,094.13 (-15,190.55 to 7,002.29) |
| MISO | demand served, MWh a day | -164,977.94 | -190,297.43 to -139,658.44 | 275 | -134,647.68 | -154,769.24 to -114,526.13 | 275 | 18.4 | -58,147.43 (-111,695.93 to -4,598.93) |
| NYISO | demand served, MWh a day | -38,087.78 | -44,059.31 to -32,116.25 | 276 | -28,931.15 | -33,493.90 to -24,368.41 | 276 | 24.0 | -12,054.76 (-24,433.22 to 323.70) |
| PJM | demand served, MWh a day | -203,166.44 | -240,235.80 to -166,097.08 | 275 | -136,185.56 | -160,229.24 to -112,141.88 | 275 | 33.0 | -70,303.07 (-155,360.13 to 14,753.98) |
| SPP | demand served, MWh a day | -49,681.74 | -60,506.76 to -38,856.72 | 276 | -36,514.78 | -44,684.78 to -28,344.78 | 276 | 26.5 | -9,776.20 (-36,026.55 to 16,474.16) |
| Lower 48 | demand served, MWh a day | -606,600.64 | -767,512.43 to -445,688.85 | 184 | no station |  |  |  | one baseline year: none |
| ERCOT hub average | real-time price, USD/MWh | -4.33 | -7.50 to -1.16 | 276 | -3.71 | -6.77 to -0.66 | 276 | 14.3 | -7.29 (-12.95 to -1.63) |

**caiso_heat_2020**

| Grid | Outcome | Pooled effect | 95 percent interval | Days | Controlling for temperature | 95 percent interval | Days | Weather share, percent | Linear trend in place of year effects |
|---|---|---|---|---|---|---|---|---|---|
| CAISO | demand served, MWh a day | 83,812.35 | 46,905.66 to 120,719.05 | 42 | 24,746.88 | 900.28 to 48,593.49 | 42 | 70.5 | 117,003.23 (55,974.28 to 178,032.18) |

**uri_2021**

| Grid | Outcome | Pooled effect | 95 percent interval | Days | Controlling for temperature | 95 percent interval | Days | Weather share, percent | Linear trend in place of year effects |
|---|---|---|---|---|---|---|---|---|---|
| ERCOT | demand served, MWh a day | 155,794.96 | 53,420.68 to 258,169.25 | 54 | 30,283.66 | -28,962.93 to 89,530.26 | 54 | 80.6 | 140,869.61 (14,593.93 to 267,145.29) |
| ERCOT hub average | real-time price, USD/MWh | 2,293.84 | 686.08 to 3,901.61 | 54 | 287.79 | -559.80 to 1,135.37 | 54 | 87.5 | 2,243.58 (621.23 to 3,865.93) |

**elliott_2022**

| Grid | Outcome | Pooled effect | 95 percent interval | Days | Controlling for temperature | 95 percent interval | Days | Weather share, percent | Linear trend in place of year effects |
|---|---|---|---|---|---|---|---|---|---|
| ERCOT | demand served, MWh a day | 269,581.50 | 156,948.75 to 382,214.25 | 33 | 72,488.32 | 31,733.94 to 113,242.69 | 33 | 73.1 | 245,939.45 (91,343.03 to 400,535.88) |
| ISO-NE | demand served, MWh a day | 10,549.09 | 1,185.42 to 19,912.76 | 33 | 3,906.75 | -1,810.53 to 9,624.02 | 33 | 63.0 | -2,989.36 (-24,100.36 to 18,121.63) |
| MISO | demand served, MWh a day | 236,278.71 | 115,485.54 to 357,071.88 | 32 | 125,412.58 | 32,144.02 to 218,681.14 | 32 | 46.9 | 269,046.57 (33,680.69 to 504,412.44) |
| NYISO | demand served, MWh a day | 24,802.64 | 12,282.81 to 37,322.47 | 33 | 5,921.22 | -3,788.41 to 15,630.85 | 33 | 76.1 | 26,279.73 (-228.99 to 52,788.45) |
| PJM | demand served, MWh a day | 386,999.95 | 256,963.62 to 517,036.28 | 33 | 134,170.93 | 24,428.52 to 243,913.35 | 33 | 65.3 | 560,037.91 (242,263.53 to 877,812.29) |
| SPP | demand served, MWh a day | 146,160.91 | 80,505.19 to 211,816.63 | 33 | 46,809.05 | 20,370.41 to 73,247.70 | 33 | 68.0 | 179,503.45 (83,393.97 to 275,612.94) |
| ERCOT hub average | real-time price, USD/MWh | 56.52 | -19.85 to 132.89 | 33 | -28.14 | -61.31 to 5.03 | 33 | none (see text) | 41.13 (-70.05 to 152.31) |

**ercot_heat_2023**

| Grid | Outcome | Pooled effect | 95 percent interval | Days | Controlling for temperature | 95 percent interval | Days | Weather share, percent | Linear trend in place of year effects |
|---|---|---|---|---|---|---|---|---|---|
| ERCOT | demand served, MWh a day | 271,284.09 | 239,602.57 to 302,965.60 | 123 | 133,742.58 | 113,031.52 to 154,453.64 | 123 | 50.7 | 242,062.95 (170,102.33 to 314,023.58) |
| ERCOT hub average | real-time price, USD/MWh | 128.68 | 65.61 to 191.74 | 123 | 78.18 | 7.02 to 149.35 | 123 | 39.2 | 55.00 (-13.91 to 123.91) |

**What the numbers show** (session 49):

- **Heat waves and cold snaps:** for every demand estimate of CAISO's 2020 heat, Uri, Elliott and ERCOT's 2023 heat, the temperature-controlled estimate is smaller than the original, by 47 to 81 percent. CAISO's 2020 heat, Elliott's in ERCOT, MISO, PJM and SPP, and ERCOT's 2023 heat keep intervals that exclude zero; Uri's, and Elliott's in ISO-NE and NYISO, include zero once temperature is controlled.
- **ERCOT's hub price:** Uri's estimate falls from 2,293.84 to 287.79 USD/MWh and its interval then includes zero; ERCOT 2023's falls from 128.68 to 78.18 and still excludes zero; Elliott's changes sign, and both of its intervals include zero.
- **COVID-19:** with the 2018 baseline restored, the original estimates are negative in every grid, ERCOT's interval including zero. Controlling for temperature makes them smaller in MISO, NYISO, PJM, SPP and ISO-NE (by 4 to 33 percent) and larger in CAISO; ERCOT's turns positive, with an interval that includes zero.
- **The trend row** moves some estimates far from both others (CAISO's COVID-19 estimate turns positive, PJM's Elliott estimate grows): with two baseline years a linear trend is two points extrapolated, so it is a check on the assumption of no trend, not a better estimate.

## Results of session 47 (before the 2018 baseline and the weather terms)

Run 20260930T234948Z of `warehouse/derived/event_study.py`: pooled effects per day of the window. The full table in `event_study_estimates` also holds each event day's effect and the hour-of-day profiles.

**covid_2020**

| Grid | Outcome | Pooled effect | 95 percent interval | Percent of expected | Days |
|---|---|---|---|---|---|
| CAISO | demand served, MWh a day | 14,920.51 | 3,097.78 to 26,743.24 | 2.92 | 183 |
| ERCOT | demand served, MWh a day | -7,630.38 | -36,976.45 to 21,715.68 | -0.81 | 184 |
| ISO-NE | demand served, MWh a day | -17,179.50 | -23,705.52 to -10,653.48 | -5.91 | 184 |
| MISO | demand served, MWh a day | -129,298.35 | -157,955.03 to -100,641.67 | -7.90 | 183 |
| NYISO | demand served, MWh a day | -29,410.11 | -36,417.16 to -22,403.05 | -7.66 | 184 |
| PJM | demand served, MWh a day | -158,685.97 | -204,987.37 to -112,384.56 | -7.97 | 183 |
| SPP | demand served, MWh a day | -36,379.89 | -49,293.60 to -23,466.18 | -5.55 | 184 |
| Lower 48 | demand served, MWh a day | -606,600.64 | -767,512.43 to -445,688.85 | -6.06 | 184 |
| ERCOT hub average | real-time price, USD/MWh | -5.32 | -8.77 to -1.87 | -21.28 | 184 |

**caiso_heat_2020**

| Grid | Outcome | Pooled effect | 95 percent interval | Percent of expected | Days |
|---|---|---|---|---|---|
| CAISO | demand served, MWh a day | 83,812.35 | 46,905.66 to 120,719.05 | 11.47 | 42 |

**uri_2021**

| Grid | Outcome | Pooled effect | 95 percent interval | Percent of expected | Days |
|---|---|---|---|---|---|
| ERCOT | demand served, MWh a day | 155,794.96 | 53,420.68 to 258,169.25 | 16.24 | 54 |
| ERCOT hub average | real-time price, USD/MWh | 2,293.84 | 686.08 to 3,901.61 | 9,850.47 | 54 |

**elliott_2022**

| Grid | Outcome | Pooled effect | 95 percent interval | Percent of expected | Days |
|---|---|---|---|---|---|
| ERCOT | demand served, MWh a day | 269,581.50 | 156,948.75 to 382,214.25 | 28.31 | 33 |
| ISO-NE | demand served, MWh a day | 10,549.09 | 1,185.42 to 19,912.76 | 3.14 | 33 |
| MISO | demand served, MWh a day | 236,278.71 | 115,485.54 to 357,071.88 | 13.74 | 32 |
| NYISO | demand served, MWh a day | 24,802.64 | 12,282.81 to 37,322.47 | 5.99 | 33 |
| PJM | demand served, MWh a day | 386,999.95 | 256,963.62 to 517,036.28 | 17.73 | 33 |
| SPP | demand served, MWh a day | 146,160.91 | 80,505.19 to 211,816.63 | 20.90 | 33 |
| ERCOT hub average | real-time price, USD/MWh | 56.52 | -19.85 to 132.89 | 264.66 | 33 |

**ercot_heat_2023**

| Grid | Outcome | Pooled effect | 95 percent interval | Percent of expected | Days |
|---|---|---|---|---|---|
| ERCOT | demand served, MWh a day | 271,284.09 | 239,602.57 to 302,965.60 | 20.33 | 123 |
| ERCOT hub average | real-time price, USD/MWh | 128.68 | 65.61 to 191.74 | 208.43 | 123 |

**Hour-of-day profiles** (pooled effect at each local hour, MW, `demand_mw_effect_hHH`):

- **COVID-19:** the fall in demand was deepest in the morning, 07:00 to 10:00 local time for most grids (US48 at 08:00, -34,359 MW).
- **Elliott:** the rise was largest at 04:00 to 07:00, the cold morning peak (PJM 18,963 MW at 07:00).
- **ERCOT's 2023 heat:** the effect peaked at 18:00 (13,873 MW).
- **Uri:** the effect was largest at night (03:00, 8,141 MW) and smallest at 19:00.

These profiles come from the hourly extracts, which are raw files, not warehouse tables. The notebook cannot fetch them through the `erw` package, and the pages do not show them.

## Reading the results (session 47)

- **COVID-19:** daily demand fell in every grid but ERCOT and CAISO, by 5.5 to 8 percent.
  - ERCOT's interval includes zero.
  - CAISO's estimate is positive, a reminder that one baseline year carries that year's weather.
- **Every winter storm and heat wave:** demand served rose, with intervals that exclude zero. The exception is ERCOT's hub price during Elliott, whose interval includes zero.
- **How to read the sizes:** these effects include the weather and the growth since the baseline years. Read them as upper bounds on what the event did beyond them, not as the event alone.

## Replication

- **Tables:** `event_study_estimates`, from `event_window_daily`; both are public.
- **The notebook:** [`notebooks/event_study.ipynb`](https://github.com/SamuelEnrique/erw/blob/main/notebooks/event_study.ipynb) fetches `event_window_daily` with `erw.fetch` and reproduces every pooled and daily estimate on the pages, and the table's.
- **Tests:**
  - `tests/test_session47.py`: the estimator against a synthetic panel with a known effect, and the windows against `event_window.py`.
  - `site/scripts/test-eventstudy.mjs`: the TypeScript estimator against the same panel and against the Python table, all 1,077 daily and pooled estimates (session 49: 2,060, the temperature-controlled ones included, 0 mismatched).
  - The notebook reproduces both specifications (relative tolerance 1e-6).
- **`site/scripts/check-values.mjs`:** recomputes every number on the pages from Supabase.
