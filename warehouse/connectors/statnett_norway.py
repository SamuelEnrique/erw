#!/usr/bin/env python3
"""Norway's electricity production and consumption a day, from Statnett's operational data (driftsdata) (session 2300,
chain 105: a source of the session's own choosing).

Energy Research Warehouse (ERW) connector. One series table from one request to the REST address behind Statnett's
Production and Consumption chart (https://driftsdata.statnett.no/Web/ProductionConsumption?language=en):

    https://driftsdata.statnett.no/restapi/ProductionConsumption/GetData?From=2020-01-01

    statnett_norway_daily   entity statnett:norway; variable production or consumption; value in MWh as published;
               ts_utc the day (Norway's day, Europe/Oslo) at 00:00:00Z (Decision 11: a label); freq P1D; geo NO; the days
               ended before the retrieval (Norway's time) only

The answer is two arrays (Production, Consumption) with a start time (StartPointUTC, Norway's midnight of the first day),
an end time and a step of 24 hours. The arrays hold one slot more than Norway's days each autumn: the slot after the day
the clocks go back (the last Sunday of October) is empty in every year (2020 to 2025, session 2300), and the values go on
after it. So: a slot is a day, in order from the first day, except an empty slot right after an autumn clock-change
day, which is skipped; any other empty slot is a day not published (no row, named in the header: eight days of November
2025 when this was written). The slots must come out at Norway's day of the end time, or the run stops. The day in
progress (the last slot) is not written. Nothing is filled.

Statnett's page says data "may be missing in some places on this page, for example, data from wind power production that
came into operation after 2019": its production is about 1 percent under Statistics Norway's total generation (session
2300: 99.4 percent, the median of 81 months; consumption 99.2 percent of gross consumption, ssb_norway_electricity_monthly).

    python warehouse/connectors/statnett_norway.py [--offline] [--out-dir DIR]

Ceiling: one request, asked again unless --offline. driftsdata.statnett.no and www.statnett.no have no robots file (HTTP
404, session 2300). License: internal until the licenses' round reads Statnett's terms (none found on its data pages).
"""

import argparse
import datetime as dt
import json
import os
import sys
import traceback
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "statnett_norway"
SOURCE = "statnett:driftsdata_production_consumption"
HOST = "driftsdata.statnett.no"
PAGE = "https://driftsdata.statnett.no/Web/ProductionConsumption?language=en"
URL = "https://driftsdata.statnett.no/restapi/ProductionConsumption/GetData?From=2020-01-01"
TABLE = "statnett_norway_daily"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
OSLO = ZoneInfo("Europe/Oslo")
DAY_MS = 86400000


def autumn_change(year):
    d = dt.date(year, 10, 31)
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)  # the last Sunday of October


def oslo_day(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).astimezone(OSLO).date()


def place(d):
    """(day, production, consumption) for every slot that is a day, and the days not published."""
    if d.get("PeriodTickMs") != DAY_MS:
        raise RuntimeError(f"the step is {d.get('PeriodTickMs')} ms, not a day")
    prod, cons = d["Production"], d["Consumption"]
    if len(prod) != len(cons):
        raise RuntimeError(f"{len(prod)} production slots, {len(cons)} consumption slots")
    first, end = oslo_day(d["StartPointUTC"]), oslo_day(d["EndPointUTC"])
    out, missing, day = [], [], first
    for i, (p, c) in enumerate(zip(prod, cons)):
        if p is None and c is None and day - dt.timedelta(days=1) == autumn_change(day.year) and i > 0 and out and out[-1][0] == day - dt.timedelta(days=1):
            continue  # the empty slot after the clocks go back
        if p is None or c is None:
            missing.append(day)
        else:
            out.append((day, float(p), float(c)))
        day += dt.timedelta(days=1)
    if day - dt.timedelta(days=1) != end:
        raise RuntimeError(f"the slots end at {day - dt.timedelta(days=1)}, the answer's end time is {end}")
    return out, missing


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statnett: Norway's production and consumption a day")
    ap.add_argument("--offline", action="store_true", help="the saved answer only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        got = rec.get("retrieved_at") or ""
        today = pd.Timestamp(got).tz_convert(OSLO).date() if got else dt.datetime.now(OSLO).date()
        days, missing = place(json.loads(content))
        base = dict(source=SOURCE, source_url=URL, retrieved_at=got, vintage=ip.vintage_of(rec))
        rows = []
        for day, p, c in days:
            if day >= today:
                continue  # the day in progress
            for var, v in (("production", p), ("consumption", c)):
                rows.append(dict(base, entity="statnett:norway", variable=var, ts_utc=f"{day}T00:00:00Z", value=v, unit="MWh",
                                 freq="P1D", geo="NO", market="", node=""))
        s = pd.DataFrame(rows)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        gaps = ", ".join(str(m) for m in missing) or "none"
        head = [
            f"Energy Research Warehouse (ERW): Statnett, Production and Consumption, Norway a day, {s.ts_utc.min()[:10]} to "
            f"{s.ts_utc.max()[:10]} (session 2300)",
            "Shape: series (docs/datastandard.md v0). entity statnett:norway; variable production or consumption; unit MWh as "
            "published; freq P1D; ts_utc Norway's day (Europe/Oslo) at 00:00:00Z, a label; geo NO.",
            "Statnett's arrays hold one empty slot after each autumn clock-change day, skipped; the slots end at Norway's day of "
            f"the answer's end time (checked). Days Statnett leaves empty (no row): {gaps}. The day in progress is not written. "
            "Statnett says data may be missing, for example from wind power that came into operation after 2019: production is "
            "about 1 percent under Statistics Norway's total generation (session 2300). Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statnett_norway.py; the answer retrieved at {got}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Statnett SF, Data from the power system, Production and Consumption, {PAGE}",
            f"  access: {URL}",
            "License: internal until the licenses' round reads Statnett's terms. Source: Statnett.",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s):,} rows, {s.ts_utc.min()[:10]} to {s.ts_utc.max()[:10]}, {len(missing)} days not published")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statnett SF", report="Data from the power system, Production and Consumption",
                                    report_url=PAGE, document_list="https://www.statnett.no/en/for-stakeholders-in-the-power-industry/data-from-the-power-system/",
                                    license="internal", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
