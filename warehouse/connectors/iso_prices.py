#!/usr/bin/env python3
"""Day-ahead and real-time prices for US ISOs, in the ERW series shape.

Energy Research Warehouse (ERW) shared price connector. One function per ISO
(`pull_ercot`, `pull_caiso`, `pull_nyiso`, `pull_miso`, `pull_spp`,
`pull_isone`) pulls day-ahead (DAM) and real-time (RTM) prices through
gridstatus and returns them in the `series` shape of docs/datastandard.md. The
CLI writes one CSV per ISO and market to warehouse/output/, a run log to
warehouse/output/logs/, and every raw file the ISO returned to
warehouse/raw/<iso>/<run_id>/ (gitignored) with a manifest.

    python warehouse/connectors/iso_prices.py ercot --days 30
    python warehouse/connectors/iso_prices.py all --days 30

Rules shared by every ISO (session 1 and 2 decisions, SESSION_*_REPORT.md):
  - Window: the N complete operating days before today, in the ISO's local
    time. DAM also includes any later operating day whose results are already
    published and complete (the next-day auction), marked by `vintage`.
  - Strict completeness: a market's file is written only if every node has
    every interval in the window. Otherwise nothing is written for that market
    and the reason is logged. A forward DAM day is included only if complete.
  - Where the ISO publishes 5-minute real-time prices, the file holds 15-minute
    means: each value is the mean of exactly three 5-minute prices, and a
    quarter hour missing any of them is incomplete. The variable name says so.
  - Real data only. A failed download is retried, then fails the market.

Every row records where it came from: `source` (iso:report), `source_url` (the
exact file when one file supplied the day, otherwise the report page),
`retrieved_at`, and `vintage` (the ISO's publish time where it gives one:
ERCOT document publish time, else the file's HTTP Last-Modified header).
PJM is not included: its data API needs a key the ERW does not have yet.
"""

import argparse
import datetime as dt
import hashlib
import io
import os
import re
import sys
import threading
import time
import traceback
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from email.utils import parsedate_to_datetime

import pandas as pd
import requests

import gridstatus
from gridstatus import Ercot, Markets

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "warehouse", "output")
LOG_DIR = os.path.join(OUT_DIR, "logs")
RAW_DIR = os.path.join(ROOT, "warehouse", "raw")

SERIES_COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo",
               "market", "node", "source", "source_url", "retrieved_at", "vintage"]
TOLERANCE = 0.005  # USD/MWh; published prices carry 2 decimals
MEAN_DECIMALS = 4  # rounding of 15-minute means of 5-minute prices
RETRIES = 4


def utc_iso(ts):
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Raw capture: every HTTP response gridstatus receives is saved to disk.
# gridstatus fetches through both `requests` and pandas' urllib-based
# read_csv(url), so both are hooked. Hooks are installed once per process.
# ---------------------------------------------------------------------------

class RawStore:
    def __init__(self):
        self.dir = None
        self.lock = threading.Lock()
        self.seq = 0
        self.by_hash = {}
        self.local = threading.local()
        self.manifest = None

    def open(self, iso, run_id):
        self.dir = os.path.join(RAW_DIR, iso, run_id)
        os.makedirs(self.dir, exist_ok=True)
        self.manifest = os.path.join(self.dir, "manifest.csv")
        with open(self.manifest, "w", encoding="utf-8", newline="\n") as f:
            f.write("retrieved_at,status,bytes,sha256,last_modified,file,url\n")

    def record(self, url, status, content, headers):
        if self.dir is None:
            return None
        now = pd.Timestamp.now(tz="UTC")
        digest = hashlib.sha256(content).hexdigest()
        lm = headers.get("Last-Modified") if headers is not None else None
        with self.lock:
            self.seq += 1
            if digest in self.by_hash:
                fname = self.by_hash[digest]  # identical bytes already saved this run
            else:
                base = os.path.basename(url.split("?")[0]) or "response"
                q = re.sub(r"[^A-Za-z0-9._-]+", "_", url.split("?", 1)[1])[:60] if "?" in url else ""
                base = re.sub(r"[^A-Za-z0-9._-]+", "_", base)[:60]
                fname = f"{now:%Y%m%dT%H%M%S.%f}Z_{self.seq:05d}_{base}{'_' + q if q else ''}"
                with open(os.path.join(self.dir, fname), "wb") as f:
                    f.write(content)
                self.by_hash[digest] = fname
            with open(self.manifest, "a", encoding="utf-8", newline="\n") as f:
                row = [utc_iso(now), str(status), str(len(content)), digest, lm or "", fname, url]
                f.write(",".join('"' + v.replace('"', '""') + '"' for v in row) + "\n")
        rec = {"url": url, "retrieved_at": now, "last_modified": lm, "file": fname, "status": status}
        for bucket in getattr(self.local, "stack", []):
            bucket.append(rec)
        return rec

    def collect(self):
        store = self

        class _Collect:
            def __enter__(self_):
                self_.records = []
                if not hasattr(store.local, "stack"):
                    store.local.stack = []
                store.local.stack.append(self_.records)
                return self_.records

            def __exit__(self_, *exc):
                store.local.stack.remove(self_.records)
                return False
        return _Collect()


RAW = RawStore()
_orig_send = requests.Session.send
_orig_urlopen = urllib.request.urlopen


_send_depth = threading.local()


def _send(self, request, **kwargs):
    # requests re-enters Session.send to follow redirects and the outer call
    # returns the same final response, so record at the outermost call only
    depth = getattr(_send_depth, "n", 0)
    _send_depth.n = depth + 1
    try:
        resp = _orig_send(self, request, **kwargs)
    finally:
        _send_depth.n = depth
    if depth == 0:
        try:
            RAW.record(resp.url, resp.status_code, resp.content, resp.headers)
        except Exception as exc:  # capture must never hide the data call's own result
            sys.stderr.write(f"raw capture failed for {request.url}: {exc!r}\n")
    return resp


class _Buffered(io.BytesIO):
    def __init__(self, content, headers, url, status):
        super().__init__(content)
        self.headers, self.url, self.status = headers, url, status

    def geturl(self):
        return self.url

    def getcode(self):
        return self.status


def _urlopen(*args, **kwargs):
    r = _orig_urlopen(*args, **kwargs)
    with r:
        content = r.read()
        headers, url, status = r.headers, r.geturl(), getattr(r, "status", 200)
    RAW.record(url, status, content, headers)
    return _Buffered(content, headers, url, status)


requests.Session.send = _send
urllib.request.urlopen = _urlopen


def vintage_of(rec):
    lm = rec.get("last_modified") if rec else None
    if not lm:
        return ""
    try:
        return utc_iso(pd.Timestamp(parsedate_to_datetime(lm)))
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Shared shaping, checks and writing
# ---------------------------------------------------------------------------

class Log:
    def __init__(self, path):
        self.path = path
        self.f = open(path, "w", encoding="utf-8", newline="\n")
        self.lock = threading.Lock()

    def __call__(self, msg):
        with self.lock:
            self.f.write(msg + "\n")
            self.f.flush()

    def close(self):
        self.f.close()


def window(tz, days):
    today = pd.Timestamp.now(tz=tz).normalize()
    start = pd.Timestamp((today - pd.Timedelta(days=days)).date()).tz_localize(tz)
    end = pd.Timestamp(today.date()).tz_localize(tz)
    return start, end


def latest_per_key(rows, log):
    """One row per (node, interval): the most recently published document wins."""
    rows = rows.sort_values("vintage", kind="stable")
    dup = rows.duplicated(["node", "interval_start"], keep=False)
    if dup.any():
        spread = rows[dup].groupby(["node", "interval_start"])["value"].agg(["min", "max"])
        differing = spread[spread["max"] - spread["min"] > TOLERANCE]
        log(f"  duplicate (node, interval) keys across documents: {int(dup.sum())} rows; "
            f"{len(differing)} keys with differing values, latest-published kept")
        for key, r in differing.head(50).iterrows():
            log(f"    differing: {key[0]} {utc_iso(key[1])} min={r['min']} max={r['max']}")
    return rows.drop_duplicates(["node", "interval_start"], keep="last")


def missing_report(rows, nodes, start, end, step):
    expected = pd.date_range(start.tz_convert("UTC"), end.tz_convert("UTC"),
                             freq=step, inclusive="left")
    problems = []
    for node in nodes:
        have = pd.DatetimeIndex(rows.loc[rows["node"] == node, "interval_start"])
        missing = expected.difference(have)
        extra = have.difference(expected)
        if len(missing) or len(extra) or have.has_duplicates:
            problems.append(f"{node}: {len(have)} rows, expected {len(expected)}, "
                            f"missing {len(missing)} (first {[utc_iso(t) for t in missing[:5]]}), "
                            f"extra {len(extra)}")
    return expected, problems


def check_complete(rows, nodes, start, end, step, log):
    """Every node has every interval in [start, end) exactly once, or raise."""
    expected, problems = missing_report(rows, nodes, start, end, step)
    if problems:
        for p in problems:
            log("  INCOMPLETE " + p)
        raise RuntimeError("incomplete data, no file written: " + "; ".join(problems[:5])
                           + (f"; and {len(problems) - 5} more nodes" if len(problems) > 5 else ""))
    log(f"  complete: {len(nodes)} nodes x {len(expected)} intervals")


def forward_days(rows, nodes, end, tz, step, log):
    """Complete operating days on or after `end` (published next-day DAM)."""
    fwd = rows[rows["interval_start"] >= end]
    if fwd.empty:
        log("  forward DAM days: none published")
        return fwd, []
    local_days = sorted(set(fwd["interval_start"].dt.tz_convert(tz).dt.date))
    keep, kept = [], []
    for d in local_days:
        d0 = pd.Timestamp(d).tz_localize(tz)
        d1 = pd.Timestamp(d + dt.timedelta(days=1)).tz_localize(tz)
        part = fwd[(fwd["interval_start"] >= d0) & (fwd["interval_start"] < d1)]
        _, problems = missing_report(part, nodes, d0, d1, step)
        if problems:
            log(f"  forward DAM day {d}: incomplete, not included ({problems[0]})")
        else:
            keep.append(part)
            kept.append(str(d))
            log(f"  forward DAM day {d}: complete, included ({len(part)} rows)")
    return (pd.concat(keep) if keep else fwd.iloc[0:0]), kept


def to_series(rows, iso, variable, freq, market, geo):
    s = pd.DataFrame({
        "entity": f"{iso}:" + rows["node"],
        "variable": variable,
        "ts_utc": rows["interval_start"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value": rows["value"],
        "unit": "USD/MWh",
        "freq": freq,
        "geo": geo,
        "market": market,
        "node": rows["node"],
        "source": rows["source"],
        "source_url": rows["source_url"],
        "retrieved_at": rows["retrieved_at"],
        "vintage": rows["vintage"],
    })
    return s.sort_values(["entity", "ts_utc"]).reset_index(drop=True)[SERIES_COLS]


def write_csv(series, name, header_lines, log):
    path = os.path.join(OUT_DIR, name + ".csv")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        for line in header_lines:
            f.write("# " + line + "\n")
        series.to_csv(f, index=False, lineterminator="\n")
    os.replace(tmp, path)
    v = series["value"]
    summary = (f"{name}.csv: rows={len(series)} "
               f"range={series['ts_utc'].min()}..{series['ts_utc'].max()} "
               f"nodes={','.join(sorted(series['node'].unique()))} "
               f"min={v.min():.2f} max={v.max():.2f} USD/MWh")
    print(summary)
    log("  " + summary)
    return path


def header(iso_label, title, run_id, iso, start, end, tz, sources, notes, fwd=()):
    lines = [
        f"Energy Research Warehouse (ERW): {title}",
        "Shape: series (docs/datastandard.md v0). Units: USD/MWh. ts_utc is interval start, UTC.",
        f"Window: {iso_label} operating days {start.date()} to {(end - pd.Timedelta(days=1)).date()} "
        f"({tz}), [{utc_iso(start)}, {utc_iso(end)})",
    ]
    if fwd:
        lines.append(f"Forward DAM days also included (published before retrieval): {', '.join(fwd)}")
    lines += [
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/iso_prices.py via gridstatus "
        f"{gridstatus.__version__}",
        f"Run log: warehouse/output/logs/{iso}_prices_{run_id}.log (every source document, by name)",
        f"Raw files: warehouse/raw/{iso}/{run_id}/ (not in git; manifest.csv lists each file and URL)",
    ]
    lines += sources
    lines += notes
    return lines


def with_retries(what, fn, log, attempts=RETRIES, wait=5):
    last = None
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:
            last = exc
            log(f"    retry {attempt + 1}/{attempts} for {what}: {exc!r}")
            time.sleep(wait * (attempt + 1))
    raise RuntimeError(f"{what} failed after {attempts} attempts: {last!r}")


def pull_days(days, fetch, nodes, source, report_page, log, workers=1,
              optional=False, what="", data_url=None):
    """Call fetch(day) per operating day, keep `nodes`, attach provenance.

    fetch returns a gridstatus frame with Location, Interval Start, Interval
    End and LMP. `data_url` is a regex naming the ISO's data files, so that
    helper requests (a cookie page, a latest-interval lookup) are not
    mistaken for the source; when exactly one data file supplied the day,
    rows cite it and take its Last-Modified as vintage. A day that fails raises, unless `optional` (forward DAM days,
    which may simply not be published yet): those are logged and skipped.
    """
    def one(day):
        def call():
            with RAW.collect() as recs:
                df = fetch(day)
            return df, list(recs)
        try:
            if optional:
                with RAW.collect() as recs:
                    df = fetch(day)
                return day, df, list(recs), None
            df, recs = with_retries(f"{what} {day.date()}", call, log)
            return day, df, recs, None
        except Exception as exc:
            if optional:
                return day, None, [], exc
            raise

    out, used = [], []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(one, days))
    for day, df, recs, exc in results:
        if exc is not None:
            log(f"  {what} {day.date()}: not available ({type(exc).__name__}: {str(exc)[:160]}), skipped")
            continue
        ok = [r for r in recs if str(r["status"]).startswith("2")]
        data = [r for r in ok if data_url is None or re.search(data_url, r["url"])]
        d = df[df["Location"].astype(str).isin(nodes)]
        single = data[0] if len(data) == 1 else None
        last = data[-1] if data else (ok[-1] if ok else None)
        out.append(pd.DataFrame({
            "node": d["Location"].astype(str).values,
            "interval_start": pd.to_datetime(d["Interval Start"], utc=True).values,
            "interval_end": pd.to_datetime(d["Interval End"], utc=True).values,
            "value": pd.to_numeric(d["LMP"]).values,
            # a fetch that can draw on two reports names the one it used per row
            "source": d["_source"].values if "_source" in d.columns else source,
            "source_url": single["url"] if single else report_page,
            "retrieved_at": utc_iso(last["retrieved_at"]) if last else "",
            "vintage": vintage_of(single),
        }))
        used.append((day, ok, len(d)))
        log(f"  {what} {day.date()}: {len(d)} rows from {len(data)} data file(s) "
            f"({len(ok)} responses)")
        for r in ok:
            log(f"    {r['file']} {r['url']} last-modified={r['last_modified'] or ''}")
    if not out:
        return pd.DataFrame(columns=["node", "interval_start", "interval_end", "value", "source",
                                     "source_url", "retrieved_at", "vintage"]), used
    rows = pd.concat(out, ignore_index=True)
    rows["interval_start"] = pd.to_datetime(rows["interval_start"], utc=True)
    rows["interval_end"] = pd.to_datetime(rows["interval_end"], utc=True)
    return rows, used


def check_interval_length(rows, minutes, log):
    length = (rows["interval_end"] - rows["interval_start"]).dt.total_seconds() / 60
    bad = rows[length != minutes]
    if len(bad):
        raise RuntimeError(f"{len(bad)} rows are not {minutes}-minute intervals, e.g. "
                           f"{bad[['node', 'interval_start', 'interval_end']].head(3).to_dict('records')}")
    log(f"  interval length: all {len(rows)} rows are {minutes} minutes")


def rebuild_irregular_intervals(rows, start, end, nodes, log):
    """NYISO: intervals run from the previous time stamp to this one.

    NYISO's real-time file stamps each price at its interval end and adds
    extra dispatch intervals at irregular times (e.g. 09:47:51) between the
    regular 5-minute stamps; gridstatus labels every row as 5 minutes long,
    which makes those rows overlap. Rebuild each interval as (previous stamp,
    this stamp]. A regular stamp is sometimes published a few seconds late
    (12:10:03 for 12:10). Completeness stays strict: no interval may be longer
    than 5 minutes, so a missing stamp can never be bridged by stretching a
    price over the gap, and every quarter hour must still be fully covered.
    """
    r = rows.sort_values(["node", "interval_end"]).copy()
    prev = r.groupby("node")["interval_end"].shift(1)
    r["interval_start"] = prev.fillna(r["interval_end"] - pd.Timedelta(minutes=5))
    secs = (r["interval_end"] - r["interval_start"]).dt.total_seconds()
    too_long = r[secs > 300]
    if len(too_long):
        for _, t in too_long.head(20).iterrows():
            log(f"  INCOMPLETE {t['node']}: gap from {utc_iso(t['interval_start'])} to "
                f"{utc_iso(t['interval_end'])} ({(t['interval_end'] - t['interval_start']).total_seconds():.0f} s)")
        raise RuntimeError(f"incomplete data, no file written: {len(too_long)} intervals longer "
                           f"than 5 minutes (a missing time stamp), first at "
                           f"{too_long.iloc[0]['node']} {utc_iso(too_long.iloc[0]['interval_end'])}")
    grid = pd.date_range(start.tz_convert("UTC") + pd.Timedelta(minutes=5), end.tz_convert("UTC"),
                         freq="5min")
    offgrid = int((~r["interval_end"].isin(grid)).sum())
    log(f"  irregular intervals: {len(r)} intervals for {len(nodes)} nodes, {offgrid} stamped off "
        f"the regular 5-minute grid; none longer than 5 minutes; weighted by length")
    return r


def split_at_quarters(rows):
    """Split any interval that crosses a quarter-hour boundary into two pieces."""
    q_end = rows["interval_start"].dt.floor("15min") + pd.Timedelta(minutes=15)
    cross = rows["interval_end"] > q_end
    if not cross.any():
        return rows
    a = rows[cross].copy()
    b = rows[cross].copy()
    a["interval_end"] = q_end[cross]
    b["interval_start"] = q_end[cross]
    return pd.concat([rows[~cross], a, b], ignore_index=True)


def to_15min_means(rows, log):
    """Time-weighted mean price per node and quarter hour, full coverage required.

    With regular 5-minute intervals this is the plain mean of exactly three
    prices. A quarter hour counts only if its intervals cover all 900 seconds
    and none crosses the quarter-hour boundary.
    """
    r = rows.copy()
    r["q"] = r["interval_start"].dt.floor("15min")
    r["secs"] = (r["interval_end"] - r["interval_start"]).dt.total_seconds()
    r["crosses"] = r["interval_end"] > r["q"] + pd.Timedelta(minutes=15)
    r["wv"] = r["value"] * r["secs"]
    g = r.groupby(["node", "q"])
    agg = g.agg(wv=("wv", "sum"), secs=("secs", "sum"), n=("value", "size"),
                crosses=("crosses", "any"),
                source=("source", "first"), retrieved_at=("retrieved_at", "max"),
                vintage=("vintage", "max"), n_urls=("source_url", "nunique"),
                source_url=("source_url", "first")).reset_index()
    bad = agg[(agg["secs"] != 900) | agg["crosses"]]
    if len(bad):
        log(f"  15-minute buckets not fully covered: {len(bad)} (dropped; completeness check "
            f"decides): {bad[['node', 'q', 'n', 'secs']].head(10).to_dict('records')}")
    agg = agg[(agg["secs"] == 900) & ~agg["crosses"]].copy()
    irregular = int((agg["n"] != 3).sum())
    if irregular:
        log(f"  {irregular} quarter hours hold other than three intervals (time-weighted)")
    agg["value"] = (agg["wv"] / agg["secs"]).round(MEAN_DECIMALS)
    multi = agg["n_urls"] > 1
    if multi.any():
        # quarter hour spans two source files (a day boundary cannot, so this is rare)
        agg.loc[multi, "source_url"] = agg.loc[multi, "source_url"] + " (and others, see run log)"
    agg = agg.rename(columns={"q": "interval_start"})
    log(f"  aggregated {len(rows)} 5-minute rows to {len(agg)} 15-minute means")
    return agg[["node", "interval_start", "value", "source", "source_url", "retrieved_at", "vintage"]]


def log_sources(rows, log):
    g = rows.groupby(["source", "source_url"]).size().reset_index(name="rows")
    log(f"  distinct source_url values: {len(g)}")


def source_lines(rows, reports):
    lines = []
    for src, g in rows.groupby("source"):
        name, page = reports[src]
        lines.append(f"Source: {src} {name}, {page}")
        files = g["source_url"].nunique()
        vint = g.loc[g["vintage"] != "", "vintage"]
        span = f", published {vint.min()} to {vint.max()}" if len(vint) else ", publish time not given by source"
        lines.append(f"  {files} distinct file URL(s){span}; per row: see source_url and vintage")
    return lines


def run_market(ctx, spec):
    """Pull, check and write one ISO market. Raises on any failure."""
    log = ctx["log"]
    iso, tz, geo = ctx["iso"], ctx["tz"], ctx["geo"]
    start, end = ctx["start"], ctx["end"]
    nodes = spec["nodes"]
    log(f"{spec['name']}: {spec['describe']}")
    days = list(pd.date_range(start, end, freq="D", inclusive="left"))
    rows, _ = pull_days(days, spec["fetch"], nodes, spec["source"], spec["page"], log,
                        workers=spec.get("workers", 1), what=spec["name"],
                        data_url=ctx.get("data_url"))
    fwd_rows, fwd = rows.iloc[0:0], []
    if spec.get("forward"):
        now_local = pd.Timestamp.now(tz=tz)
        fdays = list(pd.date_range(end, now_local.normalize() + pd.Timedelta(days=1), freq="D"))
        f, _ = pull_days(fdays, spec["fetch"], nodes, spec["source"], spec["page"], log,
                         optional=True, what=spec["name"] + " forward",
                         data_url=ctx.get("data_url"))
        if len(f):
            f = latest_per_key(f[f["interval_start"] >= end], log)
            fwd_rows, fwd = forward_days(f, nodes, end, tz, spec["step"], log)
    rows = rows[(rows["interval_start"] >= start) & (rows["interval_start"] < end)]
    rows = latest_per_key(rows, log)
    if spec.get("irregular"):
        rows = rebuild_irregular_intervals(rows, start, end, nodes, log)
        rows = to_15min_means(split_at_quarters(rows), log)
    elif spec.get("five_min"):
        check_interval_length(rows, 5, log)
        rows = to_15min_means(rows, log)
    elif "minutes" in spec:
        check_interval_length(rows, spec["minutes"], log)
    check_complete(rows, nodes, start, end, spec["step"], log)
    if len(fwd_rows):
        fwd_rows = fwd_rows[["node", "interval_start", "value", "source", "source_url",
                             "retrieved_at", "vintage"]]
        rows = pd.concat([rows, fwd_rows], ignore_index=True)
    log_sources(rows, log)
    s = to_series(rows, iso, spec["variable"], spec["freq"], spec["market"], geo)
    return write_csv(s, spec["file"],
                     header(ctx["label"], spec["title"], ctx["run_id"], iso, start, end, tz,
                            source_lines(rows, ctx["reports"]), spec.get("notes", []), fwd), log)


def run_iso(ctx, specs):
    failures = 0
    for spec in specs:
        try:
            run_market(ctx, spec)
        except Exception:
            failures += 1
            tb = traceback.format_exc()
            ctx["log"](f"{spec['name']} FAILED, no output file written:\n{tb}")
            print(f"{ctx['iso']} {spec['name']} FAILED, no output file written: "
                  f"{tb.strip().splitlines()[-1]}", file=sys.stderr)
    return failures


FIVE_MIN_NOTE = ("RTM values are 15-minute means of the ISO's 5-minute real-time prices: each is the "
                 "arithmetic mean of exactly three 5-minute LMPs (interval starts :00, :05, :10 of the "
                 f"quarter hour), rounded to {MEAN_DECIMALS} decimals. A quarter hour missing any "
                 "5-minute price is incomplete and fails the file.")
NYISO_RT_NOTE = ("RTM values are 15-minute time-weighted means of NYISO's real-time (RTD) LBMPs. NYISO "
                 "stamps each price at its interval end and adds extra RTD intervals at irregular times "
                 "between the regular 5-minute stamps; each price is weighted by its interval length "
                 "(previous stamp to this stamp), and an interval crossing a quarter-hour boundary is "
                 "split at it. No interval may exceed 5 minutes (a missing stamp is never bridged) and "
                 "each quarter hour must be fully covered, otherwise the file is not written. Where a quarter hour "
                 "holds exactly the three regular intervals this equals their arithmetic mean. Rounded "
                 f"to {MEAN_DECIMALS} decimals.")


# ---------------------------------------------------------------------------
# ERCOT (session 1 logic, unchanged apart from forward DAM days)
# ---------------------------------------------------------------------------

ERCOT_HUBS = ["HB_NORTH", "HB_SOUTH", "HB_WEST", "HB_HOUSTON", "HB_BUSAVG"]
ERCOT_TZ = "America/Chicago"
ERCOT_REPORTS = {
    "NP4-190-CD": ("DAM Settlement Point Prices", 12331),
    "NP6-785-ER": ("Historical RTM Load Zone and Hub Prices", 13061),
    "NP6-905-CD": ("Settlement Point Prices at Resource Nodes, Hubs and Load Zones", 12301),
}
ERCOT_PAGE = "https://www.ercot.com/mp/data-products/data-product-details?id={}"
ERCOT_DOC_LIST = "https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId={}"


class TracedErcot(Ercot):
    """Ercot that remembers every document it reads, and retries downloads.

    gridstatus concatenates documents and drops which row came from which one.
    These overrides keep that link so each output row can name its document.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frames = []   # (doc, retrieved_at, parsed frame) per document read
        self.singles = []  # (doc, retrieved_at) per _get_document call

    def read_doc(self, doc, *args, **kwargs):
        last = None
        for attempt in range(RETRIES):
            try:
                df = super().read_doc(doc, *args, **kwargs)
                self.frames.append((doc, pd.Timestamp.now(tz="UTC"), df.copy()))
                return df
            except Exception as exc:  # retried, then re-raised with context
                last = exc
                time.sleep(2 * (attempt + 1))
        raise RuntimeError(f"could not read ERCOT document {doc.url} "
                           f"({doc.constructed_name}) after {RETRIES} attempts: {last!r}")

    def parse_doc(self, doc, *args, **kwargs):
        # gridstatus 0.36.0 bug: the current year's NP6-785-ER workbook has
        # empty sheets for the months still to come. get_rtm_spp concatenates
        # all sheets, the empty ones turn the hour column into dtype object,
        # and parse_doc's .astype("timedelta64[h]") then raises. Cast
        # whole-number hours to int64 first; values are unchanged, and anything
        # that is not a whole number is left alone so the parent still fails.
        for col in ("Delivery Hour", "DeliveryHour", "HourEnding"):
            if col in doc.columns and not pd.api.types.is_integer_dtype(doc[col]):
                h = pd.to_numeric(doc[col], errors="coerce")
                if h.notna().all() and (h == h.round()).all():
                    doc[col] = h.astype("int64")
        return super().parse_doc(doc, *args, **kwargs)

    def _get_document(self, *args, **kwargs):
        doc = super()._get_document(*args, **kwargs)
        self.singles.append((doc, pd.Timestamp.now(tz="UTC")))
        return doc


def _ercot_rows_from_frames(frames, report_id):
    out = []
    for doc, retrieved_at, df in frames:
        loc_col = next(c for c in ("SettlementPointName", "SettlementPoint",
                                   "Settlement Point Name", "Settlement Point")
                       if c in df.columns)
        price_col = next(c for c in ("SettlementPointPrice", "Settlement Point Price")
                         if c in df.columns)
        d = df[df[loc_col].isin(ERCOT_HUBS)]
        out.append(pd.DataFrame({
            "node": d[loc_col].astype(str).values,
            "interval_start": d["Interval Start"].values,
            "value": pd.to_numeric(d[price_col]).values,
            "source": f"ercot:{report_id}",
            "source_url": doc.url,
            "doc_name": doc.constructed_name,
            "retrieved_at": utc_iso(retrieved_at),
            "vintage": utc_iso(doc.publish_date),
        }))
    if not out:
        return pd.DataFrame(columns=["node", "interval_start", "value", "source",
                                     "source_url", "doc_name", "retrieved_at", "vintage"])
    r = pd.concat(out, ignore_index=True)
    r["interval_start"] = pd.to_datetime(r["interval_start"], utc=True)
    return r


def _ercot_cross_check(rows, ret, log):
    """The traced rows must equal what gridstatus returned for the same keys."""
    r = ret[ret["Location"].isin(ERCOT_HUBS)].copy()
    r["interval_start"] = pd.to_datetime(r["Interval Start"], utc=True)
    r = r.rename(columns={"Location": "node"}).groupby(["node", "interval_start"])["SPP"]
    # ERCOT retry files can repeat a key; accept a match against any returned value
    r_min, r_max = r.min(), r.max()
    m = rows.set_index(["node", "interval_start"])["value"]
    joined = m.to_frame().join(r_min.rename("lo")).join(r_max.rename("hi"))
    if len(joined) != len(rows):
        raise RuntimeError(f"cross-check join fanned out: {len(joined)} keys for {len(rows)} rows")
    missing = int(joined["lo"].isna().sum())
    off = joined[(joined["value"] < joined["lo"] - TOLERANCE)
                 | (joined["value"] > joined["hi"] + TOLERANCE)]
    log(f"  cross-check vs gridstatus return: {len(joined)} keys, {missing} absent from return, "
        f"{len(off)} with a different value")
    if missing or len(off):
        raise RuntimeError(f"cross-check failed: {missing} traced rows absent from gridstatus "
                           f"output, {len(off)} with a different value")


def _ercot_compare_overlap(hist, live, log):
    j = hist.set_index(["node", "interval_start"])["value"].to_frame("archive").join(
        live.set_index(["node", "interval_start"])["value"].rename("live"), how="inner")
    if j.empty:
        log("  overlap NP6-785-ER vs NP6-905-CD: none")
        return
    d = (j["archive"] - j["live"]).abs()
    n_diff = int((d > TOLERANCE).sum())
    log(f"  overlap NP6-785-ER vs NP6-905-CD: {len(j)} keys, {n_diff} differ by more than "
        f"{TOLERANCE}, max abs diff {d.max():.4f}. Archive values kept in the overlap.")
    for key, row in j[d > TOLERANCE].head(20).iterrows():
        log(f"    differs: {key[0]} {utc_iso(key[1])} archive={row['archive']} live={row['live']}")


def _ercot_log_docs(rows, log):
    g = rows.groupby(["source", "doc_name", "source_url", "vintage"]).size().reset_index(name="rows")
    log(f"  source documents used: {len(g)}")
    for _, r in g.sort_values("vintage").iterrows():
        log(f"    {r['source']} {r['doc_name']} published {r['vintage']} rows {r['rows']} {r['source_url']}")


def _ercot_header(title, run_id, start, end, used_docs, notes, fwd=()):
    lines = [
        f"Energy Research Warehouse (ERW): {title}",
        "Shape: series (docs/datastandard.md v0). Units: USD/MWh. ts_utc is interval start, UTC.",
        f"Window: ERCOT operating days {start.date()} to {(end - pd.Timedelta(days=1)).date()} "
        f"(America/Chicago), [{utc_iso(start)}, {utc_iso(end)})",
    ]
    if fwd:
        lines.append(f"Forward DAM days also included (published before retrieval): {', '.join(fwd)}")
    lines += [
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/iso_prices.py via gridstatus Ercot",
        f"Run log: warehouse/output/logs/ercot_prices_{run_id}.log (every source document, by name)",
        f"Raw files: warehouse/raw/ercot/{run_id}/ (not in git; manifest.csv lists each file and URL)",
    ]
    for rid, g in used_docs.groupby("source"):
        rid = rid.split(":", 1)[1]
        name, rtid = ERCOT_REPORTS[rid]
        lines.append(f"Source: ERCOT {rid} {name}, {ERCOT_PAGE.format(rid)}")
        lines.append(f"  document list: {ERCOT_DOC_LIST.format(rtid)}")
        lines.append(f"  {len(g)} document(s) used, published {g['vintage'].min()} to "
                     f"{g['vintage'].max()}; rows from each: see source_url and vintage columns")
    lines += notes
    return lines


def _ercot_dam(ctx):
    log, start, end, run_id = ctx["log"], ctx["start"], ctx["end"], ctx["run_id"]
    e = TracedErcot()
    log("DAM: ERCOT NP4-190-CD via Ercot.get_spp(market=DAY_AHEAD_HOURLY)")
    # a delivery day's DAM file is published the day before, so ask from start - 1 day;
    # ask up to now so any already-published forward day is included
    ret = e.get_spp(date=start - pd.Timedelta(days=1), end=pd.Timestamp.now(tz=ERCOT_TZ),
                    market=Markets.DAY_AHEAD_HOURLY, location_type="Trading Hub")
    all_rows = _ercot_rows_from_frames(e.frames, "NP4-190-CD")
    rows = all_rows[(all_rows["interval_start"] >= start) & (all_rows["interval_start"] < end)]
    log(f"  documents read: {len(e.frames)}; hub rows in window: {len(rows)}")
    rows = latest_per_key(rows, log)
    check_complete(rows, ERCOT_HUBS, start, end, "1h", log)
    _ercot_cross_check(rows, ret, log)
    fwd_rows, fwd = forward_days(latest_per_key(all_rows[all_rows["interval_start"] >= end], log),
                                 ERCOT_HUBS, end, ERCOT_TZ, "1h", log)
    if len(fwd_rows):
        _ercot_cross_check(fwd_rows, ret, log)
        rows = pd.concat([rows, fwd_rows], ignore_index=True)
    _ercot_log_docs(rows, log)
    s = to_series(rows, "ercot", "spp_dam", "PT1H", "ercot_dam", "US-TX")
    return write_csv(s, "ercot_dam_hub_prices",
                     _ercot_header("ERCOT day-ahead market settlement point prices, trading hubs",
                                   run_id, start, end,
                                   rows[["source", "vintage", "source_url"]].drop_duplicates(),
                                   [], fwd), log)


def _ercot_rtm(ctx):
    log, start, end, run_id = ctx["log"], ctx["start"], ctx["end"], ctx["run_id"]
    e = TracedErcot()
    log("RTM: ERCOT NP6-785-ER via Ercot.get_rtm_spp(year), then NP6-905-CD via "
        "Ercot.get_spp(market=REAL_TIME_15_MIN)")
    hist = []
    for year in range(start.year, (end - pd.Timedelta(seconds=1)).year + 1):
        n = len(e.singles)
        df = e.get_rtm_spp(year=year)
        doc, retrieved_at = e.singles[n]
        d = df[df["Location"].isin(ERCOT_HUBS)]
        hist.append(pd.DataFrame({
            "node": d["Location"].astype(str).values,
            "interval_start": pd.to_datetime(d["Interval Start"], utc=True).values,
            "value": pd.to_numeric(d["SPP"]).values,
            "source": "ercot:NP6-785-ER",
            "source_url": doc.url,
            "doc_name": doc.constructed_name,
            "retrieved_at": utc_iso(retrieved_at),
            "vintage": utc_iso(doc.publish_date),
        }))
        log(f"  NP6-785-ER {year}: {doc.constructed_name}, published {utc_iso(doc.publish_date)}, "
            f"hub rows {len(d)}, last interval {utc_iso(d['Interval Start'].max())}")
    hist = pd.concat(hist, ignore_index=True)
    hist["interval_start"] = pd.to_datetime(hist["interval_start"], utc=True)
    hist = hist[(hist["interval_start"] >= start) & (hist["interval_start"] < end)]
    hist_last = hist["interval_start"].max() if len(hist) else start - pd.Timedelta(minutes=15)

    live = _ercot_rows_from_frames([], "NP6-905-CD")
    if hist_last + pd.Timedelta(minutes=15) < end:
        # one day of overlap with the archive, to compare the two sources
        live_from = max(start, hist_last - pd.Timedelta(days=1))
        e.frames = []
        ret = e.get_spp(date=live_from.tz_convert(ERCOT_TZ), end=end + pd.Timedelta(minutes=15),
                        market=Markets.REAL_TIME_15_MIN, location_type="Trading Hub")
        live = _ercot_rows_from_frames(e.frames, "NP6-905-CD")
        live = live[(live["interval_start"] >= live_from) & (live["interval_start"] < end)]
        log(f"  NP6-905-CD: documents read {len(e.frames)}, hub rows in window {len(live)}")
        live = latest_per_key(live, log)
        _ercot_cross_check(live, ret, log)
        _ercot_compare_overlap(hist, live, log)
        live = live[live["interval_start"] > hist_last]

    rows = pd.concat([hist, live], ignore_index=True)
    check_complete(rows, ERCOT_HUBS, start, end, "15min", log)
    _ercot_log_docs(rows, log)
    s = to_series(rows, "ercot", "spp_rtm", "PT15M", "ercot_rtm", "US-TX")
    notes = [f"Split: NP6-785-ER for intervals up to {utc_iso(hist_last)}, "
             f"NP6-905-CD after. See run log for the overlap comparison."]
    return write_csv(s, "ercot_rtm_hub_prices",
                     _ercot_header("ERCOT real-time market settlement point prices, trading hubs, "
                                   "15-minute", run_id, start, end,
                                   rows[["source", "vintage", "source_url"]].drop_duplicates(),
                                   notes), log)


def pull_ercot(ctx):
    """ERCOT: DAM NP4-190-CD; RTM NP6-785-ER archive plus NP6-905-CD live."""
    failures = 0
    for name, fn in (("DAM", _ercot_dam), ("RTM", _ercot_rtm)):
        try:
            fn(ctx)
        except Exception:
            failures += 1
            tb = traceback.format_exc()
            ctx["log"](f"{name} FAILED, no output file written:\n{tb}")
            print(f"ercot {name} FAILED, no output file written: {tb.strip().splitlines()[-1]}",
                  file=sys.stderr)
    return failures


# ---------------------------------------------------------------------------
# CAISO
# ---------------------------------------------------------------------------

CAISO_HUBS = ["TH_NP15_GEN-APND", "TH_SP15_GEN-APND", "TH_ZP26_GEN-APND"]
CAISO_OASIS = "https://oasis.caiso.com/mrioasis/logon.do"


def pull_caiso(ctx):
    """CAISO trading hubs via OASIS PRC_LMP (DAM) and PRC_INTVL_LMP (RTD, 5-minute)."""
    c = gridstatus.CAISO()
    ctx["data_url"] = r"oasisapi/SingleZip"

    def fetch(market):
        return lambda day: c.get_lmp(date=day, end=day + pd.Timedelta(days=1), market=market,
                                     locations=CAISO_HUBS, sleep=5)
    ctx["reports"] = {
        "caiso:PRC_LMP": ("OASIS Locational Marginal Prices, day-ahead market (DAM)", CAISO_OASIS),
        "caiso:PRC_INTVL_LMP": ("OASIS Interval Locational Marginal Prices, real-time dispatch "
                                "(RTD, 5-minute)", CAISO_OASIS),
    }
    specs = [
        dict(name="DAM", describe="CAISO OASIS PRC_LMP via CAISO.get_lmp(DAY_AHEAD_HOURLY)",
             fetch=fetch(Markets.DAY_AHEAD_HOURLY), nodes=CAISO_HUBS, source="caiso:PRC_LMP",
             page=CAISO_OASIS, step="1h", minutes=60, forward=True, variable="lmp_dam",
             freq="PT1H", market="caiso_dam", file="caiso_dam_hub_prices",
             title="CAISO day-ahead market LMPs, trading hubs"),
        dict(name="RTM", describe="CAISO OASIS PRC_INTVL_LMP via CAISO.get_lmp(REAL_TIME_5_MIN), "
             "aggregated to 15-minute means", fetch=fetch(Markets.REAL_TIME_5_MIN),
             nodes=CAISO_HUBS, source="caiso:PRC_INTVL_LMP", page=CAISO_OASIS, step="15min",
             five_min=True, variable="lmp_rtm_15m_mean", freq="PT15M", market="caiso_rtm",
             file="caiso_rtm_hub_prices", notes=[FIVE_MIN_NOTE],
             title="CAISO real-time (RTD) LMPs, trading hubs, 15-minute means of 5-minute prices"),
    ]
    return run_iso(ctx, specs)


# ---------------------------------------------------------------------------
# NYISO
# ---------------------------------------------------------------------------

NYISO_ZONES = ["CAPITL", "CENTRL", "DUNWOD", "GENESE", "HUD VL", "LONGIL", "MHK VL",
               "MILLWD", "N.Y.C.", "NORTH", "WEST"]
NYISO_PAGE = "https://www.nyiso.com/energy-market-operational-data"


def pull_nyiso(ctx):
    """NYISO 11 load zones: damlbmp (DAM, hourly) and realtime (RTD, 5-minute)."""
    n = gridstatus.NYISO()
    # daily csv or monthly zip; not realtime_zone_lbmp.csv, the latest-interval
    # file gridstatus reads only to label 5- versus 15-minute rows
    ctx["data_url"] = r"/\d{8}(realtime|damlbmp)_zone"

    def fetch(market):
        def f(day):
            df = n.get_lmp(date=day, market=market, location_type="zone")
            if market == Markets.REAL_TIME_5_MIN:
                # the daily file can carry 15-minute RTC rows after the last RTD
                # interval; a complete past day is RTD only, anything else is left
                # for the interval-length check to reject
                df = df[df["Market"] == Markets.REAL_TIME_5_MIN.value]
            return df
        return f
    ctx["reports"] = {
        "nyiso:damlbmp": ("Day-Ahead Market LBMP, zonal (P-2A)", "http://mis.nyiso.com/public/P-2Alist.htm"),
        "nyiso:realtime": ("Real-Time Market LBMP, zonal, RTD 5-minute (P-24A)",
                           "http://mis.nyiso.com/public/P-24Alist.htm"),
    }
    specs = [
        dict(name="DAM", describe="NYISO damlbmp zone via NYISO.get_lmp(DAY_AHEAD_HOURLY)",
             fetch=fetch(Markets.DAY_AHEAD_HOURLY), nodes=NYISO_ZONES, source="nyiso:damlbmp",
             page=ctx["reports"]["nyiso:damlbmp"][1], step="1h", minutes=60, forward=True,
             variable="lmp_dam", freq="PT1H", market="nyiso_dam", file="nyiso_dam_zone_prices",
             title="NYISO day-ahead market LBMPs, 11 load zones"),
        dict(name="RTM", describe="NYISO realtime zone via NYISO.get_lmp(REAL_TIME_5_MIN), "
             "aggregated to 15-minute means", fetch=fetch(Markets.REAL_TIME_5_MIN),
             nodes=NYISO_ZONES, source="nyiso:realtime", page=ctx["reports"]["nyiso:realtime"][1],
             step="15min", five_min=True, irregular=True, variable="lmp_rtm_15m_mean",
             freq="PT15M", market="nyiso_rtm", file="nyiso_rtm_zone_prices", notes=[NYISO_RT_NOTE],
             title="NYISO real-time (RTD) LBMPs, 11 load zones, 15-minute means of 5-minute prices"),
    ]
    return run_iso(ctx, specs)


# ---------------------------------------------------------------------------
# MISO
# ---------------------------------------------------------------------------

MISO_HUBS = ["ARKANSAS.HUB", "ILLINOIS.HUB", "INDIANA.HUB", "LOUISIANA.HUB", "MICHIGAN.HUB",
             "MINN.HUB", "MS.HUB", "TEXAS.HUB"]
MISO_PAGE = "https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/"


def pull_miso(ctx):
    """MISO 8 hubs: DA ex-post LMP (hourly) and RT ex-post LMP (hourly, final or prelim).

    MISO's 5-minute real-time LMPs are not retrievable for a 30-day window
    without an API key: gridstatus reads 5-minute prelim data for today and
    yesterday only, and the weekly 5-minute final files lag one to two weeks.
    The RTM file therefore holds MISO's own hourly real-time ex-post LMPs:
    the final report where published, the preliminary report otherwise.
    """
    m = gridstatus.MISO()
    ctx["data_url"] = r"marketreports/\d{8}_"

    def dam(day):
        return m.get_lmp(date=day, market=Markets.DAY_AHEAD_HOURLY, locations="ALL")

    def rtm(day):
        try:
            df = m.get_lmp(date=day, market=Markets.REAL_TIME_HOURLY_FINAL, locations="ALL")
            df["_source"] = "miso:rt_lmp_final"
        except Exception as exc:
            if "404" not in repr(exc):
                raise
            df = m.get_lmp(date=day, market=Markets.REAL_TIME_HOURLY_PRELIM, locations="ALL")
            df["_source"] = "miso:rt_lmp_prelim"
        return df

    ctx["reports"] = {
        "miso:da_expost_lmp": ("Day-Ahead Ex-Post LMP (daily csv)", MISO_PAGE),
        "miso:rt_lmp_final": ("Real-Time Final Market LMP, hourly (daily csv)", MISO_PAGE),
        "miso:rt_lmp_prelim": ("Real-Time Preliminary Ex-Post LMP, hourly (daily csv)", MISO_PAGE),
    }
    specs = [
        dict(name="DAM", describe="MISO DA ex-post LMP via MISO.get_lmp(DAY_AHEAD_HOURLY)",
             fetch=dam, nodes=MISO_HUBS, source="miso:da_expost_lmp", page=MISO_PAGE, step="1h",
             minutes=60, forward=True, variable="lmp_dam", freq="PT1H", market="miso_dam",
             file="miso_dam_hub_prices", title="MISO day-ahead market ex-post LMPs, 8 trading hubs"),
        dict(name="RTM", describe="MISO RT ex-post hourly LMP via MISO.get_lmp("
             "REAL_TIME_HOURLY_FINAL, else REAL_TIME_HOURLY_PRELIM)", fetch=rtm, nodes=MISO_HUBS,
             source="miso:rt_lmp_final", page=MISO_PAGE, step="1h", minutes=60,
             variable="lmp_rtm", freq="PT1H", market="miso_rtm", file="miso_rtm_hub_prices",
             title="MISO real-time market ex-post LMPs, 8 trading hubs, hourly",
             notes=["Hourly, not 15-minute: MISO 5-minute real-time LMPs for the whole window are "
                    "not retrievable without an API key (see connector docstring). Rows from the "
                    "preliminary report have source miso:rt_lmp_prelim."]),
    ]
    return run_iso(ctx, specs)


# ---------------------------------------------------------------------------
# SPP
# ---------------------------------------------------------------------------

SPP_HUBS = ["SPPNORTH_HUB", "SPPSOUTH_HUB"]
SPP_DAM_PAGE = "https://portal.spp.org/pages/da-lmp-by-location"
SPP_RTM_PAGE = "https://portal.spp.org/pages/rtbm-lmp-by-location"


def pull_spp(ctx):
    """SPP 2 hubs: DA-LMP-SL (hourly) and RTBM-LMP-SL (5-minute).

    The SPP portal serves about 0.1 MB/s per connection and a daily RTBM file
    is about 50 MB, so days are fetched in parallel. A day whose daily file is
    not posted yet is read from its 288 five-minute interval files instead.
    """
    s = gridstatus.SPP()
    ctx["data_url"] = r"file-browser-api/download"

    def dam(day):
        return s.get_lmp_day_ahead_hourly(date=day, location_type="Hub")

    def rtm(day):
        try:
            return s.get_lmp_real_time_5_min_by_location(date=day, location_type="Hub",
                                                         use_daily_files=True)
        except Exception as exc:
            if "404" not in repr(exc):
                raise
        stamps = pd.date_range(day, day + pd.Timedelta(days=1), freq="5min", inclusive="left")
        parts = [with_retries(f"SPP RTBM interval {t}", lambda t=t: s.get_lmp_real_time_5_min_by_location(
            date=t, location_type="Hub"), ctx["log"]) for t in stamps]
        return pd.concat(parts, ignore_index=True)

    ctx["reports"] = {
        "spp:DA-LMP-SL": ("Day-Ahead LMP by Settlement Location", SPP_DAM_PAGE),
        "spp:RTBM-LMP-SL": ("RTBM LMP by Settlement Location, 5-minute", SPP_RTM_PAGE),
    }
    specs = [
        dict(name="DAM", describe="SPP DA-LMP-SL via SPP.get_lmp_day_ahead_hourly(Hub)",
             fetch=dam, nodes=SPP_HUBS, source="spp:DA-LMP-SL", page=SPP_DAM_PAGE, step="1h",
             minutes=60, forward=True, workers=6, variable="lmp_dam", freq="PT1H",
             market="spp_dam", file="spp_dam_hub_prices",
             title="SPP day-ahead market LMPs, trading hubs"),
        dict(name="RTM", describe="SPP RTBM-LMP-SL via SPP.get_lmp_real_time_5_min_by_location(Hub), "
             "aggregated to 15-minute means", fetch=rtm, nodes=SPP_HUBS, source="spp:RTBM-LMP-SL",
             page=SPP_RTM_PAGE, step="15min", five_min=True, workers=8,
             variable="lmp_rtm_15m_mean", freq="PT15M", market="spp_rtm",
             file="spp_rtm_hub_prices", notes=[FIVE_MIN_NOTE],
             title="SPP real-time balancing market LMPs, trading hubs, 15-minute means of 5-minute prices"),
    ]
    return run_iso(ctx, specs)


# ---------------------------------------------------------------------------
# ISO-NE
# ---------------------------------------------------------------------------

ISONE_NODES = [".H.INTERNAL_HUB", ".Z.CONNECTICUT", ".Z.MAINE", ".Z.NEMASSBOST",
               ".Z.NEWHAMPSHIRE", ".Z.RHODEISLAND", ".Z.SEMASS", ".Z.VERMONT", ".Z.WCMASS"]
ISONE_DAM_PAGE = "https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmps-da-hourly"
ISONE_RTM_PAGE = "https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmps-rt-five-min-final"


def pull_isone(ctx):
    """ISO-NE 8 load zones and the Hub: DA hourly LMP and RT 5-minute LMP."""
    i = gridstatus.ISONE()
    ctx["data_url"] = r"histRpts|static-transform"

    def fetch(market):
        return lambda day: i.get_lmp(date=day, market=market)
    ctx["reports"] = {
        "isone:da_lmp_hourly": ("Day-Ahead Energy Market Hourly LMPs", ISONE_DAM_PAGE),
        "isone:rt_lmp_5min": ("Real-Time Energy Market Five-Minute LMPs", ISONE_RTM_PAGE),
    }
    specs = [
        dict(name="DAM", describe="ISO-NE DA hourly LMP via ISONE.get_lmp(DAY_AHEAD_HOURLY)",
             fetch=fetch(Markets.DAY_AHEAD_HOURLY), nodes=ISONE_NODES,
             source="isone:da_lmp_hourly", page=ISONE_DAM_PAGE, step="1h", minutes=60,
             forward=True, variable="lmp_dam", freq="PT1H", market="isone_dam",
             file="isone_dam_zone_prices",
             title="ISO-NE day-ahead market LMPs, 8 load zones and the Internal Hub"),
        dict(name="RTM", describe="ISO-NE RT 5-minute LMP via ISONE.get_lmp(REAL_TIME_5_MIN), "
             "aggregated to 15-minute means", fetch=fetch(Markets.REAL_TIME_5_MIN),
             nodes=ISONE_NODES, source="isone:rt_lmp_5min", page=ISONE_RTM_PAGE, step="15min",
             five_min=True, variable="lmp_rtm_15m_mean", freq="PT15M", market="isone_rtm",
             file="isone_rtm_zone_prices", notes=[FIVE_MIN_NOTE],
             title="ISO-NE real-time market LMPs, 8 load zones and the Internal Hub, "
                   "15-minute means of 5-minute prices"),
    ]
    return run_iso(ctx, specs)


# ---------------------------------------------------------------------------
# Registry and CLI
# ---------------------------------------------------------------------------

ISOS = {
    # iso: (pull function, display label, local time zone, geo)
    "ercot": (pull_ercot, "ERCOT", ERCOT_TZ, "US-TX"),
    "caiso": (pull_caiso, "CAISO", "America/Los_Angeles", "US-CA"),
    "nyiso": (pull_nyiso, "NYISO", "America/New_York", "US-NY"),
    "miso": (pull_miso, "MISO", "EST", "US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,"
             "US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI"),
    "spp": (pull_spp, "SPP", "America/Chicago", "US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,"
            "US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY"),
    "isone": (pull_isone, "ISO-NE", "America/New_York", "US-CT,US-MA,US-ME,US-NH,US-RI,US-VT"),
}
# MISO publishes its market day in Eastern Standard Time all year (gridstatus
# MISO.default_timezone is "EST"), so its operating days are EST days.


def run(iso, days):
    fn, label, tz, geo = ISOS[iso]
    os.makedirs(LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = Log(os.path.join(LOG_DIR, f"{iso}_prices_{run_id}.log"))
    RAW.open(iso, run_id)
    start, end = window(tz, days)
    log(f"ERW {iso}_prices run {run_id}")
    log(f"gridstatus {gridstatus.__version__}, pandas {pd.__version__}, python {sys.version.split()[0]}")
    log(f"window: {days} operating days, {start} to {end} (exclusive), "
        f"UTC [{utc_iso(start)}, {utc_iso(end)})")
    log(f"raw files: {os.path.relpath(RAW.dir, ROOT)}")
    ctx = dict(iso=iso, label=label, tz=tz, geo=geo, start=start, end=end, run_id=run_id,
               log=log, reports={})
    failures = fn(ctx)
    log(f"done, failures={failures}")
    log.close()
    print(f"{iso} run log: {os.path.relpath(log.path, ROOT)}")
    return failures


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW ISO price connector")
    ap.add_argument("iso", choices=sorted(ISOS) + ["all"],
                    help="ISO to pull (pjm is not supported: it needs an API key)")
    ap.add_argument("--days", type=int, default=30, help="complete operating days (default 30)")
    ap.add_argument("--out-dir", help="write CSVs, logs and raw files under this directory "
                    "instead of the repository (for trial runs)")
    args = ap.parse_args(argv)
    if args.out_dir:
        global OUT_DIR, LOG_DIR, RAW_DIR
        OUT_DIR = os.path.abspath(args.out_dir)
        LOG_DIR = os.path.join(OUT_DIR, "logs")
        RAW_DIR = os.path.join(OUT_DIR, "raw")
        os.makedirs(OUT_DIR, exist_ok=True)
    isos = sorted(ISOS) if args.iso == "all" else [args.iso]
    failures = sum(run(i, args.days) for i in isos)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
