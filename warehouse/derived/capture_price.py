#!/usr/bin/env python3
"""The capture price of a solar and a wind plant at every public hub and zone (session 145).

Energy Research Warehouse (ERW). No warehouse table is written and no request is made: this reads the public hub and
zone price tables held and the grid's hourly solar and wind generation, and writes the site's own file for
/cost-of-power/seller, site/data/seller/capture.json. Method: docs/methods/cost_of_power.md, "The capture price".

    python warehouse/derived/capture_price.py                                   # the tables of this copy
    python warehouse/derived/capture_price.py --in-dir C:/.../warehouse/output  # the tables of another copy (read only)
    python warehouse/derived/capture_price.py --out-dir DIR                     # a trial run: the file under DIR
    python warehouse/derived/capture_price.py --fixture-dir DIR --fixture-hub ercot:HB_WEST --fixture-week 2026-06-01
                                                                                # also cut a week of the real rows for a test

What a capture price is. For a hub, a fuel (solar, wind) and a market (real time, day-ahead), over a span of hours:

    generation-weighted price = sum(price x generation) / sum(generation)      USD per MWh
    flat average              = sum(price) / hours                             USD per MWh, over the same hours
    premium or discount       = the first less the second, in USD per MWh, and as a percent of the flat average

over the hours in which both the price and the fuel's generation are held. The generation is the grid's whole fleet
(the hours of warehouse/derived/mix_profile.py, hours_of: EIA-930's hourly net generation by source, and for
California from 16 December 2025 CAISO's own supply by fuel), so the shape is the fleet's and not a site's. An hour of
generation is held when the fuel's own value is not blank. The mix's test of a whole hour (do all the sources add up to
the total) is not applied: it asks about every source, and it fails in Texas from 6 to 14 December 2025 because EIA's
"other" repeats the batteries' output there, while solar and wind stand as reported; with it, December 2025 would hold
87 percent of its hours and Texas would have no twelve months to September 2026. The log counts the hours used that
fail it. An hour in which the fuel's generation is below zero (a plant's own use at night) weighs nothing and stays in
the flat average.

The prices are those of warehouse/derived/price_compare.py (its reader, and its rule for an hour of real time: the mean
of the hour's four 15-minute prices, held only when all four are; where a real-time price is held two ways, the one
that holds more hours is used whole). The two histories session 140 pulled (ercot_zone_prices_history,
iso_zone_prices_history) are read when they are on the machine; without them the file holds what the other tables
give. A table marked internal in coverage.csv, or whose own header does not say "License: public", is not read. A
publisher in warehouse/metadata/paused_sources.csv is not read: MISO's hubs appear in no figure.

The file holds months, never a span: for each hub, market and fuel, each local month's
    [hours used, hours in the month, sum of the prices, sum of the generation in MWh, sum of price x generation]
A month counts when the hours used are at least NEAR (95 percent) of the month's hours. The page (site/lib/capture.ts)
adds counted months up: the last twelve months are the newest counted month and the eleven before it, when all twelve
count; a year is whole with twelve counted months, else it is marked partial and holds its counted months only.
Nothing is filled or scaled: a month under 95 percent is in no figure.
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
import mix_profile as mp  # noqa: E402  (the grid's hours of generation by source: hours_of)
import price_compare as pc  # noqa: E402  (the reader of every hub and zone price table, and the 15-minute to hourly rule)

SITE_FILE = os.path.join(ROOT, "site", "data", "seller", "capture.json")
METHOD = "docs/methods/cost_of_power.md"
NEAR = 0.95        # a month counts when the hours with both a price and the fuel's generation are at least this share of it
SINCE = "2018-12-31"  # the mix's hours begin in January 2019, local time
FUELS = ("solar", "wind")
SIDES = (("rtm", "rt"), ("dam", "da"))
# the price tables read: the comparison's own, and the two histories of session 140 when they are on the machine
EXTRA = ["ercot_zone_prices_history", "iso_zone_prices_history"]
TABLES = ["iso_hub_prices_history", "ercot_all_hub_prices_history"] + EXTRA + [t for t in pc.TABLES if t not in ("iso_hub_prices_history", "ercot_all_hub_prices_history")]
# the public grids, with each one's main hub (the seller's model is priced there) and its time zone
GRIDS = {
    "ercot": dict(name="ERCOT", tz="America/Chicago", main="HB_HUBAVG"),
    "caiso": dict(name="CAISO", tz="America/Los_Angeles", main="TH_SP15_GEN-APND"),
    "nyiso": dict(name="NYISO", tz="America/New_York", main="N.Y.C."),
    "isone": dict(name="ISO-NE", tz="America/New_York", main=".H.INTERNAL_HUB"),
    "spp": dict(name="SPP", tz="America/Chicago", main="SPPNORTH_HUB"),
}
# the grids shown and blanked, with the words the page shows (the owner's rule)
BLANK = {
    "miso": dict(name="MISO", words="paused while terms are reviewed"),
    "pjm": dict(name="PJM", words="licensed source needed"),
}


def header_license(path):
    """The license a table's own provenance header states ("# License: public ..."), lower case, or ""."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            if line.lower().startswith("# license:"):
                return line.split(":", 1)[1].strip().lower()
    return ""


def readable(in_dir, lic, log):
    """The price tables that are on the machine and public: by coverage.csv, or, for a table coverage.csv does not list
    yet, by the table's own header."""
    out = []
    for t in TABLES:
        path = os.path.join(in_dir, f"{t}.csv")
        if not os.path.exists(path):
            log(f"  {t}: not on this machine")
            continue
        known = lic.get(t)
        if known is None:
            stated = header_license(path)
            if not stated.startswith("public"):
                log(f"  {t}: not in coverage.csv and its header does not say License: public ({stated[:60] or 'no license line'}); not read")
                continue
            log(f"  {t}: not in coverage.csv yet; its header says License: {stated[:40]}")
        elif known != "public":
            log(f"  {t}: {known} in coverage.csv; not read")
            continue
        out.append(t)
    return out


def read_one(in_dir, table, log):
    """One price table through price_compare's reader, made small: entity, side, freq as categories. None when the
    table holds no row from SINCE."""
    try:
        try:
            x = pc.read_prices(in_dir, SINCE, log, tables=[table])  # session 140's reader takes the tables
        except TypeError:
            kept = pc.TABLES
            pc.TABLES = [table]
            try:
                x = pc.read_prices(in_dir, SINCE, log)
            finally:
                pc.TABLES = kept
    except ValueError:
        return None  # no row from SINCE: the reader had nothing to join
    x = x[["entity", "side", "ts", "value", "freq"]].copy()
    for c in ("entity", "side", "freq"):
        x[c] = x[c].astype("category")
    x["table"] = table
    x["table"] = x["table"].astype("category")
    return x


def hourly_side(e, side):
    """One market of one hub by hour (UTC): of the ways it is held (15-minute means, or the operator's own hourly
    report), the one that holds more hours, whole. Rows held in two tables: the first of TABLES."""
    s = e[e["side"] == side]
    best, basis, tables = None, "", []
    for f, part in s.groupby("freq", observed=True):
        part = part.sort_values("rank").drop_duplicates("ts", keep="first")
        c = pc.hourly(pd.Series(part["value"].values, index=pd.DatetimeIndex(part["ts"])).sort_index(), f).dropna()
        if best is None or len(c) > len(best):
            best, basis, tables = c, f, sorted(part["table"].astype(str).unique())
    return best, basis, tables


def hours_in_month(month, tz):
    a = pd.Timestamp(f"{month}-01", tz=tz)
    b = (pd.Period(month) + 1).to_timestamp().tz_localize(tz)
    return int(round((b - a) / pd.Timedelta(hours=1)))


def month_sums(price, gen, tz):
    """{local month: [hours used, hours in the month, sum of prices, sum of generation, sum of price x generation]} over
    the hours both series hold. price, gen: Series by the hour's start (UTC). Generation below zero weighs nothing."""
    d = pd.DataFrame({"p": price}).join(pd.DataFrame({"g": gen}), how="inner").dropna()
    if d.empty:
        return {}
    d["g"] = d["g"].clip(lower=0)
    d["pg"] = d["p"] * d["g"]
    d["m"] = d.index.tz_convert(tz).strftime("%Y-%m")
    s = d.groupby("m").agg(n=("p", "size"), sp=("p", "sum"), g=("g", "sum"), pg=("pg", "sum"))
    return {m: [int(r.n), hours_in_month(m, tz), round(float(r.sp), 2), round(float(r.g), 1), round(float(r.pg), 2)] for m, r in s.iterrows()}


# the page's arithmetic, here for the log and the tests: site/lib/capture.ts holds the same rules

def counted(rec, near=NEAR):
    return rec[0] >= near * rec[1] - 1e-9


def figure(recs):
    """The capture figures of a list of month records, or None when no generation or no hour is in them."""
    n, sp, g, pg = (sum(r[i] for r in recs) for i in (0, 2, 3, 4))
    if not n or g <= 0:
        return None
    price, flat = pg / g, sp / n
    return dict(price=price, flat=flat, premium=price - flat, pct=(100 * (price - flat) / flat if flat > 0 else None), hours=n, mwh=g)


def prev_month(m, k):
    return (pd.Period(m) - k).strftime("%Y-%m")


def last_twelve(months, near=NEAR):
    """The newest counted month whose eleven months before it all count: the twelve, oldest first, or None."""
    for m in sorted(months, reverse=True):
        twelve = [prev_month(m, k) for k in range(11, -1, -1)]
        if all(t in months and counted(months[t], near) for t in twelve):
            return twelve
    return None


def years(months, near=NEAR):
    """Each calendar year's counted months: {year: (months counted, whole, figure)}."""
    out = {}
    for y in sorted({m[:4] for m in months}):
        ms = [m for m in months if m[:4] == y and counted(months[m], near)]
        if ms:
            out[y] = (len(ms), len(ms) == 12, figure([months[m] for m in ms]))
    return out


def mix_hours(iso, cache_dir, log):
    """The grid's hours of solar and wind from the mix (mix_profile.hours_of), and the workbook's name. With a cache
    folder, the hours read from a workbook are kept there and read back while the workbook is the same file (reading
    one workbook takes minutes)."""
    wb = mp.workbook(mp.GRIDS[iso]["ba"])
    stamp = f"{os.path.basename(os.path.dirname(wb))}/{os.path.basename(wb)}:{os.path.getsize(wb)}"
    cached = os.path.join(cache_dir, f"mix_hours_{iso}.pkl") if cache_dir else None
    if cached and os.path.exists(cached):
        kept = pd.read_pickle(cached)
        if kept.attrs.get("stamp") == stamp:
            log(f"  {iso}: the mix's hours read back from {cached} (workbook {stamp})")
            return kept, wb
    hours, wb = mp.hours_of(iso, log)
    gen = hours[["solar", "wind", "held", "side"]].copy()
    if cached:
        os.makedirs(cache_dir, exist_ok=True)
        gen.attrs["stamp"] = stamp
        gen.to_pickle(cached)
    return gen, wb


def cut_fixture(folder, in_dir, entity, week, x, gen, tz, log):
    """A week of the real rows, for tests/test_session145.py: the hub's price rows as price_compare read them, and the
    mix's hours of the same week."""
    os.makedirs(folder, exist_ok=True)
    a = pd.Timestamp(week, tz=tz).tz_convert("UTC")
    b = a + pd.Timedelta(days=7)
    rows = x[(x["entity"] == entity) & (x["ts"] >= a) & (x["ts"] < b)].sort_values(["side", "freq", "ts", "rank"]).drop_duplicates(["side", "freq", "ts"], keep="first")
    p = pd.DataFrame({"entity": rows["entity"].astype(str), "side": rows["side"].astype(str), "freq": rows["freq"].astype(str), "ts_utc": [ip.utc_iso(t) for t in rows["ts"]],
                      "value": rows["value"].values, "table": rows["table"].astype(str)})
    g = gen[(gen.index >= a) & (gen.index < b)]
    stamp = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    with open(os.path.join(folder, "prices_week.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Energy Research Warehouse (ERW): a test sample, the price rows of {entity} for the week from {week} ({tz}), as the warehouse holds them\n")
        f.write(f"# Cut {stamp} by warehouse/derived/capture_price.py --fixture-dir from the tables {sorted(p['table'].unique())}; side dam is day-ahead, rtm real time; USD/MWh; ts_utc is the interval's start\n")
        p.to_csv(f, index=False, lineterminator="\n")
    with open(os.path.join(folder, "generation_week.csv"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Energy Research Warehouse (ERW): a test sample, the grid's hourly solar and wind generation for the same week (MWh in the hour; ts_utc is the hour's start)\n")
        f.write(f"# Cut {stamp} by warehouse/derived/capture_price.py --fixture-dir from the hours of mix_profile.hours_of (EIA-930's hourly net generation by source); held is the mix's own test of the hour\n")
        pd.DataFrame({"ts_utc": [ip.utc_iso(t) for t in g.index], "solar": g["solar"].values, "wind": g["wind"].values, "held": g["held"].astype(int).values}).to_csv(f, index=False, lineterminator="\n")
    log(f"  fixture: {len(p)} price rows and {len(g)} hours of generation for {entity}, the week from {week}, under {folder}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="The capture price of a solar and a wind plant at every public hub and zone")
    ap.add_argument("--in-dir", help="read the tables from this folder (another copy's warehouse/output); nothing is written there")
    ap.add_argument("--raw-dir", help="the folder of the EIA-930 workbooks (default: warehouse/raw/eia930_emissions beside the tables read)")
    ap.add_argument("--out-dir", help="a trial run: the file under this directory; nothing in site/data")
    ap.add_argument("--cache-dir", help="keep the mix's hours read from each workbook under this folder, and read them back while the workbook is the same")
    ap.add_argument("--fixture-dir", help="also cut a week of the real rows for a test, under this folder")
    ap.add_argument("--fixture-hub", default="ercot:HB_WEST")
    ap.add_argument("--fixture-week", default="2026-06-01", help="the local day the week begins")
    a = ap.parse_args(argv)
    in_dir = os.path.abspath(a.in_dir) if a.in_dir else ip.OUT_DIR
    out_path = os.path.join(a.out_dir, "capture.json") if a.out_dir else SITE_FILE
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    run_id = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    built = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    log_dir = os.path.join(a.out_dir, "logs") if a.out_dir else os.path.join(ROOT, "warehouse", "output", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"capture_price_{run_id}.log"))
    log(f"ERW capture price run {run_id}: tables from {in_dir}")
    # the mix's reader takes the tables of ip.OUT_DIR and the workbooks of mp.RAW: both are pointed at the copy read
    ip.OUT_DIR = in_dir
    mp.RAW = os.path.abspath(a.raw_dir) if a.raw_dir else os.path.join(os.path.dirname(in_dir), "raw", "eia930_emissions")
    # California's hydro gap of 2019 and 2020 is filled by the mix from a 149 MB history of CAISO's own supply. Solar
    # and wind are not part of that gap (EIA held them throughout), so the history is not read here.
    mp.caiso_gap = lambda: None

    lic, _ = pc.licenses()
    tables = readable(in_dir, lic, log)
    paused = {iso for iso in list(GRIDS) + list(BLANK) if ip.paused(iso)}
    log(f"  price tables read: {tables}; publishers paused, in no figure: {sorted(paused)}")
    parts = []
    for i, t in enumerate(tables):
        x = read_one(in_dir, t, log)
        if x is None:
            log(f"  {t}: no row from {SINCE}")
            continue
        x["iso"] = x["entity"].astype(str).str.split(":", n=1).str[0]
        x = x[x["iso"].isin([g for g in GRIDS if g not in paused])].drop(columns="iso")
        x["rank"] = np.int8(i)
        parts.append(x)
    x = pd.concat(parts, ignore_index=True)
    del parts
    x["entity"] = x["entity"].astype(str)
    tables_read = sorted(x["table"].astype(str).unique())

    out = {"built": built, "method": METHOD, "near": NEAR, "tables": tables_read, "grids": {}, "blank": {}}
    for iso, b in BLANK.items():
        out["blank"][iso] = dict(name=b["name"], words=b["words"])
    summary = []
    for iso, g in GRIDS.items():
        if iso in paused:
            out["blank"][iso] = dict(name=g["name"], words="paused while terms are reviewed")
            continue
        gen, wb = mix_hours(iso, a.cache_dir, log)
        used = {}
        for fuel in FUELS:
            ok = gen[fuel].notna()
            used[fuel] = gen.loc[ok, fuel]
            log(f"  {iso} {fuel}: {len(gen):,} hours of the mix, {int(ok.sum()):,} with {fuel} not blank and used; of them {int((ok & ~gen['held']).sum()):,} fail the mix's "
                f"test of the whole hour; below zero (weigh nothing): {int((used[fuel] < 0).sum()):,}")
        sub = x[x["entity"].str.startswith(iso + ":")]
        hubs = []
        for entity, e in sub.groupby("entity"):
            node = entity.split(":", 1)[1]
            rec = {"id": node, "entity": entity}
            for side, key in SIDES:
                h, basis, tabs = hourly_side(e, side)
                if h is None or h.empty:
                    continue
                rec[key] = {"basis": basis, "tables": tabs, "first": ip.utc_iso(h.index.min()), "last": ip.utc_iso(h.index.max()), "hours": int(len(h))}
                for fuel in FUELS:
                    months = month_sums(h, used[fuel], g["tz"])
                    if months:
                        rec[key][fuel] = months
            if "rt" in rec or "da" in rec:
                hubs.append(rec)
        hubs.sort(key=lambda r: (r["id"] != g["main"], -max(r.get("rt", {}).get("hours", 0), r.get("da", {}).get("hours", 0)), r["id"]))
        sides = sorted(set(gen["side"]))
        out["grids"][iso] = dict(name=g["name"], tz=g["tz"], main=g["main"], workbook=os.path.basename(wb), generation=sides,
                                 mix_first=ip.utc_iso(gen.index.min()), mix_last=ip.utc_iso(gen.index.max()), hubs=hubs)
        for r in hubs:
            for key in ("rt", "da"):
                for fuel in FUELS:
                    months = r.get(key, {}).get(fuel)
                    if not months:
                        continue
                    t = last_twelve(months)
                    f = figure([months[m] for m in t]) if t else None
                    ys = years(months)
                    line = f"  {iso} {r['id']} {key} {fuel}: {sum(1 for m in months if counted(months[m]))} of {len(months)} months count"
                    if f:
                        line += f"; last twelve months {t[0]} to {t[-1]}: {f['price']:.2f} against {f['flat']:.2f} USD/MWh, {f['premium']:+.2f} ({f['pct']:+.1f} percent), {f['hours']:,} hours"
                        summary.append((iso, r["id"], key, fuel, t[0], t[-1], f))
                    else:
                        line += "; no twelve counted months in a row"
                    line += "; years: " + ", ".join(f"{y}{'' if whole else f' (partial, {n} months)'} {fg['premium']:+.2f}" for y, (n, whole, fg) in ys.items() if fg)
                    log(line)
        if a.fixture_dir and a.fixture_hub.startswith(iso + ":"):
            cut_fixture(a.fixture_dir, in_dir, a.fixture_hub, a.fixture_week, x, gen, g["tz"], log)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, separators=(",", ":"), allow_nan=False)
    log(f"  written: {out_path} ({os.path.getsize(out_path):,} bytes)")
    log.close()
    print(f"capture price: {sum(len(v['hubs']) for v in out['grids'].values())} hubs and zones of {len(out['grids'])} grids; blank: {sorted(out['blank'])}; "
          f"{len(summary)} last-twelve-month figures; {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
