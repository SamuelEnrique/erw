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
    "ercot": dict(name="ERCOT", std=6, main="LZ_NORTH", zone="US Central standard time"),
    "caiso": dict(name="CAISO", std=8, main="TH_SP15_GEN-APND", zone="US Pacific standard time"),
    "nyiso": dict(name="NYISO", std=5, main="N.Y.C.", zone="US Eastern standard time"),
    "isone": dict(name="ISO-NE", std=5, main=".H.INTERNAL_HUB", zone="US Eastern standard time"),
    "spp": dict(name="SPP", std=6, main="SPPNORTH_HUB", zone="US Central standard time"),
}
# Session 140: the price tables read. The comparison's own (price_compare.TABLES), and the two histories pulled for this
# page: ERCOT's load zones, where a Texas load settles (ercot_zone_prices_history); NYISO's zones back to 2019, CAISO's
# ZP26 and SPP South as far as their operators serve them (iso_zone_prices_history). A table earlier in the list wins
# an hour both hold.
# NOT read: ISO-NE's load zones back to 2019 (isone_zone_prices_history, HELD_INTERNAL). It is internal: it comes from
# the same ISO-NE workbook as the demand the owner ruled internal. It must not even be read and then set aside: the
# reader keeps the first table that holds an hour, so an internal table in the list would take ISO-NE's hours from the
# public six-week tables and then be dropped, and those hours would be lost to the page. To show it after a ruling:
# its license in coverage, and its name moved into TABLES after iso_zone_prices_history.
HELD_INTERNAL = ["isone_zone_prices_history"]
TABLES = ["iso_hub_prices_history", "ercot_all_hub_prices_history", "ercot_zone_prices_history", "iso_zone_prices_history"] + [
    t for t in pc.TABLES if t not in ("iso_hub_prices_history", "ercot_all_hub_prices_history")]
# ERCOT's load zones, where a load settles, each with its name and the trading hub shown beside it for reference. The
# four competitive zones have a hub of the same area; the four zones of municipal and cooperative systems (Austin
# Energy, CPS Energy, the Lower Colorado River Authority, Rayburn) have none of their own and stand beside the hub
# average. A default region is a load zone (the owner's ruling, session 140: a Texas load prices at its load zone).
ZONES = {
    "ercot": {
        "LZ_NORTH": dict(name="North load zone", ref="HB_NORTH"), "LZ_HOUSTON": dict(name="Houston load zone", ref="HB_HOUSTON"),
        "LZ_SOUTH": dict(name="South load zone", ref="HB_SOUTH"), "LZ_WEST": dict(name="West load zone", ref="HB_WEST"),
        "LZ_AEN": dict(name="Austin Energy load zone", ref="HB_HUBAVG"), "LZ_CPS": dict(name="CPS Energy load zone (San Antonio)", ref="HB_HUBAVG"),
        "LZ_LCRA": dict(name="Lower Colorado River Authority load zone", ref="HB_HUBAVG"), "LZ_RAYBN": dict(name="Rayburn load zone", ref="HB_HUBAVG"),
    },
}
CLEAN_TABLE = "clean_energy_hourly"  # the carbon-free share of each grid's generation by hour (mix_clean.py), public

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


# Texas delivery charges (texas_delivery_charges, session 138; the owner's ruling of session 140). The table is internal
# as a whole. Session 138 showed Oncor's rows alone, by its reading of each utility's terms of use. The owner then ruled:
# all four utilities' charges are shown, each row citing its tariff document, address and date, as public regulatory
# filings (the tariffs are on file with the Public Utility Commission of Texas). So every row a transmission-voltage
# load pays is written, with its line, page, address and effective date, and with what the charge is (transmission,
# distribution, or another rider), which the review of session 140 states row by row
# (warehouse/derived/texas_delivery_review.json).
DELIVERY_TABLE = "texas_delivery_charges"
MATRIX_TABLE = "texas_transmission_matrix"
REVIEW = os.path.join(HERE, "texas_delivery_review.json")
FILING = "Shown as a public regulatory filing: the utility's Tariff for Retail Delivery Service, on file with the Public Utility Commission of Texas"
DELIVERY = {
    "oncor:retail_delivery_tariff": dict(utility="Oncor", code="ONC"),
    "centerpoint:retail_delivery_tariff": dict(utility="CenterPoint Energy Houston Electric", code="CNP"),
    "aeptexas:retail_delivery_tariff": dict(utility="AEP Texas", code="AEP"),
    "tnmp:retail_delivery_tariff": dict(utility="Texas-New Mexico Power", code="TNMP"),
}
KINDS = ["transmission", "distribution", "other"]
GENERIC = {"factor", "transmission service", "rate schedule fee", "base revenue factor", "is", "rce", "transmission service*"}
# the Commission's matrix: the figures the page shows, statewide and for the four utilities as transmission providers
MATRIX_STATEWIDE = ["postage_stamp_rate", "total_transmission_cost_of_service", "total_average_4cp"]
MATRIX_PROVIDER = ["transmission_cost_of_service", "access_fee", "average_4cp"]


def delivery_rows(d, review):
    """The rows of the delivery table a transmission-voltage load pays, as the page shows them, and the counts of the
    rows left out with the reason. A row is shown only when the review names it (so its class is the transmission-voltage
    class and its kind is stated), its unit is printed on its page, its figure's column was checked where its line holds
    more than one figure, and the review does not say it is another customer's column (a non-profit rate)."""
    by = {r["event_id"]: r for r in review}
    rows, left = [], {"not the transmission-voltage class, or not reviewed": 0, "no unit printed": 0, "column not checked": 0, "another customer's rate": 0}
    for _, r in d.iterrows():
        rule, v = DELIVERY.get(r["source"]), by.get(r["event_id"])
        if rule is None:
            continue
        if v is None:
            left["not the transmission-voltage class, or not reviewed"] += 1
            continue
        if not r["unit_as_written"].strip():
            left["no unit printed"] += 1
            continue
        many = int(r["figures_in_sentence"] or 1) > 1
        if many and not v["column_checked"]:
            left["column not checked"] += 1
            continue
        applies = str(v.get("applies_to_a_for_profit_datacenter") or "yes")
        if applies.startswith("no"):
            left["another customer's rate"] += 1
            continue
        name = r["charge_name"].strip()
        if name.lower() in GENERIC or name == r["rate_class"]:
            name = re.sub(r"^[\d.]+\s*", "", r["schedule"]).strip() or name
        rows.append(dict(utility=rule["utility"], rate_class=r["rate_class"], kind=v["kind"], charge=" ".join(name.split()), value=float(r["amount"]),
                         value_as_written=r["value_as_written"], unit=" ".join(r["unit_as_written"].split()), effective=r["effective_date_as_written"] or None,
                         document=r["document_title"], url=r["source_url"], page=r["page"] or None, sentence=" ".join(r["sentence"].split()),
                         column=f"checked against the printed header: {v['header_words']}" if many and v.get("header_words") else "",
                         applies="" if applies == "yes" else applies, why=" ".join(str(v.get("why") or "").split()), terms=FILING))
    order = list(DELIVERY)
    src_of = {v["utility"]: k for k, v in DELIVERY.items()}
    rows.sort(key=lambda r: (order.index(src_of[r["utility"]]), KINDS.index(r["kind"]) if r["kind"] in KINDS else 9, -abs(r["value"]), r["charge"]))
    return rows, left


def matrix_rows(m):
    """The Commission's transmission charge matrix as the page shows it: the statewide rate, cost and load, and the four
    utilities' own rows, for each year and matrix, each as printed with its document, page and line. Nothing computed."""
    codes = {v["code"]: v["utility"] for v in DELIVERY.values()}
    out = []
    for _, r in m.iterrows():
        q, code = r["quantity"], r["entity_code"]
        if not ((q in MATRIX_STATEWIDE) or (q in MATRIX_PROVIDER and code in codes)):
            continue
        out.append(dict(year=r["year"], matrix=r["matrix"], scope=codes.get(code, "ERCOT"), quantity=q, value=float(r["amount"]), value_as_written=r["value_as_written"],
                        unit=r["unit_as_written"], header=r["column_header_as_written"], status=r["status"], docket=r["docket"], item=r["item"], filed=r["date_filed"],
                        document=r["document_title"], url=r["source_url"], page=r["page"] or None, scan_url=r["scan_url"], scan_page=r["scan_page"] or None,
                        sentence=" ".join(r["sentence"].split()), docket_status=r["docket_status"], digits_spaced=r["digits_spaced_in_text"] == "yes"))
    scopes = ["ERCOT"] + [v["utility"] for v in DELIVERY.values()]
    out.sort(key=lambda r: (r["year"], r["matrix"], scopes.index(r["scope"]), (MATRIX_STATEWIDE + MATRIX_PROVIDER).index(r["quantity"])))
    return out


def delivery(in_dir, out_dir, built, log):
    """The site's copy of the Texas delivery charges a transmission-voltage load pays, each as its tariff states it,
    with the line it was read from, and of the Commission's transmission charge matrix. Nothing is computed here.
    Without a table on this machine its part of the kept file stands."""
    path, mpath, kept_path = os.path.join(in_dir, f"{DELIVERY_TABLE}.csv"), os.path.join(in_dir, f"{MATRIX_TABLE}.csv"), os.path.join(out_dir, "texas_delivery.json")
    kept = {}
    if os.path.exists(kept_path):
        with open(kept_path, encoding="utf-8") as f:
            kept = json.load(f)
    if not os.path.exists(path) and not os.path.exists(mpath):
        log(f"  {DELIVERY_TABLE} and {MATRIX_TABLE} are not on this machine; the kept delivery file stands")
        return
    with open(REVIEW, encoding="utf-8") as f:
        review = json.load(f)["rows"]
    if os.path.exists(path):
        d = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
        rows, left = delivery_rows(d, review)
        log(f"  delivery: {len(rows)} charges of {sorted({r['utility'] for r in rows})} written; left out: {left}")
    else:
        rows = kept.get("rows", [])
        log(f"  {DELIVERY_TABLE} is not on this machine; the kept delivery rows stand")
    if os.path.exists(mpath):
        m = pd.read_csv(mpath, skiprows=ip.header_rows(mpath), dtype=str, keep_default_na=False)
        matrix = matrix_rows(m)
        log(f"  matrix: {len(matrix)} figures of the Commission's transmission charge matrices written, of {len(m)} held")
    else:
        matrix = kept.get("matrix", [])
        log(f"  {MATRIX_TABLE} is not on this machine; the kept matrix rows stand")
    obj = dict(table=DELIVERY_TABLE, matrix_table=MATRIX_TABLE, built=built, license="internal",
               note="Each charge as its tariff prints it, read by a model and kept only where the line is found in the page's text with the figure in it; "
                    "the Commission's matrix figures the same way. Shown as public regulatory filings, each with its document, address and date.",
               rows=rows, withheld=[], matrix=matrix)
    write_if_changed(kept_path, obj)


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


def read_clean(in_dir, grid, std, lic, log):
    """The carbon-free share of the grid's generation by hour (percent, one decimal), by year: {year: the year's hours
    in the grid's standard time, nan where not held}. {} when the table is not on this machine (the kept files' series
    stand) or is not public."""
    if lic.get(CLEAN_TABLE) not in (None, "public"):
        return {}
    path = os.path.join(in_dir, f"{CLEAN_TABLE}.csv")
    if not os.path.exists(path):
        log(f"  {grid}: {CLEAN_TABLE} is not on this machine; the kept carbon-free hours stand")
        return {}
    if "_clean" not in read_clean.__dict__:
        d = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc", "value"])
        d = d[d["variable"] == "carbon_free_share_pct"].dropna(subset=["value"])
        d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
        read_clean._clean = d.drop_duplicates(["entity", "ts"], keep="last")
    d = read_clean._clean
    d = d[d["entity"] == f"iso:{grid}"]
    out = {}
    if d.empty:
        return out
    ys, hs = to_std(pd.DatetimeIndex(d["ts"]), std)
    vals = np.round(d["value"].values.astype(float), 1)
    for y in np.unique(ys):
        m = ys == y
        arr = np.full(year_hours(int(y)), np.nan)
        arr[hs[m]] = vals[m]
        out[int(y)] = arr
    log(f"  {grid}: carbon-free share by hour from {CLEAN_TABLE}, {len(d):,} hours, years {min(out)} to {max(out)}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="What a datacenter pays: the site's files for /cost-of-power")
    ap.add_argument("--out-dir", help="a trial run: the files under this directory; nothing in site/data")
    ap.add_argument("--in-dir", help="read the price tables from this directory instead of warehouse/output (a trial)")
    a = ap.parse_args(argv)
    out_dir = a.out_dir or SITE_DIR
    os.makedirs(out_dir, exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    built = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else ip.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"datacenter_page_{run_id}.log"))
    lic, paused = pc.licenses()
    internal = [t for t in TABLES if lic.get(t) not in (None, "public")]
    log(f"  internal price tables, not read: {internal}; publishers under review, not read: {sorted(paused)}")
    x = pc.read_prices(a.in_dir or ip.OUT_DIR, FIRST, log, tables=[t for t in TABLES if t not in internal])   # an internal table is not read at all
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
        # with the hours of the files already kept. Session 140: a region's market is held one way, whole, across
        # builds too. Where the kept file's hours and this build's are of two kinds (the operator's own hourly report
        # in one, the mean of four 15-minute prices in the other: the runner holds only the rolling 15-minute tables,
        # the data machine the hourly history), the kind that holds more hours stands whole and the other adds nothing.
        old_regions = {r["id"]: r for r in old_index.get("regions", [])}
        whole_old = set()
        for (node, key), h in list(how.items()):
            was = old_regions.get(node, {}).get(key, {})
            if was.get("basis") and h["basis"] and was["basis"] != h["basis"]:
                new_hours = sum(int((~np.isnan(years[y][node][key])).sum()) for y in years if key in years[y].get(node, {}))
                if new_hours > int(was.get("hours") or 0):
                    for y, f in kept.items():   # this build's kind holds more: the kept hours of the other kind are dropped
                        f.get("regions", {}).get(node, {}).pop(key, None)
                    log(f"  {iso} {node} {key}: this build's {h['basis']} hours ({new_hours:,}) stand whole; the kept {was['basis']} hours ({was.get('hours')}) are not mixed in")
                else:
                    whole_old.add((node, key))
                    for y in years:
                        years[y].get(node, {}).pop(key, None)
                    how.pop((node, key))
                    log(f"  {iso} {node} {key}: the kept {was['basis']} hours ({was.get('hours')}) stand whole; this build's {h['basis']} hours ({new_hours:,}) are not mixed in")
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
        clean_years = read_clean(ip.OUT_DIR, iso, g["std"], lic, log)
        withheld = str(demand_source or "").startswith("withheld:")
        demand_summary = {} if withheld else dict(old_index.get("demand", {}))
        for y in sorted(set(years) | set(dem_years)):
            n = year_hours(y)
            obj = {"grid": iso, "year": y, "hours": n, "built": built, "regions": {}}
            for node, sides in sorted(years.get(y, {}).items()):
                obj["regions"][node] = {k: trimmed(arr) for k, arr in sorted(sides.items())}
            c = merged(untrimmed(kept[y]["clean"], n) if y in kept and "clean" in kept[y] else None, clean_years.get(y))
            if c is not None and (~np.isnan(c)).any():
                obj["clean"] = trimmed(c)
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
        for node in sorted({n for y in years for n in years[y]}):
            rec = {"id": node, "entity": f"{iso}:{node}"}
            zone = ZONES.get(iso, {}).get(node)
            if zone:
                rec.update(kind="zone", name=zone["name"], ref=zone["ref"])
            elif iso in ZONES:
                rec["kind"] = "hub"
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
