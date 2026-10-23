#!/usr/bin/env python3
"""The Department of Energy's electric emergency incident and disturbance reports (Form DOE-417, formerly OE-417): each
event a utility or grid operator reported, with its start and restoration, the area, the NERC region, the event type,
the demand lost and the customers affected (session 2028, chain 058: the grid's disturbances, which the ERW held only
as reliability indices by utility).

Energy Research Warehouse (ERW) connector. One events table from the yearly summaries DOE's Office of Cybersecurity,
Energy Security, and Emergency Response publishes on the DOE-417 site (built by Pacific Northwest National Laboratory;
the old host, www.oe.netl.doe.gov, no longer answers):

    https://doe417.pnnl.gov/                                   the form's site; "Annual Summaries Archives"
    https://doe417.pnnl.gov/summaries/<year>_Annual_Summary.xlsx   2024 on
    https://doe417.pnnl.gov/summaries/<year>_Annual_Summary.xls    2001 to 2023 (the site's own rule)

    doe_oe417_events   event_id doe417:<year>-<row in the year's summary>; event_date the day the event began; event_type
                       the first event type the summary lists, lower case with underscores (x_event_types all it
                       lists, x_event_type_as_published its words); parties empty; entity_ids empty; mw the demand lost in MW where the summary gives a
                       number; status restored where a restoration day is given, else empty; x_ the begin and
                       restoration day and time as printed (local, the summaries name no zone), the area affected, the
                       NERC region, the alert criteria and the customers affected as printed

A summary's header row is found by its column names (Date Event Began, Area Affected, Event Type and the rest), never by
position; a summary without those columns, or a begin date not a date, stops the run. A figure the summary gives as
"Unknown" or a range stays as printed in its x_ column, and mw is then empty. Nothing is filled.

    python warehouse/connectors/doe_oe417.py [--offline] [--out-dir DIR] [--years 2016-2025]

Ceiling: one request a year (ten for the default years), saved in warehouse/raw/doe_oe417/ and reused offline.
doe417.pnnl.gov has no robots file (its address answers with the site's page). License: public (DOE, read 54 of
license_reads.csv: "Government information at DOE websites is in the public domain").
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

CONNECTOR = "doe_oe417"
SOURCE = "doe:oe417"
HOST = "https://doe417.pnnl.gov"
TABLE = "doe_oe417_events"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEARS = (2016, 2025)
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status",
              "source", "source_url"]
X_COLS = ["x_year", "x_row", "x_begin_date", "x_begin_time", "x_restoration_date", "x_restoration_time", "x_area_affected",
          "x_nerc_region", "x_alert_criteria", "x_event_types", "x_event_type_as_published", "x_demand_loss_mw_as_published",
          "x_customers_affected_as_published", "x_customers_affected", "retrieved_at", "vintage"]
# the columns taken, by the words of their header (lower case, spaces collapsed); the first found wins
WANT = {
    "begin_date": ["date event began", "event date", "date began"],
    "begin_time": ["time event began", "time began"],
    "restoration_date": ["date of restoration", "date restored", "restoration date"],
    "restoration_time": ["time of restoration", "time restored", "restoration time"],
    "area": ["area affected", "area"],
    "nerc": ["nerc region"],
    "criteria": ["alert criteria"],
    "event_type": ["event type"],
    "demand_loss": ["demand loss (mw)", "demand loss"],
    "customers": ["number of customers affected", "customers affected"],
}
NEEDED = ["begin_date", "area", "event_type", "demand_loss", "customers"]


def url_of(year):
    return f"{HOST}/summaries/{year}_Annual_Summary.{'xlsx' if year >= 2024 else 'xls'}"


def words(v):
    return re.sub(r"\s+", " ", str(v)).strip().lower() if v is not None and not (isinstance(v, float) and pd.isna(v)) else ""


def find_header(raw):
    """(header row index, {field: column index}) of the first row naming every NEEDED field, else None."""
    for i in range(min(len(raw), 40)):
        names = [words(v) for v in raw.iloc[i].tolist()]
        got = {}
        for field, alts in WANT.items():
            for a in alts:
                if a in names:
                    got[field] = names.index(a)
                    break
        if all(f in got for f in NEEDED):
            return i, got
    return None


def as_day(v, what):
    """A summary's date cell (a datetime, an Excel serial, or text M/D/YYYY) as YYYY-MM-DD; empty stays empty."""
    if v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip() == "":
        return ""
    if isinstance(v, (dt.datetime, dt.date, pd.Timestamp)):
        return pd.Timestamp(v).strftime("%Y-%m-%d")
    if isinstance(v, (int, float)):
        return (pd.Timestamp("1899-12-30") + pd.Timedelta(days=float(v))).strftime("%Y-%m-%d")
    s = str(v).strip()
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})( 00:00:00)?", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    raise ValueError(f"{what}: not a date: {s!r}")


def as_time(v):
    """A time cell as printed: a datetime.time or a fraction of a day as HH:MM, text kept."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, dt.time):
        return v.strftime("%H:%M")
    if isinstance(v, (dt.datetime, pd.Timestamp)):
        return pd.Timestamp(v).strftime("%H:%M")
    if isinstance(v, float) and 0 <= v < 1:
        mins = int(round(v * 1440))
        return f"{mins // 60:02d}:{mins % 60:02d}"
    return re.sub(r"\s+", " ", str(v)).strip()


def as_text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return re.sub(r"\s+", " ", str(v)).strip()


def number(s):
    """A figure printed as a plain number (commas allowed) as text, else empty: 'Unknown', ranges and words stay out."""
    t = s.replace(",", "").strip()
    return t if re.fullmatch(r"\d+(\.\d+)?", t) else ""


def type_key(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


FORM_LABEL = "additional_information_comments_limit_250_characters"


def types_of(s):
    """The event types a summary cell lists, keyed, in its order: 2023's cells list them as "- A" lines joined by a
    no-break space, 2024's on by "; ". The form's label for its comment box ("Additional Information/Comments (limit
    250 characters):"), which the summaries print among the types without the comment, is not a type and is left out."""
    parts = re.split("[;" + chr(0xA0) + chr(10) + "]+", s)
    keys = [type_key(re.sub(r"^\s*-\s*", "", p).strip().rstrip(".:")) for p in parts]
    return [k for k in dict.fromkeys(keys) if k and k != FORM_LABEL]


def maybe_day(v, what):
    """A restoration cell: a day where it is one, else empty (the words it prints, Unknown or Ongoing, kept apart)."""
    s = as_text(v)
    if s == "" or not re.search(r"\d", s):
        return ""
    return as_day(v, what)


END_RE = re.compile(r"end of report\W+(\d[\d,]*) total incident\(s\) for (\d{4})", re.I)


def read_year(content, year):
    """(rows, printed total or None, rows left out for want of a begin day) of one year's summary: every sheet whose
    header names the needed fields, in sheet and row order. A row with no begin day (2023's August block prints none,
    in the workbook and in the PDF beside it) is left out and counted, never given a day. A total the summary prints
    ("End of report - 622 total incident(s) for 2024") that is not the rows read plus those left out stops the run."""
    engine = "openpyxl" if year >= 2024 else "xlrd"
    sheets = pd.read_excel(io.BytesIO(content), sheet_name=None, header=None, engine=engine, dtype=object)
    rows, found, printed, no_day = [], 0, None, 0
    for sname, raw in sheets.items():
        h = find_header(raw)
        if h is None:
            continue
        found += 1
        i, col = h
        for j in range(i + 1, len(raw)):
            r = raw.iloc[j].tolist()
            g = (lambda f: r[col[f]] if f in col else None)
            first = " ".join(as_text(v) for v in r if as_text(v))
            m = END_RE.search(first)
            if m:
                if int(m.group(2)) != year:
                    raise RuntimeError(f"{year}: the summary's total names {m.group(2)}")
                printed = int(m.group(1).replace(",", ""))
                continue
            area, etype, begin = as_text(g("area")), as_text(g("event_type")), as_text(g("begin_date"))
            if begin == "" and area == "" and etype == "":
                continue  # a blank line
            if begin != "" and not re.search(r"\d", begin):
                raise RuntimeError(f"{year} {sname} row {j + 1}: a begin date not a date: {begin!r}")
            if begin == "":
                no_day += 1
                continue
            where = f"{year} {sname} row {j + 1}"
            rows.append(dict(n=len(rows) + no_day + 1, begin=as_day(g("begin_date"), where), begin_time=as_time(g("begin_time")),
                             rest=maybe_day(g("restoration_date"), where), rest_raw=as_text(g("restoration_date")),
                             rest_time=as_time(g("restoration_time")), area=area, nerc=as_text(g("nerc")),
                             criteria=as_text(g("criteria")), etype=etype, loss=as_text(g("demand_loss")),
                             customers=as_text(g("customers"))))
    if not found:
        raise RuntimeError(f"{year}: no sheet with the columns {NEEDED}")
    if not rows:
        raise RuntimeError(f"{year}: a header but no row")
    if printed is not None and printed != len(rows) + no_day:
        raise RuntimeError(f"{year}: the summary prints {printed} incidents, {len(rows) + no_day} rows read")
    return rows, printed, no_day


def build(per_year, base_of):
    out = []
    for year, rows in per_year:
        for r in rows:
            n = r["n"]  # the incident's place in the year's summary, rows left out counted, so an id never shifts
            types = types_of(r["etype"])
            out.append(dict(
                event_id=f"doe417:{year}-{n:04d}", event_date=r["begin"], event_type=types[0] if types else "not_given", parties="",
                entity_ids="", mw=number(r["loss"]), price="", currency="", status="restored" if r["rest"] else "",
                x_year=str(year), x_row=str(n), x_begin_date=r["begin"], x_begin_time=r["begin_time"],
                x_restoration_date=r["rest"] or r["rest_raw"], x_restoration_time=r["rest_time"], x_area_affected=r["area"],
                x_nerc_region=r["nerc"], x_alert_criteria=r["criteria"], x_event_types="; ".join(types), x_event_type_as_published=r["etype"],
                x_demand_loss_mw_as_published=r["loss"], x_customers_affected_as_published=r["customers"],
                x_customers_affected=number(r["customers"]), **base_of(year)))
    return pd.DataFrame(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="DOE's electric emergency incident and disturbance reports (DOE-417), the yearly summaries")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--years", default=f"{YEARS[0]}-{YEARS[1]}", help="first-last year (default %(default)s)")
    args = ap.parse_args(argv)
    y0, y1 = (int(x) for x in args.years.split("-"))
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
        per_year, recs, printed, left_out = [], {}, {}, {}
        for year in range(y0, y1 + 1):
            content, rec = ip.fetch_raw(CONNECTOR, url_of(year), log, offline=args.offline, headers=UA, timeout=120, pause=1)
            recs[year] = rec
            rows, printed[year], left_out[year] = read_year(content, year)
            per_year.append((year, rows))
            log(f"  {year}: {len(rows)} events, {left_out[year]} left out (no begin day), the summary's total {printed[year]}")

        def base_of(year):
            rec = recs[year]
            return dict(source=SOURCE, source_url=url_of(year), retrieved_at=ip.utc_iso(pd.Timestamp(rec["retrieved_at"]))
                        if rec.get("retrieved_at") is not None else "", vintage=ip.vintage_of(rec))
        e = build(per_year, base_of)
        cols = EVENT_COLS + X_COLS
        e = e[cols].sort_values("event_id").reset_index(drop=True)
        counts = ", ".join(f"{y} {len(r)}" for y, r in per_year)
        with_mw = int((e.mw != "").sum())
        gaps = "; ".join(f"{y}: {k} incidents left out, the summary printing no begin day for them" for y, k in left_out.items() if k) or "none left out"
        totals = ", ".join(f"{y} {p}" for y, p in printed.items() if p is not None)
        head = [
            "Energy Research Warehouse (ERW): U.S. Department of Energy, Office of Cybersecurity, Energy Security, and Emergency Response, "
            f"Electric Emergency Incident and Disturbance Reports (Form DOE-417, formerly OE-417), the yearly summaries {y0} to {y1}: each reported "
            "event's start, restoration, area, NERC region, alert criteria, event type, demand lost and customers affected (session 2028)",
            "Shape: events (docs/datastandard.md v0). event_id doe417:<year>-<row in the year's summary>; event_date the day the event began; "
            "event_type the first event type the summary lists, lower case with underscores (x_event_types all it lists, in its order, without the "
            "form's label for its comment box; x_event_type_as_published its words); mw the demand lost in MW "
            "where the summary prints a number; status restored where a restoration day is printed; x_ the summary's fields as printed (days and "
            "times local, the summaries name no zone).",
            f"Events by year: {counts}; {len(e)} in all, {with_mw} with a demand loss in MW. A figure printed as Unknown or a range stays in its "
            "x_ column and mw is empty. Nothing is filled. A row is a report: DOE's summaries can list one event under several reports.",
            f"Rows left out: {gaps}. The totals the summaries print (rows read plus rows left out, checked): {totals or 'none printed'}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/doe_oe417.py; per row, retrieved_at and vintage (the file's Last-Modified)",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Department of Energy, DOE-417 Annual Summaries, {HOST}/",
            f"  access: {url_of(y0)} to {url_of(y1)} (the .xls files to 2023, .xlsx from 2024, as the site builds them)",
            'License: public (DOE: "Government information at DOE websites is in the public domain"; cite "U.S. Department of Energy, Form DOE-417").',
        ]
        ip.write_snapshot(e, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(e)} rows"))
        print(f"{TABLE}: {len(e)} events ({counts}); {with_mw} with MW")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of Energy (DOE)",
                                    report="Office of Cybersecurity, Energy Security, and Emergency Response (CESER), Electric Emergency Incident and Disturbance Reports (Form DOE-417): Annual Summaries", report_url=HOST + "/",
                                    document_list=HOST + "/summaries/", license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
