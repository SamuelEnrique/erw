# Replication: the ERW forecast (`/forecast`)

Session 10600, chain 730. Method: `docs/methods/predict.md`.

- `python warehouse/predict/run.py` rebuilds every file of `site/data/predict/` from `eia930_ba_demand_hourly` and `eia930_forecast_error_hourly` (set `ERW_DATA_ROOT` to the folder whose `warehouse/output` holds them; `--now` fixes the hour the forecast is taken as made; `--no-ledger` appends nothing to the ledger).
- `python replication/predict/export.py --place region-tex --day 2026-11-20` writes the inputs of the Stata file for one place and one target day of the backtest, and the Python forecast for that day.
- `replication/predict/predict_demand.do` rebuilds the regression for that place and day in Stata from those inputs and prints, hour by hour, its forecast beside the Python one. Not run on the machine that wrote it (no Stata there).
- `replication/predict/replicate.py` (chain 730, part F) reproduces every figure of `site/data/predict/scores.json` from the public tables.
- `replication/predict/crosscheck_ercot.py` sets ERCOT's own chart of its day-ahead (RUC) forecast's monthly error (read off the image to about 0.05 point) beside the backtest's monthly score of ERCOT's EIA-930 filing, and writes `crosscheck_ercot.csv` (method note, section 15).
