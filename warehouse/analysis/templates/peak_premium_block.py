"""Peak premium by time-of-day block, for any ISO with 15-minute real-time prices."""
import pandas as pd

from common import ISO_LABEL, RT, NoData, complete_local_days, fetch, nodes, r2, render, result, weeks_back  # noqa: F401

NAME = "peak_premium_block"
TITLE = "Peak premium by time of day"
PUBLIC = True
ISOS = ["ercot", "caiso", "nyiso", "isone", "spp"]  # the ISOs whose real-time table holds 15-minute prices
PARAMS = {"iso": {"default": "ercot", "choices": ISOS},
          "hub": {"default": {i: RT[i][2] for i in ISOS}, "choices": "nodes of the ISO's real-time table"},
          "window": {"default": 30, "choices": [7, 30]}}
TABLES = [RT[i][0] for i in ISOS]
METHOD = """The ERCOT peak-premium method (docs/methods/ercot_peak_premium.md) applied to any ISO whose real-time
table holds 15-minute prices (ERCOT, CAISO, NYISO, ISO-NE, SPP; MISO's is hourly). Each 15-minute interval is put in a
block by the local clock hour h in which it starts: overnight (h >= 21 or h < 12), midday (12 <= h < 16) and peak
(16 <= h < 21). Over the last `window` complete local days of the hub's prices, the chart shows each block's first
quartile, median and third quartile (numpy percentiles, linear). The headline is the peak-minus-midday median spread over
the latest 7 complete days; its history is the same spread for each earlier 7-day window the warehouse holds (for ERCOT
this includes the yearly history tables, ercot_rtm_hub_prices_<year>, where present). Every interval is used; nothing is
capped."""
BLOCKS = {"overnight": lambda h: (h >= 21) | (h < 12), "midday": lambda h: (h >= 12) & (h < 16),
          "peak": lambda h: (h >= 16) & (h < 21)}


def _prices(iso, hub, history):
    table, tz, _ = RT[iso]
    df = fetch(table, node=hub)
    tables = [table]
    if history and iso == "ercot":
        import erw
        years = sorted(t for t in erw.list_tables() if t.startswith("ercot_rtm_hub_prices_20"))[-2:]
        for t in years:
            try:
                df = pd.concat([df, fetch(t, node=hub)], ignore_index=True)
                tables.append(t)
            except Exception:
                pass
        df = df.drop_duplicates(["ts_utc"])
    if df.empty:
        raise NoData(f"{table}: no rows for {hub}")
    return df.sort_values("ts_utc"), tables, tz


def _spread(p, tz):
    h = p["ts_utc"].dt.tz_convert(tz).dt.hour
    return float(p[BLOCKS["peak"](h)]["value"].median() - p[BLOCKS["midday"](h)]["value"].median())


def compute(iso="ercot", hub=None, window=30, history=True):
    hub = hub or RT[iso][2]
    df, tables, tz = _prices(iso, hub, history)
    days = complete_local_days(df, tz)
    if len(days) < window:
        raise NoData(f"{RT[iso][0]} {hub}: {len(days)} complete local days, {window} needed")
    use = days[-window:]
    loc = df["ts_utc"].dt.tz_convert(tz)
    w = df[loc.dt.date.isin(use)]
    h = w["ts_utc"].dt.tz_convert(tz).dt.hour
    rows = []
    for b, rule in BLOCKS.items():
        v = w[rule(h)]["value"]
        for stat, q in (("q1", 25), ("median", 50), ("q3", 75)):
            rows.append({"block": b, "stat": stat, "value": r2(v.quantile(q / 100)), "unit": "USD/MWh",
                         "n_intervals": int(len(v)), "table": RT[iso][0], "node": hub,
                         "first_day": str(use[0]), "last_day": str(use[-1])})
    frame = pd.DataFrame(rows)
    hist = []
    for a, b in weeks_back(days, 7):
        p = df[loc.dt.date.between(a, b)]
        hist.append([f"{a} to {b}", r2(_spread(p, tz))])
    cur = hist[-1] if hist else [f"{use[-7]} to {use[-1]}", r2(_spread(df[loc.dt.date.isin(use[-7:])], tz))]
    med = {r["block"]: r["value"] for r in rows if r["stat"] == "median"}
    label = ISO_LABEL[iso]
    chart = {"kind": "bar", "x": list(BLOCKS), "x_label": "Block (local time)", "y_label": "USD/MWh",
             "series": [{"name": s.upper() if s != "median" else "Median",
                         "values": [r["value"] for r in rows if r["stat"] == s]} for s in ("q1", "median", "q3")]}
    facts = [f"{label} {hub} real-time prices, {use[0]} to {use[-1]} ({window} days): median overnight {med['overnight']}, "
             f"midday {med['midday']}, peak {med['peak']} USD/MWh.",
             f"Peak minus midday median, {cur[0]}: {cur[1]} USD/MWh."]
    return result(NAME, {"iso": iso, "hub": hub, "window": window}, f"{label} {hub}: real-time prices by time of day",
                  f"Quartiles of 15-minute prices by block, {use[0]} to {use[-1]}, USD/MWh", frame, tables, chart,
                  {"label": "peak minus midday median, latest 7 days", "value": cur[1], "unit": "USD/MWh",
                   "period": cur[0], "history": hist[:-1]}, facts)
