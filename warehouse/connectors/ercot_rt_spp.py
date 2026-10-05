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
KEEP_TYPES = {"HU", "SH", "AH", "LZ", "LZ_DC"}   # hubs and Load Zones: kept whatever resource sits there
TWICE = {"LZEW", "LZ_DCEW"}                     # a zone's second row in the file, under the same name: left in the saved file
ESR_TABLE = "ercot_dam_esr_awards"
NAME = re.compile(r"SPPHLZNP6905_(\d{8})_(\d{4})_csv$")
COLS = ip.SERIES_COLS + ["x_point_type"]


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


def pull(a, log, get=requests.get):
    saved = os.path.join(RAW, "doclist_latest.json")
    os.makedirs(ZIPS, exist_ok=True)
    if a.offline:
        log("offline: no request")
        return 0
    if ip.paused("ercot"):
        raise RuntimeError("ERCOT is paused (warehouse/metadata/paused_sources.csv): nothing is requested")
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
    n = failed = 0
    for d in todo:
        size = int(d["ContentSize"])
        if size > MAX_FILE:
            log(f"  {d['FriendlyName']}: listed at {size:,} bytes, not requested")
            continue
        if done + size > MAX_BYTES:
            log(f"STOPPED at this connector's ceiling of {MAX_BYTES:,} bytes")
            return 3
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
        if n % 100 == 0:
            log(f"  {n} of {len(todo)} saved; {done:,} bytes downloaded")
    log(f"{n} files saved by this run, {failed} failed; {len(glob.glob(os.path.join(ZIPS, '*.zip')))} on this machine; {done:,} bytes downloaded in all")
    return 0


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
    files = sorted(glob.glob(os.path.join(zips or ZIPS, "*.zip")))
    urls = {m["file"]: (m["url"], m["retrieved_at"]) for m in manifest()}
    parts, bad = [], []
    for p in files:
        with open(p, "rb") as f:
            content = f.read()
        try:
            df, utc = read_interval(content)
        except (ValueError, zipfile.BadZipFile) as e:
            bad.append((os.path.basename(p), str(e)[:120]))
            continue
        keep = df[(df["SettlementPointName"].isin(points) | df["SettlementPointType"].isin(KEEP_TYPES)) & ~df["SettlementPointType"].isin(TWICE)]
        url, when = urls.get(os.path.basename(p), (PAGE, ""))
        parts.append(pd.DataFrame({
            "entity": "ercot:" + keep["SettlementPointName"], "variable": "spp_rtm", "ts_utc": utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "value": keep["SettlementPointPrice"], "unit": "USD/MWh", "freq": "PT15M", "geo": "US-TX", "market": "ercot_rtm",
            "node": keep["SettlementPointName"], "source": SOURCE, "source_url": url, "retrieved_at": when, "vintage": "",
            "x_point_type": keep["SettlementPointType"]}))
    for name, why in bad:
        log(f"  not written: {name}: {why}")
    if not parts:
        raise RuntimeError("no interval could be read")
    out = pd.concat(parts, ignore_index=True)
    if out.duplicated(["entity", "ts_utc"]).any():
        raise RuntimeError("a settlement point and interval twice across files")
    return out[COLS].sort_values(["entity", "ts_utc"]).reset_index(drop=True), len(files), bad


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
    a = ap.parse_args(argv)
    os.makedirs(RAW, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logf = open(os.path.join(RAW, f"pull_{run_id}.log"), "a", encoding="utf-8")

    def log(m):
        print(m, flush=True)
        logf.write(m + "\n")
        logf.flush()
    try:
        if a.pull:
            return pull(a, log)
        if a.write:
            return write(log, run_id)
        ap.error("--pull or --write")
    finally:
        logf.close()


if __name__ == "__main__":
    sys.exit(main())
