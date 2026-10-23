#!/usr/bin/env python3
"""EIA's U.S. Liquefaction Capacity: each LNG export project's trains in operation, commissioning or construction, and
the large approved projects not yet built, with their capacity, authorizations and dockets (session 2021, chain 057: the
plants behind the LNG exports the ERW holds a month, which it did not hold).

Energy Research Warehouse (ERW) connector. One entities table from EIA's quarterly workbook:

    https://www.eia.gov/naturalgas/importsexports/liquefactioncapacity/U.S.liquefactioncapacity_<YEAR>_Q<N>.xlsx

    eia_lng_liquefaction_projects   entity_id eia_lng:<project>:<train> (a train or group of trains of the sheet
                                    "Existing & Under Construction") or eia_lng:<project> (a project of the sheet
                                    "Approved"), each slugged from EIA's words; entity_type project; name EIA's project
                                    name, with the train; geo US-<state>, or US offshore; status operating ("Commercial
                                    operation"), under_construction ("Under construction") or planned (an approved
                                    project), and empty for "Commissioning", which the standard's statuses do not name;
                                    status_date the in-service date where EIA gives a day; operator EIA's operator;
                                    capacity_mw empty (a gas plant's capacity is in x_ columns)
                                    x_sheet, x_train, x_status (EIA's words), x_in_service (as EIA writes it: a day, a
                                    year or a half year), x_commercial_operation_date, x_trains (approved projects),
                                    capacities in billion cubic feet a day and million tonnes a year: x_baseload_bcfd,
                                    x_baseload_mtpa, x_peak_bcfd, x_peak_mtpa (a train's nameplate; for an approved
                                    project its proposed design capacity, per train and in all), the authorized export
                                    quantities x_doe_fta_*, x_doe_nonfta_*, x_ferc_* with their dockets, x_project_type,
                                    x_marks (EIA's footnote marks beside a figure, "column:mark", the notes in the file)

Each sheet's header must name the columns read below where they are read, or the run stops. A figure EIA writes with a
footnote mark ("0.66B", "6.20^", "1.20+") is read as the number and its mark kept in x_marks; a cell "Note A" has no
figure and its mark is kept, as is "n/a" (not applicable); any other text in a figure's place stops the run. Names, train labels and statuses are kept
as EIA prints them, footnote letters included ("Train 1B", "Gulf LNGE", "Under constructionH"): no rule tells EIA's
letter from a name's own. An entity_id given twice stops the run. Nothing is filled.

    python warehouse/connectors/eia_lng_liquefaction.py [--offline] [--out-dir DIR] [--file U.S.liquefactioncapacity_2026_Q3.xlsx]

Ceiling: one request (the quarter's file; EIA's natural gas data page lists each quarter's file, and the next quarter's
is a new name, given with --file). EIA's robots file does not disallow /naturalgas/importsexports/. License: public (EIA,
read 1); EIA names FERC, DOE and the projects' sponsors as its sources.
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

CONNECTOR = "eia_lng_liquefaction"
SOURCE = "eia:us_liquefaction_capacity"
PAGE = "https://www.eia.gov/naturalgas/data.php"
BASE = "https://www.eia.gov/naturalgas/importsexports/liquefactioncapacity/"
FILE = "U.S.liquefactioncapacity_2026_Q3.xlsx"
TABLE = "eia_lng_liquefaction_projects"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source"]
FIGS = ["x_baseload_bcfd", "x_baseload_mtpa", "x_peak_bcfd", "x_peak_mtpa", "x_doe_fta_bcfd", "x_doe_fta_mtpa", "x_doe_nonfta_bcfd",
        "x_doe_nonfta_mtpa", "x_ferc_bcfd", "x_ferc_mtpa"]
EXTRA = (["x_sheet", "x_train", "x_status", "x_in_service", "x_commercial_operation_date", "x_trains"] + FIGS
         + ["x_doe_fta_docket", "x_doe_nonfta_docket", "x_ferc_docket", "x_project_type", "x_marks", "source_url", "retrieved_at", "vintage"])
STATES = {"AK", "AL", "FL", "GA", "LA", "MD", "MS", "OR", "TX", "WA"}
# sheet -> {column: (field, words its header must hold)}; the header is the sheet's two rows above the first project
SHEETS = {
    "Existing & Under Construction": {
        0: ("project", "Project name"), 1: ("x_train", "Train"), 2: ("x_baseload_bcfd", "Baseload"), 3: ("x_baseload_mtpa", "Mtpa"),
        4: ("x_peak_bcfd", "Peak"), 5: ("x_peak_mtpa", "Mtpa"), 7: ("x_status", "Project status"), 8: ("x_in_service", "In-service"),
        9: ("x_commercial_operation_date", "commercial"), 10: ("state", "Location"), 11: ("x_doe_fta_bcfd", "DOE-authorized"),
        12: ("x_doe_fta_mtpa", "Mtpa"), 13: ("x_doe_fta_docket", "FTA application docket"), 14: ("x_doe_nonfta_bcfd", "DOE-authorized"),
        15: ("x_doe_nonfta_mtpa", "Mtpa"), 16: ("x_doe_nonfta_docket", "non-FTA application docket"), 17: ("x_ferc_bcfd", "FERC-authorized"),
        18: ("x_ferc_mtpa", "Mtpa"), 19: ("x_ferc_docket", "FERC docket"), 20: ("x_project_type", "Project type"), 21: ("operator", "Operator")},
    "Approved": {
        0: ("project", "Project name"), 1: ("operator", "Project operator"), 2: ("x_baseload_bcfd", "capacity per t"), 3: ("x_baseload_mtpa", "Mtpa"),
        4: ("x_trains", "Number of trains"), 5: ("x_peak_bcfd", "Proposed design capacity"), 6: ("x_peak_mtpa", "Mtpa"),
        7: ("x_status", "Project status"), 8: ("state", "Location"), 9: ("x_doe_fta_bcfd", "DOE-authorized"), 10: ("x_doe_fta_mtpa", "Mtpa"),
        11: ("x_doe_fta_docket", "FTA application docket"), 12: ("x_doe_nonfta_bcfd", "DOE-authorized"), 13: ("x_doe_nonfta_mtpa", "Mtpa"),
        14: ("x_doe_nonfta_docket", "non-FTA application docket"), 15: ("x_ferc_bcfd", "FERC-authorized"), 16: ("x_ferc_mtpa", "Mtpa"),
        17: ("x_ferc_docket", "FERC docket"), 18: ("x_project_type", "Project type")},
}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, (dt.datetime, pd.Timestamp)):
        return pd.Timestamp(v).strftime("%Y-%m-%d")
    return re.sub(r"\s+", " ", str(v)).strip()


def figure(v, where):
    """(number or None, mark): EIA's figure with any footnote mark it carries split off."""
    if v is None or (isinstance(v, float) and pd.isna(v)) or text(v) == "":
        return None, ""
    if isinstance(v, (int, float)):
        return round(float(v), 6), ""
    s = text(v)
    if re.fullmatch(r"Note [A-Z]", s) or s.lower() == "n/a":  # "n/a": not applicable, as EIA writes it
        return None, s
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([A-Z^+]{1,2})", s)
    if not m:
        raise RuntimeError(f"{where}: not a figure: {s!r}")
    return float(m.group(1)), m.group(2)


def status_of(sheet, s):
    if sheet == "Approved":
        return "planned"
    if s.startswith("Commercial operation"):
        return "operating"
    if s.lower().startswith("under construction"):
        return "under_construction"
    if s.startswith("Commissioning"):
        return ""
    raise RuntimeError(f"a project status not in the map: {s!r}")


def parse(content, base):
    book = pd.read_excel(io.BytesIO(content), sheet_name=None, header=None, dtype=object, keep_default_na=False)
    out = []
    for sheet, cols in SHEETS.items():
        if sheet not in book:
            raise RuntimeError(f"no sheet {sheet!r}: sheets {list(book)}")
        v = book[sheet]
        hdr = [i for i in range(min(len(v), 8)) if text(v.iat[i, 0]) == "Project name"]
        if len(hdr) != 1:
            raise RuntimeError(f"{sheet}: no single 'Project name' header row")
        h = hdr[0]
        for j, (field, words) in cols.items():
            head = " ".join(text(v.iat[i, j]) for i in (h, h + 1) if j < v.shape[1])
            if words.lower() not in head.lower():
                raise RuntimeError(f"{sheet}: column {j} ({field}) should hold {words!r}; it reads {head!r}")
        for i in range(h + 2, len(v)):
            first = text(v.iat[i, 0])
            if first.startswith("Notes") or re.match(r"^\d+ Projects need", first):
                break
            if not first:
                continue
            r = {field: v.iat[i, j] for j, (field, _) in cols.items()}
            project = text(r["project"])
            train = text(r.get("x_train", ""))
            row = dict(base, entity_type="project", lat="", lon="", capacity_mw="", x_sheet=slug(sheet), x_train=train)
            marks = []
            for f in FIGS + (["x_trains"] if "x_trains" in r else []):
                if f not in r:
                    row[f] = ""
                    continue
                n, mark = figure(r[f], f"{sheet} {project} {train} {f}")
                row[f] = "" if n is None else (int(n) if f == "x_trains" else n)
                if mark:
                    marks.append(f"{f[2:]}:{mark}")
            row.setdefault("x_trains", "")
            for f in ("x_doe_fta_docket", "x_doe_nonfta_docket", "x_ferc_docket", "x_project_type", "operator"):
                row[f] = text(r[f])
            row["x_status"] = text(r["x_status"])
            row["status"] = status_of(sheet, row["x_status"])
            ins = r.get("x_in_service", "")
            row["x_in_service"] = text(ins)
            row["status_date"] = text(ins) if isinstance(ins, (dt.datetime, pd.Timestamp)) else ""
            cod = r.get("x_commercial_operation_date", "")
            if cod not in ("", None) and not isinstance(cod, (dt.datetime, pd.Timestamp)):
                raise RuntimeError(f"{sheet} {project} {train}: a commercial operation date that is not a date: {cod!r}")
            row["x_commercial_operation_date"] = text(cod)
            state = text(r["state"])
            row["geo"] = f"US-{state}" if state in STATES else ("US" if state.lower().startswith("offshore") else "")
            if not row["geo"]:
                raise RuntimeError(f"{sheet} {project}: a location not in the map: {state!r}")
            row["name"] = f"{project}, {train}" if train else project
            row["entity_id"] = f"eia_lng:{slug(project)}" + (f":{slug(train)}" if train else "")
            row["x_marks"] = "; ".join(marks)
            out.append(row)
    ids = pd.Series([r["entity_id"] for r in out])
    if ids.duplicated().any():
        raise RuntimeError(f"an entity_id given twice: {ids[ids.duplicated()].tolist()}")
    if not out:
        raise RuntimeError("no project")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's U.S. liquefaction capacity: LNG export projects and their trains")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--file", default=FILE)
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
        url = BASE + args.file
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120, pause=1)
        base = dict(source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = pd.DataFrame(parse(content, base))
        cols = ENTITY_COLS + EXTRA
        t = t[cols].sort_values("entity_id").reset_index(drop=True)
        n_st = t.status.replace("", "commissioning").value_counts().to_dict()
        head = [
            "Energy Research Warehouse (ERW): EIA, U.S. Liquefaction Capacity: LNG export projects' trains in operation, commissioning and "
            f"construction, and the large approved projects, {args.file} (session 2021)",
            "Shape: entities (docs/datastandard.md v0). entity_id eia_lng:<project>:<train> or eia_lng:<project> (approved); entity_type project; "
            "status operating, under_construction, planned (approved), or empty for EIA's Commissioning; status_date the in-service day where EIA "
            "gives one; capacity_mw empty. Capacities and authorized quantities in the x_ columns, bcfd (billion cubic feet a day) and mtpa (million "
            "tonnes a year) as EIA gives them; x_marks EIA's footnote marks beside a figure (its notes are in the file).",
            f"{len(t)} rows: {', '.join(f'{k} {v}' for k, v in sorted(n_st.items()))}. Names, trains and statuses as EIA prints them, its footnote "
            "letters included. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_lng_liquefaction.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, U.S. Liquefaction Capacity (quarterly), listed on {PAGE}",
            f"  access: {url}",
            "License: public (EIA: U.S. government publications are in the public domain); EIA names FERC, DOE and the projects' sponsors as its sources.",
        ]
        ip.write_snapshot(t, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{TABLE}: {len(t)} rows; {n_st}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="U.S. Liquefaction Capacity: LNG export projects, trains and approvals (quarterly)", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
