#!/usr/bin/env python3
"""ERCOT's Transmission Project and Information Tracking report (TPIT): every transmission project the transmission
owners report to ERCOT, future, planned, completed and cancelled (session 852, chain 046: transmission projects by
county for the All grids tab's ERCOT nodes).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/ercot_transmission_projects.csv, from the
TPIT workbook ERCOT links on its planning page (the public edition, without costs):

    page   https://www.ercot.com/gridinfo/planning
    file   the workbook titled "Transmission Project and Information Tracking" there (on 23 October 2026,
           https://www.ercot.com/files/docs/2022/03/02/ERCOT-July-Ad-Hoc-TPIT-No-Cost-071326-UPDATE.xlsx, updated
           17 July 2026, "future projects as of 7/13/2026")

    event_id    ercot_tpit:<ERCOT project number>:<phase number>, unique in the four project sheets
    event_date  the actual in-service date where ERCOT gives one, else the projected one (x_date_kind says which), as
                ERCOT gives it. ERCOT writes 9999-01-01 where a project has no actual date: it is not taken as a date
                (x_actual_in_service keeps ERCOT's cell)
    event_type  transmission_project
    parties     the transmission owner as ERCOT names it
    status      future, planned, completed or cancelled: the sheet the project is on (ERCOT's own status text in
                x_ercot_status)
    x_*         ERCOT's fields: title, description, the from and to locations, kV, new and upgraded circuit miles,
                autotransformer MVA, reactive Mvar, the counties of the start and the end, the planning tier, the RPG
                and RTP numbers, the projected and actual in-service dates, the comment

Left out on purpose: the "TSP/Company Contact" column and the owners' contact sheet (people's names, addresses and
telephone numbers), and the cost summary (this edition carries no cost by project). A text cell is written with ERCOT's
line breaks as spaces. ERCOT's robots file (read by session 850) allows /gridinfo/ and /files/docs/. Every run replaces
the table with the newest workbook (a snapshot).

    python warehouse/connectors/ercot_tpit.py [--offline]

Ceiling: two requests (the page and the workbook; a workbook saved in warehouse/raw/ercot_tpit/ is reused unless the page
names another). License: public (ERCOT, licenses.md #2; cite "ERCOT, Transmission Project and Information Tracking").
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

NAME = "ercot_transmission_projects"
CONNECTOR = "ercot_tpit"
SOURCE = "ercot:tpit"
PAGE = "https://www.ercot.com/gridinfo/planning"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SHEETS = {"Future": "future", "Planned": "planned", "Completed": "completed", "Cancelled": "cancelled"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
# ERCOT's heading (its start, lower case) -> the x field
FIELDS = [("ercot project number", "x_project_number"), ("phase number", "x_phase"), ("project title", "x_title"),
          ("project description", "x_description"), ("comments/reasons", "x_comment"), ('terminal "from"', "x_from"),
          ('terminal "to"', "x_to"), ("transmission status", "x_ercot_status"), ("transmission owner (text)", "x_owner"),
          ("projected in-service", "x_projected_in_service"), ("actual in-service", "x_actual_in_service"),
          ("service level kv", "x_kv"), ("trans circuit miles new", "x_new_circuit_miles"),
          ("trans circuit miles rebuilt", "x_upgraded_circuit_miles"), ("autotransformer capacity", "x_autotransformer_mva"),
          ("reactive capability", "x_reactive_mvar"), ("county location for substation", "x_county_start"),
          ("county location for ending", "x_county_end"), ("planning charter tier", "x_tier"), ("rpg number", "x_rpg_number"),
          ("rtp project number", "x_rtp_number")]
X_COLS = [x for _, x in FIELDS] + ["x_date_kind", "x_sheet"]
LEFT_OUT = ("tsp/company contact",)


def clean(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, (pd.Timestamp, dt.datetime)):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v).replace("_x000D_", " ")).strip()


def sheet_rows(frame, tab, url):
    """One project sheet, its title and heading rows included, as events."""
    heads = [r for r in range(min(6, len(frame))) if any(clean(v) == "ERCOT Project Number" for v in frame.iloc[r])]
    if not heads:
        raise RuntimeError(f"{tab}: no heading row names 'ERCOT Project Number'")
    hr = heads[0]
    names = [clean(v).lower() for v in frame.iloc[hr]]
    cols = {}
    for start, x in FIELDS:
        hit = [i for i, n in enumerate(names) if n.startswith(start)]
        if len(hit) != 1:
            raise RuntimeError(f"{tab}: the heading '{start}' is found {len(hit)} times")
        cols[x] = hit[0]
    out = []
    for _, r in frame.iloc[hr + 1:].iterrows():
        x = {k: clean(r.iloc[c]) for k, c in cols.items()}
        if not x["x_project_number"]:
            continue
        actual, projected = x["x_actual_in_service"], x["x_projected_in_service"]
        actual = "" if actual.startswith("9999") else actual          # ERCOT's mark for no date
        projected = "" if projected.startswith("9999") else projected
        date = actual or projected
        out.append(dict(event_id=f"ercot_tpit:{x['x_project_number']}:{x['x_phase'] or x['x_project_number']}",
                        event_date=date, event_type="transmission_project", parties=x["x_owner"], entity_ids="", mw="",
                        price="", currency="", status=SHEETS[tab], source=SOURCE, source_url=url,
                        x_date_kind="actual" if actual else ("projected" if projected else ""), x_sheet=tab, **x))
    return pd.DataFrame(out)


def workbook_url(page_html):
    m = re.findall(r'href="(https://www\.ercot\.com/files/docs/[^"]+\.xlsx)"\s+title="Transmission Project and Information Tracking"', page_html)
    if len(set(m)) != 1:
        raise RuntimeError(f"the page links {len(set(m))} workbooks titled 'Transmission Project and Information Tracking'")
    return m[0]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT's Transmission Project and Information Tracking report, every project")
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
        if ip.paused("ercot"):
            raise RuntimeError("ERCOT is paused (warehouse/metadata/paused_sources.csv): nothing is requested")
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA)
        url = workbook_url(page.decode("utf-8", errors="replace"))
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300)
        if content[:2] != b"PK":
            raise RuntimeError(f"{url} is not a workbook")
        xl = pd.ExcelFile(io.BytesIO(content))
        frames, title = [], ""
        for tab in SHEETS:
            names = [s for s in xl.sheet_names if s.startswith(tab) and "TPIT" in s]
            if len(names) != 1:
                raise RuntimeError(f"the workbook has {len(names)} sheets for {tab}: {xl.sheet_names}")
            f = pd.read_excel(xl, names[0], header=None)
            title = title or clean(f.iloc[0, 0])
            t = sheet_rows(f, tab, url)
            log(f"{names[0]}: {len(t):,} projects")
            frames.append(t)
        s = pd.concat(frames, ignore_index=True)
        # chain 030's rule: a row ERCOT repeats with every field the same is kept once and counted; two different rows
        # under one project and phase stop the run (on 23 October 2026: 5 repeated, all identical)
        repeated = int(s.duplicated().sum())
        s = s.drop_duplicates().reset_index(drop=True)
        if s["event_id"].duplicated().any():
            raise RuntimeError(f"an event_id is given twice: {s.loc[s['event_id'].duplicated(), 'event_id'].head(5).tolist()}")
        s = s[EVENT_COLS + X_COLS]
        counts = s["status"].value_counts().to_dict()
        header = [
            "Energy Research Warehouse (ERW): ERCOT, Transmission Project and Information Tracking (TPIT): every transmission project the owners report, future, planned, completed and cancelled (session 852)",
            "Shape: events (docs/datastandard.md v0). event_id ercot_tpit:<project>:<phase>; event_date the actual in-service date, else the projected one (x_date_kind; ERCOT's 9999-01-01 is no date); "
            "event_type transmission_project; parties the transmission owner; status the sheet (future, planned, completed, cancelled); x_* ERCOT's fields.",
            f"Workbook: {title}; {len(s):,} project phases ({', '.join(f'{k} {v:,}' for k, v in counts.items())}); {repeated} rows ERCOT gives twice, identical, kept once. The owners' contact names, addresses and telephone numbers are left out; this edition has no costs.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_tpit.py (the workbook retrieved {rec.get('retrieved_at', '')})",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Electric Reliability Council of Texas (ERCOT), Transmission Project and Information Tracking, {PAGE}",
            f"  access: {url}",
            'License: public (ERCOT, licenses.md #2; cite "ERCOT, Transmission Project and Information Tracking").',
        ]
        ip.write_snapshot(s, NAME, header, log, EVENT_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Electric Reliability Council of Texas (ERCOT)",
                                    report="Transmission Project and Information Tracking (TPIT)", report_url=PAGE, document_list=PAGE,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="ercot", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} project phases {counts}; {s['parties'].nunique()} owners")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="ercot", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
