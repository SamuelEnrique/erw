# Event studies: method

Energy Research Warehouse (ERW), session 47. The table `event_study_estimates` (tier derived, public) holds, for each event of the Historical Event Analyzer and each grid in it, the estimated effect of the event on:

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
| `covid_2020` | 2020-03-01 to 2020-05-31 | the same weekday 364 days earlier (728 days earlier is before the extracts start, 2018-06-30) |
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

- **Weather.** The warehouse holds no temperature for these years, so no estimate controls for it.
  - A heat wave's effect on demand is, by design, mostly the effect of heat.
  - A cold snap's effect is the cold's plus the load shed's (Uri), and the two cannot be separated here.
- **Concurrent events.**
  - COVID-19's spring 2020 also had its own weather.
  - Uri's window holds both the cold days of high demand and the days of rotating outages, when demand served fell because load was shed, not because customers wanted less.
- **Reporting changes** in EIA-930 between the baseline years and the event year.

## Results

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

## Reading the results

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
  - `site/scripts/test-eventstudy.mjs`: the TypeScript estimator against the same panel and against the Python table, all 1,077 daily and pooled estimates.
- **`site/scripts/check-values.mjs`:** recomputes every number on the pages from Supabase.
