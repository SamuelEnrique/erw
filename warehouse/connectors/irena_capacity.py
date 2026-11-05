#!/usr/bin/env python3
"""The International Renewable Energy Agency's installed electricity capacity by country and technology, a year, from
IRENASTAT (session 2085, chain 068: the world's fleets, renewable and not, beside the U.S. tables).

Energy Research Warehouse (ERW) connector. One series table from IRENASTAT's PxWeb service (pxweb.irena.org, whose robots
address answers 404; www.irena.org itself answers the ERW's reader with an Azure WAF challenge and is not asked):

    https://pxweb.irena.org/api/v1/en/IRENASTAT/Power Capacity and Generation/Country_ELECSTAT_2026_H2_PX.px
        "Electricity statistics by Country/area, Technology, Data Type, Grid connection and Year": a POST of a JSON query
        (Data Type 1, Electrical Installed Capacity (MW); Grid connection 0, All; every country and technology; the
        years asked), answered in PxWeb's JSON

    irena_capacity_annual   entity irena:<the table's country code, ISO 3166 alpha-3 as IRENA writes it>; variable
                            capacity_<technology> (the technology's name as IRENA writes it, lower case with
                            underscores; IRENA's totals, Total Renewable and Total Non-Renewable, are its own); unit MW;
                            ts_utc the year's first day (IRENA's capacity is at the year's end); freq P1Y; geo empty
                            (ISO alpha-3 is not the standard's geo); node the country's name; x_technology_code

A cell IRENA leaves empty (".." or "-") has no row; a 0 IRENA gives is kept. A query whose variables are not the five
above, a country or technology code not in the table's metadata, or a value neither a number nor empty stops the run.
Nothing is filled.

    python warehouse/connectors/irena_capacity.py [--offline] [--out-dir DIR] [--years 2015-2025]

Ceiling: two requests (the table's metadata and the query), saved in warehouse/raw/irena_capacity/ and reused offline.
License: not settled (IRENA's terms of use are on www.irena.org, which refused the reader; the licenses round reads them).
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "irena_capacity"
SOURCE = "irena:irenastat_elecstat"
TABLE_URL = "https://pxweb.irena.org/api/v1/en/IRENASTAT/Power%20Capacity%20and%20Generation/Country_ELECSTAT_2026_H2_PX.px"
TABLE = "irena_capacity_annual"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
VARS = ["Country/area", "Technology", "Data Type", "Grid connection", "Year"]
YEARS = (2015, 2025)
X_COLS = ["x_technology_code"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def query(meta, y0, y1):
    """The JSON query of the capacity cells, every country and technology, Grid connection All, the years asked."""
    codes = [v["code"] for v in meta["variables"]]
    if codes != VARS:
        raise RuntimeError(f"the table's variables are {codes}, not {VARS}")
    var = {v["code"]: v for v in meta["variables"]}
    dtype = [c for c, t in zip(var["Data Type"]["values"], var["Data Type"]["valueTexts"]) if t == "Electrical Installed Capacity (MW)"]
    grid = [c for c, t in zip(var["Grid connection"]["values"], var["Grid connection"]["valueTexts"]) if t == "All"]
    years = [c for c, t in zip(var["Year"]["values"], var["Year"]["valueTexts"]) if t.isdigit() and y0 <= int(t) <= y1]
    if len(dtype) != 1 or len(grid) != 1 or len(years) != y1 - y0 + 1:
        raise RuntimeError(f"the metadata has no capacity type, no All, or not every year asked: {dtype}, {grid}, {len(years)}")
    sel = [("Country/area", var["Country/area"]["values"]), ("Technology", var["Technology"]["values"]), ("Data Type", dtype),
           ("Grid connection", grid), ("Year", years)]
    return {"query": [{"code": c, "selection": {"filter": "item", "values": v}} for c, v in sel], "response": {"format": "json"}}


def parse(answer, meta, base):
    var = {v["code"]: dict(zip(v["values"], v["valueTexts"])) for v in meta["variables"]}
    cols = [c["code"] for c in answer["columns"]]
    if cols[:5] != VARS:
        raise RuntimeError(f"the answer's columns are {cols}")
    rows, empty = [], 0
    for d in answer["data"]:
        country, tech, _, _, year = d["key"]
        if country not in var["Country/area"] or tech not in var["Technology"]:
            raise RuntimeError(f"a code not in the metadata: {country}, {tech}")
        v = str(d["values"][0]).strip()
        if v in ("", "..", "-", "."):
            empty += 1
            continue
        if not re.fullmatch(r"-?\d+(\.\d+)?", v):
            raise RuntimeError(f"a value neither a number nor empty: {v!r}")
        rows.append(dict(entity=f"irena:{country}", variable=f"capacity_{slug(var['Technology'][tech])}",
                         ts_utc=f"{var['Year'][year]}-01-01T00:00:00Z", value=float(v), unit="MW", freq="P1Y", geo="", market="",
                         node=var["Country/area"][country], **base, x_technology_code=tech))
    return pd.DataFrame(rows), empty


def saved_path(name):
    return os.path.join(ip.RAW_DIR, CONNECTOR, name)


def load_saved(name, log):
    """Offline: the metadata and the answer from the file a run saved them in (they share one address, so the raw store's
    lookup by address cannot tell them apart)."""
    path = saved_path(name)
    if not os.path.exists(path):
        raise RuntimeError(f"offline: no saved query at {path}")
    saved = json.load(open(path, encoding="utf-8"))
    log(f"  saved metadata and answer reused: {path} (retrieved {saved['retrieved_at']})")
    return saved["meta"], json.dumps(saved["answer"]).encode("utf-8"), {"retrieved_at": saved["retrieved_at"], "last_modified": ""}


def post(url, body, meta, log, name):
    """The query's answer by POST (captured by the raw store), saved with the metadata under its own name."""
    r = requests.post(url, json=body, headers=UA, timeout=180)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} for the query")
    rec = {"retrieved_at": ip.utc_iso(pd.Timestamp.now(tz="UTC")), "last_modified": r.headers.get("Last-Modified") or ""}
    path = saved_path(name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump({"retrieved_at": rec["retrieved_at"], "query": body, "meta": meta, "answer": r.json()}, open(path, "w", encoding="utf-8"))
    log(f"  POST {url}: {len(r.content)} bytes, saved with the metadata as {path}")
    return r.content, rec


def main(argv=None):
    ap = argparse.ArgumentParser(description="IRENA's installed electricity capacity by country and technology, a year")
    ap.add_argument("--offline", action="store_true", help="the saved answers only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--years", default=f"{YEARS[0]}-{YEARS[1]}")
    args = ap.parse_args(argv)
    y0, y1 = (int(x) for x in args.years.split("-"))
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
        name = f"capacity_query_{y0}_{y1}.json"
        if args.offline:
            meta, content, rec = load_saved(name, log)
            query(meta, y0, y1)  # the saved metadata still holds the variables and years asked
        else:
            mcontent, _ = ip.fetch_raw(CONNECTOR, TABLE_URL, log, fresh=True, headers=UA, timeout=60, pause=1)
            meta = json.loads(mcontent.decode("utf-8"))
            content, rec = post(TABLE_URL, query(meta, y0, y1), meta, log, name)
        base = dict(source=SOURCE, source_url=TABLE_URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        s, empty = parse(json.loads(content.decode("utf-8")), meta, base)
        if s.empty:
            raise RuntimeError("no value in the answer")
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a country, technology and year given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): International Renewable Energy Agency (IRENA), IRENASTAT, Electricity statistics by Country/area, "
            f"Technology, Data Type, Grid connection and Year (2026 H2): installed electricity capacity, {y0} to {y1} (session 2085)",
            "Shape: series (docs/datastandard.md v0). entity irena:<country code as IRENA writes it, ISO alpha-3>; variable capacity_<technology, as "
            "IRENA names it> (its totals, total_renewable and total_non_renewable, are IRENA's own); unit MW; ts_utc the year's first day (the "
            "capacity at the year's end); freq P1Y; geo empty; node the country's name; x_technology_code IRENA's code. Grid connection: All.",
            f"{len(s)} rows, {s.entity.nunique()} countries, {s.variable.nunique()} technologies; {empty} cells IRENA leaves empty have no row. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/irena_capacity.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} International Renewable Energy Agency, IRENASTAT (PxWeb), {TABLE_URL}",
            "  access: the table's metadata (GET) and one JSON query (POST) to the same address",
            "License: not settled (IRENA's terms of use are on www.irena.org, which answered the ERW's reader with a challenge).",
        ]
        ip.write_snapshot(s, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{TABLE}: {len(s)} rows, {s.entity.nunique()} countries, {s.variable.nunique()} technologies; {empty} empty")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="International Renewable Energy Agency (IRENA)",
                                    report="IRENASTAT: Electricity statistics by Country/area, Technology, Data Type, Grid connection and Year",
                                    report_url=TABLE_URL, document_list="https://pxweb.irena.org/api/v1/en/IRENASTAT", license="internal",
                                    tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
