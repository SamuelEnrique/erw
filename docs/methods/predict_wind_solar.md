# The ERW forecast of wind and solar output, by region (`site/data/predict/wind_solar.json`)

Session 10602, chain 730 (lab-desktop's second window, part F), 27 November 2026, on Samuel's order of that day: "a
forecast of wind and solar output by region, scored against the operators' own wind and solar forecasts the warehouse
holds". Code: `warehouse/predict/predict_ws.py` (the methods and the backtest) and `warehouse/predict/wind_solar.py`
(the daily run, the file and the ledger), with `predict_data.py` and `predict_demand.py` shared with the demand
forecast (`docs/methods/predict.md`, whose rules hold here unless this note says otherwise). Tests:
`tests/test_predict.py`. Replication: `replication/predict/replicate_ws.py`.

**What it is.** The ERW's own forecast of tomorrow's wind and solar output, hour by hour, with a band, and its report
card beside the operators' own forecasts where the warehouse holds them. Tier `derived`, labelled "ERW forecast": a
model's output, never a published or official figure.

## 1. The places and what each is scored against

- **The 13 EIA regions** (`region-<code>`): EIA-930's net generation from wind and from solar
  (`eia930_region_fuel_hourly`, July 2018 on). No operator's forecast is held for 12 of them; their operator rows are
  present, every number null, with the reason.
- **Texas** (`region-tex`): TEX is ERCOT alone, and EIA-930's figure equals ERCOT's own actual output to the megawatt
  in every hour both hold (`runs/c730/ws_check.py`). The operator's forecast: ERCOT's short-term wind and solar
  forecasts (STWPF, STPPF), the newest posting published at least 24 hours before the hour
  (`ercot_wind_solar_forecast`, from 27 September 2026: about two months).
- **CAISO's own output** (`grid-caiso`): its three trading hubs summed (`caiso_wind_solar_forecast`, market run
  ACTUAL, June 2023 on), against CAISO's day-ahead market forecast of the same hubs (market run DAM). EIA-930's
  California region is a larger footprint: CAISO's hubs are 60 to 92 percent of its wind and 82 to 86 percent of its
  solar, month by month. So CAISO's forecast is scored against CAISO's own actual, never against EIA-930's.

## 2. What was known when

The forecast for local day T is taken as made at 20:00 UTC on T-1, from output through day A = T-2, as the demand
forecast (h = 2). The operators' forecasts are made later, with weather: CAISO's for its day-ahead market before about
18:00 UTC on T-1, ERCOT's at least 24 hours before each hour. No weather enters the ERW's: no dated forecast of wind or
cloud is held for the regions (the NWS airport forecasts began on 26 November 2026, at one airport an ISO, and carry no
cloud cover). A test holds that no output after day T-2 moves the forecast for day T.

## 3. The methods, the choice and the band

By local hour: **yesterday** (the hour on day A); **profile7** (the hour's mean over days A-6 to A); **regression**
(least squares in MW on 1, the hour on day A, day A's mean, the hour's seven-day mean and the hour's highest over
A-13 to A, which carries new capacity; refit for every target day on the 365 days before it, at least 120; never
below zero). The choice: the lowest mean absolute error over the last two years, on the hours every candidate holds
(the operator's forecast does not restrict the choice: in Texas it is held for two months only). The band: the 10th
and 90th percentile of the method's own past errors (actual less forecast, MW) at the hour over 365 days, the low end
not clipped (a plant's net output at night is a little below zero, its own use).

The error is given in MW and as `nmae_pct`, the mean absolute error over the mean actual output of the same hours: a
percent of each hour means nothing at night. A region with no output of a fuel (the Carolinas' wind) scores zero for
every method; its choice is then a tie, broken by name.

## 4. CAISO: the output available

CAISO forecasts the output its wind and solar plants could give; its actual is net of the curtailment it orders or
the plants take. In spring, when solar is curtailed most, CAISO's forecast scored against the actual looks worse than
it is. So the same hours are also scored against the actual plus the curtailment CAISO reports
(`caiso_curtailment_intervals`: five-minute MW to 2025, hourly MWh from 2026, every reason summed; an hour of a day the
daily rows cover with no interval is zero): the cut `with_operator_available`, every method alike.

## 5. The scores

Filled in from the files after the first full build (section 6).

## 6. The files and the ledger

`site/data/predict/wind_solar.json`: for each place and fuel, the method, the forecast for the next local day with
its band and the operator's forecast where held, the summaries (last two years, the backtest, with the operator, and
for CAISO against the output available), the band's share of past hours inside it (`band_coverage`), and 35 days of
history; the score rows (columns `place, fuel, method, cut, key, hours, mae_mw, nmae_pct, held`) for the cuts all,
last_2_years, month, hour, with_operator, with_operator_month and with_operator_available.
`site/data/predict/ledger_wind_solar.csv`: every forecast as made, one row a fuel, place and UTC hour, never
rewritten. When the latest whole day held is not two days before the target day (CAISO's actual is often four days
behind), no forecast is made for that day and the file says why.
