#!/usr/bin/env python3
"""CAISO Today's Outlook: supply by fuel source, hourly (session 73).

Energy Research Warehouse (ERW) connector. Session 68 found that EIA-930's net generation for CAISO fell by about 80 GWh
a day from December 2025 while demand and interchange did not; session 73 dates the break to 2025-12-16 and needs
CAISO's own figures beside EIA's. Reads CAISO's public Today's Outlook history file for each day,
https://www.caiso.com/outlook/history/YYYYMMDD/fuelsource.csv (5-minute MW by source, Pacific wall-clock time), and
writes one series table, caiso_fuel_supply:

    entity    caiso:ISO
    variable  <source>_mw for each of CAISO's columns: solar, wind, geothermal, biomass, biogas, small_hydro, coal,
              nuclear, natural_gas, large_hydro, batteries, imports, other (CAISO's names, lowercased)
    value     the hour's mean of the twelve 5-minute values, MW (so also the hour's MWh); batteries positive when
              discharging, negative when charging, as CAISO publishes them
    freq      PT1H; ts_utc is the hour's start (Pacific hours converted to UTC)

    python warehouse/connectors/caiso_fuel_supply.py --start 2025-06-01            # to yesterday (Pacific)
    python warehouse/connectors/caiso_fuel_supply.py --start 2025-06-01 --dry-run  # count only, nothing written
    python warehouse/connectors/caiso_fuel_supply.py --days 3                      # the daily run: the last 3 Pacific days

Session 82 (Samuel's approval of the small daily pull): --days N pulls the N Pacific days ending yesterday, at most 312
rows a day (13 sources, 24 hours), and merges them into the table on (entity, variable, ts_utc), as the writer does for
every rolling table; the history stays. The daily run calls it before the carbon tables, which from the join read
California's generation here (warehouse/derived/caiso_join.py). On the runner the table is restored from Redivis first
(warehouse/redivis/config.yaml).

Completeness: a day is written only if it has every 5-minute interval of the Pacific operating day (288, or 276 and
300 on the clock-change days); a day that falls short is logged and skipped, never filled. Ceiling: the approved pull
is at most 300,000 rows; the run stops before writing if the table would exceed it. Raw files are stored under
warehouse/raw/caiso_fuel_supply/<run_id>/. License: public (CAISO's public system data; cite "California ISO, Today's
Outlook").
"""

import argparse
import datetime as dt
import io
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "caiso_fuel_supply"
URL = "https://www.caiso.com/outlook/history/{day}/fuelsource.csv"
PAGE = "https://www.caiso.com/todays-outlook/supply"
SOURCE = "caiso:todays_outlook_fuelsource"
TZ = "America/Los_Angeles"
CEILING = 300_000
SOURCES = ["Solar", "Wind", "Geothermal", "Biomass", "Biogas", "Small hydro", "Coal", "Nuclear", "Natural Gas", "Large Hydro",
           "Batteries", "Imports", "Other"]
VAR = {c: c.lower().replace(" ", "_") + "_mw" for c in SOURCES}


def day_rows(day, log):
    url = URL.format(day=day.strftime("%Y%m%d"))

    def call():
        r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0 (ERW research)"})
        if r.status_code != 200:
            raise RuntimeError(f"CAISO outlook HTTP {r.status_code} for {url}")
        return r
    r = ip.with_retries(f"CAISO outlook fuelsource {day}", call, log)
    got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    d = pd.read_csv(io.StringIO(r.text))
    if "Time" not in d.columns or not set(SOURCES) <= set(d.columns):
        raise RuntimeError(f"{url}: columns {list(d.columns)}")
    start = pd.Timestamp(day).tz_localize(TZ)
    end = pd.Timestamp(day + dt.timedelta(days=1)).tz_localize(TZ)
    expected = int((end - start) / pd.Timedelta(minutes=5))
    # the file's Time is a Pacific wall-clock time without an offset (caiso_outlook.py's rule): localize with DST inference
    t = pd.to_datetime(d["Time"].astype(str).str.slice(0, 5), format="%H:%M", errors="coerce")
    ts = (pd.Timestamp(day) + (t - t.dt.normalize())).dt.tz_localize(TZ, ambiguous="infer")
    d = d.assign(ts=ts).dropna(subset=SOURCES + ["ts"])
    if len(d) != expected or d["ts"].duplicated().any():
        return None, f"{day}: {len(d)} of {expected} intervals"
    d["hour"] = d["ts"].dt.tz_convert("UTC").dt.floor("h")
    n = d.groupby("hour").size()
    if (n != 12).any():
        return None, f"{day}: an hour without its twelve intervals"
    h = d.groupby("hour")[SOURCES].mean()
    long = h.reset_index().melt(id_vars=["hour"], value_vars=SOURCES, var_name="col", value_name="value")
    out = pd.DataFrame({
        "entity": "caiso:ISO", "variable": long["col"].map(VAR),
        "ts_utc": long["hour"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value": long["value"].astype(float).round(4), "unit": "MW", "freq": "PT1H", "geo": "US-CA", "market": "",
        "node": "", "source": SOURCE, "source_url": url, "retrieved_at": got, "vintage": ""})
    return out, None


def main(argv=None):
    ap = argparse.ArgumentParser(description="CAISO Today's Outlook supply by fuel source, hourly")
    ap.add_argument("--start", help="first Pacific day, YYYY-MM-DD")
    ap.add_argument("--days", type=int, help="session 82, the daily run: the last N Pacific days, ending yesterday")
    ap.add_argument("--end", help="last Pacific day (default yesterday)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true", help="count the rows the window would hold; no request")
    args = ap.parse_args(argv)
    if bool(args.start) == bool(args.days):
        ap.error("give --start or --days, one of them")
    last = dt.date.fromisoformat(args.end) if args.end else pd.Timestamp.now(tz=TZ).date() - dt.timedelta(days=1)
    first = dt.date.fromisoformat(args.start) if args.start else last - dt.timedelta(days=args.days - 1)
    days = [first + dt.timedelta(days=k) for k in range((last - first).days + 1)]
    most = len(days) * 25 * len(SOURCES)
    print(f"{len(days)} days, {first} to {last}: at most {most:,} rows (ceiling {CEILING:,})")
    if most > CEILING:
        print(f"refused: the window could exceed the approved ceiling of {CEILING:,} rows", file=sys.stderr)
        return 1
    if args.dry_run:
        return 0
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"caiso_fuel_supply_{run_id}.log"))
    ip.RAW.open("caiso_fuel_supply", run_id)
    results = []
    try:
        def one(day):
            time.sleep(0.25)
            try:
                return day, *day_rows(day, log)
            except Exception as exc:
                return day, None, f"{day}: {ip.redact(repr(exc))[:200]}"
        frames, short = [], []
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            for day, rows, why in ex.map(one, days):
                if rows is None:
                    short.append(why)
                    log(f"  skipped {why}")
                else:
                    frames.append(rows)
        if not frames:
            raise RuntimeError(f"no complete day in {first} to {last}: {short[:3]}")
        s = pd.concat(frames, ignore_index=True).sort_values(["variable", "ts_utc"])
        if len(s) > CEILING:
            raise RuntimeError(f"{len(s):,} rows exceed the approved ceiling of {CEILING:,}; nothing written")
        header = [
            "Energy Research Warehouse (ERW): CAISO supply by fuel source, hourly (Today's Outlook)",
            "Shape: series (docs/datastandard.md v0). freq PT1H; ts_utc is the hour's start. value: the mean of the hour's "
            "twelve 5-minute values, MW (also the hour's MWh). Variables are CAISO's columns: solar, wind, geothermal, "
            "biomass, biogas, small_hydro, coal, nuclear, natural_gas, large_hydro, batteries (positive discharging), "
            "imports, other, each _mw.",
            f"Window: this run pulled Pacific days {first} to {last}; the table holds every day pulled since 2025-06-01 (session "
            f"73's approved pull, ceiling {CEILING:,} rows a run; session 82's approved daily pull of the last days, merged in); "
            "a day short of any 5-minute interval is not written"
            + (f" (this run skipped {len(short)}: {'; '.join(short[:5])})" if short else "") + ".",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/caiso_fuel_supply.py",
            f"Run log: warehouse/output/logs/caiso_fuel_supply_{run_id}.log",
            f"Raw files: warehouse/raw/caiso_fuel_supply/{run_id}/ (not in git)",
            f"Source: {SOURCE} California ISO, Today's Outlook, supply by fuel source history files ({URL.format(day='YYYYMMDD')})",
            f"  page: {PAGE}",
            "License: public (CAISO public system data; cite \"California ISO, Today's Outlook\").",
        ]
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        ip.update_sources([dict(source=SOURCE, publisher="California ISO (CAISO)",
                                report="Today's Outlook: supply by fuel source (fuelsource.csv history)", report_url=PAGE,
                                document_list=URL.format(day="YYYYMMDD"), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="supply", status="ok",
                            detail=f"{len(frames)} days, {len(s):,} rows" + (f"; skipped {len(short)}" if short else "")))
        print(f"{NAME}: {len(frames)} days, {len(s):,} rows; skipped {len(short)}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last_line = tb.strip().splitlines()[-1]
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"caiso_fuel_supply {NAME} FAILED, no output file written: {last_line}", file=sys.stderr)
        results.append(dict(table=NAME, market="supply", status="failed", detail=last_line[:300]))
    ip.write_status("caiso_fuel_supply", run_id, results)
    log.close()
    print(f"caiso_fuel_supply run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if any(r["status"] != "ok" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
