#!/usr/bin/env python3
"""Run every datacenter operator connector: warehouse/output/datacenter_operator_sites.csv.

Energy Research Warehouse (ERW), session 22, Task 2b. The operators' own public lists of
their regions, campuses and data centers, one connector per operator in this folder:

    python warehouse/datacenters/operators/run.py            # all operators
    python warehouse/datacenters/operators/run.py --only aws,meta

Each connector reads its operator's public page (and the pages it links, where the list
points to per-site pages), every response stored raw under
warehouse/raw/datacenter_operators/<run_id>/ with a manifest, and yields facilities with
their source_url; the rules are in common.py (nothing inferred: a state only where the page
names one, MW only with its exact span, a status only where stated). A connector that fails
is logged with its error and the others continue; its operator is missing from the table
and the run log and run status say so.

Skipped operators (the prompt's twelve less the nine connectors), checked each run: the page
is read and stored raw, and the log says what it holds.
- QTS: qtsdatacenters.com redirects to q.com, which answers HTTP 503 to a plain request.
- CoreWeave: the region list is in the documentation behind a login
  (docs.coreweave.com/docs/platform/regions redirects to /login); the public page on regions
  names only example region codes (US-EAST-04, US-EAST-05), with no places.
- Crusoe: crusoe.ai/data-centers states fleet totals (6.1 gigawatts, 16.8M sq ft, 3,500
  acres) and no list of sites; its sites are named only in press releases (the news tracker
  reads those).

Placement: a facility with the operator's own coordinates (Google, Digital Realty) is placed
there (geo_precision operator); else at the Census gazetteer's internal point of its stated
county or city (the datacenter extractor's locate(), geo_precision county or place); else not
placed (none), with the reason in geo_note.

Output: entities, entity_type datacenter, kind operator, one snapshot per run.
"""
import argparse
import datetime as dt
import hashlib
import importlib
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402
from common import ip  # noqa: E402

ROOT = common.ROOT
sys.path.insert(0, os.path.join(ROOT, "warehouse", "datacenters"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))

NAME = "datacenter_operator_sites"
CONNECTORS = ["aws", "azure", "google", "meta", "oracle", "digital_realty", "equinix", "vantage", "switch"]
SKIPPED = {
    "QTS": ("https://qtsdatacenters.com/data-centers",
            "the site redirects to q.com, which answers HTTP 503 to a plain request; no list could be read"),
    "CoreWeave": ("https://docs.coreweave.com/platform/regions/about-regions-and-azs",
                  "the region list is behind a login; the public page names only example region codes, no places"),
    "Crusoe": ("https://www.crusoe.ai/data-centers",
               "the page states fleet totals only (gigawatts, square feet, acres), no list of sites"),
}
STD = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date",
       "operator", "source", "source_url", "retrieved_at", "vintage"]
EXTRA = ["kind", "site_type", "operator_code", "place_text", "state", "county", "city", "mw", "mw_span",
         "status_text", "detail", "geo_precision", "geo_note"]
COLS = STD + EXTRA


def site_id(f):
    key = "|".join([f["operator"], f["site_type"], f["operator_code"] or f["name"]])
    return "dcsite:" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW datacenter operator sites")
    ap.add_argument("--only", help="comma-separated connectors (default: all)")
    args = ap.parse_args(argv)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"datacenter_operators_{run_id}.log"))
    ip.RAW.open("datacenter_operators", run_id)
    names = args.only.split(",") if args.only else CONNECTORS
    log(f"ERW datacenter operator sites {run_id}: connectors {', '.join(names)}")
    rows, results, sources = [], [], []
    for n in names:
        mod = importlib.import_module(n)
        try:
            got = mod.facilities(log)
        except Exception as exc:  # noqa: BLE001  (fail loudly per operator, continue with the others)
            log(f"  FAILED {n}: {exc!r}")
            results.append(dict(table=NAME, market=f"operator:{n}", status="failed", detail=repr(exc)[:300]))
            continue
        for f in got:
            f["source"] = mod.SOURCE
        rows += got
        results.append(dict(table=NAME, market=f"operator:{n}", status="ok" if got else "failed",
                            detail=f"{len(got)} facilities" if got else "no facilities found"))
        sources.append(dict(source=mod.SOURCE, publisher=mod.OPERATOR,
                            report=f"{mod.OPERATOR} public list of data center sites and regions",
                            report_url=mod.URL, document_list="", license="public", tables=[NAME]))
    for op, (url, why) in SKIPPED.items():
        try:
            common.get(url, log)
            seen = "read"
        except Exception as exc:  # noqa: BLE001
            seen = f"not read ({exc})"
        log(f"  SKIPPED {op}: {why} (page {url}: {seen})")
        results.append(dict(table=NAME, market=f"operator:{op}", status="skipped", detail=why))
    if not rows:
        log("no facilities from any connector; table not written")
        ip.write_status("datacenter_operators", run_id, results)
        log.close()
        return 1

    import extract as dcx  # the datacenter extractor's placement (county or place internal point)
    import energy_projects as ep
    counties, _ = ep.load_gazetteer(run_id, log)
    places, _ = dcx.load_places(log)
    now = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    out = []
    for f in rows:
        r = {c: "" for c in COLS}
        r.update({k: f[k] for k in ("operator", "name", "site_type", "operator_code", "place_text", "state", "county",
                                    "city", "mw_span", "status", "status_text", "detail", "source", "source_url")})
        r["entity_id"], r["entity_type"], r["kind"] = site_id(f), "datacenter", "operator"
        r["geo"] = f"US-{f['state']}" if f["state"] else "US"
        r["retrieved_at"], r["vintage"] = now, run_id[:8]
        if f["mw"] is not None:
            r["mw"] = r["capacity_mw"] = f"{f['mw']:g}"
        if f["lat"] and f["lon"]:
            r["lat"], r["lon"] = f"{float(f['lat']):.6f}", f"{float(f['lon']):.6f}"
            r["geo_precision"], r["geo_note"] = "operator", "the operator's own coordinates on the page"
        else:
            r["lat"], r["lon"], r["geo_precision"], r["geo_note"] = dcx.locate(r, counties, places)
        out.append(r)
    table = pd.DataFrame(out, columns=COLS)
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if args.only and os.path.exists(path):
        # a partial run replaces only its own operators' rows; the others stay as the last full run wrote them
        with open(path, encoding="utf-8") as fh:
            n = sum(1 for line in fh if line.startswith("#"))
        old = pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, na_values=[])
        keep = old[~old["source"].isin(set(table["source"]))]
        log(f"  --only: {len(keep)} rows of other operators kept from the last table")
        table = pd.concat([table, keep[COLS]], ignore_index=True)
    dup = table["entity_id"].duplicated()
    if dup.any():
        log(f"  {int(dup.sum())} repeated sites (same operator, type and code) kept once")
        table = table[~dup]
    table = table.sort_values(["operator", "state", "name"]).reset_index(drop=True)
    header = [
        "Energy Research Warehouse (ERW): Datacenter sites from the operators' own public lists (session 22)",
        "Shape: entities (docs/datastandard.md), entity_type datacenter, kind operator; one snapshot per run. "
        "capacity_mw = mw, only where the page states it, with the exact span in mw_span.",
        f"Retrieved: {run_id} (UTC) by warehouse/datacenters/operators/run.py (one connector per operator)",
        f"Run log: warehouse/output/logs/datacenter_operators_{run_id}.log",
        f"Raw files: warehouse/raw/datacenter_operators/{run_id}/ (not in git; manifest.csv lists each page)",
        "Sources: " + "; ".join(f"{s['publisher']} {s['report_url']}" for s in sources),
        "Rules: a state only where the page names it; MW only with its exact span, checked against the page text; "
        "status only where stated (Oracle Live or Coming soon; Google inDevelopment). geo_precision: operator "
        "(the page's coordinates), county or place (Census gazetteer internal point of the stated county or city), "
        "or none. Skipped operators: " + "; ".join(f"{k}: {v[1]}" for k, v in SKIPPED.items()) + ".",
        "License: public (facts from the operators' public pages).",
    ]
    if args.only:
        header.insert(3, f"Partial run (--only {args.only}): the other operators' rows are from the previous run; "
                         "each row's retrieved_at and source say when and where it came from.")
    ip.write_snapshot(table, NAME, header, log, COLS)
    ip.update_sources(sources)
    ip.write_status("datacenter_operators", run_id, results)
    by = table.groupby("operator").agg(n=("entity_id", "size"), placed=("geo_precision", lambda s: int((s != "none").sum())),
                                      with_mw=("mw", lambda s: int((s != "").sum())))
    log("  per operator (sites, placed, with MW):\n" + by.to_string())
    log(f"done: {len(table)} sites from {table['operator'].nunique()} operators")
    log.close()
    print(f"datacenter operator sites: {len(table)} from {table['operator'].nunique()} operators; run log "
          f"{os.path.relpath(log.path, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
