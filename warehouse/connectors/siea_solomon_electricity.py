#!/usr/bin/env python3
"""The Solomon Islands' public electricity production by station a year, 2017 to 2025, as the Solomon Islands Electricity
Authority (trading as Solomon Power) gives it in the table "Energy Produced" of its Annual Report 2025 (session 2602, chain
129; the ERW held the Solomon Islands only in EIA's international table).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/siea_solomon_electricity_annual.csv, from one
PDF (no key):

    https://solomonpower.com.sb/wp-content/uploads/2026/09/2025-Annual-Report.pdf

    entity      siea:sb:<station>: lungga, honiara, outstations, henderson_solar, ranadi_solar, total
    variable    production
    unit        MWh (the report's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo SB
    node        the report's label

The table's page is found by its title line ("Energy produced in 2025 compared with ...") and its header ("Station 2017 ...
2025"). Lungga, Honiara, the outstations and the total each hold one figure a year on their line. Henderson's label stands
alone, its figures on the next line ("Solar (1 MW)" after them). Ranadi's line prints "Not" for each year without a figure
("Not Available"), its figures on the next line; the figures are the last years', as many as the line's figures, and a year
printed "Not Available" is not written. Each year's stations must add to its total within 0.1 GWh. Nothing is filled.

    python warehouse/connectors/siea_solomon_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/siea_sb/ and reused unless --fresh; --offline asks nothing.
solomonpower.com.sb's robots file asks a crawl delay of 10 seconds (session 2602), kept by the one request. License:
internal. Solomon Power's site reads "(c) 2026 | Solomon Islands Electricity Authority"; no terms of reuse found; internal
until a ruling.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "siea_solomon_electricity_annual"
CONNECTOR = "siea_sb"
SOURCE = "siea_sb:annual_report_2025_energy_produced"
HOST = "solomonpower.com.sb"
URL = "https://solomonpower.com.sb/wp-content/uploads/2026/09/2025-Annual-Report.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "Solomon Islands Electricity Authority (Solomon Power), Annual Report 2025, Energy Produced (by station, 2017 to 2025)"
TITLE = "Energy produced in 2025 compared with"
FIG = r"\d+(?:\.\d+)?"
X_COLS = []


def figs(s):
    return [float(x) for x in re.findall(FIG, s)] if re.fullmatch(r"(?:" + FIG + r" ?)+", s.strip()) else None


def parse_lines(lines, base):
    at = [k for k, ln in enumerate(lines) if ln.startswith(TITLE)]
    if len(at) != 1:
        raise RuntimeError(f"the table's title found {len(at)} times")
    body = lines[at[0]:]
    hd = [k for k, ln in enumerate(body) if ln.startswith("Station ")]
    if not hd:
        raise RuntimeError("the header line not found")
    years = [int(y) for y in body[hd[0]].split()[1:]]
    if not years or years != list(range(years[0], years[-1] + 1)):
        raise RuntimeError(f"the header's years are not a run: {body[hd[0]]!r}")
    n = len(years)
    rows = body[hd[0] + 1:]
    vals = {}

    def one_line(label, item):
        hit = [ln for ln in rows if ln.startswith(label + " ")]
        if len(hit) != 1:
            raise RuntimeError(f"{label!r} found {len(hit)} times")
        f = figs(hit[0][len(label):])
        if not f or len(f) != n:
            raise RuntimeError(f"{label!r}: not {n} figures: {hit[0]!r}")
        vals[item] = dict(zip(years, f))

    for label, item in (("Lungga", "lungga"), ("Honiara", "honiara"), ("Outstations", "outstations"), ("Total", "total")):
        one_line(label, item)
    k = [i for i, ln in enumerate(rows) if ln.strip() == "Henderson"]
    if len(k) != 1 or k[0] + 2 >= len(rows) or not rows[k[0] + 2].startswith("Solar"):
        raise RuntimeError("Henderson's lines not as expected")
    f = figs(rows[k[0] + 1])
    if not f or len(f) != n:
        raise RuntimeError(f"Henderson: not {n} figures: {rows[k[0] + 1]!r}")
    vals["henderson_solar"] = dict(zip(years, f))
    k = [i for i, ln in enumerate(rows) if ln.startswith("Ranadi Solar")]
    if len(k) != 1 or k[0] + 2 >= len(rows) or "Available" not in rows[k[0] + 2]:
        raise RuntimeError("Ranadi's lines not as expected")
    nots = rows[k[0]].split()[2:]
    f = figs(rows[k[0] + 1])
    if any(w != "Not" for w in nots) or not f or len(nots) + len(f) != n:
        raise RuntimeError(f"Ranadi: {len(nots)} years not available and {len(f or [])} figures for {n} years")
    vals["ranadi_solar"] = dict(zip(years[len(nots):], f))
    parts = [s for s in vals if s != "total"]
    for y in years:
        s = sum(vals[p].get(y, 0.0) for p in parts)
        if abs(s - vals["total"][y]) > 0.1:
            raise RuntimeError(f"{y}: the stations make {s:.2f} GWh, the total {vals['total'][y]}")
    labels = {"lungga": "Lungga", "honiara": "Honiara", "outstations": "Outstations", "henderson_solar": "Henderson Solar (1 MW)",
              "ranadi_solar": "Ranadi Solar (50kW)", "total": "Total"}
    out = [dict(entity=f"siea:sb:{item}", variable="production", ts_utc=f"{y}-01-01T00:00:00Z", value=round(v * 1000, 1), unit="MWh",
                freq="P1Y", geo="SB", market="", node=labels[item], **base)
           for item, d in vals.items() for y, v in d.items()]
    return pd.DataFrame(out)


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = [(pg.extract_text() or "").split("\n") for pg in pdf.pages]
    hits = [p for p in pages if any(ln.startswith(TITLE) for ln in p)]
    if len(hits) != 1:
        raise RuntimeError(f"the table's page found {len(hits)} times")
    return parse_lines(hits[0], base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Solomon Power: the Solomon Islands' production by station, 2017 to 2025")
    ap.add_argument("--offline", action="store_true", help="the saved report only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the report again")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=300, pause=10)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        tot = t[t.entity == "siea:sb:total"]
        head = [
            "Energy Research Warehouse (ERW): Solomon Islands Electricity Authority (Solomon Power), Annual Report 2025, Energy Produced: "
            "the public supply's production by station, 2017 to 2025 (session 2602)",
            "Shape: series (docs/datastandard.md v0). entity siea:sb:<station>; variable production; unit MWh (the report's GWh times "
            "1,000); ts_utc the year's first day; freq P1Y; geo SB; node the report's label.",
            f"{len(t)} rows; the total {tot.value.iloc[0] / 1e3:,.2f} GWh in {tot.ts_utc.iloc[0][:4]}, {tot.value.iloc[-1] / 1e3:,.2f} GWh in "
            f"{tot.ts_utc.iloc[-1][:4]}. Ranadi's years printed Not Available are not written; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/siea_solomon_electricity.py; the report retrieved {base['retrieved_at']}; last "
            f"modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            f"License: internal. Solomon Power's site states only its copyright line; internal until a ruling. Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Solomon Islands Electricity Authority (Solomon Power)",
                                    report="Annual Report 2025, Energy Produced (by station, 2017 to 2025)", report_url=URL,
                                    document_list="https://solomonpower.com.sb/annual-reports/", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
