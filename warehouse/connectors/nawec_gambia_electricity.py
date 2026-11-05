#!/usr/bin/env python3
"""The Gambia's electricity a month in 2022 by source, as the National Water and Electricity Company (NAWEC) gives it in Table 3
("Electricity Month Production") of its Annual Activity Report 2022: NAWEC's own plants, the imports from SENELEC and through
the OMVG interconnection, Karpowership's supply and the total (session 2617, chain 130; the ERW held the Gambia in no table but
EIA's international one).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/nawec_gambia_electricity_monthly.csv, from one
PDF (no key):

    https://nawec.gm/wp-content/uploads/2026/08/NAWEC-Annual-Activity-Report-2022.pdf

    entity      nawec:gm:<source>: nawec (NAWEC's plants: Kotu, Brikama 1 to 3 and the provinces' stations), senelec (imports
                from SENELEC over its lines), omvg (imports through the OMVG 225 kV interconnection), karpower (Karpowership, an
                independent producer) and total
    variable    generation (nawec, karpower), imports (senelec, omvg), supply (total); the report calls every column "production"
    unit        MWh; ts_utc the month's first day; freq P1M; geo GM
    node        the report's column heading

The table is found by its title line ("2022 Monthly Production ( MWh)"), once; the next line must name the columns (NAWEC,
SENELEC, OMVG, Karpower, Total, read with the PDF's stray spaces removed); then twelve lines, January to December, each a month
and five figures, then the "Total" line. Checks: each month's four sources add to its total within 0.1 MWh; each column's
months add to its Total within 0.5 MWh. The table's percentages are not taken. Nothing is filled.

    python warehouse/connectors/nawec_gambia_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/nawec_gm/ and reused unless --fresh; --offline asks nothing. nawec.gm has no
robots file (HTTP 404, session 2617). License: internal. NAWEC's site reads "(c) 2026 NAWEC ... All rights reserved." and links no
terms page; internal until a ruling.
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

NAME = "nawec_gambia_electricity_monthly"
CONNECTOR = "nawec_gm"
SOURCE = "nawec_gm:annual_activity_report_2022_table3"
HOST = "nawec.gm"
URL = "https://nawec.gm/wp-content/uploads/2026/08/NAWEC-Annual-Activity-Report-2022.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = "National Water and Electricity Company (NAWEC), Annual Activity Report 2022, Table 3: Electricity Month Production"
TITLE = "2022 Monthly Production ( MWh)"
YEAR = 2022
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
COLS = [("NAWEC", "nawec", "generation"), ("SENELEC", "senelec", "imports"), ("OMVG", "omvg", "imports"),
        ("Karpower", "karpower", "generation"), ("Total", "total", "supply")]
FIG = r"\d[\d,]*(?:\.\d+)?"
X_COLS = []


def figs(s):
    v = re.findall(FIG, s)
    if " ".join(v) != s.strip():
        raise RuntimeError(f"not a line of figures: {s!r}")
    return [float(x.replace(",", "")) for x in v]


def parse_lines(lines, base):
    lines = [ln.strip() for ln in lines]
    at = [i for i, ln in enumerate(lines) if ln == TITLE]
    if len(at) != 1:
        raise RuntimeError(f"the table's title found {len(at)} times")
    head = lines[at[0] + 1].replace(" ", "")
    if head != "Month" + "".join(c[0] for c in COLS):
        raise RuntimeError(f"the column line is {lines[at[0] + 1]!r}")
    rows = {}
    for k, month in enumerate(MONTHS):
        ln = lines[at[0] + 2 + k]
        if not ln.startswith(month + " "):
            raise RuntimeError(f"{month}: the line is {ln!r}")
        v = figs(ln[len(month):])
        if len(v) != len(COLS):
            raise RuntimeError(f"{month}: {len(v)} figures")
        if abs(sum(v[:4]) - v[4]) > 0.1:
            raise RuntimeError(f"{month}: the sources make {sum(v[:4]):.2f} MWh, the total {v[4]}")
        rows[k + 1] = v
    ln = lines[at[0] + 14]
    if not ln.startswith("Total "):
        raise RuntimeError(f"the Total line is {ln!r}")
    tot = figs(ln[len("Total"):])
    if len(tot) != len(COLS):
        raise RuntimeError("the Total line's figures")
    for j, (label, _, _) in enumerate(COLS):
        s = sum(r[j] for r in rows.values())
        if abs(s - tot[j]) > 0.5:
            raise RuntimeError(f"{label}: the months make {s:.2f} MWh, the Total {tot[j]}")
    out = [dict(entity=f"nawec:gm:{item}", variable=variable, ts_utc=f"{YEAR}-{m:02d}-01T00:00:00Z", value=round(v[j], 3), unit="MWh",
                freq="P1M", geo="GM", market="", node=label, **base)
           for m, v in rows.items() for j, (label, item, variable) in enumerate(COLS)]
    return pd.DataFrame(out)


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        lines = [ln for pg in pdf.pages for ln in (pg.extract_text() or "").split("\n")]
    return parse_lines(lines, base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="NAWEC: the Gambia's electricity by source a month in 2022")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=300, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        tot = t[t.entity == "nawec:gm:total"]
        head = [
            "Energy Research Warehouse (ERW): National Water and Electricity Company (NAWEC), Annual Activity Report 2022, Table 3: the "
            "Gambia's electricity a month in 2022 by source (session 2617)",
            "Shape: series (docs/datastandard.md v0). entity nawec:gm:<source> (nawec, senelec, omvg, karpower, total); variable "
            "generation (nawec, karpower), imports (senelec, omvg) or supply (total); unit MWh; ts_utc the month's first day; freq P1M; "
            "geo GM; node the report's column.",
            f"{len(t)} rows; the year's supply {tot.value.sum():,.2f} MWh. Each month's sources checked against its total and each "
            "column against the Total line; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nawec_gambia_electricity.py; the report retrieved {base['retrieved_at']}; "
            f"last modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            f"License: internal. NAWEC's site states only its copyright line; internal until a ruling. Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="National Water and Electricity Company (NAWEC)",
                                    report="Annual Activity Report 2022, Table 3: Electricity Month Production", report_url=URL,
                                    document_list="https://nawec.gm/?page_id=196", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
