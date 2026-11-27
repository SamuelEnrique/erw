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

## 8. More places: the authorities, and a choice mended (session 10603)

Samuel's order of 27 November 2026 ("more places"). Window A's landing 20 wrote `eia930_ba_wind_solar_hourly` (data
request 10): each authority's net generation from wind and from solar, July 2018 on. `wind_solar.json` now carries 35
more entries, one for every authority among the demand forecast's 64 places that the table holds (`BA_PLACES`), with
the same methods, choice, band and scores as the regions, on each authority's own clock. Left out: the six
authorities that are each a whole region (ERCO, ISNE, NYIS, PJM, SOCO, TVA), which their region's entry shows (its
`shown_for` names them), and CISO, which `grid-caiso` shows. A fuel an authority reports on no hour of EIA-930 (a
utility with no wind plant) is `not held` in this file; for net demand it is taken as zero (`predict.md` section 26).
No operator's forecast of an authority's wind or solar is held. The 14 entries of before are unchanged but for the
choice mended below; the file grows from 2.7 to 7.6 MB.

**A choice mended.** The rule picks the method with the lowest mean absolute error over the last two years. It compared
the errors after rounding them to 0.1 MW, so where a place's output is a few MW every method rounded to the same figure
and the tie went to `profile7` by name, the worse method. It now compares the unrounded errors (a true tie still goes
by name); the printed errors stay rounded. Two entries already on main change: New York's solar (`profile7` to
`yesterday`, 97.6 to 83.3 percent of the mean output) and Tennessee's wind (a few MW at most; `profile7` to
`yesterday`). Five authorities added would have taken the worse method too (AVA, CPLW, PSEI, SEC and WALC solar).

From the build of 27 November 2026 (made as at 18:00 UTC on 26 November), the last two years, the error over the mean
output of the same hours (percent), each fuel the authority reports:

| Authority | Fuel | Method | ERW, yesterday, profile7 | Band inside % |
|---|---|---|---|---:|
| AECI | wind | regression | 58.86, 73.44, 59.29 | 78.0 |
| AVA | wind | regression | 81.3, 96.68, 82.86 | 80.6 |
| AVA | solar | regression | 37.35, 41.74, 37.47 | 86.2 |
| AZPS | wind | regression | 55.72, 68.14, 59.48 | 73.0 |
| AZPS | solar | regression | 19.31, 22.25, 19.97 | 74.5 |
| BANC | solar | regression | 21.09, 23.1, 21.34 | 76.8 |
| BPAT | wind | profile7 | 89.63, 106.66, 89.63 | 79.2 |
| BPAT | solar | regression | 27.15, 31.04, 27.95 | 74.6 |
| CHPD | wind | regression | 104.76, 120.99, 105.32 | 80.8 |
| CPLE | solar | regression | 31.29, 37.19, 32.49 | 78.3 |
| CPLW | solar | yesterday | 34.55, 34.55, 41.98 | 92.7 |
| DUK | solar | regression | 32.26, 39.28, 33.34 | 82.7 |
| EPE | solar | regression | 22.67, 27.16, 23.18 | 64.6 |
| FMPP | solar | regression | 29.4, 34.3, 30.2 | 77.6 |
| FPC | solar | regression | 24.07, 28.04, 25.07 | 82.8 |
| FPL | solar | regression | 17.69, 20.68, 18.71 | 77.6 |
| IID | solar | regression | 21.37, 24.25, 21.77 | 73.4 |
| IPCO | wind | regression | 65.63, 83.41, 67.08 | 81.2 |
| IPCO | solar | regression | 26.36, 30.93, 27.71 | 81.8 |
| JEA | solar | regression | 36.95, 40.8, 38.31 | 79.6 |
| LDWP | wind | regression | 54.53, 66.55, 57.67 | 73.2 |
| LDWP | solar | regression | 16.72, 19.55, 17.71 | 66.9 |
| LGEE | solar | regression | 38.49, 40.6, 38.64 | 79.2 |
| MISO | wind | regression | 40.71, 50.11, 41.21 | 78.2 |
| MISO | solar | regression | 22.56, 26.63, 23.61 | 71.0 |
| NEVP | wind | regression | 91.56, 106.29, 97.39 | 78.9 |
| NEVP | solar | regression | 16.72, 19.12, 17.91 | 76.9 |
| NWMT | wind | regression | 53.13, 66.17, 54.15 | 77.4 |
| NWMT | solar | regression | 33.82, 40.24, 34.67 | 84.9 |
| PACE | wind | profile7 | 46.44, 57.84, 46.44 | 74.1 |
| PACE | solar | regression | 20.74, 23.9, 22.3 | 74.8 |
| PACW | wind | regression | 92.12, 108.97, 93.01 | 75.2 |
| PACW | solar | regression | 24.7, 28.05, 25.53 | 82.6 |
| PNM | wind | regression | 53.41, 64.82, 54.2 | 80.7 |
| PNM | solar | regression | 19.46, 22.99, 20.36 | 80.5 |
| PSCO | wind | regression | 43.97, 56.99, 45.74 | 79.5 |
| PSCO | solar | profile7 | 30.11, 36.67, 30.11 | 76.8 |
| PSEI | wind | regression | 73.14, 90.04, 73.97 | 80.4 |
| PSEI | solar | regression | 33.67, 37.06, 33.69 | 84.8 |
| SC | solar | regression | 33.94, 38.62, 35.46 | 80.7 |
| SCEG | solar | regression | 32.41, 38.03, 34.17 | 78.4 |
| SEC | solar | yesterday | 44.71, 44.71, 51.66 | 95.4 |
| SRP | wind | regression | 69.88, 83.82, 72.84 | 75.2 |
| SRP | solar | regression | 26.49, 32.64, 27.91 | 74.7 |
| SWPP | wind | regression | 35.11, 41.48, 36.29 | 77.5 |
| SWPP | solar | yesterday | 29.48, 29.48, 31.67 | 75.2 |
| TAL | solar | regression | 36.7, 42.53, 38.14 | 87.6 |
| TEC | solar | regression | 27.23, 32.45, 28.42 | 76.1 |
| TEPC | wind | regression | 49.27, 60.94, 51.07 | 80.9 |
| TEPC | solar | regression | 18.89, 22.25, 19.96 | 83.0 |
| WALC | wind | regression | 79.44, 95.41, 83.15 | 80.0 |
| WALC | solar | regression | 30.55, 34.88, 30.63 | 79.5 |

What it says: as for the regions, the ERW reads no weather, so its wind forecast misses by half to all of the mean
output (MISO 40.7, SWPP 35.1, BPAT 89.6, NEVP 91.6 percent) and its solar forecast by a fifth to a third; the
regression beats yesterday's output in nearly every case, and the seven-day profile is as good where output is small
and regular. No operator's forecast is held to set beside these.

Replication (`replication/predict/replicate_ws.py`, which now reads the authority table on each authority's clock and
chooses on the unrounded error): its count on the 49 places is in the progress file and landing row 10.
