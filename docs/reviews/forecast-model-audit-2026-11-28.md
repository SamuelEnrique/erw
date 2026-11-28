# The ERW forecast (/forecast): the model audited as a hostile expert would

Session 11402, chain 770 part B item 1, 28 November 2026, the old laptop. Read as a power trader's quant who wants to find it wrong: is anything known early, is the operator scored on the same hours, does the band mean what the page says, are the losses shown as plainly as the wins, do the tomorrow file and the ledger agree, and does each forecast beat the naive line it is set beside.

- The page: `https://erw-flame.vercel.app/forecast` (in review). It opens on Texas, demand, the newest past day, percent error.
- Nothing changed on main but this file and its evidence folder. No table written, no lock taken, no default moved, no model called.
- This machine holds none of the demand tables the forecast reads (`eia930_ba_demand_hourly`, `eia930_forecast_error_hourly` are not in its `warehouse/output`). Every figure here is restated from the page's own files (`site/data/predict/`, origin/main `f35d8245b`) and from two earlier builds of them read with `git show`, with none of the builder's code. What needs the tables is a data request at the foot.
- Each finding has its own branch, `wip/audit-forecast-<n>`, cut from origin/main. Words fixes (1, 2, 3, 5) are for landing; 4 moves figures and waits for Samuel.

## In short

- **The arithmetic is right.** Every figure the default view prints comes out to the digit from its files: tomorrow's highest and lowest hour, the past day's errors, the last 30 days restated from the hour rows, the backtest equal to the score file's row in all 64 places, the months and hours adding up to their spans in all 128 checks, and every method of every score row scored on one count of hours (9,015 of 9,015 groups).
- **Nothing is known early in the backtest's code.** Every regressor, fit and band reads days up to two days before the target (demand) or the day before (price), Henry Hub ten days back, the real-time forecast's day-ahead price only after the markets publish. The one way in is revisions: the backtest reads demand as revised, a live forecast reads it as first published; the newest day moved in 184 of 696 hours between two builds a day apart, by 0.08 percent on mean (finding 5, words).
- **The live price forecast is not the forecast scored.** It is scored as made at 14:00 UTC with demand through three days before; the daily run makes it at 19:00 UTC, after ERCOT has usually published the day-ahead prices it forecasts (median 18:36 UTC), and refits it on demand through two days before (finding 3, words; holding it to the scored hour is Samuel's).
- **The page draws a past day as "Tomorrow" and mislabels the forecast it draws.** Main's place files are a day behind the ledger (the ledger holds 28 November for all 64 places; the files draw 27 November, and for 35 of them a forecast no ledger holds). Where the file takes tomorrow from the ledger it keeps the build's horizon and input hour: all 29 places say "from demand through 25 November, 2 days before" of a forecast made from demand through 24 November, 3 days before (findings 1 and 2, words).
- **The tomorrow file and the ledger agree on every figure** (data request 577): values and bands equal in all 29 places on main and all 64 in the data machine's build of 27 November; the 24 empty rows of SPA (data request 20) are still in the public ledger.
- **The hourly demand forecast beats both naive lines, and not only where it was chosen:** before the two years it is chosen on, it beats the same hour two days before and a week before in all 64 places. It beats the operator in 21 places over the last two years and 13 before them.
- **The choice is made on the window it is scored on, and twice that flatters it.** SPP's price regression beats yesterday's price over its last two years (14.52 against 16.53 USD/MWh) and loses over the page's own backtest (34.63 against 18.73); PSCO's peak loses to yesterday's peak before its window (727.5 against 527.7 MW). Choosing on the whole backtest moves those two figures and little else (finding 4, Samuel's ruling).
- **The band means what the page says, as an average:** 78.5 percent of the last two years' hours inside (10.6 below, 11.0 above), 56 of 64 places under 80. It is an unconditional band: 316 of 1,504 place-months held under 70 percent (Tennessee 41.8 in January 2026), and the page's own month table shows it. Its coverage on the ledger cannot be measured yet: no live day has a demand figure in any file.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/forecast/page.tsx`, `view.tsx` | The page: the choices, Tomorrow (three figures, the chart with its band, the hours), the days after tomorrow, net demand, How it has done (a past day, the report card, the peak, the weather line, months, hours, the other cuts), Every place, Downloads. Every figure carries its key into its file. |
| `site/app/forecast/lines.tsx`, `realtime.tsx` | Net demand, wind and solar, the operator's filing check, the weather forecast line, the band's record (by hour and by month); the real-time price and the other hubs. |
| `site/app/forecast/*/route.ts`, `reader.ts` | The downloads: rows, scores, the two ledgers, the days ahead, net demand, the hubs, each with a Python and a Stata reader. |
| `site/lib/predict.ts`, `predictlines.ts`, `predictfiles.ts` | The page's reading of the files: the default day, a past day's errors (`dayScore`), the score tables, the made-hour check (`madeOffRule`), the ledger's text. |
| `warehouse/predict/predict_data.py` | Reads the tables: demand (the demand pages' sums), the operator's filed forecast with its screened hours left out, hub prices, Henry Hub, weather. |
| `warehouse/predict/predict_demand.py` | The demand methods (yesterday, week ago, regression, regression_recent), the walk-forward least squares, the band, tomorrow's rows. |
| `warehouse/predict/predict_price.py`, `predict_rt.py` | The day-ahead price forecast (scored as made at 14:00 UTC) and the real-time price forecast (as made at 22:00 UTC). |
| `warehouse/predict/predict_score.py` | The report card: the common hours, the cuts, the choice, the band's coverage, the peaks, the operator's filing check. |
| `warehouse/predict/run.py` | The daily run: every place's backtest, the choice, tomorrow, the ledgers, the page files; `from_ledger` (request 577) draws tomorrow from the first making. |
| `warehouse/predict/ahead.py`, `long_backtest.py`, `long_price.py`, `price_hubs.py`, `rt_price.py`, `wind_solar.py`, `predict_ws.py`, `predict_weather.py`, `predict_tables.py` | The days ahead, the backtests from 2016, the other hubs, the real-time price, wind and solar, the weather line, the ledgers as tables. |
| `site/data/predict/` | The files: `index.json` (the rules), 64 place files, `scores.json` (52,030 rows), `ahead.json`, `ahead_more.json`, `long_backtest.json`, `long_price.json`, `price_hubs.json`, `rt_price.json`, `wind_solar.json`, `ledger_demand.csv` (2,232 rows), `ledger_price.csv` (288), `ledger_wind_solar.csv`. No `ledger_price_hubs.csv` or `ledger_rt_price.csv` is on main. |
| `docs/methods/predict.md`, `predict_price.md`, `predict_wind_solar.md` | The method notes the page links to. |
| `docs/reviews/predict-ground-2026-11-26.md` | Chain 730's ground: the places, the spans, what was known when. |
| `docs/state/data_requests_predict.md` | The forecast's data requests (577 is the done-line request of the ledger; 20 the empty SPA rows). |
| `docs/state/progress_c730.md`, `note_2026-11-26_window2_c730.md`, main's log on the forecast | The builds: the first making at 11:00 UTC 26 November (29 places, horizon 3 and 4); rebuilds made as at 18:00 UTC 26 November (16 to 18: 64 places, no ledger row); the data machine's run of 27 November (`15511cb2e`, made 19:00 UTC, all 64 in the ledger); and `993a5d99b`, which put main's place files back to the rebuild of 26 November while keeping the run's ledgers. |

## The default view re-done, to the digit

Texas (`region-tex`), demand, percent error, from main's files (built 2026-11-27T14:39:36Z). Scripts and outputs: `docs/reviews/forecast-model-audit-2026-11-28/`.

| Figure | Restated | The page's file |
|---|---|---|
| Tomorrow's day | Friday 27 November 2026 (a past day on 28 November: finding 2) | the same |
| Highest hour of the ERW forecast | 54,040 MW at 17:00 CST | 54,039.5 |
| Operator, same hour | not held (not yet in the files for that day) | null |
| Lowest hour | 44,362 MW at 03:00 CST | 44,362.4 |
| The newest past day | 25 November | the same |
| Its error on the day, MW (24 hours): ERW, operator, yesterday, week ago | 3,765; 870; 4,166; 4,793 | the page computes them from the rows; the same |
| Last 30 days, MAPE %: ERW, operator, yesterday, week ago (721 hours) | 3.384, 1.109, 4.635, 5.104 (restated from the hour rows) | the same |
| Last 30 days, MAE MW | 1,784.45; 577.29; 2,414.85; 2,637.00 | the same |
| The backtest, MAPE % (64,763 hours, 1 July 2019 to 25 November 2026) | 5.468, 2.389, 7.308, 8.874 | equal to `scores.json`'s `all` row |
| The day's peak, last two years, MAPE % (720 days): ERW, operator, yesterday, week ago | 6.109, 2.194, 6.714, 9.123 | the same |
| The band: share of the last two years' hours inside | 80.3 percent (9.4 below, 10.3 above; 17,400 hours) | the same |

- **The last 30 days, every place.** Restated from the hour rows: equal to the digit in 61 of 64 places; in three the file's figure also requires both regressions to be held, which the hour rows do not carry (at most 66 MW, 0.27 point apart). Expected, not a fault.
- **The score file adds up.** The backtest summary equals the `all` row in all 64 places; the months' hour-weighted errors equal `all`, and the hours' equal `last_2_years`, for the ERW and the operator in every place (128 and 128 checks).
- **The band's November**, restated from the hour rows: equal in 58 of 64 places; in six small authorities (SPA, HST, CHPD, DOPD, SCL, TIDC) 0.1 to 0.5 point apart on the same hour counts: an hour or three on a band edge once the file rounds the band to 0.1 MW.

### One choice changed at a time

From the files alone. Anything that refits needs the tables.

| Choice | The page | Changed to | Measured worth |
|---|---|---|---|
| The window the method is chosen on | the last two years | the whole backtest | the method changes in 2 price places (SPP: backtest MAE 34.63 to 18.73 USD/MWh, last two years 14.52 to 16.53), 2 demand places by under 2 percent (LDWP, SPA), and the peak's method in 14 places, by much only at PSCO (backtest peak MAPE 10.39 to 8.35 percent, last two years 7.35 to 8.76) and Tennessee (8.62 to 7.95; 8.32 to 8.49). Finding 4 |
| How old the demand read is | two days before the day (h = 2) | three days (h = 3, `ahead.json`) | median +17.9 percent MAE over the 29 places; Texas 2,841 to 3,424 MW |
| The weather | none read | the day's own observed temperature (not a forecast) | median 24.0 percent off the regression's MAPE; Texas 5.27 to 3.90, the operator 2.07; it would beat the operator in 28 of 64 |
| The fourth candidate, added after looking at the last two years | regression_recent | the plain regression | regression_recent is better before the window too, in 63 of 64 places (not PSCO): not a fit to the window |
| The comparator's months | every month | the months whose filing passes its check | the ERW ahead of the operator in 16 of the 59 places with sound months, then in 12 |
| The peak's own choice | the candidate whose peaks missed least | the hourly method's peak | differs in 17 places; Central 6.02 against 7.35 percent, SWPP 6.31 against 6.90, FMPP 7.17 against 7.84 |

## Each question against the code

- **Is anything known early?** Read in the code:
  - Demand (`predict_demand.features`, `walk_ols`): day A's hours and mean lag the target by h = 2; the week's mean ends on day A; T-7 and T-14 lag 7 and 14; the fit for day i uses rows up to i - h only (`hi = i - h + 1`); holidays are a rule; a lone missing hour is filled for regressors only. Right.
  - The band (`band`): the rolling 365 days of errors shifted by h, so it ends with day A's error, known when the forecast is made. Right.
  - Price (`predict_price.features`, `gas_by_day`): the hub's prices through T-1 (published on T-2), the demand forecast refit at hd = 3 with the week's demand through T-3, Henry Hub at least ten days before T-1. Right in the backtest; not live (finding 3).
  - Real-time (`predict_rt`): day T's day-ahead price, real-time prices through T-2, as at 22:00 UTC, after the three markets' ordinary publication. Right. The daily run reaches this step at about 05:00 UTC the next day, when the warehouse does not yet hold the next day's day-ahead price, so no live real-time forecast has been made (each hub says "no forecast yet") and no ledger of it exists: honest.
  - Weather line (`predict_weather.forecast_matrix`, `made_hour=20`): an issue no later than 20:00 UTC the day before. Right.
  - Revisions: the backtest reads each day as revised. Finding 5.
- **Is the operator scored on exactly the same hours?** Yes, everywhere: `predict_score.common` takes the hours the actual and every scored method hold, the operator included, for every score row, every summary (`also=SCORED`), the peak and the sound months; the page's own day error (`dayScore`) takes the hours every drawn method holds. In the file, 9,015 of 9,015 groups (place, series, cut, key) carry one hour count for every method. What a quant adds: the operator's hours screened as filing errors (`x_screened`: a filed forecast above three times or below a third of the demand) are chosen by reading the demand, and leave the comparison for both lines. That drops the operator's worst misses; its size needs the table (data request 2).
- **Does the band mean what the page says?** "About eight hours in ten have fallen inside it, and each file prints the share that did": over the last two years 78.5 percent hour-weighted, 71.2 (SRP) to 81.1 (PGE), 10.6 below and 11.0 above. True as an average. It is no probability: 316 of 1,504 place-months (600 hours or more) held under 70 percent (SRP 31.2 in April 2026, Tennessee 41.8 and the Carolinas 42.5 in January 2026), while the last 35 days held 86.8 (too wide in a calm month, too narrow in a cold one). The page's band record draws the months and the hours (`BandCheck`), so it is said: no finding. The price bands: 77.9 to 78.7 percent. On the ledger: not measurable yet, no live day has its demand in any file (data request 3).
- **Are the losses shown as plainly as the wins?** Yes. Every table puts the operator and the naive lines beside the ERW at one weight, months in the calendar's order, places in the index's; no sentence says the ERW wins. The operator wins in 43 of 64 places over the last two years and the tables show it. The loss a reader must work out is finding 4's: the backtest row shows SPP's regression far behind yesterday's price, yet it is drawn as the ERW forecast.
- **Do the tomorrow file and the ledger agree (request 577)?** On every figure: values and bands equal in the 29 places of main whose tomorrow comes from the ledger, and in all 64 places and six price places of the data machine's build of 27 November. Not on what the file says the forecast read (finding 1), nor on which day (finding 2).
- **Does each forecast beat its naive line?** From the score file's `all` and `last_2_years` rows, which share their hours, so the years before the choice window are their difference:
  - Demand by the hour: beats the same hour two days before and a week before in all 64 places, over the last two years and over the years before them (narrowest: WALC, 0.917 of yesterday's error before the window).
  - The peak: beats yesterday's peak in 62 of 64 over the last two years (at SPA and WALC the peak's method is yesterday's: a tie) and in 61 before them; PSCO loses before them, 727.5 against 527.7 MW (finding 4).
  - The days ahead: all 145 place-horizons beat the week-ago hour, as the page says, and the latest day held too; narrowest Texas seven days ahead, 9.5 percent under the week-ago hour.
  - The day-ahead price: at ERCOT the ERW forecast is yesterday's price (a tie by construction); at CAISO the regression wins the last two years (5.90 against 6.20) and loses the months before (7.81 against 7.50 over 4,776 hours); at SPP it wins the last two years and loses the backtest (finding 4).
  - The real-time price: the day-ahead price beats the ERW at six of seven hubs over the last two years (SPP North the exception, 17.63 against 17.91 USD/MWh); the page and the note say so.

## Findings

| # | Severity | Finding | Measured | Branch | Kind |
|---|---|---|---|---|---|
| 1 | Major | A tomorrow drawn from the ledger keeps the build's horizon, last hour read and fit day | all 29 places on main: "2 days before, from demand through 25 November" of a making through 24 November at 3 (MIDW, NW, MISO: 4); the six price places 1 against 2 | `wip/audit-forecast-1` | words, for landing |
| 2 | Major | Main's files are a day behind the ledger: "Tomorrow" is a past day, and for 35 places a forecast no ledger holds | the ledger holds 28 November for 64 of 64 places; the files draw 27 November; 35 of those drawn days in no ledger | `wip/audit-forecast-2` | words, for landing; the files are the desk's (data request 1) |
| 3 | Major | The live price forecast is made at the run's hour (19:00 UTC), after ERCOT's day-ahead prices are usually public, and on demand one day newer than the forecast scored | made 19:00 UTC 27 November for 28 November; ERCOT's median publication 18:36 UTC; `demand_horizon_days` 2 against the backtest's 3 | `wip/audit-forecast-3` | words, for landing; the hour and horizon are Samuel's |
| 4 | Moderate | The method is chosen on the window it is scored on; twice the choice loses to the naive line over the rest of the backtest | SPP price 14.52 against 16.53 in the window, 34.63 against 18.73 over the backtest; CAISO 7.81 against 7.50 before the window; PSCO peak 727.5 against 527.7 MW before it | `wip/audit-forecast-4` | figure, Samuel's ruling |
| 5 | Minor | The backtest reads demand as revised; a live forecast reads it as first published | the newest day moved in 184 of 696 place-hours a day later, 0.08 percent on mean (FPC 0.82) | `wip/audit-forecast-5` | words, for landing |

### 1. A tomorrow drawn from the ledger says it read what it did not

- **Where.** `warehouse/predict/run.py` `from_ledger` (request 577) replaces tomorrow's values, band, method and making hour with the ledger's; `demand_series` and `price_shown` then write `horizon_days`, `inputs_through_utc` and `fit_day` from the build. The page prints them in the place's hover (`view.tsx` `PlaceHead`).
- **What a reader sees.** Drawn from main's files: "made 2026-11-26 05:00 CST (11:00 UTC), from the place's own figures through 2026-11-25 23:00 CST, 2 days before the day forecast ... last fit 2026-11-26". The ledger's making read demand through 24 November 23:00 CST, three days before. The band's coverage beside it is the method chosen now (regression_recent at two days), not the making's (the regression at three).
- **How much.** 29 of 29 places whose tomorrow comes from the ledger; the six price places (1 against 2). On the data machine's own build the two agree, because its making is the ledger's; the fault shows whenever the files are rebuilt after the making, as main's are now.
- **The test.** `tests/test_audit_forecast_1.py`: on main's files every value equals the ledger's and every horizon and input hour differs (passes on main while the files are those audited); `from_ledger` carries the ledger's horizon and input hour (fails on main, passes on the branch).
- **The fix on the branch.** Words only: `from_ledger` returns the ledger's `horizon_days` and `inputs_through_utc`; `fit_day` becomes the making's day; a price making of another hour leaves `demand_horizon_days` null (the ledger does not name it). No forecast figure, band or score moves. It shows on the page at the data machine's next run. `tests/test_predict.py` passes on the branch (36 of 36).

### 2. The page draws a day that has passed under "Tomorrow"

- **Where.** `993a5d99b` (chain 701) put main's place files, index and scores back to the rebuild of 26 November because ba-sceg's demand ended two days behind the 29 places and a test allows one, while keeping the run's ledgers. `view.tsx` `Tomorrow` draws the file's `target_day` with nothing to say it has passed.
- **What a reader sees on 28 November.** "Tomorrow ... ERW forecast of demand: Friday 27 Nov 2026" for every place and both series, while the ledger holds Saturday 28 November for all 64. For the 35 authorities added on 27 November, the day drawn was made by a rebuild as at 18:00 UTC on 26 November that wrote no ledger row: a forecast the page draws and its record does not hold. `price_hubs.json` is the same (its four hubs draw 27 November; `ledger_price_hubs.csv` is not on main).
- **The test.** `tests/test_audit_forecast_2.py`: the ledger holds a later day than the file in 64 of 64 places and no row of the drawn day for 35 (passes on main while the files are those audited); the page says so (fails on main).
- **The fix on the branch.** Words only, on the page (chain 720's file, for the desk to land): where the ledger of the series holds a later day for the place than its file, the Tomorrow block says "The ledger already holds a newer ERW forecast for this place, for Saturday 28 Nov 2026: these files, built 2026-11-27, are behind it, and the day drawn here, Friday 27 Nov 2026, is the newest they hold." Clock-free: it reads the ledger, never today's date. Drawn to HTML from main's files (Texas demand and price, AECI). The figures are the desk's to bring current (data request 1).

### 3. The live price forecast is not the one scored

- **Where.** `run.py` `price_place`: `made` is the hour of the run, and `hp, hd = (target - last price day), (target - last demand day)`; when the pair is not (1, 3) the model is refit at the horizons held. `index.json` `made_rule` and `predict_price.md` section 2 say 14:00 UTC, before any grid publishes, demand through three days before.
- **Why it matters to a trader.** A day-ahead price forecast issued after the auction has cleared is no forecast. The daily run makes it at about 19:00 UTC (the ledger: 19:00 UTC 27 November for 28 November), when ERCOT's day-ahead prices are usually out (11.4 hours before the day begins on the table's median `vintage`, 18:36 UTC in winter). The forecast does not read them (the price tables do not hold them at that hour), so nothing leaks; but the claim "before any grid publishes" is false for every live forecast at ERCOT. And at 19:00 UTC the warehouse holds demand through two days before, which the refit reads: the data machine's build shows `demand_horizon_days` 2 in all six price places, against the 3 of every scored forecast.
- **How much.** At ERCOT none on the figures: the forecast shown is yesterday's price, which reads no demand. At SPP and CAISO the regression shown live is a model the backtest never scored; its difference from the scored one needs the tables (data request 4).
- **The test.** `tests/test_audit_forecast_3.py`: the code takes both horizons from what is held; the data machine's build made all six at 19:00 UTC with two days of demand (both pass on main); the rule and the note say what the live forecast is, and the page's made-hour check still reads 14:00 as the price rule's hour (fails on main).
- **The fix on the branch.** Words only: `made_rule` and `predict_price.md` section 2 say the daily run makes it at about 19:00 UTC, after ERCOT's prices are usually public, from demand through two days before.
- **For Samuel.** Hold the live price forecast to the scored horizon (`hd = 3`) and move its step before ERCOT's publication, or leave it. Default: left as it is.

### 4. The choice is scored on the window it is made on

- **Where.** `predict_score.choose`: the candidate with the lowest error over the last 730 days; the cut `last_2_years` is the same 730 days. `run.py` applies it to demand, price and (for the peak) the peak's error.
- **Why it matters.** A method chosen on a window always looks best there. The fair test is the years before the window, which the score file holds as the difference of its `all` and `last_2_years` rows (same hours, same methods).
- **How much.**
  - SPP's day-ahead price (CENT, SWPP): the regression beats yesterday's price over its window, 14.52 against 16.53 USD/MWh; over the page's own backtest (March 2020 on, 48,001 hours) it loses, 34.63 against 18.73; before the window 45.81 against 19.95 (30,847 hours). Winter Storm Uri and 2022 are in those years, and the page's "The backtest" row shows the loss beside the name "ERW forecast".
  - CAISO SP15: wins its window, 5.90 against 6.20; loses the months before, 7.81 against 7.50 (4,776 hours); over the whole backtest it still wins (6.31 against 6.48).
  - PSCO's day peak: regression_recent beats yesterday's peak in its window (492.2 against 563.1 MW) and loses before it, 727.5 against 527.7 (1,912 days); over the whole backtest yesterday's peak is ahead (MAPE 8.35 against 10.39 percent).
  - Not affected: the hourly demand forecast, which beats both naive lines before the window in all 64 places.
- **The test.** `tests/test_audit_forecast_4.py` (passes on main while the files are those audited).
- **For Samuel.** Choose on the whole backtest. SPP's price forecast becomes yesterday's price (the last two years 14.52 to 16.53 USD/MWh, the backtest 34.63 to 18.73); PSCO's peak becomes yesterday's peak (last two years 7.35 to 8.76 percent, backtest 10.39 to 8.35); Tennessee's peak the regression (8.32 to 8.49; 8.62 to 7.95); 11 more places' peaks and LDWP's and SPA's hours by under 2 percent. Default: left as it is.

### 5. The backtest knows day A a little better than a live forecast

- **Where.** `predict_data.demand_panel` reads the table as it stands at the build; the backtest's day-A regressors are revised values. The method note's "What was known when" did not say so.
- **How much.** Three builds of the place files a day apart (`0cdfd65ad`, `e5f755eda`, `15511cb2e`; tables through 24, 25 and 26 November): the newest day changed in 184 of 696 place-hours from its first publication to the next day's (12 of 29 places), 0.08 percent of demand on mean (FPC 0.82, CPLE 0.50; one New England hour 6.7); older days in 384 of 22,736 hours, 0.01 percent. The operator's filed forecast barely moved (19 hours, NW only). Small beside errors of 3 to 10 percent; one day of vintages is too few to say more.
- **The test.** `tests/test_audit_forecast_5.py`: the measure from the builds (passes on main where the history is held); the note says it (fails on main).
- **The fix on the branch.** Words only: a paragraph in the note's section 2.

## What was checked and found right

- The arithmetic of every figure of the default view, and of every place's last 30 days (61 of 64 to the digit; the other three by the rule above).
- The score file's identities: backtest equals `all`, months add to `all`, hours to `last_2_years`, in every place.
- Every score group holds one count of hours for every method (9,015 of 9,015): the operator, the ERW and the naive lines are scored on the same hours.
- The ledger never rewritten: the two makings of 27 and 28 November sit side by side; a second making of a day adds nothing (`append_ledger` keys by series, place and day).
- No known-early read in the backtest's code (demand, band, price, real-time, weather line), section "Each question against the code".
- regression_recent, added after looking at the last two years, is better before them too (63 of 64).
- The days ahead: all 145 place-horizons beat both the week-ago hour and the latest day held, as shown.
- The real-time price's losses to the day-ahead price are printed and said.

## Not covered, or left open

- Anything that refits: the live price forecast held to three days of demand, the band's coverage on the ledger, the screened hours' effect. Data requests below.
- The band's coverage on the stress days and spike hours: the hour rows hold 35 days only; the month table shows January 2026 at 42 to 46 percent in the Southeast and Tennessee.
- Wind, solar and net demand (`predict_wind_solar.md`): not re-done here beyond the same-hours rule. CAISO's wind and solar forecasts carry no publication time, so CISO's operator line for net demand cannot be shown to be the day-ahead one; the note says so of the ERW's side, not of the comparator's.
- The Ask panel was not run (it calls a model).

## The branches

Each cut from origin/main `f35d8245b`, pushed, none requested by this file (the rows are the main session's to write).

| Branch | Head | Kind | What it holds |
|---|---|---|---|
| `wip/audit-forecast-1` | `18d30a35e` | words | `warehouse/predict/run.py` (`from_ledger`, `demand_series`, `price_shown`), `tests/test_audit_forecast_1.py`; `tests/test_predict.py` 36 of 36 |
| `wip/audit-forecast-2` | `ae81856ab` | words | `site/app/forecast/view.tsx` (`ledgerNewest`, the line in `Tomorrow`), `tests/test_audit_forecast_2.py`; the page's three drawing tests pass (128, 131, 214 checks), tests 10410, 10411, 10413 pass (34); no site build was run on this machine |
| `wip/audit-forecast-3` | `a8d99768f` | words | `run.py` `made_rule`, `docs/methods/predict_price.md` section 2, `tests/test_audit_forecast_3.py` |
| `wip/audit-forecast-4` | `21e5f2677` | for Samuel's ruling | `tests/test_audit_forecast_4.py` only |
| `wip/audit-forecast-5` | `74d58b919` | words | `docs/methods/predict.md` section 2, `tests/test_audit_forecast_5.py` |

Scripts and outputs of this audit: `docs/reviews/forecast-model-audit-2026-11-28/` (`audit.py` the default view, request 577, the band, the naive lines; `revisions.py` the three builds; `choices.py` one choice at a time; `draw2.mjs` the page drawn from main's files with branch 2's line; `peek.py` the files' shapes).

## Data requests for the main session

1. The desk (data machine): bring main's place files, `index.json`, `scores.json` and `price_hubs.json` level with the ledger (the run's own files of 27 November or a newer run), and commit `ledger_price_hubs.csv` when `price_hubs.py` writes it; the test that sent them back (ba-sceg's demand two days behind) wants a reason in the file, not files a day behind.
2. On the data machine, with `eia930_forecast_error_hourly`: per place, the hours of the last two years screened out (`x_screened` true) and the ERW's and the operator's MAE with those hours put back, to size how much the screen flatters the operator.
3. On the data machine, from 27 November on: the share of the ledger's demand and price hours inside their band, below and above, against `eia930_ba_demand_hourly` and the hub prices, by place, once 30 days are held.
4. On the data machine: `run.py` for 28 November made as at 14:00 UTC on 27 November (`--now 2026-11-27T14:00:00Z --no-ledger`, `--places region-cent ba-swpp region-cal ba-ciso`), and the price forecasts set beside the ledger's 19:00 UTC making: what the live refit at two days of demand moves.
5. The 24 empty SPA rows of `ledger_demand.csv` (data request 20 of `data_requests_predict.md`) are still on main and in the page's ledger download.
