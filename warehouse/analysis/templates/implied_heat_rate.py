"""Implied heat rate: the day-ahead price over Henry Hub gas."""
import pandas as pd

from common import ISO_LABEL, RT, NoData, fetch, r2, render, result  # noqa: F401

NAME = "implied_heat_rate"
TITLE = "Implied heat rate"
PUBLIC = True
ISOS = ["ercot", "caiso", "nyiso", "miso", "spp", "isone"]
PARAMS = {"iso": {"default": "ercot", "choices": ISOS},
          "hub": {"default": {i: RT[i][2] for i in ISOS}, "choices": "hubs of the ISO's trader view table"},
          "window": {"default": 30, "choices": [7, 30]}}
TABLES = [f"{i}_trader_daily" for i in ISOS] + ["eia_fuel_spot_prices"]
METHOD = """The trader view's implied heat rate (docs/methods/trader_view.md), read from <iso>_trader_daily: the hub's
day-ahead daily mean price over the Henry Hub spot price of the operating day, or of the latest trading day up to 4 days
before it, in MMBtu/MWh. It shows how many MMBtu of gas a MWh of power sells for; it is not any plant's heat rate and
ignores the basis between Henry Hub and the ISO's own gas hubs. The chart is the daily value over the last `window`
operating days in the table. The headline is the mean over the latest 7 operating days; its history is the mean of each
earlier 7-day run of operating days in the table (the table grows every day from session 19)."""


def compute(iso="ercot", hub=None, window=30, history=True):
    hub = hub or RT[iso][2]
    t = f"{iso}_trader_daily"
    d = fetch(t, node=hub)
    s = d[d["variable"] == "implied_heat_rate"].sort_values("ts_utc")
    if len(s) < min(window, 7):
        raise NoData(f"{t} {hub}: {len(s)} days of implied_heat_rate")
    w = s.tail(window)
    frame = pd.DataFrame({"day": w["ts_utc"].dt.strftime("%Y-%m-%d"), "implied_heat_rate": [r2(v) for v in w["value"]],
                          "unit": "MMBtu/MWh", "table": t, "node": hub})
    vals = s["value"].tolist()
    dates = s["ts_utc"].dt.strftime("%Y-%m-%d").tolist()
    hist = []
    for i in range(len(vals) - 7, -1, -7):
        hist.append([f"{dates[i]} to {dates[i + 6]}", r2(sum(vals[i:i + 7]) / 7)])
    hist = hist[::-1]
    cur = hist[-1]
    label = ISO_LABEL[iso]
    top = w.loc[w["value"].idxmax()]
    chart = {"kind": "line", "x_time": True, "x": w["ts_utc"].dt.strftime("%Y-%m-%dT00:00:00Z").tolist(),
             "y_label": "MMBtu/MWh", "series": [{"name": f"{hub} implied heat rate", "values": [r2(v) for v in w["value"]]}]}
    facts = [f"{label} {hub}, {dates[-len(w)]} to {dates[-1]}: the implied heat rate peaked at {r2(top['value'])} MMBtu/MWh "
             f"on {top['ts_utc']:%Y-%m-%d}.",
             f"Mean implied heat rate, {cur[0]}: {cur[1]} MMBtu/MWh."]
    return result(NAME, {"iso": iso, "hub": hub, "window": window}, f"{label} {hub}: implied heat rate",
                  f"Day-ahead daily mean over Henry Hub spot, {dates[-len(w)]} to {dates[-1]}", frame,
                  [t, "eia_fuel_spot_prices"], chart,
                  {"label": "mean implied heat rate, latest 7 operating days", "value": cur[1], "unit": "MMBtu/MWh",
                   "period": cur[0], "history": hist[:-1]}, facts)
