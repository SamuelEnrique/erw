#!/usr/bin/env python3
"""ERCOT load zone prices, day-ahead and real time, from 2015 (session 140, approved pull).

Energy Research Warehouse (ERW) connector. One series table,

    warehouse/output/ercot_zone_prices_history.csv      partition columns market (ercot_dam, ercot_rtm), year

the Settlement Point Prices of ERCOT's load zones, from the two yearly workbooks the hub history
(ercot_all_hub_prices_history, session 8) was read from:

    NP4-180-ER  Historical DAM Load Zone and Hub Prices   one workbook a year, one line a settlement point and hour
    NP6-785-ER  Historical RTM Load Zone and Hub Prices   one workbook a year, one line a point and 15-minute interval

    python warehouse/connectors/ercot_zone_prices.py --pull                  # ERCOT's two lists, then each workbook not yet held
    python warehouse/connectors/ercot_zone_prices.py --pull --write --years 2025 2026   # a refresh: the years still growing
    python warehouse/connectors/ercot_zone_prices.py --write                 # the table, from the saved files (data lock)
    python warehouse/connectors/ercot_zone_prices.py --write --out-dir DIR   # a trial: the table under DIR, no lock
    python warehouse/connectors/ercot_zone_prices.py --check                 # the workbooks' hub rows against the hub history

WHAT IS KEPT. The owner's approval (7 October 2026): USD 0 and a ceiling of 3,000,000 rows. Eight zones at full
resolution would be about 4.1 million rows, so the table keeps
  - day-ahead, hourly, all eight load zones: LZ_HOUSTON, LZ_NORTH, LZ_SOUTH, LZ_WEST (the competitive zones) and
    LZ_AEN, LZ_CPS, LZ_LCRA, LZ_RAYBN (the non-opt-in zones: Austin Energy, CPS Energy, LCRA, Rayburn);
  - real time, 15-minute as ERCOT settles it, the four competitive load zones only.
The hubs of the same workbooks are in ercot_all_hub_prices_history and are not written here. ERCOT prints a load zone
twice in a real-time interval, as Settlement Point Type LZ and as LZEW, and the two prices can differ: the LZ row is
kept and the LZEW row is left in the saved file, as ercot_rtm_node_prices does (one name cannot hold two prices of one
interval). The DC ties (LZ_DC and LZ_DCEW rows) are not kept. Real time for the four non-opt-in zones is in the saved
workbooks and is not written: it would pass the ceiling.

THE CEILING counts the load zone rows kept, once for every copy of a workbook ever downloaded (a repeat of the current
year counts again). Before a workbook is asked for, the most rows it could add (every hour of its year, every zone
kept) is added to the count so far; if that would pass the ceiling the pull stops before the request. --write counts
the kept rows of every saved copy and refuses to write past the ceiling. The rows of the files read (hubs, LZEW and
the rest, discarded) are counted apart and logged. --ceiling lowers or raises the number: only on the owner's word.

TWO STAGES. --pull needs no data lock: it asks ERCOT for each report's document list (saved), then downloads each
year's workbook once to warehouse/raw/ercot_zone_prices/ (one request at a time, a pause between them; manifest.csv
holds the address, bytes, sha256 and retrieval time of each; requests.csv every request made). A finished year held
(a copy ERCOT published after the year ended) is never asked for again. A year still growing when its copy was
published (the current year, which ERCOT posts again on Sundays, and last year until its final copy is held) is
asked for again only when ERCOT's list names a document this machine does not hold. --write makes no request (with
--years it rebuilds those years only and keeps the rest of the table as it is): it reads the saved
workbooks (each parsed once, the wanted rows cached beside it under parsed/) and merges them into the table by
(entity, variable, ts_utc), a year and market at a time, so a machine that holds only the current year's workbook
(the daily runner) adds to the table and never thins it. --out-dir moves the table, its log, the registry and the
status of a trial under DIR (the saved workbooks stay where --raw-dir says).

THE INTERVAL. The hub history's rule (gridstatus Ercot.parse_doc, which iso_prices.backfill_ercot used), written out
here: ERCOT gives the delivery date, the hour ending (1 to 24, Central time) and, in real time, the interval of the
hour (1 to 4). The interval's start is date + (hour ending - 1) hours + (interval - 1) x 15 minutes, Central time,
and ts_utc is that instant in UTC. On the day the clocks go back the hour ending 2 is in the workbook twice: ERCOT's
Repeated Hour Flag is N for the first (daylight time) and Y for the second (standard time), and they become two
distinct UTC hours. On the day the clocks go forward ERCOT skips the hour ending 3. A flag Y anywhere else, a time
the clock change makes absent, or a zone and interval twice with two prices stops the year: nothing is guessed.
--check proves the reading: the hub rows of the same workbooks, read by this code, against the hub history.

Real data only. A price cell that is blank or not a number is not written and is counted in the log and the header;
an interval a zone lacks stays missing and is listed in the log (a zone that begins late begins late).

License: public. ERCOT's terms of use, item 5 (https://www.ercot.com/help/terms, read 6 October 2026, the sentence
session 136 quoted): "raw data provided in public portions of this website may be used, reproduced, and redistributed
in compilations, charts, and analyses without maintaining such notices." Also: "Use of this website in a manner that
negatively affects the performance of this website or other ERCOT systems is prohibited." Hence one request at a
time and a pause.
"""

import argparse
import calendar
import collections
import csv
import datetime as dt
import glob
import hashlib
import io
import json
import os
import re
import shutil
import sys
import time
import traceback
import zipfile

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

TABLE = "ercot_zone_prices_history"
CONNECTOR = "ercot_zone_prices"
HUB_TABLE = "ercot_all_hub_prices_history"
CEILING = 3_000_000
FIRST_YEAR = 2015
TZ = ip.ERCOT_TZ
COMPETITIVE_ZONES = ["LZ_HOUSTON", "LZ_NORTH", "LZ_SOUTH", "LZ_WEST"]
NON_OPT_IN_ZONES = ["LZ_AEN", "LZ_CPS", "LZ_LCRA", "LZ_RAYBN"]
LOAD_ZONES = COMPETITIVE_ZONES + NON_OPT_IN_ZONES
HUBS = list(ip.ERCOT_HUBS)                    # read for --check only, never written here
TWICE = {"LZEW", "LZ_DCEW"}                   # a zone's second row of an interval under the same name: left in the saved file
MARKETS = {
    "dam": dict(report="NP4-180-ER", zones=LOAD_ZONES, variable="spp_dam", freq="PT1H", market="ercot_dam",
                step="1h", per_hour=1, label="day-ahead, hourly"),
    "rtm": dict(report="NP6-785-ER", zones=COMPETITIVE_ZONES, variable="spp_rtm", freq="PT15M", market="ercot_rtm",
                step="15min", per_hour=4, label="real time, 15-minute"),
}
COLS = ip.SERIES_COLS + ["year"]              # the columns of ercot_all_hub_prices_history
FILE_URL = "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={doc}"
UA = {"User-Agent": "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)"}   # dam_cleared.UA
PAUSE = 5                                     # seconds between requests
MAX_FILE = 80_000_000                         # a listed file larger than this is not a year's workbook: not requested
RAW = os.path.join(ROOT, "warehouse", "raw", CONNECTOR)
MANIFEST_COLS = ["market", "year", "file", "doc_id", "url", "bytes", "sha256", "published", "friendly_name",
                 "retrieved_at", "how"]
REQUEST_COLS = ["requested_at", "what", "url", "status", "bytes"]
PARSED_COLS = ["date", "he", "interval", "flag", "point", "ptype", "price"]
TERMS = ("ERCOT's terms of use, item 5 (https://www.ercot.com/help/terms, read 6 October 2026): \"raw data provided in "
         "public portions of this website may be used, reproduced, and redistributed in compilations, charts, and "
         "analyses without maintaining such notices.\"")


def report_page(market):
    return ip.ERCOT_PAGE.format(MARKETS[market]["report"])


def report_list(market):
    return ip.ERCOT_DOC_LIST.format(ip.ERCOT_REPORTS[MARKETS[market]["report"]][1])


def source_id(market):
    return "ercot:" + MARKETS[market]["report"]


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def this_year():
    return pd.Timestamp.now(tz=TZ).year


# ---------------------------------------------------------------------------
# The saved files: the manifest, the list of requests, the counts
# ---------------------------------------------------------------------------

def _read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _append_csv(path, cols, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(row)


def manifest(raw=None):
    """Every workbook saved, one row a copy, oldest first."""
    return _read_csv(os.path.join(raw or RAW, "manifest.csv"))


def counts(raw=None):
    """{sha256: what a parse of that saved copy counted} (rows_read, rows_kept and more)."""
    path = os.path.join(raw or RAW, "counts.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def counts_set(sha, entry, raw=None):
    path = os.path.join(raw or RAW, "counts.json")
    c = counts(raw)
    c[sha] = entry
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(c, f, indent=1, sort_keys=True)
    os.replace(path + ".tmp", path)


def hours_in_year(year):
    """The hours of ERCOT's operating year: 8,760, or 8,784 in a leap year (the two clock changes cancel)."""
    return (366 if calendar.isleap(year) else 365) * 24


def bound(market, year):
    """The most rows of the table one copy of a year's workbook can hold: every interval of the year, every zone kept."""
    m = MARKETS[market]
    return hours_in_year(int(year)) * m["per_hour"] * len(m["zones"])


def counted(raw=None):
    """The rows counted against the ceiling so far: for every copy ever saved, its kept rows (as parsed), or, for a
    copy not parsed yet, the most it can hold. A repeat of a year counts again."""
    c = counts(raw)
    total = 0
    for m in manifest(raw):
        entry = c.get(m["sha256"])
        total += int(entry["rows_kept"]) if entry else bound(m["market"], m["year"])
    return total


# ---------------------------------------------------------------------------
# --pull
# ---------------------------------------------------------------------------

def choose(docs, year):
    """ERCOT's document for a year: the one whose name ends <year>.zip, the newest published when it lists several
    (the rule gridstatus's get_dam_spp and get_rtm_spp apply, which the hub history was read with)."""
    hits = [d for d in docs if f"{year}.zip" in d.get("ConstructedName", "")]
    if not hits:
        return None
    return max(hits, key=lambda d: pd.Timestamp(d["PublishDate"]).tz_localize(None))


def final_copy(m):
    """Whether a saved copy (a manifest row) holds its whole year: ERCOT published it after the year ended."""
    return pd.Timestamp(m["published"]).tz_localize(None) >= pd.Timestamp(f"{int(m['year']) + 1}-01-01")


def vintage_of(published):
    """ERCOT's PublishDate (Central time, its offset not trusted, as gridstatus reads it) in UTC."""
    t = pd.Timestamp(published).tz_localize(None).tz_localize(TZ, ambiguous=True)
    return ip.utc_iso(t)


def pull(a, log, get=None, sleep=time.sleep, raw=None):
    """ERCOT's two lists, then each year's workbook not yet held. Returns 0, or 3 when stopped at the ceiling,
    or 1 when a file could not be had."""
    raw = raw or RAW
    os.makedirs(raw, exist_ok=True)
    if a.offline:
        log("offline: no request")
        return 0
    held_pause = ip.paused("ercot")
    if held_pause:
        line = f"{CONNECTOR} {ip.pause_line('ercot')}"
        log(line)
        return 0
    if get is None:
        import requests
        get = requests.get
    years = sorted(a.years) if a.years else list(range(FIRST_YEAR, this_year() + 1))
    markets = a.markets or list(MARKETS)
    ceiling = a.ceiling
    current = this_year()
    made = failed = 0

    def ask(what, url):
        nonlocal made
        if made:
            sleep(PAUSE)
        made += 1
        r, status, size = None, "", 0
        try:
            r = get(url, headers=UA, timeout=300)
            status, size = str(r.status_code), len(r.content)
        except Exception as e:  # recorded and returned as a failure: the caller decides
            status = f"{type(e).__name__}: {str(e)[:160]}"
            r = None
        _append_csv(os.path.join(raw, "requests.csv"), REQUEST_COLS,
                    {"requested_at": now_iso(), "what": what, "url": url, "status": status, "bytes": size})
        return r

    for market in markets:
        m = MARKETS[market]
        url = report_list(market)
        r = None
        for attempt in range(3):
            r = ask(f"{m['report']} document list", url)
            if r is not None and r.status_code == 200:
                break
            sleep(15 * (attempt + 1))
        if r is None or r.status_code != 200:
            log(f"{m['report']}: the document list could not be read ({'no answer' if r is None else r.status_code}); nothing asked for this report")
            failed += 1
            continue
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        with open(os.path.join(raw, f"doclist_{m['report']}_{stamp}.json"), "wb") as f:
            f.write(r.content)
        docs = [d["Document"] for d in r.json()["ListDocsByRptTypeRes"]["DocumentList"]]
        log(f"{m['report']}: ERCOT lists {len(docs)} documents")
        for year in years:
            d = choose(docs, year)
            if d is None:
                log(f"  {market} {year}: ERCOT lists no document named {year}.zip; nothing asked")
                continue
            man = manifest(raw)
            mine = [x for x in man if x["market"] == market and int(x["year"]) == year]
            if any(x["doc_id"] == str(d["DocID"]) for x in mine):
                log(f"  {market} {year}: held (document {d['DocID']}, published {d['PublishDate']}); not asked again")
                continue
            if mine and year != current and final_copy(mine[-1]):
                log(f"  {market} {year}: held as document {mine[-1]['doc_id']}, published after the year ended; ERCOT now lists "
                    f"{d['DocID']} (published {d['PublishDate']}): not asked again (a finished year is pulled once)")
                continue
            size = int(d.get("ContentSize") or 0)
            if size > MAX_FILE:
                log(f"  {market} {year}: listed at {size:,} bytes, more than a year's workbook: not requested")
                failed += 1
                continue
            so_far = counted(raw)
            most = bound(market, year)
            if so_far + most > ceiling:
                log(f"STOPPED before {market} {year}: {so_far:,} rows counted so far and this workbook can hold up to {most:,} "
                    f"kept rows, which would pass the ceiling of {ceiling:,}. Nothing more is requested.")
                return 3
            file_url = FILE_URL.format(doc=d["DocID"])
            g = None
            for attempt in range(3):
                g = ask(f"{m['report']} {year}", file_url)
                if g is not None and g.status_code == 200 and g.content[:2] == b"PK" and (not size or len(g.content) == size):
                    break
                log(f"  {market} {year}: attempt {attempt + 1} failed "
                    f"({'no answer' if g is None else str(g.status_code) + ', ' + str(len(g.content)) + ' bytes'})")
                g = None
                sleep(10 * (attempt + 1))
            if g is None:
                failed += 1
                log(f"  {market} {year}: three attempts failed; left for a later run")
                continue
            sha = hashlib.sha256(g.content).hexdigest()
            name = f"{market}_{year}_{d['DocID']}.zip"
            path = os.path.join(raw, name)
            with open(path + ".tmp", "wb") as f:
                f.write(g.content)
            os.replace(path + ".tmp", path)
            _append_csv(os.path.join(raw, "manifest.csv"), MANIFEST_COLS,
                        {"market": market, "year": year, "file": name, "doc_id": d["DocID"], "url": file_url,
                         "bytes": len(g.content), "sha256": sha, "published": d["PublishDate"],
                         "friendly_name": d.get("FriendlyName", ""), "retrieved_at": now_iso(), "how": "requested"})
            log(f"  {market} {year}: saved {name}, {len(g.content):,} bytes, published {d['PublishDate']}; "
                f"counted against the ceiling: {counted(raw):,} of {ceiling:,}")
    reqs = _read_csv(os.path.join(raw, "requests.csv"))
    log(f"this run made {made} requests; in all {len(reqs)} requests and {sum(int(x['bytes']) for x in reqs):,} bytes; "
        f"{len(manifest(raw))} workbooks held; counted against the ceiling {counted(raw):,} of {ceiling:,}")
    return 1 if failed else 0


# ---------------------------------------------------------------------------
# Reading a workbook
# ---------------------------------------------------------------------------

def workbook_bytes(content):
    """The year's workbook: the file itself, or the one workbook inside ERCOT's zip."""
    if content[:2] != b"PK":
        raise RuntimeError("not a zip or a workbook")
    z = zipfile.ZipFile(io.BytesIO(content))
    names = z.namelist()
    if "[Content_Types].xml" in names:
        return content
    books = [n for n in names if n.lower().endswith(".xlsx")]
    if len(books) != 1:
        raise RuntimeError(f"the zip holds {names}, expected one workbook")
    return z.read(books[0])


def _norm(c):
    return re.sub(r"[^a-z]", "", str(c).lower())


def read_workbook(content, market, want=None):
    """Every sheet of a year's workbook, a line at a time. Returns (the lines of the settlement points in `want`, as
    ERCOT printed them: date, he, interval, flag, point, ptype, price; what was counted). Nothing is converted here
    but the date to YYYY-MM-DD and the hour ending to its number."""
    import openpyxl
    want = set(LOAD_ZONES + HUBS if want is None else want)
    wb = openpyxl.load_workbook(io.BytesIO(workbook_bytes(content)), read_only=True, data_only=True)
    rows, seen = [], collections.Counter()
    stats = {"sheets": 0, "empty_sheets": 0, "rows_read": 0, "blank_lines": 0}
    need = (["deliverydate", "settlementpointprice", "repeatedhourflag"]
            + (["deliveryhour", "deliveryinterval", "settlementpointname", "settlementpointtype"] if market == "rtm"
               else ["hourending", "settlementpoint"]))
    try:
        for ws in wb.worksheets:
            stats["sheets"] += 1
            ws.reset_dimensions()                   # ERCOT's sheets declare one cell (A1); the lines are read to their end
            it = ws.iter_rows(values_only=True)
            head = next(it, None)
            if head is None or all(c is None for c in head):
                stats["empty_sheets"] += 1          # the current year's workbook has a sheet for each month to come
                continue
            col = {_norm(c): i for i, c in enumerate(head) if c is not None}
            missing = [c for c in need if c not in col]
            if missing:
                raise RuntimeError(f"sheet {ws.title!r}: columns {list(head)}, missing {missing}")
            i_date, i_price, i_flag = col["deliverydate"], col["settlementpointprice"], col["repeatedhourflag"]
            if market == "rtm":
                i_he, i_int, i_pt, i_type = col["deliveryhour"], col["deliveryinterval"], col["settlementpointname"], col["settlementpointtype"]
            else:
                i_he, i_int, i_pt, i_type = col["hourending"], None, col["settlementpoint"], None
            for r in it:
                point = r[i_pt]
                if point is None:
                    if any(c is not None for c in r):
                        stats["rows_read"] += 1
                    stats["blank_lines"] += 1
                    continue
                stats["rows_read"] += 1
                ptype = r[i_type] if i_type is not None else ""
                seen[f"{point}|{ptype}"] += 1
                if point not in want:
                    continue
                d = r[i_date]
                if isinstance(d, (dt.datetime, dt.date)):
                    d = f"{d.year:04d}-{d.month:02d}-{d.day:02d}"
                else:
                    mo, day, yr = str(d).strip().split("/")
                    d = f"{int(yr):04d}-{int(mo):02d}-{int(day):02d}"
                he = r[i_he]
                he = int(str(he).split(":")[0]) if isinstance(he, str) else int(he)
                rows.append((d, he, 1 if i_int is None else int(r[i_int]), str(r[i_flag]).strip(), point, ptype,
                             "" if r[i_price] is None else r[i_price]))
    finally:
        wb.close()
    stats["points"] = dict(sorted(seen.items()))
    return pd.DataFrame(rows, columns=PARSED_COLS), stats


def interval_start(df):
    """ts (UTC, the interval's start) for lines of a workbook: the rule in the module docstring. Raises on a flag
    that is not N or Y, a Y outside the repeated hour, an hour or interval out of range, a time the clocks skip."""
    flags = set(df["flag"].unique())
    if not flags <= {"N", "Y"}:
        raise RuntimeError(f"Repeated Hour Flag holds {sorted(flags)}, expected N and Y")
    he, q = df["he"].astype(int), df["interval"].astype(int)
    if not (he.between(1, 24).all() and q.between(1, 4).all()):
        raise RuntimeError("an hour ending outside 1 to 24 or an interval outside 1 to 4")
    local = pd.to_datetime(df["date"], format="%Y-%m-%d") + pd.to_timedelta(he - 1, unit="h") + pd.to_timedelta((q - 1) * 15, unit="m")
    first = (df["flag"] == "N").to_numpy()            # pandas: True places a repeated time in daylight time, the first
    ts = local.dt.tz_localize(TZ, ambiguous=first, nonexistent="raise").dt.tz_convert("UTC")
    second = ~first
    if second.any():
        other = local[second].dt.tz_localize(TZ, ambiguous=True, nonexistent="raise").dt.tz_convert("UTC")
        if (other.to_numpy() == ts[second].to_numpy()).any():
            bad = df[second][other.to_numpy() == ts[second].to_numpy()].iloc[0]
            raise RuntimeError(f"ERCOT flags {bad['date']} hour ending {bad['he']} as a repeated hour, and it is not one")
    return ts


def shape(lines, market, year, zones=None):
    """The kept lines of one workbook as rows (node, interval_start, value), with what was dropped and why.
    zones: the settlement points wanted (default: the market's load zones). LZEW rows are never taken."""
    zones = MARKETS[market]["zones"] if zones is None else zones
    d = lines[lines["point"].isin(zones) & ~lines["ptype"].isin(TWICE)].copy()
    notes = {"blank_prices": 0, "same_twice": 0}
    if d.empty:
        return pd.DataFrame(columns=["node", "interval_start", "value"]), notes
    years = set(d["date"].str[:4])
    if years != {str(year)}:
        raise RuntimeError(f"{market} {year}: the workbook holds delivery dates of {sorted(years)}")
    d["value"] = pd.to_numeric(d["price"], errors="coerce")
    blank = d["value"].isna()
    notes["blank_prices"] = int(blank.sum())
    notes["blank_examples"] = [f"{r.point} {r.date} hour ending {r.he} interval {r.interval}: {r.price!r}" for r in d[blank].head(10).itertuples()]
    d = d[~blank]
    d["interval_start"] = interval_start(d)
    out = pd.DataFrame({"node": d["point"].astype(str).values, "interval_start": d["interval_start"].values, "value": d["value"].values})
    out["interval_start"] = pd.to_datetime(out["interval_start"], utc=True)
    dup = out.duplicated(["node", "interval_start"], keep=False)
    if dup.any():
        spread = out[dup].groupby(["node", "interval_start"])["value"].agg(["min", "max"])
        two = spread[spread["max"] != spread["min"]]
        if len(two):
            k = two.index[0]
            raise RuntimeError(f"{market} {year}: {len(two)} zone intervals are in the workbook twice with two prices "
                               f"(first {k[0]} {ip.utc_iso(k[1])}: {two.iloc[0]['min']} and {two.iloc[0]['max']}); the year is not written")
        notes["same_twice"] = int(out.duplicated(["node", "interval_start"]).sum())
        out = out.drop_duplicates(["node", "interval_start"])
    return out.sort_values(["node", "interval_start"]).reset_index(drop=True), notes


def parsed(m, log, raw=None):
    """The wanted lines of one saved copy (a manifest row): read from the cache beside it, or parsed once and
    cached. The cache is named by the copy's sha256, so it can never stand for another file."""
    raw = raw or RAW
    cache = os.path.join(raw, "parsed", f"{m['market']}_{m['year']}_{m['sha256'][:16]}.csv.gz")
    entry = counts(raw).get(m["sha256"])
    if entry and os.path.exists(cache):
        return pd.read_csv(cache, dtype={"date": str, "flag": str, "point": str, "ptype": str, "price": str},
                           keep_default_na=False, na_values=[]), entry
    path = os.path.join(raw, m["file"])
    with open(path, "rb") as f:
        content = f.read()
    if hashlib.sha256(content).hexdigest() != m["sha256"]:
        raise RuntimeError(f"{m['file']} is not the file the manifest describes (sha256 differs)")
    t0 = time.time()
    lines, stats = read_workbook(content, m["market"])
    del content
    kept, notes = shape(lines, m["market"], int(m["year"]))
    stats["rows_kept"] = int(len(kept))
    stats["market"], stats["year"], stats["file"] = m["market"], int(m["year"]), m["file"]
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    lines.to_csv(cache + ".tmp", index=False, compression="gzip", lineterminator="\n")
    os.replace(cache + ".tmp", cache)
    counts_set(m["sha256"], stats, raw)
    log(f"  read {m['file']}: {stats['sheets']} sheets ({stats['empty_sheets']} empty), {stats['rows_read']:,} rows in the file, "
        f"{stats['rows_kept']:,} load zone rows kept, {time.time() - t0:.0f} s")
    return pd.read_csv(cache, dtype={"date": str, "flag": str, "point": str, "ptype": str, "price": str},
                       keep_default_na=False, na_values=[]), stats


def gaps(rows, market, year, zones, log):
    """What each zone holds of its year, and what it lacks. Reported, never filled."""
    step = MARKETS[market]["step"]
    start = pd.Timestamp(f"{year}-01-01").tz_localize(TZ).tz_convert("UTC")
    end = pd.Timestamp(f"{year + 1}-01-01").tz_localize(TZ).tz_convert("UTC")
    if len(rows):
        end = min(end, rows["interval_start"].max() + pd.Timedelta(step))   # the current year ends where the workbook ends
    expected = pd.date_range(start, end, freq=step, inclusive="left")
    out = []
    for z in zones:
        have = pd.DatetimeIndex(rows.loc[rows["node"] == z, "interval_start"])
        if not len(have):
            out.append(f"{market} {year} {z}: no row")
            continue
        missing = expected.difference(have)
        extra = have.difference(expected)
        if len(missing) or len(extra):
            lead = int((missing < have.min()).sum())
            out.append(f"{market} {year} {z}: {len(have):,} of {len(expected):,} intervals; missing {len(missing):,} "
                       f"({lead:,} before its first row at {ip.utc_iso(have.min())}; first missing {[ip.utc_iso(t) for t in missing[:3]]}); "
                       f"outside the year {len(extra)}")
    for line in out:
        log("    GAP " + line)
    return out


# ---------------------------------------------------------------------------
# --write
# ---------------------------------------------------------------------------

def series(rows, market, year, m):
    cfg = MARKETS[market]
    return pd.DataFrame({
        "entity": "ercot:" + rows["node"],
        "variable": cfg["variable"],
        "ts_utc": rows["interval_start"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value": rows["value"],
        "unit": "USD/MWh",
        "freq": cfg["freq"],
        "geo": "US-TX",
        "market": cfg["market"],
        "node": rows["node"],
        "source": source_id(market),
        "source_url": m["url"],
        "retrieved_at": m["retrieved_at"],
        "vintage": vintage_of(m["published"]),
        "year": str(year),
    })[COLS]


def _split_old(path, tmp, log):
    """The table already on the machine, a (market, year) at a time, as files under tmp. Returns {(market, year): path}."""
    parts = {}
    if not os.path.exists(path):
        return parts
    skip = ip.header_rows(path)
    for chunk in pd.read_csv(path, skiprows=skip, dtype=str, keep_default_na=False, na_values=[], chunksize=200_000):
        if list(chunk.columns) != COLS:
            raise RuntimeError(f"{path} has columns {list(chunk.columns)}, expected {COLS}; not merging into a file of another shape")
        for (market, year), g in chunk.groupby(["market", "year"], sort=False):
            p = os.path.join(tmp, f"old_{market}_{year}.csv")
            g.to_csv(p, mode="a", index=False, header=not os.path.exists(p), lineterminator="\n")
            parts[(market, year)] = p
    log(f"  the table on this machine: {len(parts)} (market, year) parts")
    return parts


def write(a, log, run_id, raw=None):
    """The table from the saved workbooks, merged a (market, year) at a time into what the machine holds."""
    raw = raw or RAW
    path = os.path.join(ip.OUT_DIR, TABLE + ".csv")
    ip._require_lock(path, f"writing {TABLE}")   # the data lock; a trial under --out-dir is not a data write
    man = manifest(raw)
    if not man:
        raise RuntimeError(f"no saved workbook under {raw}: run --pull first")
    for m in man:                                # every copy is read (once) so the ceiling is counted, not estimated
        parsed(m, log, raw)
    c = counts(raw)
    kept_all = sum(int(c[m["sha256"]]["rows_kept"]) for m in man)
    read_all = sum(int(c[m["sha256"]]["rows_read"]) for m in man)
    log(f"counted against the ceiling: {kept_all:,} load zone rows kept in {len(man)} saved copies (ceiling {a.ceiling:,}); "
        f"rows in the files read: {read_all:,}")
    if kept_all > a.ceiling:
        raise RuntimeError(f"{kept_all:,} kept rows pass the ceiling of {a.ceiling:,}: nothing is written")
    tmp = os.path.join(raw, f"tmp_write_{run_id}")
    os.makedirs(tmp, exist_ok=True)
    results, notes, gap_lines, used = [], [], [], []
    try:
        old_parts = _split_old(path, tmp, log)
        copies = collections.defaultdict(list)
        for m in man:
            if a.years and int(m["year"]) not in a.years:
                continue                          # --years: only these years are rebuilt; the others stay as the table holds them
            copies[(MARKETS[m["market"]]["market"], str(m["year"]))].append(m)
        body = os.path.join(tmp, "body.csv")
        total = added = replaced = kept_old = 0
        first_ts, last_ts, per = None, None, collections.Counter()
        with open(body, "w", encoding="utf-8", newline="") as bf:
            for key in sorted(set(old_parts) | set(copies)):
                market_name, year = key
                market = "dam" if market_name == "ercot_dam" else "rtm"
                name = f"{market_name} {year}"
                new = None
                try:
                    frames = []
                    for m in copies.get(key, []):            # oldest copy first: a newer copy's row replaces an older one's
                        lines, _ = parsed(m, log, raw)
                        rows, n = shape(lines, market, int(year))
                        del lines
                        if n["blank_prices"]:
                            notes.append(f"{name}: {n['blank_prices']} price cells blank or not a number, not written ({'; '.join(n['blank_examples'][:3])})")
                            log(f"    {name}: {n['blank_prices']} blank price cells: {n['blank_examples']}")
                        if n["same_twice"]:
                            log(f"    {name}: {n['same_twice']} zone intervals twice in the workbook with the same price, written once")
                        frames.append(series(rows, market, year, m))
                        used.append(m)
                        if m is copies[key][-1]:
                            gap_lines += gaps(rows, market, int(year), MARKETS[market]["zones"], log)
                    if frames:
                        new = pd.concat(frames, ignore_index=True).drop_duplicates(ip.SERIES_KEY, keep="last")
                    results.append(dict(table=TABLE, market=name, status="ok", detail=""))
                except Exception:
                    tb = traceback.format_exc()
                    last = tb.strip().splitlines()[-1]
                    log(f"{name} FAILED, its rows are not written (rows already in the table stay):\n{tb}")
                    print(f"{CONNECTOR} {market_name}_{year} FAILED: {last}", file=sys.stderr)
                    results.append(dict(table=TABLE, market=name, status="failed", detail=last[:300]))
                    new = None
                old = None
                if key in old_parts:
                    old = pd.read_csv(old_parts[key], dtype=str, keep_default_na=False, na_values=[])
                    old["value"] = pd.to_numeric(old["value"], errors="raise")
                if new is None and old is None:
                    continue
                if new is None:
                    merged, st = old.sort_values(ip.SERIES_KEY).reset_index(drop=True)[COLS], {"kept": len(old), "replaced": 0, "added": 0}
                else:
                    merged, st = ip.merge_series(old, new, cols=COLS)
                merged.to_csv(bf, index=False, header=(total == 0), lineterminator="\n")
                total += len(merged)
                added, replaced, kept_old = added + st["added"], replaced + st["replaced"], kept_old + st["kept"]
                first_ts = merged["ts_utc"].min() if first_ts is None else min(first_ts, merged["ts_utc"].min())
                last_ts = merged["ts_utc"].max() if last_ts is None else max(last_ts, merged["ts_utc"].max())
                for node, n in merged.groupby("node").size().items():
                    per[(market_name, node)] += int(n)
                log(f"  {name}: {len(merged):,} rows ({st['added']:,} new, {st['replaced']:,} replacing, {st['kept']:,} kept), "
                    f"{merged['ts_utc'].min()} to {merged['ts_utc'].max()}, min {merged['value'].min():.2f} max {merged['value'].max():.2f}")
                del merged, old, new
        if not total:
            raise RuntimeError("no row could be written")
        header = _header(run_id, a, first_ts, last_ts, used, kept_all, read_all, per, notes, gap_lines)
        header.append(f"File holds {total} rows, {first_ts} to {last_ts}. This run wrote {added + replaced} rows: {added} new, "
                      f"{replaced} replacing earlier rows with the same (entity, variable, ts_utc); {kept_old} rows are kept from "
                      "earlier runs. Per row, source, source_url and retrieved_at say where it came from.")
        with open(path + ".tmp", "w", encoding="utf-8", newline="") as f:
            for line in header:
                f.write("# " + line + "\n")
            with open(body, encoding="utf-8", newline="") as bf:
                shutil.copyfileobj(bf, f, 1 << 20)
        os.replace(path + ".tmp", path)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    summary = (f"{TABLE}.csv: rows={total} (this run {added + replaced}: {added} new, {replaced} replaced, {kept_old} kept) "
               f"range={first_ts}..{last_ts}")
    print(summary)
    log("  " + summary)
    for (market_name, node), n in sorted(per.items()):
        log(f"    {market_name} {node}: {n:,} rows")
    ok = {r["market"].split(" ")[0] for r in results if r["status"] == "ok"}
    by_market = []                                # the status: one line a market, as the hub connector writes it
    for k, cfg in MARKETS.items():
        mine = [r for r in results if r["market"].split(" ")[0] == cfg["market"]]
        bad = [r for r in mine if r["status"] == "failed"]
        if mine:
            by_market.append(dict(table=TABLE, market=k.upper(), status="failed" if bad else "ok",
                                  detail="; ".join(f"{r['market']}: {r['detail']}" for r in bad)[:300]))
    ip.update_sources([dict(source=source_id(k), publisher=ip.ISO_PUBLISHERS["ercot"],
                            # the registry already holds both reports (the hub history reads them): the same words, so
                            # this table adds its name to the row's tables and changes nothing else
                            report=ip.ERCOT_REPORTS[MARKETS[k]["report"]][0], report_url=report_page(k),
                            document_list=report_list(k), tables=[TABLE] if MARKETS[k]["market"] in ok else [])
                       for k in MARKETS])
    ip.write_status(CONNECTOR, run_id, by_market)
    return 1 if any(r["status"] == "failed" for r in results) else 0


def _header(run_id, a, first_ts, last_ts, used, kept_all, read_all, per, notes, gap_lines):
    start = pd.Timestamp(first_ts).tz_convert(TZ)
    end = pd.Timestamp(last_ts).tz_convert(TZ)
    lines = [
        "Energy Research Warehouse (ERW): ERCOT load zone settlement point prices, day-ahead (hourly, the eight load zones) and "
        "real time (15-minute, the four competitive load zones), one row per interval of each operating year from 2015 (session 140)",
        "Shape: series (docs/datastandard.md v0). Units: USD/MWh. ts_utc is interval start, UTC. Partition columns market, year "
        "(ERCOT's operating year, America/Chicago), as ercot_all_hub_prices_history has them.",
        f"Window: ERCOT operating days {start.date()} to {end.date()} (America/Chicago), first interval {first_ts}, last {last_ts}",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_zone_prices.py --write, from the workbooks its --pull saved; "
        "each row's retrieved_at is the time its own workbook was downloaded and vintage the time ERCOT published it",
        "Run log: " + os.path.relpath(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"), ROOT).replace(os.sep, "/"),
        f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git; manifest.csv lists each workbook, its address, bytes and sha256)",
    ]
    for k, cfg in MARKETS.items():
        mine = [m for m in used if m["market"] == k]
        if not mine:
            continue
        v = sorted(vintage_of(m["published"]) for m in mine)
        lines.append(f"Source: ERCOT {cfg['report']} {ip.ERCOT_REPORTS[cfg['report']][0]}, {report_page(k)}")
        lines.append(f"  document list: {report_list(k)}")
        lines.append(f"  {len(mine)} document(s) used, published {v[0]} to {v[-1]}; rows from each: see source_url and vintage columns")
    lines += [
        "Kept: day-ahead " + ", ".join(LOAD_ZONES) + "; real time " + ", ".join(COMPETITIVE_ZONES) + ". The hubs of the same "
        "workbooks are in ercot_all_hub_prices_history. A zone's second real-time row (Settlement Point Type LZEW) and the DC ties "
        "stay in the saved workbooks. Real time for LZ_AEN, LZ_CPS, LZ_LCRA and LZ_RAYBN is not written: it would pass the ceiling.",
        f"Ceiling (the owner's approval of 7 October 2026): {a.ceiling:,} rows, USD 0. Counted against it: {kept_all:,} load zone rows "
        f"kept, every saved copy of a workbook counted; rows in the files read (hubs and the rest, discarded): {read_all:,}.",
        "Rows by market and zone: " + "; ".join(f"{mk} {node} {n}" for (mk, node), n in sorted(per.items())),
        "DST: interval starts are UTC. The hour the clocks skip in spring does not exist; the hour they repeat in autumn is in "
        "ERCOT's workbook twice (Repeated Hour Flag N, then Y) and is two distinct UTC hours here.",
        "Missing stays missing: " + (f"{len(gap_lines)} zone-years lack intervals (" + " | ".join(gap_lines[:12])
                                    + (f" | and {len(gap_lines) - 12} more, in the run log" if len(gap_lines) > 12 else "") + ")"
                                    if gap_lines else "every zone has every interval of every year it is in, up to each workbook's last interval."),
    ]
    lines += notes
    lines.append("License: public. " + TERMS)
    return lines


# ---------------------------------------------------------------------------
# --check: the hub rows of the same workbooks against the hub history
# ---------------------------------------------------------------------------

def check(a, log, raw=None):
    """The proof of the reading: every row of ercot_all_hub_prices_history, found again in the hub lines of the saved
    workbooks as this connector reads them (same hub, same UTC interval), and the largest difference of price."""
    raw = raw or RAW
    hub_path = a.hub_table or os.path.join(ROOT, "warehouse", "output", HUB_TABLE + ".csv")
    want_years = set(a.years) if a.years else None
    hist = []
    for chunk in pd.read_csv(hub_path, skiprows=ip.header_rows(hub_path), usecols=["node", "ts_utc", "value", "market", "year"],
                             dtype={"node": "category", "market": "category", "ts_utc": str}, chunksize=400_000):
        if want_years is not None:
            chunk = chunk[chunk["year"].isin(want_years)]
        chunk = chunk.assign(ts=pd.to_datetime(chunk["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True)).drop(columns=["ts_utc"])
        hist.append(chunk)
    hist = pd.concat(hist, ignore_index=True)
    log(f"hub history: {len(hist):,} rows read from {hub_path}")
    latest = {}
    for m in manifest(raw):
        latest[(m["market"], int(m["year"]))] = m           # the newest copy of each year
    bad = 0
    worst = (0.0, "")
    for (market, year), m in sorted(latest.items()):
        if want_years is not None and year not in want_years:
            continue
        cfg = MARKETS[market]
        h = hist[(hist["market"] == cfg["market"]) & (hist["year"] == year)]
        lines, _ = parsed(m, log, raw)
        mine, _ = shape(lines, market, year, zones=HUBS)
        del lines
        j = h.merge(mine, left_on=["node", "ts"], right_on=["node", "interval_start"], how="left", validate="one_to_one")
        if len(j) != len(h):
            raise RuntimeError(f"{market} {year}: the join fanned out: {len(j)} rows for {len(h)} of the hub history")
        absent = int(j["value_y"].isna().sum())
        d = (j["value_x"] - j["value_y"]).abs()
        differ = int((d > ip.TOLERANCE).sum())
        big = float(d.max()) if len(d) and d.notna().any() else 0.0
        beyond = len(mine) - (len(j) - absent)
        line = (f"  {market} {year}: hub history {len(h):,} rows, all joined ({len(j):,}); {absent} absent from the workbook as read here; "
                f"{differ} differ by more than {ip.TOLERANCE}; largest difference {big:.4f}; hub rows read here and not in the history: {beyond:,}")
        log(line)
        if big > worst[0]:
            k = j.loc[d.idxmax()]
            worst = (big, f"{market} {year} {k['node']} {ip.utc_iso(k['ts'])}: history {k['value_x']} workbook {k['value_y']}")
        for _, k in j[d > ip.TOLERANCE].head(5).iterrows():
            log(f"    differs: {k['node']} {ip.utc_iso(k['ts'])} history {k['value_x']} workbook {k['value_y']}")
        if absent or differ or not len(h):
            bad += 1
    log(f"hub cross-check: {'FAILED for ' + str(bad) + ' year(s)' if bad else 'passed'}; largest difference {worst[0]:.4f} {worst[1]}")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT load zone prices, day-ahead and real time, from 2015 (session 140)")
    ap.add_argument("--pull", action="store_true", help="ERCOT's lists, then each year's workbook not yet held (no data lock)")
    ap.add_argument("--offline", action="store_true", help="with --pull: no request")
    ap.add_argument("--write", action="store_true", help="the table from the saved workbooks (data lock; no request)")
    ap.add_argument("--check", action="store_true", help="the saved workbooks' hub rows against ercot_all_hub_prices_history")
    ap.add_argument("--years", type=int, nargs="*", help="only these years (default: 2015 to this year)")
    ap.add_argument("--markets", nargs="*", choices=sorted(MARKETS), help="only these markets (default: both)")
    ap.add_argument("--ceiling", type=int, default=CEILING, help=f"rows kept, every saved copy counted (default {CEILING:,}, the owner's approval)")
    ap.add_argument("--out-dir", help="a trial: the table, log, registry and status under this directory, no lock")
    ap.add_argument("--raw-dir", help="where the workbooks are saved and read (default warehouse/raw/ercot_zone_prices)")
    ap.add_argument("--hub-table", help="with --check: the hub history file (default warehouse/output)")
    a = ap.parse_args(argv)
    if not (a.pull or a.write or a.check):
        ap.error("--pull, --write or --check")
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    raw = os.path.abspath(a.raw_dir) if a.raw_dir else RAW
    os.makedirs(raw, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if a.write or a.out_dir:
        os.makedirs(ip.LOG_DIR, exist_ok=True)
        log_path = os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log")
    else:
        log_path = os.path.join(raw, f"{'pull' if a.pull else 'check'}_{run_id}.log")   # no data lock: nothing under warehouse/output
    logf = open(log_path, "a", encoding="utf-8", newline="\n")

    def log(msg):
        print(msg, flush=True)
        logf.write(str(msg) + "\n")
        logf.flush()
    log(f"ERW {CONNECTOR} run {run_id}: {'pull ' if a.pull else ''}{'write ' if a.write else ''}{'check ' if a.check else ''}"
        f"raw {raw}; ceiling {a.ceiling:,}")
    rc = 0
    try:
        if a.pull:
            rc = max(rc, pull(a, log, raw=raw))
        if a.write and rc in (0, 1):
            rc = max(rc, write(a, log, run_id, raw=raw))
        if a.check:
            rc = max(rc, check(a, log, raw=raw))
    except Exception:
        log(f"{CONNECTOR} FAILED:\n{traceback.format_exc()}")
        rc = 1
    finally:
        log(f"done, exit {rc}; log {log_path}")
        logf.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
