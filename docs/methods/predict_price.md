# The ERW forecast of day-ahead hub prices (`site/data/predict/`, the page `/forecast`)

Session 10600, chain 730 (lab-desktop's second window, part E), 26 November 2026. Code: `warehouse/predict/predict_price.py` (the methods and the backtest), with `predict_data.py`, `predict_score.py` and `run.py` shared with the demand forecast (`docs/methods/predict.md`, whose rules on the backtest, the choice, the band and the scores hold here unless this note says otherwise). Contract of the files: `docs/state/page_files_predict.md`. Tests: `tests/test_predict.py`.

**Correction of the same session (26 November 2026, about 12:00 UTC).** The first version of this note, pushed at about 11:46 UTC, forecast and scored ISO-NE's and NYISO's hubs too, reading the `license` column of `coverage.csv` (public) instead of the per-publisher record (`license_verdicts.csv`: written permission needed). They are held now: no number of theirs is in this note or in any file, the 96 forecast rows already written for them were taken out of the price ledger before anything landed, and the branch that carried them was replaced (`wip/c730-predict-v2`).

**What it is.** The ERW's own forecast of tomorrow's day-ahead price at one hub of each grid whose hub prices the warehouse holds under a public license, hour by hour, with a band, and its report card. Tier `derived`: a model's output, never a published or official figure, and no advice. No operator publishes a forecast of its own day-ahead price, so there is no "operator" line here; the yardsticks are yesterday's price and last week's.

## 1. The grids and their hubs

| Grid | Hub forecast | Shown for | Held from | Why this hub |
|---|---|---|---|---|
| ERCOT | HB_NORTH | TEX, ERCO | 2015-01-01 | the hub most quoted for ERCOT; the six hubs are held |
| SPP | SPPNORTH_HUB | CENT, SWPP | 2018-07-01 | the only SPP hub held before 26 August 2026 |
| CAISO | TH_SP15_GEN-APND (SP15) | CAL, CISO | 2023-07-06 | Southern California's trading hub, the larger load |

The three grids' prices "may be public" by their publishers' terms (`warehouse/metadata/license_verdicts.csv`). Not forecast, with the reason in every file: ISO-NE and NYISO (their terms ask for written permission, which the ERW has not recorded; `iso_hub_prices_history` is "license needed" since 21 October 2026 in `warehouse/metadata/license_status.csv`; the forecast reads none of their rows), MISO (paused since 4 October 2026: MISO's terms forbid automated access, `warehouse/metadata/paused_sources.csv`; no price after that day can be used or scored), PJM (its prices need a paid data license, `docs/licenses.md`; none is held), and every place with no organised day-ahead market whose hub prices the warehouse holds (CAR, FLA, NW, SE, SW, TEN and their authorities).

## 2. What was known when

The forecast for day T is taken as made at **14:00 UTC on day T-1**, before any of these grids publishes its day-ahead prices for T (the tables' `vintage` puts ERCOT's at about 11.4 hours and ISO-NE's at about 11.1 hours before the day begins, that is about 17:00 UTC or later on T-1; NYISO's and CAISO's tables hold no publication time that can be read, and 14:00 UTC is taken as early enough for them on the same day-ahead timetable, a reading written here and not checked against their sites tonight). Whatever the hour, the method never reads day T's price: it reads prices through T-1 only (`tests/test_predict.py` changes every later price and finds the forecast unmoved). At 14:00 UTC on T-1:

- the hub's day-ahead prices are known **through day T-1** (published on T-2);
- the place's demand is known **through 23:00 local on day T-3** (EIA's six-month files of T-2);
- Henry Hub is read as the latest price dated **at least ten days before T-1** (EIA publishes daily spot prices weekly; the table's last day was nine days before this was written).

The wind and solar forecasts the warehouse holds are not used. CAISO's day-ahead wind and solar forecasts (`caiso_wind_solar_forecast`, from June 2023) carry no publication time, so it cannot be shown that they were out before 14:00 UTC on T-1; ERCOT's (`ercot_wind_solar_forecast`) begin on 30 September 2026, too short to fit. Using either would risk knowing something early. A data request asks for their publication times (`docs/state/data_requests_predict.md`, row 5).

## 3. The methods

- **(a) yesterday:** the same local hour's day-ahead price on day T-1, already published.
- **(b) week_ago:** the same local hour on day T-7.
- **(c) regression:** for each local hour, ordinary least squares in USD/MWh (not logs: prices fall below zero) on: a constant; the same hour's price on T-1; T-1's mean price; the same hour's price on T-7; the mean price of the seven days ending on T-1 (at least five held); the ERW's own demand forecast for the hour (the demand regression of `docs/methods/predict.md`, made with demand through T-3) over the mean demand of the seven days ending on T-3, and that ratio squared (prices rise faster than demand near the top of the supply curve); Henry Hub as above; six weekday dummies; holiday and bridge dummies for T; one yearly wave (sine and cosine of T's day of the year). 18 coefficients an hour, refit for every day T on the 730 days before it whose price was held when T's forecast was made (no fit with fewer than 300). A lone missing hour inside a day is the mean of its neighbours, for the regressors only.

The band is the forecast plus the 10th and 90th percentile of the method's own out-of-sample errors (actual less forecast, USD/MWh) at the same local hour over the 365 days held when the forecast is made.

## 4. The backtest, the choice and the scores

Walking forward a day at a time to 25 November 2026, from the first day each method can be made: the regression needs 300 days of its own inputs, so its backtest begins on 5 March 2020 for ERCOT (the demand regression it reads begins in July 2019), 4 March 2020 for SPP and 10 May 2024 for CAISO. All methods of a grid are scored on the same hours (where the actual price and every method's forecast are held). The choice is the demand forecast's rule: the lowest mean absolute error over the last two years. The percent error counts only hours whose actual price is at least 5 USD/MWh in size. **Spikes are scored apart:** the hours above the grid's own 99th percentile of the backtest's actual prices (cut `spike`).

**The last two years (built 26 November 2026 at 11:37 UTC; `runs/c730/table_price.py` prints it from `scores.json`):**

| Grid (place) | Hub | Chosen | Hours (2 years) | ERW MAE | Yesterday's price MAE | Week-ago MAE | Regression MAE | ERW MAPE % | Spike hours (whole backtest) | ERW MAE, spikes | Yesterday MAE, spikes | Regression MAE, spikes |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ERCOT (TEX) | HB_NORTH | yesterday | 17,348 | 13.07 | 13.07 | 17.33 | 16.23 | 33.6 | 588 | 1027.9 | 1027.9 | 1479.8 |
| SPP (CENT) | SPPNORTH_HUB | regression | 17,153 | 14.52 | 16.54 | 21.37 | 14.52 | 57.1 | 480 | 1331.9 | 416.5 | 1331.9 |
| CAISO (CAL) | SP15 | regression | 17,468 | 5.91 | 6.20 | 10.41 | 5.91 | 23.4 | 223 | 40.9 | 46.5 | 40.9 |

MAE in USD/MWh. The authorities' rows (ERCO, SWPP, CISO) are the same hubs and differ only where their demand forecast differs from the region's (SWPP's regression 14.54 against CENT's 14.52).

What the table says, plainly:

- **The regression is barely better than yesterday's price, where it is better at all.** It wins in CAISO (5.91 against 6.20) and SPP (14.52 against 16.54); it loses in ERCOT, where the page shows yesterday's price as the ERW forecast. A day-ahead price is mostly yesterday's price plus what tomorrow's weather and outages will do, and the ERW reads neither weather nor outages.
- **On spikes the ERW forecast is poor and says so.** In SPP the regression misses its spike hours by 1,332 USD/MWh on average against yesterday's 417 (the February 2021 storm dominates); in ERCOT a spike hour is missed by about 1,000 USD/MWh by every method. No method here sees a spike coming.
- **The percent errors are large** (23 to 57 percent) because day-ahead prices are often low and volatile; the MAE is the measure to read.
- The band holds about eight hours in ten (ERCOT 77.9 percent of the last two years' hours, SPP 78.0, CAISO 78.7), but it is wide where prices jump, and a spike falls outside it.

## 5. The files

The price is `series.price` of each place's file, with `hub`, `market` (`day-ahead`), `horizon_days` (the days between the last whole day of prices read and the target day: 1 in the backtest, 2 for the first live forecast, made at 11:00 UTC on 26 November when the warehouse held prices through 25 November) and `demand_horizon_days` (3). `operator` is `null` throughout and `operator_held` says why. Every forecast as made is appended to `site/data/predict/ledger_price.csv`, never rewritten (the one exception is the correction at the head of this note: rows for held places that should never have been written); the first rows are for 27 November, six places (TEX, ERCO, CENT, SWPP, CAL, CISO).

## 6. Tried and not built (session 10601)

A price regression with more of the latest days' shape (the same hour two days before, and the latest day's highest and lowest hourly prices; `runs/c730/trial_price2.py`), over the last two years: ERCOT 17.51 USD/MWh against the regression's 16.25 and yesterday's price 13.07 (worse: the latest day's highest price carries a spike into the next day); SPP 14.22 against 14.64; CAISO 5.82 against 5.91. Gains of 3 and 1.5 percent where it helps and a loss where the ERW already trails yesterday's price: it is not added as a candidate.

## 7. The real-time price (session 10602)

Samuel's order of 27 November 2026. Code: `warehouse/predict/predict_rt.py` and `warehouse/predict/rt_price.py`
(the daily run, `site/data/predict/rt_price.json` and `ledger_rt_price.csv`, never rewritten). The same three hubs
(ERCOT HB_NORTH, SPP North Hub, CAISO SP15; ISO-NE's, NYISO's, PJM's and MISO's stay held as above). The real-time
price of an hour is the mean of its four fifteen-minute prices (markets `*_rtm` of the price tables), held only when
all four are.

**When it is made.** At 22:00 UTC the day before the target local day: after the three day-ahead markets publish
their prices for the day on their ordinary timelines (ERCOT about 19:30 UTC, SPP about 19:00 to 20:00, CAISO about
20:00 to 21:00), with real-time prices read through two days before (h = 2). A day a market published late is not
detected: the timeline is the market's own. A test holds that a later real-time price, or a day-ahead price of a later
day, moves nothing. The warehouse's daily run (14:00 UTC) does not yet hold the next day's day-ahead prices, so the
run must follow the evening price refresh; until then the file says, for tomorrow, that the day-ahead price is not held.

**The methods.** `day_ahead`: the hub's day-ahead price for the hour, the market's own forecast of the real-time price,
the comparator as the operator's forecast is for demand, never an ERW method. `yesterday`: the real-time price of the
same hour two days before. `regression`: least squares by local hour on the day-ahead price for the hour, the
real-time less day-ahead price at the hour two days before, and its mean over the seven days to then; refit for every
target day on the 730 days before it (at least 300). The choice, the band (additive, in USD/MWh) and the scores (MAPE
over hours of at least 5 USD/MWh in size, the spike cut above the hub's 99th percentile) are as above.

The scores, from the first full build (27 November 2026; `runs/c730/table_ws.py`), the last two years:

| Hub | Method | MAE USD/MWh: ERW, day-ahead price, yesterday | MAPE %: ERW, day-ahead price | Spike hours (above the 99th percentile): hours, ERW, day-ahead price MAE | Band inside % |
|---|---|---|---|---|---:|
| ERCOT HB_NORTH | regression | 12.33, 11.83, 19.72 | 33.88, 30.85 | 649: 1,969.9, 989.0 | 77.5 |
| SPP North Hub | regression | 17.63, 17.92, 29.85 | 57.53, 59.43 | 541: 393.0, 431.0 | 77.1 |
| CAISO SP15 | regression | 8.17, 7.83, 13.74 | 29.91, 28.28 | 224: 95.0, 93.0 | 77.5 |

The market's own day-ahead price is the better forecast of the real-time price at ERCOT and CAISO; the ERW's is a little
better at SPP. On ERCOT's spike hours the ERW's regression is twice as far off as the day-ahead price: it carries the
latest real-time spread into the next day. Replication (`replication/predict/replicate_rt.py`): 1,120 of 1,120 figures
equal.

## 8. The real-time price over a longer backtest (session 10603)

Samuel's order of 27 November 2026 ("longer backtests and more places"). The day-ahead price forecast of sections 1 to 4
reads the place's demand, which the warehouse holds from 1 July 2018 only, so its backtest cannot start earlier than it
does. The real-time forecast of section 7 reads only the hub's own prices, and ERCOT's are held from January 2015
(`ercot_all_hub_prices_history`): its walk can run from 1 January 2016, the first day after the regression's 300 days.
SPP's prices are held from July 2018 and CAISO's real-time prices from 2023, so their longer backtest starts where the
backtest of section 7 does.

`rt_price.json` gains, for each hub, `long_backtest`: the same walk forward from 1 January 2016 (nothing known early: the
walk is the one of section 7, only scored from an earlier day), scored over the whole span (`all`) and by the calendar
year of the target day (`by_year`), on the hours every method and the day-ahead price hold, with the share of hours
inside the band. The ERW's method in every year is the one chosen now on the last two years: the earlier years test
that choice, they do not make it. Nothing above changes: the backtest of section 7, its cuts and the choice are as
they were (the file equals the one on main once `built` and `long_backtest` are set aside).

From the build of 27 November 2026 (made as at 22:00 UTC on 26 November; `runs/c730/table_long_rt.py`), mean absolute
error, USD/MWh:

| Hub | Year | Hours | ERW (regression) | Day-ahead price | Yesterday |
|---|---:|---:|---:|---:|---:|
| ERCOT HB_NORTH | 2016 | 8,783 | 6.25 | 5.83 | 7.96 |
| ERCOT HB_NORTH | 2017 | 8,759 | 5.58 | 5.51 | 8.58 |
| ERCOT HB_NORTH | 2018 | 8,759 | 12.80 | 13.90 | 17.07 |
| ERCOT HB_NORTH | 2019 | 8,759 | 29.84 | 25.00 | 29.07 |
| ERCOT HB_NORTH | 2020 | 8,783 | 11.17 | 8.72 | 12.24 |
| ERCOT HB_NORTH | 2021 | 8,759 | 130.79 | 46.84 | 118.80 |
| ERCOT HB_NORTH | 2022 | 8,759 | 35.05 | 29.75 | 42.97 |
| ERCOT HB_NORTH | 2023 | 8,759 | 39.81 | 33.76 | 48.70 |
| ERCOT HB_NORTH | 2024 | 8,783 | 14.87 | 12.25 | 19.78 |
| ERCOT HB_NORTH | 2025 | 8,759 | 11.58 | 11.15 | 19.73 |
| ERCOT HB_NORTH | 2026 | 7,799 | 13.51 | 13.00 | 20.34 |
| ERCOT HB_NORTH | 2016 to 2026 | 95,461 | 28.43 | 18.75 | 31.48 |
| SPP North Hub | 2019 to 2026 | 55,397 | 20.27 | 19.12 | 26.88 |
| CAISO SP15 | 2024 to 2026 | 22,317 | 8.23 | 8.16 | 13.59 |

The losses are the finding. At ERCOT the market's day-ahead price beats the ERW in ten of the eleven years; the ERW is
ahead only in 2018. In 2021 (Winter Storm Uri, February) the ERW's error is nearly three times the day-ahead price's:
the regression carries the last real-time spread into the next day, and in a scarcity week that spread is thousands of
dollars. In 2019 the yesterday method beats the ERW as well. SPP's years are scored by the file (2023 and 2024 hold
fewer hours: the price tables have gaps there); over its whole span the day-ahead price is ahead, while over the last
two years the ERW is (section 7). The share of hours inside the band over the whole span: ERCOT 77.5, SPP 76.6, CAISO
78.2 percent, against a nominal 80.

Replication (`replication/predict/replicate_rt.py`, from this section's words): 1,220 of 1,220 figures equal (the
1,120 of section 7 and 100 of the longer backtest). A test (`test_the_longer_backtest_adds_up_and_changes_nothing_above`)
holds that the years add up to the span, that its MAE is their hour-weighted mean, that it ends where the backtest
ends, and that the method is the one chosen now.
