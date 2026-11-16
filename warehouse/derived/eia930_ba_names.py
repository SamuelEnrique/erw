#!/usr/bin/env python3
"""EIA's balancing authorities, code and name, as a site file (session 7019, chain 301; done-line request 21).

Energy Research Warehouse (ERW). Writes site/data/eia930_ba_names.json from the newest saved copy of EIA's EIA-930
reference tables (warehouse/raw/eia930_reference/<run>/EIA930_Reference_Tables.xlsx, sheet "BAs"): every balancing
authority's code, name, time zone and region, as EIA prints them. The contracts page names the delivery balancing
authority FERC's filers write by these codes (it named only the seven grids' before). EIA's publications are in the
public domain. Nothing from the internal EQR tables is written here: the page maps its own codes.

    python warehouse/derived/eia930_ba_names.py            # from the newest saved workbook
    python warehouse/derived/eia930_ba_names.py --fetch    # save a new copy first (one request to www.eia.gov)

No model is called. It writes only the one site file (and, with --fetch, the raw copy and its manifest).
"""
import argparse
import csv
import datetime as dt
import glob
import hashlib
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RAW = os.path.join(ROOT, "warehouse", "raw", "eia930_reference")
OUT = os.path.join(ROOT, "site", "data", "eia930_ba_names.json")
URL = "https://www.eia.gov/electricity/930-content/EIA930_Reference_Tables.xlsx"
PAGE = "https://www.eia.gov/electricity/gridmonitor/about"


def fetch():
    run = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder = os.path.join(RAW, run)
    os.makedirs(folder, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "ERW-research-warehouse"})
    with urllib.request.urlopen(req, timeout=60) as r:
        body, status, final = r.read(), r.status, r.geturl()
    with open(os.path.join(folder, "EIA930_Reference_Tables.xlsx"), "wb") as f:
        f.write(body)
    got = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(os.path.join(folder, "manifest.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["retrieved_at", "status", "bytes", "sha256", "url"])
        w.writerow([got, status, len(body), hashlib.sha256(body).hexdigest(), final])
    return folder


def newest():
    runs = sorted(d for d in glob.glob(os.path.join(RAW, "*")) if os.path.exists(os.path.join(d, "manifest.csv")))
    if not runs:
        raise SystemExit("no saved EIA-930 reference workbook: run with --fetch")
    return runs[-1]


def build(folder):
    import openpyxl
    with open(os.path.join(folder, "manifest.csv"), encoding="utf-8") as f:
        man = next(csv.DictReader(f))
    wb = openpyxl.load_workbook(os.path.join(folder, "EIA930_Reference_Tables.xlsx"), read_only=True)
    rows = wb["BAs"].iter_rows(values_only=True)
    head = list(next(rows))
    need = ["BA Code", "BA Name", "Time Zone", "Region/Country Code", "Region/Country Name", "U.S. BA"]
    if not set(need) <= set(head):
        raise SystemExit(f"sheet BAs: columns {head} are not EIA's reference table's")
    at = {k: head.index(k) for k in need}
    out = {}
    for r in rows:
        code = (r[at["BA Code"]] or "").strip()
        if not code:
            continue
        out[code] = {"name": (r[at["BA Name"]] or "").strip(), "time_zone": r[at["Time Zone"]] or "",
                     "region": r[at["Region/Country Name"]] or "", "region_code": r[at["Region/Country Code"]] or "",
                     "us": (r[at["U.S. BA"]] or "") == "Yes"}
    if len(out) < 50:
        raise SystemExit(f"sheet BAs: {len(out)} authorities read, fewer than EIA lists")
    doc = {"about": "EIA's balancing authorities, code and name, from the EIA-930 reference tables (sheet BAs), as EIA prints "
                    "them; public domain. Written by warehouse/derived/eia930_ba_names.py (session 7019).",
           "source": "U.S. Energy Information Administration, EIA-930 reference tables", "source_url": man["url"],
           "page": PAGE, "retrieved_at": man["retrieved_at"], "sha256": man["sha256"],
           "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "count": len(out),
           "authorities": dict(sorted(out.items()))}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's balancing authorities as a site file")
    ap.add_argument("--fetch", action="store_true")
    a = ap.parse_args(argv)
    folder = fetch() if a.fetch else newest()
    doc = build(folder)
    print(f"eia930_ba_names: {doc['count']} authorities from {folder} written to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
