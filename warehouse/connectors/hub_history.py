#!/usr/bin/env python3
"""A year of main-hub prices, kept as history past the rolling window (session 49, approved pull b).

Energy Research Warehouse (ERW) connector. Writes one series table,

    warehouse/output/iso_hub_prices_history.csv    partition column market (caiso_dam, caiso_rtm, miso_dam, ...)

with the day-ahead and real-time prices of the main hubs from 2025-09-01: CAISO SP15 (TH_SP15_GEN-APND) and the NP15
zone (TH_NP15_GEN-APND), MISO Indiana Hub, NYISO N.Y.C., ISO-NE .H.INTERNAL_HUB and SPP SPPNORTH_HUB. ERCOT's history
is ercot_all_hub_prices_history (session 8).

    python warehouse/connectors/hub_history.py backfill [--iso caiso ...]   # the pull, 2025-09-01 to yesterday
    python warehouse/connectors/hub_history.py append                       # the daily run: the live tables' rows

backfill reuses each ISO's own pull in warehouse/connectors/iso_prices.py (the same reports, raw capture, per-row
source_url and vintage, 5-minute prices as 15-minute means, NYISO's time-weighting), with the node lists narrowed to
the hubs above, the window widened to 2025-09-01, and the per-day completeness rule for every market (session 13): a
day is written only when every interval of every hub is there. It works a calendar month at a time and writes after
each month, so an interrupted pull resumes at the first month the table does not hold. Ceiling 1.5 million rows.

Session 64: the second year (2024-09-01 to 2025-08-31, --start 2024-09-01 --until 2025-09-01). SPP no longer serves
2024's daily files at their own paths (HTTP 404): it keeps each finished year as one archive per report
(<report>?path=/2024/2024.zip; 294 MB for the day-ahead, 5.15 GB for the real-time). For an SPP day whose daily file
answers 404, spp_archive() reads the same daily file (By_Day/...) out of the year's archive with HTTP range requests: the
archive's directory once, then only that member's bytes, so a day costs about its own compressed size (0.6 MB day-ahead,
7 MB real-time). The rows' source_url is the archive's URL; the member is the daily file the 404 named.

append merges the rows of the hubs above from the live rolling tables (iso_dam_hub_prices, iso_rtm_hub_prices,
nyiso_*_zone_prices, isone_*_zone_prices) into the history: the history grows by merging and is never trimmed.
"""

import argparse
import datetime as dt
import glob
import os
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "iso_hub_prices_history"
START = "2025-09-01"
CEILING = 1_500_000
TARGETS = {  # iso: (iso_prices node list name, the hubs kept)
    "caiso": ("CAISO_HUBS", ["TH_NP15_GEN-APND", "TH_SP15_GEN-APND"]),
    "miso": ("MISO_HUBS", ["INDIANA.HUB"]),
    "nyiso": ("NYISO_ZONES", ["N.Y.C."]),
    "isone": ("ISONE_NODES", [".H.INTERNAL_HUB"]),
    "spp": ("SPP_HUBS", ["SPPNORTH_HUB"]),
}
LIVE = {  # market: the live table holding it
    "caiso_dam": "iso_dam_hub_prices", "caiso_rtm": "iso_rtm_hub_prices", "miso_dam": "iso_dam_hub_prices",
    "miso_rtm": "iso_rtm_hub_prices", "spp_dam": "iso_dam_hub_prices", "spp_rtm": "iso_rtm_hub_prices",
    "nyiso_dam": "nyiso_dam_zone_prices", "nyiso_rtm": "nyiso_rtm_zone_prices",
    "isone_dam": "isone_dam_zone_prices", "isone_rtm": "isone_rtm_zone_prices",
}
ENTITIES = {f"{iso}:{n}" for iso, (_, nodes) in TARGETS.items() for n in nodes}


class _Remote:
    """A file-like view of a URL that serves byte ranges, for zipfile to read an archive's directory."""

    def __init__(self, url):
        import requests
        self.url, self.pos, self.rq = url, 0, requests
        h = requests.get(url, headers={"Range": "bytes=0-0"}, timeout=120)
        if h.status_code != 206:
            raise RuntimeError(f"{url}: no byte ranges (HTTP {h.status_code})")
        self.size = int(h.headers["Content-Range"].split("/")[1])

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.size + off
        return self.pos

    def read(self, n=-1):
        n = self.size - self.pos if n is None or n < 0 else min(n, self.size - self.pos)
        if n <= 0:
            return b""
        r = self.rq.get(self.url, headers={"Range": f"bytes={self.pos}-{self.pos + n - 1}"}, timeout=300)
        if r.status_code != 206:
            raise RuntimeError(f"{self.url}: range read HTTP {r.status_code}")
        self.pos += len(r.content)
        return r.content


_ARCHIVES = {}


def _archive_member(archive_url, member):
    """The bytes of one member of a remote zip: the directory read once per archive (cached), then the member's local
    header and data by range."""
    import struct
    import threading
    import zipfile
    import zlib
    import requests
    if archive_url not in _ARCHIVES:
        _ARCHIVES.setdefault("_lock", threading.Lock())
        with _ARCHIVES["_lock"]:
            if archive_url not in _ARCHIVES:
                import io
                z = zipfile.ZipFile(io.BufferedReader(_RawAdapter(_Remote(archive_url)), buffer_size=1 << 20))
                _ARCHIVES[archive_url] = {i.filename: i for i in z.infolist()}
    info = _ARCHIVES[archive_url].get(member)
    if info is None:
        raise FileNotFoundError(f"{member} is not in {archive_url}")
    get = lambda a, b: requests.get(archive_url, headers={"Range": f"bytes={a}-{b}"}, timeout=600)  # noqa: E731
    head = get(info.header_offset, info.header_offset + 29).content
    n, m = struct.unpack("<HH", head[26:30])
    start = info.header_offset + 30 + n + m
    data = get(start, start + info.compress_size - 1).content
    if len(data) != info.compress_size:
        raise RuntimeError(f"{member}: {len(data)} of {info.compress_size} bytes")
    out = zlib.decompress(data, -15) if info.compress_type == zipfile.ZIP_DEFLATED else data
    if zlib.crc32(out) != info.CRC:
        raise RuntimeError(f"{member}: CRC mismatch")
    return out


def _raw_adapter():
    import io

    class RawAdapter(io.RawIOBase):
        def __init__(self, remote):
            self.r = remote

        def seekable(self):
            return True

        def readable(self):
            return True

        def tell(self):
            return self.r.tell()

        def seek(self, off, whence=0):
            return self.r.seek(off, whence)

        def readinto(self, b):
            d = self.r.read(len(b))
            b[:len(d)] = d
            return len(d)
    return RawAdapter


_RawAdapter = _raw_adapter()


def spp_archive():
    """Session 64: pandas.read_csv wrapped so that an SPP daily file answering 404 is read from its year's archive
    (<report>?path=/<year>/<year>.zip, member <year>/<month>/By_Day/<file>). Installed for SPP backfills only."""
    import io
    import re
    import urllib.error
    orig = pd.read_csv
    pat = re.compile(r"^(https://portal\.spp\.org/file-browser-api/download/[a-z-]+)\?path=/((\d{4})/\d{2}/By_Day/[^/]+\.csv)$")

    def read_csv(src, *a, **k):
        m = pat.match(src) if isinstance(src, str) else None
        if not m:
            return orig(src, *a, **k)
        try:
            return orig(src, *a, **k)
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
        return orig(io.BytesIO(_archive_member(f"{m.group(1)}?path=/{m.group(3)}/{m.group(3)}.zip", m.group(2))), *a, **k)
    pd.read_csv = read_csv
    return orig


def held_days(market, tz):
    """The local days the history already holds for a market (resume)."""
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if not os.path.exists(path):
        return set()
    s = ip.read_series(path)
    s = s[s["market"] == market]
    if not len(s):
        return set()
    return set(pd.to_datetime(s["ts_utc"], utc=True).dt.tz_convert(tz).dt.strftime("%Y-%m-%d"))


WORKERS = {"caiso": 1, "miso": 6, "nyiso": 4, "isone": 6, "spp": 8}  # CAISO OASIS resets under parallel load


def month(ctx, spec, m0, m1, workers):
    """One calendar month of one market, its days fetched in parallel, each day checked and kept only if complete, as
    iso_prices.run_market_per_day does it (session 13); the complete days merged into the table. [(day, reason)] back."""
    from concurrent.futures import ThreadPoolExecutor
    log, nodes, tz = ctx["log"], spec["nodes"], ctx["tz"]
    days = list(pd.date_range(m0, m1, freq="D", inclusive="left"))

    def one(day):
        try:
            rows, _ = ip.pull_days([day], spec["fetch"], nodes, spec["source"], spec["page"], log,
                                   what=spec["name"], data_url=ctx.get("data_url"))
            return day, rows, None
        except Exception as exc:
            return day, None, exc
    with ThreadPoolExecutor(max_workers=workers) as pool:
        got = list(pool.map(one, days))
    parts, gaps = [], []
    for day, rows, exc in got:
        d0 = pd.Timestamp(day.date()).tz_localize(tz)
        d1 = pd.Timestamp(day.date() + dt.timedelta(days=1)).tz_localize(tz)
        try:
            if exc is not None:
                raise exc
            rows = rows[(rows["interval_start"] >= d0) & (rows["interval_start"] < d1)]
            rows = ip.latest_per_key(rows, log)
            if spec.get("irregular"):
                rows = ip.rebuild_irregular_intervals(rows, d0, d1, nodes, log)
                rows = ip.to_15min_means(ip.split_at_quarters(rows), log)
            elif spec.get("five_min"):
                ip.check_interval_length(rows, 5, log)
                rows = ip.to_15min_means(rows, log)
            elif "minutes" in spec:
                ip.check_interval_length(rows, spec["minutes"], log)
            ip.check_complete(rows, nodes, d0, d1, spec["step"], log)
            parts.append(rows[["node", "interval_start", "value", "source", "source_url", "retrieved_at", "vintage"]])
        except Exception as e:
            reason = " ".join(str(e).split()).replace("incomplete data, no file written: ", "day incomplete: ")[:250]
            gaps.append((str(day.date()), reason))
            log(f"  GAP {spec['name']} {day.date()}: not written ({reason})")
    if parts:
        rows = pd.concat(parts, ignore_index=True)
        srs = ip.to_series(rows, ctx["iso"], spec["variable"], spec["freq"], spec["market"], ctx["geo"])
        ip.write_csv(srs, NAME, ip.header(ctx["label"], spec["title"], ctx["run_id"], ctx["iso"], m0, m1, tz,
                                          ip.source_lines(rows, ctx["reports"]), spec.get("notes", [])), log)
    log(f"  {ctx['iso']} {spec['name']} {m0:%Y-%m}: {len(parts)} complete days written, {len(gaps)} not")
    return gaps


def backfill(isos, until=None):
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"hub_history_{run_id}.log"))
    results, reports = [], {}
    log(f"ERW hub_history backfill {run_id}: {', '.join(isos)} from {START}; ceiling {CEILING} rows")
    for iso in isos:
        fn, label, tz, geo = ip.ISOS[iso]
        listname, nodes = TARGETS[iso]
        setattr(ip, listname, nodes)  # the pull functions read their node list at call time
        if iso == "spp":  # session 64: 2024's daily files are only in the year's archive
            spp_archive()
        ip.RAW.open(f"hub_history_{iso}", run_id)
        end = pd.Timestamp(until).tz_localize(tz) if until else ip.window(tz, 1)[1]
        captured = []

        def run_specs(ctx, specs, iso=iso, tz=tz, end=end):
            failures = 0
            ctx["specs"] = specs
            for spec in [s for s in specs if s["name"] in ("DAM", "RTM")]:
                spec = dict(spec, per_day=True, file=NAME, nodes=TARGETS[iso][1])
                have = held_days(spec["market"], tz)
                m0 = pd.Timestamp(START).tz_localize(tz)
                written = gaps = 0
                while m0 < end:
                    m1 = min(end, (m0 + pd.offsets.MonthBegin(1)).normalize().tz_localize(None).tz_localize(tz))
                    days = pd.date_range(m0, m1, freq="D", inclusive="left").strftime("%Y-%m-%d")
                    if all(d in have for d in days):
                        log(f"{iso} {spec['name']} {m0:%Y-%m}: held, skipped")
                    else:
                        try:
                            g = month(ctx, spec, m0, m1, WORKERS[iso])
                            gaps += len(g)
                            written += len(days) - len(g)
                            for day, reason in g:
                                results.append(dict(table=NAME, market=f"{spec['market']} {day}", status="gap", detail=reason))
                        except Exception:
                            failures += 1
                            last = traceback.format_exc().strip().splitlines()[-1]
                            log(f"{iso} {spec['name']} {m0:%Y-%m} FAILED: {last}")
                            results.append(dict(table=NAME, market=f"{spec['market']} {m0:%Y-%m}", status="failed", detail=last[:300]))
                    m0 = m1
                log(f"{iso} {spec['name']}: {written} days written this run, {gaps} not complete")
                results.append(dict(table=NAME, market=spec["market"], status="ok",
                                    detail=f"{written} days written, {gaps} not complete"))
                captured.append(spec)
            return failures

        orig = ip.run_iso
        ip.run_iso = run_specs
        try:
            ctx = dict(iso=iso, label=label, tz=tz, geo=geo, start=pd.Timestamp(START).tz_localize(tz), end=end,
                       run_id=run_id, log=log, reports={}, results=[], specs=[])
            fn(ctx)
            reports.update(ctx["reports"])
        except Exception:
            last = traceback.format_exc().strip().splitlines()[-1]
            log(f"{iso} FAILED: {last}")
            results.append(dict(table=NAME, market=iso, status="failed", detail=last[:300]))
        finally:
            ip.run_iso = orig
        n = len(ip.read_series(os.path.join(ip.OUT_DIR, NAME + ".csv"))) if os.path.exists(os.path.join(ip.OUT_DIR, NAME + ".csv")) else 0
        log(f"after {iso}: the history holds {n:,} rows")
        if n > CEILING:
            log(f"STOP: {n:,} rows, over the {CEILING:,} ceiling")
            results.append(dict(table=NAME, market="all", status="failed", detail=f"over the ceiling: {n} rows"))
            break
    rewrite_header(run_id, reports, log)
    ip.update_sources([dict(source=sid, publisher=ip.ISO_PUBLISHERS.get(sid.split(":")[0], sid.split(":")[0]), report=name,
                            report_url=page, document_list="", tables=[NAME]) for sid, (name, page) in reports.items()])
    ip.write_status("hub_history", run_id, results)
    log.close()
    return 0 if all(r["status"] != "failed" for r in results) else 1


def rewrite_header(run_id, reports, log):
    """One provenance header for every market of the table: each report's line, from the rows' own sources."""
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    n = 0
    while n < len(lines) and lines[n].startswith("#"):
        n += 1
    old = [ln[1:].strip() for ln in lines[:n]]
    s = ip.read_series(path)
    known = {}
    for ln in old:  # keep report names of earlier runs
        if ln.startswith("Source: "):
            sid, rest = ln[8:].split(" ", 1)
            known[sid] = rest
    for sid, (name, page) in reports.items():
        known[sid] = f"{name}, {page}"
    span = s.groupby("market")["ts_utc"].agg(["min", "max", "size"])
    hdr = [
        "Energy Research Warehouse (ERW): main-hub day-ahead and real-time prices, history from "
        f"{str(s['ts_utc'].min())[:10]} (session 49 from 2025-09-01; session 64 the year before, from 2024-09-01): "
        "CAISO SP15 and NP15, MISO Indiana Hub, NYISO N.Y.C., ISO-NE .H.INTERNAL_HUB, SPP SPPNORTH_HUB",
        "Shape: series (docs/datastandard.md v0), partition column market. Units: USD/MWh. ts_utc is interval start, UTC. "
        "lmp_dam hourly; real-time lmp_rtm_15m_mean (15-minute means of 5-minute prices; NYISO time-weighted) or "
        "MISO's hourly lmp_rtm.",
        "Markets: " + "; ".join(f"{m} {r['size']:,} rows, {str(r['min'])[:10]} to {str(r['max'])[:10]}" for m, r in span.iterrows()),
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/hub_history.py (each ISO's pull in iso_prices.py, via gridstatus "
        f"{ip.gridstatus.__version__}); earlier and later days by earlier runs and the daily append",
        f"Run log: warehouse/output/logs/hub_history_{run_id}.log; the backfills' logs: "
        + (", ".join(sorted({os.path.basename(x) for x in glob.glob(os.path.join(ip.LOG_DIR, "hub_history_2*.log"))})) or "none here"),
        "Raw files: " + (", ".join(sorted({os.path.relpath(x, ip.ROOT).replace(os.sep, "/") for x in
                                          glob.glob(os.path.join(ip.RAW_DIR, "hub_history_*", "*"))})) or "none on this machine")
        + " (not in git; each manifest.csv lists each file and URL)",
    ] + [f"Source: {sid} {rest}" for sid, rest in sorted(known.items()) if sid in set(s["source"])] + [
        "Completeness per operating day (session 13): a day is written only when every interval of every hub is there; "
        "each day not written is a gap row in warehouse/metadata/run_status.csv.",
        ip.FIVE_MIN_NOTE, ip.NYISO_RT_NOTE,
        "Session 64: SPP's 2024 days are read from SPP's archive of the year (<report>?path=/2024/2024.zip), the same daily "
        "file (By_Day) the 404'd path named, by HTTP range; those rows' source_url is the archive's URL.",
        "History: the daily run merges the live tables' rows of these hubs into this table (hub_history.py append); never trimmed.",
    ]
    with open(path + ".tmp", "w", encoding="utf-8", newline="") as f:
        f.writelines("# " + h + "\n" for h in hdr)
        f.writelines(lines[n:])
    os.replace(path + ".tmp", path)
    log(f"header rewritten: {len(s):,} rows")


def append():
    """The daily run: merge the live tables' rows of the target hubs into the history (never trims)."""
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"hub_history_append_{run_id}.log"))
    results = []
    try:
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if not os.path.exists(path):
            raise RuntimeError(f"{NAME} is not on this machine (restored from the Redivis draft on the runner)")
        parts = []
        for table in sorted(set(LIVE.values())):
            p = os.path.join(ip.OUT_DIR, table + ".csv")
            if not os.path.exists(p):
                log(f"  {table}: not on this machine, skipped")
                continue
            t = ip.read_series(p)
            t = t[t["entity"].isin(ENTITIES) & t["market"].isin([m for m, tb in LIVE.items() if tb == table])]
            parts.append(t)
            log(f"  {table}: {len(t)} rows of the target hubs")
        rows = pd.concat(parts, ignore_index=True)
        with open(path, encoding="utf-8") as f:
            hdr = [ln[1:].strip() for ln in f if ln.startswith("#")]
        before = len(ip.read_series(path))
        ip.write_csv(rows[ip.SERIES_COLS], NAME, hdr, log)
        after = len(ip.read_series(path))
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{after - before} rows added ({before} to {after})"))
        print(f"hub_history append: {before:,} -> {after:,} rows")
    except Exception:
        last = traceback.format_exc().strip().splitlines()[-1]
        log(f"FAILED: {last}")
        print(f"hub_history append FAILED: {last}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=last[:300]))
    ip.write_status("hub_history_append", run_id, results)
    log.close()
    return 0 if results[-1]["status"] == "ok" else 1


def reports_of(isos):
    """Each ISO's report list, as its pull function registers it, without pulling: run_iso is replaced by a no-op."""
    reports = {}
    orig = ip.run_iso
    ip.run_iso = lambda ctx, specs: 0
    try:
        for iso in isos:
            fn, label, tz, geo = ip.ISOS[iso]
            ctx = dict(iso=iso, label=label, tz=tz, geo=geo, start=pd.Timestamp(START).tz_localize(tz),
                       end=pd.Timestamp(START).tz_localize(tz), run_id="", log=lambda *a: None, reports={}, results=[], specs=[])
            fn(ctx)
            reports.update(ctx["reports"])
    finally:
        ip.run_iso = orig
    return reports


def header_and_sources(src_dirs=()):
    """Session 49: the combined header and the source registry, for a history built by runs that ended early (a
    stopped run leaves the last month's single-ISO header) or merged from other directories (merge)."""
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"hub_history_header_{run_id}.log"))
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    s = ip.read_series(path)
    isos = sorted({e.split(":")[0] for e in s["entity"]})
    reports = reports_of(isos)
    reports = {sid: v for sid, v in reports.items() if sid in set(s["source"])}
    rewrite_header(run_id, reports, log)
    ip.update_sources([dict(source=sid, publisher=ip.ISO_PUBLISHERS.get(sid.split(":")[0], sid.split(":")[0]), report=name,
                            report_url=page, document_list="", tables=[NAME]) for sid, (name, page) in reports.items()])
    log(f"sources: {', '.join(sorted(reports))}; merged from: {', '.join(src_dirs) or 'none'}")
    log.close()
    print(f"hub_history header: {len(s):,} rows, {len(reports)} sources")
    return 0


def merge(src_dirs):
    """Session 49: merge the history built in other directories (backfills run in parallel, one ISO each) into this
    one, by key, then rewrite the header. Their run logs stay where they were written; the header names this run."""
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"hub_history_merge_{run_id}.log"))
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    with open(path, encoding="utf-8") as f:
        hdr = [ln[1:].strip() for ln in f if ln.startswith("#")]
    for d in src_dirs:
        p = os.path.join(d, NAME + ".csv")
        t = ip.read_series(p)
        t = t[t["entity"].isin(ENTITIES)]
        log(f"merge {p}: {len(t):,} rows, " + ", ".join(f"{m} {n:,}" for m, n in t.groupby('market').size().items()))
        ip.write_csv(t[ip.SERIES_COLS], NAME, hdr, log)
    log.close()
    return header_and_sources(src_dirs)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW main-hub price history (session 49)")
    ap.add_argument("cmd", choices=["backfill", "append", "header", "merge"])
    ap.add_argument("--from", dest="src", action="append", default=[], help="merge: a directory holding a history to merge")
    ap.add_argument("--iso", action="append", choices=list(TARGETS))
    ap.add_argument("--until", help="backfill: the first local day not pulled (YYYY-MM-DD); default today")
    ap.add_argument("--start", help="backfill: a later first day, for a trial (default 2025-09-01)")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    global START
    if args.start:
        START = args.start
    if args.cmd == "append":
        return append()
    if args.cmd == "header":
        return header_and_sources()
    if args.cmd == "merge":
        return merge(args.src)
    return backfill(args.iso or list(TARGETS), args.until)


if __name__ == "__main__":
    sys.exit(main())
