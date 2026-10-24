#!/usr/bin/env python3
"""The Canada Energy Regulator's pipeline throughput and capacity data for the pipelines that cross the U.S. border:
each key point's throughput and capacity, a month for oil and a day for gas (session 2169, chain 094: the Canadian oil
and gas that reach the United States, beside the CER's trade summaries the warehouse holds).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/cer_pipeline_throughput.csv, from the
CER's "Pipeline Throughput and Capacity Data" (open.canada.ca's catalogue lists every file; the files are on
www.cer-rec.gc.ca/open/energy/throughput-capacity/), nine of its pipelines:

    oil (a month, by product):  Keystone, Enbridge Canadian Mainline, Southern Lights (an import line), Cochin (an
                                import line)
    gas (a day):                Foothills, Alliance, Westcoast, TransCanada Mainline, Maritimes & Northeast

    entity      cer_pipe:<pipeline>:<key point>, and for an oil line's throughput and contracted volumes
                cer_pipe:<pipeline>:<key point>:<product>:<trade type> (a key point can carry one product as export and
                as intracanada flow, as Enbridge's ex-Gretna does), and for a gas line cer_pipe:<pipeline>:<key point>:
                <direction of flow> (a key point can carry flow both ways, as Westcoast's Kingsvale does), each in snake
                case as the CER names them; node the pipeline, key point and product in the CER's words
    variable    throughput; for oil also committed_volume, uncommitted_volume, nameplate_capacity, available_capacity
                (a key point's capacity is one figure a month for all its products: written once, without a product);
                for gas capacity
    unit        m3/d (Decision 69: the CER's thousand cubic metres a day times 1,000)
    ts_utc      the CER's Date at 00:00:00Z (an oil month's first day, freq P1M; a gas day, freq P1D); geo CA
    x_*         the company, the direction of flow, the trade type (export, import, intracanada, domestic), the key
                point's latitude and longitude, the CER's reason for variance (oil)

The gas files' throughput in GJ/d is not taken (the volume is). Values as published; a blank has no row; nothing is
filled. Enbridge's Mainline file gives no committed or uncommitted volumes (the CER's shorter oil header), so its lines
have throughput and capacity only. A file whose header is not one of the CER's oil or gas headers, a value that is not a number, a key point whose capacity
differs between its products in one month, or a key given twice stops the run.

    python warehouse/connectors/cer_throughput.py [--offline] [--out-dir DIR]

Ceiling: nine requests (one a pipeline's file), each reused from warehouse/raw/cer_throughput/ with --offline.
www.cer-rec.gc.ca's robots file disallows only /fracfocus and /bin for every reader (session 2169). License: the Open
Government Licence - Canada (the catalogue's licence for this dataset, session 2169); the CER's own site terms are record
96. Attribution: "Contains information licensed under the Open Government Licence - Canada."
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "cer_pipeline_throughput"
CONNECTOR = "cer_throughput"
SOURCE = "cer:throughput_capacity"
PAGE = "https://open.canada.ca/data/en/dataset/dc343c43-a592-4a27-8ee7-c77df56afb34"
BASE = "https://www.cer-rec.gc.ca/open/energy/throughput-capacity/"
FILES = {"keystone": "oil", "enbridge-mainline": "oil", "southern-lights": "oil", "cochin": "oil",
         "foothills": "gas", "alliance": "gas", "westcoast": "gas", "tcpl-mainline": "gas", "mnp": "gas"}
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
OIL = ["Date", "Month", "Year", "Company", "Pipeline", "Key Point", "Latitude", "Longitude", "Direction Of Flow",
       "Trade Type", "Product", "Throughput (1000 m3/d)", "Committed Volumes (1000 m3/d)",
       "Uncommitted Volumes (1000 m3/d)", "Nameplate Capacity (1000 m3/d)", "Available Capacity (1000 m3/d)",
       "Reason For Variance"]
OIL_SHORT = [c for c in OIL if not c.startswith(("Committed", "Uncommitted"))]   # Enbridge Mainline gives no contracted volumes
GAS = ["Date", "Day", "Month", "Year", "Company", "Pipeline", "Key Point", "Latitude", "Longitude", "Direction Of Flow",
       "Trade Type", "Capacity (1000 m3/d)", "Throughput (1000 m3/d)", "Throughput (GJ/d)"]
OIL_PRODUCT_VARS = {"Throughput (1000 m3/d)": "throughput", "Committed Volumes (1000 m3/d)": "committed_volume",
                    "Uncommitted Volumes (1000 m3/d)": "uncommitted_volume"}
OIL_POINT_VARS = {"Nameplate Capacity (1000 m3/d)": "nameplate_capacity", "Available Capacity (1000 m3/d)": "available_capacity"}
GAS_VARS = {"Capacity (1000 m3/d)": "capacity", "Throughput (1000 m3/d)": "throughput"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_company", "x_direction", "x_trade_type", "x_latitude", "x_longitude", "x_reason"]


def text(v):
    return re.sub(r"\s+", " ", str(v or "")).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", text(s).lower()).strip("_")


def num(v, where):
    s = text(v)
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        raise RuntimeError(f"{where}: not a number: {s!r}")


def file_rows(content, kind, url, retrieved, vintage):
    t = pd.read_csv(io.StringIO(content.lstrip("﻿")), dtype=str, keep_default_na=False)
    want = [OIL, OIL_SHORT] if kind == "oil" else [GAS]
    if list(t.columns) not in want:
        raise RuntimeError(f"{url}: the header is not the CER's {kind} header: {list(t.columns)}")
    freq = "P1M" if kind == "oil" else "P1D"
    out, caps = [], {}
    for r in t.to_dict("records"):
        day = text(r["Date"])
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            raise RuntimeError(f"{url}: a date not YYYY-MM-DD: {day!r}")
        point = f"cer_pipe:{slug(r['Pipeline'])}:{slug(r['Key Point'])}"
        base = {"ts_utc": f"{day}T00:00:00Z", "unit": "m3/d", "freq": freq, "geo": "CA", "market": "", "source": SOURCE,
                "source_url": url, "retrieved_at": retrieved, "vintage": vintage, "x_company": text(r["Company"]),
                "x_direction": text(r["Direction Of Flow"]), "x_trade_type": text(r["Trade Type"]),
                "x_latitude": text(r["Latitude"]), "x_longitude": text(r["Longitude"]),
                "x_reason": text(r.get("Reason For Variance", ""))}
        where = f"{url} {day} {text(r['Key Point'])}"
        if kind == "oil":
            entity = f"{point}:{slug(r['Product'])}:{slug(r['Trade Type'])}"
            node = f"{text(r['Pipeline'])}, {text(r['Key Point'])}, {text(r['Product'])}"
            for col, var in OIL_PRODUCT_VARS.items():
                if col not in r:
                    continue
                v = num(r[col], where)
                if v is not None:
                    out.append({"entity": entity, "variable": var, "value": round(v * 1000, 3), "node": node, **base})
            for col, var in OIL_POINT_VARS.items():
                v = num(r[col], where)
                if v is None:
                    continue
                key = (point, var, day)
                if key in caps:
                    if caps[key] != v:
                        raise RuntimeError(f"{where}: {var} differs between products: {caps[key]} and {v}")
                    continue
                caps[key] = v
                out.append({"entity": point, "variable": var, "value": round(v * 1000, 3),
                            "node": f"{text(r['Pipeline'])}, {text(r['Key Point'])}", **base})
        else:
            for col, var in GAS_VARS.items():
                v = num(r[col], where)
                if v is not None:
                    out.append({"entity": f"{point}:{slug(r['Direction Of Flow'])}", "variable": var, "value": round(v * 1000, 3),
                                "node": f"{text(r['Pipeline'])}, {text(r['Key Point'])}", **base})
    return out


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    twice = t[t.duplicated(["entity", "variable", "ts_utc"], keep=False)]
    if len(twice):
        raise RuntimeError(f"a key given twice: {twice.entity.iloc[0]} {twice.variable.iloc[0]} {twice.ts_utc.iloc[0]}")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="CER pipeline throughput and capacity, the lines that cross the U.S. border")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
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
        if not args.offline and (ip.paused("cer") or ip.paused_host("www.cer-rec.gc.ca")):
            raise RuntimeError("the CER is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, got = [], []
        for name, kind in FILES.items():
            url = f"{BASE}{name}-throughput-and-capacity.csv"
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
            rows += file_rows(content.decode("utf-8", errors="replace"), kind, url, rec.get("retrieved_at") or "", ip.vintage_of(rec))
            got.append((name, rec.get("retrieved_at") or ""))
        t = finish(rows)
        pipes = t.entity.str.split(":").str[1]
        by = t.assign(p=pipes).groupby("p").agg(rows=("value", "size"), start=("ts_utc", "min"), end=("ts_utc", "max"))
        header = [
            "Energy Research Warehouse (ERW): Canada Energy Regulator (CER), Pipeline Throughput and Capacity Data, the nine pipelines that cross the U.S. border (session 2169)",
            "Shape: series (docs/datastandard.md v0). entity cer_pipe:<pipeline>:<key point>[:<product>:<trade type> for an oil line's volumes, :<direction> for a gas line]; variable throughput, committed_volume, uncommitted_volume, nameplate_capacity, "
            "available_capacity (oil) or capacity (gas); unit m3/d (Decision 69: the CER's thousand cubic metres a day times 1,000); ts_utc the CER's date (an oil month's first day, P1M; a gas day, P1D); geo CA.",
            f"{len(t)} rows: " + "; ".join(f"{p} {r.rows} rows, {r.start[:10]} to {r.end[:10]}" for p, r in by.iterrows())
            + ". A key point's oil capacity is written once a month, not for each product. The gas files' GJ/d are not taken. A blank has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/cer_throughput.py; the files retrieved " + "; ".join(f"{n} {r}" for n, r in got),
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Canada Energy Regulator, Pipeline Throughput and Capacity Data (open.canada.ca), {PAGE}",
            f"  access: {BASE}<pipeline>-throughput-and-capacity.csv",
            "License: public. Contains information licensed under the Open Government Licence - Canada (https://open.canada.ca/en/open-government-licence-canada).",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Canada Energy Regulator (CER), Open Government Licence - Canada",
                                    report="Pipeline Throughput and Capacity Data (nine cross-border pipelines)",
                                    report_url=PAGE, document_list=BASE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {pipes.nunique()} pipelines")
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
