#!/usr/bin/env python3
"""Spain's electricity balance a month: generation by technology, storage, cross-border exchanges and demand at busbars,
from Red Electrica's REData API (session 2239, chain 101: Spain's generation by technology).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ree_spain_balance_monthly.csv, from the
REData widget "balance/balance-electrico" (no key), one request a year (the API answers HTTP 400 for a range longer
than a year, session 2239):

    https://apidatos.ree.es/en/datos/balance/balance-electrico?start_date=<year>-01-01T00:00&end_date=<year>-12-31T23:59&time_trunc=month

The answer is JSON: groups (Renewable, Non-renewable, Almacenamiento, Demand), each with its series of monthly values;
REE's own title: "Electrical energy balance: Allocation of production units according to primary fuel." Every series
is taken, its name in snake case (hydro, wind, solar_photovoltaic, ..., nuclear, combined_cycle, coal, ..., pumping_
consumption, battery_charging, storage_balance, cross_border_exchange_balance, demand_at_busbars), REE's subtotals
(renewable_generation, non_renewable_generation, storage_balance) among them, so a sum over technologies leaves those
out. Consumption by pumping and batteries and a net export are negative, as REE gives them.

    entity      ree:ES (REE's default geography, the national system); node Spain; geo ES
    unit        MWh (the API states no unit; a year's demand at busbars agrees with Ember's Spanish demand, session
                2239's cross-check); ts_utc the month's first day at 00:00:00Z (Decision 11); freq P1M
    x_*         REE's group and its series id

A month not yet ended when the year's answer was fetched is left out and counted (October 2026 in session 2239's
files). A value REE does not give has no row; nothing is filled. An answer that is not the balance, a series without
values, a value that is not a number or a month given twice stops the run.

    python warehouse/connectors/ree_balance.py [--first 2020] [--last 2026] [--offline] [--out-dir DIR]

Ceiling: one request a year, reused from warehouse/raw/ree_balance/ with --offline. apidatos.ree.es has no robots file
(HTTP 404) and www.ree.es's disallows only search, feeds and press events (session 2239). License: REE's legal notice
allows users to "publish them on their website or create company or academic content, as long as it is for information
only, and not for commercial purposes", naming REE as the source, not altering the data's meaning and giving the date
of their latest update (REE's "last-update", kept in the header).
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ree_spain_balance_monthly"
CONNECTOR = "ree_balance"
SOURCE = "ree:redata_balance_electrico"
PAGE = "https://www.ree.es/en/datos/balance"
API = "https://apidatos.ree.es/en/datos/balance/balance-electrico?start_date={y}-01-01T00:00&end_date={y}-12-31T23:59&time_trunc=month"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_group", "x_series_id"]


def snake(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def month_ended(month_start, retrieved):
    """Whether the month starting at month_start (YYYY-MM) had ended, in Spain's time, when the answer was fetched."""
    y, m = int(month_start[:4]), int(month_start[5:7])
    end = pd.Timestamp(year=y + (m == 12), month=m % 12 + 1, day=1, tz="Europe/Madrid")
    return pd.Timestamp(retrieved) >= end


def file_rows(body, url, retrieved, vintage, counts):
    d = json.loads(body)
    if "errors" in d or (d.get("data") or {}).get("attributes", {}).get("title") != "Electrical energy balance":
        raise RuntimeError(f"{url}: the answer is not REE's electrical energy balance: {str(d)[:200]}")
    updated = d["data"]["attributes"].get("last-update", "")
    out = []
    for g in d.get("included", []):
        for x in g["attributes"].get("content", []):
            vals = x["attributes"].get("values")
            if not vals:
                raise RuntimeError(f"{url}: series {x.get('type')!r} without values")
            for v in vals:
                month = str(v["datetime"])[:7]
                if not re.fullmatch(r"\d{4}-\d{2}", month):
                    raise RuntimeError(f"{url}: a month not in REE's form: {v['datetime']!r}")
                if not isinstance(v.get("value"), (int, float)):
                    raise RuntimeError(f"{url}: {x['type']} {month}: not a number: {v.get('value')!r}")
                if not month_ended(month, retrieved):
                    counts["open_month"] += 1
                    continue
                out.append({"entity": "ree:ES", "variable": snake(x["type"]), "ts_utc": f"{month}-01T00:00:00Z",
                            "value": float(v["value"]), "unit": "MWh", "freq": "P1M", "geo": "ES", "market": "",
                            "node": "Spain", "source": SOURCE, "source_url": url, "retrieved_at": retrieved,
                            "vintage": vintage, "x_group": g["type"], "x_series_id": str(x["id"])})
    return out, updated


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a month given twice: {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="REE REData: Spain's electricity balance a month")
    ap.add_argument("--first", type=int, default=2020)
    ap.add_argument("--last", type=int, default=2026)
    ap.add_argument("--offline", action="store_true", help="the saved answers only, no request")
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
        if not args.offline and (ip.paused("ree") or ip.paused_host("apidatos.ree.es")):
            raise RuntimeError("REE is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, got, updated = [], [], set()
        counts = {"open_month": 0}
        for y in range(args.first, args.last + 1):
            url = API.format(y=y)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
            r, u = file_rows(content.decode("utf-8"), url, rec.get("retrieved_at") or "", ip.vintage_of(rec), counts)
            rows += r
            updated.add(u)
            got.append((y, rec.get("retrieved_at") or ""))
        t = finish(rows)
        header = [
            f"Energy Research Warehouse (ERW): Red Electrica (REE), REData, Spain's electrical energy balance a month: generation by technology, storage, exchanges and demand at busbars, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2239)",
            "Shape: series (docs/datastandard.md v0). entity ree:ES; variable REE's series in snake case, its subtotals (renewable_generation, non_renewable_generation, storage_balance) among them; "
            "unit MWh; ts_utc the month's first day; freq P1M; geo ES. Pumping and battery consumption and a net export are negative, as REE gives them.",
            f"{len(t)} rows, {t.variable.nunique()} series. {counts['open_month']} values of a month not yet ended when fetched are left out. A value REE does not give has no row; nothing is filled. "
            "The API states no unit: MWh, as a year's demand at busbars agrees with Ember's demand.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ree_balance.py; the answers retrieved " + "; ".join(f"{y} {r}" for y, r in got)
            + "; REE's last update " + ", ".join(sorted(u for u in updated if u)),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Red Electrica (REE), REData API, balance-electrico, {PAGE}",
            f"  access: {API.format(y='<year>')}",
            "License: public. REE's legal notice: users may publish the content on their website or in company or academic work, for information only and not for commercial purposes, "
            "naming REE as the source, not altering the meaning of the data, and giving the date of their latest update. Cite: Red Electrica, REData.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Red Electrica (REE)",
                                    report="REData API, electrical energy balance (balance-electrico), a month",
                                    report_url=PAGE, document_list=API.format(y="<year>"), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows; {counts['open_month']} values of an open month left out")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
