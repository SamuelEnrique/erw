#!/usr/bin/env python3
"""The Bureau of Safety and Environmental Enforcement's offshore incidents: each incident reported on the Outer
Continental Shelf, with its date, operator, area, block, lease, structure, what happened (fire, explosion, loss of well
control, collision, lifting, gas release), the fatalities and injuries, and BSEE's summary (session 2177, chain 097).

Energy Research Warehouse (ERW) connector. One events table from BSEE's calendar-year workbooks "for public use",
linked from

    https://www.bsee.gov/stats-facts/offshore-incident-statistics

    bsee_offshore_incidents   event_id bsee_incident:<BSEE's serial number, or h and a hash of the incident's date, time,
               operator, area, block, lease and summary for the years whose workbooks give no serial>; event_date the incident's date; event_type
               offshore_incident; parties the operator as BSEE names it; entity_ids lease:<lease number> where BSEE gives
               one; mw, price, currency empty; status empty; x_year the workbook's calendar year; x_time (24-hour, as
               BSEE writes it); x_region; x_district; x_area; x_block; x_water_depth_ft; x_structure; x_structure_type;
               x_rig; x_fatalities and x_injuries (operator and contractor summed, every injury class); x_fire;
               x_explosion; x_loss_of_well_control (any of BSEE's four kinds); x_collision (major or minor); x_lifting
               (crane or other lifting device); x_gas_release (reportable H2S or shut-down gas release); x_summary BSEE's
               own words

Each workbook's incidents sheet must hold BSEE's header row (naming Date and Operator Name, and the columns read below); its last line holds BSEE's totals
(2018's has none, and is not checked), and every Y/N column's count of Y and every count column's sum must equal that
line, or the run stops. BSEE's notes under 2018's incidents, written in the date column, end the sheet. A serial number
given twice, a date that does not read, or a flag that is neither Y nor N stops the run. Blank lines are passed over.
Nothing is filled. The calendar years are those the page links from 2018 (2017's workbook holds its fourth quarter only, and the
fiscal-year files before it are in another form): neither is taken.

    python warehouse/connectors/bsee_incidents.py [--offline] [--out-dir DIR]

Ceiling: the page and one request a year, saved in warehouse/raw/bsee_incidents/; asked again unless --offline. BSEE's
robots file disallows its admin, search and user paths, not /sites/ or /stats-facts/. License: public (BSEE's workbooks
are marked "Public Access Level: Public"; a work of the Department of the Interior, read 159; see license_verdicts.csv).
"""

import argparse
import datetime as dt
import hashlib
import io
import os
import re
import sys
import traceback
import urllib.parse

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "bsee_incidents"
SOURCE = "bsee:offshore_incidents"
HOST = "www.bsee.gov"
PAGE = "https://www.bsee.gov/stats-facts/offshore-incident-statistics"
TABLE = "bsee_offshore_incidents"
FIRST = 2018  # the 2017 workbook holds its fourth quarter only
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
X_COLS = ["x_year", "x_time", "x_region", "x_district", "x_area", "x_block", "x_water_depth_ft", "x_structure", "x_structure_type", "x_rig",
          "x_fatalities", "x_injuries", "x_fire", "x_explosion", "x_loss_of_well_control", "x_collision", "x_lifting", "x_gas_release",
          "x_summary"]
FLAGS = {"x_fire": ["Fire"], "x_explosion": ["Explosion"],
         "x_loss_of_well_control": ["Loss of Well Control Underground", "Loss of Well Control Surface", "Loss of Well Control Diverter",
                                    "Loss of Well Control Equipment Failure"],
         "x_collision": ["Major Collision", "Minor Collision"], "x_lifting": ["Crane", "Other Lifting Device"],
         "x_gas_release": ["Reportable H2S Release", "Shut Down Gas Release"]}
FATAL = ["Operator Fatalities", "Contractor Fatalities"]
NEEDED = ["Date", "Time", "Operator Name", "OCS Region", "District Name", "Area Name", "Block", "Lease", "Water Depth (feet)",
          "Structure Name", "Structure Type", "Rig Name", "Incident Summary"] + [c for v in FLAGS.values() for c in v]


def year_links(page):
    out = {}
    for h in set(re.findall(r'href="([^"]+\.xlsx)"', page)):
        name = h.lower().rsplit("/", 1)[-1]
        m = re.match(r"cy-?(\d{4})", name)
        if m:
            y = int(m.group(1))
            if y in out:
                raise RuntimeError(f"two workbooks for {y}: {out[y]} and {h}")
            out[y] = urllib.parse.urljoin(PAGE, h)
    if not out:
        raise RuntimeError("the page links no calendar-year workbook")
    return out


def normal(h):
    """A column's name as the 2020 to 2024 workbooks write it (2018's carries descriptions in brackets)."""
    h = re.sub(r"\s+", " ", h).strip()
    m = re.match(r"Loss of Well Control \((Underground|Surface|Diverter|Equipment)", h)
    if m:
        return f"Loss of Well Control {m.group(1).replace('Equipment', 'Equipment Failure')}"
    for c in ("Major Collision", "Minor Collision"):
        if h.startswith(c + " ("):
            return c
    if h == "Redacted Incident Summary":  # 2020's workbook
        return "Incident Summary"
    return h


def text(x):
    return "" if x is None or (isinstance(x, float) and pd.isna(x)) else str(x).strip()


def count(x, where):
    s = text(x)
    if s == "":
        return 0
    if not re.fullmatch(r"\d+(\.0)?", s):
        raise RuntimeError(f"{where}: not a count: {x!r}")
    return int(float(s))


def flag(x, where):
    s = text(x).upper()
    if s not in ("Y", "N", ""):
        raise RuntimeError(f"{where}: a flag neither Y nor N: {x!r}")
    return s == "Y"


def parse(content, year, url):
    x = pd.ExcelFile(io.BytesIO(content))
    sheets = [s for s in x.sheet_names if "incident" in s.lower()]
    if len(sheets) != 1:
        raise RuntimeError(f"{year}: not one incidents sheet: {x.sheet_names}")
    v = pd.read_excel(x, sheets[0], header=None, dtype=object, keep_default_na=False)
    h = [i for i in range(min(len(v), 10)) if {"Date", "Operator Name"} <= {text(c) for c in v.iloc[i]}]
    if len(h) != 1:
        raise RuntimeError(f"{year}: no single header row naming Date and Operator Name")
    head = [normal(text(c)) for c in v.iloc[h[0]]]
    serial = head.index("SN_EV_MASTERS") if "SN_EV_MASTERS" in head else None  # 2018 to 2020's workbooks have no serial
    missing = [c for c in NEEDED if c not in head]
    inj = [c for c in head if "injur" in c.lower()]
    fatal = [c for c in head if "fatalit" in c.lower()]  # operator and contractor from 2020; one column in 2018
    if missing or not inj or not fatal:
        raise RuntimeError(f"{year}: columns not found: {missing or 'no injury or fatality columns'}")
    ix = {c: head.index(c) for c in NEEDED + inj + fatal}
    out, seen, total = [], set(), None
    for i in range(h[0] + 1, len(v)):
        r = v.iloc[i]
        d = r.iloc[ix["Date"]]
        if not text(d):
            if any(text(c) for c in r):
                total = r  # BSEE's totals line: no date, figures under the columns; what follows is BSEE's notes
                break
            continue
        if not isinstance(d, (dt.datetime, pd.Timestamp)):
            if isinstance(d, str) and not any(text(c) for k, c in enumerate(r) if k != ix["Date"]):
                break  # BSEE's notes, written in the date column under the incidents (2018's workbook)
            raise RuntimeError(f"{year} row {i}: a date that does not read: {d!r}")
        if serial is not None:
            sn = text(r.iloc[serial])
        else:  # no serial: a hash of the incident's own fields, stable while BSEE's file is
            key = "|".join(text(r.iloc[ix[c]]) for c in ("Date", "Time", "Operator Name", "Area Name", "Block", "Lease", "Incident Summary"))
            sn = "h" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
        where = f"{year} {sn}"
        if sn in seen:
            raise RuntimeError(f"{where}: given twice")
        seen.add(sn)
        lease = text(r.iloc[ix["Lease"]])
        row = {"event_id": f"bsee_incident:{sn}", "event_date": pd.Timestamp(d).strftime("%Y-%m-%d"), "event_type": "offshore_incident",
               "parties": text(r.iloc[ix["Operator Name"]]), "entity_ids": f"lease:{lease}" if lease else "", "mw": "", "price": "",
               "currency": "", "status": "", "source": SOURCE, "source_url": url, "x_year": str(year), "x_time": text(r.iloc[ix["Time"]]),
               "x_region": text(r.iloc[ix["OCS Region"]]), "x_district": text(r.iloc[ix["District Name"]]),
               "x_area": text(r.iloc[ix["Area Name"]]), "x_block": text(r.iloc[ix["Block"]]),
               "x_water_depth_ft": text(r.iloc[ix["Water Depth (feet)"]]), "x_structure": text(r.iloc[ix["Structure Name"]]),
               "x_structure_type": text(r.iloc[ix["Structure Type"]]), "x_rig": text(r.iloc[ix["Rig Name"]]),
               "x_fatalities": sum(count(r.iloc[ix[c]], f"{where} {c}") for c in fatal),
               "x_injuries": sum(count(r.iloc[ix[c]], f"{where} {c}") for c in inj),
               "x_summary": re.sub(r"\s+", " ", text(r.iloc[ix["Incident Summary"]]))}
        for k, cols in FLAGS.items():
            row[k] = "Y" if any(flag(r.iloc[ix[c]], f"{where} {c}") for c in cols) else "N"
        out.append(row)
    if total is None:
        return out, False  # 2018's workbook has no totals line
    for c in [c for cols in FLAGS.values() for c in cols]:
        got, want = sum(1 for i in range(h[0] + 1, len(v)) if text(v.iat[i, ix["Date"]]) and flag(v.iat[i, ix[c]], c)), total.iloc[ix[c]]
        if text(want) and count(want, f"{year} total {c}") != got:
            raise RuntimeError(f"{year} {c}: {got} incidents marked Y, BSEE's total is {want}")
    for c in fatal + inj:
        got = sum(count(v.iat[i, ix[c]], c) for i in range(h[0] + 1, len(v)) if text(v.iat[i, ix["Date"]]))
        want = total.iloc[ix[c]]
        if text(want) and count(want, f"{year} total {c}") != got:
            raise RuntimeError(f"{year} {c}: the incidents sum to {got}, BSEE's total is {want}")
    return out, True


def main(argv=None):
    ap = argparse.ArgumentParser(description="BSEE's offshore incidents, one row an incident")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        page, _ = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=1)
        links = year_links(page.decode("utf-8", errors="replace"))
        rows, years, unchecked = [], [], []
        for year in sorted(y for y in links if y >= FIRST):
            content, rec = ip.fetch_raw(CONNECTOR, links[year], log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=2)
            got, checked = parse(content, year, links[year])
            unchecked += [] if checked else [year]
            for r in got:
                r["retrieved_at"] = rec.get("retrieved_at") or ""
            log(f"  {year}: {len(got)} incidents")
            rows += got
            years.append(year)
        t = pd.DataFrame(rows)
        if t.event_id.duplicated().any():
            raise RuntimeError(f"an incident in two years: {t.event_id[t.event_id.duplicated()].iloc[0]}")
        cols = EVENT_COLS + X_COLS
        t = t[cols].sort_values(["event_date", "event_id"]).reset_index(drop=True)
        head = [
            f"Energy Research Warehouse (ERW): Bureau of Safety and Environmental Enforcement, offshore incidents for public use, calendar years "
            f"{', '.join(map(str, years))}: {len(t):,} incidents (session 2177)",
            "Shape: events (docs/datastandard.md v0). event_id bsee_incident:<serial>; event_date; event_type offshore_incident; parties the "
            "operator; entity_ids lease:<number>; x_year; x_time; x_region; x_district; x_area; x_block; x_water_depth_ft; x_structure; "
            "x_structure_type; x_rig; x_fatalities and x_injuries (operator and contractor, every injury class, summed); x_fire, x_explosion, "
            "x_loss_of_well_control, x_collision, x_lifting, x_gas_release (Y or N); x_summary (BSEE's words).",
            f"Checked as read: each year's Y counts and count sums equal BSEE's totals line, which is not kept (no totals line to check in "
            f"{', '.join(map(str, unchecked)) or 'none'}). Fatalities {int(t.x_fatalities.sum())}, "
            f"injuries {int(t.x_injuries.sum()):,}, fires {int((t.x_fire == 'Y').sum())}, losses of well control "
            f"{int((t.x_loss_of_well_control == 'Y').sum())}. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/bsee_incidents.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Bureau of Safety and Environmental Enforcement, Offshore Incident Statistics, {PAGE}",
            f"  access: the calendar-year workbooks the page links, {min(years)} to {max(years)}",
            "License: public (BSEE's workbooks: Public Access Level: Public; the Department of the Interior's notice, see license_verdicts.csv). "
            "Cite the Bureau of Safety and Environmental Enforcement.",
        ]
        ip.write_snapshot(t, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{TABLE}: {len(t):,} incidents, years {years}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of the Interior, Bureau of Safety and Environmental Enforcement (BSEE)",
                                    report="Offshore Incident Statistics: incidents for public use, by calendar year", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
