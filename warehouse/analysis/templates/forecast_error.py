"""Day-ahead demand forecast error by ISO (EIA-930)."""
import pandas as pd

from common import NoData, fetch, r2, render, result  # noqa: F401

NAME = "forecast_error"
TITLE = "Demand forecast error"
PUBLIC = True
BAS = {"erco": "ERCOT", "ciso": "CAISO", "nyis": "NYISO", "miso": "MISO", "swpp": "SPP", "isne": "ISO-NE", "pjm": "PJM",
       "us48": "Lower 48"}
PARAMS = {"ba": {"default": "erco", "choices": list(BAS)}, "window": {"default": 30, "choices": [7, 30]}}
TABLES = [f"eia930_{b}_demand" for b in BAS]
METHOD = """From EIA-930 (EIA's Hourly Electric Grid Monitor), each balancing authority's day-ahead demand forecast
(demand_forecast_mw) against its demand (demand_mw), hour by hour. For each UTC day with all 24 hours of both, the mean
absolute percentage error, MAPE = mean(|forecast - demand| / demand) x 100, and the mean signed error (forecast minus
demand, MW; positive means the forecast was high). The chart is the daily MAPE over the last `window` complete days. The
headline is the MAPE over the latest 7 complete days; its history is the MAPE of each earlier 7-day window in the table.
EIA publishes the operators' own forecasts; the ERW does not forecast."""


def compute(ba="erco", window=30, history=True):
    t = f"eia930_{ba}_demand"
    d = fetch(t)
    p = d.pivot_table(index="ts_utc", columns="variable", values="value").dropna(subset=["demand_mw", "demand_forecast_mw"])
    p = p[p["demand_mw"] > 0]
    p = p.assign(ape=(p["demand_forecast_mw"] - p["demand_mw"]).abs() / p["demand_mw"] * 100,
                 err=p["demand_forecast_mw"] - p["demand_mw"], day=p.index.date)
    full = p.groupby("day").size()
    days = sorted(full[full == 24].index)
    if len(days) < window:
        raise NoData(f"{t}: {len(days)} complete days, {window} needed")
    p = p[p["day"].isin(days)]
    daily = p.groupby("day").agg(mape=("ape", "mean"), mean_error_mw=("err", "mean"))
    use = days[-window:]
    w = daily.loc[use]
    frame = pd.DataFrame({"day": [str(x) for x in w.index], "mape_pct": [r2(v) for v in w["mape"]],
                          "mean_error_mw": [r2(v) for v in w["mean_error_mw"]], "table": t})
    hist = []
    for i in range(len(days) - 7, -1, -7):
        chunk = days[i:i + 7]
        hist.append([f"{chunk[0]} to {chunk[-1]}", r2(p[p["day"].isin(chunk)]["ape"].mean())])
    hist = hist[::-1]
    cur = hist[-1]
    worst = w["mape"].idxmax()
    name = BAS[ba]
    chart = {"kind": "line", "x_time": True, "x": [f"{x}T00:00:00Z" for x in w.index], "y_label": "MAPE, %",
             "series": [{"name": "Daily MAPE", "values": [r2(v) for v in w["mape"]]}]}
    facts = [f"{name} day-ahead demand forecast, {use[0]} to {use[-1]}: the daily MAPE was highest on {worst}, "
             f"{r2(w['mape'].max())}%, and lowest on {w['mape'].idxmin()}, {r2(w['mape'].min())}%.",
             f"MAPE over {cur[0]}: {cur[1]}%."]
    return result(NAME, {"ba": ba, "window": window}, f"{name}: how far off was the day-ahead demand forecast?",
                  f"Daily mean absolute percentage error, {use[0]} to {use[-1]} (UTC days)", frame, [t], chart,
                  {"label": "demand forecast MAPE, latest 7 days", "value": cur[1], "unit": "%", "period": cur[0],
                   "history": hist[:-1]}, facts)
