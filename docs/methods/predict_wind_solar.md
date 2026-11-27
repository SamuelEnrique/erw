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

From the first full build (27 November 2026, made as at 18:00 UTC on 26 November; `runs/c730/table_ws.py`), the error
over the mean output of the same hours, in percent; the operators' first:

| Place | Fuel | With the operator: hours, ERW, operator | Against the output available: ERW, operator |
|---|---|---|---|
| Texas (ERCOT) | wind | 1,368, 52.99, 13.24 | |
| Texas (ERCOT) | solar | 1,368, 30.69, 8.26 | |
| CAISO's hubs | wind | 26,997, 50.12, 14.77 | 50.08, 14.00 |
| CAISO's hubs | solar | 26,998, 13.19, 14.11 | 16.46, 6.60 |

Where the operators' forecasts are held they are far ahead: they use the weather, the ERW's does not. CAISO's solar
looks beaten against the actual only because the actual is net of curtailment; against the output available CAISO is
at 6.6 and the ERW at 16.5.

The last two years, every place (ERW, yesterday, profile7; method chosen; the share of hours inside the band):

| Place | Wind | Solar |
|---|---|---|
| California | 40.76, 49.27, 41.76 (regression; 78.7) | 13.30, 14.89, 13.85 (regression; 75.6) |
| Carolinas | no output (all methods 0 MW) | 28.34, 33.54, 29.55 (regression; 76.5) |
| Central | 35.11, 41.45, 36.17 (regression; 77.3) | 30.03, 30.03, 31.57 (yesterday; 75.0) |
| Florida | no output | 18.02, 21.05, 18.95 (regression; 78.0) |
| Mid-Atlantic | 47.70, 58.05, 48.57 (regression; 80.2) | 27.13, 33.38, 28.55 (regression; 74.4) |
| Midwest | 40.35, 49.45, 40.83 (regression; 78.2) | 22.72, 26.90, 23.79 (regression; 71.0) |
| New England | 48.43, 63.35, 49.99 (regression; 71.4) | 37.33, 46.34, 37.93 (regression; 76.7) |
| Northwest | 33.41, 43.52, 34.87 (regression; 78.8) | 14.38, 16.30, 15.87 (regression; 75.7) |
| New York | 56.99, 71.99, 58.03 (regression; 79.7) | 97.62, 83.34, 97.62 (profile7; 99.8): EIA-930's New York solar is a few MW, and no method forecasts it usefully |
| Southeast | no output | 28.70, 32.88, 29.73 (regression; 77.9) |
| Southwest | 42.90, 52.42, 44.76 (regression; 77.9) | 15.47, 18.50, 16.61 (regression; 73.5) |
| Tennessee | no output (a few MW at most) | 34.09, 38.93, 34.61 (regression; 73.4) |
| Texas | 40.46, 49.24, 42.76 (regression; 79.8) | 21.28, 24.55, 22.08 (regression; 75.7) |
| CAISO's hubs | 48.09, 57.97, 48.98 (regression; 79.7) | 13.81, 15.51, 14.40 (regression; 76.2) |

Replication (`replication/predict/replicate_ws.py`): 12,760 of 12,760 figures equal. A tie between methods (a region
with no output) is broken by name, as the builder breaks it: an earlier run of the replication broke it by order and
differed on 44 figures of Tennessee's wind and New York's solar.

## 6. The files and the ledger

`site/data/predict/wind_solar.json`: for each place and fuel, the method, the forecast for the next local day with
its band and the operator's forecast where held, the summaries (last two years, the backtest, with the operator, and
for CAISO against the output available), the band's share of past hours inside it (`band_coverage`), and 35 days of
history; the score rows (columns `place, fuel, method, cut, key, hours, mae_mw, nmae_pct, held`) for the cuts all,
last_2_years, month, hour, with_operator, with_operator_month and with_operator_available.
`site/data/predict/ledger_wind_solar.csv`: every forecast as made, one row a fuel, place and UTC hour, never
rewritten. When the latest whole day held is not two days before the target day (CAISO's actual is often four days
behind), no forecast is made for that day and the file says why.

## 7. A day not forecast, and where each entry is shown (session 10603)

Window E's reading of the file (chain 720, requests 11 and 12 of `docs/state/data_requests_predict.md`) found two
faults of this window's. (a) The seven-day profile and the regression read every hour of the days before the target
day. On 27 November the Carolinas' and the Southwest's output had a gap (EIA-930's 18 to 20 November), so the method
chosen could not forecast the day, and the file wrote 24 rows of nulls with no reason. It now writes `tomorrow: null`
and `tomorrow_held`, which names the days whose output is missing; net demand (`predict.md` section 20) says likewise in
its own `tomorrow_held`. No method is switched in to fill the day: the method stays the one the rule chose, and a day it
cannot forecast is said to be so. (b) Each entry gains `shown_for`, the place files that show it: a region shows its
own entry, `ba-erco` shows Texas's, and `ba-ciso` shows `grid-caiso` (CAISO's own three hubs, CISO's footprint), which
no place file named before. The file also gains `cuts`, the words of the cuts its rows use. Nothing else in the file
changes (it equals the one on main once `built`, `shown_for`, `cuts` and the four mended days are set aside).
