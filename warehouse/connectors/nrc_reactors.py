#!/usr/bin/env python3
"""The NRC's power reactor fleet: every operating power reactor unit with its docket, license, type, place and
owner, as the NRC's list gives them today, with the licensing dates, licensed thermal power and capacity of the NRC's
operating reactors dataset, and the units in decommissioning (session 925, chain 052: the units behind nrc_reactor_status).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/nrc_power_reactors.csv, from three
documents of the U.S. Nuclear Regulatory Commission:

    https://www.nrc.gov/reactors/operating/list-power-reactor-units.html          the operating units (the list, as of the read)
    .../reading-rm/doc-collections/datasets/reactors-operating.xlsx                 the operating reactors dataset (Information Digest)
    .../reading-rm/doc-collections/datasets/reactors-decommissioning.xlsx           the reactors in decommissioning (the same)

    entity_id    nrc_reactor:<docket number>; entity_type generator (a reactor unit); name the list's or the dataset's
    geo          US-<state> from the location's last two letters
    capacity_mw  the dataset's Capacity MWe (operating units in it; empty for a unit the dataset does not hold)
    status       operating (the list) or retired (the decommissioning dataset); status_date the shutdown for a retired unit
    operator     the list's owner and operator (the dataset's parent company and licensee in their own columns)
    the rest     the list's license, reactor type, location and NRC region; the datasets' fields, renamed, with
                 x_dataset_year the dataset's "Year of Update"

The two datasets carry a "Year of Update" (2022 when written) older than the list; their columns say which they are, and a
unit on the list but not in the dataset keeps them empty. Their derived columns (reactor age, time and share of license
remaining, as of their update) and capacity factors are not taken. A date cell that holds words (the NRC's "Application
Withdrawn") keeps them as given, counted in the header. A heading not as read, a docket given twice, or a list row
without an eight-digit docket stops the run. Nothing is filled.

    python warehouse/connectors/nrc_reactors.py [--offline]

Ceiling: three requests (the list and the two workbooks; saved in warehouse/raw/nrc_reactors/ and reused offline, the
list asked again unless --offline). The NRC's robots file allows these paths (session 925). License: "NRC's website
constitutes a U.S. Government Work under federal copyright law and as such, it is not subject to copyright" (read 16 of
license_reads.csv).
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

NAME = "nrc_power_reactors"
CONNECTOR = "nrc_reactors"
SOURCE = "nrc:power_reactors"
HOST = "https://www.nrc.gov"
LIST = HOST + "/reactors/operating/list-power-reactor-units.html"
DATASETS = HOST + "/sites/default/files/doc_library/cdn/legacy/reading-rm/doc-collections/datasets/"
OPERATING, DECOM = DATASETS + "reactors-operating.xlsx", DATASETS + "reactors-decommissioning.xlsx"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
LIST_COLS = ["Plant Name Docket Number", "License Number", "Reactor Type", "Location", "Owner/Operator", "NRC Region"]
OP_FIELDS = {"Plant Name, Unit Number": "x_dataset_name", "Parent Company Utility Name": "x_parent_company", "Licensee": "x_licensee",
             "Reactor and Containment Type": "x_containment_type", "Nuclear Steam System Supplier and Design Type": "x_nsss",
             "Architect-Engineer": "x_architect_engineer", "Constructor Name": "x_constructor",
             "Construction Permit Issued": "x_construction_permit", "Operating License Issued": "x_operating_license",
             "Commercial Operation": "x_commercial_operation", "Renewed Operating License Issued": "x_renewed_license",
             "Operating License Expires": "x_license_expires", "Subsequent Renewed Operating License Issued": "x_subsequent_renewal",
             "Licensed MWt": "x_licensed_mwt"}
DECOM_FIELDS = {"Unit": "x_dataset_name", "MWt": "x_licensed_mwt", "NSSS Vendor": "x_nsss", "Operating License (OL) Issued": "x_operating_license",
                "Shut Down": "x_shut_down", "Operating License (OL) Terminated": "x_license_terminated",
                "Closure Date Est.": "x_closure_estimate", "Decommissioning Alternative Selected": "x_decommissioning_alternative",
                "Current License Status": "x_license_status"}
DATES = {"x_construction_permit", "x_operating_license", "x_commercial_operation", "x_renewed_license", "x_license_expires",
         "x_subsequent_renewal", "x_shut_down", "x_license_terminated"}
TEXTS = []
EXTRA = (["x_docket", "x_license_number", "x_reactor_type", "x_location", "x_nrc_region", "x_dataset_year"]
         + sorted(set(OP_FIELDS.values()) | set(DECOM_FIELDS.values())))


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else re.sub(r"\s+", " ", str(v)).strip()


def day(v):
    s = text(v)
    if not s:
        return ""
    d = pd.to_datetime(s, errors="coerce")
    if pd.isna(d):
        TEXTS.append(s)   # the NRC writes a word where a date is not ("Application Withdrawn"): kept as given, counted
        return s
    return d.strftime("%Y-%m-%d")


def state(location):
    m = re.search(r"\b([A-Z]{2})\)?\s*$", location)
    return f"US-{m.group(1)}" if m else ""


def docket(v):
    s = re.sub(r"\D", "", text(v))
    return s.zfill(8) if s else ""


def list_rows(html):
    tables = pd.read_html(io.StringIO(html))
    if len(tables) != 1 or list(tables[0].columns) != LIST_COLS:
        raise RuntimeError(f"the list's table is not as read: {[list(t.columns) for t in tables]}")
    out = []
    for _, r in tables[0].iterrows():
        m = re.fullmatch(r"(.+?)\s+(\d{8})", text(r["Plant Name Docket Number"]))
        if not m:
            raise RuntimeError(f"a list row without an eight-digit docket: {text(r['Plant Name Docket Number'])!r}")
        out.append({"docket": m.group(2), "name": m.group(1), "x_license_number": text(r["License Number"]),
                    "x_reactor_type": text(r["Reactor Type"]), "x_location": text(r["Location"]), "operator": text(r["Owner/Operator"]),
                    "x_nrc_region": text(r["NRC Region"])})
    return out


def dataset(frame, fields, extra):
    missing = [c for c in list(fields) + extra if c not in frame.columns]
    if missing:
        raise RuntimeError(f"a dataset's headings are not as read: missing {missing}")
    out = {}
    for _, r in frame.iterrows():
        d = docket(r["Docket Number"])
        if not d:
            continue
        if d in out:
            raise RuntimeError(f"a docket given twice in a dataset: {d}")
        row = {"x_dataset_year": text(r["Year of Update"])}
        for k, v in fields.items():
            row[v] = day(r[k]) if v in DATES else text(r[k])
        for k in extra:
            row[k] = text(r[k])
        out[d] = row
    return out


def build(listed, op, decom, urls, retrieved, vintage):
    rows = []
    for u in listed:
        d = op.get(u["docket"], {})
        cap = pd.to_numeric(d.get("Capacity MWe", ""), errors="coerce")
        row = {"entity_id": f"nrc_reactor:{u['docket']}", "entity_type": "generator", "name": u["name"], "geo": state(u["x_location"]),
               "lat": "", "lon": "", "capacity_mw": "" if pd.isna(cap) else float(cap), "status": "operating", "status_date": "",
               "operator": u["operator"], "source": SOURCE, "source_url": urls["list"], "retrieved_at": retrieved["list"],
               "vintage": vintage["list"], "x_docket": u["docket"]}
        row.update({k: v for k, v in u.items() if k.startswith("x_")})
        row.update({k: v for k, v in d.items() if k.startswith("x_")})
        rows.append(row)
    on_list = {u["docket"] for u in listed}
    for k, d in decom.items():
        if k in on_list:
            continue
        loc = d.get("Location", "")
        row = {"entity_id": f"nrc_reactor:{k}", "entity_type": "generator", "name": d["x_dataset_name"], "geo": state(loc + ")") if loc else "",
               "lat": "", "lon": "", "capacity_mw": "", "status": "retired", "status_date": d.get("x_shut_down", ""), "operator": "",
               "source": SOURCE, "source_url": urls["decom"], "retrieved_at": retrieved["decom"], "vintage": vintage["decom"],
               "x_docket": k, "x_location": loc, "x_reactor_type": d.get("Reactor Type", "")}
        row.update({c: v for c, v in d.items() if c.startswith("x_")})
        rows.append(row)
    t = pd.DataFrame(rows)
    for c in EXTRA:
        if c not in t.columns:
            t[c] = ""
    t = t.fillna("")
    if t.entity_id.duplicated().any():
        raise RuntimeError(f"a docket given twice: {t.loc[t.entity_id.duplicated(), 'entity_id'].head(3).tolist()}")
    return t[ENTITY_COLS + EXTRA].sort_values(["status", "entity_id"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The NRC's power reactor units, operating and in decommissioning")
    ap.add_argument("--offline", action="store_true", help="the saved list and workbooks only, no request")
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
        html, lrec = ip.fetch_raw(CONNECTOR, LIST, log, offline=args.offline, fresh=not args.offline, headers=UA)
        ob, orec = ip.fetch_raw(CONNECTOR, OPERATING, log, offline=args.offline, headers=UA)
        db, drec = ip.fetch_raw(CONNECTOR, DECOM, log, offline=args.offline, headers=UA)
        listed = list_rows(html.decode("utf-8", errors="replace"))
        op = dataset(pd.read_excel(io.BytesIO(ob), dtype=str), OP_FIELDS, ["Docket Number", "Year of Update", "Capacity MWe"])
        decom = dataset(pd.read_excel(io.BytesIO(db), dtype=str), DECOM_FIELDS, ["Docket Number", "Year of Update", "Location", "Reactor Type"])
        urls = {"list": LIST, "decom": DECOM}
        retrieved = {"list": lrec.get("retrieved_at") or "", "decom": drec.get("retrieved_at") or ""}
        vintage = {"list": ip.vintage_of(lrec), "decom": ip.vintage_of(drec)}
        t = build(listed, op, decom, urls, retrieved, vintage)
        on = t[t.status == "operating"]
        no_ds = int((on.x_dataset_year == "").sum())
        years = sorted(set(v["x_dataset_year"] for v in list(op.values()) + list(decom.values())))
        not_listed = sorted(set(op) - {u["docket"] for u in listed})
        cap = pd.to_numeric(on.capacity_mw, errors="coerce")
        header = [
            "Energy Research Warehouse (ERW): the NRC's power reactor units, operating (the NRC's list) and in decommissioning (the NRC's dataset), with the operating reactors dataset's licensing dates and capacity (session 925)",
            "Shape: entities (docs/datastandard.md v0). entity_id nrc_reactor:<docket number>; entity_type generator (a reactor unit); geo US-<state>; "
            "capacity_mw the operating dataset's Capacity MWe; status operating (on the list) or retired (in decommissioning, status_date its shutdown); "
            "operator the list's owner and operator; x_* the list's and the datasets' fields, x_dataset_year the datasets' Year of Update.",
            f"{len(on)} operating units on the list ({cap.sum():,.0f} MWe for the {int(cap.notna().sum())} the dataset holds; {no_ds} on the list but not "
            f"in the dataset, their dataset columns empty); {int((t.status == 'retired').sum())} units in decommissioning. The datasets' Year of Update: "
            f"{', '.join(years)}, older than the list" + (f"; in the operating dataset but not on the list: {', '.join(not_listed)}" if not_listed else "")
            + f". Their derived columns (age, license remaining) and capacity factors are not taken. {len(TEXTS)} date cells hold words, kept as given"
            + (f" ({'; '.join(sorted(set(TEXTS)))})" if TEXTS else "") + ". Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nrc_reactors.py; the list retrieved {retrieved['list']}, the datasets "
            f"{orec.get('retrieved_at', '')} (last modified {ip.vintage_of(orec)} and {vintage['decom']})",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Nuclear Regulatory Commission, List of Power Reactor Units and the operating and decommissioning reactors datasets, {LIST}",
            f"  access: {LIST}; {OPERATING}; {DECOM}",
            "License: public (the NRC's website is a U.S. Government Work, not subject to copyright; read 16 of license_reads.csv).",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Nuclear Regulatory Commission (NRC)",
                                    report="List of Power Reactor Units; operating and decommissioning reactors datasets", report_url=LIST,
                                    document_list=HOST + "/documents-reports/nrc-data", license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} units"))
        print(f"{NAME}: {len(on)} operating, {int((t.status == 'retired').sum())} retired; {no_ds} operating not in the dataset")
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
