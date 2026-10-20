#!/usr/bin/env python3
"""ERCOT's real-time Settlement Point Prices at the storage resources' nodes, by 15-minute interval (session 120).

    python warehouse/connectors/ercot_rt_spp.py --pull          # ERCOT's list, then each listed interval not yet held
    python warehouse/connectors/ercot_rt_spp.py --pull --offline   # the saved files only; no request
    python warehouse/connectors/ercot_rt_spp.py --write         # the table, from the saved files (data lock)

Energy Research Warehouse (ERW). Table: ercot_rtm_node_prices, a series table, one row per settlement point and
15-minute interval (method docs/methods/ercot_storage_realtime.md).

The source. "Settlement Point Prices at Resource Nodes, Hubs and Load Zones" (EMIL NP6-905-CD, report type 12301): a
small zip for each 15-minute Settlement Interval, with the Real-Time Settlement Point Price of every settlement point
(1,142 of them on 5 October 2026: 831 Resource Nodes, 228 combined-cycle nodes, 52 private-use networks, hubs and
Load Zones).

**ERCOT's public list keeps seven days of it.** Measured on 5 October 2026: 689 files, stamped 28 September 00:00 to 5
October 04:00 Central (a file's stamp is the END of its interval: the first holds 27 September 23:45 to 24:00, and the
interval is read from the file's own columns, never from its name). The storage disclosure runs 60 days behind, so the two do not meet: on the day a storage resource's
real-time output is disclosed, the price at its node for that day left the public list 53 days before. Prices at the
nodes for the disclosed days (February to August 2026) therefore cannot be had from this list at any ceiling. What
can be had is what is listed today, which this connector pulls and keeps, so that:

- the difference between a storage node's real-time price and the hub's is measured, on a real week, not assumed;
- the method that values real-time energy at the node is built and tested on real prices;
- if the pull is repeated before the list forgets a day (approved or not is a person's decision: this session pulled
  once), the days it holds will be met by the storage disclosure 60 days later.

An approved pull (session 120), USD 0, under the same ceilings as the storage disclosure pulled beside it (12 GB of
downloads and 9,000,000 stored rows in all). One file at a time, a pause between requests; a file is saved once, under
warehouse/raw/ercot_rtm_spp/zips/, and never asked for twice. The table keeps the settlement points a storage resource
is settled at (the Settlement Point Names of ercot_dam_esr_awards), the hubs and the Load Zones; the saved files hold
every point. ERCOT prints a Load Zone twice in one interval, as type LZ and as type LZEW (and a DC tie as LZ_DC and
LZ_DCEW), and the two prices can differ (in 4 of 12 such pairs in the first file read): the table keeps the LZ and
LZ_DC rows and leaves the EW rows in the saved files, since one name cannot hold two prices of one interval. A value is
written as ERCOT prints it. An interval ERCOT flags as a repeated hour (DSTFlag Y) is not
written: the day of the autumn clock change is left out, not guessed at.

Session 204 (the owner's ruling of 12 October 2026): the pull is a standing one, a soft step of the data machine's
daily run (warehouse/run_data_machine.sh, through warehouse/scheduled.py ercot_rtm_node_prices), so that no listed day
is lost: ERCOT's list forgets an interval after seven days and it cannot be had later.

    python warehouse/connectors/ercot_rt_spp.py --daily         # the list, each listed interval not yet held, then the table (data lock)

The row ceiling: 500,000 rows a UTC day (MAX_ROWS_DAY; --max-rows names another). A row counts once, on the day its
file is saved: the rows of that file the table keeps (the storage resources' points, the hubs and the Load Zones).
The count of every run is kept in warehouse/raw/ercot_rtm_spp/rows_by_run.csv, and the day's runs are added up. Before
each request the run asks whether one more file could pass the ceiling (the most rows a file can keep: the storage
points of ercot_dam_esr_awards and 64 more, or the most this run has met); if it could, the request is not made, the
run says STOPPED, and the files saved so far are written. A file not asked for today is asked for tomorrow while
ERCOT still lists it. The table is internal to the warehouse: no page reads it and it is not in the live set
(warehouse/supabase).

Session 358 (the chain of 20 October 2026): the day-ahead prices at the same points, for node_basis_daily
(docs/methods/node_basis.md). ERCOT's "DAM Settlement Point Prices" (EMIL NP4-190-CD, report type 12331), one small
zip a day with the day-ahead price of every settlement point and hour, kept on the public list for 31 days (measured
on 20 October 2026: 31 days, posted 19 September to 19 October). The stage saves each listed day not yet held, once,
under warehouse/raw/ercot_dam_spp/zips/ with a manifest, at the same pace; it writes no table (the derived builder
reads the saved files). Day-ahead prices at the resource nodes for the days before the list come from the 60-Day DAM
Disclosure's resource files (warehouse/connectors/ercot_dam_esr.py), which give each resource's settlement point and
its Energy Settlement Point Price.

    python warehouse/connectors/ercot_rt_spp.py --pull-dam      # ERCOT's DAM list, then each listed day not yet held
"""
import argparse
import csv
import datetime as dt
import glob
import hashlib
import io
import json
import os
import re
import sys
import time
import zipfile

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

TABLE = "ercot_rtm_node_prices"
REPORT_TYPE = 12301
SOURCE = "ercot:NP6-905-CD"
PAGE = "https://www.ercot.com/mp/data-products/data-product-details?id=NP6-905-CD"
LIST = f"https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId={REPORT_TYPE}"
FILE = "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={doc}"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
PAUSE = 1.5
TZ = "America/Chicago"
RAW = os.path.join(ROOT, "warehouse", "raw", "ercot_rtm_spp")
ZIPS = os.path.join(RAW, "zips")
MANIFEST = os.path.join(ZIPS, "manifest.csv")
MANIFEST_COLS = ["interval", "file", "doc_id", "url", "bytes", "sha256", "published", "retrieved_at", "how"]
MAX_FILE = 200_000          # a listed file larger than this is not what this report posts (they are about 9 kB): not requested
MAX_BYTES = 200_000_000     # this connector's share of the session's download ceiling
MAX_ROWS_DAY = 500_000      # session 204: the rows a UTC day's runs may add to the table, counted as each file is saved
ROW_MARGIN = 64             # the hubs, Load Zones and DC ties a file can hold beside the storage points (20 on 5 October 2026)
ROWS_LOG = os.path.join(RAW, "rows_by_run.csv")
ROWS_COLS = ["run_id", "day_utc", "files_saved", "rows_counted", "ceiling", "stopped"]
KEEP_TYPES = {"HU", "SH", "AH", "LZ", "LZ_DC"}   # hubs and Load Zones: kept whatever resource sits there
TWICE = {"LZEW", "LZ_DCEW"}                     # a zone's second row in the file, under the same name: left in the saved file
ESR_TABLE = "ercot_dam_esr_awards"
NAME = re.compile(r"SPPHLZNP6905_(\d{8})_(\d{4})_csv$")
COLS = ip.SERIES_COLS + ["x_point_type"]
# session 358: the day-ahead prices of every settlement point (NP4-190-CD), saved for node_basis_daily
DAM_REPORT_TYPE = 12331
DAM_SOURCE = "ercot:NP4-190-CD"
DAM_LIST = f"https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId={DAM_REPORT_TYPE}"
DAM_RAW = os.path.join(ROOT, "warehouse", "raw", "ercot_dam_spp")
DAM_ZIPS = os.path.join(DAM_RAW, "zips")
DAM_MANIFEST = os.path.join(DAM_ZIPS, "manifest.csv")
DAM_MANIFEST_COLS = ["operating_day", "file", "doc_id", "url", "bytes", "sha256", "published", "retrieved_at", "how"]
DAM_NAME = re.compile(r"DAMSPNP4190_csv$")
DAM_MAX_FILE = 2_000_000    # a day's zip is about 180 kB; a larger one is not what this report posts
DAM_MAX_FILES = 40          # the most a run asks for (the list holds 31 days)


def manifest():
    if not os.path.exists(MANIFEST):
        return []
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def manifest_add(row):
    os.makedirs(ZIPS, exist_ok=True)
    new = not os.path.exists(MANIFEST)
    with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_COLS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(row)


def rows_today(day, path=None):
    """The rows the runs of one UTC day have counted against the ceiling so far (rows_by_run.csv)."""
    path = path or ROWS_LOG
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8", newline="") as f:
        return sum(int(r["rows_counted"]) for r in csv.DictReader(f) if r["day_utc"] == day)


def rows_add(row, path=None):
    path = path or ROWS_LOG
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ROWS_COLS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(row)


def kept_rows(content, points):
    """The rows of one interval's file the table keeps; 0 for a file the table will not read."""
    try:
        df, _ = read_interval(content)
    except (ValueError, zipfile.BadZipFile):
        return 0
    return int(((df["SettlementPointName"].isin(points) | df["SettlementPointType"].isin(KEEP_TYPES)) & ~df["SettlementPointType"].isin(TWICE)).sum())


def pull(a, log, get=requests.get, run_id=None, result=None):
    """ERCOT's list, then each listed interval not yet held. With a.max_rows (session 204) the rows the table keeps of
    each saved file are counted against that ceiling for the UTC day, and the request that could pass it is not made.
    result, when given, receives files (saved by this run), rows (counted) and stopped."""
    saved = os.path.join(RAW, "doclist_latest.json")
    os.makedirs(ZIPS, exist_ok=True)
    result = {} if result is None else result
    result.update(files=0, rows=0, stopped=False)
    if a.offline:
        log("offline: no request")
        return 0
    if ip.paused("ercot"):
        raise RuntimeError("ERCOT is paused (warehouse/metadata/paused_sources.csv): nothing is requested")
    ceiling = getattr(a, "max_rows", None)
    day = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    points, counted, most = set(), 0, 0
    if ceiling:
        points = esr_points()
        counted = rows_today(day)
        most = len(points) + ROW_MARGIN
        if counted + most > ceiling:
            log(f"STOPPED before any request: {counted:,} rows are counted against the ceiling of {ceiling:,} for {day} (UTC) and one more file could keep {most}")
            result["stopped"] = True
            return 3
    r = None
    for attempt in range(4):
        try:
            r = get(LIST, headers=UA, timeout=120)
            r.raise_for_status()
            break
        except requests.RequestException as e:
            log(f"  the list: attempt {attempt + 1} failed ({type(e).__name__})")
            time.sleep(15)
    else:
        raise IOError("the list could not be read")
    with open(saved, "w", encoding="utf-8") as f:
        f.write(r.text)
    docs = [d["Document"] for d in r.json()["ListDocsByRptTypeRes"]["DocumentList"]]
    want = sorted((d for d in docs if NAME.search(d["FriendlyName"])), key=lambda d: d["FriendlyName"])
    held = {os.path.basename(p) for p in glob.glob(os.path.join(ZIPS, "*.zip"))}
    todo = [d for d in want if d["ConstructedName"] not in held]
    done = sum(int(m["bytes"]) for m in manifest() if m["how"] == "requested")
    log(f"ERCOT lists {len(want)} intervals, {want[0]['FriendlyName'][13:26]} to {want[-1]['FriendlyName'][13:26]}; {len(todo)} not yet on this machine, "
        f"{sum(int(d['ContentSize']) for d in todo):,} bytes; downloaded so far {done:,}")
    n = failed = rows = 0
    rc = 0

    def close():
        if ceiling:
            rows_add({"run_id": run_id or "", "day_utc": day, "files_saved": n, "rows_counted": rows, "ceiling": ceiling, "stopped": int(result["stopped"])})
            log(f"rows counted against the ceiling: {counted + rows:,} of {ceiling:,} for {day} (UTC); this run {rows:,} in {n} files")
        result.update(files=n, rows=rows)

    for d in todo:
        size = int(d["ContentSize"])
        if size > MAX_FILE:
            log(f"  {d['FriendlyName']}: listed at {size:,} bytes, not requested")
            continue
        if done + size > MAX_BYTES:
            log(f"STOPPED at this connector's ceiling of {MAX_BYTES:,} bytes")
            result["stopped"] = True
            close()
            return 3
        if ceiling and counted + rows + most > ceiling:
            log(f"STOPPED before {d['FriendlyName']}: {counted + rows:,} rows are counted against the ceiling of {ceiling:,} for {day} (UTC) "
                f"and one more file could keep {most}; {len(todo) - n - failed} listed files are left for a later day")
            result["stopped"] = True
            rc = 3
            break
        url = FILE.format(doc=d["DocID"])
        time.sleep(PAUSE)
        g = None
        for attempt in range(3):
            try:
                g = get(url, headers=UA, timeout=120)
                if g.status_code == 200 and len(g.content) == size:
                    break
            except requests.RequestException:
                pass
            g = None
            time.sleep(10 * (attempt + 1))
        if g is None:
            failed += 1
            log(f"  {d['FriendlyName']}: three attempts failed; left for a later run")
            continue
        path = os.path.join(ZIPS, d["ConstructedName"])
        with open(path + ".tmp", "wb") as f:
            f.write(g.content)
        os.replace(path + ".tmp", path)
        m = NAME.search(d["FriendlyName"])
        manifest_add({"interval": f"{m.group(1)}_{m.group(2)}", "file": d["ConstructedName"], "doc_id": d["DocID"], "url": url, "bytes": len(g.content),
                      "sha256": hashlib.sha256(g.content).hexdigest(), "published": d["PublishDate"],
                      "retrieved_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "how": "requested"})
        done += len(g.content)
        n += 1
        if ceiling:
            k = kept_rows(g.content, points)
            rows += k
            most = max(most, k)
        if n % 100 == 0:
            log(f"  {n} of {len(todo)} saved; {done:,} bytes downloaded")
    log(f"{n} files saved by this run, {failed} failed; {len(glob.glob(os.path.join(ZIPS, '*.zip')))} on this machine; {done:,} bytes downloaded in all")
    close()
    return rc


def dam_manifest():
    if not os.path.exists(DAM_MANIFEST):
        return []
    with open(DAM_MANIFEST, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def pull_dam(a, log, get=requests.get):
    """Session 358: ERCOT's list of DAM Settlement Point Prices, then each listed day's csv zip not yet held, saved
    once with a line in the manifest. Writes no table. Returns the files saved."""
    if ip.paused("ercot"):
        raise RuntimeError("ERCOT is paused (warehouse/metadata/paused_sources.csv): nothing is requested")
    os.makedirs(DAM_ZIPS, exist_ok=True)
    r = get(DAM_LIST, headers=UA, timeout=120)
    r.raise_for_status()
    with open(os.path.join(DAM_RAW, "doclist_latest.json"), "w", encoding="utf-8") as f:
        f.write(r.text)
    docs = [d["Document"] for d in r.json()["ListDocsByRptTypeRes"]["DocumentList"]]
    want = sorted((d for d in docs if DAM_NAME.search(d["FriendlyName"])), key=lambda d: d["PublishDate"])
    held = {m["file"] for m in dam_manifest()} | {os.path.basename(p) for p in glob.glob(os.path.join(DAM_ZIPS, "*.zip"))}
    todo = [d for d in want if d["ConstructedName"] not in held][:DAM_MAX_FILES]
    log(f"{DAM_LIST}: {len(want)} days listed, posted {want[0]['PublishDate'][:10]} to {want[-1]['PublishDate'][:10]}; {len(todo)} not yet on this machine")
    n = 0
    for d in todo:
        size = int(d["ContentSize"])
        if size > DAM_MAX_FILE:
            log(f"  {d['ConstructedName']}: listed at {size:,} bytes, not requested")
            continue
        url = FILE.format(doc=d["DocID"])
        time.sleep(PAUSE)
        g = None
        for attempt in range(3):
            try:
                g = get(url, headers=UA, timeout=120)
                if g.status_code == 200 and len(g.content) == size:
                    break
            except requests.RequestException:
                pass
            g = None
            time.sleep(10 * (attempt + 1))
        if g is None:
            log(f"  {d['ConstructedName']}: three attempts failed; left for a later run")
            continue
        z = zipfile.ZipFile(io.BytesIO(g.content))
        day = pd.read_csv(z.open(z.namelist()[0]), usecols=["DeliveryDate"], dtype=str, nrows=1)["DeliveryDate"].iloc[0]
        path = os.path.join(DAM_ZIPS, d["ConstructedName"])
        with open(path + ".tmp", "wb") as f:
            f.write(g.content)
        os.replace(path + ".tmp", path)
        new = not os.path.exists(DAM_MANIFEST)
        with open(DAM_MANIFEST, "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=DAM_MANIFEST_COLS, lineterminator="\n")
            if new:
                w.writeheader()
            w.writerow({"operating_day": dt.datetime.strptime(day, "%m/%d/%Y").date().isoformat(), "file": d["ConstructedName"], "doc_id": d["DocID"], "url": url,
                        "bytes": len(g.content), "sha256": hashlib.sha256(g.content).hexdigest(), "published": d["PublishDate"],
                        "retrieved_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "how": "requested"})
        n += 1
    log(f"DAM Settlement Point Prices: {n} files saved by this run; {len(glob.glob(os.path.join(DAM_ZIPS, '*.zip')))} on this machine")
    return n


def read_interval(content):
    """One interval's file: its rows as strings, with the interval's start in UTC. Raises ValueError on a file that is
    not one interval, has a repeated-hour flag, or a time the clock change makes absent."""
    z = zipfile.ZipFile(io.BytesIO(content))
    if len(z.namelist()) != 1:
        raise ValueError(f"{len(z.namelist())} files in the zip")
    df = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])), dtype=str, keep_default_na=False, na_values=[])
    need = ["DeliveryDate", "DeliveryHour", "DeliveryInterval", "SettlementPointName", "SettlementPointType", "SettlementPointPrice", "DSTFlag"]
    if [c for c in need if c not in df.columns]:
        raise ValueError(f"columns {list(df.columns)}")
    keys = set(zip(df["DeliveryDate"], df["DeliveryHour"], df["DeliveryInterval"], df["DSTFlag"]))
    if len(keys) != 1:
        raise ValueError(f"{len(keys)} intervals in one file")
    date, hour, interval, dst = keys.pop()
    if dst.upper() != "N":
        raise ValueError("a repeated hour (DSTFlag Y): not written")
    h, q = int(hour), int(interval)
    if not (1 <= h <= 24 and 1 <= q <= 4):
        raise ValueError(f"hour {hour}, interval {interval}")
    local = pd.Timestamp(dt.datetime.strptime(date, "%m/%d/%Y")) + pd.Timedelta(hours=h - 1, minutes=15 * (q - 1))
    try:
        utc = local.tz_localize(TZ, ambiguous="raise", nonexistent="raise").tz_convert("UTC")
    except Exception as e:
        raise ValueError(f"a time the clock change makes ambiguous or absent: {e}")
    if pd.to_numeric(df["SettlementPointPrice"], errors="coerce").isna().any():
        raise ValueError("a price that is not a number")
    if df.duplicated(["SettlementPointName", "SettlementPointType"]).any():
        raise ValueError("a settlement point and type twice in one interval")
    one = df[~df["SettlementPointType"].isin(TWICE)]
    if one.duplicated(["SettlementPointName"]).any():
        raise ValueError("a settlement point twice in one interval, beyond a zone's LZ and LZEW rows")
    return df, utc


def esr_points(out_dir=None):
    """The settlement points storage resources are settled at: the Settlement Point Names of the day-ahead awards table."""
    path = os.path.join(out_dir or ip.OUT_DIR, ESR_TABLE + ".csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{ESR_TABLE} is not on this machine: the storage resources' settlement points are read from it")
    nodes = pd.read_csv(path, skiprows=ip.header_rows(path), usecols=["node"], dtype=str, keep_default_na=False)["node"]
    return set(nodes[nodes != ""].unique())


def table(points, log, zips=None):
    """The table's rows from the saved files: the storage resources' points, the hubs and the Load Zones."""
    files = sorted(glob.glob(os.path.join(zips or ZIPS, "*.zip")))   # by name: a later posting of an interval sorts after the earlier
    urls = {m["file"]: (m["url"], m["retrieved_at"]) for m in manifest()}
    held, bad, differ = {}, [], set()   # held: interval -> (file, its prices by point and type, its rows of the table)
    for p in files:
        name = os.path.basename(p)
        with open(p, "rb") as f:
            content = f.read()
        try:
            df, utc = read_interval(content)
        except (ValueError, zipfile.BadZipFile) as e:
            bad.append((name, str(e)[:120]))
            continue
        ts = utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        prices = dict(zip(zip(df["SettlementPointName"], df["SettlementPointType"]), df["SettlementPointPrice"]))
        # session 204: ERCOT posted the interval ending 8 October 2026 11:45 twice, a second apart, every price the same.
        # Two files of one interval with the same prices are one interval (the later posting is read); two whose prices
        # differ leave the interval out: which is right is ERCOT's to say, and nothing here chooses
        if ts in differ:
            bad.append((name, f"the interval {ts} was posted more than once with prices that differ"))
            continue
        if ts in held:
            if held[ts][1] != prices:
                differ.add(ts)
                bad.append((held[ts][0], f"the interval {ts} was posted more than once with prices that differ"))
                bad.append((name, f"the interval {ts} was posted more than once with prices that differ"))
                del held[ts]
                continue
            log(f"  {ts}: posted twice with the same prices; {held[ts][0]} left out, {name} read")
        keep = df[(df["SettlementPointName"].isin(points) | df["SettlementPointType"].isin(KEEP_TYPES)) & ~df["SettlementPointType"].isin(TWICE)]
        url, when = urls.get(name, (PAGE, ""))
        held[ts] = (name, prices, pd.DataFrame({
            "entity": "ercot:" + keep["SettlementPointName"], "variable": "spp_rtm", "ts_utc": ts,
            "value": keep["SettlementPointPrice"], "unit": "USD/MWh", "freq": "PT15M", "geo": "US-TX", "market": "ercot_rtm",
            "node": keep["SettlementPointName"], "source": SOURCE, "source_url": url, "retrieved_at": when, "vintage": "",
            "x_point_type": keep["SettlementPointType"]}))
    parts = [v[2] for v in held.values()]
    for name, why in bad:
        log(f"  not written: {name}: {why}")
    if not parts:
        raise RuntimeError("no interval could be read")
    out = pd.concat(parts, ignore_index=True)
    if out.duplicated(["entity", "ts_utc"]).any():
        raise RuntimeError("a settlement point and interval twice across files")
    return out[COLS].sort_values(["entity", "ts_utc"]).reset_index(drop=True), len(parts), bad   # the intervals read: a second posting of one is not counted


def write(log, run_id):
    points = esr_points()
    out, n_files, bad = table(points, log)
    found = set(out["node"]) & points
    first, last = out["ts_utc"].min(), out["ts_utc"].max()
    header = [
        "Energy Research Warehouse (ERW): ERCOT real-time Settlement Point Prices at the storage resources' settlement points, the hubs and the Load Zones, by 15-minute interval (session 120)",
        "Shape: series (docs/datastandard.md v0). entity ercot:<settlement point>; variable spp_rtm, USD/MWh, as ERCOT prints it; ts_utc the interval's start; x_point_type ERCOT's SettlementPointType.",
        f"Coverage: {n_files} intervals read, {first} to {last}; {len(bad)} files not written. ERCOT's public list keeps seven days of this report: the table holds what was listed when it was pulled, and no more.",
        f"Settlement points: {out['node'].nunique()} ({len(found)} of the {len(points)} points a storage resource is settled at in {ESR_TABLE}, and the hubs and Load Zones). The saved files hold every point.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_rt_spp.py",
        f"Run log: warehouse/raw/ercot_rtm_spp/pull_{run_id}.log",
        f"Source: {SOURCE} ERCOT, Settlement Point Prices at Resource Nodes, Hubs and Load Zones (report type {REPORT_TYPE}), {PAGE}",
        "License: public. ERCOT's terms of use (https://www.ercot.com/help/terms): raw data in public portions of the website may be used, reproduced and redistributed in compilations, charts and analyses.",
    ]
    out["value"] = pd.to_numeric(out["value"])   # ERCOT prints two decimals; the number is the same number
    ip.write_csv(out, TABLE, header, log, cols=COLS, key=["entity", "variable", "ts_utc"], time_col="ts_utc")
    ip.update_sources([dict(source=SOURCE, publisher="Electric Reliability Council of Texas (ERCOT)",
                            # the registry already holds this report (ercot_rtm_hub_prices reads it) and /terms, a live page, prints its
                            # words: the same words, so that this table adds a name to the row's tables and changes nothing a visitor reads
                            report="Settlement Point Prices at Resource Nodes, Hubs and Load Zones",
                            report_url=PAGE, document_list=LIST, license="public", tables=[TABLE])])
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT real-time Settlement Point Prices at storage nodes (session 120)")
    ap.add_argument("--pull", action="store_true")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--daily", action="store_true", help="session 204: the pull under the day's row ceiling, then the table when a file was saved (data lock)")
    ap.add_argument("--max-rows", type=int, help=f"the rows a UTC day's runs may add (--daily: {MAX_ROWS_DAY:,} unless named)")
    ap.add_argument("--pull-dam", action="store_true", help="session 358: save the listed days of DAM Settlement Point Prices (NP4-190-CD); no table")
    a = ap.parse_args(argv)
    if a.daily:
        if a.offline:
            ap.error("--daily asks ERCOT's list; --offline does not go with it")
        a.max_rows = a.max_rows or MAX_ROWS_DAY
        if ip.paused("ercot"):   # asked before the log file is opened: a paused publisher is a skip with its reason, never a failure
            print(f"{TABLE} SKIPPED: ERCOT is paused (warehouse/metadata/paused_sources.csv); nothing is requested and the table stays as it is")
            return int(os.environ.get("ERW_SKIP_EXIT") or 0)
    os.makedirs(RAW, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logf = open(os.path.join(RAW, f"pull_{run_id}.log"), "a", encoding="utf-8")

    def log(m):
        print(m, flush=True)
        logf.write(m + "\n")
        logf.flush()
    try:
        if a.daily:
            got = {}
            rc = pull(a, log, run_id=run_id, result=got)
            if rc not in (0, 3):
                return rc
            if not got["files"]:
                log(f"{TABLE}: no file saved by this run; the table is left as it is")
                return 0
            return write(log, run_id)   # a run stopped at the ceiling still writes what it saved: the stop is the rule, not a failure
        if a.pull_dam:
            pull_dam(a, log)
            return 0
        if a.pull:
            return pull(a, log, run_id=run_id)
        if a.write:
            return write(log, run_id)
        ap.error("--pull, --pull-dam, --write or --daily")
    finally:
        logf.close()


if __name__ == "__main__":
    sys.exit(main())
