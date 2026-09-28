#!/usr/bin/env python3
"""CAISO Today's Outlook: battery storage output, every 5 minutes.

Energy Research Warehouse (ERW) connector, session 23 (for the Automated Analysis template
storage_evening_peak, platform tool 26). EIA-930 carries no battery series for any balancing
authority in the warehouse (the connector maps EIA's BAT fuel type, but EIA returns no BAT rows),
so the storage template reads CAISO's own figure. Reads CAISO's public Today's Outlook history file
for each day, https://www.caiso.com/outlook/history/YYYYMMDD/storage.csv, and writes one series
table, caiso_battery_storage:

    entity    caiso:ISO
    variable  batteries_mw (CAISO's "Total batteries" column),
              standalone_batteries_mw, hybrid_batteries_mw
              Positive is discharge to the grid, negative is charging, as CAISO publishes them.
    freq      PT5M; ts_utc is the interval start (CAISO's "Interval Start", Pacific time, converted)

    python warehouse/connectors/caiso_outlook.py              # the last 30 complete days
    python warehouse/connectors/caiso_outlook.py --days 3

Completeness: a day is written only if it has every 5-minute interval of the Pacific operating day
(288, or 276 and 300 on the clock-change days); a day that falls short is logged and skipped. Each
run merges into the file (new intervals added, the same interval replaced). Raw files are stored under
warehouse/raw/caiso_outlook/<run_id>/. License: public, as the other CAISO tables (CAISO's public
market and system data; cite "California ISO, Today's Outlook").
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "caiso_battery_storage"
URL = "https://www.caiso.com/outlook/history/{day}/storage.csv"
PAGE = "https://www.caiso.com/todays-outlook/supply"
SOURCE = "caiso:todays_outlook_storage"
TZ = "America/Los_Angeles"
COLS = {"Total batteries": "batteries_mw", "Stand-alone batteries": "standalone_batteries_mw", "Hybrid batteries": "hybrid_batteries_mw"}


def day_rows(day, log):
    url = URL.format(day=day.strftime("%Y%m%d"))

    def call():
        r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0 (ERW research)"})
        if r.status_code != 200:
            raise RuntimeError(f"CAISO outlook HTTP {r.status_code} for {url}")
        return r
    r = ip.with_retries(f"CAISO outlook storage {day}", call, log)
    got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    d = pd.read_csv(io.StringIO(r.text))
    if "Time" not in d.columns or not set(COLS) <= set(d.columns):
        raise RuntimeError(f"{url}: columns {list(d.columns)}")
    start = pd.Timestamp(day).tz_localize(TZ)
    end = pd.Timestamp(day + dt.timedelta(days=1)).tz_localize(TZ)
    expected = int((end - start) / pd.Timedelta(minutes=5))
    # the file's Time is a Pacific wall-clock time without an offset; localize with DST inference
    t = pd.to_datetime(d["Time"].astype(str).str.slice(0, 16), format="%H:%M", errors="coerce")
    if t.isna().all():
        t = pd.to_datetime(d["Time"], errors="coerce")
        ts = t.dt.tz_localize(TZ, ambiguous="infer") if t.dt.tz is None else t.dt.tz_convert(TZ)
    else:
        ts = (pd.Timestamp(day) + (t - t.dt.normalize())).dt.tz_localize(TZ, ambiguous="infer")
    d = d.assign(ts=ts).dropna(subset=list(COLS))
    if len(d) != expected or d["ts"].duplicated().any():
        return None, f"{day}: {len(d)} of {expected} intervals"
    long = d.melt(id_vars=["ts"], value_vars=list(COLS), var_name="col", value_name="value")
    out = pd.DataFrame({
        "entity": "caiso:ISO", "variable": long["col"].map(COLS),
        "ts_utc": long["ts"].dt.tz_convert("UTC").dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value": long["value"].astype(float), "unit": "MW", "freq": "PT5M", "geo": "US-CA", "market": "",
        "node": "", "source": SOURCE, "source_url": url, "retrieved_at": got, "vintage": ""})
    return out, None


def main(argv=None):
    ap = argparse.ArgumentParser(description="CAISO Today's Outlook battery storage")
    ap.add_argument("--days", type=int, default=30)
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"caiso_outlook_{run_id}.log"))
    ip.RAW.open("caiso_outlook", run_id)
    results = []
    try:
        today = pd.Timestamp.now(tz=TZ).date()
        frames, short = [], []
        for k in range(args.days, 0, -1):
            day = today - dt.timedelta(days=k)
            try:
                rows, why = day_rows(day, log)
            except Exception as exc:
                why = f"{day}: {ip.redact(repr(exc))[:200]}"
                rows = None
            if rows is None:
                short.append(why)
                log(f"  skipped {why}")
                continue
            frames.append(rows)
            log(f"  {day}: {len(rows) // len(COLS)} intervals")
        if not frames:
            raise RuntimeError(f"no complete day among the last {args.days}: {short[:3]}")
        s = pd.concat(frames, ignore_index=True)
        header = [
            "Energy Research Warehouse (ERW): CAISO battery storage output, 5-minute (Today's Outlook)",
            "Shape: series (docs/datastandard.md v0). freq PT5M; ts_utc is the interval start. MW; positive is "
            "discharge to the grid, negative is charging. batteries_mw is CAISO's Total batteries column; "
            "standalone_batteries_mw and hybrid_batteries_mw are its two parts as CAISO publishes them.",
            f"Window: the last {args.days} complete Pacific days each run, merged into earlier runs; a day short of "
            "any 5-minute interval is not written" + (f" (this run: {'; '.join(short)})" if short else "") + ".",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/caiso_outlook.py",
            f"Run log: warehouse/output/logs/caiso_outlook_{run_id}.log",
            f"Raw files: warehouse/raw/caiso_outlook/{run_id}/ (not in git)",
            f"Source: {SOURCE} California ISO, Today's Outlook, storage history files ({URL.format(day='YYYYMMDD')})",
            f"  page: {PAGE}",
            "License: public (CAISO public system data; cite \"California ISO, Today's Outlook\").",
        ]
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        ip.update_sources([dict(source=SOURCE, publisher="California ISO (CAISO)",
                                report="Today's Outlook: batteries trend (storage.csv history)", report_url=PAGE,
                                document_list=URL.format(day="YYYYMMDD"), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="storage", status="ok",
                            detail=f"{len(frames)} days" + (f"; skipped {len(short)}" if short else "")))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"caiso_outlook {NAME} FAILED, no output file written: {last}", file=sys.stderr)
        results.append(dict(table=NAME, market="storage", status="failed", detail=last[:300]))
    ip.write_status("caiso_outlook", run_id, results)
    log.close()
    print(f"caiso_outlook run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if any(r["status"] != "ok" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
