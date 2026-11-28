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

**Ready branch of session 11408, not the default.** ERCOT's real-time prices (`ercot_all_hub_prices_history`) are filled
by its legacy `/misapp` pulls, paths ERCOT's robots file disallows (the owner's ruling 2 of 6 November 2026), so no
ERCOT hub's real-time price is forecast (`LEGACY_MISAPP` in `warehouse/predict/rt_price.py`): `rt_price.json` keeps
SPP's and CAISO's hubs. The day-ahead price forecast is unchanged.

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

## 9. The real-time price at more hubs (session 10603)

Samuel's order of 27 November 2026 ("more places"). The real-time forecast of section 7 reads one hub a grid. The
price tables hold, over at least two years and in both markets, four more hubs of the same three grids: ERCOT's
Houston, South and West hubs (`HB_HOUSTON`, `HB_SOUTH`, `HB_WEST`, from January 2015, `ercot_all_hub_prices_history`)
and CAISO's NP15 (`TH_NP15_GEN-APND`, from July 2023, `iso_hub_prices_history`). Each is added to `rt_price.json` after
the three hubs of section 7, with the same methods, choice, band, scores and longer backtest (`grid` `ercot-houston`,
`ercot-south`, `ercot-west`, `caiso-np15`; score rows under `hub-<grid>`). Left out, and why: SPP's South Hub and
CAISO's ZP26 hold day-ahead prices from 26 August 2026 only and no real-time price; ERCOT's `HB_HUBAVG` and `HB_BUSAVG`
are averages of the hubs already scored; ERCOT's Panhandle hub is not held. The three hubs of section 7 are unchanged
(their blocks and their 1,120 score rows equal those on main, the longer backtest aside). The forecast is made at the
same hour, 22:00 UTC, after the grids' day-ahead markets publish.

From the build of 27 November 2026 (made as at 22:00 UTC on 26 November), the last two years:

| Hub | Hours | MAE USD/MWh: ERW, day-ahead price, yesterday | MAPE %: ERW, day-ahead price | Band inside % | Longer backtest: years, ERW ahead of the day-ahead price in |
|---|---:|---|---|---:|---|
| ERCOT HB_HOUSTON | 17,422 | 10.92, 10.68, 16.81 | 27.87, 26.27 | 77.4 | 2016 to 2026: 2017, 2018 |
| ERCOT HB_SOUTH | 17,422 | 11.03, 10.47, 17.65 | 30.35, 27.72 | 77.8 | 2016 to 2026: 2017, 2018 |
| ERCOT HB_WEST | 17,422 | 13.97, 12.63, 24.43 | 40.67, 34.48 | 79.0 | 2016 to 2026: 2018 |
| CAISO NP15 | 17,470 | 8.27, 8.04, 13.20 | 27.36, 26.38 | 78.6 | 2024 to 2026: 2024 |

The day-ahead price is the better forecast at all four, as at ERCOT North and CAISO SP15; the gap is widest at ERCOT
West, where the real-time price swings most. Over 2016 to 2026 the day-ahead price's error at the three ERCOT hubs is
about two thirds of the ERW's (Houston 19.94 against 29.85, South 18.44 against 28.42, West 19.80 against 29.18),
most of the difference made in 2021. The method chosen is the regression at every hub.

Replication (`replication/predict/replicate_rt.py`, from sections 7 to 9): 3,020 of 3,020 figures equal, every hub,
method and cut and the longer backtest's years. A test (`test_the_hubs_added_come_after_the_three`) holds the order and
the entities.

## 10. The day-ahead price at more hubs (session 10603)

Samuel's order of 27 November 2026 ("more places"). The place files carry the day-ahead price at one hub a grid (section
1). The same four hubs as section 9 (ERCOT Houston, South and West; CAISO NP15) now have the day-ahead forecast too, in a
file of their own, `site/data/predict/price_hubs.json` (code `warehouse/predict/price_hubs.py`, which calls the place
files' own functions: the same methods, the same hour of making, 14:00 UTC the day before, the same choice, band and
scores, the same `series.price` shape a place file has, with `place` `hub-<grid>`, `grid`, `demand_place` and `time`
added). Each hub reads its grid's demand forecast, as the grid's first hub does: ERCO's for ERCOT's hubs, CISO's for NP15.
Every forecast as made is appended to `ledger_price_hubs.csv`, never rewritten; the regression's backtest is written as a
file (`predict_price_hubs_backtest.csv`, in the run's `--out-dir`, not a warehouse table). Nothing in the place files
changes.

From the build of 27 November 2026 (made as at 18:00 UTC on 26 November, the place files' hour; `runs/c730/table_ph.py`),
the last two years, with the grid's first hub (from the place files) above each:

| Hub (demand read) | Chosen | Hours | MAE USD/MWh: ERW, yesterday, week ago, regression | ERW MAPE % | Spike hours: n, MAE of ERW, yesterday, regression | Band inside % |
|---|---|---:|---|---:|---|---:|
| ERCOT HB_NORTH (ERCO; place file) | yesterday | 17,348 | 13.06, 13.06, 17.32, 16.22 | 33.5 | 589: 1,026, 1,026, 1,477 | 77.9 |
| ERCOT HB_HOUSTON (ERCO) | yesterday | 17,348 | 11.47, 11.47, 15.66, 14.49 | 28.6 | 588: 1,013, 1,013, 1,474 | 78.4 |
| ERCOT HB_SOUTH (ERCO) | yesterday | 17,348 | 11.78, 11.78, 15.81, 14.86 | 30.8 | 589: 1,006, 1,006, 1,466 | 78.4 |
| ERCOT HB_WEST (ERCO) | yesterday | 17,348 | 17.81, 17.81, 22.85, 19.32 | 59.5 | 589: 1,031, 1,031, 1,449 | 78.7 |
| CAISO SP15 (CISO; place file) | regression | 17,516 | 5.89, 6.20, 10.39, 5.89 | 23.3 | 224: 40.9, 46.4, 40.9 | 78.7 |
| CAISO NP15 (CISO) | regression | 17,516 | 5.07, 5.60, 8.73, 5.07 | 17.7 | 224: 38.8, 41.4, 38.8 | 79.6 |

What it says: at every ERCOT hub the ERW's regression loses to yesterday's price, as at North, so the ERW forecast shown
there is yesterday's price; at West, where prices swing with wind and congestion, the regression comes nearest
(19.32 against 17.81) but still loses. At NP15, as at SP15, the regression wins by about a tenth. No method sees a spike
coming: on ERCOT's spike hours every method misses by about 1,000 USD/MWh, and the regression by more.

Replication (`replication/predict/replicate_price.py`, session 10603): the day-ahead price rebuilt end to end from the
public tables and the notes' words, imported from nothing of the builder: the hub's prices, the place's demand, Henry
Hub, the demand regression made with demand through T-3 refitted for every target day, the price regression refitted
for every target day, the simple methods, the choice and every cut, for the six places of the place files (their price
rows in `scores.json`, which had no replication of their own before) and the four hubs of this section. Its count is in
the progress file and the landing row.

## 11. The day-ahead price over a longer backtest (session 10603)

Section 8 said the day-ahead price's backtest could not start earlier, because it reads the place's demand forecast
and the warehouse's demand began in July 2018. Window A's landing 20 (data request 9) added every authority's demand
from July 2015 (`eia930_all_history`). `warehouse/predict/long_price.py` walks the day-ahead price forecast from 1 July
2016 on that longer demand (`predict_data.demand_panel_long`) for the six places of the place files and the four hubs of
section 10, with the same methods, fits, hour of making and horizons, and writes `site/data/predict/long_price.json`:
every calendar year scored on the hours every method holds, and the whole span. The first scored day is where the
regression first has its 300 days: 1 March 2017 at ERCOT's hubs; 6 May 2019 at SPP's (its prices begin in July 2018;
the published backtest starts in March 2020 because its demand regression started a year later); May 2024 at CAISO's,
as before. The place files and `price_hubs.json` are unchanged; the method in every year is the one chosen now.

From the build of 27 November 2026 (`runs/c730/table_long_price.py`), mean absolute error, USD/MWh:

| Place (hub) | Chosen | First day | Hours | MAE USD/MWh over the span: ERW, yesterday, week ago, regression | Years the regression beats yesterday's price |
|---|---|---|---:|---|---|
| region-tex (HB_NORTH) | yesterday | 2017-03-01 | 85,107 | 19.82, 19.82, 42.82, 39.7 | 1 of 10: 2017 |
| ba-erco (HB_NORTH) | yesterday | 2017-03-01 | 85,107 | 19.82, 19.82, 42.82, 39.7 | 1 of 10: 2017 |
| region-cent (SPPNORTH_HUB) | regression | 2019-05-06 | 55,274 | 29.76, 17.05, 27.14, 29.76 | 5 of 8: 2019, 2020, 2024, 2025, 2026 |
| ba-swpp (SPPNORTH_HUB) | regression | 2019-05-06 | 55,514 | 29.77, 17.05, 27.11, 29.77 | 5 of 8: 2019, 2020, 2024, 2025, 2026 |
| region-cal (TH_SP15_GEN-APND) | regression | 2024-05-10 | 22,244 | 6.31, 6.48, 11.03, 6.31 | 2 of 3: 2025, 2026 |
| ba-ciso (TH_SP15_GEN-APND) | regression | 2024-05-08 | 22,340 | 6.3, 6.47, 11.0, 6.3 | 2 of 3: 2025, 2026 |
| hub-ercot-houston (HB_HOUSTON) | yesterday | 2017-03-01 | 85,107 | 19.38, 19.38, 42.6, 39.5 | 1 of 10: 2017 |
| hub-ercot-south (HB_SOUTH) | yesterday | 2017-03-01 | 85,107 | 19.28, 19.28, 42.28, 39.0 | 1 of 10: 2017 |
| hub-ercot-west (HB_WEST) | yesterday | 2017-03-01 | 85,107 | 23.12, 23.12, 46.78, 41.09 | 1 of 10: 2017 |
| hub-caiso-np15 (TH_NP15_GEN-APND) | regression | 2024-05-08 | 22,340 | 5.41, 5.82, 9.54, 5.41 | 2 of 3: 2025, 2026 |

What the longer record says: at ERCOT the regression has beaten yesterday's price in one year of ten (2017, when
prices were low and calm); in 2021, the year of Winter Storm Uri, it missed by 197.5 USD/MWh against yesterday's 62.2,
in 2022 by more than twice yesterday's error and in 2023 by a quarter more. So the ERW forecast shown at ERCOT,
yesterday's price, is the
right one by this record too. At SPP the regression wins five years of eight, but its three losses (2021 to 2023) are
large enough that over the whole span yesterday's price is far ahead (17.05 against 29.76); the rule, which looks only at
the last two years, chooses the regression there. That is the rule working as written, not a fault: it is said here so
that a reader of the last two years knows what the longer record shows.

Replication (`replication/predict/replicate_long_price.py`, from this section's words, with the longer demand of
`replicate_long.py` and the price walk of `replicate_price.py`): its count is in the progress file and the next landing
row.
