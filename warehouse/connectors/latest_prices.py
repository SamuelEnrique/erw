#!/usr/bin/env python3
"""The newest real-time price per ISO hub or zone, for Supabase's latest_prices (session 10).

Energy Research Warehouse (ERW). Run every 15 minutes by
.github/workflows/latest-prices.yml, and nothing else runs there.

    python warehouse/connectors/latest_prices.py
    python warehouse/connectors/latest_prices.py --no-upsert     # fetch and mirror locally only

For each hub or zone already in the ERW's real-time tables (the node lists in
iso_prices.py), it takes the newest real-time interval the ISO has published:
gridstatus's "latest" methods where they exist (Ercot.get_spp, CAISO, NYISO,
MISO and ISONE get_lmp with date="latest", SPP
get_lmp_real_time_5_min_by_location with date="latest"). Each row:
entity, variable, ts_utc (interval start, UTC), value, unit, source,
retrieved_at, license. Variables: ERCOT `spp_rtm` (its settlement interval is 15
minutes); the others `lmp_rtm_5min`, the single newest 5-minute price (the ERW
tables hold 15-minute means or hourly prices, a different variable).

CAISO's variable stays `lmp_rtm_5min` (session 13). Session 11 asked whether it
should be `lmp_rtm_15min`, because its newest interval often starts a minute or
two after the time it was fetched, and the intervals seen then happened to fall
on quarter hours. The human ruled to relabel it. Session 13 checked the source
before changing anything, and the source says 5 minutes:
- `get_lmp(date="today", market=REAL_TIME_5_MIN)` for TH_SP15_GEN-APND on
  2026-09-26 returned 108 intervals, every one 5 minutes long (CAISO's own
  interval start and end), 5 minutes apart;
- the newest interval, fetched at 15:54:49 UTC, was 15:55 to 16:00 UTC.
CAISO publishes each binding 5-minute (RTD) price shortly before its interval
begins, so a newest interval that starts after the fetch is expected. A 15-minute
label would be wrong; the ruling rested on the session 11 guess, and the report
of session 13 says so.

No completeness rule: this is a live board, not a table of record. An ISO that
fails or returns none of its hubs is logged and skipped; the others are still
written. The rows are upserted into latest_prices (one row per entity and
variable; with SUPABASE_URL and SUPABASE_SERVICE_KEY) and mirrored to
runs/latest_prices.csv, where a row is replaced only by a newer interval.
Exit 1 if no ISO returned a price or the upsert failed.
"""

import argparse
import datetime as dt
import os
import sys
import traceback
import urllib.parse

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

import gridstatus  # noqa: E402
from gridstatus import Markets  # noqa: E402

MIRROR = os.path.join(ip.ROOT, "runs", "latest_prices.csv")
COLS = ["entity", "variable", "ts_utc", "value", "unit", "source", "retrieved_at", "license"]
INTERNAL = {"pjm"}  # ISOs whose data are licensed for internal use only (license_of in iso_prices)


def fetchers():
    """ISO -> (callable returning a gridstatus frame, price column, node list, variable, source)."""
    return {
        "ercot": (lambda: gridstatus.Ercot().get_spp(date="latest", market=Markets.REAL_TIME_15_MIN,
                                                     location_type="Trading Hub"),
                  "SPP", ip.ERCOT_HUBS, "spp_rtm", "ercot:NP6-905-CD"),
        "caiso": (lambda: gridstatus.CAISO().get_lmp(date="latest", market=Markets.REAL_TIME_5_MIN,
                                                     locations=ip.CAISO_HUBS),
                  "LMP", ip.CAISO_HUBS, "lmp_rtm_5min", "caiso:PRC_INTVL_LMP"),
        "nyiso": (lambda: gridstatus.NYISO().get_lmp(date="latest", market=Markets.REAL_TIME_5_MIN,
                                                     location_type="zone"),
                  "LMP", ip.NYISO_ZONES, "lmp_rtm_5min", "nyiso:realtime"),
        "miso": (lambda: gridstatus.MISO().get_lmp(date="latest", market=Markets.REAL_TIME_5_MIN, locations="ALL"),
                 "LMP", ip.MISO_HUBS, "lmp_rtm_5min", "miso:rt_lmp_5min_latest"),
        "spp": (lambda: gridstatus.SPP().get_lmp_real_time_5_min_by_location(date="latest", location_type="Hub"),
                "LMP", ip.SPP_HUBS, "lmp_rtm_5min", "spp:RTBM-LMP-SL"),
        "isone": (lambda: gridstatus.ISONE().get_lmp(date="latest", market=Markets.REAL_TIME_5_MIN),
                  "LMP", ip.ISONE_NODES, "lmp_rtm_5min", "isone:lmps-rt-five-min-prelim"),
    }


def rows_for(iso, df, col, nodes, variable, source, got, log):
    d = df[df["Location"].isin(nodes)].copy()
    if d.empty:
        raise RuntimeError(f"none of the ERW's {len(nodes)} nodes in the ISO's latest data")
    d["ts"] = pd.to_datetime(d["Interval Start"], utc=True)
    d = d.sort_values("ts").groupby("Location").tail(1)  # the newest interval per node
    missing = sorted(set(nodes) - set(d["Location"]))
    if missing:
        log(f"  {iso}: no latest price for {missing}")
    return [dict(entity=f"{iso}:{r.Location}", variable=variable, ts_utc=r.ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                 value=float(r[col]), unit="USD/MWh", source=source, retrieved_at=got,
                 license="internal" if iso in INTERNAL else "public")
            for _, r in d.iterrows()]


def mirror(rows):
    new = pd.DataFrame(rows, columns=COLS)
    if os.path.exists(MIRROR):
        old = pd.read_csv(MIRROR, dtype={"value": float}, keep_default_na=False)
        both = pd.concat([old, new], ignore_index=True)
    else:
        both = new
    both = both.sort_values(["entity", "variable", "ts_utc", "retrieved_at"]) \
        .groupby(["entity", "variable"]).tail(1).sort_values("entity")
    os.makedirs(os.path.dirname(MIRROR), exist_ok=True)
    both[COLS].to_csv(MIRROR, index=False, lineterminator="\n")
    return both


def upsert(rows):
    from dotenv import dotenv_values
    env = {**dotenv_values(os.path.join(ip.ROOT, ".env")), **os.environ}
    url, key = (env.get("SUPABASE_URL") or "").strip(), (env.get("SUPABASE_SERVICE_KEY") or "").strip()
    if not url or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_KEY is not set")
    from supabase import create_client
    u = urllib.parse.urlparse(url)
    client = create_client(f"{u.scheme}://{u.netloc}", key)
    client.table("latest_prices").upsert(rows, on_conflict="entity,variable").execute()


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW latest real-time prices")
    ap.add_argument("--no-upsert", action="store_true", help="fetch and mirror locally only")
    args = ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"latest_prices_{run_id}.log"))
    rows = []
    for iso, (fn, col, nodes, variable, source) in fetchers().items():
        if ip.paused(iso):  # session 89: no request; the publisher's last row in latest_prices stays as it is
            log(f"{iso}: {ip.pause_line(iso)}")
            continue
        try:
            got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
            r = rows_for(iso, fn(), col, nodes, variable, source, got, log)
            rows += r
            log(f"{iso}: {len(r)} of {len(nodes)} nodes, newest interval {max(x['ts_utc'] for x in r)}")
        except Exception as exc:
            log(f"{iso}: MISSING, no latest price this run: {type(exc).__name__}: {str(exc)[:300]}")
            log(traceback.format_exc())
    if not rows:
        log("no ISO returned a latest price")
        log.close()
        return 1
    table = mirror(rows)
    log(f"mirror {os.path.relpath(MIRROR, ip.ROOT)}: {len(table)} rows")
    rc = 0
    if not args.no_upsert:
        try:
            upsert(rows)
            log(f"upserted {len(rows)} rows into Supabase latest_prices")
        except Exception as exc:
            log(f"UPSERT FAILED: {type(exc).__name__}: {str(exc)[:300]}")
            print(f"latest_prices upsert FAILED: {type(exc).__name__}: {str(exc)[:200]}", file=sys.stderr)
            rc = 1
    log(f"done: {len(rows)} rows from {len({r['entity'].split(':')[0] for r in rows})} ISOs")
    log.close()
    print(f"latest_prices: {len(rows)} rows; run log {os.path.relpath(log.path, ip.ROOT)}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
