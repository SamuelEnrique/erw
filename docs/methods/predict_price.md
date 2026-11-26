# The ERW forecast of day-ahead hub prices (`site/data/predict/`, the page `/forecast`)

Session 10600, chain 730 (lab-desktop's second window, part E), 26 November 2026. Code: `warehouse/predict/price.py` (the methods and the backtest), with `data.py`, `score.py` and `run.py` shared with the demand forecast (`docs/methods/predict.md`, whose rules on the backtest, the choice, the band and the scores hold here unless this note says otherwise). Contract of the files: `docs/state/page_files_predict.md`. Tests: `tests/test_predict.py`.

**What it is.** The ERW's own forecast of tomorrow's day-ahead price at one hub of each grid whose hub prices the warehouse holds under a public license, hour by hour, with a band, and its report card. Tier `derived`: a model's output, never a published or official figure, and no advice. No operator publishes a forecast of its own day-ahead price, so there is no "operator" line here; the yardsticks are yesterday's price and last week's.

## 1. The grids and their hubs

| Grid | Hub forecast | Shown for | Held from | Why this hub |
|---|---|---|---|---|
| ERCOT | HB_NORTH | TEX, ERCO | 2015-01-01 | the hub most quoted for ERCOT; the six hubs are held |
| SPP | SPPNORTH_HUB | CENT, SWPP | 2018-07-01 | the only SPP hub held before 26 August 2026 |
| CAISO | TH_SP15_GEN-APND (SP15) | CAL, CISO | 2023-07-06 | Southern California's trading hub, the larger load |
| ISO-NE | .H.INTERNAL_HUB | NE, ISNE | 2024-09-01 | the one hub held |
| NYISO | N.Y.C. (zone J) | NY, NYIS | 2024-09-01 | the one New York price held |

Not forecast, with the reason in every file: MISO (paused since 4 October 2026: MISO's terms forbid automated access, `warehouse/metadata/paused_sources.csv`; no price after that day can be used or scored), PJM (its prices need a paid data license, `docs/licenses.md`; none is held), and every place with no organised day-ahead market whose hub prices the warehouse holds (CAR, FLA, NW, SE, SW, TEN and their authorities).

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

Walking forward a day at a time to 25 November 2026, from the first day each method can be made: the regression needs 300 days of its own inputs, so its backtest begins on 5 March 2020 for ERCOT (the demand regression it reads begins in July 2019), 4 March 2020 for SPP, 10 May 2024 for CAISO, 5 July 2025 for ISO-NE and 7 July 2025 for NYISO. All methods of a grid are scored on the same hours (where the actual price and every method's forecast are held). The choice is the demand forecast's rule: the lowest mean absolute error over the last two years (or all the backtest has, for ISO-NE and NYISO). The percent error counts only hours whose actual price is at least 5 USD/MWh in size. **Spikes are scored apart:** the hours above the grid's own 99th percentile of the backtest's actual prices (cut `spike`).

**The last two years (built 26 November 2026 at 11:37 UTC; `runs/c730/table_price.py` prints it from `scores.json`):**

| Grid (place) | Hub | Chosen | Hours (2 years) | ERW MAE | Yesterday's price MAE | Week-ago MAE | Regression MAE | ERW MAPE % | Spike hours (whole backtest) | ERW MAE, spikes | Yesterday MAE, spikes | Regression MAE, spikes |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ERCOT (TEX) | HB_NORTH | yesterday | 17,348 | 13.07 | 13.07 | 17.33 | 16.23 | 33.6 | 588 | 1027.9 | 1027.9 | 1479.8 |
| SPP (CENT) | SPPNORTH_HUB | regression | 17,153 | 14.52 | 16.54 | 21.37 | 14.52 | 57.1 | 480 | 1331.9 | 416.5 | 1331.9 |
| CAISO (CAL) | SP15 | regression | 17,468 | 5.91 | 6.20 | 10.41 | 5.91 | 23.4 | 223 | 40.9 | 46.5 | 40.9 |
| ISO-NE (NE) | Internal hub | regression | 12,094 | 15.74 | 16.09 | 29.80 | 15.74 | 22.8 | 121 | 164.3 | 163.8 | 164.3 |
| NYISO (NY) | N.Y.C. | yesterday | 12,012 | 13.61 | 13.61 | 29.87 | 14.45 | 16.7 | 121 | 193.0 | 193.0 | 203.0 |

MAE in USD/MWh. The authorities' rows (ERCO, SWPP, CISO, ISNE, NYIS) are the same hubs and differ only where their demand forecast differs from the region's (SWPP's regression 14.54 against CENT's 14.52).

What the table says, plainly:

- **The regression is barely better than yesterday's price, where it is better at all.** It wins in CAISO (5.91 against 6.20), SPP (14.52 against 16.54) and ISO-NE (15.74 against 16.09); it loses in ERCOT and NYISO, where the page shows yesterday's price as the ERW forecast. A day-ahead price is mostly yesterday's price plus what tomorrow's weather and outages will do, and the ERW reads neither weather nor outages.
- **On spikes the ERW forecast is poor and says so.** In SPP the regression misses its spike hours by 1,332 USD/MWh on average against yesterday's 417 (the February 2021 storm dominates); in ERCOT a spike hour is missed by about 1,000 USD/MWh by every method. No method here sees a spike coming.
- **The percent errors are large** (17 to 57 percent) because day-ahead prices are often low and volatile; the MAE is the measure to read.
- The band holds about eight hours in ten (ERCOT 77.9 percent of the last two years' hours, CAISO 78.7, ISO-NE 82.9), but it is wide where prices jump, and a spike falls outside it.

## 5. The files

The price is `series.price` of each place's file, with `hub`, `market` (`day-ahead`), `horizon_days` (the days between the last whole day of prices read and the target day: 1 in the backtest, 2 for the first live forecast, made at 11:00 UTC on 26 November when the warehouse held prices through 25 November) and `demand_horizon_days` (3). `operator` is `null` throughout and `operator_held` says why. Every forecast as made is appended to `site/data/predict/ledger_price.csv`, never rewritten; the first rows are for 27 November.
