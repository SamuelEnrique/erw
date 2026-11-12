#!/usr/bin/env python3
"""Grid operators' reserve margins, as their own assessments print them: the registry of figures a session reads (session
3798, chain 215).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/iso_reserve_margin_reports.csv, from the
registry files sessions fill by reading each grid operator's resource adequacy assessment:

    warehouse/sources/reserve_margins/<body>_<document>.yaml    one file a document (README.md there: the form)

No request is made here: a session reads the document (robots and terms first), writes each figure into the file with
the page it is printed on and the words it is printed in, and this connector turns the files into rows. A figure is kept
as the document prints it (x_printed), never derived, summed or estimated. A figure the document does not print has no
row. It fills the All grids tab's Headroom row "reserve margins by zone" for the grids whose operator publishes an
assessment this reader may read (ERCOT's has its own table, ercot_cdr_reserve_margins).

    entity      reserve_report:<grid>:<document slug>; node the document; geo US
    ts_utc      the period's first day (the registry's ts), 00:00:00Z; freq blank
    variable    prm_achieved_pct (pct), prm_required_pct (pct), capacity_surplus_mw (MW), peak_forecast_mw (MW),
                ra_prm_load_weighted_pct (pct)
    source      the file's source (one a publisher, named in sources.csv with its publisher for the license record)
    source_url  the document; x_page the page of the figure
    x_*         x_grid, x_body, x_document, x_period, x_page, x_printed

License: each row as its publisher's verdict (warehouse/metadata/license_verdicts.csv): the file's license field is
public only where the publisher's terms allow it.

    python warehouse/connectors/reserve_margin_reports.py              # the table (data lock)
    python warehouse/connectors/reserve_margin_reports.py --check      # read and check the registry, write nothing
    python warehouse/connectors/reserve_margin_reports.py --out-dir D  # a trial: the table under D (no data lock)

Method: docs/methods/reserve_margin_reports.md.
"""

import argparse
import datetime as dt
import glob
import os
import re
import sys
import traceback

import pandas as pd
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REGISTRY = os.path.join(ROOT, "warehouse", "sources", "reserve_margins")
NAME = "iso_reserve_margin_reports"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/reserve_margin_reports.md"
UNITS = {"prm_achieved_pct": "pct", "prm_required_pct": "pct", "capacity_surplus_mw": "MW", "peak_forecast_mw": "MW",
         "ra_prm_load_weighted_pct": "pct"}
FIELDS = ("body", "grid", "publisher", "source", "document", "document_url", "period", "ts", "retrieved_at", "license", "figures")
X_COLS = ["x_grid", "x_body", "x_document", "x_period", "x_page", "x_printed"]
COLS = ip.SERIES_COLS + X_COLS
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")[:60]


def check(reg, path):
    """The problems of one document's file, as sentences; [] when it can be written."""
    bad = [f"no {k}" for k in FIELDS if reg.get(k) in (None, "", [])]
    if not DATE_RE.match(str(reg.get("ts") or "")):
        bad.append(f"ts {reg.get('ts')!r} is not YYYY-MM-DD")
    if not TS_RE.match(str(reg.get("retrieved_at") or "")):
        bad.append(f"retrieved_at {reg.get('retrieved_at')!r} is not YYYY-MM-DDTHH:MM:SSZ")
    if not str(reg.get("document_url") or "").startswith(("http://", "https://")):
        bad.append("document_url is not an address")
    if str(reg.get("license") or "") not in ("public", "internal"):
        bad.append(f"license {reg.get('license')!r} is not public or internal")
    seen = set()
    for i, f in enumerate(reg.get("figures") or []):
        v = f.get("variable")
        if v not in UNITS:
            bad.append(f"figure {i}: variable {v!r} is not one of {sorted(UNITS)}")
        if v in seen:
            bad.append(f"figure {i}: {v} twice")
        seen.add(v)
        if not isinstance(f.get("value"), (int, float)) or isinstance(f.get("value"), bool):
            bad.append(f"figure {i} ({v}): value {f.get('value')!r} is not a number")
        if f.get("page") in (None, ""):
            bad.append(f"figure {i} ({v}): no page")
        if not str(f.get("printed") or "").strip():
            bad.append(f"figure {i} ({v}): no printed words")
    return [f"{os.path.basename(path)}: {b}" for b in bad]


def read_registry(folder=REGISTRY):
    """(the documents' files as dicts with their paths, the problems)."""
    regs, problems = [], []
    for p in sorted(glob.glob(os.path.join(folder, "*.yaml"))):
        with open(p, encoding="utf-8") as fh:
            reg = yaml.safe_load(fh) or {}
        for k in ("ts", "retrieved_at"):   # YAML reads an unquoted date or time as one: written back as text
            v = reg.get(k)
            if isinstance(v, dt.datetime):
                reg[k] = v.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if v.tzinfo else v.strftime("%Y-%m-%dT%H:%M:%SZ")
            elif isinstance(v, dt.date):
                reg[k] = v.isoformat()
        problems += check(reg, p)
        regs.append((p, reg))
    return regs, problems


def rows(regs):
    """The table's rows from the public documents' files."""
    out = []
    for p, reg in regs:
        if str(reg.get("license")) != "public":
            continue
        common = {"entity": f"reserve_report:{str(reg['grid']).lower()}:{slug(reg['document'])}", "ts_utc": f"{reg['ts']}T00:00:00Z",
                  "freq": "", "geo": "US", "market": "", "node": str(reg["document"]), "source": str(reg["source"]),
                  "source_url": str(reg["document_url"]), "retrieved_at": str(reg["retrieved_at"]), "vintage": "",
                  "x_grid": str(reg["grid"]), "x_body": str(reg["body"]), "x_document": str(reg["document"]), "x_period": str(reg["period"])}
        for f in reg["figures"]:
            v = f["variable"]
            out.append({**common, "variable": v, "value": float(f["value"]), "unit": UNITS[v], "x_page": str(f["page"]),
                        "x_printed": " ".join(str(f["printed"]).split())})
    d = pd.DataFrame(out, columns=COLS).fillna("")
    return d.sort_values(["x_grid", "entity", "variable"]).reset_index(drop=True)


def header(d, run_id):
    docs = d.drop_duplicates("entity")[["x_grid", "x_document"]].itertuples(index=False) if len(d) else []
    return [
        "Energy Research Warehouse (ERW): grid operators' reserve margins as their own assessments print them, one row a figure (session 3798, chain 215)",
        "Shape: series (docs/datastandard.md v0). entity reserve_report:<grid>:<document>; ts_utc the period's first day at 00:00:00Z; variables "
        + ", ".join(f"{k} ({u})" for k, u in UNITS.items()) + ". value is the printed figure (x_printed); nothing is derived. source_url is the document, x_page its page.",
        "Documents: " + ("; ".join(f"{g}: {doc}" for g, doc in docs) if len(d) else "none"),
        "Source: the registry warehouse/sources/reserve_margins/ (one file a document, each figure with its page and words), filled by reading each "
        "grid operator's own assessment. No request is made by this connector.",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/reserve_margin_reports.py; each row's retrieved_at is when its document was read",
        f"Method: {METHOD_URL}",
        "License: public, row by row: a document is written here only where its publisher's terms allow it (warehouse/metadata/license_verdicts.csv).",
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: grid operators' reserve margins from the registry (session 3798)")
    ap.add_argument("--check", action="store_true", help="read and check the registry; write nothing")
    ap.add_argument("--out-dir", help="a trial: write under this directory (no data lock)")
    ap.add_argument("--registry", default=REGISTRY, help="the registry folder (a test's)")
    a = ap.parse_args(argv)
    regs, problems = read_registry(a.registry)
    for p in problems:
        print(f"REFUSED: {p}")
    if problems:
        print(f"{NAME} FAILED: {len(problems)} problems in the registry; nothing written")
        return 1
    d = rows(regs)
    print(f"{NAME}: {len(regs)} documents, {len(d)} rows, grids {sorted(d['x_grid'].unique()) if len(d) else []}")
    if a.check:
        return 0
    if d.empty:
        print(f"{NAME} SKIPPED: the registry holds no public document; nothing written")
        return int(os.environ.get("ERW_SKIP_EXIT", "75"))
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    try:
        ip.write_csv(d, NAME, header(d, run_id), log, cols=COLS)
        if not a.out_dir:
            seen = {}
            for _, reg in regs:
                if str(reg.get("license")) == "public":
                    seen.setdefault(str(reg["source"]), reg)
            ip.update_sources([dict(source=s, publisher=str(reg["publisher"]), report=str(reg["document"]), report_url=str(reg["document_url"]),
                                    document_list=METHOD_URL, license="public", tables=[NAME]) for s, reg in seen.items()])
    except Exception as exc:
        print(f"{NAME} FAILED: {type(exc).__name__}: {exc}")
        log(traceback.format_exc())
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
