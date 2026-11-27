# Replication: the ERW forecast (`/forecast`)

Session 10600, chain 730. Method: `docs/methods/predict.md`.

- `python warehouse/predict/run.py` rebuilds every file of `site/data/predict/` from `eia930_ba_demand_hourly` and `eia930_forecast_error_hourly` (set `ERW_DATA_ROOT` to the folder whose `warehouse/output` holds them; `--now` fixes the hour the forecast is taken as made; `--no-ledger` appends nothing to the ledger).
- `python replication/predict/export.py --place region-tex --day 2026-11-20` writes the inputs of the Stata file for one place and one target day of the backtest, and the Python forecast for that day.
- `replication/predict/predict_demand.do` rebuilds the regression for that place and day in Stata from those inputs and prints, hour by hour, its forecast beside the Python one. Not run on the machine that wrote it (no Stata there).
- `replication/predict/replicate.py` (chain 730, part F) reproduces every figure of `site/data/predict/scores.json` from the public tables.
- `replication/predict/replicate_ws.py` (session 10602) reproduces every figure of `site/data/predict/wind_solar.json` from the public tables (`eia930_region_fuel_hourly`, `caiso_wind_solar_forecast`, `ercot_wind_solar_forecast`, `caiso_curtailment_intervals`), the three methods rebuilt and the regression refitted for every target day; it imports nothing of the builder (`docs/methods/predict_wind_solar.md`).
- `replication/predict/replicate_rt.py` (session 10602) does the same for `site/data/predict/rt_price.json` from the hub price tables (`docs/methods/predict_price.md`, section 7).
- `replication/predict/replicate_net.py` (session 10602) recomputes the net demand rows of `scores.json` (series `net_demand`) from the demand of `replicate.py` and the wind and solar of `replicate_ws.py` (`docs/methods/predict.md`, section 20).
- `replication/predict/replicate_wx.py` (session 10602) refits the separate line "with the weather forecast" from the note's words (the regression's rows of `replicate.py` with the airport's temperature added; NOAA's and NWS's observations for the fit, the NWS forecast issued by 20:00 UTC the day before for the target day) and recomputes the series `demand_weather_forecast` (`docs/methods/predict.md`, section 19).
- `replicate.py` also recomputes the cuts `operator_sound` and `operator_sound_last_2_years` from the operator's filing check (`docs/methods/predict.md`, section 18).
- `replication/predict/crosscheck_ercot.py` sets ERCOT's own chart of its day-ahead (RUC) forecast's monthly error (read off the image to about 0.05 point) beside the backtest's monthly score of ERCOT's EIA-930 filing, and writes `crosscheck_ercot.csv` (method note, section 15).
