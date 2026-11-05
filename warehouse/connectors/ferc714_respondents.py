#!/usr/bin/env python3
"""FERC Form 714's respondents: each planning area's filer, with FERC's and EIA's ids (session 514).

Energy Research Warehouse (ERW) connector. One entities table, warehouse/output/ferc714_respondents.csv, from Catalyst
Cooperative's Public Utility Data Liberation project (PUDL), stable release, table core_ferc714__respondent_id (FERC's
filings as filed; FERC's own site refuses automated requests, session 484):

    https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/core_ferc714__respondent_id.parquet

    entity_id     ferc714:<PUDL's respondent id>, the entity of ferc714_area_demand_<year>
    entity_type   utility; name the respondent's name as filed; geo US
    the rest      respondent_id_ferc714_csv (FERC's id in its CSV years, to 2020), respondent_id_ferc714_xbrl (its id in
                  the XBRL years, 2021 on), eia_code (the respondent's EIA utility code, blank where PUDL has none)

Values as PUDL publishes them; a blank stays blank; an id given twice stops the run. The file is the one session 484's
connector saved (warehouse/raw/ferc714_demand/), reused; it is asked again only when it is not there.

    python warehouse/connectors/ferc714_respondents.py

Ceiling: one request a run. License: internal until a person rules, as ferc714_area_demand_* (PUDL's CC-BY-4.0, read as
record 85; FERC's own terms page could not be read).
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

NAME = "ferc714_respondents"
CONNECTOR = "ferc714_respondents"
RAW_CONNECTOR = "ferc714_demand"   # session 484's connector saved the file
SOURCE = "pudl:core_ferc714__respondent_id"
URL = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/core_ferc714__respondent_id.parquet"
PAGE = "https://docs.catalyst.coop/pudl/en/stable/data_sources/ferc714.html"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
ENTITY_COLS = ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator",
               "source", "source_url", "retrieved_at", "vintage"]
EXTRA_COLS = ["respondent_id_ferc714", "respondent_id_ferc714_csv", "respondent_id_ferc714_xbrl", "eia_code"]


def text(v):
    """A cell as text; the column is read as pandas' string type first, so a whole number with a blank beside it stays
    "200", never "200.0"."""
    return "" if pd.isna(v) else str(v).strip()


def respondents(d, url, retrieved, vintage):
    need = ["respondent_id_ferc714", "respondent_id_ferc714_csv", "respondent_id_ferc714_xbrl", "respondent_name_ferc714", "eia_code"]
    missing = [c for c in need if c not in d.columns]
    if missing:
        raise RuntimeError(f"the file lacks {missing}")
    if d["respondent_id_ferc714"].isna().any():
        raise RuntimeError("a respondent with no id")
    ids = d["respondent_id_ferc714"].astype(int)
    if ids.duplicated().any():
        raise RuntimeError(f"a respondent id given twice: {sorted(ids[ids.duplicated()])[:5]}")
    return pd.DataFrame({
        "entity_id": "ferc714:" + ids.astype(str), "entity_type": "utility", "name": d["respondent_name_ferc714"].astype("string").map(text),
        "geo": "US", "lat": None, "lon": None, "capacity_mw": None, "status": "", "status_date": "", "operator": "",
        "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": vintage,
        "respondent_id_ferc714": ids.astype(str), "respondent_id_ferc714_csv": d["respondent_id_ferc714_csv"].astype("string").map(text),
        "respondent_id_ferc714_xbrl": d["respondent_id_ferc714_xbrl"].astype("string").map(text), "eia_code": d["eia_code"].astype("string").map(text),
    }).sort_values("respondent_id_ferc714", key=lambda s: s.astype(int)).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="FERC Form 714's respondents, from PUDL")
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
        hit = ip.raw_cached(RAW_CONNECTOR, URL)
        content, rec = hit if hit else ip.fetch_raw(CONNECTOR, URL, log, headers=UA)
        log(("  raw file reused from warehouse/raw/ferc714_demand/: " if hit else "  fetched: ") + URL)
        lm = rec.get("last_modified") or ""
        vintage = ip.utc_iso(pd.Timestamp(lm)) if lm else ""
        retrieved = rec.get("retrieved_at") or ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        t = respondents(pd.read_parquet(io.BytesIO(content)), URL, retrieved, vintage)
        with_eia = int((t["eia_code"] != "").sum())
        header = [
            "Energy Research Warehouse (ERW): FERC Form 714's respondents, each planning area's filer with FERC's and EIA's ids (session 514)",
            "Shape: entities (docs/datastandard.md v0). entity_id ferc714:<PUDL's respondent id> (the entity of ferc714_area_demand_<year>); entity_type utility; "
            "respondent_id_ferc714_csv FERC's id to 2020, respondent_id_ferc714_xbrl from 2021, eia_code the EIA utility code.",
            f"Respondents: {len(t)}; with an EIA code: {with_eia}. Values as PUDL publishes them; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ferc714_respondents.py; the file's Last-Modified {lm or 'not given'}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            "Raw files: warehouse/raw/ferc714_demand/ (not in git)",
            f"Source: {SOURCE} Catalyst Cooperative (PUDL), from FERC Form 714: respondent ids (stable release), {URL}",
            "License: internal (PUDL's data are CC-BY-4.0; FERC's own terms page could not be read; held internal until a person rules, as ferc714_area_demand_*).",
        ]
        ip.write_snapshot(t, NAME, header, log, cols=ENTITY_COLS + EXTRA_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Catalyst Cooperative (PUDL), from FERC Form 714",
                                    report="FERC Form 714 respondent ids (PUDL core table, stable release)", report_url=PAGE,
                                    document_list=URL, license="internal", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} respondents"))
        print(f"{NAME}: {len(t)} respondents, {with_eia} with an EIA code")
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
