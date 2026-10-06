#!/usr/bin/env python3
"""Day-ahead energy cleared: what the five connectors of session 136 share.

Energy Research Warehouse (ERW). Each operator that publishes its day-ahead market's cleared energy openly has a
connector of its own (ercot_dam_cleared.py, caiso_dam_cleared.py, nyiso_dam_cleared.py, isone_dam_cleared.py,
spp_dam_cleared.py): its report, its route, its terms quoted, its parsing. Five connectors need the same frame, so
it is here once (CLAUDE.md: no shared code until two connectors need it): the arguments, the pause check, the count
of rows against the pull's ceiling, the freshness test, the table's header, the status record.

Every table is a series, one row an hour:

    entity    <iso>:system (SPP: one entity for each balancing authority area its file names)
    variable  dam_cleared_energy
    value     the operator's own figure for the hour, in the unit the operator gives (MWh, or MW over the hour)
    freq      PT1H; ts_utc is the hour's start
    node      the name of the operator's column or data item the value is read from

An hour the operator does not give is not written. Nothing is filled, summed across hours or estimated. The table is
merged into the one already held (iso_prices.write_csv), so it grows past the window an operator keeps.

MISO is paused (warehouse/metadata/paused_sources.csv) and PJM's data is licensed: neither has a connector here.
"""

import argparse
import datetime as dt
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

VARIABLE = "dam_cleared_energy"
UA = {"User-Agent": "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)"}


class Ceiling(RuntimeError):
    pass


class Counter:
    """The rows read from the operator in this run, against the run's ceiling. Past it the run stops and writes nothing."""

    def __init__(self, ceiling):
        self.ceiling, self.read = ceiling, 0

    def add(self, n, what=""):
        self.read += int(n)
        if self.read > self.ceiling:
            raise Ceiling(f"{self.read:,} rows read, past this run's ceiling of {self.ceiling:,}{' at ' + what if what else ''}")

    def room(self, n):
        return self.read + int(n) <= self.ceiling


def reused(rec):
    """True when iso_prices.fetch_raw answered from a raw file an earlier run kept: no row crossed the wire again."""
    return bool(rec.get("file"))


def row(spec, entity, ts, value, node, url, retrieved, unit=None):
    return dict(entity=entity, variable=VARIABLE, ts_utc=ip.utc_iso(ts), value=float(value), unit=unit or spec["unit"], freq="PT1H", geo=spec["geo"],
                market=f"{spec['iso']}_dam", node=node, source=spec["source"], source_url=url, retrieved_at=retrieved, vintage="")


def run(spec, pull, argv=None):
    """One connector's run. spec: iso, name, connector, source, entry (the registry's row), unit, geo, days (the days
    asked for by default), ceiling (rows a run may read), stale_days, what (the header's first line), notes (header
    lines), license (the header's license line). pull(log, days, counter) returns the rows."""
    ap = argparse.ArgumentParser(description=spec["what"])
    ap.add_argument("--days", type=int, default=spec["days"], help=f"how many days back to ask for (default {spec['days']})")
    ap.add_argument("--ceiling", type=int, default=spec["ceiling"], help=f"the rows this run may read (default {spec['ceiling']:,})")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name, connector = spec["name"], spec["connector"]
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{connector}_{run_id}.log"))
    results = []
    held = ip.paused(spec["iso"])
    if held:
        log(f"{spec['iso']} is paused since {held.get('paused_on')}: no request is made")
        print(f"{connector}: {spec['iso']} is paused; no request made")
        results.append(dict(table=name, market="all", status="skipped", detail="the publisher's pulls are paused"))
        ip.write_status(connector, run_id, results)
        log.close()
        return 0
    ip.RAW.open(connector, run_id)
    counter = Counter(args.ceiling)
    try:
        rows = pull(log, args.days, counter)
        s = pd.DataFrame(rows, columns=ip.SERIES_COLS)
        if s.empty:
            raise RuntimeError("the operator answered no hour")
        dup = s.duplicated(["entity", "variable", "ts_utc"])
        if dup.any():
            raise RuntimeError(f"{int(dup.sum())} hours given twice, for example {s.loc[dup, 'ts_utc'].iloc[0]}")
        age = (pd.Timestamp.now(tz="UTC") - pd.Timestamp(s["ts_utc"].max())).days
        if age > spec["stale_days"]:
            raise RuntimeError(f"the newest hour the operator gave is {s['ts_utc'].max()}, {age} days old (limit {spec['stale_days']})")
        header = [
            f"Energy Research Warehouse (ERW): {spec['what']} (session 136)",
            "Shape: series (docs/datastandard.md v0). variable dam_cleared_energy: the operator's own figure for the hour, in the unit it gives; freq PT1H, ts_utc the hour's start. "
            "An hour the operator does not give is not written; nothing is filled or estimated. The table is merged into the one held, so it grows past the window the operator keeps.",
            *spec["notes"],
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/{connector}.py",
            f"Run log: warehouse/output/logs/{connector}_{run_id}.log",
            f"Raw files: warehouse/raw/{connector}/ (not in git)",
            f"Source: {spec['source']} {spec['entry']['publisher']}, {spec['entry']['report']}, {spec['entry']['report_url']}",
            f"  access: {spec['entry']['document_list']}",
            f"Rows read from the operator in this run: {counter.read:,} (this run's ceiling {args.ceiling:,}). Hours written by this run: {len(s):,}, {s['ts_utc'].min()} to {s['ts_utc'].max()}.",
            spec["license"],
        ]
        ip.write_csv(s[ip.SERIES_COLS], name, header, log)
        if not args.out_dir:
            ip.update_sources([spec["entry"]])
        results.append(dict(table=name, market="all", status="ok", detail=f"{len(s):,} hours; {counter.read:,} rows read"))
        print(f"{name}: {len(s):,} hours, {s['ts_utc'].min()[:10]} to {s['ts_utc'].max()[:10]}; rows read {counter.read:,}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{connector} FAILED, no output file written: {tb.strip().splitlines()[-1]}; rows read {counter.read:,}", file=sys.stderr)
        results.append(dict(table=name, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(connector, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1
