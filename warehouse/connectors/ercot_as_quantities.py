#!/usr/bin/env python3
"""ERCOT ancillary service quantities: the DAM Ancillary Service Plan, MW by product and hour (session 74).

Energy Research Warehouse (ERW) connector. Writes one series table, warehouse/output/ercot_as_quantities.csv:

    entity    ercot:<service as ERCOT names it>   ercot:REGUP, ercot:REGDN, ercot:RRS, ercot:NSPIN, ercot:ECRS
    variable  quantity_mw_plan   the MW ERCOT plans to procure in the day-ahead market for the hour (NP4-33-CD)
    unit      MW
    freq      PT1H; ts_utc is the start of the delivery hour, UTC
    market    ercot_dam
    node      the service

    python warehouse/connectors/ercot_as_quantities.py

Source: NP4-33-CD, DAM Ancillary Service Plan, on ERCOT's public reports site (the route ercot_as_prices.py uses):
one CSV a day, published about 05:00 Central, each holding the plan for the next seven delivery days. A delivery day's
quantities are taken from the file published on the day before it, the plan the day-ahead market for that day used;
a day without that file is left out and counted, never taken from another publication.

What this can and cannot hold. ERCOT's public reports site keeps about the last month of NP4-33-CD; the session 74
prompt asked for 2018 to today, and no keyless public source of the history was found (ERCOT's archive API needs a
subscription key; the yearly methodology documents give rules and adjustment tables, not the quantities). So the table
holds what the site holds, and grows by a day each run if the connector is scheduled; 2018 to the start is not held.

Never fill. A (service, delivery day) is written only when every hour of the Central day is there exactly once (24, or
23 and 25 at the clock changes). Ceiling: 400,000 rows (session 74's approved pull). License: public (ERCOT's terms,
https://www.ercot.com/help/terms, item 5).
"""

import argparse
import datetime as dt
import io
import json
import os
import sys
import traceback
import zipfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402
import ercot_as_prices as eap  # noqa: E402  the same report site, time handling and completeness rule

NAME = "ercot_as_quantities"
CONNECTOR = "ercot_as_quantities"
REPORT = 12316  # NP4-33-CD
SOURCE = "ercot:np4-33-cd"
PAGE = eap.PAGE.format("NP4-33-CD")
CEILING = 400_000


def parse(raw):
    """One NP4-33-CD zip: long rows (service, ts, value, day)."""
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = [n for n in z.namelist() if n.lower().endswith(".csv")]
    if len(names) != 1:
        raise RuntimeError(f"NP4-33-CD zip holds {z.namelist()}, expected one CSV")
    x = pd.read_csv(z.open(names[0]), dtype=str, keep_default_na=False)
    x.columns = [c.strip() for c in x.columns]
    if list(x.columns) != ["DeliveryDate", "HourEnding", "AncillaryType", "Quantity", "DSTFlag"]:
        raise RuntimeError(f"NP4-33-CD columns {list(x.columns)}: layout changed")
    svc = x["AncillaryType"].str.strip()
    if not svc.isin(eap.SERVICES).all():
        raise RuntimeError(f"NP4-33-CD: unknown service {sorted(set(svc) - set(eap.SERVICES))}")
    v = x["Quantity"].str.strip()
    keep = v != ""
    ts = eap.to_utc(x["DeliveryDate"], x["HourEnding"], x["DSTFlag"])
    return pd.DataFrame({"service": svc[keep], "ts": ts[keep], "value": pd.to_numeric(v[keep], errors="raise"),
                         "day": x.loc[keep, "DeliveryDate"].str.strip()}).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: ERCOT DAM Ancillary Service Plan quantities")
    ap.parse_args(argv)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    try:
        raw, _ = ip.fetch_raw(CONNECTOR, eap.DOC_LIST.format(REPORT), log, fresh=True, pause=eap.PAUSE)
        docs = [d["Document"] for d in json.loads(raw)["ListDocsByRptTypeRes"]["DocumentList"]]
        docs = [d for d in docs if d["FriendlyName"].endswith("_csv")]
        log(f"NP4-33-CD: {len(docs)} CSV files listed")
        frames, short = [], []
        for d in sorted(docs, key=lambda d: d["PublishDate"]):
            pub = pd.Timestamp(d["PublishDate"]).tz_convert(eap.TZ).date()
            want = (pub + dt.timedelta(days=1)).strftime("%m/%d/%Y")  # the plan for the next day, which its DAM used
            body, _ = ip.fetch_raw(CONNECTOR, eap.DOWNLOAD.format(d["DocID"]), log, pause=eap.PAUSE)
            rows = parse(body)
            rows = rows[rows["day"] == want]
            if rows.empty:
                short.append(f"{want}: not in the file published {pub}")
                continue
            rows = rows.assign(source=SOURCE, source_url=eap.DOWNLOAD.format(d["DocID"]),
                               retrieved_at=ip.utc_iso(pd.Timestamp.now(tz="UTC")), vintage=ip.utc_iso(pd.Timestamp(d["PublishDate"])))
            frames.append(rows)
        if not frames:
            raise RuntimeError("no delivery day held")
        rows, gaps = eap.complete_days(pd.concat(frames, ignore_index=True), log)
        if len(rows) > CEILING:
            raise RuntimeError(f"{len(rows):,} rows exceed the approved ceiling of {CEILING:,}; nothing written")
        s = pd.DataFrame({
            "entity": "ercot:" + rows["service"], "variable": "quantity_mw_plan", "ts_utc": rows["ts"].map(ip.utc_iso),
            "value": rows["value"], "unit": "MW", "freq": "PT1H", "geo": "US-TX", "market": "ercot_dam",
            "node": rows["service"], "source": rows["source"], "source_url": rows["source_url"],
            "retrieved_at": rows["retrieved_at"], "vintage": rows["vintage"],
        }).sort_values(["entity", "ts_utc"]).reset_index(drop=True)[ip.SERIES_COLS]
        days = sorted(rows["day"].unique(), key=lambda x: dt.datetime.strptime(x, "%m/%d/%Y"))
        header = [
            "Energy Research Warehouse (ERW): ERCOT DAM Ancillary Service Plan, MW by product and hour (NP4-33-CD)",
            "Shape: series (docs/datastandard.md v0). freq PT1H; ts_utc is the start of the delivery hour. quantity_mw_plan: "
            "the MW ERCOT plans to procure in the day-ahead market for the hour, from the plan published the day before "
            "delivery (the one that day's DAM used).",
            f"Window: delivery days {days[0]} to {days[-1]} ({len(days)} days), what ERCOT's public reports site holds; "
            "2018 to the first day is not held (no keyless public source of the history was found, session 74)."
            + (f" Left out: {'; '.join(short + gaps)}." if short or gaps else ""),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ercot_as_quantities.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{run_id}/ (not in git)",
            f"Source: {SOURCE} ERCOT, DAM Ancillary Service Plan, NP4-33-CD ({eap.DOC_LIST.format(REPORT)})",
            f"  page: {PAGE}",
            "License: public (ERCOT's terms, https://www.ercot.com/help/terms, item 5).",
        ]
        ip.write_csv(s, NAME, header, log)
        ip.update_sources([dict(source=SOURCE, publisher="Electric Reliability Council of Texas (ERCOT)",
                                report="DAM Ancillary Service Plan (NP4-33-CD)", report_url=PAGE,
                                document_list=eap.DOC_LIST.format(REPORT), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="ancillary", status="ok", detail=f"{len(days)} days, {len(s):,} rows"))
        print(f"{NAME}: {len(days)} delivery days, {days[0]} to {days[-1]}, {len(s):,} rows; left out {len(short) + len(gaps)}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {last}", file=sys.stderr)
        results.append(dict(table=NAME, market="ancillary", status="failed", detail=last[:300]))
    ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 1 if any(r["status"] != "ok" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
