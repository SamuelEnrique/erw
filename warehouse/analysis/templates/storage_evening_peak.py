"""Battery discharge against the evening peak (CAISO)."""
import pandas as pd

from common import NoData, complete_local_days, fetch, r2, render, result  # noqa: F401

NAME = "storage_evening_peak"
TITLE = "Batteries and the evening peak"
PUBLIC = True
PARAMS = {"window": {"default": 30, "choices": [7, 30]}}
TABLES = ["caiso_battery_storage", "eia930_ciso_demand"]
TZ = "America/Los_Angeles"
METHOD = """CAISO only: EIA-930 carries no battery series for any balancing authority in the warehouse, so the batteries
are CAISO's own Today's Outlook figure (caiso_battery_storage, batteries_mw, 5-minute, positive is discharge, negative is
charging). Demand is EIA-930's CISO hourly demand (eia930_ciso_demand, demand_mw). For each Pacific hour of the day, the
chart shows the mean battery output and the mean demand over the last `window` days complete in both tables. The
headline is the mean battery output from 17:00 to 21:00 Pacific (the evening peak) over the latest 7 complete days of the
battery table; its history is the same mean for each earlier 7-day window the battery table holds (from 2025-08, a
backfill of CAISO's history files)."""


def compute(window=30, history=True):
    b = fetch("caiso_battery_storage")
    b = b[b["variable"] == "batteries_mw"]
    d = fetch("eia930_ciso_demand")
    d = d[d["variable"] == "demand_mw"]
    bdays = complete_local_days(b, TZ)
    ddays = complete_local_days(d, TZ)
    both = sorted(set(bdays) & set(ddays))
    if len(both) < window:
        raise NoData(f"{len(both)} Pacific days complete in both tables, {window} needed")
    use = both[-window:]
    bl = b.assign(day=b["ts_utc"].dt.tz_convert(TZ).dt.date, h=b["ts_utc"].dt.tz_convert(TZ).dt.hour)
    dl = d.assign(day=d["ts_utc"].dt.tz_convert(TZ).dt.date, h=d["ts_utc"].dt.tz_convert(TZ).dt.hour)
    bp = bl[bl["day"].isin(use)].groupby("h")["value"].mean()
    dp = dl[dl["day"].isin(use)].groupby("h")["value"].mean()
    frame = pd.DataFrame({"hour": bp.index, "battery_mw": [r2(v) for v in bp.values],
                          "demand_mw": [r2(dp.get(h)) for h in bp.index], "first_day": str(use[0]), "last_day": str(use[-1]),
                          "tables": "caiso_battery_storage, eia930_ciso_demand"})
    ev = bl[(bl["h"] >= 17) & (bl["h"] < 21) & bl["day"].isin(bdays)].groupby("day")["value"].mean()
    days = sorted(ev.index)
    hist = []
    for i in range(len(days) - 7, -1, -7):
        chunk = days[i:i + 7]
        if (pd.Timestamp(chunk[-1]) - pd.Timestamp(chunk[0])).days == 6:
            hist.append([f"{chunk[0]} to {chunk[-1]}", r2(ev.loc[chunk].mean())])
    hist = hist[::-1]
    if not hist:
        raise NoData("fewer than 7 consecutive complete battery days")
    cur = hist[-1]
    peak_h = int(dp.idxmax())
    chart = {"kind": "line", "x": [f"{h:02d}" for h in bp.index], "x_label": "Hour starting (Pacific)",
             "y_label": "Battery output, MW", "y2_label": "Demand, MW",
             "series": [{"name": "Batteries (mean MW)", "values": [r2(v) for v in bp.values]},
                        {"name": "Demand (mean MW)", "values": [r2(dp.get(h)) for h in bp.index], "y2": True}]}
    facts = [f"CAISO, {use[0]} to {use[-1]}: mean demand peaked in the hour starting {peak_h:02d}:00 Pacific at "
             f"{r2(dp.max())} MW, when batteries delivered a mean {r2(bp.get(peak_h))} MW; batteries delivered the most in the "
             f"hour starting {int(bp.idxmax()):02d}:00, {r2(bp.max())} MW, and charged hardest in the hour starting "
             f"{int(bp.idxmin()):02d}:00, {r2(bp.min())} MW.",
             f"Mean battery output 17:00 to 21:00 Pacific, {cur[0]}: {cur[1]} MW."]
    return result(NAME, {"window": window}, "CAISO: batteries and the evening peak",
                  f"Mean by hour of the day, {use[0]} to {use[-1]}; battery output below zero is charging", frame, TABLES,
                  chart, {"label": "mean battery output 17:00 to 21:00 Pacific, latest 7 days", "value": cur[1],
                          "unit": "MW", "period": cur[0], "history": hist[:-1]}, facts)
