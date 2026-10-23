#!/usr/bin/env python3
"""The National Interagency Fire Center's wildfires, from the Wildland Fire Interagency Geospatial Services (WFIGS)
incident locations: every wildfire of 1,000 acres or more discovered from 2015, with its discovery and containment, its
place, its size and its cause (session 2134, chain 090: the fires near the grid, beside the storms and outages the ERW
holds).

Energy Research Warehouse (ERW) connector. One events table from the WFIGS Incident Locations feature service, which
NIFC's open data site (data-nifc.opendata.arcgis.com) publishes:

    https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Incident_Locations/FeatureServer/0/query
        where FireDiscoveryDateTime >= 2015-01-01, IncidentTypeCategory 'WF' (wildfire) and the final size (FinalAcres,
        else IncidentSize) at least 1,000 acres; pages of 2,000 records ordered by OBJECTID

    wfigs_wildfires   event_id wfigs:<IRWIN id>; event_date the discovery's UTC day; event_type wildfire;
                      parties empty; entity_ids empty; mw empty; status out where a fire-out time is given, contained
                      where a containment time is, else empty; x_ the incident's name, state (POOState, US-<state>), county,
                      latitude and longitude of its point of origin, final acres and incident size as published, the
                      cause (general and as published), discovery, containment and fire-out times (UTC), the unique fire
                      identifier (a few are given twice, under two IRWIN records: both kept, counted in the header)

Fires below 1,000 acres are not taken: the service holds tens of thousands a year, more than the session's ceiling of
pages allows; the threshold is in the header. A page without the fields above, a discovery time not a time, or an IRWIN
record given twice stops the run. Nothing is filled.

    python warehouse/connectors/wfigs_wildfires.py [--offline] [--out-dir DIR] [--min-acres 1000]

Ceiling: one request a page (four for 2015 to October 2026), saved in warehouse/raw/wfigs_wildfires/ and reused offline.
The service's host has no robots file; data-nifc.opendata.arcgis.com's asks a 60-second crawl delay and is not asked by
this connector. License: public (a federal interagency record; read in the licenses round).
"""

import argparse
import datetime as dt
import json
import os
import sys
import traceback
import urllib.parse

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "wfigs_wildfires"
SOURCE = "nifc:wfigs_incident_locations"
SERVICE = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Incident_Locations/FeatureServer/0"
HUB = "https://data-nifc.opendata.arcgis.com/"
TABLE = "wfigs_wildfires"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
FIELDS = ["OBJECTID", "UniqueFireIdentifier", "IrwinID", "IncidentName", "POOState", "POOCounty", "InitialLatitude", "InitialLongitude",
          "FinalAcres", "IncidentSize", "FireCauseGeneral", "FireCause", "FireDiscoveryDateTime", "ContainmentDateTime", "FireOutDateTime"]
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
X_COLS = ["x_name", "x_state", "x_county", "x_latitude", "x_longitude", "x_final_acres", "x_incident_size_acres", "x_cause_general",
          "x_cause", "x_discovered_utc", "x_contained_utc", "x_out_utc", "x_unique_fire_id", "retrieved_at", "vintage"]
PAGE = 2000


def where(min_acres):
    return (f"FireDiscoveryDateTime >= DATE '2015-01-01' AND IncidentTypeCategory = 'WF' AND "
            f"COALESCE(FinalAcres,IncidentSize) >= {int(min_acres)}")


def page_url(min_acres, offset):
    q = {"where": where(min_acres), "outFields": ",".join(FIELDS), "orderByFields": "OBJECTID", "resultOffset": str(offset),
         "resultRecordCount": str(PAGE), "returnGeometry": "false", "f": "json"}
    return SERVICE + "/query?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote)


def utc(ms, what):
    if ms in (None, ""):
        return ""
    try:
        return pd.Timestamp(int(ms), unit="ms", tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError):
        raise RuntimeError(f"{what}: a time not a time: {ms!r}")


def num(v):
    return "" if v in (None, "") else f"{float(v):g}"


def rows_of(page, base):
    if "error" in page:
        raise RuntimeError(f"the service answered an error: {page['error']}")
    feats = page.get("features")
    if feats is None:
        raise RuntimeError("a page without features")
    out = []
    for f in feats:
        a = f.get("attributes") or {}
        miss = [k for k in FIELDS if k not in a]
        if miss:
            raise RuntimeError(f"a record without {miss}")
        if not a["IrwinID"]:
            raise RuntimeError(f"fire {a['UniqueFireIdentifier']}: no IRWIN id")
        disc = utc(a["FireDiscoveryDateTime"], f"fire {a['UniqueFireIdentifier']}")
        if not disc:
            raise RuntimeError(f"fire {a['UniqueFireIdentifier']}: no discovery time")
        cont, out_t = utc(a["ContainmentDateTime"], "containment"), utc(a["FireOutDateTime"], "fire out")
        out.append(dict(event_id="wfigs:" + a["IrwinID"].strip("{}").lower(), event_date=disc[:10], event_type="wildfire", parties="", entity_ids="",
                        mw="", price="", currency="", status="out" if out_t else "contained" if cont else "", **base,
                        x_name=a["IncidentName"] or "", x_state=a["POOState"] or "", x_county=a["POOCounty"] or "",
                        x_latitude=num(a["InitialLatitude"]), x_longitude=num(a["InitialLongitude"]), x_final_acres=num(a["FinalAcres"]),
                        x_incident_size_acres=num(a["IncidentSize"]), x_cause_general=a["FireCauseGeneral"] or "", x_cause=a["FireCause"] or "",
                        x_discovered_utc=disc, x_contained_utc=cont, x_out_utc=out_t, x_unique_fire_id=a["UniqueFireIdentifier"] or ""))
    return out, bool(page.get("exceededTransferLimit"))


def main(argv=None):
    ap = argparse.ArgumentParser(description="NIFC's WFIGS wildfires of 1,000 acres or more, from 2015")
    ap.add_argument("--offline", action="store_true", help="the saved pages only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--min-acres", type=int, default=1000)
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host("services3.arcgis.com"):
        print(f"{TABLE}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
        return 0
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
        rows, offset, pages, latest = [], 0, 0, ""
        while True:
            url = page_url(args.min_acres, offset)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=120, pause=2)
            base = dict(source=SOURCE, source_url=SERVICE, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            got, more = rows_of(json.loads(content.decode("utf-8")), base)
            rows += got
            pages += 1
            latest = max(latest, str(base["retrieved_at"]))
            if not more or not got:
                break
            offset += len(got)
            if pages > 20:
                raise RuntimeError("more than 20 pages: the threshold lets too many fires through")
        e = pd.DataFrame(rows)
        if e.event_id.duplicated().any():
            raise RuntimeError(f"an IRWIN record given twice: {e.event_id[e.event_id.duplicated()].head(3).tolist()}")
        twice = int(e.x_unique_fire_id[e.x_unique_fire_id != ""].duplicated().sum())
        cols = EVENT_COLS + X_COLS
        e = e[cols].sort_values(["event_date", "event_id"]).reset_index(drop=True)
        by_year = e.event_date.str[:4].value_counts().sort_index().to_dict()
        head = [
            "Energy Research Warehouse (ERW): National Interagency Fire Center (NIFC), Wildland Fire Interagency Geospatial Services (WFIGS), "
            f"Incident Locations: every wildfire of {args.min_acres:,} acres or more discovered from 2015 (session 2134)",
            "Shape: events (docs/datastandard.md v0). event_id wfigs:<IRWIN id>; event_date the discovery's UTC day; event_type wildfire; "
            "status out or contained where those times are given; x_ the name, state and county of origin, the point of origin, the final acres "
            "and incident size as published (acres), the cause, the discovery, containment and fire-out times (UTC), and the unique fire identifier.",
            f"{len(e)} fires in {pages} pages: " + ", ".join(f"{y} {n}" for y, n in by_year.items()) + f". Fires below {args.min_acres:,} acres are "
            f"not taken. {twice} unique fire identifiers are each given under two IRWIN records, and both are kept as published. Nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/wfigs_wildfires.py; the latest page retrieved {latest}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} NIFC, WFIGS Incident Locations, {HUB}",
            f"  access: {SERVICE}/query (where {where(args.min_acres)}; pages of {PAGE})",
            'License: public (a federal interagency record; cite "National Interagency Fire Center, WFIGS").',
        ]
        ip.write_snapshot(e, TABLE, head, log, cols)
        results.append(dict(table=TABLE, market="all", status="ok", detail=f"{len(e)} rows"))
        print(f"{TABLE}: {len(e)} fires in {pages} pages")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{TABLE} FAILED, no output file written:\n{tb}")
        print(f"{TABLE} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=TABLE, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="National Interagency Fire Center (NIFC)",
                                    report="Wildland Fire Interagency Geospatial Services (WFIGS): Incident Locations", report_url=HUB,
                                    document_list=SERVICE, license="public", tables=[TABLE])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
