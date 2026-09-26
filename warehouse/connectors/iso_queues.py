#!/usr/bin/env python3
"""ISO interconnection queues as entities tables, one per ISO.

Energy Research Warehouse (ERW) connector, session 8. Reads each ISO's
public interconnection queue with gridstatus (get_interconnection_queue) and
writes `<iso>_interconnection_queue` in the `entities` shape
(docs/datastandard.md):

    python warehouse/connectors/iso_queues.py                 # all ISOs
    python warehouse/connectors/iso_queues.py ercot caiso     # some

ISOs: ERCOT, CAISO, NYISO, MISO, SPP, ISO-NE. PJM's queue needs PJM_API_KEY;
it is read only if that key is set, and otherwise skipped and logged.

One row per queue position. entity_type `project`. entity_id is
`<iso>_queue:<queue id>`; where an ISO lists one queue id on several rows
(project phases, units), the id gets `:<n>`, n counting those rows in the
ISO's own order, and the log says so. name is the project name (empty where
the ISO gives none). capacity_mw is gridstatus's `Capacity (MW)`: the ISO's
requested capacity, or for MISO the larger of summer and winter net MW.
operator is the interconnecting entity.

Status: iso_status keeps the ISO's own vocabulary (SPP's original status
text, the others' status column as gridstatus reads it). `status` is the
harmonized value, one of active, withdrawn, completed, suspended, from the
per-ISO table STATUS_MAP; a status not in that table fails the ISO, so a new
ISO status is noticed. status_date is the withdrawn date for withdrawn rows,
the actual in-service date for completed rows where the ISO gives one, else
empty. A row the ISO lists with no status at all (SPP's affected-system
"ASGI" requests) keeps an empty status and iso_status; it is not guessed.

Dates (queue_date, proposed_in_service_date, actual_in_service_date,
withdrawn_date) are the ISO's dates, written YYYY-MM-DD; a timestamp's time of
day is dropped. Rows with no queue id and nothing else (blank spreadsheet rows
gridstatus reads from NYISO's withdrawn sheet) are dropped and counted; a row
with any data but no queue id fails the ISO.

Each table is a snapshot of the ISO's current queue (a later queue replaces
it; earlier ones stay in git history and the raw files). Weekly cadence:
run_daily.sh runs this on Mondays (UTC), or on any day with QUEUES=1.
"""

import argparse
import datetime as dt
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

import gridstatus  # noqa: E402

ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status",
               "status_date", "operator", "source"]
EXTRA_COLS = ["source_url", "retrieved_at", "vintage", "queue_id", "county", "state", "poi", "zone",
              "transmission_owner", "fuel_technology", "iso_status", "queue_date",
              "proposed_in_service_date", "actual_in_service_date", "withdrawn_date"]
STATES = {"Alabama": "AL", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
          "Connecticut": "CT", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
          "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Massachusetts": "MA", "Michigan": "MI",
          "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
          "Nevada": "NV", "New Hampshire": "NH", "New Mexico": "NM", "New York": "NY",
          "North Dakota": "ND", "Oklahoma": "OK", "Oregon": "OR", "Rhode Island": "RI",
          "South Dakota": "SD", "Texas": "TX", "Vermont": "VT", "Wisconsin": "WI", "Wyoming": "WY"}

PUBLISHERS = {"ercot": "Electric Reliability Council of Texas (ERCOT)",
              "caiso": "California Independent System Operator (CAISO)",
              "nyiso": "New York Independent System Operator (NYISO)",
              "miso": "Midcontinent Independent System Operator (MISO)",
              "spp": "Southwest Power Pool (SPP)", "isone": "ISO New England (ISO-NE)",
              "pjm": "PJM Interconnection (PJM)"}
# ISO status (as in iso_status) -> harmonized status
STATUS_MAP = {
    "ercot": {"Active": "active", "Completed": "completed"},
    "caiso": {"ACTIVE": "active", "WITHDRAWN": "withdrawn", "COMPLETED": "completed"},
    "nyiso": {"Active": "active", "Withdrawn": "withdrawn", "Completed": "completed"},
    "miso": {"Active": "active", "Withdrawn": "withdrawn", "Done": "completed", "LEGACY: Done": "completed",
             "Pending Revision Approval": "active", "Pending Transfer": "active"},
    "spp": {"WITHDRAWN": "withdrawn", "TERMINATED": "withdrawn",
            "IA FULLY EXECUTED/COMMERCIAL OPERATION": "completed",
            "IA FULLY EXECUTED/ON SUSPENSION": "suspended",
            "IA FULLY EXECUTED/ON SCHEDULE": "active", "IA PENDING": "active", "DISIS STAGE": "active",
            "FACILITY STUDY STAGE": "active", "SPECIAL STUDY": "active", "ERAS": "active", "ICS": "active"},
    "isone": {"Active": "active", "Withdrawn": "withdrawn", "Completed": "completed"},
    "pjm": {"Active": "active", "Withdrawn": "withdrawn", "In Service": "completed",
            "Suspended": "suspended", "Deactivated": "withdrawn", "Engineering and Procurement": "active",
            "Under Construction": "active", "Partially in Service - Under Construction": "active",
            "Retracted": "withdrawn", "Annulled": "withdrawn", "Confirmed": "active"},
}
ISOS = {
    "ercot": dict(cls="Ercot", label="ERCOT", page="https://www.ercot.com/mp/data-products/data-product-details?id=PG7-200-ER",
                  report="Generation Interconnection Status (GIS) report", data=r"mirDownload"),
    "caiso": dict(cls="CAISO", label="CAISO", page="http://www.caiso.com/PublishedDocuments/PublicQueueReport.xlsx",
                  report="Public Queue Report", data=r"PublicQueueReport"),
    "nyiso": dict(cls="NYISO", label="NYISO", page="https://www.nyiso.com/interconnections",
                  report="NYISO Interconnection Queue", data=r"Interconnection-Queue"),
    "miso": dict(cls="MISO", label="MISO", page="https://www.misoenergy.org/planning/resource-utilization/GI_Queue/",
                 report="Generator Interconnection Queue (giqueue API)", data=r"giqueue"),
    "spp": dict(cls="SPP", label="SPP", page="https://opsportal.spp.org/Studies/GIActive",
                report="Generation Interconnection Queue summary", data=r"GenerateSummaryCSV"),
    "isone": dict(cls="ISONE", label="ISO-NE", page="https://irtt.iso-ne.com/reports/external",
                  report="Interconnection Request Tracking Tool (IRTT) queue", data=r"irtt"),
    "pjm": dict(cls="PJM", label="PJM", page="https://www.pjm.com/planning/services-requests/interconnection-queues",
                report="New Services Queue", data=r"pjm"),
}


def text(s):
    return s.astype("string").fillna("").str.strip().replace({"nan": "", "None": "", "NaT": ""})


def dates(s, what, iso):
    t = text(s)
    parsed = pd.to_datetime(t.where(t != ""), errors="coerce", utc=True, format="mixed")
    bad = t[(t != "") & parsed.isna()]
    if len(bad):
        raise RuntimeError(f"{iso}: unparseable {what}: {bad.unique()[:5].tolist()}")
    # a date written with a local midnight (07:00Z, 08:00Z) is that local date, not the UTC one
    local = pd.to_datetime(t.where(t != ""), errors="coerce", format="mixed")
    try:
        local = local.dt.tz_localize(None)
    except TypeError:
        local = local.dt.tz_convert(None) if hasattr(local.dt, "tz_convert") else local
    return local.dt.strftime("%Y-%m-%d").fillna("")


def pick(df, *cols):
    for c in cols:
        if c in df.columns:
            return df[c]
    return pd.Series("", index=df.index)


def build(iso, df, url, got, log):
    cfg = ISOS[iso]
    df = df.reset_index(drop=True)
    qid = text(df["Queue ID"])
    blank = qid.eq("") & text(pick(df, "Project Name")).eq("") & text(pick(df, "Interconnecting Entity")).eq("")
    data_cols = [c for c in ("County", "Interconnection Location", "Generation Type", "Queue Date") if c in df]
    blank &= df[data_cols].isna().all(axis=1) if data_cols else True
    if blank.any():
        log(f"  {int(blank.sum())} rows with no queue id and no data dropped (blank source rows)")
    df, qid = df[~blank].reset_index(drop=True), qid[~blank].reset_index(drop=True)
    if qid.eq("").any():
        raise RuntimeError(f"{iso}: {int(qid.eq('').sum())} rows with data but no queue id")
    n = qid.groupby(qid).cumcount() + 1
    dup = qid.duplicated(keep=False)
    eid = f"{iso}_queue:" + qid
    eid[dup] = eid[dup] + ":" + n[dup].astype(str)
    if dup.any():
        log(f"  {int(dup.sum())} rows share {qid[dup].nunique()} queue ids; ids get :<n> in the ISO's row order")
    iso_status = text(df["Status (Original)"]) if iso == "spp" else text(df["Status"])
    unknown = sorted(set(iso_status) - set(STATUS_MAP[iso]) - {""})
    if unknown:
        raise RuntimeError(f"{iso}: status value(s) not in STATUS_MAP: {unknown}")
    if iso_status.eq("").any():
        # the ISO lists the position with no status (SPP: affected-system ASGI requests);
        # status stays empty rather than guessed
        log(f"  {int(iso_status.eq('').sum())} rows have no status in the ISO's file; status left empty, e.g. "
            f"{qid[iso_status.eq('')].head(5).tolist()}")
    status = iso_status.map(STATUS_MAP[iso]).fillna("")
    cap = pd.to_numeric(text(df["Capacity (MW)"]).replace("", None), errors="coerce")
    bad = text(df["Capacity (MW)"])[cap.isna() & text(df["Capacity (MW)"]).ne("")]
    if len(bad):
        raise RuntimeError(f"{iso}: non-numeric capacity {bad.unique()[:5].tolist()}")
    state = text(pick(df, "State"))
    state = state.map(lambda s: STATES.get(s, s))
    geo = state.map(lambda s: f"US-{s}" if re.fullmatch(r"[A-Z]{2}", s) else "")
    withdrawn = dates(pick(df, "Withdrawn Date"), "withdrawn date", iso)
    actual = dates(pick(df, "Actual Completion Date", "In-Service Date", "Op Date"), "in-service date", iso) \
        if iso != "spp" else dates(pick(df, "Commercial Operation Date"), "in-service date", iso)
    status_date = pd.Series("", index=df.index)
    status_date[status == "withdrawn"] = withdrawn[status == "withdrawn"]
    status_date[status == "completed"] = actual[status == "completed"]
    out = pd.DataFrame({
        "entity_id": eid, "entity_type": "project", "name": text(pick(df, "Project Name")),
        "geo": geo, "lat": "", "lon": "",
        "capacity_mw": cap.map(lambda v: "" if pd.isna(v) else repr(float(v))),
        "status": status, "status_date": status_date,
        "operator": text(pick(df, "Interconnecting Entity")), "source": f"{iso}:interconnection_queue",
        "source_url": url, "retrieved_at": got, "vintage": got[:10],
        "queue_id": qid, "county": text(pick(df, "County")), "state": state,
        "poi": text(pick(df, "Interconnection Location")),
        "zone": text(pick(df, "Zone", "Z")),
        "transmission_owner": text(pick(df, "Transmission Owner")),
        "fuel_technology": text(pick(df, "Generation Type")),
        "iso_status": iso_status,
        "queue_date": dates(pick(df, "Queue Date"), "queue date", iso),
        "proposed_in_service_date": dates(pick(df, "Proposed Completion Date"), "proposed date", iso),
        "actual_in_service_date": actual, "withdrawn_date": withdrawn,
    })
    log(f"  {len(out)} queue positions: " + ", ".join(f"{k} {v}" for k, v in status.value_counts().items()))
    return out[ENTITY_COLS + EXTRA_COLS]


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW ISO interconnection queues (entities)")
    ap.add_argument("isos", nargs="*", default=[])
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    bad = [i for i in args.isos if i not in ISOS]
    if bad:
        ap.error(f"unknown ISO(s) {bad}; choose from {sorted(ISOS)}")
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"iso_queues_{run_id}.log"))
    ip.RAW.open("iso_queues", run_id)
    results, reg = [], []
    todo = args.isos or [i for i in ISOS if i != "pjm"] + ["pjm"]
    for iso in todo:
        cfg, name = ISOS[iso], f"{iso}_interconnection_queue"
        try:
            if iso == "pjm":
                key = ip.load_key("PJM_API_KEY", log)
                if not key:
                    log("pjm: PJM_API_KEY is empty; PJM queue skipped")
                    print("iso_queues pjm skipped: no PJM_API_KEY")
                    continue
            log(f"{name}: gridstatus {cfg['cls']}.get_interconnection_queue()")
            with ip.RAW.collect() as recs:
                obj = getattr(gridstatus, cfg["cls"])(api_key=key) if iso == "pjm" else getattr(gridstatus, cfg["cls"])()
                df = ip.with_retries(f"{iso} queue", obj.get_interconnection_queue, log)
            data = [r for r in recs if re.search(cfg["data"], r["url"], re.I) and str(r["status"]).startswith("2")]
            if not data:
                raise RuntimeError(f"{iso}: no captured response matches {cfg['data']!r}; cannot cite the file")
            url = data[-1]["url"]
            got = ip.utc_iso(data[-1]["retrieved_at"])
            for r in recs:
                log(f"  fetched {r['status']} {r['url']} -> raw {r['file']}")
            out = build(iso, df, url, got, log)
            header = [
                f"Energy Research Warehouse (ERW): {cfg['label']} interconnection queue",
                "Shape: entities (docs/datastandard.md v0). One row per queue position; entity_type project; "
                "status harmonized (active, withdrawn, completed, suspended), iso_status the ISO's own.",
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/iso_queues.py via gridstatus "
                f"{gridstatus.__version__} {cfg['cls']}.get_interconnection_queue",
                f"Run log: warehouse/output/logs/iso_queues_{run_id}.log",
                f"Raw files: warehouse/raw/iso_queues/{run_id}/ (not in git)",
                f"Source: {iso}:interconnection_queue {cfg['label']} {cfg['report']}, {url}",
                f"  report page: {cfg['page']}",
                "capacity_mw: the ISO's requested capacity as gridstatus reads it (MISO: the larger of "
                "summer and winter net MW). Dates are the ISO's, YYYY-MM-DD.",
                "Snapshot: the table holds the queue as retrieved; the next run replaces it.",
                "License: " + ("internal. PJM data terms bar non-members from republishing." if iso == "pjm"
                               else "public (ISO public queue report)."),
            ]
            ip.write_snapshot(out, name, header, log, ENTITY_COLS + EXTRA_COLS)
            reg.append(dict(source=f"{iso}:interconnection_queue", publisher=PUBLISHERS[iso],
                            report=f"{cfg['report']}", report_url=cfg["page"], document_list=cfg["page"],
                            tables=[name]))
            results.append(dict(table=name, market="queue", status="ok", detail=""))
        except Exception:
            tb = ip.redact(traceback.format_exc())
            last = tb.strip().splitlines()[-1]
            log(f"{name} FAILED, no output file written:\n{tb}")
            print(f"iso_queues {iso} FAILED, no output file written: {last}", file=sys.stderr)
            results.append(dict(table=name, market="queue", status="failed", detail=last[:300]))
    if reg:
        ip.update_sources(reg)
    ip.write_status("iso_queues", run_id, results)
    failures = sum(r["status"] != "ok" for r in results)
    log(f"done, failures={failures}")
    log.close()
    print(f"iso_queues run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
