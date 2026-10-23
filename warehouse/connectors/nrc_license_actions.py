#!/usr/bin/env python3
"""The NRC's renewed reactor licenses and approved power uprates (session 2064, chain 066: the licenses that keep the
reactors running and the uprates that add to them, which the ERW held only as the reactors' list and daily status).

Energy Research Warehouse (ERW) connector. One events table from two pages of www.nrc.gov:

    https://www.nrc.gov/reactors/operating/licensing/renewal/applications.html            completed renewals
    https://www.nrc.gov/reactors/operating/licensing/power-uprates/status-power-apps/approved-applications.html

    nrc_license_actions   event_id nrc:renewal:<plant slug>:<YYYYMMDD received> or nrc:uprate:<NRC's row number>;
                          event_date the renewed license's issue date, or the uprate's approval date; event_type
                          license_renewal (the page's completed initial renewals; the subsequent renewals, listed
                          only as links, are not taken) or power_uprate; parties NRC; status issued (renewals) or approved (uprates); x_plant the plant
                          and units as the NRC writes them; x_application_received (renewals); x_extended_operation
                          (as the NRC writes it, a date a unit); x_uprate_type MU (measurement uncertainty recapture),
                          S (stretch), E (extended) or E(1), as the NRC writes it; x_uprate_pct; x_uprate_mwt (MW
                          thermal, not electric: mw is left empty); x_accession (ADAMS); x_link the row's NRC page

The renewal page's planned, received and under-review tables are not taken (their dates are a quarter, not a day). The
uprate table's two total rows are not rows of the table; the page's "Total MWt" (24,089 when read) is not its rows'
sum (24,146.2), and the header says both. Footnote marks (*, **, ..., +++) are split from the cells and each row's
notes kept in x_note; a row with no issue date must have a note saying the application was withdrawn (status
withdrawn, event_date the date received), or the run stops. A date that does not read, a plant twice with the same received date, or a column not found stops
the run. Nothing is filled.

    python warehouse/connectors/nrc_license_actions.py [--offline] [--out-dir DIR]

Ceiling: two requests (the pages, saved in warehouse/raw/nrc_license_actions/). www.nrc.gov's robots file disallows
only its search and two files for every reader. License: public (the NRC's website is a U.S. Government Work, read 16).
"""

import argparse
import datetime as dt
import html
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "nrc_license_actions"
SOURCE = "nrc:license_renewals_uprates"
RENEWALS = "https://www.nrc.gov/reactors/operating/licensing/renewal/applications.html"
UPRATES = "https://www.nrc.gov/reactors/operating/licensing/power-uprates/status-power-apps/approved-applications.html"
TABLE = "nrc_license_actions"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
X_COLS = ["x_plant", "x_application_received", "x_extended_operation", "x_note", "x_uprate_type", "x_uprate_pct", "x_uprate_mwt", "x_accession",
          "x_link", "retrieved_at", "vintage"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")


def day(v, what):
    """The NRC's MM/DD/YY, or MM/DD/YYYY (Diablo Canyon's issue date is written so)."""
    v = str(v).strip()
    t = pd.to_datetime(v, format="%m/%d/%Y" if re.fullmatch(r"\d{2}/\d{2}/\d{4}", v) else "%m/%d/%y", errors="coerce")
    if pd.isna(t):
        raise RuntimeError(f"{what}: a date that does not read: {v!r}")
    return t.strftime("%Y-%m-%d")


MARK = re.compile(r"\s*(\*+|\+{3})\s*$")


def footnotes(text):
    """{mark: its note} from the renewal page's notes below the table (* Fort Calhoun Station was ..., +++ Pilgrim ...)."""
    s = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text)).replace(chr(160), " "))
    i = s.find("* Fort Calhoun")
    j = s.find("Industry Activities", i)
    if i < 0:
        raise RuntimeError("the renewal page's notes were not found")
    notes = {}
    for m in re.finditer(r"(\*+|\+{3})\s+(.+?)(?=\s(?:\*+|\+{3})\s|$)", s[i:j if j > 0 else None]):
        notes.setdefault(m.group(1), m.group(2).strip())
    return notes


def unmark(v):
    """(text without its footnote mark, the mark)."""
    v = re.sub(r"\s+", " ", str(v or "")).strip()
    m = MARK.search(v)
    return (v[:m.start()].strip(), m.group(1)) if m else (v, "")


def renewals(content, base):
    text = content.decode("utf-8", errors="replace")
    notes = footnotes(text)
    tables = pd.read_html(io.StringIO(text), extract_links="body")
    done = [d for d in tables if "Renewed License Issued" in d.columns]
    if len(done) != 1:
        raise RuntimeError(f"no single table with 'Renewed License Issued': {[list(d.columns) for d in tables]}")
    d = done[0]
    out, seen = [], set()
    for r in d.itertuples(index=False):
        (plant, m1), link = unmark(r[0][0]), r[0][1]
        received = day(r[1][0], plant)
        issued, m2 = unmark(r[2][0])
        extended, m3 = unmark(r[3][0] if r[3][0] is not None and str(r[3][0]) != "nan" else "")
        marks = [m for m in (m1, m2, m3) if m]
        for m in marks:
            if m not in notes:
                raise RuntimeError(f"{plant}: a mark with no note: {m!r}")
        withdrawn = issued == ""
        if withdrawn and not any("withdrawn" in notes[m] for m in marks):
            raise RuntimeError(f"{plant}: no issue date and no note saying the application was withdrawn")
        key = (slug(plant), received)
        if key in seen:
            raise RuntimeError(f"{plant}: received {received} given twice")
        seen.add(key)
        # session 2064: the completed table is the initial renewals; a row's link may point to the plant's later subsequent
        # renewal page (Cooper: renewed 2010, its link the subsequent application), so the link does not classify a row
        kind = "license_renewal"
        out.append(dict(base, event_id=f"nrc:renewal:{key[0]}:{received.replace('-', '')}", event_date=received if withdrawn else day(issued, plant),
                        event_type=kind, parties="NRC", entity_ids="", mw="", price="", currency="", status="withdrawn" if withdrawn else "issued",
                        x_plant=plant, x_application_received=received, x_extended_operation=extended,
                        x_note=" ".join(notes[m] for m in marks), x_uprate_type="", x_uprate_pct="", x_uprate_mwt="",
                        x_accession="", x_link=("https://www.nrc.gov" + link) if link and link.startswith("/") else (link or "")))
    return out


def uprates(content, base):
    tables = pd.read_html(io.StringIO(content.decode("utf-8", errors="replace")))
    hit = [d for d in tables if {"PLANT", "MWt", "DATE APPROVED", "TYPE"} <= set(d.columns)]
    if len(hit) != 1:
        raise RuntimeError(f"no single uprate table: {[list(d.columns) for d in tables]}")
    d = hit[0]
    total = d[d.PLANT.astype(str).str.strip() == "Total MWt"]
    rows = d[d["NO."].notna()]
    if len(total) != 1:
        raise RuntimeError("no 'Total MWt' row")
    s = rows.MWt.astype(float).sum()
    printed = float(total.MWt.iloc[0])  # session 2064: the page's total is not its rows' sum (24,089 against 24,146.2); both are said
    out = []
    for r in rows.itertuples(index=False):
        r = dict(zip(d.columns, r))
        n = int(r["NO."])
        out.append(dict(base, event_id=f"nrc:uprate:{n}", event_date=day(r["DATE APPROVED"], r["PLANT"]), event_type="power_uprate", parties="NRC",
                        entity_ids="", mw="", price="", currency="", status="approved", x_plant=str(r["PLANT"]).strip(), x_application_received="",
                        x_extended_operation="", x_note="", x_uprate_type=str(r["TYPE"]).strip(), x_uprate_pct=float(r["% UPRATE"]),
                        x_uprate_mwt=float(r["MWt"]), x_accession=str(r["ACCESSION #"]).strip(), x_link=""))
    return out, s, printed


def main(argv=None):
    ap = argparse.ArgumentParser(description="The NRC's renewed reactor licenses and approved power uprates")
    ap.add_argument("--offline", action="store_true", help="the saved pages only, no request")
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
        c1, r1 = ip.fetch_raw(CONNECTOR, RENEWALS, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=2)
        c2, r2 = ip.fetch_raw(CONNECTOR, UPRATES, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=2)
        b1 = dict(source=SOURCE, source_url=RENEWALS, retrieved_at=r1.get("retrieved_at") or "", vintage=ip.vintage_of(r1))
        b2 = dict(source=SOURCE, source_url=UPRATES, retrieved_at=r2.get("retrieved_at") or "", vintage=ip.vintage_of(r2))
        ren = renewals(c1, b1)
        up, mwt, printed = uprates(c2, b2)
        t = pd.DataFrame(ren + up)
        dup = t.event_id.duplicated(keep=False)
        if dup.any():
            raise RuntimeError(f"an event_id given twice: {t[dup].event_id.head(5).tolist()}")
        cols = EVENT_COLS + X_COLS
        t = t[cols].sort_values(["event_date", "event_id"]).reset_index(drop=True)
        by = t.event_type.value_counts().to_dict()
        head = [
            "Energy Research Warehouse (ERW): U.S. Nuclear Regulatory Commission, renewed reactor licenses and approved power uprates (session 2064)",
            "Shape: events (docs/datastandard.md v0). event_id nrc:renewal:<plant>:<received> or nrc:uprate:<NRC's number>; event_date the "
            "renewed license's issue date or the uprate's approval date; event_type license_renewal (initial renewals) or power_uprate; "
            "parties NRC; status issued or approved; x_plant as the NRC writes it; x_uprate_mwt in MW thermal (mw empty); x_uprate_type MU, S, E.",
            f"{len(t)} rows: {', '.join(f'{k} {v}' for k, v in sorted(by.items()))}; the uprates' rows add to {mwt:,.1f} MWt; the page prints a total of "
            f"{printed:,.1f} MWt. Crystal River 3's withdrawn application is a row, status withdrawn, dated its receipt. The "
            "planned and pending renewals are not taken. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nrc_license_actions.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Nuclear Regulatory Commission, Status of License Renewal Applications and Approved Applications for Power Uprates",
            f"  access: {RENEWALS}, {UPRATES}",
            "License: public (the NRC's website is a U.S. Government Work under federal copyright law, read 16).",
        ]
        ip.write_snapshot(t, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{TABLE}: {len(t)} rows; {by}; uprates {mwt:,.0f} MWt")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Nuclear Regulatory Commission (NRC)",
                                    report="Status of License Renewal Applications; Approved Applications for Power Uprates", report_url=RENEWALS,
                                    document_list=UPRATES, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
