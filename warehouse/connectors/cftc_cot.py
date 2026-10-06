#!/usr/bin/env python3
"""CFTC Commitments of Traders: managed money positions in four energy futures, weekly (session 134, approved pull).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/cftc_cot_positions.csv, from the
Commodity Futures Trading Commission's Disaggregated Commitments of Traders report, futures only, read from the CFTC's
public reporting service (https://publicreporting.cftc.gov/resource/72hh-3qpy.json), from 2015:

    entity    cftc:<contract market code>: 067651 WTI crude oil (NYMEX), 06765T Brent Last Day (NYMEX),
              023651 Henry Hub natural gas (NYMEX), 111659 RBOB gasoline (NYMEX)
    variable  managed_money_long, managed_money_short, managed_money_net (long less short), open_interest
    value     contracts, as the CFTC reports them; managed_money_net is the one figure computed here
    freq      P1W; ts_utc is the report's "as of" date (a Tuesday) at 00:00:00Z; node is the CFTC's market name

    python warehouse/connectors/cftc_cot.py [--out-dir DIR]

BRENT. The Brent contract most of the market trades is ICE Futures Europe's, and ICE publishes its own report. ICE's
terms of use forbid copying, republishing and systematic retrieval of its site's content without written permission
(https://www.ice.com/terms-of-use, read 6 October 2026), so that report is not pulled. The Brent row here is the
NYMEX Brent Last Day contract, which the CFTC reports: a far smaller market, and labeled so.

A week the CFTC lists with a blank position is not written. Nothing is filled. The table is written only if its newest
report is within 21 days. Ceiling: 1,200,000 rows for session 134's pulls in all; this pull reads about 2,500.
License: public. "Government information at the CFTC website is in the public domain. Public domain information may be
freely distributed and copied, but it is requested that in any subsequent use the CFTC be given appropriate
acknowledgement" (https://www.cftc.gov/WebPolicy/index.htm, read 6 October 2026).
"""

import argparse
import datetime as dt
import json
import os
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "cftc_cot_positions"
CONNECTOR = "cftc_cot"
SOURCE = "cftc:disaggregated_cot_futures"
API = "https://publicreporting.cftc.gov/resource/72hh-3qpy.json"
PAGE = "https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm"
START = "2015-01-01"
STALE_DAYS = 21
UA = {"User-Agent": "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)"}
CONTRACTS = {"067651": "WTI crude oil, NYMEX", "06765T": "Brent Last Day, NYMEX", "023651": "Henry Hub natural gas, NYMEX", "111659": "RBOB gasoline, NYMEX"}
FIELDS = {"m_money_positions_long_all": "managed_money_long", "m_money_positions_short_all": "managed_money_short", "open_interest_all": "open_interest"}
SOURCE_ENTRY = dict(source=SOURCE, publisher="Commodity Futures Trading Commission (CFTC)", report="Commitments of Traders, Disaggregated report, futures only", report_url=PAGE, document_list=API, license="public", tables=[NAME])


def parse(rows, code, url, retrieved):
    """The CFTC's rows of one contract as the table's rows, and the number of weeks left out for a blank position."""
    out, blank = [], 0
    for r in rows:
        if r.get("cftc_contract_market_code") != code:
            raise RuntimeError(f"the CFTC answered contract {r.get('cftc_contract_market_code')!r}, asked for {code}")
        vals = {}
        for field, variable in FIELDS.items():
            v = r.get(field)
            vals[variable] = None if v in (None, "") else float(v)
        if vals["managed_money_long"] is None or vals["managed_money_short"] is None:
            blank += 1
            continue
        vals["managed_money_net"] = vals["managed_money_long"] - vals["managed_money_short"]
        ts = str(r["report_date_as_yyyy_mm_dd"])[:10] + "T00:00:00Z"
        for variable, v in vals.items():
            if v is not None:
                out.append(dict(entity=f"cftc:{code}", variable=variable, ts_utc=ts, value=v, unit="count", freq="P1W", geo="US", market="nymex", node=str(r.get("market_and_exchange_names") or "").strip(),
                                source=SOURCE, source_url=url, retrieved_at=retrieved, vintage=""))
    return out, blank


def main(argv=None):
    ap = argparse.ArgumentParser(description="CFTC Commitments of Traders: managed money positions in four energy futures")
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
        out, read, blank = [], 0, 0
        for code, what in CONTRACTS.items():
            url = requests.Request("GET", API, params={"cftc_contract_market_code": code, "$where": f"report_date_as_yyyy_mm_dd >= '{START}T00:00:00'", "$order": "report_date_as_yyyy_mm_dd ASC", "$limit": "5000"}).prepare().url
            content, rec = ip.fetch_raw(CONNECTOR, url, log, fresh=True, headers=UA, pause=1)
            rows = json.loads(content)
            read += len(rows)
            shaped, n = parse(rows, code, url, rec["retrieved_at"])
            blank += n
            out += shaped
            log(f"  {code} ({what}): {len(rows)} weeks, newest {rows[-1]['report_date_as_yyyy_mm_dd'][:10] if rows else 'none'}")
        s = pd.DataFrame(out, columns=ip.SERIES_COLS)
        if s.empty or s["entity"].nunique() != len(CONTRACTS):
            raise RuntimeError(f"the CFTC answered for {sorted(set(s['entity'])) if len(s) else 'no contract'}")
        age = (pd.Timestamp.now(tz="UTC") - pd.Timestamp(s["ts_utc"].max())).days
        if age > STALE_DAYS:
            raise RuntimeError(f"the newest report the CFTC holds is {s['ts_utc'].max()[:10]}, {age} days old (limit {STALE_DAYS})")
        header = [
            "Energy Research Warehouse (ERW): CFTC Commitments of Traders, managed money positions in WTI, Brent Last Day, Henry Hub and RBOB futures (NYMEX), weekly from 2015 (session 134)",
            "Shape: series (docs/datastandard.md v0). managed_money_long, managed_money_short and open_interest are the CFTC's figures, contracts, futures only (Disaggregated report); managed_money_net is long less short, computed here. "
            "freq P1W; ts_utc is the report's as-of date (a Tuesday) at 00:00:00Z; the CFTC publishes it on the Friday after. node is the CFTC's market name.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/cftc_cot.py",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} Commodity Futures Trading Commission, {SOURCE_ENTRY['report']}, {PAGE}",
            f"  access: {API}?cftc_contract_market_code=<code> for " + "; ".join(f"{k} = {v}" for k, v in CONTRACTS.items()),
            f"Rows read: {read:,} weeks of four contracts. Weeks with a blank managed money position, not written: {blank}. Nothing is filled. ICE's own report for ICE Brent is not pulled: ICE's terms forbid republishing.",
            "License: public. Government information at the CFTC website is in the public domain (https://www.cftc.gov/WebPolicy/index.htm); the CFTC asks to be acknowledged.",
        ]
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if os.path.exists(path):
            os.remove(path)
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        if not args.out_dir:
            ip.update_sources([SOURCE_ENTRY])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows; {read:,} read"))
        print(f"{NAME}: {len(s):,} rows, {s['ts_utc'].min()[:10]} to {s['ts_utc'].max()[:10]}; {read:,} weeks read")
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
