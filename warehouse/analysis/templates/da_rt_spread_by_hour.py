"""Day-ahead against real-time spread by hour of day."""
import pandas as pd

from common import DA, DA_MARKET, ISO_LABEL, RT, RT_MARKET, NoData, complete_local_days, fetch, r2, render, result, weeks_back  # noqa: F401

NAME = "da_rt_spread_by_hour"
TITLE = "Day-ahead minus real-time, by hour"
PUBLIC = True
ISOS = ["ercot", "caiso", "nyiso", "miso", "isone", "spp"]
PARAMS = {"iso": {"default": "ercot", "choices": ISOS},
          "hub": {"default": {i: RT[i][2] for i in ISOS}, "choices": "nodes in both the ISO's day-ahead and real-time tables"},
          "window": {"default": 30, "choices": [7, 30]}}
TABLES = list(dict.fromkeys([DA[i] for i in ISOS] + [RT[i][0] for i in ISOS]))
METHOD = """For one hub, the day-ahead hourly price minus the real-time price of the same hour, where the real-time
price of an hour is the mean of the table's intervals in that hour (15-minute or 5-minute means, or the hourly price
itself). Only hours present in both tables count, and only local days complete in both. The chart is the mean spread
for each local hour of the day over the last `window` complete days (positive: day-ahead above real-time). The headline
is the mean spread over all hours of the latest 7 complete days; its history is the same mean for each earlier 7-day
window the tables hold."""


def _hourly(iso, hub):
    da = fetch(DA[iso], node=hub, market=DA_MARKET[iso])[["ts_utc", "value"]].rename(columns={"value": "da"})
    rt = fetch(RT[iso][0], node=hub, market=RT_MARKET[iso])
    rt = rt.assign(hour=rt["ts_utc"].dt.floor("h")).groupby("hour")["value"].mean().rename("rt").reset_index()
    tz = RT[iso][1]
    days = sorted(set(complete_local_days(fetch(DA[iso], node=hub, market=DA_MARKET[iso]), tz)) &
                  set(complete_local_days(fetch(RT[iso][0], node=hub, market=RT_MARKET[iso]), tz)))
    m = da.merge(rt, left_on="ts_utc", right_on="hour", how="inner")
    m = m.assign(spread=m["da"] - m["rt"], day=m["ts_utc"].dt.tz_convert(tz).dt.date,
                 h=m["ts_utc"].dt.tz_convert(tz).dt.hour)
    return m[m["day"].isin(days)], days


def compute(iso="ercot", hub=None, window=30, history=True):
    hub = hub or RT[iso][2]
    m, days = _hourly(iso, hub)
    if len(days) < window:
        raise NoData(f"{ISO_LABEL[iso]} {hub}: {len(days)} complete days in both tables, {window} needed")
    use = days[-window:]
    w = m[m["day"].isin(use)]
    by = w.groupby("h")["spread"].mean()
    frame = pd.DataFrame({"hour": by.index, "mean_spread": [r2(v) for v in by.values], "unit": "USD/MWh",
                          "tables": f"{DA[iso]}, {RT[iso][0]}", "node": hub, "first_day": str(use[0]),
                          "last_day": str(use[-1])})
    hist = [[f"{a} to {b}", r2(m[m["day"].between(a, b)]["spread"].mean())] for a, b in weeks_back(days, 7)]
    if not hist:
        raise NoData("fewer than 7 complete days")
    cur = hist[-1]
    label = ISO_LABEL[iso]
    top = by.idxmax(), r2(by.max())
    low = by.idxmin(), r2(by.min())
    chart = {"kind": "bar", "x": [f"{h:02d}" for h in by.index], "x_label": "Hour starting (local)", "y_label": "USD/MWh",
             "series": [{"name": "Day-ahead minus real-time", "values": [r2(v) for v in by.values]}]}
    facts = [f"{label} {hub}, {use[0]} to {use[-1]}: the mean day-ahead minus real-time spread was highest in the hour "
             f"starting {top[0]:02d}:00 local, {top[1]} USD/MWh, and lowest in the hour starting {low[0]:02d}:00, {low[1]} USD/MWh.",
             f"Mean spread over all hours, {cur[0]}: {cur[1]} USD/MWh."]
    return result(NAME, {"iso": iso, "hub": hub, "window": window}, f"{label} {hub}: day-ahead minus real-time by hour",
                  f"Mean spread for each local hour, {use[0]} to {use[-1]}, USD/MWh", frame, [DA[iso], RT[iso][0]], chart,
                  {"label": "mean day-ahead minus real-time spread, latest 7 days", "value": cur[1], "unit": "USD/MWh",
                   "period": cur[0], "history": hist[:-1]}, facts)
