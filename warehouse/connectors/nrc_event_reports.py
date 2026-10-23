#!/usr/bin/env python3
"""The Nuclear Regulatory Commission's Event Notification Reports: each power reactor event the licensees reported to
the NRC's Operations Center, with each unit's power before and after and the rule it was reported under (session 2043,
chain 059: the reactors' own reports beside nrc_reactor_status's daily power).

Energy Research Warehouse (ERW) connector. One events table, warehouse/output/nrc_event_notifications.csv, from two
of the NRC's own publications of the same reports:

    the raw data file  https://www.nrc.gov/sites/default/files/doc_library/reading-rm/doc-collections/event-status/event/
                       event-notification-rpt-lastmonth.txt (pipe separated, the fields of the NRC's data dictionary;
                       its Last-Modified was 5 August 2025 when session 2043 read it; its reports were notified in June and July
                       2025, of events from May to July)
    the daily pages    https://www.nrc.gov/documents-reports/document-collections/events-reports-associated-with/
                       event-notification-reports/<YEAR>/<YYYYMMDD>en, listed by the year's index page

Only the reports the NRC files under "Power Reactor" are kept; agreement state, materials, fuel cycle and Part 21
reports are not. One row a report and unit (a report about two units is two rows). The event text is not taken.

    event_id     nrc_en:<event number>:<unit>, or nrc_en:<event number> when the report names no unit
    event_date   the event's time in UTC, from the NRC's event date and time in the zone the report names (EDT, CST and
                 the rest); x_event_local and x_event_tz keep the NRC's
    event_type   reactor_scram when the unit's scram code is not N (A/R automatic, M/R manual) or the report is made
                 under 50.72(b)(2)(iv)(B) (the reactor protection system actuated while critical), else reactor_event
    parties      the licensee where the report names one (the raw file names it; the daily pages' power reactor reports
                 name none, and those rows' parties are empty);
                 x_facility the site; x_last_update the date of the report's last update
    x_*          the event number, unit, region, state, county, docket, reactor type, the notification's time (the NRC's
                 Eastern time and UTC), the last update, the emergency class, every 10 CFR section and its words, the
                 scram code, whether the reactor was critical, the initial and current power in percent and modes, and
                 which publication the row was read from

Values as the NRC publishes them; a blank stays blank; nothing is filled. A label not in the map, a time zone not in
ZONES, a page without its event numbers or a report given twice with different contents stops the run.

    python warehouse/connectors/nrc_event_reports.py [--offline] [--no-refresh] [--pages N] [--year 2026] [--out-dir DIR]

Ceiling: the raw file and the year's index (fresh each run unless --no-refresh), and at most N daily pages a run
(--pages, default 10), the newest first, of the year --year names (the current year by default); a page saved by an
earlier run is reused from warehouse/raw/nrc_event_reports/ and not counted, so later runs reach further back within that
year, and an earlier year is read with --year. The table is rewritten whole from every saved page each run. The NRC's robots file disallows only its search pages, ads.txt and
autodiscover for every reader. License: the NRC's site disclaimer, a U.S. Government work, "no restrictions on use"
(read 16).
"""

import argparse
import datetime as dt
import html as htmllib
import io
import os
import re
import sys
import traceback
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "nrc_event_notifications"
CONNECTOR = "nrc_event_reports"
SOURCE = "nrc:event_notification_reports"
BASE = "https://www.nrc.gov/documents-reports/document-collections/events-reports-associated-with/event-notification-reports"
RAW_FILE = ("https://www.nrc.gov/sites/default/files/doc_library/reading-rm/doc-collections/event-status/event/"
            "event-notification-rpt-lastmonth.txt")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status",
              "source", "source_url", "retrieved_at"]
X_COLS = ["x_en_number", "x_facility", "x_unit", "x_region", "x_state", "x_county", "x_docket", "x_reactor_type",
          "x_notification_et", "x_notification_utc", "x_event_local", "x_event_tz", "x_last_update",
          "x_emergency_class", "x_cfr", "x_cfr_words", "x_scram_code", "x_rx_crit", "x_initial_power_pct",
          "x_initial_mode", "x_current_power_pct", "x_current_mode", "x_read_from"]
# hours from UTC of the zones the NRC writes; ET is the Operations Center's own Eastern time, read with daylight saving
ZONES = {"EST": -5, "EDT": -4, "CST": -6, "CDT": -5, "MST": -7, "MDT": -6, "PST": -8, "PDT": -7, "AKST": -9,
         "AKDT": -8, "HST": -10, "UTC": 0, "GMT": 0}
EASTERN = ZoneInfo("America/New_York")
PAGE_RE = re.compile(r'href="[^"]*/event-notification-reports/(\d{4})/(\d{8})en"')


def text(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", str(v)))).strip()


def mdy(s):
    s = text(s)
    if not s:
        return ""
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})(?: .*)?", s)
    if not m:
        raise RuntimeError(f"not a date in the NRC's form: {s!r}")
    return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"


def hm(s):
    s = text(s)
    m = re.fullmatch(r"(\d{1,2}):(\d{2})(?::\d{2})?", s)
    if not m:
        raise RuntimeError(f"not a time in the NRC's form: {s!r}")
    return f"{int(m.group(1)):02d}:{m.group(2)}"


def to_utc(day, clock, zone):
    """(local ISO time, UTC ISO time) of the NRC's date, time and zone; ET with daylight saving."""
    if not day:
        return "", ""
    local = dt.datetime.fromisoformat(f"{day}T{hm(clock) if text(clock) else '00:00'}:00")
    zone = text(zone).upper()
    if zone == "ET":
        utc = local.replace(tzinfo=EASTERN).astimezone(dt.timezone.utc)
    elif zone in ZONES:
        utc = local - dt.timedelta(hours=ZONES[zone])
    else:
        raise RuntimeError(f"a time zone not in the map: {zone!r}")
    return local.strftime("%Y-%m-%dT%H:%M:%S"), utc.strftime("%Y-%m-%dT%H:%M:%SZ")


def unit_rows(base, units):
    """One row a unit: base holds the report's fields, units a list of dicts (unit, scram code, power, modes)."""
    out = []
    for u in units or [{}]:
        r = dict(base)
        unit = text(u.get("unit"))
        r["x_unit"] = unit
        r["event_id"] = f"nrc_en:{base['x_en_number']}" + (f":{unit}" if unit else "")
        for k in ("x_scram_code", "x_rx_crit", "x_initial_power_pct", "x_initial_mode", "x_current_power_pct", "x_current_mode"):
            r[k] = text(u.get(k))
        code = r["x_scram_code"].upper()
        rps = "50.72(b)(2)(iv)(B)" in r["x_cfr"]
        r["event_type"] = "reactor_scram" if (code and code != "N") or rps else "reactor_event"
        out.append(r)
    return out


def base_row(**kw):
    r = {c: "" for c in EVENT_COLS + X_COLS}
    r.update(source=SOURCE, **kw)
    return r


# ---------------------------------------------------------------- the raw data file

RAW_FIELDS = ["Event Desc", "En No", "Site Name", "Licensee Name", "Region No", "City Name", "State Cd", "County Name",
              "License No", "Agreement State Ind", "Docket No", "Unit Ind1", "Unit Ind2", "Unit Ind3", "Reactor Type",
              "Nrc Notified By", "Ops Officer", "Notification Dt", "Notification Time", "Event Dt", "Event Time",
              "Time Zone", "Last Updated Dt", "Emergency Class"] + [f"Cfr {k}{i}" for i in range(1, 5) for k in ("Cd", "Descr")] \
    + [f"{k}{i}" for i in range(1, 11) for k in ("Staff Name", "Org Abbrev")] \
    + ["Scram Code 1", "RX CRIT 1", "Initial PWR 1", "Initial RX Mode1", "Current PWR 1", "Current RX Mode 1"] \
    + [f"{k} {i}" for i in (2, 3) for k in ("Scram Code", "RX CRIT", "Initial PWR", "Initial RX Mode", "Current PWR", "Current RX Mode")] \
    + ["Event Text"]


def raw_events(content, url, retrieved):
    t = pd.read_csv(io.StringIO(content.decode("utf-8", errors="replace")), sep="|", dtype=str, keep_default_na=False)
    t = t.loc[:, [c for c in t.columns if not c.startswith("Unnamed")]]
    if list(t.columns) != RAW_FIELDS:
        raise RuntimeError(f"{url}: the fields are not the data dictionary's: {[c for c in t.columns if c not in RAW_FIELDS]}")
    out = []
    for r in t[t["Event Desc"].str.strip() == "Power Reactor"].to_dict("records"):
        en = text(r["En No"])
        event_local, event_utc = to_utc(mdy(r["Event Dt"]), r["Event Time"], r["Time Zone"])
        note_local, note_utc = to_utc(mdy(r["Notification Dt"]), r["Notification Time"], "ET")
        cfr = [(text(r[f"Cfr Cd{i}"]), text(r[f"Cfr Descr{i}"])) for i in range(1, 5)]
        base = base_row(x_en_number=en, event_date=event_utc, parties=text(r["Licensee Name"]), source_url=url,
                        retrieved_at=retrieved, x_facility=text(r["Site Name"]), x_region=text(r["Region No"]),
                        x_state=text(r["State Cd"]), x_county=text(r["County Name"]), x_docket=text(r["Docket No"]),
                        x_reactor_type=text(r["Reactor Type"]), x_notification_et=note_local, x_notification_utc=note_utc,
                        x_event_local=event_local, x_event_tz=text(r["Time Zone"]),
                        x_last_update=mdy(r["Last Updated Dt"]), x_emergency_class=text(r["Emergency Class"]),
                        x_cfr="; ".join(c for c, _ in cfr if c), x_cfr_words="; ".join(d for c, d in cfr if c),
                        x_read_from="raw_file")
        units = []
        for i, ind in enumerate(("Unit Ind1", "Unit Ind2", "Unit Ind3"), start=1):
            if text(r[ind]):
                s = "" if i == 1 else " "
                units.append({"unit": text(r[ind]), "x_scram_code": r[f"Scram Code {i}"], "x_rx_crit": r[f"RX CRIT {i}"],
                              "x_initial_power_pct": r[f"Initial PWR {i}"],
                              "x_initial_mode": r["Initial RX Mode1"] if i == 1 else r[f"Initial RX Mode{s}{i}"],
                              "x_current_power_pct": r[f"Current PWR {i}"], "x_current_mode": r[f"Current RX Mode {i}"]})
        out.extend(unit_rows(base, units))
    return out


# ---------------------------------------------------------------- the daily pages

LABELS = {"Facility": "x_facility", "Rep Org": "parties", "Licensee": "parties", "Region": "x_region", "State": "x_state",
          "City": None, "County": "x_county", "License #": None, "Agreement": None, "Docket": "x_docket",
          "Unit": "units", "RX Type": "x_reactor_type", "NRC Notified By": None, "HQ OPS Officer": None,
          "Notification Date": "notification_date", "Notification Time": "notification_time", "Event Date": "event_date",
          "Event Time": "event_time", "Last Update Date": "x_last_update", "Emergency Class": "x_emergency_class",
          "Person (Organization)": None}
UNIT_HEAD = ["Unit", "SCRAM Code", "RX Crit", "Initial PWR", "Initial RX Mode", "Current PWR", "Current RX Mode"]


def page_events(page, url, retrieved):
    blocks = re.split(r'<div class="grid border" id="en(\d+)">', page)
    if len(blocks) < 3:
        if "EVENT NUMBERS" in page or "Event Number:" in page:
            raise RuntimeError(f"{url}: event numbers listed but no block read")
        return []
    out = []
    for i in range(1, len(blocks), 2):
        en, body = blocks[i], blocks[i + 1]
        body = body.split("<b>Event Text</b>")[0] if "<b>Event Text</b>" in body else body
        kind = text(re.search(r'<div class="th">(.*?)</div>', body, re.S).group(1))
        if kind != "Power Reactor":
            continue
        fields = {}
        for label, value in re.findall(r"<b>([^<:]+):</b>(.*?)(?=<b>|<br|</div>)", body, re.S):
            label = text(label)
            if label not in LABELS:
                raise RuntimeError(f"{url}: EN {en}: a label not in the map: {label!r}")
            if LABELS[label]:
                fields[LABELS[label]] = text(value)
        cfr = re.search(r"10 CFR Section:(.*?)</div>", body, re.S)
        cfr_lines = [text(x) for x in re.split(r"<br\s*/?>", cfr.group(1))] if cfr else []
        cfr_lines = [x for x in cfr_lines if x]
        codes, words = [], []
        for line in cfr_lines:
            m = re.match(r"^(\d+\.\d+\S*)\s*-\s*(.*)$", line)
            codes.append(m.group(1) if m else line)
            words.append(m.group(2) if m else "")
        tz = re.search(r"\[(\w+)\]", fields.get("event_time", ""))
        ntz = re.search(r"\[(\w+)\]", fields.get("notification_time", ""))
        event_local, event_utc = to_utc(mdy(fields.get("event_date", "")), re.sub(r"\s*\[.*", "", fields.get("event_time", "")),
                                        tz.group(1) if tz else "")
        note_local, note_utc = to_utc(mdy(fields.get("notification_date", "")),
                                      re.sub(r"\s*\[.*", "", fields.get("notification_time", "")), ntz.group(1) if ntz else "ET")
        base = base_row(x_en_number=en, event_date=event_utc, parties=fields.get("parties", ""), source_url=url,
                        retrieved_at=retrieved, x_facility=fields.get("x_facility", ""), x_region=fields.get("x_region", ""),
                        x_state=fields.get("x_state", ""), x_county=fields.get("x_county", ""),
                        x_docket=fields.get("x_docket", ""), x_reactor_type=fields.get("x_reactor_type", ""),
                        x_notification_et=note_local, x_notification_utc=note_utc, x_event_local=event_local,
                        x_event_tz=tz.group(1) if tz else "", x_last_update=mdy(fields.get("x_last_update", "")),
                        x_emergency_class=fields.get("x_emergency_class", ""), x_cfr="; ".join(codes),
                        x_cfr_words="; ".join(w for w in words if w), x_read_from="daily_page")
        out.extend(unit_rows(base, unit_table(blocks[i + 1], url, en)))
    return out


def unit_table(body, url, en):
    """The report's table of units (unit, scram code, criticality, initial and current power and mode), if any."""
    m = re.search(r"<table.*?</table>", body.split("<b>Event Text</b>")[0], re.S)
    if not m:
        return []
    rows = [[text(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)] for tr in re.findall(r"<tr.*?</tr>", m.group(0), re.S)]
    rows = [r for r in rows if any(r)]
    if not rows or rows[0] != UNIT_HEAD:
        raise RuntimeError(f"{url}: EN {en}: a unit table not in the expected form: {rows[:1]}")
    keys = ["unit", "x_scram_code", "x_rx_crit", "x_initial_power_pct", "x_initial_mode", "x_current_power_pct", "x_current_mode"]
    return [dict(zip(keys, r)) for r in rows[1:]]


def build(rows):
    t = pd.DataFrame(rows, columns=EVENT_COLS + X_COLS)
    if t.empty:
        raise RuntimeError("no power reactor report read")
    t = t.drop_duplicates()
    twice = t.event_id[t.event_id.duplicated()]
    if len(twice):
        # the same report in both publications: the daily page's row is kept when the two agree on what was measured
        keys = ["x_scram_code", "x_initial_power_pct", "x_current_power_pct", "event_date"]
        for eid in twice.unique():
            same = t[t.event_id == eid]
            if len(same.drop_duplicates(subset=keys)) > 1:
                raise RuntimeError(f"a report given twice with different contents: {eid}")
        t = t.sort_values("x_read_from").drop_duplicates(subset=["event_id"], keep="first")  # daily_page before raw_file
    return t.sort_values(["event_date", "event_id"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The NRC's event notification reports, power reactors")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--no-refresh", action="store_true", help="the raw file and the index as saved, not asked again")
    ap.add_argument("--pages", type=int, default=10, help="at most this many daily pages asked for a run")
    ap.add_argument("--year", type=int, default=dt.datetime.now(dt.timezone.utc).year)
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
    fresh = not args.no_refresh
    try:
        content, rec = ip.fetch_raw(CONNECTOR, RAW_FILE, log, offline=args.offline, fresh=fresh, headers=UA, timeout=120)
        rows = raw_events(content, RAW_FILE, rec.get("retrieved_at") or "")
        raw_vintage = ip.vintage_of(rec)
        index_url = f"{BASE}/{args.year}"
        content, _ = ip.fetch_raw(CONNECTOR, index_url, log, offline=args.offline, fresh=fresh, headers=UA, timeout=120)
        days = sorted({d for y, d in PAGE_RE.findall(content.decode("utf-8", errors="replace")) if int(y) == args.year}, reverse=True)
        if not days:
            raise RuntimeError(f"{index_url} lists no daily page")
        asked, read = 0, []
        for d in days:
            url = f"{BASE}/{d[:4]}/{d}en"
            cached = ip.raw_cached(CONNECTOR, url)
            if not cached:
                if args.offline or asked >= args.pages:
                    continue
                asked += 1
            page, prec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, headers=UA, timeout=120)
            rows.extend(page_events(page.decode("utf-8", errors="replace"), url, prec.get("retrieved_at") or ""))
            read.append(d)
        t = build(rows)
        by = t.groupby(["x_read_from", "event_type"]).size()
        header = [
            "Energy Research Warehouse (ERW): U.S. Nuclear Regulatory Commission, Event Notification Reports, power reactors: each report and unit, "
            "with the unit's power before and after and the 10 CFR sections it was reported under (session 2043)",
            "Shape: events (docs/datastandard.md v0). event_id nrc_en:<event number>:<unit>; event_date the event's time in UTC (the NRC's date, time and zone; "
            "x_event_local and x_event_tz keep them); event_type reactor_scram (the unit's scram code not N: A/R automatic, M/R manual; or reported under 50.72(b)(2)(iv)(B)) or reactor_event; "
            "parties the licensee where the report names one; x_initial_power_pct and x_current_power_pct the unit's power in percent before and at the report.",
            f"{len(t)} rows: " + "; ".join(f"{a} {b} {n}" for (a, b), n in by.items()) + f". The raw file's last modification: {raw_vintage}; "
            f"the daily pages read: {len(read)}" + (f", {read[-1]} to {read[0]}" if read else "") + ". Only reports filed under Power Reactor; the event text is not taken. "
            "Values as published; a blank stays blank; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nrc_event_reports.py; per row, retrieved_at and source_url",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Nuclear Regulatory Commission, Operations Center, Event Notification Reports, {BASE}",
            f"  access: {RAW_FILE} ; {BASE}/<YEAR>/<YYYYMMDD>en",
            "License: a U.S. Government work, not subject to copyright; \"there are no restrictions on use\" (the NRC's site disclaimer).",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=EVENT_COLS + X_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Nuclear Regulatory Commission (NRC)",
                                    report="Event Notification Reports (power reactors)", report_url=BASE,
                                    document_list=f"{RAW_FILE} ; {BASE}/<YEAR>", license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows ({by.to_dict()}); {asked} pages asked, {len(read)} read")
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
