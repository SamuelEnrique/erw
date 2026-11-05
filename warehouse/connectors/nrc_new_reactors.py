#!/usr/bin/env python3
"""The Nuclear Regulatory Commission's new reactor work: the advanced reactor applications under review, each with its
applicant, kind, place, design, power and milestones, and the applicants and vendors in pre-application engagement
(session 2001, chain 056).

Energy Research Warehouse (ERW) connector. Two tables from the NRC's public pages:

    https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/advanced-reactor-application-projects
        and each project's page linked there
    https://www.nrc.gov/facilities-safety/new-reactors/advanced-reactors/who-were-working-with/pre-application-activities

    nrc_new_reactor_applications    events, one row an application under review: event_id nrc_app:<the page's name>;
                                    event_date the application's submittal ("When:", or "Application Tendered" where the
                                    page gives no "When:"); event_type the kind (construction_permit_application,
                                    early_site_permit_application, limited_work_authorization_application,
                                    operating_license_application, combined_license_application, other); parties the
                                    applicant ("Who:"); mw the electric power the page states ("NNN MWe"), else empty;
                                    status the latest milestone the page marks done ("A"); x_ the project's title, place,
                                    state, what the NRC says it is, reactor type, power level and fuel as written, the
                                    latest milestone's date, the next one with its target, and the decision's target
    nrc_advanced_reactor_preapplicants  entities, one row an applicant or vendor the pre-application table lists:
                                    entity_id nrc_preapp:<the page's name>; entity_type company; name as the table writes it;
                                    x_technology the table's column; x_microreactor (the table's "*"); x_active (no, for
                                    the table's "Inactive Projects")

The pages carry no docket numbers; none is made. A heading not as read, a table not found, a date not read, or an id
given twice stops the run; a field the page leaves out stays blank; nothing is filled.

    python warehouse/connectors/nrc_new_reactors.py [--offline] [--out-dir DIR]

Ceiling: eight requests (the two lists and the application pages they link, six on 23 October 2026), saved in
warehouse/raw/nrc_new_reactors/ and reused offline. nrc.gov's robots file disallows only its search pages, ads.txt and
autodiscover for every reader. License: public (NRC, read 16 of license_reads.csv: "a U.S. Government Work ... not
subject to copyright").
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "nrc_new_reactors"
SOURCE = "nrc:new_reactors"
HOST = "https://www.nrc.gov"
WHO = HOST + "/facilities-safety/new-reactors/advanced-reactors/who-were-working-with"
APPS = WHO + "/advanced-reactor-application-projects"
PRE = WHO + "/pre-application-activities"
APP_TABLE, PRE_TABLE = "nrc_new_reactor_applications", "nrc_advanced_reactor_preapplicants"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
MAX_PAGES = 12
DASH = chr(0x2014)  # the milestone tables set a step's description after this dash
APP_X = ["x_project", "x_when", "x_place", "x_state", "x_what", "x_reactor_type", "x_power_level", "x_fuel", "x_status_date",
         "x_next_milestone", "x_next_target", "x_decision", "x_decision_target", "x_page"]
PRE_X = ["x_technology", "x_microreactor", "x_active", "x_page"]
TECHNOLOGIES = ["High Temperature Gas Reactors", "Light Water Reactors", "Molten Salt Reactors / Molten Chloride Fast Reactors",
                "Liquid Metal Cooled Reactors", "Other Designs/ Not Specified"]
KINDS = [  # (pattern in "What:" or the title, event_type), first match wins
    (r"limited work authori[sz]ation", "limited_work_authorization_application"),
    (r"early site permit|\bESP\b", "early_site_permit_application"),
    (r"construction permit|\bCPA?\b", "construction_permit_application"),
    (r"combined licen[cs]e|\bCOL\b", "combined_license_application"),
    (r"operating licen[cs]e|\bOLA?\b", "operating_license_application"),
]
STATES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
    "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
    "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI",
    "Wyoming": "WY", "N.C.": "NC", "Tenn.": "TN", "Tex.": "TX",
}
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September",
                                      "October", "November", "December"], start=1)}


def text(node):
    return re.sub(r"\s+", " ", node.get_text(" ") if hasattr(node, "get_text") else str(node or "")).replace("\xa0", " ").strip()


def day(s):
    """A date as the NRC writes it: 03/31/2025, 09/26/25, March 31, 2025, or a month and year (the first of the month)."""
    s = s.strip()
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2,4})\b", s)
    if m:
        y = int(m.group(3))
        y = y + 2000 if y < 100 else y
        return f"{y:04d}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    m = re.match(r"([A-Z][a-z]+)\.? (\d{1,2}), (\d{4})\b", s)
    if m and m.group(1) in MONTHS:
        return f"{m.group(3)}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}"
    m = re.match(r"([A-Z][a-z]+) (\d{4})\b", s)
    if m and m.group(1) in MONTHS:
        return f"{m.group(2)}-{MONTHS[m.group(1)]:02d}-01"
    return ""


def main_part(html):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    if main is None:
        raise RuntimeError("no <main> in the page")
    return main


def project_links(html):
    main = main_part(html)
    out = []
    for a in main.find_all("a", href=True):
        h = a["href"].split("#")[0].rstrip("/")
        if "/advanced-reactor-application-projects/" in h and h not in out:
            out.append(h)
    if not out:
        raise RuntimeError("no application project linked from the list")
    if len(out) > MAX_PAGES:
        raise RuntimeError(f"{len(out)} application projects, more than the ceiling allows; raise it on purpose")
    return [h if h.startswith("http") else HOST + h for h in out]


def application(html, url, base):
    main = main_part(html)
    soup_title = BeautifulSoup(html, "html.parser").title
    title = re.sub(r"\s*\|\s*Nuclear Regulatory Commission\s*$", "", text(soup_title)) if soup_title else ""  # the page's <title>
    fields = {}
    for tr in main.find_all("tr"):
        tds = tr.find_all(["td", "th"], recursive=False)
        if len(tds) == 2:
            k = text(tds[0]).rstrip(":").strip()
            if k and k not in fields:
                fields[k] = tds[1]
    who, what, when, where = (text(fields[k]) if k in fields else "" for k in ("Who", "What", "When", "Where"))
    if not who:
        raise RuntimeError(f"{url}: no 'Who:' row")
    # the milestones: the table whose heading is "Milestones"
    rows, ms = [], None
    for table in main.find_all("table"):
        th = table.find("th")
        if th is not None and text(th) == "Milestones":
            ms = table
            break
    if ms is not None:
        for tr in ms.find_all("tr")[1:]:
            tds = tr.find_all("td")
            if len(tds) == 2:
                name = re.split(r"\s+" + DASH + r"\s+", text(tds[0]))[0].strip("* ")
                val = text(tds[1])
                mark = "A" if re.search(r"\bA\s*$", val) else ("T" if re.search(r"\bT\s*$", val) else "")
                rows.append((name, day(val), mark, val))
    tendered = [d for n, d, _, _ in rows if n.lower().startswith("application tendered") and d]
    # "March 31, 2025 (date of application submittal)", or "Application submitted December 30, 2025; ...": the first date written
    found = re.search(r"\d{1,2}/\d{1,2}/\d{2,4}|[A-Z][a-z]+\.? \d{1,2}, \d{4}", when)
    if found is None:  # "April 2025 to present (date of application submittal)": the month's first day, x_when as written
        found = re.search(r"(?:" + "|".join(MONTHS) + r") \d{4}", when)
    date = day(found.group(0)) if found else ""
    date = date or (tendered[0] if tendered else "")
    if not date:
        raise RuntimeError(f"{url}: no date of submittal read ('When:' {when!r})")
    kind = next((k for p, k in KINDS if re.search(p, what, re.I)), "") or next((k for p, k in KINDS if re.search(p, title, re.I)), "other")
    done = [(n, d) for n, d, mark, _ in rows if mark == "A" or (n.lower().startswith("application tendered") and d)]
    nxt = [(n, v) for n, d, mark, v in rows if mark == "T" or (not d and v.upper().startswith("TBD"))]
    decision = [(n, v) for n, d, mark, v in rows if re.search(r"decision|issuance|issued permit|licen[cs]e issued", n, re.I) and "Docketing" not in n]
    chars = {text(tr.find_all("td")[0]): text(tr.find_all("td")[1]) for tr in main.find_all("tr") if len(tr.find_all("td")) == 2}
    power = chars.get("Power Level", "")
    mwe = re.findall(r"([\d,.]+)\s*MWe\b", power)
    state = next((v for k, v in STATES.items() if re.search(r"(^|[ ,])" + re.escape(k) + r"($|[ ,.])", where)), "")
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    return dict(
        event_id=f"nrc_app:{slug}", event_date=date, event_type=kind, parties=who, entity_ids="",
        mw=mwe[-1].replace(",", "") if mwe else "", price="", currency="", status=done[-1][0] if done else "",
        source=base["source"], source_url=url, retrieved_at=base["retrieved_at"], vintage=base["vintage"],
        x_project=title, x_when=when, x_place=where, x_state=state, x_what=what, x_reactor_type=chars.get("Reactor Type", ""),
        x_power_level=power, x_fuel=chars.get("Fuel", ""), x_status_date=done[-1][1] if done else "",
        x_next_milestone=nxt[0][0] if nxt else "", x_next_target=nxt[0][1] if nxt else "",
        x_decision=decision[-1][0] if decision else "", x_decision_target=decision[-1][1] if decision else "", x_page=url)


def preapplicants(html, base, url):
    main = main_part(html)
    table = None
    for t in main.find_all("table"):
        heads = [text(th) for th in t.find_all("th")]
        if heads == TECHNOLOGIES:
            table = t
            break
    if table is None:
        raise RuntimeError("the pre-application table (by technology) not found as read")
    out = []
    for tr in table.find("tbody").find_all("tr"):
        for j, td in enumerate(tr.find_all("td")):
            a = td.find("a", href=True)
            if a is None:
                continue
            name = text(a)
            slug = a["href"].rstrip("/").rsplit("/", 1)[-1]
            out.append(dict(entity_id=f"nrc_preapp:{slug}", entity_type="company", name=name, geo="", lat="", lon="", capacity_mw="",
                            status="", status_date="", operator="", source=base["source"], source_url=url,
                            retrieved_at=base["retrieved_at"], vintage=base["vintage"], x_technology=TECHNOLOGIES[j],
                            x_microreactor="yes" if "*" in text(td).split(name)[0] else "no", x_active="yes",
                            x_page=HOST + a["href"] if a["href"].startswith("/") else a["href"]))
    # the inactive projects, named after the table: "Inactive Projects - * Shepherd Power, LLC , * Westinghouse eVinci"
    after = table.find_next(string=re.compile(r"Inactive Projects"))
    if after is not None:
        holder = after.parent
        while holder is not None and holder.name not in ("p", "div", "li"):
            holder = holder.parent
        inside = set(map(id, holder.find_all("a", href=True))) if holder is not None else set()
        for a in [a for a in after.find_all_next("a", href=True) if id(a) in inside]:  # the links after the words, in their block
            slug = a["href"].rstrip("/").rsplit("/", 1)[-1]
            hit = [r for r in out if r["entity_id"] == f"nrc_preapp:{slug}"]
            if hit:
                hit[0]["x_active"] = "no"
            else:
                out.append(dict(entity_id=f"nrc_preapp:{slug}", entity_type="company", name=text(a), geo="", lat="", lon="", capacity_mw="",
                                status="", status_date="", operator="", source=base["source"], source_url=url,
                                retrieved_at=base["retrieved_at"], vintage=base["vintage"], x_technology="",
                                x_microreactor="yes" if "*" in text(holder).split(text(a))[0][-4:] else "no", x_active="no",
                                x_page=HOST + a["href"] if a["href"].startswith("/") else a["href"]))
    if not out:
        raise RuntimeError("the pre-application table holds no applicant")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="The NRC's advanced reactor applications and pre-applicants")
    ap.add_argument("--offline", action="store_true", help="the saved pages only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
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

    def get(url):
        content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=60, pause=1)
        return content.decode("utf-8", errors="replace"), dict(source=SOURCE, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))

    common = [
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/nrc_new_reactors.py",
        f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
        f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
        f"Source: {SOURCE} U.S. Nuclear Regulatory Commission, Advanced Reactors: Who We're Working With, {WHO}",
        'License: public (NRC: "a U.S. Government Work under federal copyright law and as such, it is not subject to copyright").',
    ]
    try:
        html, base = get(APPS)
        links = project_links(html)
        rows = []
        for u in links:
            h, b = get(u)
            rows.append(application(h, u, b))
        a = pd.DataFrame(rows)
        if a.event_id.duplicated().any():
            raise RuntimeError("an event_id given twice")
        cols = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source",
                "source_url", "retrieved_at", "vintage"] + APP_X
        a = a[cols].sort_values("event_date").reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): U.S. Nuclear Regulatory Commission, the advanced reactor applications under review, one row an application "
            "with its applicant, kind, place, design, power and milestones (session 2001)",
            "Shape: events (docs/datastandard.md v0). event_id nrc_app:<the page's name>; event_date the application's submittal ('When:', its first date, a month's first day where it gives a "
            "month, x_when as written; or 'Application Tendered'); event_type the kind of application; parties the applicant; mw the electric power the page states (MWe), else empty; status the latest "
            "milestone the page marks done (A); x_status_date its date; x_next_milestone and x_next_target the first one marked a target (T) or TBD; "
            "x_decision and x_decision_target the permit or license decision's row; x_reactor_type, x_power_level, x_fuel as written.",
            f"{len(a)} applications, as the list {APPS} links them. The pages carry no docket numbers; none is made. A field the page leaves out stays "
            "blank. Nothing is filled.",
            f"  access: {APPS} and each project's page (x_page)",
        ]
        ip.write_snapshot(a, APP_TABLE, head + common, log, cols)
        results.append(dict(table=APP_TABLE, market="all", status="ok", detail=f"{len(a)} rows"))
        print(f"{APP_TABLE}: {len(a)} applications")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{APP_TABLE} FAILED, no output file written:\n{tb}")
        print(f"{APP_TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=APP_TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    try:
        html, base = get(PRE)
        p = pd.DataFrame(preapplicants(html, base, PRE))
        if p.entity_id.duplicated().any():
            raise RuntimeError(f"an entity_id given twice: {p[p.entity_id.duplicated()].entity_id.tolist()}")
        cols = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
                "source", "source_url", "retrieved_at", "vintage"] + PRE_X
        p = p[cols].sort_values("entity_id").reset_index(drop=True)
        head = [
            "Energy Research Warehouse (ERW): U.S. Nuclear Regulatory Commission, the applicants, vendors and research or test reactors in pre-application "
            "engagement for advanced reactors, by technology (session 2001)",
            "Shape: entities (docs/datastandard.md v0). entity_id nrc_preapp:<the page's name>; entity_type company; name as the NRC's table writes it; "
            "x_technology the table's column; x_microreactor yes where the table marks a microreactor design (*); x_active no for the 'Inactive Projects' "
            "the page names after the table. A link's text is kept as written (the NRC's 'Advance Energy Bridge (AEB)' links to its Nuclear Vault System page).",
            f"{len(p)} rows, {int((p.x_active == 'no').sum())} inactive. Nothing is filled.",
            f"  access: {PRE}",
        ]
        ip.write_snapshot(p, PRE_TABLE, head + common, log, cols)
        results.append(dict(table=PRE_TABLE, market="all", status="ok", detail=f"{len(p)} rows"))
        print(f"{PRE_TABLE}: {len(p)} rows")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{PRE_TABLE} FAILED, no output file written:\n{tb}")
        print(f"{PRE_TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=PRE_TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ok = [r["table"] for r in results if r["status"] == "ok"]
        if ok:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Nuclear Regulatory Commission (NRC)",
                                    report="Advanced Reactors: application projects and pre-application activities", report_url=WHO,
                                    document_list=APPS + " ; " + PRE, license="public", tables=[APP_TABLE, PRE_TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
