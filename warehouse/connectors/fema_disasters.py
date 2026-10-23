#!/usr/bin/env python3
"""FEMA's disaster declarations: every major disaster, emergency and fire management declaration and the areas it
names, from 2015 (session 2056, chain 066: the disasters that follow the storms and outages the ERW holds).

Energy Research Warehouse (ERW) connector. One events table from OpenFEMA's Disaster Declarations Summaries (v2), its
whole data set as one CSV:

    https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries.csv

    fema_disaster_declarations   event_id fema:<declaration>:<state FIPS><county FIPS>:<place code> (FEMA's
                                 femaDeclarationString, e.g. DR-4834-FL, and the designated area's codes); event_date
                                 the declaration date (UTC day); event_type major_disaster (DR), emergency (EM) or
                                 fire_management (FM); parties FEMA; entity_ids the designated area as US-<state>, and its
                                 county FIPS where FEMA names a county (its code is not 000); status open, or closed where FEMA gives a closeout date; x_incident_type
                                 FEMA's incident type (Hurricane, Severe Storm, Fire, ...); x_title the declaration's
                                 title; x_state; x_designated_area; x_incident_begin, x_incident_end (UTC days, empty
                                 where FEMA gives none); x_programs the programs declared (IH, IA, PA, HM); x_disaster_number;
                                 x_region; x_tribal (1 for a tribal request)

A row whose declaration date is before 2015 is left out (the chain asked from 2015; FEMA's set runs from 1953). A
column not read below, a declaration type not in the map, a date that does not read, or an event_id given twice stops
the run. Nothing is filled.

    python warehouse/connectors/fema_disasters.py [--offline] [--out-dir DIR] [--since 2015-01-01]

Ceiling: one request (the whole set, refreshed by FEMA as declarations change; saved in warehouse/raw/fema_disasters/).
www.fema.gov's robots file asks a crawl delay of 15 seconds and disallows no path under /api/open/. License: public
(OpenFEMA's terms, read in session 2056: cite the endpoint and the time retrieved, and state "This product uses the
Federal Emergency Management Agency's OpenFEMA API, but is not endorsed by FEMA. The Federal Government or FEMA cannot
vouch for the data or analyses derived from these data after the data have been retrieved from the Agency's
website(s)."; FEMA's and DHS's logos and seals are not used).
"""

import argparse
import datetime as dt
import io
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "fema_disasters"
SOURCE = "fema:openfema_disaster_declarations_v2"
PAGE = "https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2"
URL = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries.csv"
TABLE = "fema_disaster_declarations"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
X_COLS = ["x_incident_type", "x_title", "x_state", "x_designated_area", "x_incident_begin", "x_incident_end", "x_programs",
          "x_disaster_number", "x_region", "x_tribal", "retrieved_at", "vintage"]
TYPES = {"DR": "major_disaster", "EM": "emergency", "FM": "fire_management"}
NEED = ["femaDeclarationString", "disasterNumber", "state", "declarationType", "declarationDate", "incidentType", "declarationTitle",
        "ihProgramDeclared", "iaProgramDeclared", "paProgramDeclared", "hmProgramDeclared", "incidentBeginDate", "incidentEndDate",
        "disasterCloseoutDate", "tribalRequest", "fipsStateCode", "fipsCountyCode", "placeCode", "designatedArea", "region"]
NOTICE = ("This product uses the Federal Emergency Management Agency's OpenFEMA API, but is not endorsed by FEMA. The Federal Government "
          "or FEMA cannot vouch for the data or analyses derived from these data after the data have been retrieved from the Agency's website(s).")


def day(v, what, required=True):
    if pd.isna(v) or str(v).strip() == "":
        if required:
            raise RuntimeError(f"{what}: no date")
        return ""
    t = pd.to_datetime(v, utc=True, errors="coerce")
    if pd.isna(t):
        raise RuntimeError(f"{what}: a date that does not read: {v!r}")
    return t.strftime("%Y-%m-%d")


def parse(content, base, since):
    d = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    missing = [c for c in NEED if c not in d.columns]
    if missing:
        raise RuntimeError(f"no column {missing}; the file's columns are {list(d.columns)}")
    out = []
    for r in d.itertuples(index=False):
        r = r._asdict()
        date = day(r["declarationDate"], r["femaDeclarationString"])
        if date < since:
            continue
        kind = r["declarationType"].strip()
        if kind not in TYPES:
            raise RuntimeError(f"{r['femaDeclarationString']}: a declaration type not in the map: {kind!r}")
        st, co, place = r["fipsStateCode"].zfill(2), r["fipsCountyCode"].zfill(3), r["placeCode"].strip()
        progs = [p for p, c in (("IH", "ihProgramDeclared"), ("IA", "iaProgramDeclared"), ("PA", "paProgramDeclared"),
                                ("HM", "hmProgramDeclared")) if r[c].strip() in ("1", "True", "true")]
        closed = day(r["disasterCloseoutDate"], r["femaDeclarationString"], required=False)
        out.append(dict(base, event_id=f"fema:{r['femaDeclarationString'].strip()}:{st}{co}:{place}", event_date=date, event_type=TYPES[kind],
                        parties="FEMA", entity_ids=f"US-{r['state'].strip()}" + (f";fips:{st}{co}" if co != "000" else ""), mw="", price="",
                        currency="", status="closed" if closed else "open", x_incident_type=r["incidentType"].strip(),
                        x_title=r["declarationTitle"].strip(), x_state=r["state"].strip(), x_designated_area=r["designatedArea"].strip(),
                        x_incident_begin=day(r["incidentBeginDate"], r["femaDeclarationString"], required=False),
                        x_incident_end=day(r["incidentEndDate"], r["femaDeclarationString"], required=False), x_programs=";".join(progs),
                        x_disaster_number=r["disasterNumber"].strip(), x_region=r["region"].strip(),
                        x_tribal="1" if r["tribalRequest"].strip() in ("1", "True", "true") else "0"))
    if not out:
        raise RuntimeError(f"no declaration on or after {since}")
    return out, len(d)


def main(argv=None):
    ap = argparse.ArgumentParser(description="FEMA's disaster declarations and their designated areas")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--since", default="2015-01-01")
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
        # session 2066: the pause list first (CLAUDE.md), as boem_ogor.py asks it
        if ip.paused(CONNECTOR) or ip.paused_host("www.fema.gov"):
            raise RuntimeError("www.fema.gov is paused (warehouse/metadata/paused_sources.csv): no request made")
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=300, pause=15)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        rows, n_all = parse(content, base, args.since)
        t = pd.DataFrame(rows)
        dup = t.event_id.duplicated(keep=False)
        if dup.any():
            raise RuntimeError(f"an event_id given twice: {t[dup].event_id.head(5).tolist()}")
        cols = EVENT_COLS + X_COLS
        t = t[cols].sort_values(["event_date", "event_id"]).reset_index(drop=True)
        by = t.event_type.value_counts().to_dict()
        head = [
            "Energy Research Warehouse (ERW): FEMA, OpenFEMA Disaster Declarations Summaries (v2): each declaration and designated area, "
            f"declared on or after {args.since} (session 2056)",
            "Shape: events (docs/datastandard.md v0). event_id fema:<declaration>:<state and county FIPS>:<place code>; event_date the declaration "
            "date; event_type major_disaster, emergency or fire_management; parties FEMA; entity_ids US-<state>, and fips:<state><county> where FEMA names a county; status "
            "open or closed (a closeout date); x_ columns FEMA's incident type, title, area, incident dates, programs, disaster number, region.",
            f"{len(t)} rows of FEMA's {n_all} ({t.x_disaster_number.nunique()} declarations; {', '.join(f'{k} {v}' for k, v in sorted(by.items()))}); "
            "rows declared before the start date are left out. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/fema_disasters.py; the file retrieved {base['retrieved_at']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Federal Emergency Management Agency (FEMA), OpenFEMA Dataset: Disaster Declarations Summaries - v2, {PAGE}",
            f"  access: {URL}",
            f"License: public (OpenFEMA's terms). {NOTICE}",
        ]
        ip.write_snapshot(t, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{TABLE}: {len(t)} rows of {n_all}; {by}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Federal Emergency Management Agency (FEMA)",
                                    report="OpenFEMA Dataset: Disaster Declarations Summaries - v2", report_url=PAGE,
                                    document_list=PAGE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
