#!/usr/bin/env python3
"""Zone and hub prices back to 2019, kept as history past the six-week tables (session 140, approved pull).

Energy Research Warehouse (ERW) connector. Two series tables, partition column market, split by license so that
ISO-NE's notice does not hold the other grids internal:

    warehouse/output/iso_zone_prices_history.csv      NYISO, CAISO and SPP markets (public sources)
    warehouse/output/isone_zone_prices_history.csv    ISO-NE's two markets (isone:smd_hourly_lmp, internal)

with the hourly prices of the regions the six-week tables hold too briefly for "What a datacenter pays"
(/cost-of-power) to answer for a year: NYISO's eleven load zones, ISO-NE's eight load zones, CAISO's ZP26 and SPP's
South hub. Entities, variables and columns are those of the six-week tables and of iso_hub_prices_history, so
warehouse/derived/price_compare.py and datacenter_page.py read them as they read those. The two tables have the same
columns, the same rules and the same merge; a market belongs to one table only, and the writer refuses a row of
another table's market.

    python warehouse/connectors/zone_price_history.py --pull [--iso nyiso ...] [--from YYYY-MM-DD] [--until YYYY-MM-DD] [--limit N]
    python warehouse/connectors/zone_price_history.py --write [--out-dir DIR]     # both tables, from the saved files only
    python warehouse/connectors/zone_price_history.py --check [--out-dir DIR]     # the hour, against the six-week tables
    python warehouse/connectors/zone_price_history.py --pull --recent 9           # the weekly run: the newest files
    python warehouse/connectors/zone_price_history.py --write --recent 9          # and their rows into the table held

WHAT IS ASKED FOR, one request at a time a publisher, with a pause, each file saved once:

    market      what                                    source                                             from
    nyiso_dam   day-ahead LBMP, hourly, 11 zones        NYISO P-2A, a zip a month (one CSV a day)          2019-01-01
                http://mis.nyiso.com/public/csv/damlbmp/<YYYYMM>01damlbmp_zone_csv.zip
    nyiso_rtm   real-time LBMP, hourly, 11 zones        NYISO P-4A, "Time-Weighted/Integrated Real-Time    2019-01-01
                LBMP", NYISO's own hourly figure        http://mis.nyiso.com/public/csv/rtlbmp/<YYYYMM>01rtlbmp_zone_csv.zip
    isone_dam   day-ahead LMP, hourly, 8 load zones     ISO-NE "SMD Hourly Data", a workbook a year, one    2019-01-01
    isone_rtm   real-time LMP, hourly, 8 load zones     sheet a zone (columns DA_LMP, RT_LMP). The years
                                                        isone_zone_load.py already keeps are read from its
                                                        raw files and never asked for again
    caiso_dam   day-ahead LMP, hourly, ZP26             OASIS PRC_LMP, a calendar month a request           2019-01-01 asked;
                                                                                                           OASIS keeps 39 months
    caiso_rtm   real-time (RTD) LMP, 5-minute, held     OASIS PRC_INTVL_LMP, a calendar month a request     2024-09-01
                as 15-minute means, as the hub history
                holds SP15
    spp_dam     day-ahead LMP, hourly, SPPSOUTH_HUB     SPP DA-LMP-SL, a file a day; a finished year from   2019-01-01
                                                        SPP's archive of the year by HTTP range requests
                                                        (hub_history.py, session 64), the day's member only

SPP's real-time 5-minute files (about 7 MB a day) are not asked for here: no spp_rtm rows are written.

THE STAGES. --pull saves every file under warehouse/raw/zone_price_history/<iso>/ with a manifest (manifest.csv: when,
HTTP status, bytes and sha256 of the body received, the file, its address, the rows of these series in it, the rows in
the file). It takes no data lock and writes no table. It can be stopped and run again: a period whose file is kept is
not asked for again, unless the file was fetched before its period had ended (the current month, the current year).
It works newest first, so a pull that is stopped holds the latest months. --write reads the saved files only (no
request) and merges their rows into the table, a market at a time; into warehouse/output it needs the data lock.
--check joins the table to the six-week tables over the hours both hold and says, per market, how many prices agree
at the same hour and at one hour either side.

THE CEILING. 3,000,000 rows of these series read to keep, over every run of the history pull, repeats and probes
included (the count is the sum of the manifests' series_rows and of probes.csv; a 5-minute source row counts as one
row, although three of them make one row of the table; a workbook reused from isone_zone_load.py counts as read).
Before each request the rows the file is taken to hold are added to the count: a request that would pass the ceiling
is not made and the pull stops. The rows of other nodes in the files read are counted apart (file_rows). The weekly
run (--recent) has a ceiling of its own, 250,000 rows a run, and its rows are marked "refresh" in the manifest.

THE HOUR. ts_utc is the hour's (or quarter hour's) start, UTC. Session 140 proved each convention with prices
against the six-week tables (--check): day-ahead prices equal to the cent at the same hour, in every market.
NYISO: Time Stamp is the hour's start, Eastern, with no zone on the line; the repeated autumn hour is in the file
twice and is placed by its order (the first daylight time, the second standard time).
ISO-NE: Hr_End is the hour ending in Eastern prevailing time. The workbooks from 2024 have 23 lines on the spring day
(01, then 03: the line 03 is placed by its end, zone_load.to_utc) and 25 on the autumn day (02, then 02X). The
workbooks of 2019 to 2023 have 24 lines on both days, and their Notes sheet says why: "In March, the switch to DST
necessitates the averaging of the hour ending '01' data and the hour ending '03' data to create the hour ending '02'
data. In November, the return to Standard Time is handled by averaging the data for the two hour ending '02'
observations." So in those years the spring day's line 02 is not an hour and is not written, and the autumn day's
one line 02 is ISO-NE's average of two hours, neither of which is written: two hours a zone, market and year, 2019
to 2023, are missing and counted. The workbook's cells are cents held as binary fractions (49.410000000000004);
a value within a millionth of a cent figure is written as that figure.
CAISO and SPP give GMT on every line.
An hour a file does not hold is not written: nothing is filled, averaged across zones or estimated; --write counts
the missing hours of every market and zone. A zone hour a file gives twice is written once when its rows agree and
not at all when they differ.

WHAT THE PUBLISHERS DO NOT HOLD (found 7 October 2026). OASIS answers a month before late June 2023 with "No data
returned for the specified selection": it keeps about 39 months, so CAISO's day-ahead history starts there and grows
no further back. After three such months in a row the months before are not asked for, and a month OASIS has said it
keeps nothing of is not asked for again. NYISO's archive of the hourly real-time report for July 2026 holds 12 of
the month's 31 days (the 19th and the 21st to the 31st); the other days' own files answer HTTP 404.

A PUBLISHER THAT IS PAUSED (warehouse/metadata/paused_sources.csv) is never asked. HTTP 401 or 403, or a page where a
file was expected, stops that publisher's pull and is reported: no access control is worked around.

License. NYISO: public, with a caution (sessions 65, 85, 136): "Access to this Web site does not confer any license
or ownership interest in either the form or content of the Web site"; the notice forbids republishing "any image or
video on this website as a stand-alone file", not data (https://www.nyiso.com/legal-notice, read 6 October 2026).
CAISO: public: materials "may be used by you provided that you keep intact all copyright, trademark and other
proprietary notices and that you credit the California ISO when using such materials and/or information."
(https://www.caiso.com/privacy-terms-of-use, read 6 October 2026). SPP: public, with citation: "Permission is
implicitly granted to copy and distribute (via computer network or printed form) in whole or in part (with
appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication
... Any commercial use of these materials requires prior, express written authorization"
(https://www.spp.org/terms-conditions/, read 6 October 2026). ISO-NE: INTERNAL: "Any duplication of the Content or
non-personal use may violate copyright, trademark, and other laws." (https://www.iso-ne.com/legal-privacy, read
6 October 2026). The registry marks isone:smd_hourly_lmp internal; its rows are in isone_zone_prices_history only,
whose header says "License: internal", and no ISO-NE row is in iso_zone_prices_history.
"""

import argparse
import collections
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import re
import struct
import sys
import time
import traceback
import zipfile
import zlib

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import iso_prices as ip  # noqa: E402
import zone_load as zl  # noqa: E402

NAME = "iso_zone_prices_history"            # NYISO, CAISO, SPP: public sources
NAME_ISONE = "isone_zone_prices_history"    # ISO-NE: internal
TABLES = {NAME: ["nyiso_dam", "nyiso_rtm", "caiso_dam", "caiso_rtm", "spp_dam"], NAME_ISONE: ["isone_dam", "isone_rtm"]}
CONNECTOR = "zone_price_history"
START = "2019-01-01"
CEILING = 3_000_000
REFRESH_CEILING = 250_000     # the rows one weekly run (--recent) may read; its rows are not counted in the history pull's ceiling
REFRESH = False               # set by --recent
RUN = {"rows": 0}             # the rows of these series this run has read
RAW_ROOT = os.path.join(ip.ROOT, "warehouse", "raw", CONNECTOR)
UA = zl.UA
MANIFEST = ["retrieved_at", "status", "bytes", "sha256", "last_modified", "file", "url", "member", "market", "period",
            "series_rows", "file_rows", "note"]
PAUSE = {"nyiso": 2, "isone": 3, "caiso": 6, "spp": 1}
ISO_ORDER = ["nyiso", "isone", "caiso", "spp"]
NYISO_ZONES = ip.NYISO_ZONES
NYISO_URL = "http://mis.nyiso.com/public/csv/{kind}/{ym}01{kind}_zone_csv.zip"
NYISO_KIND = {"nyiso_dam": "damlbmp", "nyiso_rtm": "rtlbmp"}
ISONE_SHEETS = {"ME": ".Z.MAINE", "NH": ".Z.NEWHAMPSHIRE", "VT": ".Z.VERMONT", "CT": ".Z.CONNECTICUT", "RI": ".Z.RHODEISLAND",
                "SEMA": ".Z.SEMASS", "WCMA": ".Z.WCMASS", "NEMA": ".Z.NEMASSBOST"}
ISONE_COLUMNS = {"isone_dam": "DA_LMP", "isone_rtm": "RT_LMP"}
ISONE_LOAD_RAW = "isone_zone_load"       # the connector whose kept workbooks are reused
CAISO_NODE = "TH_ZP26_GEN-APND"
CAISO_URL = ("https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname={q}&version={v}&market_run_id={run}"
             "&node={node}&startdatetime={a}&enddatetime={b}")
CAISO_QUERY = {"caiso_dam": ("PRC_LMP", 12, "DAM"), "caiso_rtm": ("PRC_INTVL_LMP", 3, "RTM")}
CAISO_RTM_START = "2024-09-01"
SPP_HUB = "SPPSOUTH_HUB"
SPP_BASE = "https://portal.spp.org/file-browser-api/download/da-lmp-by-settlement-location?path="
TZ = {"nyiso": "America/New_York", "isone": "America/New_York", "caiso": "America/Los_Angeles", "spp": "America/Chicago"}
MARKETS = {  # market: (iso, variable, freq, source id)
    "nyiso_dam": ("nyiso", "lmp_dam", "PT1H", "nyiso:damlbmp"), "nyiso_rtm": ("nyiso", "lmp_rtm", "PT1H", "nyiso:rtlbmp"),
    "isone_dam": ("isone", "lmp_dam", "PT1H", "isone:smd_hourly_lmp"), "isone_rtm": ("isone", "lmp_rtm", "PT1H", "isone:smd_hourly_lmp"),
    "caiso_dam": ("caiso", "lmp_dam", "PT1H", "caiso:PRC_LMP"), "caiso_rtm": ("caiso", "lmp_rtm_15m_mean", "PT15M", "caiso:PRC_INTVL_LMP"),
    "spp_dam": ("spp", "lmp_dam", "PT1H", "spp:DA-LMP-SL"),
}
NYISO_TERMS = ("[terms: \"Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site\"; "
               "the notice forbids republishing \"any image or video on this website as a stand-alone file\", not data (https://www.nyiso.com/legal-notice, read 6 October 2026)]")
CAISO_TERMS = ("[terms: materials \"may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit "
               "the California ISO when using such materials and/or information.\" (https://www.caiso.com/privacy-terms-of-use, read 6 October 2026)]")
ISONE_TERMS = ("[terms: \"Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws.\" "
               "(https://www.iso-ne.com/legal-privacy, read 6 October 2026); held internal]")
SOURCES = {
    "nyiso:damlbmp": dict(publisher=ip.ISO_PUBLISHERS["nyiso"], report="Day-Ahead Market LBMP, zonal (P-2A)", report_url="http://mis.nyiso.com/public/P-2Alist.htm",
                          document_list="", license="public"),
    "nyiso:rtlbmp": dict(publisher=ip.ISO_PUBLISHERS["nyiso"], report="Time-Weighted/Integrated Real-Time LBMP, zonal, hourly (P-4A) " + NYISO_TERMS,
                         report_url="http://mis.nyiso.com/public/P-4Alist.htm", document_list=NYISO_URL.format(kind="rtlbmp", ym="<YYYYMM>"), license="public"),
    "isone:smd_hourly_lmp": dict(publisher=ip.ISO_PUBLISHERS["isone"], report="Zonal Information, SMD Hourly Data (yearly workbook), day-ahead and real-time LMP by load zone " + ISONE_TERMS,
                                 report_url="https://www.iso-ne.com/isoexpress/web/reports/load-and-demand/-/tree/zone-info",
                                 document_list="https://www.iso-ne.com/static-assets/documents/<folder>/<YYYY>_smd_hourly.xlsx", license="internal"),
    "caiso:PRC_LMP": dict(publisher=ip.ISO_PUBLISHERS["caiso"], report="OASIS Locational Marginal Prices, day-ahead market (DAM)", report_url=ip.CAISO_OASIS,
                          document_list="", license="public"),
    "caiso:PRC_INTVL_LMP": dict(publisher=ip.ISO_PUBLISHERS["caiso"], report="OASIS Interval Locational Marginal Prices, real-time dispatch (RTD, 5-minute)",
                                report_url=ip.CAISO_OASIS, document_list="", license="public"),
    "spp:DA-LMP-SL": dict(publisher=ip.ISO_PUBLISHERS["spp"], report="Day-Ahead LMP by Settlement Location", report_url=ip.SPP_DAM_PAGE, document_list="", license="public"),
}
SKIPPED = collections.Counter()      # lines read and not written, by reason (the write stage reports them)


class Blocked(RuntimeError):
    """The publisher refused (401, 403) or answered a page where a file was expected: its pull stops, nothing is worked around."""


class CeilingStop(RuntimeError):
    """The next request would pass the ceiling: it is not made."""


def http_get(url, headers=None, timeout=300):
    """One request. The tests replace this function; nothing else in this file reaches the network."""
    import requests
    return requests.get(url, headers=headers, timeout=timeout)


# ---------------------------------------------------------------------------
# The saved files and their manifest
# ---------------------------------------------------------------------------


def manifest_path(iso):
    return os.path.join(RAW_ROOT, iso, "manifest.csv")


def manifest(iso):
    path = manifest_path(iso)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def record(iso, **row):
    os.makedirs(os.path.join(RAW_ROOT, iso), exist_ok=True)
    path = manifest_path(iso)
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(MANIFEST)
        if REFRESH:
            row["note"] = ("refresh; " + str(row.get("note", ""))).strip("; ")
        w.writerow([str(row.get(c, "")) for c in MANIFEST])
    RUN["rows"] += int(row.get("series_rows") or 0)


def path_of(iso, row):
    """A manifest row's file: under this connector's raw folder, or (a workbook reused from another connector's raw
    files) a path from the repository's root."""
    f = row["file"]
    return os.path.join(ip.ROOT, f) if f.startswith("warehouse/") else os.path.join(RAW_ROOT, iso, f)


def held(iso):
    """{(market, period): the newest manifest row with HTTP 200 whose file is on this machine}."""
    out = {}
    for r in manifest(iso):
        if r["status"] == "200" and r["file"] and os.path.exists(path_of(iso, r)):
            out[(r["market"], r["period"])] = r
    return out


def counted():
    """(rows of these series read, rows in the files read, requests, bytes) by the history pull, every run and every
    publisher, probes included. The weekly runs (--recent) have a ceiling of their own a run and are not counted here."""
    series = files = requests_ = size = 0
    for iso in ISO_ORDER:
        for r in manifest(iso):
            if r["note"].startswith("refresh"):
                continue
            series += int(r["series_rows"] or 0)
            files += int(r["file_rows"] or 0)
            if r["note"].startswith("reused"):
                continue
            requests_ += 1
            size += int(r["bytes"] or 0)
    probes = os.path.join(RAW_ROOT, "probes.csv")
    if os.path.exists(probes):
        with open(probes, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                series += int(r["series_rows"] or 0)
                files += int(r["file_rows"] or 0)
                requests_ += int(r.get("requests") or 1)
                size += int(r["bytes"] or 0)
    return series, files, requests_, size


def room(est):
    if REFRESH:
        return RUN["rows"] + int(est) <= REFRESH_CEILING
    return counted()[0] + int(est) <= CEILING


def now_utc():
    return pd.Timestamp.now(tz="UTC")


def stamp(ts):
    return pd.Timestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Parsers: saved bytes to {market: rows of entity, node, ts (UTC), value}, the lines of these series, the lines in the file
# ---------------------------------------------------------------------------


def place(local, names, tz):
    """Naive local interval starts, one a line, as UTC. The hour the autumn clock repeats is placed by its order within
    a node: the first is daylight time, the second standard time; held once it could be either and is NaT. A clock
    time the spring day never had is NaT."""
    idx = pd.DatetimeIndex(pd.to_datetime(np.asarray(local)))
    k = pd.DataFrame({"n": np.asarray(names), "t": idx})
    occ = k.groupby(["n", "t"]).cumcount().values
    size = k.groupby(["n", "t"])["t"].transform("size").values
    first = np.asarray(idx.tz_localize(tz, ambiguous=True, nonexistent="NaT").tz_convert("UTC").tz_localize(None), dtype="datetime64[ns]")
    plain = np.asarray(idx.tz_localize(tz, ambiguous="NaT", nonexistent="NaT").isna())
    repeated = plain & ~np.isnat(first)
    ts = np.asarray(idx.tz_localize(tz, ambiguous=(occ == 0), nonexistent="NaT").tz_convert("UTC").tz_localize(None), dtype="datetime64[ns]").copy()
    ts[repeated & (size == 1)] = np.datetime64("NaT")
    return pd.DatetimeIndex(ts).tz_localize("UTC")


def parse_nyiso_day(text, market):
    """One day's zonal LBMP CSV (day-ahead P-2A or the hourly integrated real-time P-4A): the eleven zones' lines on the hour."""
    df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    need = ["Time Stamp", "Name", "LBMP ($/MWHr)"]
    if not set(need) <= set(df.columns):
        raise RuntimeError(f"columns {list(df.columns)}, expected {need}")
    n = len(df)
    df = df[df["Name"].str.strip().isin(NYISO_ZONES)]
    zone = df["Name"].str.strip()
    raw = df["Time Stamp"].str.strip()
    local = pd.to_datetime(raw, format="%m/%d/%Y %H:%M:%S" if raw.str.len().max() > 16 else "%m/%d/%Y %H:%M")
    ts = place(local, zone, TZ["nyiso"])
    v = pd.to_numeric(df["LBMP ($/MWHr)"], errors="coerce")
    on_hour = ((local.dt.minute == 0) & (local.dt.second == 0)).values
    keep = on_hour & v.notna().values & ~ts.isna()
    piece = pd.DataFrame({"entity": ("nyiso:" + zone).values[keep], "node": zone.values[keep], "ts": ts[keep], "value": v.values[keep]})
    return piece, len(df), n


def parse_nyiso(content, market):
    z = zipfile.ZipFile(io.BytesIO(content))
    pieces, k, n = [], 0, 0
    for name in sorted(z.namelist()):
        if name.lower().endswith(".csv"):
            p, a, b = parse_nyiso_day(z.read(name).decode("utf-8", "replace"), market)
            pieces.append(p)
            k += a
            n += b
    piece = pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame(columns=zl.PIECE)
    return {market: piece}, k, n


def parse_isone_sheet(df, sheet):
    """One load zone's sheet of the SMD hourly workbook as {market: rows} (the hour as isone_zone_load.py places it)."""
    df = df.rename(columns={c: str(c).strip() for c in df.columns})
    need = ["Date", "Hr_End"] + list(ISONE_COLUMNS.values())
    if not set(need) <= set(df.columns):
        raise RuntimeError(f"sheet {sheet!r} has columns {list(df.columns)[:14]}, expected {need}")
    df = df[df["Date"].notna()]
    he = df["Hr_End"].astype(str).str.strip().str.upper().str.replace(r"\.0$", "", regex=True)
    second = he.str.endswith("X").values
    hour = pd.to_numeric(he.str.rstrip("X"), errors="coerce")
    if hour.isna().any() or not hour.between(1, 24).all():
        raise RuntimeError(f"sheet {sheet!r}: hour ending {sorted(set(he[hour.isna() | ~hour.between(1, 24)]))[:5]} is not 1 to 24")
    local = pd.to_datetime(df["Date"]).dt.normalize() + pd.to_timedelta(hour.astype(int) - 1, unit="h")
    idx = pd.DatetimeIndex(local)
    # the spring day of the workbooks of 2019 to 2023 has 24 lines: the line "03" is the real hour (it began at 01:00
    # standard time) and the line "02" is ISO-NE's average of the lines "01" and "03" (the workbook's Notes), an hour
    # that day never had. Where a day holds the line "03" of a spring change, its line "02" is not an hour.
    never = np.asarray(idx.tz_localize(TZ["isone"], ambiguous=True, nonexistent="NaT").isna())
    made = np.asarray(idx.isin(idx[never] - pd.Timedelta(hours=1)))
    ts, _ = zl.to_utc(local, TZ["isone"], second=second)
    ts = pd.DatetimeIndex(pd.to_datetime(ts.values, utc=True))
    SKIPPED["isone: the spring day's line 02, ISO-NE's average of the lines 01 and 03, not an hour"] += int(made.sum())
    SKIPPED["isone: the autumn day's one line 02, ISO-NE's average of the two hours from 01:00, neither hour"] += int((ts.isna() & ~made).sum())
    out = {}
    for market, col in ISONE_COLUMNS.items():
        v = pd.to_numeric(df[col], errors="coerce").values
        cents = np.round(v, 2)
        v = np.where(np.abs(v - cents) < 1e-6, cents, v)      # the workbook's cells are cents held as binary fractions (49.410000000000004)
        keep = ~ts.isna() & ~np.isnan(v) & ~made
        out[market] = pd.DataFrame({"entity": "isone:" + ISONE_SHEETS[sheet], "node": ISONE_SHEETS[sheet], "ts": ts[keep], "value": v[keep]})
    return out, len(df)


def parse_isone(content, market=None):
    """A year's workbook: the eight load zones' sheets, one sheet in memory at a time. The lines of the other sheets
    (the control area's) are not read; file_rows counts the nine data sheets' lines by the workbook's own dimensions."""
    xf = pd.ExcelFile(io.BytesIO(content))
    names = {str(s).strip().upper(): s for s in xf.sheet_names}
    missing = [s for s in ISONE_SHEETS if s not in names]
    if missing:
        raise RuntimeError(f"the workbook's sheets are {xf.sheet_names}, expected {list(ISONE_SHEETS)}")
    parts, k = {m: [] for m in ISONE_COLUMNS}, 0
    for sheet in ISONE_SHEETS:
        got, n = parse_isone_sheet(xf.parse(names[sheet], header=0), sheet)
        k += n
        for m, p in got.items():
            parts[m].append(p)
    xf.close()
    extra = k // len(ISONE_SHEETS) if "ISO NE CA" in names else 0
    return {m: pd.concat(p, ignore_index=True) for m, p in parts.items()}, 2 * k, k + extra


def caiso_error(content):
    """OASIS answers a request it will not serve with a zip holding one XML naming the error: its text, or ""."""
    if content[:2] != b"PK":
        return content[:300].decode("utf-8", "replace")
    z = zipfile.ZipFile(io.BytesIO(content))
    for name in z.namelist():
        if name.lower().endswith(".xml"):
            text = z.read(name).decode("utf-8", "replace")
            code = re.search(r"<m:ERR_CODE>(.*?)</m:ERR_CODE>", text)
            desc = re.search(r"<m:ERR_DESC>(.*?)</m:ERR_DESC>", text)
            return f"{code.group(1) if code else ''} {desc.group(1) if desc else text[:200]}".strip()
    return ""


def parse_caiso(content, market):
    """An OASIS zip (PRC_LMP or PRC_INTVL_LMP, one node): the lines whose LMP_TYPE is LMP. Real time: the 5-minute
    prices as 15-minute means, a quarter hour only when its three prices are held (iso_prices.to_15min_means's rule)."""
    z = zipfile.ZipFile(io.BytesIO(content))
    frames = [pd.read_csv(io.BytesIO(z.read(n)), dtype=str, keep_default_na=False) for n in sorted(z.namelist()) if n.lower().endswith(".csv")]
    if not frames:
        raise RuntimeError(f"no CSV in the zip: {caiso_error(content) or z.namelist()}")
    df = pd.concat(frames, ignore_index=True)
    n = len(df)
    col = next((c for c in ("MW", "VALUE", "PRC") if c in df.columns), None)
    need = ["INTERVALSTARTTIME_GMT", "INTERVALENDTIME_GMT", "NODE", "LMP_TYPE"]
    if col is None or not set(need) <= set(df.columns):
        raise RuntimeError(f"columns {list(df.columns)}, expected {need} and MW")
    df = df[(df["LMP_TYPE"] == "LMP") & (df["NODE"] == CAISO_NODE)]
    a = pd.to_datetime(df["INTERVALSTARTTIME_GMT"], utc=True)
    b = pd.to_datetime(df["INTERVALENDTIME_GMT"], utc=True)
    v = pd.to_numeric(df[col], errors="coerce")
    minutes = ((b - a).dt.total_seconds() / 60).round().astype("Int64")
    want = 60 if market == "caiso_dam" else 5
    if len(df) and not (minutes == want).all():
        raise RuntimeError(f"{int((minutes != want).sum())} lines are not {want}-minute intervals")
    p = pd.DataFrame({"ts": a.values, "value": v.values})
    p = p[p["value"].notna()].drop_duplicates()
    if market == "caiso_rtm":
        p = p.drop_duplicates("ts", keep=False)                     # a 5-minute interval given twice with two prices: not used
        g = p.groupby(p["ts"].dt.floor("15min"))["value"]
        q = g.mean()[g.size() == 3].round(ip.MEAN_DECIMALS)
        p = pd.DataFrame({"ts": q.index, "value": q.values})
    ts = pd.DatetimeIndex(p["ts"])
    piece = pd.DataFrame({"entity": "caiso:" + CAISO_NODE, "node": CAISO_NODE, "ts": ts.tz_localize("UTC") if ts.tz is None else ts.tz_convert("UTC"), "value": p["value"].values})
    return {market: piece}, len(df), n


def parse_spp(content, market):
    """A day's DA-LMP-SL file (plain or gzip): the hub's lines. GMTIntervalEnd is the hour's end in GMT. SPP names
    the columns in two ways (Settlement Location in the files from 5 June 2026 and in the archive of 2024,
    SETTLEMENT_LOCATION in the files to 4 June 2026): the names are read without case, space or underscore."""
    if content[:2] == b"\x1f\x8b":
        content = gzip.decompress(content)
    df = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    df.columns = [re.sub(r"[ _]", "", c).upper() for c in df.columns]
    need = ["GMTINTERVALEND", "SETTLEMENTLOCATION", "LMP"]
    if not set(need) <= set(df.columns):
        raise RuntimeError(f"columns {list(df.columns)}, expected {need}")
    n = len(df)
    df = df[df["SETTLEMENTLOCATION"].str.strip() == SPP_HUB]
    stamps = df["GMTINTERVALEND"].str.strip()
    fmt = "%m/%d/%Y %H:%M:%S" if (stamps.str.count(":") == 2).all() else "%m/%d/%Y %H:%M"      # "09/01/2026 06:00:00" or "6/4/2026 6:00"
    end = pd.to_datetime(stamps, format=fmt).dt.tz_localize("UTC")
    v = pd.to_numeric(df["LMP"], errors="coerce")
    keep = v.notna().values
    piece = pd.DataFrame({"entity": "spp:" + SPP_HUB, "node": SPP_HUB, "ts": (end - pd.Timedelta(hours=1)).values[keep], "value": v.values[keep]})
    piece["ts"] = pd.to_datetime(piece["ts"], utc=True)
    return {market: piece}, len(df), n


PARSERS = {"nyiso": parse_nyiso, "isone": parse_isone, "caiso": parse_caiso, "spp": parse_spp}


def count_rows(iso, market, content):
    """(the lines of these series, the lines in the file) of a file just received; ("", "") when it cannot be read
    (the file is kept and --write will say why)."""
    try:
        _, k, n = PARSERS[iso](content, market)
        return k, n
    except Exception:
        return "", ""


# ---------------------------------------------------------------------------
# The pull: what to ask for, one request at a time
# ---------------------------------------------------------------------------


def final(row, period_end):
    """A kept file is final when it was fetched three days or more after its period ended."""
    return pd.Timestamp(row["retrieved_at"]) >= period_end + pd.Timedelta(days=3)


def due(kept, period_end, today):
    """Whether a period is asked for: no file kept, or the kept file was fetched before the period had ended and is
    more than 20 hours old."""
    if kept is None:
        return True
    if final(kept, period_end):
        return False
    return now_utc() - pd.Timestamp(kept["retrieved_at"]) > pd.Timedelta(hours=20)


def months(first, today):
    return list(reversed(pd.date_range(pd.Timestamp(first).replace(day=1), today, freq="MS")))


def save(iso, name, body, market, period, url, r_headers, member="", note="", stored=None, status="200"):
    """Write the file and its manifest row; the rows are counted from what was received."""
    os.makedirs(os.path.join(RAW_ROOT, iso), exist_ok=True)
    data = body if stored is None else stored
    k, n = count_rows(iso, market, data) if status == "200" else ("", "")
    with open(os.path.join(RAW_ROOT, iso, name), "wb") as f:
        f.write(data)
    record(iso, retrieved_at=stamp(now_utc()), status=status, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
           last_modified=(r_headers or {}).get("Last-Modified", "") or "", file=name, url=url, member=member, market=market, period=period,
           series_rows=k, file_rows=n, note=note)
    return k, n


def get(iso, url, log, headers=None, tries=3):
    """One document: its response. 404 is the publisher saying it is not there (returned, not retried); 401 and 403
    stop the publisher's pull; another failure is tried again, then raised."""
    last = None
    for i in range(tries):
        try:
            r = http_get(url, headers=dict(UA, **(headers or {})))
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
            log(f"  {url}: {last}; try {i + 1} of {tries}")
            time.sleep(10 * (i + 1))
            continue
        if r.status_code in (401, 403):
            raise Blocked(f"HTTP {r.status_code} for {url}")
        if r.status_code in (200, 206, 404):
            return r
        last = f"HTTP {r.status_code}"
        log(f"  {url}: {last}; try {i + 1} of {tries}")
        time.sleep(15 * (i + 1))
    raise RuntimeError(f"{url}: {last}")


def ask(est, what):
    if not room(est):
        read, top = (RUN["rows"], REFRESH_CEILING) if REFRESH else (counted()[0], CEILING)
        raise CeilingStop(f"stopped before {what}: {read:,} rows read and {est:,} more would pass the ceiling of {top:,}")


def pull_nyiso(log, first, today, limit):
    done, kept = 0, held("nyiso")
    for market, kind in NYISO_KIND.items():
        for m in months(max(first, pd.Timestamp(START)), today):
            period, end = m.strftime("%Y-%m"), (m + pd.offsets.MonthBegin(1)).tz_localize(TZ["nyiso"]).tz_convert("UTC")
            if not due(kept.get((market, period)), end, today):
                continue
            if done >= limit:
                return done
            ask(31 * 25 * len(NYISO_ZONES), f"NYISO {market} {period}")
            url = NYISO_URL.format(kind=kind, ym=m.strftime("%Y%m"))
            r = get("nyiso", url, log)
            done += 1
            if r.status_code == 404:
                record("nyiso", retrieved_at=stamp(now_utc()), status="404", bytes=0, url=url, market=market, period=period, note="no monthly file at NYISO")
                log(f"  nyiso {market} {period}: HTTP 404, no monthly file")
            elif r.content[:2] != b"PK":
                raise Blocked(f"{url} did not answer a zip (first bytes {r.content[:60]!r})")
            else:
                k, n = save("nyiso", f"{m:%Y%m}01{kind}_zone_csv.zip", r.content, market, period, url, r.headers)
                log(f"  nyiso {market} {period}: {len(r.content):,} bytes, {k} lines of the zones, {n} in the file")
            time.sleep(PAUSE["nyiso"])
    return done


def isone_load_copies():
    """{year: (address, retrieved_at, path from the repository's root)}: the newest SMD hourly workbook of each year in
    the raw files isone_zone_load.py keeps."""
    import glob
    import isone_zone_load as izl
    out = {}
    for man in sorted(glob.glob(os.path.join(ip.ROOT, "warehouse", "raw", ISONE_LOAD_RAW, "*", "manifest.csv"))):
        with open(man, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                m = izl.FILE.match(r["url"].replace(izl.HOST, ""))
                path = os.path.join(os.path.dirname(man), r["file"])
                if m and r["status"] == "200" and os.path.exists(path):
                    y = int(m.group(1))
                    if y not in out or r["retrieved_at"] > out[y][1]:
                        out[y] = (r["url"], r["retrieved_at"], os.path.relpath(path, ip.ROOT).replace(os.sep, "/"), r["sha256"], r["bytes"], r["last_modified"])
    return out


def pull_isone(log, first, today, limit):
    import isone_zone_load as izl
    done, kept, copies, files = 0, held("isone"), isone_load_copies(), None
    est = 2 * 8784 * len(ISONE_SHEETS)
    for year in range(today.year, max(first, pd.Timestamp(START)).year - 1, -1):
        period = str(year)
        mine = kept.get(("isone_dam", period))
        theirs = copies.get(year)
        if theirs and (mine is None or theirs[1] > mine["retrieved_at"]):
            ask(est, f"ISO-NE {year} (a workbook isone_zone_load.py keeps)")
            url, when, rel, sha, size, lm = theirs
            with open(os.path.join(ip.ROOT, rel), "rb") as f:
                k, n = count_rows("isone", "isone_dam", f.read())
            record("isone", retrieved_at=when, status="200", bytes=size, sha256=sha, last_modified=lm, file=rel, url=url, market="isone_dam", period=period,
                   series_rows=k, file_rows=n, note="reused from isone_zone_load's raw files, not requested")
            log(f"  isone {year}: the workbook isone_zone_load.py fetched {when} is reused ({rel}); {k} lines of the zones' two prices")
            continue
        end = pd.Timestamp(f"{year + 1}-01-01", tz=TZ["isone"]).tz_convert("UTC")
        if mine is not None and (final(mine, end) or year == today.year):
            continue                       # the current year grows through isone_zone_load.py's weekly run, never asked for twice
        if mine is not None:
            continue
        if done >= limit:
            return done
        if files is None:
            texts = []
            for i in range(izl.LIST_PAGES):
                u = izl.LIST.format(i * izl.LIST_STEP)
                r = get("isone", u, log)
                if r.status_code != 200:
                    raise Blocked(f"HTTP {r.status_code} for ISO-NE's file list {u}")
                texts.append(r.content.decode("utf-8", "replace"))
                os.makedirs(os.path.join(RAW_ROOT, "isone"), exist_ok=True)
                name = f"list_{stamp(now_utc()).replace(':', '')}_{i}.json"
                with open(os.path.join(RAW_ROOT, "isone", name), "wb") as f:
                    f.write(r.content)
                record("isone", retrieved_at=stamp(now_utc()), status="200", bytes=len(r.content), sha256=hashlib.sha256(r.content).hexdigest(), file=name, url=u,
                       market="list", period=str(i), series_rows=0, file_rows=0, note="ISO-NE's file list")
                time.sleep(PAUSE["isone"])
                try:
                    if len(json.loads(texts[-1]).get("data", [])) < izl.LIST_STEP:
                        break
                except ValueError:
                    raise Blocked(f"ISO-NE's file list {u} is not JSON (first bytes {r.content[:60]!r})")
            files = izl.listed(texts)
            log(f"  ISO-NE's list holds SMD hourly workbooks for {sorted(files)}")
        if year not in files:
            log(f"  isone {year}: ISO-NE's list holds no SMD hourly workbook")
            record("isone", retrieved_at=stamp(now_utc()), status="not listed", bytes=0, url=izl.PAGE, market="isone_dam", period=period, note="no SMD hourly workbook on ISO-NE's list")
            continue
        ask(est, f"ISO-NE {year}")
        url = files[year][0]
        r = get("isone", url, log)
        done += 1
        if r.status_code == 404:
            record("isone", retrieved_at=stamp(now_utc()), status="404", bytes=0, url=url, market="isone_dam", period=period, note="listed, not served")
            log(f"  isone {year}: HTTP 404")
        elif r.content[:2] != b"PK":
            raise Blocked(f"{url} did not answer a workbook (first bytes {r.content[:60]!r})")
        else:
            k, n = save("isone", f"{year}_smd_hourly.xlsx", r.content, "isone_dam", period, url, r.headers)
            log(f"  isone {year}: {len(r.content):,} bytes, {k} lines of the zones' two prices, {n} lines in the sheets")
        time.sleep(PAUSE["isone"])
    return done


def pull_caiso(log, first, today, limit):
    done, kept, tz = 0, held("caiso"), TZ["caiso"]
    nothing = {(r["market"], r["period"]) for r in manifest("caiso") if r["status"] == "refused" and "No data returned" in r["note"]}
    local_today = pd.Timestamp.now(tz=tz).normalize()
    for market, (q, v, run) in CAISO_QUERY.items():
        start = max(first, pd.Timestamp(START if market == "caiso_dam" else CAISO_RTM_START))
        last = local_today + pd.Timedelta(days=1) if market == "caiso_dam" else local_today      # day-ahead: today's hours are out
        empty = 0
        for m in months(start, today):
            if empty >= 3:
                log(f"  caiso {market}: three months in a row answered with no data; OASIS keeps nothing earlier and the months before {m:%Y-%m} are not asked for")
                break
            if (market, m.strftime("%Y-%m")) in nothing and m < today - pd.Timedelta(days=60):
                continue                                   # OASIS already said it keeps nothing of this month
            a = max(m, start.normalize()).tz_localize(tz)
            b = min((m + pd.offsets.MonthBegin(1)).tz_localize(tz), last)
            if b <= a:
                continue
            period = m.strftime("%Y-%m")
            if not due(kept.get((market, period)), (m + pd.offsets.MonthBegin(1)).tz_localize(tz).tz_convert("UTC"), today):
                continue
            if done >= limit:
                return done
            hours = int((b - a) / pd.Timedelta(hours=1))
            ask(hours if market == "caiso_dam" else hours * 12, f"CAISO {market} {period}")
            url = CAISO_URL.format(q=q, v=v, run=run, node=CAISO_NODE, a=a.tz_convert("UTC").strftime("%Y%m%dT%H:%M-0000"), b=b.tz_convert("UTC").strftime("%Y%m%dT%H:%M-0000"))
            r = get("caiso", url, log)
            done += 1
            name = f"{q}_{run}_{a:%Y%m%d}_{b:%Y%m%d}.zip"
            err = caiso_error(r.content) if r.status_code == 200 else f"HTTP {r.status_code}"
            if err:
                save("caiso", name, r.content, market, period, url, r.headers, status="refused", note=err[:300])
                log(f"  caiso {market} {period}: OASIS did not serve it: {err[:300]}")
                empty = empty + 1 if "No data returned" in err else 0
            else:
                empty = 0
                k, n = save("caiso", name, r.content, market, period, url, r.headers)
                log(f"  caiso {market} {period}: {len(r.content):,} bytes, {k} lines of {CAISO_NODE}'s LMP, {n} in the file")
            time.sleep(PAUSE["caiso"])
    return done


_SPP_DIR = {}


def spp_directory(year, log):
    """SPP's archive of a finished year: {member: (header offset, compressed size, method, CRC, size)}, or None when
    SPP holds no archive of it (HTTP 404). Read once by range requests (hub_history's reader) and kept beside the files."""
    if year in _SPP_DIR:
        return _SPP_DIR[year]
    path = os.path.join(RAW_ROOT, "spp", f"archive_{year}_directory.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            _SPP_DIR[year] = json.load(f)["members"]
        return _SPP_DIR[year]
    url = f"{SPP_BASE}/{year}/{year}.zip"
    r = get("spp", url, log, headers={"Range": "bytes=0-0"})
    if r.status_code != 206:
        log(f"  spp: no archive of {year} (HTTP {r.status_code}); its days are asked for one file a day")
        _SPP_DIR[year] = None
        return None
    import hub_history as hh
    z = zipfile.ZipFile(io.BufferedReader(hh._RawAdapter(hh._Remote(url)), buffer_size=1 << 20))
    members = {i.filename: [i.header_offset, i.compress_size, i.compress_type, i.CRC, i.file_size] for i in z.infolist()}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"url": url, "retrieved_at": stamp(now_utc()), "members": members}, f)
    log(f"  spp: the archive of {year} lists {len(members)} members")
    _SPP_DIR[year] = members
    return members


def spp_member(url, info, log):
    """One member of SPP's yearly archive by one range request: (the compressed bytes received, the same file as gzip)."""
    off, csize, method, crc, size = info
    r = get("spp", url, log, headers={"Range": f"bytes={off}-{off + 30 + 512 + csize - 1}"})
    if r.status_code != 206:
        raise RuntimeError(f"{url}: range read HTTP {r.status_code}")
    head = r.content[:30]
    if head[:4] != b"PK\x03\x04":
        raise RuntimeError(f"{url}: no member at offset {off}")
    n, m = struct.unpack("<HH", head[26:30])
    data = r.content[30 + n + m:30 + n + m + csize]
    if len(data) != csize:
        raise RuntimeError(f"{url}: {len(data)} of {csize} bytes")
    if method == zipfile.ZIP_DEFLATED:
        if zlib.crc32(zlib.decompress(data, -15)) != crc:
            raise RuntimeError(f"{url}: CRC mismatch")
        gz = b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff" + data + struct.pack("<II", crc, size & 0xFFFFFFFF)
    else:
        gz = gzip.compress(data)
    return data, gz, r.headers


def pull_spp(log, first, today, limit):
    done, kept, tz = 0, held("spp"), TZ["spp"]
    now = pd.Timestamp.now(tz=tz).normalize().tz_localize(None)
    last = min(now, today)                                               # today's file: the day-ahead market cleared yesterday
    days = pd.date_range(max(first, pd.Timestamp(START)), last, freq="D")
    for day in reversed(days):
        period = day.strftime("%Y-%m-%d")
        if ("spp_dam", period) in kept:
            continue
        if done >= limit:
            return done
        ask(25, f"SPP spp_dam {period}")
        member = f"{day:%Y}/{day:%m}/By_Day/DA-LMP-SL-{day:%Y%m%d}0100.csv"
        name = f"DA-LMP-SL-{day:%Y%m%d}0100.csv.gz"
        directory = spp_directory(day.year, log) if day.year < now.year else None     # a finished year may have its archive
        done += 1
        if directory is not None:
            url = f"{SPP_BASE}/{day.year}/{day.year}.zip"
            if member not in directory:
                record("spp", retrieved_at=stamp(now_utc()), status="not in archive", bytes=0, url=url, member=member, market="spp_dam", period=period,
                       note="SPP's archive of the year holds no file of the day")
                log(f"  spp {period}: not in SPP's archive of {day.year}")
                continue
            body, gz, hdr = spp_member(url, directory[member], log)
            k, n = save("spp", name, body, "spp_dam", period, url, hdr, member=member, stored=gz,
                        note="the member's compressed bytes, by range; kept as gzip")
        else:
            url = f"{SPP_BASE}/{member}"
            r = get("spp", url, log)
            if r.status_code == 404:
                record("spp", retrieved_at=stamp(now_utc()), status="404", bytes=0, url=url, market="spp_dam", period=period, note="no daily file at SPP")
                log(f"  spp {period}: HTTP 404, no daily file")
                time.sleep(PAUSE["spp"])
                continue
            if r.content[:9].upper() != b"INTERVAL,":
                raise Blocked(f"{url} did not answer the file (first bytes {r.content[:60]!r})")
            k, n = save("spp", name, r.content, "spp_dam", period, url, r.headers, stored=gzip.compress(r.content, 6), note="kept as gzip")
        log(f"  spp {period}: {k} lines of {SPP_HUB}, {n} in the file")
        time.sleep(PAUSE["spp"])
    return done


PULLS = {"nyiso": pull_nyiso, "isone": pull_isone, "caiso": pull_caiso, "spp": pull_spp}


def pull(isos, first=None, limit=10 ** 9, log=print, until=None):
    """The pull stage. Returns {iso: outcome}. until: the last day asked for (default today)."""
    first = pd.Timestamp(first or START)
    today = pd.Timestamp(until) if until else pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
    out = {}
    for iso in isos:
        held_ = ip.paused(iso)
        if held_:
            log(f"{iso} {ip.pause_line(iso)}")
            out[iso] = "paused: no request made"
            continue
        try:
            n = PULLS[iso](log, first, today, limit)
            out[iso] = f"ok: {n} requests"
        except CeilingStop as exc:
            log(f"STOP {exc}")
            out[iso] = f"ceiling: {exc}"
            break
        except Blocked as exc:
            log(f"{iso} BLOCKED, its pull stops and nothing is worked around: {exc}")
            out[iso] = f"blocked: {exc}"
        except Exception:
            last = traceback.format_exc().strip().splitlines()[-1]
            log(f"{iso} FAILED: {last}")
            out[iso] = f"failed: {last}"
        s, f, r, b = counted()
        log(f"after {iso}: {s:,} rows of these series read against the ceiling of {CEILING:,}; {f:,} rows in the files read; {r:,} requests, {b:,} bytes")
    return out


# ---------------------------------------------------------------------------
# The table, from the saved files only
# ---------------------------------------------------------------------------


def once(piece):
    """A zone's hour given twice: kept once when the rows agree, not at all when they differ. (rows, hours dropped)."""
    dup = piece.duplicated(["entity", "ts"], keep=False)
    if not dup.any():
        return piece, 0
    nun = piece[dup].groupby(["entity", "ts"])["value"].transform("nunique")
    differ = dup.copy()
    differ[dup] = (nun > 1).values
    n = int(piece[differ][["entity", "ts"]].drop_duplicates().shape[0])
    return piece[~differ].drop_duplicates(["entity", "ts"]), n


def series(piece, market, row, geo):
    iso, variable, freq, source = MARKETS[market]
    return pd.DataFrame({
        "entity": piece["entity"].values, "variable": variable, "ts_utc": pd.DatetimeIndex(piece["ts"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value": piece["value"].astype(float).values, "unit": "USD/MWh", "freq": freq, "geo": geo, "market": market, "node": piece["node"].values,
        "source": source, "source_url": row["url"], "retrieved_at": row["retrieved_at"], "vintage": ip.vintage_of({"last_modified": row["last_modified"]})},
        columns=ip.SERIES_COLS)


def build(isos, log, since=None):
    """{market: the rows of the saved files}, and notes on what could not be read or placed. since: only the files
    fetched from that moment on (the weekly run)."""
    parts, notes = {}, []
    SKIPPED.clear()
    for iso in isos:
        geo = ip.ISOS[iso][3]
        rows = sorted((k, r) for k, r in held(iso).items() if since is None or r["retrieved_at"] >= since)
        log(f"{iso}: {len(rows)} saved files")
        for (market, period), row in rows:
            if market == "list":
                continue
            try:
                with open(path_of(iso, row), "rb") as f:
                    got, _, _ = PARSERS[iso](f.read(), market)
            except Exception as exc:
                notes.append(f"{iso} {market} {period}: the saved file could not be read and gives no row ({type(exc).__name__}: {' '.join(str(exc).split())[:200]})")
                log("  " + notes[-1])
                continue
            for m, piece in got.items():
                piece, differ = once(piece)
                if differ:
                    notes.append(f"{m} {period}: {differ} zone hours the file gives twice with different prices are not written")
                    log("  " + notes[-1])
                if len(piece):
                    parts.setdefault(m, []).append(series(piece, m, row, geo))
    out = {}
    for m, frames in parts.items():
        s = pd.concat(frames, ignore_index=True)
        s = s.sort_values("retrieved_at", kind="stable").drop_duplicates(ip.SERIES_KEY, keep="last")     # two files may hold the same hour: the newer file
        out[m] = s.sort_values(ip.SERIES_KEY).reset_index(drop=True)
    for why, n in sorted(SKIPPED.items()):
        if n:
            notes.append(f"{n:,} lines read and not written ({why}); each stood for both of the workbook's prices")
            log("  " + notes[-1])
    return out, notes


def gaps(s, market):
    """Per entity: (rows, first, last, the hours or quarter hours missing between its first and last)."""
    step = "15min" if MARKETS[market][2] == "PT15M" else "1h"
    out = {}
    for e, g in s.groupby("entity"):
        t = pd.to_datetime(g["ts_utc"], utc=True)
        want = pd.date_range(t.min(), t.max(), freq=step)
        out[e] = (len(g), g["ts_utc"].min(), g["ts_utc"].max(), len(want.difference(pd.DatetimeIndex(t))))
    return out


def write_table(name, parts, header, log):
    """_write_table, leaving no working file behind when it fails: the table held stays as it was."""
    import glob
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    try:
        return _write_table(name, parts, header, log)
    except Exception:
        for p in glob.glob(glob.escape(path) + ".*.part") + [path + ".body", path + ".tmp"]:
            if os.path.exists(p):
                os.remove(p)
        raise


def _write_table(name, parts, header, log):
    """Merge the new rows into the table `name`, a market at a time (the table is too large to hold whole in an 8 GB
    machine): a new row replaces the held row of the same (entity, variable, ts_utc), every other held row is kept.
    header: a function of {market: (rows, first, last)} of the merged table, so a run that writes one publisher or
    one week still heads the table with every market and source it holds. A market that is not the table's own
    (TABLES) is refused, in the new rows and in the file held: no ISO-NE row enters the public table, no other grid's
    the internal one."""
    path = os.path.join(ip.OUT_DIR, name + ".csv")
    ip._require_lock(path, f"writing {name}")
    foreign = sorted(set(parts) - set(TABLES[name]))
    if foreign:
        raise RuntimeError(f"{name} does not hold the markets {foreign}; refusing to write them into it")
    for m, new in parts.items():
        if set(new["market"]) != {m} or not new["entity"].str.startswith(MARKETS[m][0] + ":").all() or set(new["source"]) != {MARKETS[m][3]}:
            raise RuntimeError(f"{name}: rows given as {m} are not all of that market, grid and source; refusing to write them")
    os.makedirs(ip.OUT_DIR, exist_ok=True)
    old = {}
    if os.path.exists(path):
        with pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False, na_values=[], chunksize=200_000) as reader:
            for chunk in reader:
                if list(chunk.columns) != ip.SERIES_COLS:
                    raise RuntimeError(f"{path} has columns {list(chunk.columns)}, expected {ip.SERIES_COLS}")
                for m, g in chunk.groupby("market"):
                    if m not in TABLES[name]:
                        raise RuntimeError(f"{path} holds rows of the market {m}, which is not one of {name}'s; not merging into it")
                    p = f"{path}.{m}.part"
                    g.to_csv(p, mode="a" if m in old else "w", header=False, index=False, lineterminator="\n")
                    old[m] = p
    body = path + ".body"
    total = added = replaced = kept = 0
    held_ = {}
    lo, hi = "9", ""
    with open(body, "w", encoding="utf-8", newline="") as f:
        for m in sorted(set(old) | set(parts)):
            new = parts.get(m)
            if new is not None:
                new = new[ip.SERIES_COLS].copy()
                if new.duplicated(ip.SERIES_KEY).any():
                    raise RuntimeError(f"{m}: new rows repeat a key; refusing to merge")
                new["value"] = new["value"].astype(float).astype(str)
            if m in old:
                o = pd.read_csv(old[m], names=ip.SERIES_COLS, dtype=str, keep_default_na=False, na_values=[])
                if new is not None:
                    gone = pd.MultiIndex.from_frame(o[ip.SERIES_KEY]).isin(pd.MultiIndex.from_frame(new[ip.SERIES_KEY]))
                    replaced += int(gone.sum())
                    o = o[~gone]
                kept += len(o)
                merged = o if new is None else pd.concat([o, new], ignore_index=True)
            else:
                merged = new
            if new is not None:
                added += len(new)
            merged = merged.sort_values(ip.SERIES_KEY)
            if merged.duplicated(ip.SERIES_KEY).any():
                raise RuntimeError(f"{m}: the merge produced a key twice")
            merged.to_csv(f, header=False, index=False, lineterminator="\n")
            total += len(merged)
            held_[m] = (len(merged), merged["ts_utc"].min(), merged["ts_utc"].max())
            lo, hi = min(lo, merged["ts_utc"].min()), max(hi, merged["ts_utc"].max())
            log(f"  {m}: {len(merged):,} rows, {merged['ts_utc'].min()} to {merged['ts_utc'].max()}")
    added -= replaced
    line = (f"File holds {total} rows, {lo} to {hi}. This run wrote {added + replaced} rows: {added} new, {replaced} replacing earlier rows with the same "
            f"(entity, variable, ts_utc); {kept} rows are kept from earlier runs. Per row, source, source_url and retrieved_at say where it came from.")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for h in list(header(held_)) + [line]:
            f.write("# " + h + "\n")
        f.write(",".join(ip.SERIES_COLS) + "\n")
        with open(body, encoding="utf-8", newline="") as b:
            while True:
                block = b.read(1 << 24)
                if not block:
                    break
                f.write(block)
    os.replace(tmp, path)
    os.remove(body)
    for p in old.values():
        os.remove(p)
    print(f"{name}.csv: rows={total} (this run {added + replaced}: {added} new, {replaced} replaced, {kept} kept) range={lo}..{hi}")
    return path, total


def table_header(name, held_, facts, notes, run_id):
    """The header of one of the two tables: what it holds, the other table's name, its sources and its license."""
    s, f, r, b = counted()
    used = sorted({MARKETS[m][3] for m in held_ if m in MARKETS})
    if name == NAME_ISONE:
        title = ("Energy Research Warehouse (ERW): ISO-NE load zone prices, history from 2019 (session 140): the eight load zones, day-ahead and real-time "
                 f"hourly LMP (SMD Hourly Data). INTERNAL. The other grids' zones and hubs (NYISO, CAISO ZP26, SPP South) are in {NAME}: the same columns, public")
        shape = ("Shape: series (docs/datastandard.md v0), partition column market. Units: USD/MWh. ts_utc is interval start, UTC. lmp_dam hourly (DA_LMP); "
                 "lmp_rtm hourly (RT_LMP, ISO-NE's own hourly average of its five-minute prices). Hr_End is the hour ending, Eastern prevailing time.")
        license_ = ("License: internal. ISO-NE's legal notice: \"Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws.\" "
                    "(https://www.iso-ne.com/legal-privacy, read 6 October 2026). Not published, in no public dataset and no download.")
        more = [f"Raw files: warehouse/raw/{CONNECTOR}/isone/ with manifest.csv (not in git); the 2025 and 2026 workbooks are those of warehouse/raw/{ISONE_LOAD_RAW}/"]
    else:
        title = ("Energy Research Warehouse (ERW): zone and hub prices, history from 2019 (session 140): NYISO's eleven load zones, CAISO ZP26 (TH_ZP26_GEN-APND) "
                 f"and SPP South (SPPSOUTH_HUB), day-ahead and real-time. ISO-NE's eight load zones are in {NAME_ISONE}: the same columns, internal (ISO-NE's notice); "
                 "no ISO-NE row is in this table")
        shape = ("Shape: series (docs/datastandard.md v0), partition column market. Units: USD/MWh. ts_utc is interval start, UTC. lmp_dam hourly; real time "
                 "lmp_rtm hourly (NYISO's own time-weighted integrated hourly LBMP, P-4A) or lmp_rtm_15m_mean (CAISO: 15-minute means of the 5-minute RTD prices, "
                 "a quarter hour only when its three prices are held).")
        license_ = ("Licenses by publisher (every source of this table is public in the registry): NYISO public with a caution (its notice grants no license and forbids "
                    "republishing \"any image or video on this website as a stand-alone file\", not data, https://www.nyiso.com/legal-notice); CAISO public with credit "
                    "(https://www.caiso.com/privacy-terms-of-use); SPP public with citation (\"Permission is implicitly granted to copy and distribute ... in whole or in "
                    "part (with appropriate citation) EXCEPT when such materials will be used ... within a commercial publication\", https://www.spp.org/terms-conditions/); "
                    "all read 6 October 2026.")
        more = [f"Raw files: warehouse/raw/{CONNECTOR}/<iso>/ with manifest.csv (not in git)",
                "SPP: a finished year's days are read from SPP's archive of the year (<report>?path=/<year>/<year>.zip), the day's own file (By_Day), by HTTP range; "
                "those rows' source_url is the archive's address."]
    return [
        title, shape,
        "Markets: " + "; ".join(f"{m} {v[0]:,} rows, {v[1]} to {v[2]}" for m, v in sorted(held_.items())),
        "This run read: " + "; ".join(facts),
        "An interval the publisher's file does not hold is not written: nothing is filled or estimated. A zone hour a file gives twice is written once "
        "when its rows agree and not at all when they differ.",
        *[f"Note: {n}" for n in notes[:40]],
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/{CONNECTOR}.py --write, from the files --pull saved (each row's retrieved_at is its file's)",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        *more,
        *[f"Source: {sid} {SOURCES[sid]['report'].split(' [terms')[0]}, {SOURCES[sid]['report_url']}" for sid in used],
        f"Rows of these series read by the pull, every run, both tables: {s:,} (ceiling {CEILING:,}); rows in the files read: {f:,}.",
        license_,
    ]


def write(isos, out_dir=None, recent=None):
    """The write stage: both tables from the saved files. A table none of whose markets has a saved file in this run
    is left as it is; one table's failure does not stop the other."""
    if out_dir:
        ip.set_out_dir(out_dir)
    since = stamp(now_utc() - pd.Timedelta(days=recent)) if recent else None
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    results, parts, notes = [], {}, []
    try:
        for name in TABLES:
            ip._require_lock(os.path.join(ip.OUT_DIR, name + ".csv"), f"writing {name}")     # before the work, not after it
        parts, notes = build(isos, log, since)
        if not parts:
            raise RuntimeError(f"no saved file under {RAW_ROOT}{' fetched since ' + since if since else ''}: run --pull first")
    except SystemExit:
        raise
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no table written:\n{tb}")
        print(f"{CONNECTOR} --write FAILED, no table written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
        parts = {}
    for name, markets in TABLES.items():
        mine = {m: parts[m] for m in markets if m in parts}
        if not mine:
            if parts:
                log(f"{name}: no saved file of this run gives a row of its markets; the table is left as it is")
            continue
        try:
            if since and not os.path.exists(os.path.join(ip.OUT_DIR, name + ".csv")):
                raise RuntimeError(f"{name} is not on this machine: a weekly run adds to the table held and never starts one from a few days' files")
            facts, ok = [], []
            for m in sorted(mine):
                g = gaps(mine[m], m)
                n, miss = sum(v[0] for v in g.values()), sum(v[3] for v in g.values())
                a, b = min(v[1] for v in g.values()), max(v[2] for v in g.values())
                facts.append(f"{m} {n:,} rows, {a} to {b}, {len(g)} entities, {miss:,} intervals missing between each entity's first and last")
                log(f"{m}: {n:,} rows, {a} to {b}, {miss:,} missing")
                print(f"{m}: {n:,} rows, {a} to {b}, {len(g)} entities, {miss:,} intervals missing between first and last")
                for e, v in sorted(g.items()):
                    log(f"    {e}: {v[0]:,} rows, {v[1]} to {v[2]}, {v[3]} missing")
                ok.append(dict(table=name, market=m, status="ok", detail=f"{n:,} rows, {a} to {b}, {miss:,} intervals missing"))
            own = [x for x in notes if ("isone" in x) == (name == NAME_ISONE)]
            write_table(name, mine, lambda held_, name=name, facts=facts, own=own: table_header(name, held_, facts, own, run_id), log)
            ip.update_sources([dict(source=sid, tables=[name], **SOURCES[sid]) for sid in sorted({MARKETS[m][3] for m in mine})])
            results.extend(ok)
        except SystemExit:
            raise
        except Exception:
            tb = ip.redact(traceback.format_exc())
            log(f"{name} FAILED, not written:\n{tb}")
            print(f"{CONNECTOR} --write FAILED, {name} not written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
            results.append(dict(table=name, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if results and all(r["status"] == "ok" for r in results) else 1


# ---------------------------------------------------------------------------
# The hour, proved against the six-week tables
# ---------------------------------------------------------------------------

LIVE = {  # market: (the six-week table, its variable)
    "nyiso_dam": ("nyiso_dam_zone_prices", "lmp_dam"), "nyiso_rtm": ("nyiso_rtm_zone_prices", "lmp_rtm_15m_mean"),
    "isone_dam": ("isone_dam_zone_prices", "lmp_dam"), "isone_rtm": ("isone_rtm_zone_prices_hourly", "lmp_rtm"),
    "caiso_dam": ("iso_dam_hub_prices", "lmp_dam"), "caiso_rtm": ("iso_rtm_hub_prices", "lmp_rtm_15m_mean"),
    "spp_dam": ("iso_dam_hub_prices", "lmp_dam"),
}


def check_market(mine, live, market):
    """Join a market's history rows to the six-week table's rows of the same entity: the joined length asserted, and
    the share of prices equal to the cent at the same stamp and at one hour either side. mine, live: entity, ts, value.
    Where the six-week table is 15-minute and the history hourly (NYISO real time), the six-week hours are the means
    of four quarter hours, all four held: those are near, not equal."""
    hourly_mine = MARKETS[market][2] == "PT1H"
    if hourly_mine and LIVE[market][1] == "lmp_rtm_15m_mean":
        g = live.groupby(["entity", live["ts"].dt.floor("h")])["value"]
        live = g.mean()[g.size() == 4].reset_index()
    out = {"market": market, "mine": len(mine), "live": len(live)}
    for lag in (0, -1, 1):
        shifted = mine.assign(ts=mine["ts"] + pd.Timedelta(hours=lag))
        j = shifted.merge(live, on=["entity", "ts"], suffixes=("_h", "_l"))
        keys = len(pd.MultiIndex.from_frame(shifted[["entity", "ts"]]).intersection(pd.MultiIndex.from_frame(live[["entity", "ts"]])))
        assert len(j) == keys, f"{market}: the join gave {len(j)} rows for {keys} common keys"
        d = (j["value_h"] - j["value_l"]).abs()
        out[lag] = dict(joined=len(j), exact=float((d < 0.005).mean()) if len(j) else float("nan"),
                        within_1=float((d < 1).mean()) if len(j) else float("nan"), mean_abs=float(d.mean()) if len(j) else float("nan"))
    return out


def check(out_dir=None, live_dir=None):
    live_dir = live_dir or os.path.join(ip.ROOT, "warehouse", "output")
    code = 0
    cache = {}
    for market in MARKETS:
        t, var = LIVE[market]
        name = next(n for n, ms in TABLES.items() if market in ms)
        table = os.path.join(out_dir or ip.OUT_DIR, name + ".csv")
        if not os.path.exists(table):
            print(f"{market}: {name} is not on this machine")
            continue
        p = os.path.join(live_dir, t + ".csv")
        if not os.path.exists(p):
            print(f"{market}: {t} is not on this machine")
            continue
        if t not in cache:
            cache[t] = pd.read_csv(p, skiprows=ip.header_rows(p), usecols=["entity", "variable", "ts_utc", "value"])
        lv = cache[t]
        lv = lv[lv["variable"] == var]
        since = lv["ts_utc"].min()
        got = []
        for chunk in pd.read_csv(table, skiprows=ip.header_rows(table), usecols=["entity", "ts_utc", "value", "market"], chunksize=500_000):
            chunk = chunk[(chunk["market"] == market) & (chunk["ts_utc"] >= str(since)[:10])]
            if len(chunk):
                got.append(chunk)
        if not got:
            print(f"{market}: {name} holds no row from {str(since)[:10]}, where {t} begins: nothing to join")
            continue
        mine = pd.concat(got)
        lv = lv[lv["entity"].isin(set(mine["entity"]))]
        mine = pd.DataFrame({"entity": mine["entity"].values, "ts": pd.to_datetime(mine["ts_utc"], utc=True).values, "value": mine["value"].values})
        lv = pd.DataFrame({"entity": lv["entity"].values, "ts": pd.to_datetime(lv["ts_utc"], utc=True).values, "value": lv["value"].values})
        r = check_market(mine, lv, market)
        line = "; ".join(f"{'same hour' if lag == 0 else ('history one hour later' if lag == -1 else 'history one hour earlier')}: joined {r[lag]['joined']:,}, "
                         f"equal to the cent {r[lag]['exact']:.4f}, within USD 1 {r[lag]['within_1']:.4f}, mean gap {r[lag]['mean_abs']:.3f}" for lag in (0, -1, 1))
        print(f"{market} ({name}) against {t}: {line}")
        if market.endswith("_dam") and r[0]["joined"] and r[0]["exact"] < 0.999:
            code = 1
    return code


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW zone and hub price history from 2019 (session 140)")
    ap.add_argument("--pull", action="store_true", help="save the publishers' files (no table is written, no data lock)")
    ap.add_argument("--write", action="store_true", help="build both tables from the saved files (the data lock into warehouse/output)")
    ap.add_argument("--check", action="store_true", help="the hour, against the six-week tables")
    ap.add_argument("--iso", action="append", choices=ISO_ORDER)
    ap.add_argument("--from", dest="first", help="pull: the first day asked for (default 2019-01-01)")
    ap.add_argument("--until", help="pull: the last day asked for (default today)")
    ap.add_argument("--recent", type=int, help="the weekly run. pull: only the periods of the last DAYS days; write: only the files fetched in the last DAYS days, merged into the table held")
    ap.add_argument("--limit", type=int, default=10 ** 9, help="pull: at most N requests a publisher in this run")
    ap.add_argument("--out-dir", help="write, check: the tables under this folder, not warehouse/output (a trial; no data lock)")
    ap.add_argument("--raw-dir", help="another folder for the saved files (a trial or a test)")
    args = ap.parse_args(argv)
    global RAW_ROOT
    if args.raw_dir:
        RAW_ROOT = os.path.abspath(args.raw_dir)
    isos = args.iso or ISO_ORDER
    code = 0
    global REFRESH
    REFRESH = bool(args.recent)
    if args.pull:
        os.makedirs(RAW_ROOT, exist_ok=True)
        run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        log = ip.Log(os.path.join(RAW_ROOT, f"pull_{'_'.join(isos)}_{run_id}.log"))
        def say(msg):
            log(msg)
            print(msg, flush=True)
        first = (pd.Timestamp.now(tz="UTC").tz_localize(None).normalize() - pd.Timedelta(days=args.recent)).strftime("%Y-%m-%d") if args.recent else args.first
        out = pull(isos, first, args.limit, say, args.until)
        for iso, what in out.items():
            say(f"{iso}: {what}")
        log.close()
        code = 0 if all(v.startswith(("ok", "paused")) for v in out.values()) else 1
    if args.write:
        code = write(isos, args.out_dir, args.recent) or code
    if args.check:
        code = check(args.out_dir) or code
    if not (args.pull or args.write or args.check):
        ap.print_help()
    return code


if __name__ == "__main__":
    sys.exit(main())
