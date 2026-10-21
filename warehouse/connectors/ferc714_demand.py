#!/usr/bin/env python3
"""FERC Form 714: hourly demand by planning area, by year (session 484, the owner's instruction of 21 October 2026).

Energy Research Warehouse (ERW) connector. Yearly series tables, warehouse/output/ferc714_area_demand_<year>.csv, from
FERC Form 714 Part III, Schedule 2a (each planning area's hourly demand, filed once a year), as Catalyst Cooperative's
Public Utility Data Liberation project (PUDL) publishes it: the table core_ferc714__hourly_planning_area_demand of
its stable release, one parquet file on its public AWS bucket. FERC's own pages answer automated requests with
HTTP 403 (Cloudflare, session 484; session 311 met the same on its terms page), so FERC's data are taken from PUDL,
never by working around FERC's protection.

    https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/core_ferc714__hourly_planning_area_demand.parquet
    https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/core_ferc714__respondent_id.parquet

    entity    ferc714:<respondent_id_ferc714>, PUDL's id linking FERC's CSV (to 2020) and XBRL (from 2021) respondent ids
    variable  demand: the planning area's demand over the hour, MW (PUDL's demand_mwh: an hour's MWh is its mean MW)
    ts_utc    the START of the hour: PUDL's datetime_utc marks the hour's end (form hour 1 is T01; T24 and the day's last
              second are T00 of the next day, PUDL's cleaning). Checked against ERCOT's own system load for 2025
              (respondent 58, 8,759 hours): one hour earlier the mean difference is 1,184 MW on a mean of 55,734, as
              stamped 2,717 MW, an hour later 4,176 MW
    node      the respondent's name as PUDL's respondent table gives it; geo US; freq PT1H

Only the core table: PUDL's out_ferc714__hourly_planning_area_demand fills missing and anomalous hours by imputation,
which the ERW never takes (CLAUDE.md, real data only). Values are as filed, negatives included (an area can export
more than it serves); a respondent's missing hour is absent, never filled.

    python warehouse/connectors/ferc714_demand.py                   # 2023 to the latest whole year
    python warehouse/connectors/ferc714_demand.py --from 2019 --to 2022

Ceiling: the two files (two requests a run; a file already in warehouse/raw/ferc714_demand/ is reused). License:
internal until a person rules: PUDL's data are CC-BY-4.0 (read 21 October 2026, record 85 of license_reads.csv) and
FERC's filings a work of the U.S. government, but FERC's own terms page could not be read (HTTP 403).
"""

import argparse
import datetime as dt
import email.utils
import io
import os
import sys
import traceback

import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "ferc714_demand"
SOURCE = "pudl:core_ferc714__hourly_planning_area_demand"
PAGE = "https://docs.catalyst.coop/pudl/en/stable/data_sources/ferc714.html"
BUCKET = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/"
DEMAND = BUCKET + "core_ferc714__hourly_planning_area_demand.parquet"
RESPONDENTS = BUCKET + "core_ferc714__respondent_id.parquet"
FIRST_DEFAULT = 2023
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
LICENSE = "internal"


def table_name(year):
    return f"ferc714_area_demand_{year}"


def rows(demand, respondents, year, url, retrieved, vintage):
    """One year of PUDL's core table as the ERW's series rows: the hour's start in UTC, the respondent's name as node."""
    d = demand[demand["start"].dt.year == year]
    if d.duplicated(["respondent_id_ferc714", "start"]).any():
        raise RuntimeError(f"{year}: a respondent's hour is given twice")
    names = dict(zip(respondents["respondent_id_ferc714"], respondents["respondent_name_ferc714"].fillna("")))
    rid = d["respondent_id_ferc714"].astype(int)
    return pd.DataFrame({
        "entity": "ferc714:" + rid.astype(str), "variable": "demand", "ts_utc": d["start"].dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "value": d["demand_mwh"].astype(float), "unit": "MW", "freq": "PT1H", "geo": "US", "market": "",
        "node": rid.map(names).fillna(""), "source": SOURCE, "source_url": url, "retrieved_at": retrieved, "vintage": vintage,
    }).sort_values(["entity", "ts_utc"], kind="stable").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="FERC Form 714 hourly demand by planning area, by year (from PUDL)")
    ap.add_argument("--from", dest="first", type=int, default=FIRST_DEFAULT)
    ap.add_argument("--to", dest="last", type=int, help="the last year (default: the latest whole year in the file)")
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
    try:
        content, rec = ip.fetch_raw(CONNECTOR, DEMAND, log, headers=UA, timeout=600)
        rcontent, _ = ip.fetch_raw(CONNECTOR, RESPONDENTS, log, headers=UA)
        lm = rec.get("last_modified") or ""  # the stable release's file time (Last-Modified), as the vintage
        vintage = email.utils.parsedate_to_datetime(lm).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if lm else ""
        demand = pq.read_table(io.BytesIO(content), columns=["respondent_id_ferc714", "datetime_utc", "demand_mwh"]).to_pandas()
        demand["start"] = pd.to_datetime(demand["datetime_utc"]) - pd.Timedelta(hours=1)
        respondents = pq.read_table(io.BytesIO(rcontent)).to_pandas()
        whole = sorted(y for y, n in demand["start"].dt.year.value_counts().items() if n > 100_000)
        last = args.last or max(whole)
        for year in range(args.first, last + 1):
            name = table_name(year)
            s = rows(demand, respondents, year, DEMAND, rec["retrieved_at"], vintage)
            per = s.groupby("entity").size()
            header = [
                f"Energy Research Warehouse (ERW): FERC Form 714 hourly demand by planning area, {year} (session 484)",
                "Shape: series (docs/datastandard.md v0). demand: the planning area's demand over the hour in MW, as filed on FERC Form 714 Part III Schedule 2a; ts_utc is the hour's start (PUDL's datetime_utc, the hour's end, less one hour); node is the respondent's name; freq PT1H.",
                f"Respondents: {per.size}; hours a respondent from {per.min():,} to {per.max():,} (a year has {8784 if year % 4 == 0 else 8760}). A missing hour is absent: nothing is filled. PUDL's imputed table (out_ferc714__...) is not used.",
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/ferc714_demand.py",
                f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
                f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
                f"Source: {SOURCE} Catalyst Cooperative, PUDL: FERC Form 714 hourly planning area demand (core table, stable release), {PAGE}",
                f"  access: {DEMAND} and {RESPONDENTS}",
                "  original: Federal Energy Regulatory Commission (FERC), Form 714 Annual Electric Balancing Authority Area and Planning Area Report, Part III Schedule 2a",
                f"License: {LICENSE} (PUDL's data CC-BY-4.0: cite Catalyst Cooperative, PUDL; FERC's filings a U.S. government work; FERC's own terms page unread, HTTP 403: a person rules on public).",
            ]
            ip.write_snapshot(s[ip.SERIES_COLS], name, header, log, ip.SERIES_COLS)
            results.append(dict(table=name, market="all", status="ok", detail=f"{len(s):,} rows, {per.size} respondents"))
            log(f"  {name}: {len(s):,} rows, {per.size} respondents")
            print(f"{name}: {len(s):,} rows, {per.size} respondents, {s['ts_utc'].min()} to {s['ts_utc'].max()}")
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="Catalyst Cooperative (PUDL), from FERC Form 714",
                                    report="FERC Form 714 hourly planning area demand (PUDL core table, stable release)",
                                    report_url=PAGE, document_list=BUCKET, license=LICENSE,
                                    tables=[r["table"] for r in results])])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=table_name(args.first), market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
