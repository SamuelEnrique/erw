#!/usr/bin/env python3
"""Ireland's gross and net electricity output a month from January 1975, as the Central Statistics Office publishes it
in PxStat (table MSM01, "Electricity Output") (session 2320, chain 106: a third source of the session's own choosing,
Ireland beside the European tables; EirGrid's own data need written permission, chain 099, and Slovenia's statistics
portal was unavailable when asked).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/cso_ireland_electricity_monthly.csv, from
PxStat's RESTful API (no key), one GET of the whole table as JSON-stat 2.0:

    https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/MSM01/JSON-stat/2.0/en

    entity      cso:ie
    variable    gross_electricity_output (CSO's MSM01C1, to December 2008: CSO discontinued it from January 2009) or
                net_electricity_output (MSM01C2); node the statistic as CSO names it; x_code its code
    unit        MWh (the table's GWh times 1,000); ts_utc the month's first day; freq P1M; geo IE

CSO's note: gross output "represents the amount of electricity that passes through the National Grid (excluding
imports). It also includes electricity that is manufactured and consumed by manufacturers of electricity"; net output
does not include the latter. A cell CSO leaves empty has no row; nothing is filled. An answer without the three
dimensions, a statistic whose unit is not "Gigawatt Hours", a month not of the form YYYYMM, a value array not the size of
the dimensions, or a statistic and month given twice stops the run.

    python warehouse/connectors/cso_ireland_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/cso_electricity/ and fetched again unless --offline. ws.cso.ie and
www.cso.ie have no robots file (HTTP 404, session 2320). License: CC BY 4.0, CSO's Copyright and Re-use Policy
("Statistical information on this website is accessible free of charge and licensed under Creative Commons Attribution
(CC BY 4.0)"); source: Central Statistics Office, Ireland.
"""

import argparse
import datetime as dt
import itertools
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "cso_ireland_electricity_monthly"
CONNECTOR = "cso_electricity"
SOURCE = "cso:MSM01"
HOST = "ws.cso.ie"
URL = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/MSM01/JSON-stat/2.0/en"
PAGE = "https://data.cso.ie/table/MSM01"
TERMS = "https://www.cso.ie/en/aboutus/whoweare/copyrightpolicy/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
STAT, TIME, STATE = "STATISTIC", "TLIST(M1)", "C02196V02652"
X_COLS = ["x_code"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def parse(content, base):
    js = json.loads(content.decode("utf-8-sig") if isinstance(content, bytes) else content)
    dims = js.get("id")
    if sorted(dims or []) != sorted([STAT, TIME, STATE]):
        raise RuntimeError(f"the answer's dimensions are not the three expected: {dims}")
    cats = []
    for d in dims:
        c = js["dimension"][d]["category"]
        idx = c["index"]
        codes = sorted(idx, key=idx.get) if isinstance(idx, dict) else list(idx)
        cats.append((d, codes, c))
    n = 1
    for s in js["size"]:
        n *= s
    if len(js["value"]) != n:
        raise RuntimeError(f"{len(js['value'])} values for dimensions of size {js['size']}")
    stat = next(c[2] for c in cats if c[0] == STAT)
    for code in stat["index"]:
        unit = (stat.get("unit") or {}).get(code, {}).get("label")
        if unit != "Gigawatt Hours":
            raise RuntimeError(f"{code} in {unit!r}, not Gigawatt Hours")
    rows = []
    for k, combo in enumerate(itertools.product(*[c[1] for c in cats])):
        v = js["value"][k]
        if v is None:
            continue
        cell = dict(zip(dims, combo))
        m = re.fullmatch(r"(\d{4})(\d\d)", cell[TIME])
        if not m:
            raise RuntimeError(f"a month not of the form YYYYMM: {cell[TIME]!r}")
        code = cell[STAT]
        label = stat["label"][code].strip()
        rows.append(dict(entity="cso:ie", variable=slug(label), ts_utc=f"{m.group(1)}-{m.group(2)}-01T00:00:00Z", value=round(float(v) * 1000, 3),
                         unit="MWh", freq="P1M", geo="IE", market="", node=label, **base, x_code=code))
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no value in the answer")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a statistic and month given twice")
    return t, js.get("updated", "") or ""


def main(argv=None):
    ap = argparse.ArgumentParser(description="CSO table MSM01: Ireland's gross and net electricity output, a month")
    ap.add_argument("--offline", action="store_true", help="the saved answer only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host(HOST):
        print(f"{NAME}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=60, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage="")
        t, updated = parse(content, base)
        t["vintage"] = updated.replace(".000Z", "Z")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        g = t[t.variable == "net_electricity_output"].assign(y=lambda q: q.ts_utc.str[:4]).groupby("y").value.agg(["sum", "size"])
        g = g[g["size"] == 12]["sum"] / 1e6
        head = [
            "Energy Research Warehouse (ERW): Central Statistics Office, Ireland, PxStat table MSM01, Electricity Output, a month, "
            f"{t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2320)",
            "Shape: series (docs/datastandard.md v0). entity cso:ie; variable gross_electricity_output (to 2008-12, discontinued by CSO) or "
            "net_electricity_output; unit MWh (the table's GWh times 1,000); ts_utc the month's first day; freq P1M; geo IE; node the statistic as "
            "CSO names it; x_code its code.",
            f"{len(t)} rows; net output TWh a full year: " + ", ".join(f"{k} {v:.2f}" for k, v in g.items() if k >= "2015")
            + ". A cell left empty has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/cso_ireland_electricity.py; the answer retrieved {base['retrieved_at']}; updated {updated}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Central Statistics Office, Ireland, PxStat, table MSM01, {PAGE}",
            f"  access: {URL}",
            f"License: public (CC BY 4.0, {TERMS}). Source: Central Statistics Office, Ireland.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} variables, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Central Statistics Office, Ireland (CSO)", report="PxStat table MSM01: Electricity Output (monthly)",
                                    report_url=PAGE, document_list=URL, license="public", tables=[NAME])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
