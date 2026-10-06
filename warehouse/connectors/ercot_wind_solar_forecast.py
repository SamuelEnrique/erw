#!/usr/bin/env python3
"""ERCOT wind and solar: the forecast a day ahead and the actual output, hourly (session 133, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ercot_wind_solar_forecast.csv, from
ERCOT's two public hourly reports, each posted once an hour and each holding about two days of actual output behind it
and a week of forecast ahead of it:

    NP4-732-CD  Wind Power Production, Hourly Averaged Actual and Forecasted Values   (report type 13028)
    NP4-745-CD  Solar Power Production, Hourly Averaged Actual and Forecasted Values  (report type 13483)

    entity    ercot:SYSTEM (ERCOT's system-wide columns)
    variable  wind_actual_mw, solar_actual_mw         ERCOT's SYSTEM_WIDE_GEN for the hour, from the newest posting that holds it
              wind_forecast_24h_mw, solar_forecast_24h_mw
                                                      ERCOT's short-term forecast for the hour (STWPF for wind, STPPF for
                                                      solar) from the newest posting published at least 24 hours before
                                                      the hour began: the forecast as it stood a day ahead
    freq      PT1H; ts_utc is the hour's start (ERCOT's DELIVERY_DATE and HOUR_ENDING are Central time)

    python warehouse/connectors/ercot_wind_solar_forecast.py [--out-dir DIR]

ERCOT's public list keeps about a week of postings, so one run yields about five days in which an hour has both its
actual and a forecast made a day before. Rows are merged on (entity, variable, ts_utc): run daily, the table grows by
a day a day and never loses one. An hour with no posting a day ahead of it has no forecast row. Nothing is filled.

Ceiling: 2,000,000 rows for session 133's forecast pulls in all (CAISO and ERCOT); one run reads about 75,000 rows of
ERCOT's files. The run stops if the rows read would pass 200,000. License: public (ERCOT's public market
information; cite "ERCOT").
"""

import argparse
import datetime as dt
import io
import os
import sys
import time
import traceback
import zipfile

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ercot_wind_solar_forecast"
CONNECTOR = "ercot_wind_solar_forecast"
LIST = "https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId={}"
DOC = "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId={}"
TZ = "America/Chicago"
CEILING = 200_000
LEAD = pd.Timedelta(hours=24)
UA = {"User-Agent": "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)"}
# what: (report type, ERCOT's id, its forecast column, its page)
REPORTS = {
    "wind": (13028, "NP4-732-CD", "STWPF_SYSTEM_WIDE", "https://www.ercot.com/mp/data-products/data-product-details?id=NP4-732-CD"),
    "solar": (13483, "NP4-745-CD", "STPPF_SYSTEM_WIDE", "https://www.ercot.com/mp/data-products/data-product-details?id=NP4-745-CD"),
}


def hour_starts(d):
    """The UTC start of each row's hour, from ERCOT's DELIVERY_DATE (Central) and HOUR_ENDING; the repeated hour of the
    autumn clock change is told apart by DSTFlag."""
    day = pd.to_datetime(d["DELIVERY_DATE"], format="%m/%d/%Y")
    local = day + pd.to_timedelta(pd.to_numeric(d["HOUR_ENDING"]) - 1, unit="h")
    second = d["DSTFlag"].astype(str).str.upper().eq("Y") if "DSTFlag" in d else pd.Series(False, index=d.index)
    return local.dt.tz_localize(TZ, ambiguous=(~second).to_numpy(), nonexistent="NaT").dt.tz_convert("UTC")


def pairs(postings, forecast_col):
    """From the postings of one report, [(published UTC, frame)], each hour's actual (the newest posting that holds it)
    and its forecast from the newest posting published at least LEAD before the hour began. Returns two Series by UTC hour."""
    actual, forecast = {}, {}
    for published, d in sorted(postings, key=lambda p: p[0]):
        ts = hour_starts(d)
        gen = pd.to_numeric(d["SYSTEM_WIDE_GEN"], errors="coerce")
        fc = pd.to_numeric(d[forecast_col], errors="coerce")
        for t, g, f in zip(ts, gen, fc):
            if pd.isna(t):
                continue
            if pd.notna(g):
                actual[t] = float(g)                      # a later posting replaces an earlier one's value for the hour
            if pd.notna(f) and published <= t - LEAD:
                forecast[t] = float(f)                    # the newest posting still a day ahead of the hour
    return pd.Series(actual, dtype=float), pd.Series(forecast, dtype=float)


def rows(what, actual, forecast, source, url, retrieved):
    out = []
    for variable, s in ((f"{what}_actual_mw", actual), (f"{what}_forecast_24h_mw", forecast)):
        for t, v in s.items():
            out.append(dict(entity="ercot:SYSTEM", variable=variable, ts_utc=t.strftime("%Y-%m-%dT%H:%M:%SZ"), value=round(v, 4), unit="MW", freq="PT1H", geo="US-TX",
                            market="", node="SYSTEM", source=source, source_url=url, retrieved_at=retrieved, vintage=""))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERCOT wind and solar: forecast a day ahead and actual output, hourly")
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
        out, read, notes, sources = [], 0, [], []
        for what, (rid, report, col, page) in REPORTS.items():
            listing = ip.with_retries(f"ERCOT list {report}", lambda: requests.get(LIST.format(rid), timeout=90, headers=UA), log)
            docs = [x["Document"] for x in listing.json()["ListDocsByRptTypeRes"]["DocumentList"] if "csv" in x["Document"]["FriendlyName"].lower()]
            postings = []
            for doc in docs:
                url = DOC.format(doc["DocID"])
                content, _ = ip.fetch_raw(CONNECTOR, url, log, headers=UA, pause=0.15)
                z = zipfile.ZipFile(io.BytesIO(content))
                d = pd.read_csv(z.open(z.namelist()[0]))
                if not {"DELIVERY_DATE", "HOUR_ENDING", "SYSTEM_WIDE_GEN", col} <= set(d.columns):
                    raise RuntimeError(f"{report} {doc['ConstructedName']}: columns {list(d.columns)[:8]}")
                read += len(d)
                if read > CEILING:
                    raise RuntimeError(f"{read:,} rows read, over the ceiling of {CEILING:,}: nothing written")
                postings.append((pd.Timestamp(doc["PublishDate"]).tz_convert("UTC"), d))
            actual, forecast = pairs(postings, col)
            both = actual.index.intersection(forecast.index)
            source = f"ercot:{report}"
            out += rows(what, actual, forecast, source, LIST.format(rid), ip.utc_iso(pd.Timestamp.now(tz="UTC")))
            sources.append((source, report, page, rid))
            notes.append(f"{what}: {len(postings)} postings, {len(actual)} hours of actual, {len(forecast)} of forecast, {len(both)} with both")
            log("  " + notes[-1])
            time.sleep(1)
        s = pd.DataFrame(out, columns=ip.SERIES_COLS)
        if s.empty:
            raise RuntimeError("ERCOT's postings held no hour")
        header = [
            "Energy Research Warehouse (ERW): ERCOT wind and solar, the forecast a day ahead and the actual output, hourly, system-wide (session 133)",
            "Shape: series (docs/datastandard.md v0). freq PT1H; ts_utc is the hour's start. wind_actual_mw and solar_actual_mw: ERCOT's SYSTEM_WIDE_GEN, from the newest posting that holds the hour. "
            "wind_forecast_24h_mw and solar_forecast_24h_mw: ERCOT's short-term forecast (STWPF, STPPF) for the hour from the newest posting published at least 24 hours before the hour began. MW.",
            "This run: " + "; ".join(notes) + ". ERCOT's public list keeps about a week of hourly postings; the table keeps every hour earlier runs wrote.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_wind_solar_forecast.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
        ]
        for source, report, page, rid in sources:
            header.append(f"Source: {source} ERCOT, {report}, {page}")
            header.append(f"  access: {LIST.format(rid)} and {DOC.format('<DocID>')}")
        header += [f"Rows read: {read:,} of ERCOT's files (the session's forecast pulls share a ceiling of 2,000,000). An hour with no posting a day ahead of it has no forecast row. Nothing is filled.",
                   'License: public (ERCOT public market information; cite "ERCOT").']
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        if not args.out_dir:
            ip.update_sources([dict(source=source, publisher="Electric Reliability Council of Texas (ERCOT)", report=f"{report}: hourly averaged actual and forecasted values",
                                    report_url=page, document_list=LIST.format(rid), license="public", tables=[NAME]) for source, report, page, rid in sources])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows; {read:,} read"))
        print(f"{NAME}: {len(s):,} rows, {s['ts_utc'].min()[:13]} to {s['ts_utc'].max()[:13]}; {'; '.join(notes)}; {read:,} rows read")
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
