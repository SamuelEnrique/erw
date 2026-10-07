#!/usr/bin/env python3
"""Where free energy is: the hours a hub or zone priced below zero or under USD 5 per MWh (session 144).

Energy Research Warehouse (ERW). No warehouse table is written and no request is made: this reads the public hourly
prices by hub and zone the warehouse holds (price_compare.read_prices over datacenter_page.TABLES, so the load zone and
zone histories are read when they are on the machine) and writes the page's file, site/data/curtailment/free_energy.json.

    python warehouse/derived/free_energy.py                  # the site's file
    python warehouse/derived/free_energy.py --out-dir DIR    # a trial: the file under DIR, nothing in site/data
    python warehouse/derived/free_energy.py --end 2026-09    # the last month of the windows (default: the last whole month held)

The rules, each stated in the file as well:
    An hour.        Real time where a location holds it, otherwise day-ahead, said per location and per window ("rt",
                    "da"). An hour of real time is the mean of its four 15-minute prices and counts only when all four
                    are held. A price held in two tables is one row (the reader keeps the first table's), and a market
                    held at two resolutions is used at the one that holds more hours, whole: an hour is counted once.
    Two counts.     "negative": hours priced below zero. "under5": hours priced under USD 5 per MWh, which INCLUDES the
                    negative ones, each once. Hours from zero to under 5 are under5 less negative.
    Two windows.    The last complete calendar month and the last twelve complete months, in each grid's standard time
                    (no daylight saving shift, so every day has 24 hours). A window's figures are written for a
                    location only when at least 95 percent of the window's hours are held on one market; otherwise
                    the window carries "missing" with the hours held, and no count.
    The heatmap.    For each of the twelve months and each hour of the day (standard time): the hours under 5, the
                    hours below zero and the hours held. A cell with no hour held is 0 held, never a count of none.
    The gap.        For each grid, among its places (hubs and zones; an average of hubs is not a place) whose window is
                    whole on one market: the mean price of each over the hours ALL of them hold, the cheapest, the
                    dearest and the difference, with the cheap hours of each over the same hours.
    Not shown.      MISO: its terms are under review (warehouse/metadata/paused_sources.csv); its hubs are named, with
                    no number. PJM: no public hub or zone price is held. A table whose license is not public is not read.
    Coordinates.    No latitude or longitude of a hub or zone is held anywhere in the site's data or the warehouse, and
                    none is made up here: every point carries lat and lon null and the state its table gives (geo).
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
import iso_prices as ip  # noqa: E402
import price_compare as pc  # noqa: E402
import datacenter_page as dp  # noqa: E402

SITE_FILE = os.path.join(ROOT, "site", "data", "curtailment", "free_energy.json")
THRESHOLD = 5.0   # USD per MWh: an hour priced under this is "under5" (it includes the hours below zero)
NEAR = 0.95       # the share of a window's hours a location must hold for the window's figures to be written
SIDES = (("rtm", "rt"), ("dam", "da"))
AVERAGES = {"ercot:HB_HUBAVG", "ercot:HB_BUSAVG"}  # averages of hubs or buses: shown, and not ranked as places
PAIRS = {
    "west_texas_houston": dict(words="West Texas against Houston", grid="ercot", pairs={"hub": ("HB_WEST", "HB_HOUSTON"), "zone": ("LZ_WEST", "LZ_HOUSTON")}),
    "california_north_south": dict(words="California north (NP15) against south (SP15)", grid="caiso", pairs={"hub": ("TH_NP15_GEN-APND", "TH_SP15_GEN-APND")}),
}
NO_COORDINATES = ("No latitude or longitude of a hub or zone is held in the site's data or the warehouse (searched: board.json, board_v4.json, markets.json, "
                  "price_compare.json, datacenter/index.json, map_v2.json, which holds projects only, and grid_network.json, whose x, y, z are a drawing's layout). "
                  "A trading hub is a set of buses and a zone an area, so a point for either is a choice a person makes; none is made up here.")


def kind_of(entity):
    iso, node = entity.split(":", 1)
    if entity in AVERAGES:
        return "average"
    if iso == "ercot":
        return "zone" if node.startswith("LZ_") else "hub"
    if iso == "nyiso":
        return "zone"
    if iso == "isone":
        return "zone" if node.startswith(".Z.") else "hub"
    return "hub"


def months_of(end_month, n):
    """The n calendar months ending with end_month, oldest first."""
    return [(pd.Period(end_month) - i).strftime("%Y-%m") for i in range(n - 1, -1, -1)]


def bounds(months, std):
    """The UTC start and end (exclusive) of a run of calendar months in a grid's standard time (std hours behind UTC),
    and its hours."""
    a = pd.Timestamp(f"{months[0]}-01", tz="UTC") + pd.Timedelta(hours=std)
    b = (pd.Period(months[-1]) + 1).to_timestamp().tz_localize("UTC") + pd.Timedelta(hours=std)
    return a, b, int((b - a) / pd.Timedelta(hours=1))


def once(h):
    """An hourly series with each hour once (the first kept) and no blank."""
    h = h.dropna()
    return h[~h.index.duplicated(keep="first")].sort_index()


def counts(h):
    """The hours of an hourly price series: held, below zero, and under THRESHOLD (which includes those below zero).
    Each hour is counted once."""
    h = once(h)
    return {"hours_held": int(len(h)), "negative": int((h < 0).sum()), "under5": int((h < THRESHOLD).sum())}


def cut(h, a, b):
    return h[(h.index >= a) & (h.index < b)]


def window_of(sides, a, b, n):
    """One location's window: real time when it holds NEAR of the window's hours, otherwise day-ahead when that does,
    otherwise no count and the reason. sides: {"rt": hourly series, "da": hourly series} (UTC)."""
    held = {k: int(len(cut(s, a, b))) for k, s in sides.items()}
    for k in ("rt", "da"):
        if k in sides and held[k] >= NEAR * n:
            h = cut(sides[k], a, b)
            rec = {"basis": k, "hours_in_window": n}
            rec.update(counts(h))
            rec["mean"] = round(float(h.mean()), 2)
            return rec
    return {"missing": "under {:.0%} of the window's hours are held: {}".format(NEAR, ", ".join(f"{'real time' if k == 'rt' else 'day-ahead'} {held[k]:,} of {n:,}" for k in ("rt", "da") if k in sides) or "no price"),
            "hours_in_window": n, **{f"{k}_hours_held": v for k, v in held.items()}}


def heat_of(h, months, std):
    """The hour of the day by month matrix of one location's hours: under5, negative and held, each [month][hour]."""
    local = (h.index - pd.Timedelta(hours=std)).tz_localize(None)
    mi = {m: i for i, m in enumerate(months)}
    under5, negative, held = (np.zeros((len(months), 24), dtype=int) for _ in range(3))
    idx = np.array([mi.get(m, -1) for m in local.strftime("%Y-%m")])
    ok = idx >= 0
    np.add.at(held, (idx[ok], local.hour.values[ok]), 1)
    v = h.values
    np.add.at(under5, (idx[ok & (v < THRESHOLD)], local.hour.values[ok & (v < THRESHOLD)]), 1)
    np.add.at(negative, (idx[ok & (v < 0)], local.hour.values[ok & (v < 0)]), 1)
    return {"under5": under5.tolist(), "negative": negative.tolist(), "held": held.tolist()}


def common(series):
    """The hours every one of the series holds."""
    idx = None
    for s in series:
        idx = s.index if idx is None else idx.intersection(s.index)
    return idx


def side_stats(h, idx):
    h = h.reindex(idx)
    return {"mean": round(float(h.mean()), 2), **{k: v for k, v in counts(h).items() if k != "hours_held"}}


def gap_of(places, a, b, n):
    """A grid's gap in a window. places: {id: {"rt": series, "da": series}}. The market is real time when at least two
    places hold NEAR of the window on it, otherwise day-ahead on the same test; the means are over the hours all of
    those places hold."""
    for k in ("rt", "da"):
        whole = {i: cut(s[k], a, b) for i, s in places.items() if k in s and len(cut(s[k], a, b)) >= NEAR * n}
        if len(whole) < 2:
            continue
        idx = common(whole.values())
        if len(idx) < NEAR * n:
            continue
        stats = {i: side_stats(h, idx) for i, h in whole.items()}
        lo = min(stats, key=lambda i: (stats[i]["mean"], i))
        hi = max(stats, key=lambda i: (stats[i]["mean"], i))
        return {"basis": k, "hours_common": int(len(idx)), "hours_in_window": n, "places": sorted(whole),
                "cheapest": {"id": lo, **stats[lo]}, "dearest": {"id": hi, **stats[hi]}, "gap": round(stats[hi]["mean"] - stats[lo]["mean"], 2),
                "by_place": stats}
    return {"missing": f"fewer than two places hold {NEAR:.0%} of the window's hours on one market", "hours_in_window": n}


def pair_of(sa, sb, a, b, n):
    """Two locations over the hours both hold, on real time when both hold NEAR of the window on it, else day-ahead."""
    if sa is None or sb is None:
        return {"missing": "one of the two is not held", "hours_in_window": n}
    for k in ("rt", "da"):
        if k in sa and k in sb:
            ha, hb = cut(sa[k], a, b), cut(sb[k], a, b)
            idx = ha.index.intersection(hb.index)
            if len(idx) >= NEAR * n:
                A, B = side_stats(ha, idx), side_stats(hb, idx)
                xa, xb = ha.reindex(idx), hb.reindex(idx)
                return {"basis": k, "hours_common": int(len(idx)), "hours_in_window": n, "a": A, "b": B, "mean_b_less_a": round(B["mean"] - A["mean"], 2),
                        "hours_a_under5_b_not": int(((xa < THRESHOLD) & ~(xb < THRESHOLD)).sum()), "hours_b_under5_a_not": int(((xb < THRESHOLD) & ~(xa < THRESHOLD)).sum())}
    return {"missing": f"the two do not both hold {NEAR:.0%} of the window's hours on one market", "hours_in_window": n}


def location_series(x):
    """{entity: {"rt": hourly series, "da": hourly series, "freq": {...}, "tables": {...}, "geo": str}} from the reader's
    rows: each market at the one resolution that holds more hours, whole, and each hour once."""
    out = {}
    for entity, e in x.groupby("entity"):
        rec = {"freq": {}, "tables": {}, "geo": str(e["geo"].dropna().iloc[0]) if e["geo"].notna().any() else ""}
        for side, key in SIDES:
            h, basis = dp.hourly_side(e, side)
            if h is None or h.empty:
                continue
            rec[key] = once(h)
            rec["freq"][key] = basis
            rec["tables"][key] = sorted(e.loc[(e["side"] == side) & (e["freq"] == basis), "table"].unique())
        if "rt" in rec or "da" in rec:
            out[entity] = rec
    return out


def build(x, end_month, blank, log):
    """The file's content from the reader's rows (MISO's already dropped)."""
    locs = location_series(x)
    year_months = months_of(end_month, 12)
    view = {"threshold_usd_per_mwh": THRESHOLD, "near_hours": NEAR, "end_month": end_month, "year_months": year_months,
            "counts": "negative: hours priced below zero. under5: hours priced under USD 5 per MWh, including the hours below zero, each hour once. hours from zero to under 5: under5 less negative.",
            "hour": "Real time where the location holds it for 95 percent of the window, otherwise day-ahead (basis rt or da, per location and window). An hour of real time is the mean of its four 15-minute prices and counts only when all four are held.",
            "time": "Months and hours of the day are in each grid's standard time, with no daylight saving shift.",
            "coordinates": {"held": False, "note": NO_COORDINATES},
            "grids": {}, "blank": blank, "compare": {}, "widest_gap": {}}
    for iso, g in dp.GRIDS.items():
        if iso in blank:
            continue
        mine = {e.split(":", 1)[1]: r for e, r in locs.items() if e.startswith(iso + ":")}
        if not mine:
            log(f"  {iso}: no price row is held")
            continue
        std = g["std"]
        wins = {"month": bounds([end_month], std), "year": bounds(year_months, std)}
        out = {"name": g["name"], "std_hours_behind_utc": std, "std_name": g["zone"],
               "windows": {w: {"start_utc": ip.utc_iso(a), "end_utc": ip.utc_iso(b), "hours": n} for w, (a, b, n) in wins.items()}, "locations": []}
        for node in sorted(mine):
            r = mine[node]
            sides = {k: r[k] for k in ("rt", "da") if k in r}
            rec = {"id": node, "entity": f"{iso}:{node}", "kind": kind_of(f"{iso}:{node}"), "geo": r["geo"], "lat": None, "lon": None,
                   "freq": r["freq"], "tables": r["tables"]}
            for w, (a, b, n) in wins.items():
                rec[w] = window_of(sides, a, b, n)
            # the heatmap: on the year's market when the year is whole, otherwise on the market that holds more of the twelve months
            a, b, n = wins["year"]
            k = rec["year"].get("basis") or max(sides, key=lambda s: (len(cut(sides[s], a, b)), s == "rt"))
            h = cut(sides[k], a, b)
            rec["heat"] = {"basis": k, "whole": "basis" in rec["year"], "hours_held": int(len(h)), **heat_of(h, year_months, std)}
            out["locations"].append(rec)
        places = {node: {k: r[k] for k in ("rt", "da") if k in r} for node, r in mine.items() if kind_of(f"{iso}:{node}") != "average"}
        out["gap"] = {w: gap_of(places, a, b, n) for w, (a, b, n) in wins.items()}
        out["most_cheap_hours"] = {}
        for w in wins:
            ranked = [(L[w]["under5"], L[w]["negative"], L["id"]) for L in out["locations"] if "basis" in L[w] and L["kind"] != "average"]
            if ranked:
                u, neg, node = max(ranked, key=lambda t: (t[0], t[1], t[2]))
                L = next(L for L in out["locations"] if L["id"] == node)
                out["most_cheap_hours"][w] = {"id": node, "under5": u, "negative": neg, "hours_held": L[w]["hours_held"], "basis": L[w]["basis"], "places_ranked": len(ranked)}
            else:
                out["most_cheap_hours"][w] = {"missing": "no place holds the window whole"}
        view["grids"][iso] = out
        log(f"  {iso}: {len(out['locations'])} locations; whole month {sum('basis' in L['month'] for L in out['locations'])}, whole year {sum('basis' in L['year'] for L in out['locations'])}")
    for key, p in PAIRS.items():
        iso = p["grid"]
        if iso not in view["grids"]:
            view["compare"][key] = {"words": p["words"], "missing": f"{dp.GRIDS[iso]['name']} is not shown"}
            continue
        std = dp.GRIDS[iso]["std"]
        rec = {"words": p["words"], "grid": iso}
        for kind, (na, nb) in p["pairs"].items():
            sa, sb = locs.get(f"{iso}:{na}"), locs.get(f"{iso}:{nb}")
            rec[kind] = {"a": na, "b": nb, "month": pair_of(sa, sb, *bounds([end_month], std)), "year": pair_of(sa, sb, *bounds(year_months, std))}
        view["compare"][key] = rec
    for w in ("month", "year"):
        have = [(g["gap"][w]["gap"], iso) for iso, g in view["grids"].items() if "gap" in g["gap"][w]]
        if have:
            gap, iso = max(have)
            G = view["grids"][iso]["gap"][w]
            view["widest_gap"][w] = {"grid": iso, "gap": gap, "cheapest": G["cheapest"]["id"], "dearest": G["dearest"]["id"], "basis": G["basis"], "grids_compared": len(have)}
        else:
            view["widest_gap"][w] = {"missing": "no grid has two places whole in the window"}
    return view


def read(in_dir, since, log):
    """The reader's rows, without a table that is not public and without MISO (named, never read into a number)."""
    lic, paused = pc.licenses()
    internal = [t for t in dp.TABLES if lic.get(t) not in (None, "public")]
    x = pc.read_prices(in_dir, since, log, tables=[t for t in dp.TABLES if t not in internal])
    iso = x["entity"].str.split(":", n=1).str[0]
    blank = {}
    for k, b in dp.BLANK.items():
        blank[k] = dict(name=b["name"], words=b["words"], regions=sorted(x.loc[iso == k, "entity"].str.split(":", n=1).str[1].unique()) if k in paused else [])
    for k in paused:
        if k in dp.GRIDS and k not in blank:
            blank[k] = dict(name=dp.GRIDS[k]["name"], words="paused while terms are reviewed", regions=sorted(x.loc[iso == k, "entity"].str.split(":", n=1).str[1].unique()))
    x = x[~iso.isin(set(blank) | set(paused))]
    log(f"  internal price tables, not read: {internal}; not shown: {sorted(blank)}")
    return x, blank, internal


def main(argv=None):
    ap = argparse.ArgumentParser(description="Where free energy is: hours below zero and under USD 5 per MWh, by hub and zone")
    ap.add_argument("--out-dir", help="a trial run: the file under this directory; nothing in site/data")
    ap.add_argument("--in-dir", help="read the price tables from this directory instead of warehouse/output")
    ap.add_argument("--end", help="the last month of the windows, YYYY-MM (default: the last whole month held)")
    a = ap.parse_args(argv)
    lines = []

    def log(s):
        lines.append(s)
        print(s)
    since = (pd.Period(a.end) - 12).strftime("%Y-%m-01") if a.end else (pd.Timestamp.now(tz="UTC").to_period("M") - 14).strftime("%Y-%m-01")
    x, blank, internal = read(a.in_dir or ip.OUT_DIR, since, log)
    hist = x[x["table"] == "iso_hub_prices_history"]
    end_month = a.end or pc.last_whole_month(hist if len(hist) else x)
    view = build(x, end_month, blank, log)
    view = {"built": ip.utc_iso(pd.Timestamp.now(tz="UTC")), "method": "warehouse/derived/free_energy.py", "tables": sorted(x["table"].unique()), "internal_tables": internal, **view}
    target = os.path.join(a.out_dir, "free_energy.json") if a.out_dir else SITE_FILE
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        json.dump(view, f, separators=(",", ":"), allow_nan=False)
    if a.out_dir:
        with open(os.path.join(a.out_dir, "free_energy.log"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
    print(f"free energy: windows to {end_month}; {sum(len(g['locations']) for g in view['grids'].values())} locations in {len(view['grids'])} grids; written {target} ({os.path.getsize(target):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
