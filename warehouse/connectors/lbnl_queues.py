#!/usr/bin/env python3
"""Berkeley Lab's "Queued Up" interconnection queue dataset (session 62, approved pull, ceiling 100,000 rows).

Energy Research Warehouse (ERW) connector. Writes one entities table, history (not in the Supabase live set):

    warehouse/output/lbnl_interconnection_queue.csv   one row per interconnection request in the Queued Up data file

The source: Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition, data file through the end
of 2025 (sheet "03. Complete Queue Data"; the codebook is sheet "04. Data Codebook"), from
https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics. License CC BY 4.0: "You may use,
share, or adapt the dataset as long as you attribute it to Lawrence Berkeley National Laboratory and GridTracker."
Copyright (c) 2026, The Regents of the University of California, through Lawrence Berkeley National Laboratory &
GridTracker. (emp.lbl.gov answers automated requests with HTTP 403; the same file is published on eta-publications.lbl.gov.)

    python warehouse/connectors/lbnl_queues.py

Resumable: a file an earlier run saved (warehouse/raw/lbnl_queues/*/manifest.csv, status 200, an xlsx) is read, not
downloaded again. Every row keeps Berkeley Lab's own fields (q_status, IA_phase_clean, dates, region, entity, type,
MW); status maps q_status to the ERW vocabulary (active, withdrawn, suspended, operational to operating), and a value
outside that map fails the run. capacity_mw is mw_1 plus mw_2 plus mw_3, as Berkeley Lab adds them for a hybrid request.
"""

import datetime as dt
import glob
import os
import sys
import traceback

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "lbnl_interconnection_queue"
URL = "https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx"
PAGE = "https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics"
SOURCE = "lbnl:queued_up"
SHEET = "03. Complete Queue Data"
CEILING = 100_000
STATUS = {"active": "active", "withdrawn": "withdrawn", "suspended": "suspended", "operational": "operating", "unknown": ""}  # unknown: no ERW status; q_status keeps it
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source"]
EXTRA = ["source_url", "retrieved_at", "vintage", "q_id", "q_status", "q_date", "prop_date", "on_date", "wd_date", "ia_date",
         "ia_phase", "region", "lbnl_entity", "utility", "state", "county", "fips_code", "poi_name", "service", "project_type",
         "type_clean", "type_1", "type_2", "type_3", "mw_1", "mw_2", "mw_3", "q_year", "prop_year"]
LICENSE_LINE = ("License: CC BY 4.0 (Berkeley Lab: \"The Queued Up data file is licensed CC BY 4.0... You may use, share, or adapt the "
                "dataset as long as you attribute it to Lawrence Berkeley National Laboratory and GridTracker.\") Copyright (c) 2026, "
                "The Regents of the University of California, through Lawrence Berkeley National Laboratory & GridTracker.")


def saved():
    """(path, retrieved_at, last_modified) of a file an earlier run saved, or None."""
    for man in sorted(glob.glob(os.path.join(ip.RAW_DIR, "lbnl_queues", "*", "manifest.csv")), reverse=True):
        m = pd.read_csv(man, dtype=str, keep_default_na=False)
        hit = m[(m["url"] == URL) & (m["status"] == "200")]
        for _, r in hit.iloc[::-1].iterrows():
            f = os.path.join(os.path.dirname(man), r["file"])
            if os.path.exists(f) and open(f, "rb").read(2) == b"PK":
                return f, r["retrieved_at"], r.get("last_modified", "")
    return None


def day(v):
    if v is None or (isinstance(v, float) and pd.isna(v)) or v == "":
        return ""
    t = pd.to_datetime(v, errors="coerce")
    return "" if pd.isna(t) else t.strftime("%Y-%m-%d")


def num(v):
    x = pd.to_numeric(v, errors="coerce")
    return "" if pd.isna(x) else repr(float(x))


def main():
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"lbnl_queues_{run_id}.log"))
    results = []
    try:
        got = saved()
        if got:
            path, retrieved, lm = got
            log(f"reading the file an earlier run saved: {os.path.relpath(path, ip.ROOT)} (retrieved {retrieved})")
        else:
            ip.RAW.open("lbnl_queues", run_id)
            r = ip.with_retries("LBNL data file", lambda: requests.get(URL, timeout=600), log)
            if r.status_code != 200 or r.content[:2] != b"PK":
                raise RuntimeError(f"LBNL data file: HTTP {r.status_code}, not an xlsx")
            got = saved()
            if not got:
                raise RuntimeError("the download was not saved under warehouse/raw/lbnl_queues/")
            path, retrieved, lm = got
            log(f"downloaded {len(r.content):,} bytes, last modified {r.headers.get('last-modified')}")
        df = pd.read_excel(path, sheet_name=SHEET, header=1, dtype=object)
        df = df[df["q_id"].notna() | df["entity"].notna()]
        log(f"{SHEET}: {len(df):,} requests")
        if len(df) > CEILING:
            raise RuntimeError(f"{len(df):,} rows, over the {CEILING:,} ceiling: nothing written")
        unknown = sorted(set(df["q_status"].dropna().astype(str).str.strip().str.lower()) - set(STATUS))
        if unknown:
            raise RuntimeError(f"q_status value(s) not mapped: {unknown}")
        # text as one line: Excel's escaped carriage return (_x000D_) and line breaks become spaces (five PSE queue ids hold them)
        txt = lambda c: df[c].map(lambda v: "" if v is None or (isinstance(v, float) and pd.isna(v)) else  # noqa: E731
                                  " ".join(str(v).replace("_x000D_", " ").split()))
        qid, ent = txt("q_id"), txt("entity")
        eid = "lbnl:" + ent + ":" + qid
        # a few q_id repeat within an entity (Berkeley Lab: combine q_id with entity); the row number keeps them apart
        dup = eid.duplicated(keep=False)
        eid = eid.where(~dup, eid + ":" + (df.reset_index().index + 1).astype(str).to_numpy())
        status = txt("q_status").str.lower().map(STATUS)
        sdate = df.apply(lambda r: day(r["on_date"]) if str(r["q_status"]).lower() == "operational" else
                         day(r["wd_date"]) if str(r["q_status"]).lower() == "withdrawn" else day(r["q_date"]), axis=1)
        mw = df[["mw_1", "mw_2", "mw_3"]].apply(pd.to_numeric, errors="coerce").sum(axis=1, min_count=1)
        state = txt("state")
        out = pd.DataFrame({
            "entity_id": eid, "entity_type": "project", "name": txt("project_name").where(txt("project_name") != "", qid),
            "geo": state.map(lambda s: f"US-{s}" if len(s) == 2 and s.isalpha() else ""), "lat": "", "lon": "",
            "capacity_mw": mw.map(lambda v: "" if pd.isna(v) else repr(float(v))), "status": status, "status_date": sdate,
            "operator": txt("utility"), "source": SOURCE, "source_url": URL, "retrieved_at": retrieved, "vintage": "2026 edition (through 2025)",
            "q_id": qid, "q_status": txt("q_status"), "q_date": df["q_date"].map(day), "prop_date": df["prop_date"].map(day),
            "on_date": df["on_date"].map(day), "wd_date": df["wd_date"].map(day), "ia_date": df["ia_date"].map(day),
            "ia_phase": txt("IA_phase_clean"), "region": txt("region"), "lbnl_entity": ent, "utility": txt("utility"), "state": state,
            "county": txt("county"), "fips_code": txt("fips_code").str.replace(r"\.0$", "", regex=True), "poi_name": txt("poi_name"),
            "service": txt("service"), "project_type": txt("project_type"), "type_clean": txt("type_clean"), "type_1": txt("type_1"),
            "type_2": txt("type_2"), "type_3": txt("type_3"), "mw_1": df["mw_1"].map(num), "mw_2": df["mw_2"].map(num),
            "mw_3": df["mw_3"].map(num), "q_year": txt("q_year").str.replace(r"\.0$", "", regex=True),
            "prop_year": txt("prop_year").str.replace(r"\.0$", "", regex=True)})
        header = [
            "Energy Research Warehouse (ERW): U.S. interconnection queue requests, Berkeley Lab's Queued Up data file (session 62)",
            "Shape: entities (docs/datastandard.md v0). One row per interconnection request; entity_type project; entity_id "
            "lbnl:<transmission provider entity>:<queue id> (a repeated pair takes its row number); status from q_status (operational is "
            "operating); status_date the online date (operating), the withdrawal date (withdrawn) or the request date; capacity_mw "
            "mw_1 + mw_2 + mw_3; Berkeley Lab's own fields after (ia_phase is IA_phase_clean, lbnl_entity is entity).",
            f"Rows: {len(out):,} of the {CEILING:,}-row ceiling; requests through the end of 2025; the 7 ISOs, West and Southeast (non-ISO).",
            f"Retrieved: {retrieved} (UTC) from {URL} (Last-Modified {lm or 'not given'}); written by warehouse/connectors/lbnl_queues.py, run {run_id}",
            f"Run log: warehouse/output/logs/lbnl_queues_{run_id}.log",
            f"Raw files: {os.path.relpath(os.path.dirname(path), ip.ROOT)}/ (not in git)",
            f"Source: {SOURCE} Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file, {PAGE}",
            LICENSE_LINE,
        ]
        ip.write_snapshot(out, NAME, header, log, ENTITY_COLS + EXTRA)
        ip.update_sources([dict(source=SOURCE, publisher="Lawrence Berkeley National Laboratory and GridTracker",
                                report="Queued Up: 2026 Edition, data file (requests through 2025)", report_url=PAGE, document_list=URL,
                                license="public", tables=[NAME])])
        msg = f"{len(out):,} requests; {int((status == 'active').sum()):,} active"
        log(msg)
        print(f"lbnl_queues: {msg}")
        results.append(dict(table=NAME, market="all", status="ok", detail=msg))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"lbnl_queues FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("lbnl_queues", run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
