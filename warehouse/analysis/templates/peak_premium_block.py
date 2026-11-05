"""Peak premium by time-of-day block, for any ISO with 15-minute real-time prices."""
import pandas as pd

from common import HISTORY, ISO_LABEL, RT, RT_MARKET, NoData, complete_local_days, fetch, nodes, r2, render, result, weeks_back  # noqa: F401

NAME = "peak_premium_block"
TITLE = "Peak premium by time of day"
PUBLIC = True
ISOS = ["ercot", "caiso", "nyiso", "isone", "spp"]  # the ISOs whose real-time table holds 15-minute prices
PARAMS = {"iso": {"default": "ercot", "choices": ISOS},
          "hub": {"default": {i: RT[i][2] for i in ISOS}, "choices": "nodes of the ISO's real-time table"},
          "window": {"default": 30, "choices": [7, 30]}}
TABLES = list(dict.fromkeys(RT[i][0] for i in ISOS)) + [HISTORY]
METHOD = """The ERCOT peak-premium method (docs/methods/ercot_peak_premium.md) applied to any ISO whose real-time
table holds 15-minute prices (ERCOT, CAISO, NYISO, ISO-NE, SPP; MISO's is hourly). Each 15-minute interval is put in a
block by the local clock hour h in which it starts: overnight (h >= 21 or h < 12), midday (12 <= h < 16) and peak
(16 <= h < 21). Over the last `window` complete local days of the hub's prices, the chart shows each block's first
quartile, median and third quartile (numpy percentiles, linear), in the facts and the frame. The headline is the
peak-minus-midday median spread over the latest 7 complete days; its history is the same spread for each earlier 7-day
window the warehouse holds (for ERCOT this includes the yearly history tables, ercot_rtm_hub_prices_<year>, where
present). The chart (session 533, the Roundup audit's fix 11: the chart of the week of 2026-W39 named this spread and
drew only the 30-day quartiles) is that spread for each of the latest 26 non-overlapping 7-day windows, one bar a window,
labelled by its first day, the latest bar being the headline, ringed and labelled with its figure. Every interval is
used; nothing is capped."""
BLOCKS = {"overnight": lambda h: (h >= 21) | (h < 12), "midday": lambda h: (h >= 12) & (h < 16),
          "peak": lambda h: (h >= 16) & (h < 21)}
BLOCK_HOURS = {"overnight": "overnight (21:00 to 11:59 local)", "midday": "midday (12:00 to 15:59 local)",
               "peak": "peak (16:00 to 20:59 local)"}  # session 470: the hours of BLOCKS, as words
WEEKS_SHOWN = 26  # session 533: the 7-day windows the chart draws, newest last (the flow's bars fit at most 31 places)


def _prices(iso, hub, history):
    table, tz, _ = RT[iso]
    df = fetch(table, node=hub, market=RT_MARKET[iso])
    tables = [table]
    if history and iso == "ercot":
        import erw
        # session 30: the last two years of ercot_all_hub_prices_history (market ercot_rtm, partitions by year)
        years = sorted({int(n.rsplit("_", 1)[1]) for n, (t, _) in erw.migrations().items()
                        if t == HISTORY and n.startswith("ercot_rtm_hub_prices_20")})[-2:]
        for y in years:
            try:
                df = pd.concat([df, fetch(HISTORY, node=hub, market="ercot_rtm", year=y)], ignore_index=True)
                if HISTORY not in tables:
                    tables.append(HISTORY)
            except Exception:
                pass
        df = df.drop_duplicates(["ts_utc"])
    if df.empty:
        raise NoData(f"{table}: no rows for {hub}")
    return df.sort_values("ts_utc"), tables, tz


def _medians(p, tz):
    """The peak and the midday block's median price over the rows p (session 533: kept apart for the frame)."""
    h = p["ts_utc"].dt.tz_convert(tz).dt.hour
    return float(p[BLOCKS["peak"](h)]["value"].median()), float(p[BLOCKS["midday"](h)]["value"].median())


def _spread(p, tz):
    peak, midday = _medians(p, tz)
    return float(peak - midday)


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
    hist, weekly = [], []
    for a, b in weeks_back(days, 7):
        p = df[loc.dt.date.between(a, b)]
        peak, midday = _medians(p, tz)
        hist.append([f"{a} to {b}", r2(peak - midday)])
        weekly.append({"measure": "peak minus midday median, 7 days", "period": f"{a} to {b}", "first_day": str(a),
                       "last_day": str(b), "block": "", "stat": "", "peak_median": r2(peak), "midday_median": r2(midday),
                       "value": r2(peak - midday), "unit": "USD/MWh", "n_intervals": int(len(p)), "table": RT[iso][0],
                       "node": hub})
    cur = hist[-1] if hist else [f"{use[-7]} to {use[-1]}", r2(_spread(df[loc.dt.date.isin(use[-7:])], tz))]
    med = {r["block"]: r["value"] for r in rows if r["stat"] == "median"}
    label = ISO_LABEL[iso]
    # session 533 (the Roundup audit's fix 11): the chart is the spread the headline names, one bar a 7-day window, the
    # latest the headline itself (common.headline_mark finds it there and style.py rings it); the 30-day quartiles stay
    # in the facts and the frame. Until then the chart was the quartiles alone, and the chart of the week of 2026-W39
    # named 28.08 USD/MWh, a number no bar of it held
    shown = weekly[-WEEKS_SHOWN:] if hist else []
    chart = {"kind": "bar", "x": [w["first_day"] for w in shown], "x_label": "7-day window, first day (local)",
             "y_label": "USD/MWh", "series": [{"name": "Peak minus midday median", "values": [w["value"] for w in shown]}]}
    for r in rows:
        r.update(measure=f"block quartile, {window} days", period=f"{use[0]} to {use[-1]}")
    frame = pd.DataFrame(shown + rows)
    # session 470 (roundup audit fix 12): the hours of each block, local time, in the fact itself, since another finding
    # (site/public/findings/peak_hour_moved.py) calls 10:00 to 15:59 midday
    facts = [f"{label} {hub} real-time prices, {use[0]} to {use[-1]} ({window} days): median {BLOCK_HOURS['overnight']} "
             f"{med['overnight']}, {BLOCK_HOURS['midday']} {med['midday']}, {BLOCK_HOURS['peak']} {med['peak']} USD/MWh.",
             f"Peak minus midday median, {cur[0]}: {cur[1]} USD/MWh."]
    span = f"{shown[0]['first_day']} to {shown[-1]['last_day']}" if shown else f"{use[-7]} to {use[-1]}"
    return result(NAME, {"iso": iso, "hub": hub, "window": window}, f"{label} {hub}: real-time prices by time of day",
                  f"Median 15-minute price at {BLOCK_HOURS['peak']} minus the median at {BLOCK_HOURS['midday']}, each "
                  f"7-day window, {span}, USD/MWh", frame, tables, chart,
                  {"label": "peak minus midday median, latest 7 days", "value": cur[1], "unit": "USD/MWh",
                   "period": cur[0], "history": hist[:-1]}, facts)
