"""Session 286: verify the weekly hunt's drafts of 14 October 2026 as they stand in public.scanner_drafts, the way
sessions 252 and 251 verified theirs.

This is session 251's verify_251.py, imported and run as it stands, with four changes made here and nowhere else:
  1. the drafts are those kept by fetch_drafts.py under runs/session286/drafts/<id>/, raised at or after 18:00 UTC on
     14 October 2026 (rule "hunt");
  2. a draft of a finding's pattern (one with a module and no measure family, here negative_prices) is rebuilt from
     today's tables by its finding's own compute, as session 252's verify_hunt.rebuild does; its tables are compared
     with hunt.OWN_TABLES where the pattern has an entry there;
  3. "the question asked another way" for the three families and the one finding pattern session 251 had no cut for:
     solar_capture_rate, implied_heat_rate, scarcity_hours and negative_prices;
  4. the output is runs/session286/verify_286.json.
No row of the review list is written, no publisher is asked and no model is called.
Exit 0: every draft reproduces. 1: one does not, named.
"""
import importlib.util
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while not os.path.exists(os.path.join(ROOT, "ARCHITECTURE.md")):
    ROOT = os.path.dirname(ROOT)
sys.dont_write_bytecode = True                     # the earlier folders are listed by their tests: leave no __pycache__
sys.path.insert(0, os.path.join(ROOT, "docs", "reviews", "findings-verified-2026-10-13"))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


v = _load("verify_251", os.path.join(ROOT, "docs", "reviews", "findings-verified-2026-10-13-session251", "verify_251.py"))
import verify_hunt as vh  # noqa: E402  (session 252's: the rebuild of a finding's pattern)

hunt, hm, common = v.hunt, v.hm, v.common
v.DRAFTS = os.path.join(ROOT, "runs", "session286", "drafts")
v.OUT = os.path.join(ROOT, "runs", "session286", "verify_286.json")
v.SINCE = "2026-10-14T18:00"

_family_rebuild = v.rebuild
for _P in v.PAT.values():
    _P.setdefault("fn", None)                      # verify_251's main reads P["fn"]; a finding's pattern has none


class SubsetOf(list):
    """OWN_TABLES's entry for a finding's pattern. Since session 258 a draft names, of those, only the tables that
    brought rows of its claim's years (hunt.tables_used), so the draft's list is compared as a part of this one."""
    def __eq__(self, other):
        return bool(other) and set(other) <= set(self)

    __hash__ = None


def rebuild(P, region):
    """A family's rebuild is session 251's; a finding's pattern is rebuilt by its finding's compute (session 252), with
    no second number, and the tables its OWN_TABLES entry names (or the draft's own, said so in the report)."""
    if P.get("fn"):
        return _family_rebuild(P, region)
    series = vh.rebuild(P, region)
    own = hunt.OWN_TABLES.get(P["module"], {}).get(hunt.grid_of(region))
    return series, {}, SubsetOf(own) if own else None


v.rebuild = rebuild


# ---------------------------------------------------------------------------------------------------------------------
# the other cuts session 251 did not have: each returns {name: {year: value}}
# ---------------------------------------------------------------------------------------------------------------------
def node_rows(region):
    return next(g for r, _, _, g, _ in hm.price_nodes(None, zones=True, hubs=True) if r == region)


def cut_heat(region):
    gas = hm.series("eia_fuel_spot_prices", None, variables=["spot_price"], entities=["eia:henry_hub"])
    hh = {t.strftime("%Y-%m-%d"): x for t, x in zip(gas["ts"], gas["value"]) if x > 0}
    g = node_rows(region)
    out = {}
    for market, name in (("rt", "the mean daily implied heat rate (real time), MMBtu per MWh"), ("da", "the median daily implied heat rate, day-ahead, MMBtu per MWh")):
        day = g.dropna(subset=[market]).groupby("day").agg(p=(market, "mean"), hours=(market, "size"), year=("year", "first"))
        day = day[day["hours"] >= 20]
        day["hh"] = day.index.map(hh)
        day = day.dropna(subset=["hh"])
        r = day["p"] / day["hh"]
        out[name] = {str(int(y)): float(r[s.index].mean() if market == "rt" else np.median(r[s.index])) for y, s in day.groupby("year")}
    out["Henry Hub, the year's mean of the days held, USD per MMBtu"] = {str(int(y)): float(np.mean([x for t, x in hh.items() if t[:4] == str(y)]))
                                                                       for y in sorted({int(t[:4]) for t in hh})}
    return out


def cut_solar(region):
    V = ["solar_revenue_per_mw", "solar_energy_per_mw", "solar_flat_price", "solar_hours"]
    m = hm.series("merchant_revenue_monthly", None, variables=V)
    m = m[m["entity"].str.startswith(region + ":")]
    w = m.pivot_table(index="ts", columns="variable", values="value").dropna(subset=V)
    y = w.groupby(w.index.year)
    out = {"the price a solar MWh earned, USD per MWh (revenue over energy)": {str(int(k)): float(s["solar_revenue_per_mw"].sum() / s["solar_energy_per_mw"].sum()) for k, s in y},
           "the time-weighted average price, USD per MWh": {str(int(k)): float((s["solar_flat_price"] * s["solar_hours"]).sum() / s["solar_hours"].sum()) for k, s in y},
           "the capture rate by the unweighted mean of the year's monthly rates, percent": {
               str(int(k)): float(((s["solar_revenue_per_mw"] / s["solar_energy_per_mw"]) / s["solar_flat_price"] * 100).mean()) for k, s in y}}
    return out


def cut_scarcity(region):
    a = hm.series("ercot_rtm_price_adders", None, variables=["rtorpa_mean"], entities=["ercot:system"])
    a["year"] = a["ts"].dt.tz_convert(hm.TZ["ercot"]).dt.year
    return {"hours with the adder above USD 1 per MWh, percent": {str(int(k)): float((s["value"] > 1).mean() * 100) for k, s in a.groupby("year")},
            "hours with the adder above USD 10 per MWh, percent": {str(int(k)): float((s["value"] > 10).mean() * 100) for k, s in a.groupby("year")},
            "the year's mean adder, USD per MWh": {str(int(k)): float(s["value"].mean()) for k, s in a.groupby("year")}}


def cut_negative_hub(region):
    node = {"ercot_houston": "HB_HOUSTON", "ercot_north": "HB_NORTH", "ercot_south": "HB_SOUTH", "ercot_west": "HB_WEST"}.get(region)
    if node is None:
        return {}
    d = common.read_table("ercot_all_hub_prices_history", None, usecols=["ts_utc", "value", "market", "node"],
                          keep=lambda c: (c["market"] == "ercot_rtm") & (c["node"] == node))
    d["value"] = d["value"].astype(float)
    t = common.to_utc(d["ts_utc"])
    d["year"] = t.dt.tz_convert(hm.TZ["ercot"]).dt.year
    d["hour"] = t.dt.floor("h")
    h = d.groupby(["year", "hour"], as_index=False)["value"].mean()
    return {"15-minute intervals below zero, percent of the year's intervals": {str(int(y)): float((s["value"] < 0).mean() * 100) for y, s in d.groupby("year")},
            "hours with a mean price below minus USD 10, percent of the year's hours": {str(int(y)): float((s["value"] < -10).mean() * 100) for y, s in h.groupby("year")}}


v.CUTS.update({"implied_heat_rate": cut_heat, "solar_capture_rate": cut_solar, "scarcity_hours": cut_scarcity})
_cuts_for = v.cuts_for


def cuts_for(P, region, c):
    if P.get("fn"):
        return _cuts_for(P, region, c)
    s = 1 if c["change"] > 0 else -1
    out = []
    for name, series in (cut_negative_hub(region) if P["name"] == "negative_prices" else {}).items():
        a, b = series.get(c["first_year"]), series.get(c["last_year"])
        row = {"name": name, "by_year": {k: series[k] for k in sorted(series)}, "first": a, "last": b}
        if a is not None and b is not None:
            row["change"], row["same_direction"] = b - a, (b - a) * s > 0
        out.append(row)
    return out


v.cuts_for = cuts_for

if __name__ == "__main__":
    sys.exit(v.main())
