#!/usr/bin/env python3
"""The fleet-limited battery estimate for the two grids in review, New York and SPP (session 100). Analysis only: it
writes no table of the live set and changes no strategy of the page.

Energy Research Warehouse (ERW). docs/methods/reserve_quantities_nyiso_spp.md.

    python warehouse/analysis/battery_fleet_limited_review.py [nyiso|spp]

The page's model (warehouse/derived/battery_stack.py, REVIEW_MARKETS) lets one battery sell all its power as reserves at
the posted price. The whole fleet cannot sell more of a product than the market buys. So, as session 74 did for ERCOT
(warehouse/analysis/battery_fleet_limited.py), for each hour and product one battery's award per MW of its power is
capped at

    cap = min(1, the MW the operator procures that hour / the operating battery MW of the grid that month)

which assumes batteries share each product in proportion to their power and between them take all of it.

Quantities:
- SPP: spp_as_quantities, the MW of Regulation-Up, Regulation-Down, Spinning and Supplemental Reserve cleared in the
  Day-Ahead Market each hour (entity spp:SPP), from 2024-09-01.
- New York, spinning reserve: NYISO publishes no hourly quantity. It publishes the requirement: "10-Minute Spinning
  Reserve ... NYCA ... 655 MW" (NYISO Locational Reserve Requirements, https://www.nyiso.com/documents/20142/3694424/
  Locational-Reserves-Requirements.pdf, read 2026-10-04). The cap uses 655 MW in every hour: the requirement of the
  whole control area, the widest of the nested requirements a battery in New York City counts toward.
- New York, regulation: the tariff says "The ISO shall establish and post a target level of Regulation Service for each
  hour" (MST Rate Schedule 3, section 15.3.7). The posted targets were not found at an address this machine could read.
  No quantity is held, so no cap can be computed. Two cases are solved and both written, and neither is the estimate:
      fleet_limited      regulation not capped: an upper bound
      no_regulation      regulation not sold at all: a lower bound
The fleet: storage_buildout_monthly, battery_operating_mw of the day's month; a month EIA-860M has not yet published takes
the newest month held, named in the output.

Prices and the program are exactly the page's (battery_stack.energy_prices, as_prices, solve_day), both strategies, 2, 4
and 8 hours. A day whose every cap is 1 is not solved twice: with no cap that binds, the fleet-limited program is the
price-taker's, and solve_day's own test holds that. Never filled: a day without every hour of a price or a quantity is
left out and counted.

Output: warehouse/output/analysis_internal/battery_fleet_limited_<grid>_daily.csv (not in git), one row per (day,
strategy, duration), USD per MW by stream under each case, the caps' daily means and the fleet month used; and a
summary by year on the terminal.
"""

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import battery_stack as bs  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output", "analysis_internal", "battery_fleet_limited_{}_daily.csv")
NYISO_SPIN_MW = 655.0  # NYISO Locational Reserve Requirements: NYCA 10-Minute Spinning Reserve
QUANTITY = {
    "spp": dict(table="spp_as_quantities", entity="spp:SPP",
                variables={"regup": "quantity_mw_dam_regup", "regdn": "quantity_mw_dam_regdn", "spin": "quantity_mw_dam_spin", "supp": "quantity_mw_dam_supp"}),
    "nyiso": dict(constant={"spin": NYISO_SPIN_MW}, not_held=["reg"]),
}


def quantities(iso, products):
    """{product key: hourly Series of MW, a constant, or None when no quantity is held}."""
    q = QUANTITY[iso]
    out = {}
    table = bs.pb.read_table(q["table"]) if "table" in q else None
    for p in products:
        k = p["key"]
        if k in q.get("constant", {}):
            out[k] = q["constant"][k]
        elif k in q.get("not_held", []):
            out[k] = None
        else:
            x = table[(table["entity"] == q["entity"]) & (table["variable"] == q["variables"][k])]
            out[k] = pd.Series(x["value"].values, index=pd.DatetimeIndex(x["ts"])).sort_index()
    return out


def fleet(iso):
    f = bs.pb.read_table("storage_buildout_monthly")
    f = f[(f["entity"] == f"iso:{iso}") & (f["variable"] == "battery_operating_mw")]
    return pd.Series(f["value"].values, index=pd.DatetimeIndex(f["ts"]).strftime("%Y-%m")).sort_index()


def caps_of(prods, qty, hrs, mw):
    """One list of hourly caps per product (1 everywhere where no quantity is held), and whether a quantity is missing."""
    caps, missing = [], False
    for p in prods:
        q = qty[p["key"]]
        if q is None:
            caps.append(np.ones(len(hrs)))
        elif isinstance(q, float):
            caps.append(np.full(len(hrs), min(1.0, q / mw)))
        else:
            s = q.reindex(hrs)
            if s.isna().any():
                missing = True
            caps.append((s.values / mw).clip(max=1))
    return caps, missing


def run(iso, log=print):
    m = bs.REVIEW_MARKETS[iso]
    tz = bs.pb.TZ[iso]
    energy = {mk: bs.energy_prices(iso, mk, log)[0] for mk in ("rtm", "dam")}
    reserve = bs.as_prices(m["as_table"], m["products"])
    qty = quantities(iso, m["products"])
    fl = fleet(iso)
    first = pd.Timestamp(m["start"])
    last = min(s.index.max() for s in reserve.values()).tz_convert(tz).tz_localize(None).normalize()
    unheld = [p["key"] for p in m["products"] if qty[p["key"]] is None]
    rows, left = [], []
    for ts in pd.date_range(first, last, freq="D"):
        day = ts.strftime("%Y-%m-%d")
        hrs = bs.day_hours(day, tz)
        prods = [p for p in m["products"] if p["first"] is None or p["first"] <= day]
        pr = [reserve[p["key"]].reindex(hrs) for p in prods]
        if any(s.isna().any() for s in pr):
            left.append((day, "an ancillary price not held"))
            continue
        month = day[:7]
        fm = month if month in fl.index else fl.index[fl.index <= month].max()
        mw = float(fl[fm])
        caps, missing = caps_of(prods, qty, hrs, mw)
        if missing:
            left.append((day, "a quantity not held"))
            continue
        binds = any(c.min() < 1 for c in caps)
        spec = tuple((p["up"], bs.required_hours(p, day)[0]) for p in prods)
        for strat, mk in bs.STRATEGIES.items():
            ep = energy[mk].reindex(hrs)
            if ep.isna().any():
                left.append((day, f"{strat}: energy not held"))
                continue
            for dur in bs.DURATIONS:
                prices = [s.values for s in pr]
                cases = {"price_taker": bs.solve_day(ep.values, prices, spec, dur)}
                cases["fleet_limited"] = bs.solve_day(ep.values, prices, spec, dur, caps=caps) if binds else cases["price_taker"]
                if unheld:
                    none = [np.zeros(len(hrs)) if p["key"] in unheld else c for p, c in zip(prods, caps)]
                    cases["no_regulation"] = bs.solve_day(ep.values, prices, spec, dur, caps=none)
                for name, sol in cases.items():
                    bad = bs.check_day(sol, spec, dur)
                    if bad:
                        raise RuntimeError(f"{iso} {day} {strat} {dur}h {name}: {bad[0]}")
                    limit = caps if name == "fleet_limited" else none if name == "no_regulation" else None
                    if limit is not None and any((sol["awards"][j] > c + 1e-6).any() for j, c in enumerate(limit)):
                        raise RuntimeError(f"{iso} {day} {strat} {dur}h {name}: an award passes its cap")
                r = dict(day=day, strategy=strat, duration_h=dur, fleet_month=fm, fleet_mw=round(mw, 1), cap_binds=int(binds))
                for name, sol in cases.items():
                    r[f"{name}_energy"] = round(sol["energy"], 4)
                    r[f"{name}_total"] = round(sol["total"], 4)
                    for p, v in zip(prods, sol["reserve"]):
                        r[f"{name}_{p['key']}"] = round(v, 4)
                for p, c in zip(prods, caps):
                    r[f"cap_mean_{p['key']}"] = round(float(c.mean()), 4) if qty[p["key"]] is not None else ""
                    r[f"cap_hours_below_1_{p['key']}"] = int((c < 1).sum()) if qty[p["key"]] is not None else ""
                rows.append(r)
    d = pd.DataFrame(rows)
    out = OUT.format(iso)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write(f"# ERW analysis, internal, for review (session 100): the fleet-limited battery estimate against the page's price-taker, {m['label']} "
                f"{bs.pb.MAIN[iso]}, USD per MW of rated power by local day (warehouse/analysis/battery_fleet_limited_review.py). Caps: min(1, the MW the "
                "operator procures / the grid's operating battery MW of the month, EIA-860M via storage_buildout_monthly; a month not yet published takes the newest "
                f"held, named in fleet_month). " + ("Regulation has no quantity held: fleet_limited leaves it uncapped (an upper bound), no_regulation sells none "
                "(a lower bound). " if unheld else "") + f"Days left out: {len(left)}" + (f" ({'; '.join(f'{a}: {b}' for a, b in left[:6])})" if left else "") + "\n")
        d.to_csv(f, index=False, lineterminator="\n")
    log(f"{iso}: {len(d)} rows, {d['day'].nunique()} days, {d['day'].min()} to {d['day'].max()}; left out {len(left)} -> {os.path.relpath(out, ROOT)}")
    d["year"] = d["day"].str[:4]
    cases = [c for c in ("price_taker", "fleet_limited", "no_regulation") if f"{c}_total" in d]
    g = d.groupby(["strategy", "duration_h", "year"]).agg(days=("day", "nunique"), days_cap_binds=("cap_binds", "sum"), **{c: (f"{c}_total", "sum") for c in cases}).reset_index()
    for c in cases:
        g[c] = (g[c] / 1000).round(2)  # USD per kW
    for c in cases[1:]:
        g[f"{c}_share"] = (g[c] / g["price_taker"]).round(4)
    log(g.to_string(index=False))
    capcols = [c for c in d.columns if c.startswith("cap_mean_")]
    cm = d[d["strategy"] == "foresight"].drop_duplicates("day")
    for c in capcols:
        v = pd.to_numeric(cm[c], errors="coerce")
        if v.notna().any():
            log(f"  {c}: mean {v.mean():.4f}, lowest daily mean {v.min():.4f}; days with an hour under 1: {int((pd.to_numeric(cm[c.replace('cap_mean_', 'cap_hours_below_1_')]) > 0).sum())} of {len(cm)}")
    log(f"  fleet MW by month used: {cm.groupby('fleet_month')['fleet_mw'].first().to_dict()}")
    return d, left


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    for iso in (argv or ["nyiso", "spp"]):
        run(iso)
    return 0


if __name__ == "__main__":
    sys.exit(main())
