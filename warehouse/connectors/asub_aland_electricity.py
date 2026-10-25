#!/usr/bin/env python3
"""Aland's electricity supply a year by origin, 1994 to 2025: imports from Sweden and Finland and the islands' own oil, wind,
bioenergy and solar production, as Statistics and Research Aland (ASUB) publishes them in table MI009 ("Anskaffning och
produktion av el") of its PxWeb database (session 2651, chain 132, the session's second own choice; the ERW held Aland in no
table: Statistics Finland's national figures include it).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/asub_aland_electricity_annual.csv, from ASUB's
PxWeb API (no key), one JSON-stat 2.0 query by POST, the GWh figures of every origin and every year selected:

    https://pxweb.asub.ax/PXWeb/api/v1/sv/Statistik/MI/MI009.px

    entity      asub:ax:<origin>: import_sweden, import_finland (variable imports), oil, wind, bioenergy, solar (generation) and
                total (supply)
    unit        MWh (the table's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo AX
    node        the origin as ASUB names it (Swedish)

A cell without a number has no row; nothing is filled. A table without its year, statistic and origin dimensions, an origin not
in the map, a year not of four digits, a value array not the size of the dimensions, a key given twice, or a year whose six
origins miss its total by more than 0.5 GWh stops the run. ASUB's note: the figures show only how electricity is physically
produced on Aland, not its trade (all of it is traded on Nord Pool); solar is estimated from the panels' installed capacity.

    python warehouse/connectors/asub_aland_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/asub_ax/ (query_MI009.json, the answer with its time of retrieval) and read
from there with --offline. pxweb.asub.ax has no robots file (HTTP 404, session 2651); www.asub.ax's robots file closes only the
site's system paths. License: CC BY 4.0, ASUB's terms of use (www.asub.ax/sv/om-asub/om-asubax/anvandarvillkor: texts, tables
and diagrams, with ASUB named as the source; third parties' material excepted): public.
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
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "asub_aland_electricity_annual"
CONNECTOR = "asub_ax"
SOURCE = "asub_ax:MI009"
HOST = "pxweb.asub.ax"
URL = "https://pxweb.asub.ax/PXWeb/api/v1/sv/Statistik/MI/MI009.px"
TERMS = "https://www.asub.ax/sv/om-asub/om-asubax/anvandarvillkor"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEAR = "år"
ORIGINS = {"Import Sverige": ("import_sweden", "imports"), "Import Finland": ("import_finland", "imports"), "Olja": ("oil", "generation"),
           "Vindkraft": ("wind", "generation"), "Bioenergi": ("bioenergy", "generation"), "Solkraft": ("solar", "generation"),
           "Totalt": ("total", "supply")}
X_COLS = []


def codes(cat):
    idx = cat["index"]
    return sorted(idx, key=idx.get) if isinstance(idx, dict) else list(idx)


def parse(js, base):
    dims = js.get("id") or []
    if sorted(dims) != sorted([YEAR, "statistik", "ursprung"]):
        raise RuntimeError(f"the dimensions are {dims}")
    n = 1
    for s in js["size"]:
        n *= s
    if len(js["value"]) != n:
        raise RuntimeError(f"{len(js['value'])} values for dimensions of size {js['size']}")
    stat = js["dimension"]["statistik"]["category"]["label"]
    if list(stat.values()) != ["GWh (gigawattimmar)"]:
        raise RuntimeError(f"the statistic is not GWh alone: {stat}")
    olabel = js["dimension"]["ursprung"]["category"]["label"]
    unknown = sorted(set(olabel.values()) - set(ORIGINS))
    if unknown:
        raise RuntimeError(f"an origin not in the map: {unknown}")
    ylabel = js["dimension"][YEAR]["category"]["label"]
    rows, gwh = [], {}
    for k, combo in enumerate(itertools.product(*[codes(js["dimension"][d]["category"]) for d in dims])):
        cell = dict(zip(dims, combo))
        v = js["value"][k]
        if v is None:
            continue
        y = ylabel.get(cell[YEAR], cell[YEAR])
        if not re.fullmatch(r"\d{4}", str(y)):
            raise RuntimeError(f"a year not of four digits: {y!r}")
        label = olabel[cell["ursprung"]]
        item, variable = ORIGINS[label]
        gwh[(int(y), item)] = float(v)
        rows.append(dict(entity=f"asub:ax:{item}", variable=variable, ts_utc=f"{y}-01-01T00:00:00Z", value=round(float(v) * 1000, 3),
                         unit="MWh", freq="P1Y", geo="AX", market="", node=label, **base))
    for y in sorted({y for y, _ in gwh}):
        if (y, "total") not in gwh:
            continue
        s = sum(gwh.get((y, it), 0.0) for it, _ in ORIGINS.values() if it != "total")
        if abs(s - gwh[(y, "total")]) > 0.5:
            raise RuntimeError(f"{y}: the origins make {s:.2f} GWh, the total {gwh[(y, 'total')]}")
    return rows


def get(offline, log):
    path = os.path.join(ip.RAW_DIR, CONNECTOR, "query_MI009.json")
    if offline:
        if not os.path.exists(path):
            raise RuntimeError(f"offline: no saved query at {path}")
        saved = json.load(open(path, encoding="utf-8"))
        log(f"  saved answer reused: {path} (retrieved {saved['retrieved_at']})")
        return saved["answer"], saved["retrieved_at"]
    body = {"query": [{"code": YEAR, "selection": {"filter": "all", "values": ["*"]}},
                      {"code": "statistik", "selection": {"filter": "item", "values": ["GWh"]}},
                      {"code": "ursprung", "selection": {"filter": "all", "values": ["*"]}}],
            "response": {"format": "json-stat2"}}
    r = requests.post(URL, json=body, headers=UA, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} for MI009")
    at = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    js = json.loads(r.content.decode("utf-8-sig"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump({"retrieved_at": at, "url": URL, "query": body, "answer": js}, open(path, "w", encoding="utf-8"))
    log(f"  POST {URL}: {len(r.content)} bytes, saved as {path}")
    return js, at


def main(argv=None):
    ap = argparse.ArgumentParser(description="ASUB: Aland's electricity supply by origin a year")
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
    results = []
    try:
        js, at = get(args.offline, log)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=at, vintage="")   # the answer's "updated" is the table's creation (2008), not its last update
        t = pd.DataFrame(parse(js, base))
        if t.empty:
            raise RuntimeError("no value in the answer")
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        tot = t[t.entity == "asub:ax:total"].set_index("ts_utc").value
        head = [
            "Energy Research Warehouse (ERW): Statistics and Research Aland (ASUB), table MI009: Aland's electricity supply by origin "
            f"(imports from Sweden and Finland; oil, wind, bioenergy and solar production), {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} "
            "(session 2651)",
            "Shape: series (docs/datastandard.md v0). entity asub:ax:<origin>; variable imports, generation or supply (the total); unit "
            "MWh (the table's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo AX; node the origin as ASUB names it.",
            f"{len(t)} rows; the supply GWh: " + ", ".join(f"{k[:4]} {v / 1e3:.1f}" for k, v in tot.items() if k[:4] in ("1994", "2005", "2015", "2025"))
            + ". Each year's origins checked against its total; physical production, not trade (ASUB's note); nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/asub_aland_electricity.py; the answer retrieved {at}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/query_MI009.json (not in git)",
            f"Source: {SOURCE} Statistics and Research Aland (ASUB), Anskaffning och produktion av el",
            f"  access: {URL} (one JSON-stat query by POST)",
            f"License: CC BY 4.0 (ASUB's terms of use, {TERMS}); credit: Statistics and Research Aland (ASUB).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics and Research Aland (ASUB)",
                                    report="Table MI009: Anskaffning och produktion av el (electricity supply and production by origin)",
                                    report_url=URL, document_list="https://pxweb.asub.ax/PXWeb/api/v1/sv/Statistik/MI", license="public",
                                    tables=[NAME])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
