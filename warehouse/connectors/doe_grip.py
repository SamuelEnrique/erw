#!/usr/bin/env python3
"""DOE's Grid Resilience and Innovation Partnerships (GRIP) selections: each project selected in the program's first
two rounds, with its recipient, program, round, status, states and the federal and recipient cost shares (session 2050,
chain 059: the federal money for the grid).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/doe_grip_selections.csv, from the GRIP
Program Projects page of the Department of Energy's Office of Electricity (the program moved there from the Grid
Deployment Office; the page's old /gdo/ address answers at its /oe/ one):

    https://www.energy.gov/oe/grid-resilience-and-innovation-partnerships-grip-program-projects

The page's list of projects is a table its script draws from the page's own settings (drupal-settings-json,
datatableRows), so the rows are read from there, as DOE publishes them. The date of each round's announcement is read
from the three program pages (Grid Resilience Utility and Industry Grants, Smart Grid Grants, Grid Innovation Program),
each of which prints "First Funding Opportunity ... On <date>" and "Second Funding Opportunity ... On <date>".

    event_id     doe_grip:<round>:<12 hex of the SHA-1 of program|applicant|project>, stable while DOE keeps the names
    event_date   the round's announcement for the program, as its program page prints it
    event_type   grip_selection; parties the applicant or selectee; status DOE's (awarded, selected, withdrawn)
    x_*          the project's name, the program, the round, the federal and recipient cost shares in USD, the states
                 (postal codes and names, as DOE lists them)

Values as published; a blank stays blank; nothing is filled. A column not in the map, an amount not in DOE's form, a
round or program without its date, or a project given twice stops the run. The page says its content "reflects
information available as of December 2024".

    python warehouse/connectors/doe_grip.py [--offline] [--out-dir DIR]

Ceiling: four requests (the projects page and the three program pages, fresh each run unless --offline). energy.gov's
robots file disallows only Drupal's own paths and search. License: "Government information at DOE websites is in the
public domain" (DOE's web policies, read 54).
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "doe_grip_selections"
CONNECTOR = "doe_grip"
SOURCE = "doe:grip_selections"
PAGE = "https://www.energy.gov/oe/grid-resilience-and-innovation-partnerships-grip-program-projects"
PROGRAMS = {"Grid Resilience Utility and Industry Grants": "https://www.energy.gov/oe/grid-resilience-utility-and-industry-grants",
            "Smart Grid Grants": "https://www.energy.gov/oe/smart-grid-grants",
            "Grid Innovation Program": "https://www.energy.gov/oe/grid-innovation-program"}
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status",
              "source", "source_url", "retrieved_at"]
FIELDS = ["Applicant/Selectee", "Project", "Federal Cost Share", "Recipient Cost Share", "Status", "Round", "program",
          "Locations", "StateFull", "keywords"]
X_COLS = ["x_project", "x_program", "x_round", "x_federal_usd", "x_recipient_usd", "x_states", "x_state_names",
          "x_announced_on", "x_dates_from"]
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"


def text(v):
    return re.sub(r"\s+", " ", str(v or "")).strip()


def usd(v):
    s = text(v)
    if not s:
        return ""
    if not re.fullmatch(r"\$\d{1,3}(,\d{3})*(\.\d+)?", s):
        raise RuntimeError(f"an amount not in DOE's form: {s!r}")
    return f"{float(s[1:].replace(',', '')):.0f}"


def settings_rows(html):
    m = re.search(r'<script type="application/json" data-drupal-selector="drupal-settings-json">(.*?)</script>', html, re.S)
    if not m:
        raise RuntimeError("the page carries no settings")
    rows = json.loads(m.group(1)).get("datatableRows")
    if not rows:
        raise RuntimeError("the page's settings hold no list of projects")
    return rows


def round_dates(html, url):
    """{"First": "YYYY-MM-DD", "Second": ...} from a program page's funding opportunity paragraphs."""
    s = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.replace("&nbsp;", " ")))
    out = {}
    for rnd, date in re.findall(rf"(First|Second|Third) Funding Opportunity\s+On ((?:{MONTHS}) \d{{1,2}}, \d{{4}})", s):
        out.setdefault(rnd, dt.datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d"))
    if not out:
        raise RuntimeError(f"{url} prints no funding opportunity's date")
    return out


def build(rows, dates, url, retrieved):
    out, seen = [], set()
    for r in rows:
        unknown = [k for k in r if k not in FIELDS]
        if unknown:
            raise RuntimeError(f"a column not in the map: {unknown}")
        program, rnd = text(r.get("program")), text(r.get("Round"))
        if program not in dates or rnd not in dates[program]:
            raise RuntimeError(f"no announcement date for {rnd} round of {program!r}")
        applicant, project = text(r.get("Applicant/Selectee")), text(r.get("Project"))
        key = hashlib.sha1(f"{program}|{applicant}|{project}".encode("utf-8")).hexdigest()[:12]
        eid = f"doe_grip:{rnd.lower()}:{key}"
        if eid in seen:
            raise RuntimeError(f"a project given twice: {applicant} {project}")
        seen.add(eid)
        out.append({"event_id": eid, "event_date": dates[program][rnd], "event_type": "grip_selection", "parties": applicant,
                    "entity_ids": "", "mw": "", "price": "", "currency": "", "status": text(r.get("Status")).lower(),
                    "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "x_project": project, "x_program": program,
                    "x_round": rnd.lower(), "x_federal_usd": usd(r.get("Federal Cost Share")),
                    "x_recipient_usd": usd(r.get("Recipient Cost Share")),
                    "x_states": ";".join(x.strip() for x in text(r.get("Locations")).split(",") if x.strip()),
                    "x_state_names": text(r.get("StateFull")), "x_announced_on": dates[program][rnd],
                    "x_dates_from": PROGRAMS[program]})
    t = pd.DataFrame(out, columns=EVENT_COLS + X_COLS)
    return t.sort_values(["event_date", "x_program", "parties", "event_id"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="DOE's GRIP selections")
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
        page, rec = ip.fetch_raw(CONNECTOR, PAGE, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
        rows = settings_rows(page.decode("utf-8", errors="replace"))
        dates = {}
        for program, url in PROGRAMS.items():
            html, _ = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120)
            dates[program] = round_dates(html.decode("utf-8", errors="replace"), url)
        t = build(rows, dates, PAGE, rec.get("retrieved_at") or "")
        fed = pd.to_numeric(t.x_federal_usd, errors="coerce")
        by = t.groupby(["x_round", "x_program"]).size()
        header = [
            "Energy Research Warehouse (ERW): U.S. Department of Energy, Office of Electricity, Grid Resilience and Innovation Partnerships (GRIP) Program Projects: "
            "each project selected in the first two rounds (session 2050)",
            "Shape: events (docs/datastandard.md v0). event_id doe_grip:<round>:<12 hex of the SHA-1 of program|applicant|project>; event_date the round's announcement "
            "as the program's page prints it; event_type grip_selection; parties the applicant; status DOE's; x_federal_usd and x_recipient_usd the cost shares in USD.",
            f"{len(t)} projects, federal share USD {fed.sum():,.0f}: " + "; ".join(f"{r} round {p} {n}" for (r, p), n in by.items())
            + ". The page says its content reflects information available as of December 2024. Values as published; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/doe_grip.py; the projects page retrieved {rec.get('retrieved_at') or ''}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Department of Energy, Office of Electricity, GRIP Program Projects, {PAGE}",
            "  access: the page's drupal-settings-json (datatableRows); the round dates from " + ", ".join(PROGRAMS.values()),
            "License: public domain (DOE: \"Government information at DOE websites is in the public domain\").",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=EVENT_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Department of Energy (DOE)",
                                    report="Grid Resilience and Innovation Partnerships (GRIP) Program Projects (Office of Electricity)",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} projects"))
        print(f"{NAME}: {len(t)} projects, federal USD {fed.sum():,.0f}")
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
