#!/usr/bin/env python3
"""CAISO Today's Outlook: supply by fuel source, hourly, June 2018 to May 2025 (session 133, approved pull).

Energy Research Warehouse (ERW) connector. The same file, the same reading and the same completeness rule as
caiso_fuel_supply.py (session 73), for the days before that table begins: one request a Pacific day to
https://www.caiso.com/outlook/history/YYYYMMDD/fuelsource.csv, the hour's mean of its twelve 5-minute values, a day
written only when every 5-minute interval of it is there. It writes its own table,

    warehouse/output/caiso_fuel_supply_history.csv      2018-06-01 to 2025-05-31

and leaves caiso_fuel_supply (2025-06-01 on, kept by the daily run, read by the carbon tables) exactly as it is, so
nothing a scheduled job or an open page reads changes. The energy mix reads the two together.

    python warehouse/connectors/caiso_fuel_supply_history.py              # the whole window
    python warehouse/connectors/caiso_fuel_supply_history.py --dry-run    # count only, no request
    python warehouse/connectors/caiso_fuel_supply_history.py --start 2019-10-01 --end 2020-08-31

WHY. EIA-930's file for California holds no hydro from October 2019 to August 2020, so the energy mix held none of
those hours (a main source blank is never taken as zero). CAISO's own supply by fuel has hydro throughout: for those
months the mix reads California's generation here (docs/methods/generation_mix_hourly.md, "California's hydro gap").

Ceiling: 800,000 rows (the approved pull). The window is 2,557 Pacific days, at most 312 rows a day (13 sources, 24
hours; 325 on the day the clocks go back): 797,784 rows if every day is complete. The run refuses a window that could
exceed the ceiling and writes nothing if the rows read exceed it. A day that falls short of an interval is logged and
skipped, never filled. License: public (CAISO's public system data; cite "California ISO, Today's Outlook").
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
import caiso_fuel_supply as cfs  # noqa: E402  (the address, the sources and their names)
import iso_prices as ip  # noqa: E402

NAME = "caiso_fuel_supply_history"
CONNECTOR = "caiso_fuel_supply_history"
SOURCE = "caiso:todays_outlook_fuelsource_history"
FIRST, LAST = dt.date(2018, 6, 1), dt.date(2025, 5, 31)
CEILING = 800_000


def day_rows(day, log):
    """One Pacific day of CAISO's file as hourly rows, or (None, why). caiso_fuel_supply.day_rows with one difference:
    CAISO wrote two columns in lower case until 2021 ("Natural gas", "Large hydro"), so a column is matched to its
    source whatever its case. Everything else, the completeness rule included, is that function's, line for line."""
    url = cfs.URL.format(day=day.strftime("%Y%m%d"))

    def call():
        r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0 (ERW research)"})
        if r.status_code != 200:
            raise RuntimeError(f"CAISO outlook HTTP {r.status_code} for {url}")
        return r
    r = ip.with_retries(f"CAISO outlook fuelsource {day}", call, log)
    got = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    d = pd.read_csv(io.StringIO(r.text))
    names = {c.lower(): c for c in cfs.SOURCES}
    d = d.rename(columns={c: names[str(c).strip().lower()] for c in d.columns if str(c).strip().lower() in names})
    if "Time" not in d.columns or not set(cfs.SOURCES) <= set(d.columns):
        raise RuntimeError(f"{url}: columns {list(d.columns)}")
    start = pd.Timestamp(day).tz_localize(cfs.TZ)
    end = pd.Timestamp(day + dt.timedelta(days=1)).tz_localize(cfs.TZ)
    expected = int((end - start) / pd.Timedelta(minutes=5))
    t = pd.to_datetime(d["Time"].astype(str).str.slice(0, 5), format="%H:%M", errors="coerce")
    ts = (pd.Timestamp(day) + (t - t.dt.normalize())).dt.tz_localize(cfs.TZ, ambiguous="infer")
    d = d.assign(ts=ts).dropna(subset=cfs.SOURCES + ["ts"])
    if len(d) != expected or d["ts"].duplicated().any():
        return None, f"{day}: {len(d)} of {expected} intervals"
    d["hour"] = d["ts"].dt.tz_convert("UTC").dt.floor("h")
    if (d.groupby("hour").size() != 12).any():
        return None, f"{day}: an hour without its twelve intervals"
    h = d.groupby("hour")[cfs.SOURCES].mean()
    long = h.reset_index().melt(id_vars=["hour"], value_vars=cfs.SOURCES, var_name="col", value_name="value")
    return pd.DataFrame({
        "entity": "caiso:ISO", "variable": long["col"].map(cfs.VAR), "ts_utc": long["hour"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value": long["value"].astype(float).round(4), "unit": "MW", "freq": "PT1H", "geo": "US-CA", "market": "",
        "node": "", "source": SOURCE, "source_url": url, "retrieved_at": got, "vintage": ""}), None


def window(start, end):
    first = max(FIRST, dt.date.fromisoformat(start)) if start else FIRST
    last = min(LAST, dt.date.fromisoformat(end)) if end else LAST
    return [first + dt.timedelta(days=k) for k in range((last - first).days + 1)]


def main(argv=None):
    ap = argparse.ArgumentParser(description="CAISO Today's Outlook supply by fuel source, hourly, June 2018 to May 2025")
    ap.add_argument("--start", help=f"first Pacific day (not before {FIRST})")
    ap.add_argument("--end", help=f"last Pacific day (not after {LAST})")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true", help="count the rows the window would hold; no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    days = window(args.start, args.end)
    most = len(days) * 24 * len(cfs.SOURCES) + 8 * len(cfs.SOURCES)      # eight days in the window have a 25th hour
    print(f"{len(days)} days, {days[0]} to {days[-1]}: at most {most:,} rows (ceiling {CEILING:,})")
    if most > CEILING:
        print(f"refused: the window could exceed the approved ceiling of {CEILING:,} rows", file=sys.stderr)
        return 1
    if args.dry_run:
        return 0
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
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
            raise RuntimeError(f"no complete day in {days[0]} to {days[-1]}: {short[:3]}")
        s = pd.concat(frames, ignore_index=True).sort_values(["variable", "ts_utc"])
        if len(s) > CEILING:
            raise RuntimeError(f"{len(s):,} rows exceed the approved ceiling of {CEILING:,}; nothing written")
        header = [
            "Energy Research Warehouse (ERW): CAISO supply by fuel source, hourly (Today's Outlook), June 2018 to May 2025 (session 133)",
            "Shape: series (docs/datastandard.md v0). freq PT1H; ts_utc is the hour's start. value: the mean of the hour's twelve 5-minute values, MW (also the hour's MWh). "
            "Variables are CAISO's columns: solar, wind, geothermal, biomass, biogas, small_hydro, coal, nuclear, natural_gas, large_hydro, batteries (positive discharging), imports, other, each _mw. "
            "The same reading as caiso_fuel_supply, which holds 2025-06-01 on.",
            f"Window: Pacific days {days[0]} to {days[-1]}; {len(frames)} complete days written; a day short of any 5-minute interval is not written"
            + (f" ({len(short)} skipped: {'; '.join(short[:8])}{' ...' if len(short) > 8 else ''})" if short else "") + ".",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/caiso_fuel_supply_history.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{run_id}/ (not in git)",
            f"Source: {SOURCE} California ISO, Today's Outlook, supply by fuel source history files ({cfs.URL.format(day='YYYYMMDD')})",
            f"  page: {cfs.PAGE}",
            f"Rows: {len(s):,} of the {CEILING:,} ceiling. Nothing is filled.",
            "License: public (CAISO public system data; cite \"California ISO, Today's Outlook\").",
        ]
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="California ISO (CAISO)", report="Today's Outlook: supply by fuel source (fuelsource.csv history), June 2018 to May 2025",
                                    report_url=cfs.PAGE, document_list=cfs.URL.format(day="YYYYMMDD"), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="supply", status="ok", detail=f"{len(frames)} days, {len(s):,} rows" + (f"; skipped {len(short)}" if short else "")))
        print(f"{NAME}: {len(frames)} days, {len(s):,} rows; skipped {len(short)}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last_line = tb.strip().splitlines()[-1]
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {last_line}", file=sys.stderr)
        results.append(dict(table=NAME, market="supply", status="failed", detail=last_line[:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 1 if any(r["status"] != "ok" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
