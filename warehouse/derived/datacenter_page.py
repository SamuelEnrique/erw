#!/usr/bin/env python3
"""What a datacenter pays: the site's own files for /cost-of-power (session 138).

Energy Research Warehouse (ERW). No warehouse table is written and no request is made: this reads the public hub and
zone price tables held and writes the page's files under site/data/datacenter/. Method: docs/methods/datacenter_cost.md.

    python warehouse/derived/datacenter_page.py                 # every grid, every year held
    python warehouse/derived/datacenter_page.py --since 2026    # only the files of 2026 on (the weekly refresh)
    python warehouse/derived/datacenter_page.py --out-dir DIR   # a trial run: the files under DIR, nothing in site/data

Files:
    index.json            the grids, each grid's regions (every hub and zone held, with the hours held of each market
                          and its first and last hour), the years of files, the tables read and when
    <grid>_<year>.json    for each region, the hourly price of that year, real time ("rt") and day-ahead ("da"), in
                          USD/MWh, by the hour of the year in the grid's STANDARD time (no daylight saving
                          shift, so every day has 24 hours and a year 8,760 or 8,784): {"s": the first hour held,
                          "v": the values from there to the last hour held}; an hour not held is null, never filled. Where the grid's own hourly demand is held in a public
                          table: "peak_mw" and "peak_hour" (the year's highest hour), "demand_mean_mw", and
                          "tight" (the hours at or above TIGHT of the year's highest hour). A demand table
                          marked internal in coverage.csv is not written (ISO-NE's).

Kept files are merged, never thinned: an hour the new build holds is the new build's, an hour only the kept file holds
is kept. The scheduled runner holds no ERCOT price history, so there the build adds the newest hours to the files.

An hour of real-time price is the mean of its four 15-minute prices and is held only when all four are (ISO-NE's
real-time price is also held as its own hourly report; the one of the two that holds more hours is used whole, never
mixed), exactly as hub_price_comparison does (warehouse/derived/price_compare.py, whose reader this uses). Prices are
written to the cent. A past year's file is rewritten only when its content changes, so the weekly refresh touches the
current year's files alone.

Not written: a table whose license does not allow republishing, and a publisher whose terms are under review
(warehouse/metadata/paused_sources.csv): MISO's regions are listed in index.json by name with the words the page
shows, and no number. PJM: no hub or zone price is held.
"""

import argparse
import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402
import price_compare as pc  # noqa: E402  (the reader of every hub and zone price table, and the 15-minute to hourly rule)

SITE_DIR = os.path.join(ROOT, "site", "data", "datacenter")
FIRST = "2015-01-01"
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
TIGHT = 0.95  # an hour is tight when the grid's demand is at or above this share of the year's highest hour
NEAR_DEMAND = 0.95  # a year's tight hours are written when at least this share of its hours of demand are held
# each grid's standard time, hours behind UTC, and its main hub (the default region), as the price board names it
GRIDS = {
    "ercot": dict(name="ERCOT", std=6, main="HB_HUBAVG", zone="US Central standard time"),
    "caiso": dict(name="CAISO", std=8, main="TH_SP15_GEN-APND", zone="US Pacific standard time"),
    "nyiso": dict(name="NYISO", std=5, main="N.Y.C.", zone="US Eastern standard time"),
    "isone": dict(name="ISO-NE", std=5, main=".H.INTERNAL_HUB", zone="US Eastern standard time"),
    "spp": dict(name="SPP", std=6, main="SPPNORTH_HUB", zone="US Central standard time"),
}
# the grids shown and blanked, with the words the page shows (the owner's rule, session 138)
BLANK = {
    "miso": dict(name="MISO", words="paused while terms are reviewed"),
    "pjm": dict(name="PJM", words="licensed source needed"),
}
# the grid's hourly demand: the operator's own table (session 138's pulls) and the entity that is the grid's total.
# NYISO's table holds its eleven zones and no total: the grid's demand is their sum, in the hours all eleven are held.
DEMAND = {
    "ercot": ("ercot_zone_load_hourly", "ercot:system"),
    "nyiso": ("nyiso_zone_load_hourly", None),
    "caiso": ("caiso_area_load_hourly", "caiso:system"),
    "isone": ("isone_zone_load_hourly", "isone:system"),
}


# Texas delivery charges (texas_delivery_charges, session 138): the table is internal as a whole. A utility's rows are
# written to the site's file only where the sentence of its terms that governs reuse, as quoted in the connector and in
# sources.csv, allows a noncommercial or educational display; the others are named with the words the page shows and
# the reason, and no figure. A person's ruling changes a line here.
DELIVERY_TABLE = "texas_delivery_charges"
DELIVERY = {
    "oncor:retail_delivery_tariff": dict(utility="Oncor", show=True, classes=["Transmission Service"],
        terms="Oncor's terms allow its content to be copied, displayed and distributed, without modification, for personal, noncommercial and educational purposes"),
    "centerpoint:retail_delivery_tariff": dict(utility="CenterPoint Energy Houston Electric", show=False, words="licensed source needed",
        terms="CenterPoint's terms of use forbid copying or publishing its site's content without its written consent. Its tariff's charges are held internally and not shown"),
    "aeptexas:retail_delivery_tariff": dict(utility="AEP Texas", show=False, words="held while terms are reviewed",
        terms="AEP's terms authorize copying and display of its content for personal use only, and forbid redistribution for commercial purposes. Whether this page's display is allowed is a person's ruling; until then its tariff's charges are held internally"),
    "tnmp:retail_delivery_tariff": dict(utility="Texas-New Mexico Power", show=False, words="held while terms are reviewed",
        terms="Texas-New Mexico Power's terms of use could not be read (its site refused the request on 7 October 2026). Its tariff's charges are held internally until a person reads them"),
}
# A figure read from a row of a many-column table: code proves the number is in the line, not which column it is. Such a
# row is shown only when a person or the session checked its column against the table's header by eye (session 138:
# Oncor's TCRF, DCRF and MG for Transmission Service). Oncor's EECRF row is NOT shown: the figure read, 0.000446, stands
# in the column "Transmission Service, Non-Profit"; the for-profit column prints 0.000000.
EYE_CHECKED = {("oncor:retail_delivery_tariff", "Transmission Cost Recovery Factor (TCRF)"), ("oncor:retail_delivery_tariff", "Distribution Cost Recovery Factor (DCRF)"),
               ("oncor:retail_delivery_tariff", "Rider MG amount")}
GENERIC = {"factor", "transmission service", "rate schedule fee", "base revenue factor", "is", "rce", "transmission service*"}


def delivery(in_dir, out_dir, built, log):
    """The site's copy of the Texas delivery charges a transmission-voltage load pays, each as its tariff states it,
    with the line it was read from. Nothing is computed here. Without the table on this machine the kept file stands."""
    path = os.path.join(in_dir, f"{DELIVERY_TABLE}.csv")
    if not os.path.exists(path):
        log(f"  {DELIVERY_TABLE} is not on this machine; the kept delivery file stands")
        return
    d = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
    rows, withheld, no_unit, unchecked = [], [], 0, 0
    for source, rule in DELIVERY.items():
        part = d[d["source"] == source]
        if not rule["show"]:
            withheld.append(dict(utility=rule["utility"], words=rule["words"], why=rule["terms"] + "."))
            continue
        part = part[part["rate_class"].isin(rule["classes"])]
        for _, r in part.iterrows():
            if not r["unit_as_written"].strip():
                no_unit += 1
                continue  # a figure whose unit is not printed on its page is not shown
            many = int(r["figures_in_sentence"] or 1) > 1
            if many and (source, r["charge_name"].strip()) not in EYE_CHECKED:
                unchecked += 1
                continue  # its column was not checked against the header
            name = r["charge_name"].strip()
            if name.lower() in GENERIC or name == r["rate_class"]:
                name = re.sub(r"^[\d.]+\s*", "", r["schedule"]).strip() or name
            rows.append(dict(utility=rule["utility"], rate_class=r["rate_class"], charge=" ".join(name.split()), value=float(r["amount"]),
                             value_as_written=r["value_as_written"], unit=" ".join(r["unit_as_written"].split()), effective=r["effective_date_as_written"] or None,
                             document=r["document_title"], url=r["source_url"], page=r["page"] or None, sentence=" ".join(r["sentence"].split()),
                             column="checked by eye against the table's header" if many else "", terms=rule["terms"]))
    kind = lambda u: 0 if re.search(r"kW(?!h)|kVA", u, re.I) else 1 if re.search(r"kWh", u, re.I) else 2  # noqa: E731
    rows.sort(key=lambda r: (list(DELIVERY).index(next(k for k, v in DELIVERY.items() if v["utility"] == r["utility"])), kind(r["unit"]), -abs(r["value"]), r["charge"]))
    obj = dict(table=DELIVERY_TABLE, built=built, license="internal",
               note="Each charge as its tariff prints it, read by a model and kept only where the line is found in the page's text with the figure in it. "
                    "Shown for the utilities whose terms allow a noncommercial display; the others are named and not shown.",
               rows=rows, withheld=withheld)
    write_if_changed(os.path.join(out_dir, "texas_delivery.json"), obj)
    log(f"  delivery: {len(rows)} charges of {sorted({r['utility'] for r in rows})} written; {no_unit} with no unit printed and {unchecked} from a many-column row not checked by eye left out; withheld: {[w['utility'] for w in withheld]}")


def year_hours(y):
    return 8784 if pd.Timestamp(year=y, month=12, day=31).dayofyear == 366 else 8760


def to_std(index, std):
    """A UTC hourly index as (year, hour of the year) in a grid's standard time."""
    local = (index - pd.Timedelta(hours=std)).tz_localize(None)
    return local.year.values, ((local.dayofyear.values - 1) * 24 + local.hour.values)


def hourly_side(e, side):
    """One market of one region by hour (UTC): of the ways it is held (15-minute means, or the operator's own hourly
    report), the one that holds more hours, whole."""
    s = e[e["side"] == side]
    best, basis = None, ""
    for f, part in s.groupby("freq"):
        c = pc.hourly(pd.Series(part["value"].values, index=part["ts"]).sort_index(), f).dropna()
        if best is None or len(c) > len(best):
            best, basis = c, f
    return best, basis


def trimmed(arr):
    """A year's hourly list without its empty ends: {"s": the index of the first hour held, "v": the values from there to
    the last hour held, an hour not held between them null}."""
    held = np.nonzero(~np.isnan(arr))[0]
    a, b = int(held.min()), int(held.max()) + 1
    return {"s": a, "v": [None if np.isnan(v) else float(v) for v in arr[a:b]]}


def write_if_changed(path, obj):
    text = json.dumps(obj, separators=(",", ":"), allow_nan=False)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
        a, b = dict(old), dict(obj)
        a.pop("built", None), b.pop("built", None)
        if a == b:
            return False
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return True


def untrimmed(s, n):
    """The opposite of trimmed: a year's full list of n hours from a stored {"s", "v"}."""
    arr = np.full(n, np.nan)
    v = np.array([np.nan if x is None else x for x in s["v"]], dtype=float)
    arr[s["s"]:s["s"] + len(v)] = v
    return arr


def merged(old, new):
    """Two builds of one year's hours as one: an hour the new build holds is the new build's; an hour only the kept
    file holds is kept. A machine that holds a shorter history (the scheduled runner holds no ERCOT history) therefore
    adds its new hours to the file and never thins it. No hour is made up: both are prices the warehouse held."""
    if old is None:
        return new
    if new is None:
        return old
    return np.where(np.isnan(new), old, new)


def hour_utc(y, i, std):
    """The UTC start of hour i of year y in a grid's standard time."""
    return ip.utc_iso(pd.Timestamp(year=y, month=1, day=1, tz="UTC") + pd.Timedelta(hours=int(i) + std))


def read_kept(out_dir, iso):
    """The files of a grid already written: {year: the file}, and the grid's entry of the index."""
    kept = {}
    for name in sorted(os.listdir(out_dir)):
        if name.startswith(f"{iso}_") and name.endswith(".json") and name[len(iso) + 1:-5].isdigit():
            with open(os.path.join(out_dir, name), encoding="utf-8") as f:
                kept[int(name[len(iso) + 1:-5])] = json.load(f)
    old_index = {}
    path = os.path.join(out_dir, "index.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old_index = json.load(f).get("grids", {}).get(iso, {})
    return kept, old_index


def zone_years(d, total, std):
    """Each zone's year: mean and highest hourly demand, hours held and due. d: entity, ts (UTC), value."""
    out = {}
    newest = None
    for entity, part in d.groupby("entity"):
        if entity == total:
            continue
        s = pd.Series(part["value"].values, index=part["ts"]).sort_index()
        s = s[~s.index.duplicated(keep="last")].dropna()
        ys, hs = to_std(s.index, std)
        newest = max(newest or 0, int(ys.max()))
        zone = entity.split(":", 1)[1]
        for y in np.unique(ys):
            m = ys == y
            out.setdefault(zone, {})[str(int(y))] = dict(mean_mw=round(float(s.values[m].mean()), 1), peak_mw=round(float(s.values[m].max()), 1),
                                                          hours_held=int(m.sum()), hours_due=year_hours(int(y)), last_hour=int(hs[m].max()))
    for zone in out:
        for y, r in out[zone].items():
            if int(y) == newest:
                r["hours_due"] = r["last_hour"] + 1  # the newest year is not whole: due up to the last hour held
            del r["last_hour"]
    return out


def read_demand(in_dir, grid, std, lic, log):
    """The grid's own hourly demand (a UTC series, MW), its source in words, and each zone's years; or None, None, {}
    when its table is not on this machine."""
    if grid not in DEMAND:
        return None, None, {}
    table, total = DEMAND[grid]
    if lic.get(table) not in (None, "public"):
        log(f"  {grid}: demand table {table} is {lic.get(table)}: held, not written to the site's files")
        return None, f"withheld:{table}", {}
    path = os.path.join(in_dir, f"{table}.csv")
    if not os.path.exists(path):
        log(f"  {grid}: demand table {table} is not on this machine; the kept tight hours stand")
        return None, None, {}
    d = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value"])
    d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    d = d.dropna(subset=["value"]).drop_duplicates(["entity", "ts"], keep="last")
    if total is None:
        wide = d.pivot(index="ts", columns="entity", values="value")
        s = wide.dropna().sum(axis=1).sort_index()
        source = f"{table} (the sum of its {wide.shape[1]} zones)"
    elif total in set(d["entity"].unique()):
        t = d[d["entity"] == total]
        s = pd.Series(t["value"].values, index=t["ts"]).sort_index()
        source = f"{table} ({total})"
    else:
        log(f"  {grid}: {table} does not hold {total} (it holds {sorted(d['entity'].unique())[:14]}); no tight hours are written")
        return None, None, zone_years(d, None, std)
    log(f"  {grid}: demand from {source}, {len(s):,} hours, {s.index.min()} to {s.index.max()}")
    return s, source, zone_years(d, total, std)


def main(argv=None):
    ap = argparse.ArgumentParser(description="What a datacenter pays: the site's files for /cost-of-power")
    ap.add_argument("--out-dir", help="a trial run: the files under this directory; nothing in site/data")
    a = ap.parse_args(argv)
    out_dir = a.out_dir or SITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    built = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"datacenter_page_{run_id}.log"))
    lic, paused = pc.licenses()
    internal = [t for t in pc.TABLES if lic.get(t) not in (None, "public")]
    log(f"  internal price tables, not read: {internal}; publishers under review, not read: {sorted(paused)}")
    x = pc.read_prices(ip.OUT_DIR, FIRST, log)
    x = x[~x["table"].isin(internal)]
    x["iso"] = x["entity"].str.split(":", n=1).str[0]
    tables_read = sorted(x["table"].unique())
    old_tables = []
    if os.path.exists(os.path.join(out_dir, "index.json")):
        with open(os.path.join(out_dir, "index.json"), encoding="utf-8") as f:
            old_tables = json.load(f).get("tables", [])

    index = {"built": built, "method": "docs/methods/datacenter_cost.md", "first": FIRST, "tight": TIGHT, "tables": sorted(set(tables_read) | set(old_tables)),
             "grids": {}, "blank": {}}
    for iso, b in BLANK.items():
        nodes = sorted(x.loc[x["iso"] == iso, "entity"].str.split(":", n=1).str[1].unique()) if iso in paused else []
        index["blank"][iso] = dict(name=b["name"], words=b["words"], regions=nodes)
    written = same = 0
    for iso, g in GRIDS.items():
        if iso in paused:
            index["blank"][iso] = dict(name=g["name"], words="paused while terms are reviewed", regions=[])
            continue
        sub = x[x["iso"] == iso]
        kept, old_index = read_kept(out_dir, iso)
        if sub.empty and not kept:
            log(f"  {iso}: no price row is held")
            continue
        # this build's hours, by year, region and market
        years, how = {}, {}
        for entity, e in sub.groupby("entity"):
            node = entity.split(":", 1)[1]
            for side, key in (("rtm", "rt"), ("dam", "da")):
                h, basis = hourly_side(e, side)
                if h is None or h.empty:
                    continue
                ys, hs = to_std(h.index, g["std"])
                vals = np.round(h.values.astype(float), 2)
                for y in np.unique(ys):
                    m = ys == y
                    arr = np.full(year_hours(int(y)), np.nan)
                    arr[hs[m]] = vals[m]
                    years.setdefault(int(y), {}).setdefault(node, {})[key] = arr
                how[(node, key)] = dict(basis=basis, tables=sorted(e.loc[e["side"] == side, "table"].unique()))
        # with the hours of the files already kept
        added = 0
        for y, f in kept.items():
            for node, sides in f.get("regions", {}).items():
                for key, s in sides.items():
                    old = untrimmed(s, f["hours"])
                    new = years.get(y, {}).get(node, {}).get(key)
                    years.setdefault(y, {}).setdefault(node, {})[key] = merged(old, new)
                    if new is not None:
                        added += int((np.isnan(old) & ~np.isnan(new)).sum())
        demand, demand_source, zones = read_demand(ip.OUT_DIR, iso, g["std"], lic, log)
        dem_years = {}
        if demand is not None:
            ys, hs = to_std(demand.index, g["std"])
            for y in np.unique(ys):
                m = ys == y
                arr = np.full(year_hours(int(y)), np.nan)
                arr[hs[m]] = demand.values[m]
                dem_years[int(y)] = arr
        withheld = str(demand_source or "").startswith("withheld:")
        demand_summary = {} if withheld else dict(old_index.get("demand", {}))
        for y in sorted(set(years) | set(dem_years)):
            n = year_hours(y)
            obj = {"grid": iso, "year": y, "hours": n, "built": built, "regions": {}}
            for node, sides in sorted(years.get(y, {}).items()):
                obj["regions"][node] = {k: trimmed(arr) for k, arr in sorted(sides.items())}
            d = dem_years.get(y)
            if d is not None:
                held = int((~np.isnan(d)).sum())
                # the newest year is not whole: its hours due are those up to the last hour held
                due = n if y < max(dem_years) else int(np.nonzero(~np.isnan(d))[0].max()) + 1
                rec = {"hours_held": held, "hours_due": due}
                if held >= NEAR_DEMAND * due:
                    peak = float(np.nanmax(d))
                    tight = np.nonzero(d >= TIGHT * peak)[0]
                    obj["peak_mw"], obj["peak_hour"], obj["tight"] = round(peak, 1), int(np.nanargmax(d)), [int(i) for i in tight]
                    obj["demand_mean_mw"] = round(float(np.nanmean(d)), 1)
                    rec.update(peak_mw=obj["peak_mw"], peak_hour=obj["peak_hour"], tight_hours=len(tight), mean_mw=obj["demand_mean_mw"], whole=bool(y < max(dem_years)))
                demand_summary[str(y)] = rec
            elif y in kept and not str(demand_source or "").startswith("withheld:"):
                # the demand table is not on this machine: the kept file's tight hours stand
                for k in ("peak_mw", "peak_hour", "tight", "demand_mean_mw"):
                    if k in kept[y]:
                        obj[k] = kept[y][k]
            if y not in years:
                continue  # a year of demand with no price held: its figures are in the index, and no file is written
            if write_if_changed(os.path.join(out_dir, f"{iso}_{y}.json"), obj):
                written += 1
            else:
                same += 1
        # the regions, from the hours now in the files
        regions = []
        old_regions = {r["id"]: r for r in old_index.get("regions", [])}
        for node in sorted({n for y in years for n in years[y]}):
            rec = {"id": node, "entity": f"{iso}:{node}"}
            for key in ("rt", "da"):
                ys = sorted(y for y in years if key in years[y].get(node, {}))
                if not ys:
                    continue
                first = int(np.nonzero(~np.isnan(years[ys[0]][node][key]))[0].min())
                last = int(np.nonzero(~np.isnan(years[ys[-1]][node][key]))[0].max())
                h = how.get((node, key)) or {k: old_regions.get(node, {}).get(key, {}).get(k) for k in ("basis", "tables")}
                old_tabs = old_regions.get(node, {}).get(key, {}).get("tables") or []
                rec[key] = {"hours": int(sum((~np.isnan(years[y][node][key])).sum() for y in ys)), "first": hour_utc(ys[0], first, g["std"]),
                            "last": hour_utc(ys[-1], last, g["std"]), "basis": h["basis"], "tables": sorted(set(h["tables"] or []) | set(old_tabs))}
            if "rt" in rec or "da" in rec:
                regions.append(rec)
        regions.sort(key=lambda r: (r["id"] != g["main"], -max(r.get("rt", {}).get("hours", 0), r.get("da", {}).get("hours", 0)), r["id"]))
        index["grids"][iso] = dict(name=g["name"], std_hours_behind_utc=g["std"], std_name=g["zone"], main=g["main"], years=sorted(years), regions=regions,
                                   demand_source=demand_source or old_index.get("demand_source"), demand=demand_summary,
                                   zones={} if withheld else (zones or old_index.get("zones", {})))
        log(f"  {iso}: {len(regions)} regions, years {min(years)} to {max(years)}, {added:,} hours added to the kept files"
            + (f", demand years {sorted(dem_years)}" if dem_years else ", no demand table here"))
    delivery(ip.OUT_DIR, out_dir, built, log)
    write_if_changed(os.path.join(out_dir, "index.json"), index)
    log(f"  files written {written}, unchanged {same}; index.json; under {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
