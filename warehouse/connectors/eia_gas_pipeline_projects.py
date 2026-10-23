#!/usr/bin/env python3
"""EIA's natural gas pipeline projects: each project's operator, type, status, states and regions, cost, miles, added
capacity, diameter, authority and docket, current and historical (session 899, chain 049).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/eia_gas_pipeline_projects.csv, from the U.S.
Energy Information Administration's natural gas pipeline projects tracker, the newest workbook its natural gas data page
links (EIA-NaturalGasPipelineProjects<Mon><year>.xlsx, sheets "Natural Gas Pipeline Projects" and "Historical Projects
(1996-...)"):

    page   https://www.eia.gov/naturalgas/data.php

    event_id    eia_gas_pipeline:<the project's name as a slug>:<EIA's year in service as a slug, none if empty> (EIA writes
                na, or a range such as "2020-2027 (phased)", for some)
    event_date  the completed date where EIA gives one (kept as EIA gives it: one historical project's is 1903-11-05
                against a year in service of 2003), else the year in service's 1 January, else the
                date EIA last updated the record; x_date_basis says which (completed, year_in_service, last_updated)
    event_type  pipeline_project; parties the pipeline operator; status EIA's status in lower case
    x_*         EIA's columns, headings as names: the project type, completed date, year in service, states and regions
                (EIA's list, the first and last), cost in millions of dollars as EIA writes it (a range stays a range),
                miles, added capacity in million cubic feet a day, diameter in inches, pipeline type, authority, docket,
                whether it crosses a state border, notes, demand served, website and when EIA last updated the record;
                x_sheet current or historical

A row with no project name is read past. A project given twice under one id with two different rows has no key: both are
left out and named in the header (chain 030's rule); a row given twice the same is kept once. A heading the map does not
know stops the run.

    python warehouse/connectors/eia_gas_pipeline_projects.py [--offline]

Ceiling: two requests (the page and the workbook; both saved in warehouse/raw/eia_gas_pipeline_projects/ and reused
offline). EIA's robots file allows these paths. License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, natural gas pipeline projects").
"""

import argparse
import datetime as dt
import hashlib
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eia_gas_pipeline_projects"
CONNECTOR = "eia_gas_pipeline_projects"
SOURCE = "eia:naturalgas:pipeline_projects"
PAGE = "https://www.eia.gov/naturalgas/data.php"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = {"Last Updated Date": "x_last_updated", "Project Name": "name", "Pipeline Operator Name": "parties",
        "Project Type": "x_project_type", "Status": "status", "Completed Date": "x_completed_date",
        "Year In Service Date": "x_year_in_service", "State(s)": "x_states", "Beg_State": "x_beg_state", "End_State": "x_end_state",
        "Region(s)": "x_regions", "Beg_Region": "x_beg_region", "End_Region": "x_end_region", "Thru_Region": "x_thru_region",
        "Cost (millions)": "x_cost_million_usd", "Miles": "x_miles", "Additional Capacity": "x_capacity_mmcfd",
        "Pipeline Diameter": "x_diameter_inches", "Pipeline Type": "x_pipeline_type", "Authority": "x_authority",
        "Docket": "x_docket", "Crosses State Border": "x_crosses_state_border", "Notes": "x_notes", "Project Notes": "x_notes",
        "Demand Served": "x_demand_served", "Website": "x_website"}
X = ["x_project_name", "x_project_type", "x_completed_date", "x_year_in_service", "x_states", "x_beg_state", "x_end_state",
     "x_regions", "x_beg_region", "x_end_region", "x_thru_region", "x_cost_million_usd", "x_miles", "x_capacity_mmcfd",
     "x_diameter_inches", "x_pipeline_type", "x_authority", "x_docket", "x_crosses_state_border", "x_notes", "x_demand_served",
     "x_website", "x_last_updated", "x_sheet", "x_date_basis"]
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
              "source_url", "retrieved_at"]


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, (pd.Timestamp, dt.datetime)):                 # session 905: the cells come as datetime, not Timestamp
        return v.strftime("%Y-%m-%d")
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


def slug(v):
    return re.sub(r"[^a-z0-9]+", "_", v.lower()).strip("_")


def newest(page_html):
    """The newest workbook the page links: (url, its month and year as named)."""
    found = re.findall(r'href="(/naturalgas/pipelines/EIA-NaturalGasPipelineProjects_?([A-Z][a-z]{2})(\d{4})\.xlsx)"', page_html)
    if not found:
        raise RuntimeError("the page links no pipeline projects workbook")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    href, mon, year = max(found, key=lambda f: (int(f[2]), months.index(f[1])))
    return "https://www.eia.gov" + href, f"{mon} {year}"


def sheet_rows(frame, which, url, retrieved):
    heads = [r for r in range(min(5, len(frame))) if any(text(v) == "Project Name" for v in frame.iloc[r])]
    if not heads:
        raise RuntimeError(f"{which}: no heading row names 'Project Name'")
    hr = heads[0]
    cols = {}
    for c, v in enumerate(frame.iloc[hr]):
        h = text(v)
        if not h:
            continue
        key = next((k for k in COLS if h.startswith(k)), None)
        if key is None:
            raise RuntimeError(f"{which}: a heading not in the map: {h!r}")
        cols[COLS[key]] = c
    out = []
    for _, r in frame.iloc[hr + 1:].iterrows():
        x = {k: text(r[c]) for k, c in cols.items()}
        if not x.get("name"):
            continue
        year = x.get("x_year_in_service", "")
        done = x.get("x_completed_date", "")
        upd = x.get("x_last_updated", "")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", done):
            date, basis = done[:10], "completed"
        elif re.fullmatch(r"\d{4}", year):
            date, basis = f"{year}-01-01", "year_in_service"
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", upd):
            date, basis = upd[:10], "last_updated"                      # no date of its own: when EIA last updated it
        else:
            date, basis = "", ""
        out.append(dict(event_id=f"eia_gas_pipeline:{slug(x['name'])}:{slug(year) or 'none'}", event_date=date, event_type="pipeline_project",
                        parties=x.get("parties", ""), entity_ids="", mw="", price="", currency="",
                        status=x.get("status", "").lower(), source=SOURCE, source_url=url, retrieved_at=retrieved,
                        x_project_name=x["name"], x_sheet=which, x_date_basis=basis,
                        **{k: v for k, v in x.items() if k.startswith("x_")}))
    return pd.DataFrame(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's natural gas pipeline projects")
    ap.add_argument("--offline", action="store_true", help="the saved page and workbook only, no request")
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
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, headers=UA)
        url, edition = newest(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=300)
        xl = pd.ExcelFile(io.BytesIO(content))
        current = next((s for s in xl.sheet_names if s.strip() == "Natural Gas Pipeline Projects"), None)
        history = next((s for s in xl.sheet_names if s.startswith("Historical Projects")), None)
        if not current or not history:
            raise RuntimeError(f"the workbook's sheets are not as read: {xl.sheet_names}")
        t = pd.concat([sheet_rows(pd.read_excel(xl, current, header=None), "current", url, rec.get("retrieved_at") or ""),
                       sheet_rows(pd.read_excel(xl, history, header=None), "historical", url, rec.get("retrieved_at") or "")],
                      ignore_index=True).fillna("")
        t = t.drop_duplicates()
        twice = t["event_id"].duplicated(keep=False)
        gone = sorted(set(t.loc[twice, "event_id"]))
        t = t[~twice]
        undated = int((t["event_date"] == "").sum())
        t = t[t["event_date"] != ""]
        cols = EVENT_COLS + X
        t = t[cols].sort_values(["event_date", "event_id"]).reset_index(drop=True)
        header = [
            f"Energy Research Warehouse (ERW): EIA, natural gas pipeline projects, current and historical, the tracker of {edition} (session 899)",
            "Shape: events (docs/datastandard.md v0). event_id eia_gas_pipeline:<project name slug>:<year in service>; event_date the completed date where "
            "EIA gives one, else the year in service's 1 January, else when EIA last updated it (x_date_basis); event_type pipeline_project; parties the operator; status EIA's in lower case; x_* EIA's "
            "columns (cost in million USD as EIA writes it, a range kept; capacity in MMcf/d; diameter in inches); x_sheet current or historical.",
            f"{len(t):,} projects ({int((t.x_sheet == 'current').sum())} current, {int((t.x_sheet == 'historical').sum())} historical); event_date by "
            f"x_date_basis: {', '.join(f'{k} {v}' for k, v in t['x_date_basis'].value_counts().items())}. Nothing is filled."
            + (f" Projects with no date at all, left out: {undated}." if undated else "")
            + (f" Ids EIA gives twice with two rows, left out (no key): {', '.join(gone)}." if gone else ""),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_gas_pipeline_projects.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, natural gas pipeline projects, {PAGE}",
            f"  access: {url} (retrieved {rec.get('retrieved_at', '')})",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, natural gas pipeline projects").',
        ]
        ip.write_snapshot(t, NAME, header, log, cols=cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Natural gas pipeline projects", report_url=PAGE, document_list=PAGE,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t):,} projects"))
        print(f"{NAME}: {len(t):,} projects ({edition})")
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
