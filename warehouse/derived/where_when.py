#!/usr/bin/env python3
"""ERW: where and when power is spare, the page file site/data/curtailment/where_when.json (session 8014, chain 581 part C).

Energy Research Warehouse (ERW). Writes one new page file; no table, no request. Contract:
docs/state/page_files_curtailment.md. Method: docs/methods/where_when.md. For each place the curtailment page may show:

  - curtailment as the operator publishes it: CAISO's wind and solar curtailed, by hour of the day, month and year
    (caiso_curtailment_profile, from CAISO's five-minute record); SPP's wind and solar curtailed by month and year
    (spp_curtailment_daily: SPP publishes by day, so no hour of the day);
  - for every hub and zone whose price a page may show, the hours priced below zero, by hour of the day, month and
    year, over every year the price tables hold (the same reader and the same hour rule as free_energy.py: real time
    where the year holds it, else day-ahead; an hour of real time is the mean of its four 15-minute prices).

ERCOT publishes no curtailment figure (the curtailment page's ERCOT estimate is the ERW's arithmetic and is not drawn
here); MISO is paused; PJM, NYISO and ISO-NE hold no curtailment figure here. A grid whose prices the license holds
(NYISO and ISO-NE by license_status.held_grids(), PJM, MISO paused) is listed by name with its places and no number. No figure of the ERW's own beyond counts, sums and shares.

    python warehouse/derived/where_when.py                 # the site's file
    python warehouse/derived/where_when.py --out-dir DIR   # a trial
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "metadata"))
import iso_prices as ip  # noqa: E402
import license_status as ls  # noqa: E402
import datacenter_page as dp  # noqa: E402
import free_energy as fe  # noqa: E402

SITE_FILE = os.path.join(ROOT, "site", "data", "curtailment", "where_when.json")
METHOD = "docs/methods/where_when.md"
NEAR = 0.95
SINCE = "2018-01-01"


def read_series(name, cols):
    p = os.path.join(ip.OUT_DIR, name + ".csv")
    fh = open(p, "rb")
    for _ in range(ip.header_rows(p)):
        fh.readline()
    d = pd.read_csv(fh, usecols=cols, dtype=str, keep_default_na=False)
    fh.close()
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d


def caiso_place():
    """CAISO's curtailment by year, month and hour of the day (Pacific time, as CAISO's record is), solar and wind."""
    with open(os.path.join(ROOT, "site", "data", "curtailment_profile.json"), encoding="utf-8") as fh:
        prof = json.load(fh)
    months = sorted(prof["months"])
    years = sorted({m[:4] for m in months})
    out = {"id": "caiso", "name": "CAISO, the whole system", "grid": "caiso", "kind": "curtailment", "table": prof["table"],
           "input_table": prof["input"], "vintage": prof["last"], "unit": "MWh", "time": "Pacific clock time, as CAISO's five-minute record is",
           "source": "California ISO, wind and solar curtailment reports (five-minute record), as the ERW's tables caiso_curtailment_intervals and caiso_curtailment_profile hold them",
           "years": years, "fuels": ["solar", "wind"], "by_hour": True, "matrix": {}, "by_year": {}, "days_held": {}}
    for y in years:
        out["matrix"][y] = {}
        for fuel in ("solar", "wind"):
            grid = []
            for mo in range(1, 13):
                m = f"{y}-{mo:02d}"
                r = prof["months"].get(m)
                grid.append([r.get(f"curtailed_{fuel}_mwh_h{h:02d}") for h in range(24)] if r else None)
            out["matrix"][y][fuel] = grid
        held = [prof["months"][m] for m in months if m.startswith(y)]
        out["days_held"][y] = {"days_held": sum(r["days_held"] for r in held), "days_in_year": 366 if int(y) % 4 == 0 else 365}
        whole = out["days_held"][y]["days_held"] >= 0.9 * out["days_held"][y]["days_in_year"] and len(held) == 12
        out["by_year"][y] = {fuel: (round(sum(r[f"curtailed_{fuel}_mwh"] for r in held), 1) if whole else None) for fuel in ("solar", "wind")}
        out["by_year"][y]["whole"] = whole
    return out


def spp_place():
    """SPP's wind and solar curtailed by month and year; SPP publishes by day, so no hour of the day."""
    d = read_series("spp_curtailment_daily", ["entity", "variable", "ts_utc", "value"])
    d["month"] = d["ts_utc"].str.slice(0, 7)
    vars_ = sorted(d["variable"].unique())
    months = sorted(d["month"].unique())
    years = sorted({m[:4] for m in months})
    out = {"id": "spp", "name": "SPP, the whole system", "grid": "spp", "kind": "curtailment", "table": "spp_curtailment_daily",
           "vintage": d["ts_utc"].max()[:10], "unit": "MWh", "time": "SPP's operating days",
           "source": "Southwest Power Pool, wind and solar curtailment (daily), as the ERW's table spp_curtailment_daily holds it",
           "years": years, "variables": vars_, "by_hour": False,
           "by_hour_reason": "SPP publishes its curtailment by day, not by hour, so it has no hour of the day",
           "entities": sorted(d["entity"].unique()), "monthly": {}, "by_year": {}}
    days = d.groupby("month")["ts_utc"].nunique()
    for v in vars_:
        g = d[d["variable"] == v].groupby("month")["value"].sum()
        out["monthly"][v] = {m: round(float(g.get(m, np.nan)), 1) if m in g.index else None for m in months}
    for y in years:
        ms = [m for m in months if m.startswith(y)]
        n_days = int(sum(days.get(m, 0) for m in ms))
        diy = 366 if int(y) % 4 == 0 else 365
        whole = n_days >= 0.9 * diy
        out["by_year"][y] = {"days_held": n_days, "days_in_year": diy, "whole": whole,
                             **{v: (round(float(sum(out["monthly"][v][m] or 0 for m in ms)), 1) if whole else None) for v in vars_}}
    out["months"] = months
    return out


def price_places(log):
    x, blank, internal = fe.read(ip.OUT_DIR, SINCE, log)
    # a grid whose prices the license holds (license_status.held_grids(), the owner's ruling of 12 October 2026) is named
    # with its places and "license needed", never read into a number (as prices_map.py does)
    held = ls.held_grids()
    for iso, g in dp.GRIDS.items():
        if g["name"] in held and iso not in blank:
            nodes = sorted(e.split(":", 1)[1] for e in x.loc[x["entity"].str.startswith(iso + ":"), "entity"].unique())
            blank[iso] = {"name": g["name"], "words": f"{ls.NEEDED}: {ls.note(g['name'])}", "regions": nodes}
    x = x[~x["entity"].str.split(":", n=1).str[0].isin(set(blank))]
    locs = fe.location_series(x)
    places = []
    for iso, g in dp.GRIDS.items():
        if iso in blank:
            continue
        std = g["std"]
        for entity in sorted(e for e in locs if e.startswith(iso + ":")):
            r = locs[entity]
            sides = {k: r[k] for k in ("rt", "da") if k in r}
            node = entity.split(":", 1)[1]
            first = min(s.index.min() for s in sides.values())
            last = max(s.index.max() for s in sides.values())
            y0 = (first - pd.Timedelta(hours=std)).year
            y1 = (last - pd.Timedelta(hours=std)).year
            rec = {"id": entity, "name": node, "grid": iso, "grid_name": g["name"], "kind": fe.kind_of(entity), "unit": "hours",
                   "time": f"{g['zone']}, no daylight saving shift", "tables": r["tables"], "freq": r["freq"],
                   "years": [], "matrix": {}, "by_year": {}}
            for y in range(y0, y1 + 1):
                months = [f"{y}-{mo:02d}" for mo in range(1, 13)]
                a, b, n = fe.bounds(months, std)
                held = {k: int(len(fe.cut(s, a, b))) for k, s in sides.items()}
                k = "rt" if held.get("rt", 0) >= NEAR * n else ("da" if held.get("da", 0) >= NEAR * n else max(held, key=lambda s: (held[s], s == "rt")))
                h = fe.cut(sides[k], a, b)
                if h.empty:
                    continue
                heat = fe.heat_of(h, months, std)
                c = fe.counts(h)
                whole = c["hours_held"] >= NEAR * n
                rec["years"].append(str(y))
                rec["matrix"][str(y)] = {"basis": k, "negative": heat["negative"], "held": heat["held"]}
                rec["by_year"][str(y)] = {"basis": k, "hours_in_year": n, "hours_held": c["hours_held"], "negative": c["negative"], "whole": whole,
                                          "share_negative_pct": round(100 * c["negative"] / c["hours_held"], 2) if whole and c["hours_held"] else None}
            if rec["years"]:
                places.append(rec)
        log(f"  {iso}: {sum(p['grid'] == iso for p in places)} places")
    return places, blank, internal, sorted(x["table"].unique())


def ranks(places):
    """The places ranked by the share of hours below zero in the newest whole year each grid holds, and by curtailment."""
    out = []
    for p in places:
        if p.get("kind") == "average":   # an average of hubs or buses is not a place (free_energy.py's rule)
            continue
        whole = [y for y, r in p["by_year"].items() if r.get("whole")]
        if not whole:
            continue
        y = max(whole)
        r = p["by_year"][y]
        out.append({"id": p["id"], "name": p["name"], "grid": p["grid"], "kind": p.get("kind"), "year": y, "share_negative_pct": r["share_negative_pct"],
                    "negative": r["negative"], "hours_held": r["hours_held"]})
    out.sort(key=lambda r: (-(r["share_negative_pct"] or 0), r["id"]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Where and when power is spare: curtailment and hours below zero by hour, month and year")
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    lines = []

    def log(s):
        lines.append(s)
        print(s)
    caiso, spp = caiso_place(), spp_place()
    prices, blank, internal, tables = price_places(log)
    doc = {"built": ip.utc_iso(pd.Timestamp.now(tz="UTC")), "method": METHOD, "contract": "docs/state/page_files_curtailment.md", "license": "public",
           "tables": sorted(set(tables) | {"caiso_curtailment_profile", "caiso_curtailment_intervals", "spp_curtailment_daily"}),
           "internal_tables": internal, "near": NEAR,
           "hour_rule": "Real time where the place holds 95 percent of the year's hours, otherwise day-ahead, said per place and year. An hour of real time is the mean of its four 15-minute prices and counts only when all four are held (free_energy.py's rule).",
           "whole_year_rule": "A year's share or total is written only when 95 percent of its hours (prices) or 90 percent of its days (curtailment) are held; else null.",
           "curtailment": [caiso, spp],
           "curtailment_not_held": {
               "ercot": "ERCOT publishes no curtailment figure; the curtailment page's ERCOT figure is the ERW's arithmetic (output against the limits ERCOT publishes) and is not drawn here",
               "miso": "MISO is paused while its terms are reviewed", "pjm": "no curtailment figure of PJM is held", "nyiso": "no curtailment figure of NYISO is held",
               # session 10210 (the curtailment audit, finding 5): ISO-NE's monthly undelivered energy is held, internal, on
               # the owner's ruling of 7 October 2026 (isone_ddg_undelivered_monthly); it is not shown, not "not held"
               "isone": "ISO-NE's monthly undelivered energy is held internal under its legal notice and not shown"},
           "prices": prices, "price_blank": blank, "ranked_negative": ranks(prices)}
    target = os.path.join(a.out_dir, "where_when.json") if a.out_dir else SITE_FILE
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, separators=(",", ":"), allow_nan=False)
    print(f"where_when: {len(prices)} price places, 2 curtailment places; {target} ({os.path.getsize(target):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
