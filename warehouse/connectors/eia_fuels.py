#!/usr/bin/env python3
"""Daily fuel spot prices: Henry Hub natural gas, WTI Cushing and Brent crude (EIA).

Energy Research Warehouse (ERW) connector. Reads the full daily history the
EIA API v2 offers and writes one `series` table:

    warehouse/output/eia_fuel_spot_prices.csv

    python warehouse/connectors/eia_fuels.py

| entity           | EIA route and series             | unit      | history from |
|------------------|----------------------------------|-----------|--------------|
| eia:henry_hub    | natural-gas/pri/fut, RNGWHHD     | USD/MMBtu | 1997         |
| eia:wti_cushing  | petroleum/pri/spt, RWTC          | USD/bbl   | 1986         |
| eia:brent        | petroleum/pri/spt, RBRTE         | USD/bbl   | 1987         |

Dates: freq P1D; ts_utc is the trading date at 00:00:00Z. It names the date
EIA reports, not an instant (docs/datastandard.md, Decisions).

Completeness: these are trading-day series, so weekends, holidays and market
closures have no value and a calendar-day completeness rule cannot apply.
Instead: every date EIA lists must carry a number, except that a date EIA
lists with an empty value is an unpublished observation and is omitted (the
standard's rule for a missing observation), and is logged; each series must
reach within 10 calendar days of the run, or the table is stale and not
written. Every run replaces the whole history, so EIA revisions are picked up.
Negative prices are real (WTI, 2020-04-20). The key comes from EIA_API_KEY.
"""

import argparse
import datetime as dt
import os
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402  shared: raw capture, merge-writer, logs, redaction

API = "https://api.eia.gov/v2/"
PAGE = 5000
STALE_DAYS = 10
SERIES = {
    # entity: (route, EIA series id, unit, geo)
    "eia:henry_hub": ("natural-gas/pri/fut", "RNGWHHD", "USD/MMBtu", "US-LA"),
    "eia:wti_cushing": ("petroleum/pri/spt", "RWTC", "USD/bbl", "US-OK"),
    "eia:brent": ("petroleum/pri/spt", "RBRTE", "USD/bbl", ""),
}
EIA_UNITS = {"$/MMBTU": "USD/MMBtu", "$/BBL": "USD/bbl"}  # as EIA writes them -> ERW units
REPORTS = {
    "eia:natural-gas/pri/fut": ("Natural Gas Spot and Futures Prices (NYMEX), daily",
                                "https://www.eia.gov/dnav/ng/ng_pri_fut_s1_d.htm",
                                API + "natural-gas/pri/fut/"),
    "eia:petroleum/pri/spt": ("Spot Prices for Crude Oil and Petroleum Products, daily",
                              "https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm",
                              API + "petroleum/pri/spt/"),
}
NAME = "eia_fuel_spot_prices"


def fetch_series(route, series, key, log):
    out, offset = [], 0
    while True:
        params = [("api_key", key), ("frequency", "daily"), ("data[0]", "value"),
                  ("facets[series][]", series), ("sort[0][column]", "period"),
                  ("sort[0][direction]", "asc"), ("offset", str(offset)), ("length", str(PAGE))]

        def call():
            r = requests.get(API + route + "/data/", params=params, timeout=120)
            if r.status_code != 200:
                raise RuntimeError(f"EIA {route} {series} HTTP {r.status_code}: {ip.redact(r.text[:300])}")
            return r
        r = ip.with_retries(f"EIA {route} {series} offset {offset}", call, log)
        body = r.json()["response"]
        rows = body.get("data", [])
        total = int(body.get("total", 0))
        url = ip.redact(r.url)
        retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
        for row in rows:
            row["_url"], row["_retrieved"] = url, retrieved
        out += rows
        log(f"  {series} offset {offset}: {len(rows)} rows (total {total}) {url}")
        offset += len(rows)
        if not rows or offset >= total:
            break
        time.sleep(0.5)
    if len(out) != total:
        raise RuntimeError(f"EIA {series}: got {len(out)} rows, API reported {total}")
    return pd.DataFrame(out)


def shape(entity, df, log):
    route, series, unit, geo = SERIES[entity]
    got_units = set(df["units"])
    if {EIA_UNITS.get(u) for u in got_units} != {unit}:
        raise RuntimeError(f"{series}: EIA units {got_units}, expected {unit}")
    if df["period"].duplicated().any():
        raise RuntimeError(f"{series}: EIA lists a date more than once")
    value = pd.to_numeric(df["value"], errors="coerce")
    bad = df[value.isna() & df["value"].notna() & (df["value"].astype(str).str.strip() != "")]
    if len(bad):
        raise RuntimeError(f"{series}: non-numeric values {bad['value'].unique()[:5]}")
    empty = df[value.isna()]
    for _, r in empty.iterrows():
        log(f"  {series} {r['period']}: EIA lists the date with no value; omitted (not published)")
    keep = value.notna()
    d = df[keep]
    return pd.DataFrame({
        "entity": entity,
        "variable": "spot_price",
        "ts_utc": pd.to_datetime(d["period"], format="%Y-%m-%d").dt.strftime("%Y-%m-%dT00:00:00Z").values,
        "value": value[keep].values,
        "unit": unit,
        "freq": "P1D",
        "geo": geo,
        "market": "",
        "node": "",
        "source": f"eia:{route}",
        "source_url": d["_url"].values,
        "retrieved_at": d["_retrieved"].values,
        "vintage": "",
    }), len(empty)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW EIA fuel spot price connector")
    ap.add_argument("--out-dir", help="write CSVs, logs and raw files here (trial runs)")
    args = ap.parse_args(argv)
    if args.out_dir:
        ip.set_out_dir(args.out_dir)
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"eia_fuels_{run_id}.log"))
    ip.RAW.open("eia_fuels", run_id)
    log(f"ERW eia_fuels run {run_id}: full daily history")
    key = ip.load_key("EIA_API_KEY", log)
    status = "ok"
    detail = ""
    try:
        if key is None:
            raise RuntimeError("EIA_API_KEY is empty; nothing pulled")
        parts, omitted = [], {}
        today = pd.Timestamp.now(tz="UTC").normalize().tz_localize(None)
        for entity, (route, series, unit, geo) in SERIES.items():
            log(f"{entity} ({route} {series}):")
            s, n_empty = shape(entity, fetch_series(route, series, key, log), log)
            last = pd.Timestamp(s["ts_utc"].max()[:10])
            if (today - last).days > STALE_DAYS:
                raise RuntimeError(f"{series}: latest value {last.date()} is more than {STALE_DAYS} "
                                   "days old; not writing a stale table")
            log(f"  {len(s)} dates {s['ts_utc'].min()[:10]} to {s['ts_utc'].max()[:10]}, "
                f"{n_empty} listed without a value")
            parts.append(s)
            omitted[entity] = n_empty
        s = pd.concat(parts, ignore_index=True).sort_values(["entity", "variable", "ts_utc"])
        header = [
            "Energy Research Warehouse (ERW): Daily fuel spot prices: Henry Hub natural gas, "
            "WTI Cushing crude, Brent crude",
            "Shape: series (docs/datastandard.md v0). Units: USD/MMBtu (Henry Hub), USD/bbl (WTI, "
            "Brent). freq P1D: ts_utc is the trading date at 00:00:00Z, a date, not an instant.",
            "Window: the full daily history the EIA API v2 offers; every run replaces all of it.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_fuels.py via the EIA API v2",
            f"Run log: warehouse/output/logs/eia_fuels_{run_id}.log (every API request, key removed)",
            f"Raw files: warehouse/raw/eia_fuels/{run_id}/ (not in git; manifest.csv lists each file and URL)",
        ]
        for src, (report, page, route_url) in REPORTS.items():
            header.append(f"Source: {src} {report}, {page}")
            header.append(f"  document list: {route_url}")
        header.append("Series: eia:henry_hub = RNGWHHD, eia:wti_cushing = RWTC, eia:brent = RBRTE. "
                      "Trading days only: dates without a value are not in the table. Dates EIA "
                      f"lists with no value, omitted: {omitted}. Negative values are real.")
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        ip.update_sources([dict(source=src, publisher="U.S. Energy Information Administration (EIA)",
                                report=r[0], report_url=r[1], document_list=r[2], tables=[NAME])
                           for src, r in REPORTS.items()])
    except Exception:
        tb = ip.redact(traceback.format_exc())
        detail = tb.strip().splitlines()[-1][:300]
        status = "failed"
        log(f"FAILED, no output file written:\n{tb}")
        print(f"eia_fuels {NAME} FAILED, no output file written: {detail}", file=sys.stderr)
    ip.write_status("eia_fuels", run_id, [dict(table=NAME, market="daily", status=status,
                                                detail=detail)])
    log(f"done, status={status}")
    log.close()
    print(f"eia_fuels run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
