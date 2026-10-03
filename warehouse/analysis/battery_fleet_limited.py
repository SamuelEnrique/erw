#!/usr/bin/env python3
"""The fleet-limited battery estimate, for review (session 74). Not a table of the live set; changes no live strategy.

Energy Research Warehouse (ERW). docs/methods/battery_stack.md, "The fleet-limited estimate (session 74, for review)".

    python warehouse/analysis/battery_fleet_limited.py

The page's model (warehouse/derived/battery_stack.py) lets one battery sell all its power as reserves at the posted
price. The whole fleet cannot sell more of a product than the market buys. So here, for each hour and product, one
battery's award per MW of its power is capped at

    cap = min(1, the MW ERCOT procures that hour / the operating battery MW in ERCOT that month)

which assumes batteries share each product in proportion to their power and between them take all of it: still
generous, before batteries were the main providers.

- Quantities: ercot_as_quantities (ERCOT's DAM Ancillary Service Plan, NP4-33-CD), the days held (from 2026-09-03).
- The fleet: storage_buildout_monthly, iso:ercot, battery_operating_mw, the day's month. A month EIA-860M has not yet
  published takes the newest month held, and the output says which month each day used.
- Prices and the program: exactly the page's (battery_stack.energy_prices, as_prices, solve_day), for both strategies
  and 2, 4 and 8 hours, each day solved twice: price-taker (no cap) and fleet-limited.

Output: warehouse/output/analysis_internal/battery_fleet_limited_ercot_daily.csv, one row per (day, strategy,
duration), USD per MW by stream under both, the caps' daily means, and the fleet month used. Never filled: a day
without every hour of a price or a quantity is left out and counted.
"""

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import battery_stack as bs  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output", "analysis_internal", "battery_fleet_limited_ercot_daily.csv")


def quantities(products):
    q = bs.pb.read_table("ercot_as_quantities")
    out = {}
    for p in products:
        x = q[(q["entity"] == p["entity"]) & (q["variable"] == "quantity_mw_plan")]
        out[p["key"]] = pd.Series(x["value"].values, index=pd.DatetimeIndex(x["ts"])).sort_index()
    return out


def fleet():
    f = bs.pb.read_table("storage_buildout_monthly")
    f = f[(f["entity"] == "iso:ercot") & (f["variable"] == "battery_operating_mw")]
    return pd.Series(f["value"].values, index=pd.DatetimeIndex(f["ts"]).strftime("%Y-%m")).sort_index()


def main():
    log = print
    m = bs.MARKETS["ercot"]
    tz = bs.pb.TZ["ercot"]
    energy = {mk: bs.energy_prices("ercot", mk, log)[0] for mk in ("rtm", "dam")}
    reserve = bs.as_prices("ercot_as_prices", m["products"])
    qty = quantities(m["products"])
    fl = fleet()
    first = min(s.index.min() for s in qty.values()).tz_convert(tz).tz_localize(None).normalize()
    last = max(s.index.max() for s in qty.values()).tz_convert(tz).tz_localize(None).normalize()
    rows, left = [], []
    for ts in pd.date_range(first, last, freq="D"):
        day = ts.strftime("%Y-%m-%d")
        hrs = bs.day_hours(day, tz)
        prods = [p for p in m["products"] if p["first"] is None or p["first"] <= day]
        pr = [reserve[p["key"]].reindex(hrs) for p in prods]
        qs = [qty[p["key"]].reindex(hrs) for p in prods]
        month = day[:7]
        fm = month if month in fl.index else fl.index[fl.index <= month].max()
        mw = float(fl[fm])
        if any(s.isna().any() for s in pr):
            left.append((day, "an ancillary price not held"))
            continue
        if any(s.isna().any() for s in qs):
            left.append((day, "a quantity not held"))
            continue
        caps = [(s.values / mw).clip(max=1) for s in qs]
        spec = tuple((p["up"], bs.required_hours(p, day)[0]) for p in prods)
        for strat, mk in bs.STRATEGIES.items():
            ep = energy[mk].reindex(hrs)
            if ep.isna().any():
                left.append((day, f"{strat}: energy not held"))
                continue
            for dur in bs.DURATIONS:
                free = bs.solve_day(ep.values, [s.values for s in pr], spec, dur)
                lim = bs.solve_day(ep.values, [s.values for s in pr], spec, dur, caps=caps)
                for name, sol in (("price_taker", free), ("fleet_limited", lim)):
                    bad = bs.check_day(sol, spec, dur)
                    if bad:
                        raise RuntimeError(f"{day} {strat} {dur}h {name}: {bad[0]}")
                    if name == "fleet_limited":
                        for j, c in enumerate(caps):
                            if (sol["awards"][j] > c + 1e-6).any():
                                raise RuntimeError(f"{day} {strat} {dur}h: an award passes its cap")
                r = dict(day=day, strategy=strat, duration_h=dur, fleet_month=fm, fleet_mw=round(mw, 1))
                for name, sol in (("price_taker", free), ("fleet_limited", lim)):
                    r[f"{name}_energy"] = round(sol["energy"], 4)
                    r[f"{name}_total"] = round(sol["total"], 4)
                    for p, v in zip(prods, sol["reserve"]):
                        r[f"{name}_{p['key']}"] = round(v, 4)
                for p, c in zip(prods, caps):
                    r[f"cap_mean_{p['key']}"] = round(float(c.mean()), 4)
                    r[f"cap_binds_hours_{p['key']}"] = int((lim["awards"][prods.index(p)] >= c - 1e-6).sum()) if c.min() < 1 else 0
                rows.append(r)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    d = pd.DataFrame(rows)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("# ERW analysis, internal, for review (session 74): the fleet-limited battery estimate against the page's price-taker, "
                "ERCOT HB_HUBAVG, USD per MW of rated power by local day (warehouse/analysis/battery_fleet_limited.py). "
                "Caps: min(1, ERCOT's DAM Ancillary Service Plan MW / ERCOT's operating battery MW of the month, EIA-860M via "
                "storage_buildout_monthly; a month not yet published takes the newest held, named in fleet_month). "
                f"Days left out: {len(left)}" + (f" ({'; '.join(f'{a}: {b}' for a, b in left[:6])})" if left else "") + "\n")
        d.to_csv(f, index=False, lineterminator="\n")
    print(f"{len(d)} rows, {d['day'].nunique()} days, {d['day'].min()} to {d['day'].max()}; left out {len(left)} -> {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
