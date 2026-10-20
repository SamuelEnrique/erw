#!/usr/bin/env python3
"""The node: ERCOT's settlement points against the hub, by day and by month (session 358).

Energy Research Warehouse (ERW) derived tables (docs/methods/node_basis.md, whose shape section was written first):

    node_basis_daily          public. Per settlement point and ERCOT operating day: the point's day-ahead and real-time
                              mean, its daily four-hour spread, and its basis to the hub (HB_HUBAVG), one statistic a
                              row; x_hub, x_resource_type, x_class.
    node_basis_summary        public. Per hub, Central month, market and class of point: percentiles across points of
                              the point's mean daily basis and mean daily spread, the hub's own spread, the share of
                              points wider than the hub, the points and days counted.
    ercot_node_prices_hourly  internal. The hourly prices of the storage settlement points for the newest days that fit
                              under the owner's ceiling of 500,000 rows.

No request is made: the builder reads files this machine holds.

    day-ahead, resource nodes   the 60-Day DAM Disclosure zips (warehouse/raw/ercot_60d_dam, ERCOT NP3-966-ER, saved by
                                warehouse/connectors/ercot_dam_esr.py): the files 60d_DAM_Gen_Resource_Data and
                                60d_DAM_ESR_Data give each resource's Settlement Point Name and its Energy Settlement
                                Point Price by hour ending. Available 60 days after the operating day.
    day-ahead, every point      ERCOT's DAM Settlement Point Prices (warehouse/raw/ercot_dam_spp, NP4-190-CD, saved by
                                warehouse/connectors/ercot_rt_spp.py --pull-dam): the days the 31-day list held.
    day-ahead, hub and zones    ercot_all_hub_prices_history (HB_HUBAVG and the other hubs) and ercot_zone_prices_history
                                (the eight load zones), hourly.
    real time, every point      the 15-minute files of Settlement Point Prices at Resource Nodes, Hubs and Load Zones
                                (warehouse/raw/ercot_rtm_spp, NP6-905-CD, saved by ercot_rt_spp.py), which hold every
                                point; an hour is the mean of its four intervals, held only when all four are.

The points kept: every settlement point a resource of the disclosures is settled at, the hubs and the load zones. A
point's day is written in a market only when every hour of the operating day is held for the point and for the hub
(the autumn clock-change day, whose repeated hour the disclosure does not mark, is left out). Nothing is filled.

    python warehouse/derived/node_basis.py --from 2025-10-01            # the tables (data lock)
    python warehouse/derived/node_basis.py --from 2025-10-01 --out-dir DIR   # a trial, no data lock
    python warehouse/derived/node_basis.py --daily       # session 376: the data machine's dm_node_rt (data lock)

Session 376: ERCOT's real-time list keeps seven days, and the data machine's run saves every file of it each day
(ercot_rt_spp.py through dm_ercot_node_prices). --daily rebuilds the three tables when the saved files hold a whole
Central day of real time that node_basis_daily does not (a day is whole when the files of all its 15-minute intervals
are saved, read from their names), and is a skip otherwise; it prints the real-time days held before and after.
"""

import argparse
import collections
import csv
import datetime as dt
import glob
import io
import os
import re
import sys
import traceback
import zipfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
import iso_prices as ip  # noqa: E402
import ercot_rt_spp as rt  # noqa: E402

DAILY, SUMMARY, HOURLY = "node_basis_daily", "node_basis_summary", "ercot_node_prices_hourly"
SOURCE = "erw:node_basis"
SOURCE_HOURLY = "erw:node_basis_hourly"   # the internal table: its own entry in the registry, licensed internal
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/node_basis.md"
TZ = "America/Chicago"
HUB = "HB_HUBAVG"
HOURLY_CEILING = 500_000          # the owner's ceiling for the internal hourly table
NEAR = 0.9                        # a point counts in a month with at least this share of the hub's days
RAW_60D = os.path.join(ROOT, "warehouse", "raw", "ercot_60d_dam")
DAILY_COLS = ip.SERIES_COLS + ["x_hub", "x_resource_type", "x_class"]
SUMMARY_COLS = ip.SERIES_COLS + ["x_market", "x_class", "x_stat"]
HOURLY_COLS = ip.SERIES_COLS + ["x_class"]
# ERCOT's resource types, by the class the summary groups them in
CLASS = {"PWRSTR": "storage", "ESR": "storage", "PVGR": "solar", "WIND": "wind",
         "CCGT90": "gas", "CCLE90": "gas", "SCGT90": "gas", "SCLE90": "gas", "GSREH": "gas", "GSNONR": "gas", "GSSUP": "gas"}
CLASSES = ["all", "storage", "solar", "wind", "gas", "zone"]
PCTS = [10, 25, 50, 75, 90]


def hours_in(day):
    """The hours of an ERCOT operating day (Central): 23 or 25 on the clock-change days."""
    a = pd.Timestamp(day).tz_localize(TZ)
    b = (pd.Timestamp(day) + pd.Timedelta(days=1)).tz_localize(TZ)
    return int(round((b - a).total_seconds() / 3600))


def hour_start_utc(day, k):
    """The UTC start of the k-th hour (from 0) of a Central operating day."""
    return pd.Timestamp(day).tz_localize(TZ).tz_convert("UTC") + pd.Timedelta(hours=k)


# ---------------------------------------------------------------------------------------------------------------------
# the inputs: each gives {day: {point: {hour index: price}}} for its market, and the points' resource types
# ---------------------------------------------------------------------------------------------------------------------

def disclosure_zips():
    """The 60-Day DAM Disclosure zips on this machine, by operating day (the manifest's day; a day saved twice: the
    later posting), and their manifest line."""
    by_day = {}
    held = {os.path.basename(p): p for p in glob.glob(os.path.join(RAW_60D, "*", "*.zip"))}
    with open(os.path.join(RAW_60D, "zips", "manifest.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            p = held.get(r["file"])
            if p and (r["operating_day"] not in by_day or r["published"] > by_day[r["operating_day"]][1]["published"]):
                by_day[r["operating_day"]] = (p, r)
    return by_day


def read_disclosure(path, day):
    """One disclosure day: {point: {hour index: price}} from its resource files, the types at each point, and the
    hours the day has. A point whose hours are not the day's (the repeated hour of the autumn change) is left out."""
    z = zipfile.ZipFile(path)
    frames = []
    for n in z.namelist():
        base = os.path.basename(n)
        if base.startswith("60d_DAM_Gen_Resource_Data") or (base.startswith("60d_DAM_ESR_Data")):
            d = pd.read_csv(z.open(n), usecols=["Delivery Date", "Hour Ending", "Resource Type", "Settlement Point Name", "Energy Settlement Point Price"], dtype=str)
            frames.append(d)
    if not frames:
        raise ValueError("no resource file in the zip")
    d = pd.concat(frames, ignore_index=True).dropna(subset=["Settlement Point Name", "Energy Settlement Point Price"])
    dates = set(d["Delivery Date"])
    if len(dates) != 1 or dt.datetime.strptime(dates.pop(), "%m/%d/%Y").date().isoformat() != day:
        raise ValueError(f"the file's delivery date is not {day}")
    n_hours = hours_in(day)
    d["h"] = d["Hour Ending"].astype(int)
    d["p"] = d["Energy Settlement Point Price"].astype(float)
    types = d.groupby("Settlement Point Name")["Resource Type"].agg(lambda s: set(s)).to_dict()
    out = {}
    for sp, g in d.groupby("Settlement Point Name"):
        g = g.drop_duplicates(["h", "p"])
        if g["h"].duplicated().any() or g["h"].nunique() != n_hours:
            continue
        # hour ending h is the h-th hour of the day; on the spring day ERCOT skips hour ending 3 (02:00 to 03:00 does not
        # happen), so the hours are taken in their order
        out[sp] = dict(enumerate(g.sort_values("h")["p"].tolist()))
    return out, types


def dam_spp_files():
    by_day = {}
    path = rt.DAM_MANIFEST
    if not os.path.exists(path):
        return by_day
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            p = os.path.join(rt.DAM_ZIPS, r["file"])
            if os.path.exists(p) and (r["operating_day"] not in by_day or r["published"] > by_day[r["operating_day"]][1]["published"]):
                by_day[r["operating_day"]] = (p, r)
    return by_day


def read_dam_spp(path, day):
    """One day of DAM Settlement Point Prices: {point: {hour index: price}}; a repeated hour (DSTFlag Y) leaves the day
    out for every point."""
    z = zipfile.ZipFile(path)
    d = pd.read_csv(z.open(z.namelist()[0]), dtype=str)
    if (d["DSTFlag"].str.upper() != "N").any():
        raise ValueError("a repeated hour (DSTFlag Y)")
    if dt.datetime.strptime(d["DeliveryDate"].iloc[0], "%m/%d/%Y").date().isoformat() != day:
        raise ValueError(f"the file's delivery date is not {day}")
    d["h"] = d["HourEnding"].str.slice(0, 2).astype(int)
    d["p"] = d["SettlementPointPrice"].astype(float)
    n_hours = hours_in(day)
    out = {}
    for sp, g in d.groupby("SettlementPoint"):
        if g["h"].duplicated().any() or len(g) != n_hours:
            continue
        out[sp] = dict(enumerate(g.sort_values("h")["p"].tolist()))
    return out


def history_hourly(table, market, entities, first, last):
    """{day: {point: {hour index: price}}} from an hourly history table (the hubs' and zones' day-ahead)."""
    path = os.path.join(ip.OUT_DIR, table + ".csv")
    keep = []
    lo = (pd.Timestamp(first).tz_localize(TZ).tz_convert("UTC") - pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    hi = (pd.Timestamp(last) + pd.Timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    for ch in pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "ts_utc", "value", "market", "freq"], dtype=str, chunksize=500_000):
        ch = ch[(ch["market"] == market) & ch["entity"].isin(entities) & (ch["freq"] == "PT1H") & (ch["ts_utc"] >= lo) & (ch["ts_utc"] <= hi)]
        if len(ch):
            keep.append(ch)
    out = collections.defaultdict(dict)
    if not keep:
        return out
    d = pd.concat(keep, ignore_index=True).drop_duplicates(["entity", "ts_utc"])
    t = pd.to_datetime(d["ts_utc"], utc=True).dt.tz_convert(TZ)
    d["day"] = t.dt.strftime("%Y-%m-%d")
    d["start"] = pd.to_datetime(d["ts_utc"], utc=True)
    d["p"] = d["value"].astype(float)
    for (day, ent), g in d.groupby(["day", "entity"]):
        if day < first or day > last:
            continue
        base = pd.Timestamp(day).tz_localize(TZ).tz_convert("UTC")
        k = ((g["start"] - base).dt.total_seconds() // 3600).astype(int)
        out[day][ent.split(":", 1)[1]] = dict(zip(k, g["p"]))
    return out


def realtime(first, last, keep):
    """{day: {point: {hour index: price}}} from the saved 15-minute files: an hour held when all four of its intervals
    are; the points of `keep` (and every hub and load zone), with ERCOT's settlement point type of each."""
    acc = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
    types = {}
    for path in sorted(glob.glob(os.path.join(rt.ZIPS, "*.zip"))):
        with open(path, "rb") as f:
            content = f.read()
        try:
            df, utc = rt.read_interval(content)
        except ValueError:
            continue
        local = utc.tz_convert(TZ)
        day = local.strftime("%Y-%m-%d")
        if day < first or day > last:
            continue
        k = int((utc - pd.Timestamp(day).tz_localize(TZ).tz_convert("UTC")).total_seconds() // 3600)
        df = df[~df["SettlementPointType"].isin(rt.TWICE)]
        for sp, typ, price in zip(df["SettlementPointName"], df["SettlementPointType"], df["SettlementPointPrice"]):
            if sp in keep or typ in ("HU", "SH", "AH", "LZ"):
                acc[day][sp][k].append(float(price))
                types.setdefault(sp, typ)
    out = {}
    for day, pts in acc.items():
        out[day] = {sp: {k: sum(v) / 4 for k, v in hrs.items() if len(v) == 4} for sp, hrs in pts.items()}
    return out, types


# ---------------------------------------------------------------------------------------------------------------------
# the statistics
# ---------------------------------------------------------------------------------------------------------------------

def day_stats(hrs, n_hours):
    """(mean, four-hour spread, the prices in hour order) of a day held whole; None otherwise."""
    if len(hrs) != n_hours or set(hrs) != set(range(n_hours)):
        return None
    v = np.array([hrs[k] for k in range(n_hours)], dtype=float)
    s = np.sort(v)
    return float(v.mean()), float(s[-4:].mean() - s[:4].mean()), v


def class_of(types):
    cs = {CLASS.get(t, "other") for t in types}
    return cs.pop() if len(cs) == 1 else "mixed"


def build(first, last, log=print):
    """The three tables' rows, and the notes of the build."""
    notes = {}
    disc = {d: v for d, v in disclosure_zips().items() if first <= d <= last}
    spp = {d: v for d, v in dam_spp_files().items() if first <= d <= last}
    da, types, failed = {}, collections.defaultdict(set), []
    for day, (path, _) in sorted(disc.items()):
        try:
            pts, ty = read_disclosure(path, day)
        except Exception as e:
            failed.append(f"{day} (disclosure): {e}")
            continue
        da[day] = pts
        for sp, t in ty.items():
            types[sp] |= set(t)
    resource_points = set(types)
    for day, (path, _) in sorted(spp.items()):
        if day in da:
            continue
        try:
            pts = read_dam_spp(path, day)
        except Exception as e:
            failed.append(f"{day} (DAM Settlement Point Prices): {e}")
            continue
        da[day] = {sp: h for sp, h in pts.items() if sp in resource_points or sp.startswith(("HB_", "LZ_"))}
    notes["disclosure_days"] = len(disc)
    notes["spp_days"] = sum(1 for d in spp if d not in disc)
    hubs = ["ercot:HB_BUSAVG", "ercot:HB_HOUSTON", "ercot:HB_HUBAVG", "ercot:HB_NORTH", "ercot:HB_SOUTH", "ercot:HB_WEST"]
    zones = ["ercot:LZ_AEN", "ercot:LZ_CPS", "ercot:LZ_HOUSTON", "ercot:LZ_LCRA", "ercot:LZ_NORTH", "ercot:LZ_RAYBN", "ercot:LZ_SOUTH", "ercot:LZ_WEST"]
    hist = history_hourly("ercot_all_hub_prices_history", "ercot_dam", hubs, first, last)
    zhist = history_hourly("ercot_zone_prices_history", "ercot_dam", zones, first, last)
    for src in (hist, zhist):
        for day, pts in src.items():
            if day in da:
                for sp, h in pts.items():
                    da[day].setdefault(sp, h)  # the day's own file first (NP4-190 holds the hubs and zones too)
    rtm, rt_types = realtime(first, last, resource_points)
    notes["failed"] = failed

    def kind(sp):
        if sp.startswith("HB_"):
            return "hub", "HU"
        if sp.startswith("LZ_"):
            return "zone", "LZ"
        if sp in types:
            return class_of(types[sp]), "+".join(sorted(types[sp]))
        return "unknown", rt_types.get(sp, "")

    daily, hourly_keep, retrieved = [], [], ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    for market, src in (("dam", da), ("rtm", rtm)):
        days_held = 0
        for day in sorted(src):
            n_hours = hours_in(day)
            hub = day_stats(src[day].get(HUB, {}), n_hours)
            if hub is None:
                continue
            days_held += 1
            for sp, hrs in src[day].items():
                st = day_stats(hrs, n_hours)
                if st is None:
                    continue
                cls, typ = kind(sp)
                daily.append((sp, day, market, st[0], st[1], st[0] - hub[0], cls, typ))
                if cls == "storage":
                    hourly_keep.append((sp, day, market, st[2]))
        notes[f"{market}_days"] = days_held
    d = pd.DataFrame(daily, columns=["sp", "day", "market", "mean", "spread", "basis", "cls", "typ"])
    return d, hourly_keep, notes, retrieved


def daily_rows(d, retrieved):
    rows = []
    for stat in ("mean", "spread", "basis"):
        name = {"mean": "mean", "spread": "spread_4h", "basis": "basis"}[stat]
        t = pd.DataFrame({
            "entity": "ercot:" + d["sp"], "variable": d["market"] + "_" + name, "ts_utc": d["day"] + "T00:00:00Z", "value": d[stat].round(4),
            "unit": "USD/MWh", "freq": "P1D", "geo": "US-TX", "market": "ercot_" + d["market"], "node": d["sp"], "source": SOURCE,
            "source_url": METHOD_URL, "retrieved_at": retrieved, "vintage": "", "x_hub": HUB, "x_resource_type": d["typ"], "x_class": d["cls"]})
        rows.append(t)
    return pd.concat(rows, ignore_index=True)[DAILY_COLS]


def summary_rows(d, retrieved):
    out = []
    d = d.assign(month=d["day"].str.slice(0, 7))
    hubd = d[d["sp"] == HUB].set_index(["market", "day"])["spread"]
    for (market, month), g in d.groupby(["market", "month"]):
        hub_days = g[g["sp"] == HUB]["day"].nunique()
        if not hub_days:
            continue
        per = g[g["sp"] != HUB].groupby("sp").agg(days=("day", "nunique"), basis=("basis", "mean"), spread=("spread", "mean"), cls=("cls", "first"))
        # the hub's spread over each point's own days, for the share wider than the hub
        hub_on = g[g["sp"] != HUB].assign(hs=lambda x: [hubd.get((market, dd), np.nan) for dd in x["day"]]).groupby("sp")["hs"].mean()
        per["hub_spread"] = hub_on
        per = per[per["days"] >= NEAR * hub_days]
        hub_spread = float(g[g["sp"] == HUB]["spread"].mean())
        for cls in CLASSES:
            if cls == "all":
                s = per[~per["cls"].isin(["hub", "zone"])]
            else:
                s = per[per["cls"] == cls]
            if s.empty:
                continue
            stats = {}
            for p in PCTS:
                stats[f"basis_p{p}"] = (float(np.percentile(s["basis"], p)), "USD/MWh")
                stats[f"spread_4h_p{p}"] = (float(np.percentile(s["spread"], p)), "USD/MWh")
            stats["hub_spread_4h"] = (hub_spread, "USD/MWh")
            stats["share_wider_pct"] = (100.0 * float((s["spread"] > s["hub_spread"]).mean()), "pct")
            stats["points"] = (float(len(s)), "count")
            stats["days"] = (float(hub_days), "count")
            for stat, (v, unit) in stats.items():
                out.append(dict(entity=f"ercot:{HUB}", variable=f"{market}_{cls}_{stat}", ts_utc=f"{month}-01T00:00:00Z", value=round(v, 4), unit=unit,
                                freq="P1M", geo="US-TX", market=f"ercot_{market}", node=HUB, source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved,
                                vintage="", x_market=market, x_class=cls, x_stat=stat))
    return pd.DataFrame(out, columns=SUMMARY_COLS)


def hourly_rows(keep, retrieved):
    """The storage points' hourly prices, both markets, for the newest days whose rows fit under the ceiling."""
    by_day = collections.defaultdict(list)
    for sp, day, market, v in keep:
        by_day[day].append((sp, market, v))
    days, n = [], 0
    for day in sorted(by_day, reverse=True):
        k = sum(len(v) for _, _, v in by_day[day])
        if n + k > HOURLY_CEILING:
            break
        days.append(day)
        n += k
    rows = []
    for day in sorted(days):
        starts = [hour_start_utc(day, k).strftime("%Y-%m-%dT%H:%M:%SZ") for k in range(hours_in(day))]
        for sp, market, v in by_day[day]:
            for k, x in enumerate(v):
                rows.append((f"ercot:{sp}", f"spp_{market}", starts[k], round(float(x), 4), "USD/MWh", "PT1H", "US-TX", f"ercot_{market}", sp, SOURCE_HOURLY, METHOD_URL,
                             retrieved, "", "storage"))
    return pd.DataFrame(rows, columns=HOURLY_COLS), (min(days) if days else None, max(days) if days else None)


def write(name, df, header, log, out_dir):
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, name + ".csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            for line in header:
                f.write("# " + line + "\n")
            df.to_csv(f, index=False, lineterminator="\n")
        return path
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    if os.path.exists(path):
        os.remove(path)  # rebuilt whole from the saved files each run
    return ip.write_csv(df, name, header, log, cols=list(df.columns))


# ---------------------------------------------------------------------------------------------------------------------
# session 376: the daily step (dm_node_rt), so that the real-time days ERCOT's seven-day list still holds reach the tables
# ---------------------------------------------------------------------------------------------------------------------

STAMP = re.compile(r"_(\d{8})_(\d{4})_csv\.zip$")


def rt_days_saved(zips=None):
    """The Central operating days whose every 15-minute interval the saved real-time files hold, by the files' names
    (a stamp is the END of its interval, so 00:00 closes the day before). A file ERCOT posted twice counts once."""
    stamps = collections.defaultdict(set)
    for path in glob.glob(os.path.join(zips or rt.ZIPS, "*.zip")):
        m = STAMP.search(os.path.basename(path))
        if not m:
            continue
        end = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M")
        start = end - dt.timedelta(minutes=15)
        stamps[start.strftime("%Y-%m-%d")].add(end)
    return sorted(d for d, s in stamps.items() if len(s) >= 4 * hours_in(d))


def rt_days_held(path=None):
    """The operating days node_basis_daily holds in real time (its rtm_mean rows for the hub), or [] without the table."""
    path = path or os.path.join(ip.OUT_DIR, DAILY + ".csv")
    if not os.path.exists(path):
        return []
    days = set()
    for ch in pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["entity", "variable", "ts_utc"], dtype=str, chunksize=500_000):
        ch = ch[(ch["variable"] == "rtm_mean") & (ch["entity"] == f"ercot:{HUB}")]
        days |= set(ch["ts_utc"].str.slice(0, 10))
    return sorted(days)


def gained(saved, held):
    """The whole real-time days saved that the table does not hold."""
    return sorted(set(saved) - set(held))


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: ERCOT's settlement points against the hub, by day and by month (session 358)")
    ap.add_argument("--from", dest="first", default="2025-10-01", help="the first operating day, YYYY-MM-DD")
    ap.add_argument("--to", dest="last", default=dt.date.today().isoformat(), help="the last operating day, YYYY-MM-DD")
    ap.add_argument("--out-dir", help="write here instead of warehouse/output (a trial: no data lock)")
    ap.add_argument("--daily", action="store_true", help="session 376: rebuild only when the saved real-time files hold a whole "
                    "day the table does not; otherwise a skip (exit ERW_SKIP_EXIT)")
    a = ap.parse_args(argv)
    if a.daily:
        saved, held = rt_days_saved(), rt_days_held(os.path.join(a.out_dir, DAILY + ".csv") if a.out_dir else None)
        new = gained(saved, held)
        say = (f"real time held before: {held[0] if held else '-'} to {held[-1] if held else '-'}, {len(held)} days; "
               f"whole days in the saved files: {saved[0] if saved else '-'} to {saved[-1] if saved else '-'}, {len(saved)}")
        print(say)
        if not new:
            print(f"{DAILY} SKIPPED: no whole real-time day saved that the table does not hold ({say})")
            return int(os.environ.get("ERW_SKIP_EXIT", "75"))
        print(f"days gained: {', '.join(new)}")
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{DAILY}_{run_id}.log"))
    results = []
    try:
        d, keep, notes, retrieved = build(a.first, a.last, log=log)
        if d.empty:
            raise RuntimeError("no point's day could be written")
        dd, sm = daily_rows(d, retrieved), summary_rows(d, retrieved)
        hr, (h0, h1) = hourly_rows(keep, retrieved)
        span = lambda m: (d[d.market == m]["day"].min(), d[d.market == m]["day"].max(), d[d.market == m]["sp"].nunique())
        (da0, da1, dan), (rt0, rt1, rtn) = span("dam"), span("rtm")
        failed = "; ".join(notes["failed"]) or "none"
        common = [
            f"Inputs (no request by this builder): the 60-Day DAM Disclosure's resource files for {notes['disclosure_days']} operating days (ERCOT NP3-966-ER, "
            f"warehouse/raw/ercot_60d_dam); DAM Settlement Point Prices for {notes['spp_days']} days (NP4-190-CD, warehouse/raw/ercot_dam_spp); "
            "ercot_all_hub_prices_history and ercot_zone_prices_history (the hubs' and zones' day-ahead); the 15-minute real-time files (NP6-905-CD, warehouse/raw/ercot_rtm_spp).",
            f"Held: day-ahead {da0} to {da1}, {notes['dam_days']} days with the hub whole, {dan} points; real time {rt0} to {rt1}, {notes['rtm_days']} days, {rtn} points. "
            "ERCOT's real-time list keeps seven days and the disclosure comes 60 days after the operating day: twelve months of real time at the nodes cannot be had "
            "from ERCOT's public lists, and the day-ahead days between the newest disclosure and the oldest day of the 31-day list are not held.",
            f"Days or files not read: {failed}.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/node_basis.py",
            f"Run log: warehouse/output/logs/{DAILY}_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, the node basis (docs/methods/node_basis.md), {METHOD_URL}",
            "Derived from: ercot_all_hub_prices_history; ercot_zone_prices_history",
            "  and ERCOT's saved files of NP3-966-ER, NP4-190-CD and NP6-905-CD, read directly (no table of their every point is kept)",
            "License: public. ERCOT's terms of use (https://www.ercot.com/help/terms): raw data in public portions of the website may be used, reproduced and redistributed "
            "in compilations, charts and analyses.",
        ]
        h_daily = ["Energy Research Warehouse (ERW): ERCOT's settlement points against the hub average, by operating day (derived, session 358)",
                   "Shape: series (docs/datastandard.md v0). entity ercot:<settlement point>; ts_utc the Central operating day at 00:00:00Z, freq P1D; variables dam_mean, "
                   "rtm_mean (the day's mean hourly price), dam_spread_4h, rtm_spread_4h (the four dearest hours' mean less the four cheapest), dam_basis, rtm_basis (the "
                   "point's mean less HB_HUBAVG's), USD/MWh; market ercot_dam or ercot_rtm. x_hub HB_HUBAVG for every point (the ERW holds no list of each node's zone and "
                   "zonal hub); x_resource_type ERCOT's resource types at the point (HU a hub, LZ a load zone); x_class storage, solar, wind, gas, other, mixed, hub, zone, "
                   "unknown (a point no disclosure names). A day is written only whole, for the point and the hub."] + common
        h_sum = ["Energy Research Warehouse (ERW): ERCOT's settlement points against the hub average, the distribution by month (derived, session 358)",
                 "Shape: series. entity ercot:HB_HUBAVG; variable <market>_<class>_<stat>; ts_utc the first day of the Central month, freq P1M. Per point, the month's "
                 "mean daily basis and mean daily four-hour spread; then across the points of a class (all: every resource node; storage, solar, wind, gas; zone: the "
                 "load zones) with at least 90 percent of the hub's days: percentiles 10, 25, 50, 75, 90 (linear, numpy's default), the hub's own mean spread, the share "
                 "of points whose mean spread is wider than the hub's over the same days (pct), the points and the hub's days (count)."] + common
        h_hr = ["Energy Research Warehouse (ERW): ERCOT's storage settlement points, hourly day-ahead and real-time prices (derived, session 358; internal)",
                f"Shape: series. entity ercot:<settlement point>; variable spp_dam or spp_rtm, USD/MWh; ts_utc the hour's start, freq PT1H. The storage points' hours of "
                f"the newest days that fit under the owner's ceiling of {HOURLY_CEILING:,} rows: {h0} to {h1}. The rest are in the saved files and in node_basis_daily."] + [
                line.replace(f"Source: {SOURCE} ", f"Source: {SOURCE_HOURLY} ") for line in common[:-3]] + [
                "Read from: ERCOT's saved files of NP3-966-ER, NP4-190-CD and NP6-905-CD, as node_basis_daily; a real-time hour is the mean of ERCOT's four "
                "15-minute prices. No ERW table is read, so the table is not marked derived; its tier is derived by rule (build_coverage.py, TIER_RULES).",
                "License: internal (the owner's rule for the hourly table: kept in the warehouse, not in the live set)."]
        write(DAILY, dd, h_daily, log, a.out_dir)
        write(SUMMARY, sm, h_sum, log, a.out_dir)
        write(HOURLY, hr, h_hr, log, a.out_dir)
        if not a.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="ERCOT's settlement points against the hub, by day and by month (warehouse/derived/node_basis.py)",
                                    report_url=METHOD_URL, document_list="", license="public", tables=[DAILY, SUMMARY]),
                               dict(source=SOURCE_HOURLY, publisher="Energy Research Warehouse (ERW), derived",
                                    report="ERCOT's storage settlement points, hourly prices behind node_basis_daily (warehouse/derived/node_basis.py)",
                                    report_url=METHOD_URL, document_list="", license="internal", tables=[HOURLY])])
        msg = (f"{DAILY} {len(dd):,} rows ({d['sp'].nunique()} points; day-ahead {da0} to {da1}, real time {rt0} to {rt1}); {SUMMARY} {len(sm):,} rows; "
               f"{HOURLY} {len(hr):,} rows ({h0} to {h1}); {len(notes['failed'])} days not read")
        log(msg)
        print(msg)
        if a.daily:
            print(f"real time held after: {rt0} to {rt1}, {d[d.market == 'rtm']['day'].nunique()} days; {HOURLY} {h0} to {h1}"
                  + (f" (the ceiling of {HOURLY_CEILING:,} rows keeps the newest days)" if len(hr) > 0.95 * HOURLY_CEILING else ""))
        results.append(dict(table=DAILY, market="derived", status="ok", detail=msg[:300]))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{DAILY} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=DAILY, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not a.out_dir:
        ip.write_status(DAILY, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
