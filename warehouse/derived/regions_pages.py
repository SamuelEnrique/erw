#!/usr/bin/env python3
"""The whole country's page files: EIA's thirteen regions of the lower 48 and every balancing authority, in the shapes
of the seven grids' files (session 8001, chain 501 part B).

Energy Research Warehouse (ERW). Writes new files under site/data/regions/ only; no table, no request. The contract:
docs/state/page_files_regions.md. Method: docs/methods/regions_pages.md.

    python warehouse/derived/regions_pages.py                         # every file (index, demand, mix, trade, events)
    python warehouse/derived/regions_pages.py --only demand mix       # some of them
    python warehouse/derived/regions_pages.py --weather               # also the regions' demand with the weather taken out
                                                                      # (without it, each file keeps the weather object it had)
    python warehouse/derived/regions_pages.py --site-dir DIR          # a trial: the files under DIR

Inputs, all in warehouse/output: eia930_region_hourly (the regions' net generation and total interchange),
eia930_ba_demand_hourly and eia930_ba_supply_hourly (every balancing authority), eia930_region_fuel_hourly (net
generation by source), region_weather_hourly (each region's population-weighted temperature), eia930_region_pair_hourly
(each region pair's flow, both sides' reports); and EIA's reference tables (warehouse/raw/eia930_reference) for codes,
names, time zones, regions and which authorities file no demand.

A REGION'S DEMAND is the sum of the demand of its balancing authorities that file demand: those EIA's reference tables
do not mark "Generation Only BA", that are U.S. authorities, and that are active in the hour (after their activation date
and before their retirement date). The hour is written only when every one of them holds a value; nothing is filled.
(eia930_region_hourly writes a region's demand only when every authority of the region holds demand, generation-only
ones included, which never file it, so it holds no demand for the Carolinas, the Northwest, the Southeast and the
Southwest, and the Midwest's only from September 2022 to May 2025.) The demand of an authority is its own.

Then, as the seven grids' files: the hours used are those that pass the impossible-value rule (demand_growth.screened);
daily, the day's demand and peak only for a day whose every hour is used; growth by year from demand_growth.summarize,
keys unchanged; with --weather, demand_weather.analyse on the region's demand and its weather, heating and cooling
degrees taken from the weighted temperature (base 65 F), keys unchanged. Mix by month and local hour over the complete
days (every hour held), as generation_mix_hourly_profile; a month is written with at least 90 percent of its days.
Trade by EIA's Eastern month, each side's report. Events: every hour of the window and the baseline hours.
"""

import argparse
import datetime as dt
import glob
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
import demand_growth as dg  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
SITE = os.path.join(ROOT, "site", "data", "regions")
METHOD = "docs/methods/regions_pages.md"
LICENSE = "public"
REGIONS = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"]
GRIDS = {"ERCO": "TEX", "CISO": "CAL", "PJM": "MIDA", "MISO": "MIDW", "SWPP": "CENT", "NYIS": "NY", "ISNE": "NE"}
ALIKE = {"TEX": "ERCO", "NY": "NYIS", "NE": "ISNE", "MIDA": "PJM"}   # a region and a grid that cover nearly the same ground
TZ = {"Eastern": "America/New_York", "Central": "America/Chicago", "Mountain": "America/Denver", "Arizona": "America/Phoenix",
      "Pacific": "America/Los_Angeles"}
SOURCES = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"]
NEAR_MONTH = 0.90
HOURLY_DAYS = 35
PARTS = ["index", "demand", "mix", "trade", "events"]


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read(name, cols, filt=None):
    """A table's columns, header lines skipped by count (never by the comment character)."""
    p = os.path.join(OUT, name + ".csv")
    fh = open(p, "rb")
    for _ in range(ip.header_rows(p)):
        fh.readline()
    d = pd.read_csv(fh, usecols=cols, engine="pyarrow")
    fh.close()
    if filt is not None:
        d = d[filt(d)]
    if "ts_utc" in d:
        d["ts"] = pd.to_datetime(d["ts_utc"], utc=True)
    return d


def reference():
    import openpyxl
    f = sorted(glob.glob(os.path.join(ROOT, "warehouse", "raw", "eia930_reference", "*", "EIA930_Reference_Tables.xlsx")))[-1]
    rows = list(openpyxl.load_workbook(f, read_only=True)["BAs"].iter_rows(values_only=True))
    head = rows[0]
    out = {}
    for r in rows[1:]:
        if not r[0]:
            continue
        x = dict(zip(head, r))

        def day(v):
            if not v:
                return None
            if isinstance(v, dt.datetime):
                return v.strftime("%Y-%m-%d")
            m, d_, y = str(v).split("/")
            return f"{int(y):04d}-{int(m):02d}-{int(d_):02d}"
        out[x["BA Code"]] = dict(code=x["BA Code"], name=x["BA Name"], tz=BA_TZ.get(x["BA Code"], TZ.get(x["Time Zone"] or "")), region=x["Region/Country Code"],
                                 generation_only=x["Generation Only BA"] == "Yes", us=x["U.S. BA"] == "Yes",
                                 active=x["Active BA"] == "Yes", activated=day(x["Activation Date"]), retired=day(x["Retirement Date"]))
    return out, f


def series(d, entity, variable):
    x = d[(d["entity"] == entity) & (d["variable"] == variable)]
    return pd.Series(x["value"].to_numpy(dtype=float), index=pd.DatetimeIndex(x["ts"])).sort_index()


def hourly_index(s):
    return s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="h")) if len(s) else s


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if np.isnan(o) else round(float(o), 4)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, pd.Timestamp):
        return ip.utc_iso(o)
    return o


def write(site, rel, doc):
    path = os.path.join(site, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(clean(doc), f, separators=(",", ":"), allow_nan=False)
    return os.path.getsize(path)


def common(tables):
    return {"built": now(), "tables": tables, "method": METHOD, "license": LICENSE}


# ------------------------------------------------------------------------------------------------ the region's demand

def region_demand(region, ref, ba_dem):
    """The sum of the region's demand-filing authorities, written for an hour only when each active one holds it."""
    members = [c for c, r in ref.items() if r["region"] == region and r["us"] and not r["generation_only"]]
    cols = {}
    for c in members:
        s = series(ba_dem, f"eia930:{c}", "demand_mw")
        if len(s):
            cols[c] = s
    if not cols:
        return pd.Series(dtype=float), []
    frame = pd.DataFrame(cols)
    frame = frame.reindex(pd.date_range(frame.index.min(), frame.index.max(), freq="h"))
    need = pd.DataFrame(False, index=frame.index, columns=frame.columns)
    for c in frame.columns:
        r = ref[c]
        on = pd.Series(True, index=frame.index)
        if r["activated"]:
            on &= frame.index >= pd.Timestamp(r["activated"], tz=r["tz"] or "UTC")
        if r["retired"]:
            on &= frame.index < pd.Timestamp(r["retired"], tz=r["tz"] or "UTC")
        need[c] = on
    held = (frame.notna() | ~need).all(axis=1) & need.any(axis=1)
    total = frame.where(need).sum(axis=1, min_count=1).where(held)
    return total, sorted(cols)


REGION_TZ = {"CAL": "America/Los_Angeles", "CAR": "America/New_York", "CENT": "America/Chicago", "FLA": "America/New_York",
             "MIDA": "America/New_York", "MIDW": "America/Chicago", "NE": "America/New_York", "NW": "America/Los_Angeles",
             "NY": "America/New_York", "SE": "America/Chicago", "SW": "America/Phoenix", "TEN": "America/Chicago",
             "TEX": "America/Chicago"}
BA_TZ = {"MISO": "America/Chicago"}   # EIA's reference gives MISO Eastern (its market's clock); the seven grids' files count its days in Central


def region_tz(region, ref, ba_dem):
    """The time zone of most of the region's demand (the mean demand of its authorities, by EIA's zone), except the
    Midwest, which is counted in Central time as the seven grids' files count MISO's days (REGION_TZ holds the result)."""
    if region in REGION_TZ:
        return REGION_TZ[region]
    w = {}
    for c, r in ref.items():
        if r["region"] != region or not r["tz"]:
            continue
        s = ba_dem.loc[(ba_dem["entity"] == f"eia930:{c}") & (ba_dem["variable"] == "demand_mw"), "value"]
        if len(s):
            w[r["tz"]] = w.get(r["tz"], 0.0) + float(s.mean())
    return max(w, key=w.get) if w else "America/New_York"


def daily(used, raw, tz):
    """Each local day from the first held to the last: demand MWh and peak only when every hour of the day is used."""
    df = pd.DataFrame({"v": used.to_numpy()}, index=used.index)
    df["day"] = used.index.tz_convert(tz).strftime("%Y-%m-%d")
    g = df.groupby("day")["v"]
    n_hours, n_used, s, mx = g.size(), g.count(), g.sum(), g.max()
    v = df.dropna()
    idx = v.groupby("day")["v"].idxmax()
    days = list(n_hours.index)
    whole = {d_: bool(n_used[d_] == n_hours[d_]) for d_ in days}
    return {"days": days,
            "demand_mwh": [round(float(s[d_]), 1) if whole[d_] else None for d_ in days],
            "peak_mw": [round(float(mx[d_]), 1) if whole[d_] else None for d_ in days],
            "peak_at": [ip.utc_iso(idx[d_]) if whole[d_] and d_ in idx.index else None for d_ in days],
            "hours": [int(n_used[d_]) for d_ in days]}


def weather_frame(region, weather):
    t = series(weather, f"eia930:{region}", "temperature_f")
    if not len(t):
        return None
    w = pd.DataFrame({"temperature_f": t})
    w["heating_degrees_f"] = (65.0 - w["temperature_f"]).clip(lower=0)
    w["cooling_degrees_f"] = (w["temperature_f"] - 65.0).clip(lower=0)
    w["dew_point_f"] = np.nan
    return w


def demand_doc(code, name, tz, level, raw, basis, summed, weather=None, prior=None, with_weather=False):
    full = hourly_index(raw)
    used = dg.screened(full)
    since = full[full.index >= pd.Timestamp(f"{dg.BASE}-01-01", tz=tz).tz_convert("UTC")]
    left = since[used.reindex(since.index).isna() & since.notna()]
    if used[used.index >= pd.Timestamp(f"{dg.BASE}-01-01", tz=tz).tz_convert("UTC")].notna().any():
        years, at, last_month = dg.summarize(used, tz)
    else:   # an authority that stopped filing before 2019: no year to summarize
        years, at, last_month = {}, {}, None
    whole_years = sorted(y for y, r in years.items() if "avg_demand_mw" in r)
    doc = {**common(["eia930_ba_demand_hourly"] + (["region_weather_hourly"] if level == "region" else [])),
           "code": code, "name": name, "tz": tz, "level": level, "basis": basis}
    if summed:
        doc["bas_summed"] = summed
    doc["screened"] = {"blank": int(since.isna().sum()), "not_positive": int((left <= 0).sum()), "jumps": int((left > 0).sum())}
    doc["first_hour"] = ip.utc_iso(full.dropna().index.min()) if full.notna().any() else None
    doc["last_hour"] = ip.utc_iso(full.dropna().index.max()) if full.notna().any() else None
    doc["daily"] = daily(used, full, tz)
    doc["growth"] = {"base": dg.BASE, "last_year": whole_years[-1] if whole_years else None, "ytd_through": last_month,
                     "years": {str(y): r for y, r in sorted(years.items())}, "at": {str(y): v for y, v in sorted(at.items())}}
    if level == "region":
        if with_weather and weather is not None:
            import demand_weather as dw
            res = dw.analyse(full, weather, tz, None, dw.FEATURES)
            plain = dw.analyse(full, weather, tz, None, dw.PLAIN)
            doc["weather"] = {"name": name, "tz": tz, "fit": {**res["fit"], "plain_oos_mape_pct": plain["fit"]["oos_mape_pct"]},
                              "holdout": res["holdout"], "years": {y: v for y, v in res["years"].items() if int(y) > max(dw.TRAIN)},
                              "through": res["through"], "newest": res["newest"],
                              "train": list(dw.TRAIN), "metrics": list(dw.METRICS), "labels": dw.LABEL,
                              "weather_table": "region_weather_hourly",
                              "features": list(dw.FEATURES), "degrees_from": "the region's weighted temperature (base 65 F)"}
        elif prior and "weather" in prior:
            doc["weather"] = prior["weather"]
    return doc


# ------------------------------------------------------------------------------------------------ mix

def mix_doc(region, name, tz, fuel, net_gen, interchange, demand):
    srcs = {s: series(fuel, f"eia930:{region}", f"net_generation_{s}_mw") for s in SOURCES}
    idx = srcs["coal"].index
    for s in SOURCES:
        if len(srcs[s]) > len(idx):
            idx = srcs[s].index
    if not len(idx):
        return None
    full = pd.date_range(idx.min(), idx.max(), freq="h")
    f = pd.DataFrame({s: srcs[s].reindex(full) for s in SOURCES})
    held = f.drop(columns=["storage"]).notna().all(axis=1)
    f["demand"] = demand.reindex(full)
    f["net_generation"] = f[SOURCES].sum(axis=1, min_count=1).where(held)
    f["net_imports"] = (-interchange).reindex(full)
    loc = full.tz_convert(tz)
    f["day"], f["month"], f["year"], f["hour"] = loc.strftime("%Y-%m-%d"), loc.strftime("%Y-%m"), loc.year, loc.hour
    f["held"] = held
    gd = f.groupby("day")
    complete = (gd["held"].sum() == gd.size())
    f["complete"] = f["day"].map(complete)
    months, years = {}, {}
    for m, g in f.groupby("month"):
        y, mo = int(m[:4]), int(m[5:])
        days_in = pd.Period(m).days_in_month
        c = g[g["complete"]]
        days_held = c["day"].nunique()
        if days_held < NEAR_MONTH * days_in:
            continue
        r = {"avg": {}, "side": "eia930"}
        for k in SOURCES + ["demand", "net_generation"]:
            by = c.groupby("hour")[k].mean()
            r["avg"][k] = [round(float(by.get(h, np.nan)), 1) if pd.notna(by.get(h, np.nan)) else None for h in range(24)]
        tot = float(c["net_generation"].sum())
        for s in SOURCES:
            mwh = float(c[s].sum()) if c[s].notna().any() else None
            r[f"{s}_mwh"] = mwh
            r[f"{s}_share_pct"] = round(100 * mwh / tot, 2) if mwh is not None and tot else None
        r["net_generation_mwh"], r["days_held"], r["days_in_month"] = tot, float(days_held), float(days_in)
        months[m] = r
    for y, g in f.groupby("year"):
        ms = sorted(m for m in months if m.startswith(str(y)))
        due = sorted(set(g["month"]))
        if not ms:
            continue
        c = g[g["complete"] & g["month"].isin(ms)]
        r = {"avg": {}, "side": "eia930", "months": len(ms), "months_due": len(due), "missing": [m for m in due if m not in ms],
             "days_held": int(c["day"].nunique())}
        for k in SOURCES + ["demand", "net_generation"]:
            by = c.groupby("hour")[k].mean()
            r["avg"][k] = [round(float(by.get(h, np.nan)), 1) if pd.notna(by.get(h, np.nan)) else None for h in range(24)]
        tot = float(c["net_generation"].sum())
        for s in SOURCES:
            mwh = float(c[s].sum()) if c[s].notna().any() else None
            r[f"{s}_mwh"] = mwh
            r[f"{s}_share_pct"] = round(100 * mwh / tot, 2) if mwh is not None and tot else None
        r["net_generation_mwh"] = tot
        years[str(int(y))] = r
    # the newest 35 local days, by hour
    last_day = max(d_ for d_, ok in complete.items() if ok) if complete.any() else None
    hourly = None
    if last_day:
        end = pd.Timestamp(last_day, tz=tz) + pd.Timedelta(days=1)
        start = end - pd.Timedelta(days=HOURLY_DAYS)
        start = pd.Timestamp(start.strftime("%Y-%m-%d"), tz=tz)
        h = f[(f.index >= start.tz_convert("UTC")) & (f.index < end.tz_convert("UTC"))]
        hourly = {"hours": {"start": ip.utc_iso(h.index.min()), "step_hours": 1, "n": int(len(h))}}
        for k in SOURCES + ["demand", "net_generation", "net_imports"]:
            hourly[k] = [None if pd.isna(v) else round(float(v), 1) for v in h[k]]
    ms = sorted(months)
    return {**common(["eia930_region_fuel_hourly", "eia930_region_hourly", "eia930_ba_demand_hourly"]),
            "grid": region.lower(), "name": name, "tz": tz, "join": None, "first": ms[0] if ms else None, "upto": ms[-1] if ms else None,
            "sources": SOURCES, "months": months, "years": years, "hourly": hourly}


# ------------------------------------------------------------------------------------------------ trade

def trade_docs(pairs, names):
    pairs = pairs.copy()
    pairs["month"] = pairs["ts"].dt.tz_convert("America/New_York").dt.strftime("%Y-%m")
    months = sorted(pairs["month"].unique())
    hours_in = {m: int((pd.Timestamp(m + "-01", tz="America/New_York") + pd.offsets.MonthBegin(1) - pd.Timestamp(m + "-01", tz="America/New_York")) / pd.Timedelta(hours=1)) for m in months}
    docs = {}
    for ent, g in pairs.groupby("entity"):
        a, b = ent.split(":")[1].split("-")
        for me, other, own, their in ((a, b, -g["x_first_report"], -g["x_second_report"]), (b, a, g["x_second_report"], g["x_first_report"])):
            if me not in REGIONS:
                continue
            t = pd.DataFrame({"month": g["month"], "own": own.to_numpy(), "their": their.to_numpy()})
            t["both"] = t["own"].notna() & t["their"].notna()
            t["gap"] = (t["own"] - t["their"]).where(t["both"])
            agg = t.groupby("month").agg(own=("own", "sum"), their=("their", "sum"), gap=("gap", "sum"),
                                         ho=("own", "count"), ht=("their", "count"), hb=("both", "sum"))
            agg = agg.reindex(months)
            d = docs.setdefault(me, {"neighbors": {}})
            d["neighbors"][other] = {
                "net_imports_mwh": [None if pd.isna(r.ho) or r.ho == 0 else round(float(r.own), 1) for r in agg.itertuples()],
                "their_report_mwh": [None if pd.isna(r.ht) or r.ht == 0 else round(float(r.their), 1) for r in agg.itertuples()],
                "gap_mwh": [None if pd.isna(r.hb) or r.hb == 0 else round(float(r.gap), 1) for r in agg.itertuples()],
                "hours_own": [0 if pd.isna(r.ho) else int(r.ho) for r in agg.itertuples()],
                "hours_their": [0 if pd.isna(r.ht) else int(r.ht) for r in agg.itertuples()],
                "hours_both": [0 if pd.isna(r.hb) else int(r.hb) for r in agg.itertuples()]}
    out = {}
    for me, d in docs.items():
        tot = []
        for i, m in enumerate(months):
            ok = all(n["hours_own"][i] >= 0.5 * hours_in[m] for n in d["neighbors"].values())
            tot.append(round(sum(n["net_imports_mwh"][i] or 0.0 for n in d["neighbors"].values()), 1) if ok else None)
        out[me] = {**common(["eia930_region_pair_hourly"]), "code": me, "name": names.get(me, me), "months": months,
                   "hours_in_month": [hours_in[m] for m in months], "net_imports_mwh": tot,
                   "neighbors": dict(sorted(d["neighbors"].items()))}
    return out


# ------------------------------------------------------------------------------------------------ events

def events_list():
    import event_window as ew
    out = []
    e0 = ew.EVENTS[0]
    out.append(dict(event=e0["event"], title="Winter Storm Uri, February 2021", start=e0["start"], end=e0["end"],
                    baseline="the same calendar days of " + " and ".join(str(y) for y in e0["baseline"]),
                    years_back=[int(e0["start"][:4]) - y for y in e0["baseline"]], offsets=None))
    for e in ew.MULTI:
        out.append(dict(event=e["event"], title=e.get("label", e["event"]), start=e["start"], end=e["end"],
                        baseline="the same weekday " + " and ".join(str(o) for o in e["offsets"]) + " days earlier",
                        years_back=None, offsets=list(e["offsets"])))
    return out


def event_doc(e, region_series, pair_series):
    """region_series: {region: {key: hourly Series}}; pair_series: {pair: Series}. The window runs from the first day's
    midnight in Eastern time to the last day's midnight after, in Pacific time, so every region's local days are in it."""
    start = pd.Timestamp(e["start"], tz="America/New_York").tz_convert("UTC")
    end = (pd.Timestamp(e["end"], tz="America/Los_Angeles") + pd.Timedelta(days=1)).tz_convert("UTC")
    hours = pd.date_range(start, end, freq="h", inclusive="left")
    if e["offsets"]:
        shifts = [hours - pd.Timedelta(days=o) for o in e["offsets"]]
        offsets = e["offsets"]
    else:
        shifts = [pd.DatetimeIndex([h - pd.DateOffset(years=k) for h in hours]) for k in e["years_back"]]
        offsets = [f"{k} calendar year(s)" for k in e["years_back"]]

    def base(s):
        vals = [s.reindex(sh).to_numpy(dtype=float) for sh in shifts]
        st = np.vstack(vals)
        n = np.sum(~np.isnan(st), axis=0)
        with np.errstate(invalid="ignore"):
            m = np.where(n > 0, np.nansum(st, axis=0) / np.maximum(n, 1), np.nan)
        return m

    def arr(v):
        return [None if (v_ is None or (isinstance(v_, float) and np.isnan(v_))) else int(round(float(v_))) for v_ in v]
    regions = {}
    for r, keys in region_series.items():
        d = {}
        for k in ("demand_mw", "net_generation_mw", "net_imports_mw"):
            d[k] = arr(keys[k].reindex(hours).to_numpy(dtype=float))
        d["gen"] = {s: arr(keys["gen"][s].reindex(hours).to_numpy(dtype=float)) for s in SOURCES}
        b = {k: arr(base(keys[k])) for k in ("demand_mw", "net_generation_mw", "net_imports_mw")}
        b["gen"] = {s: arr(base(keys["gen"][s])) for s in SOURCES}
        d["baseline"] = b
        regions[r] = d
    pairs = {p: {"flow_mw": arr(s.reindex(hours).to_numpy(dtype=float)), "baseline_mw": arr(base(s))} for p, s in pair_series.items()}
    return {**common(["eia930_region_hourly", "eia930_ba_demand_hourly", "eia930_region_fuel_hourly", "eia930_region_pair_hourly"]),
            "event": e["event"], "title": e["title"], "start": e["start"], "end": e["end"],
            "baseline": e["baseline"], "baseline_offsets_days": offsets,
            "window": "from the first day's midnight, Eastern time, to the midnight after the last day, Pacific time",
            "hours": {"start": ip.utc_iso(hours[0]), "step_hours": 1, "n": len(hours)}, "regions": regions, "pairs": pairs}


# ------------------------------------------------------------------------------------------------ main

def main(argv=None):
    ap = argparse.ArgumentParser(description="The whole country's page files (chain 501 part B)")
    ap.add_argument("--only", nargs="*", choices=PARTS)
    ap.add_argument("--weather", action="store_true", help="also fit the regions' demand to their weather")
    ap.add_argument("--site-dir", help="a trial: the files under this folder")
    ap.add_argument("--regions", nargs="*", help="only these regions (a trial)")
    a = ap.parse_args(argv)
    parts = a.only or PARTS
    site = a.site_dir or SITE
    regions = a.regions or REGIONS
    ref, ref_file = reference()
    names = {}
    import openpyxl
    for r in list(openpyxl.load_workbook(ref_file, read_only=True)["Regions"].iter_rows(values_only=True))[1:]:
        if r and r[0]:
            names[r[0]] = r[1]
    print(f"{now()} reading the tables", flush=True)
    ba_dem = read("eia930_ba_demand_hourly", ["entity", "variable", "ts_utc", "value"], lambda d: d["variable"] == "demand_mw")
    need_supply = any(p in parts for p in ("index", "mix", "events"))
    reg = read("eia930_region_hourly", ["entity", "variable", "ts_utc", "value"],
               lambda d: d["variable"].isin(["net_generation_mw", "total_interchange_mw"])) if need_supply else None
    tz_of = {r: region_tz(r, ref, ba_dem) for r in REGIONS}
    demand_of, summed_of = {}, {}
    for r in REGIONS:
        demand_of[r], summed_of[r] = region_demand(r, ref, ba_dem)
    sizes = {}
    if "index" in parts:
        sup = read("eia930_ba_supply_hourly", ["entity", "variable", "ts_utc"], lambda d: d["variable"] == "net_generation_mw")
        span_d = ba_dem.groupby("entity")["ts"].agg(["min", "max"])
        span_s = sup.groupby("entity")["ts"].agg(["min", "max"])
        bas = []
        for c, r in sorted(ref.items()):
            if not r["us"] or r["region"] not in REGIONS:
                continue
            e = f"eia930:{c}"
            span = span_d.loc[e] if e in span_d.index else (span_s.loc[e] if e in span_s.index else None)
            files = []
            if e in span_d.index and not r["generation_only"]:
                files.append("demand")
            bas.append({"code": c, "name": r["name"], "region": r["region"], "tz": r["tz"], "grid": c if c in GRIDS else None,
                        "region_grids": sorted(g for g, rg in GRIDS.items() if rg == r["region"]),
                        "generation_only": r["generation_only"], "active": r["active"], "retired": r["retired"],
                        "first_hour": ip.utc_iso(span["min"]) if span is not None else None,
                        "last_hour": ip.utc_iso(span["max"]) if span is not None else None, "files": files})
        regs = []
        for r in REGIONS:
            d = demand_of[r].dropna()
            regs.append({"code": r, "name": names.get(r, r), "tz": tz_of[r],
                         "bas": sorted(c for c, x in ref.items() if x["region"] == r and x["us"]),
                         "grids": sorted(g for g, rg in GRIDS.items() if rg == r),
                         "first_hour": ip.utc_iso(d.index.min()) if len(d) else None, "last_hour": ip.utc_iso(d.index.max()) if len(d) else None,
                         "files": ["demand", "mix", "trade"]})
        sizes["index.json"] = write(site, "index.json", {**common(["eia930_ba_demand_hourly", "eia930_ba_supply_hourly"]),
                                                         "reference": os.path.relpath(ref_file, ROOT).replace(os.sep, "/"),
                                                         "regions": regs, "bas": bas})
    if "demand" in parts:
        weather = read("region_weather_hourly", ["entity", "variable", "ts_utc", "value"]) if a.weather else None
        gpath = os.path.join(ROOT, "site", "data", "demand_growth.json")
        grids_growth = json.load(open(gpath, encoding="utf-8"))["areas"] if os.path.exists(gpath) else {}
        for r in regions:
            prior_path = os.path.join(site, "demand", f"{r.lower()}.json")
            prior = json.load(open(prior_path, encoding="utf-8")) if os.path.exists(prior_path) else None
            wf = weather_frame(r, weather) if weather is not None else None
            doc = demand_doc(r, names.get(r, r), tz_of[r], "region", demand_of[r], "region_sum", summed_of[r], wf, prior, a.weather)
            if r in ALIKE:
                g = ALIKE[r]
                ga = grids_growth.get(g, {}).get("years", {})
                yrs = {}
                for y, row in doc["growth"]["years"].items():
                    a_, b_ = row.get("avg_demand_mw"), ga.get(y, {}).get("avg_demand_mw")
                    if a_ is not None and b_ is not None:
                        yrs[y] = {"region_avg_demand_mw": a_, "grid_avg_demand_mw": b_, "difference_pct": round(100 * (a_ - b_) / b_, 2)}
                doc["alike"] = {"grid": g, "grid_file": "site/data/demand_growth.json", "years": yrs,
                                "why": ("the region's figure sums the authorities EIA places in the region from EIA's six-month files; the "
                                        "grid's file reads that one authority's own workbook from EIA, so the figures differ where the region "
                                        "holds other authorities (PJM's region holds OVEC) or the two files hold an hour differently")}
            sizes[f"demand/{r.lower()}.json"] = write(site, f"demand/{r.lower()}.json", doc)
            print(f"{now()} demand {r}", flush=True)
        if not a.regions:
            for c, x in sorted(ref.items()):
                if not x["us"] or x["generation_only"] or x["region"] not in REGIONS:
                    continue
                s = series(ba_dem, f"eia930:{c}", "demand_mw")
                if not len(s):
                    continue
                doc = demand_doc(c, x["name"], x["tz"] or tz_of[x["region"]], "ba", s, "ba", None)
                doc["region"] = x["region"]
                sizes[f"demand/ba/{c.lower()}.json"] = write(site, f"demand/ba/{c.lower()}.json", doc)
            print(f"{now()} demand of the authorities", flush=True)
    fuel = None
    if "mix" in parts or "events" in parts:
        fuel = read("eia930_region_fuel_hourly", ["entity", "variable", "ts_utc", "value"])
    if "mix" in parts:
        for r in regions:
            ng = series(reg, f"eia930:{r}", "net_generation_mw")
            ti = series(reg, f"eia930:{r}", "total_interchange_mw")
            doc = mix_doc(r, names.get(r, r), tz_of[r], fuel, ng, ti, demand_of[r])
            if doc:
                sizes[f"mix/{r.lower()}.json"] = write(site, f"mix/{r.lower()}.json", doc)
            print(f"{now()} mix {r}", flush=True)
    pairs = None
    if "trade" in parts or "events" in parts:
        pairs = read("eia930_region_pair_hourly", ["entity", "ts_utc", "value", "x_first_report", "x_second_report"])
    if "trade" in parts:
        for r, doc in trade_docs(pairs, names).items():
            if r in regions:
                sizes[f"trade/{r.lower()}.json"] = write(site, f"trade/{r.lower()}.json", doc)
        print(f"{now()} trade", flush=True)
    if "events" in parts:
        rs = {}
        for r in regions:
            rs[r] = {"demand_mw": demand_of[r], "net_generation_mw": series(reg, f"eia930:{r}", "net_generation_mw"),
                     "net_imports_mw": -series(reg, f"eia930:{r}", "total_interchange_mw"),
                     "gen": {s: series(fuel, f"eia930:{r}", f"net_generation_{s}_mw") for s in SOURCES}}
        ps = {}
        for ent, g in pairs.groupby("entity"):
            ps[ent.split(":")[1]] = pd.Series(g["value"].to_numpy(dtype=float), index=pd.DatetimeIndex(g["ts"])).sort_index()
        for e in events_list():
            sizes[f"events/{e['event']}.json"] = write(site, f"events/{e['event']}.json", event_doc(e, rs, ps))
        print(f"{now()} events", flush=True)
    for k, v in sorted(sizes.items()):
        print(f"  {k}: {v:,} bytes")
    print(f"{len(sizes)} files under {os.path.relpath(site, ROOT)}, {sum(sizes.values()):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
