"""Chokepoint transits (internal: IMF PortWatch terms unconfirmed)."""
import pandas as pd

from common import NoData, fetch, r2, render, result  # noqa: F401

NAME = "chokepoint_transits"
TITLE = "Tanker transits at the chokepoints"
PUBLIC = False  # portwatch_chokepoint_transits is licensed internal (session 8 ruling): never published
POINTS = {"chokepoint6": "Strait of Hormuz", "chokepoint1": "Suez Canal", "chokepoint2": "Panama Canal"}
PARAMS = {"chokepoint": {"default": "chokepoint6", "choices": list(POINTS)}, "window": {"default": 90, "choices": [30, 90, 365]},
          "vessels": {"default": "n_tanker", "choices": ["n_tanker", "n_total"]}}
TABLES = ["portwatch_chokepoint_transits"]
METHOD = """IMF PortWatch daily vessel transits (portwatch_chokepoint_transits) at one chokepoint: tankers or all
vessels per day over the last `window` days, with the 7-day mean. The headline is the mean daily transits over the latest
7 days; its history is the same mean for each earlier 7-day window since 2019. Internal: the table's license is internal
until the IMF's terms are confirmed, so this template runs only on the warehouse's own machines, never on the site, in
the email or as the chart of the week."""


def compute(chokepoint="chokepoint6", window=90, vessels="n_tanker", history=True):
    d = fetch("portwatch_chokepoint_transits")
    s = d[(d["entity"] == f"portwatch:{chokepoint}") & (d["variable"] == vessels)].sort_values("ts_utc")
    if len(s) < window:
        raise NoData(f"{len(s)} days")
    w = s.tail(window)
    roll = s["value"].rolling(7).mean()
    frame = pd.DataFrame({"day": w["ts_utc"].dt.strftime("%Y-%m-%d"), "transits": w["value"].astype(int),
                          "mean_7d": [r2(v) for v in roll.tail(window)], "variable": vessels,
                          "table": "portwatch_chokepoint_transits"})
    vals = s["value"].tolist()
    dates = s["ts_utc"].dt.strftime("%Y-%m-%d").tolist()
    hist = [[f"{dates[i]} to {dates[i + 6]}", r2(sum(vals[i:i + 7]) / 7)] for i in range(len(vals) - 7, -1, -7)][::-1]
    cur = hist[-1]
    name = POINTS[chokepoint]
    chart = {"kind": "line", "x_time": True, "x": w["ts_utc"].dt.strftime("%Y-%m-%dT00:00:00Z").tolist(),
             "y_label": "Transits per day",
             "series": [{"name": "Daily", "values": w["value"].astype(int).tolist()},
                        {"name": "7-day mean", "values": [r2(v) for v in roll.tail(window)]}]}
    facts = [f"{name}, {vessels}: mean daily transits over {cur[0]} were {cur[1]}."]
    return result(NAME, {"chokepoint": chokepoint, "window": window, "vessels": vessels}, f"{name}: vessel transits",
                  f"{'Tankers' if vessels == 'n_tanker' else 'All vessels'} per day, last {window} days", frame, TABLES,
                  chart, {"label": "mean daily transits, latest 7 days", "value": cur[1], "unit": "transits per day",
                          "period": cur[0], "history": hist[:-1]}, facts, extra_source="Internal: not for publication.")
