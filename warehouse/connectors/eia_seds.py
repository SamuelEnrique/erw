#!/usr/bin/env python3
"""EIA's State Energy Data System: each state's energy consumption by source, electricity prices by sector and
expenditures, a year (session 497, a public source probed while the data lock was held).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_seds_state_energy.csv, from the U.S.
Energy Information Administration's API v2, route seds (annual, 1960 to the latest year; this table from 1990):

    https://api.eia.gov/v2/seds/data/?frequency=annual&data[]=value&facets[seriesId][]=<id>...&start=1990

    entity    eia_seds:<seriesId>:<state>; variable value; node the series' name; geo US-<state> (US for the U.S.)
    ts_utc    the year's 1 January; freq P1Y
    series    SERIES below: total, electricity, natural gas, coal, petroleum and renewable consumption and nuclear
              (billion Btu, as TBtu: times 0.001); electricity's price by sector and all sectors (dollars per million
              Btu, as USD/MMBtu); electricity's and all energy's expenditures (million dollars, as USD: times 1,000,000)

SEDS's figures are EIA's estimates, as its technical notes describe them, published by EIA; nothing is filled here, and a
withheld or missing value has no row. A unit not in the map stops the run; so does a key given twice.

    python warehouse/connectors/eia_seds.py

Ceiling: 20 requests a run (pages of 5,000, 3 seconds apart; a 429 or a 5xx asked once more after 60 seconds). License:
public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information Administration, State Energy Data System").
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
import iso_prices as ip  # noqa: E402

NAME = "eia_seds_state_energy"
CONNECTOR = "eia_seds"
SOURCE = "eia:seds"
API = "https://api.eia.gov/v2/seds/"
PAGE = "https://www.eia.gov/state/seds/"
CEILING, PAUSE, RETRY_WAIT = 20, 3, 60
FIRST = "1990"
SERIES = ["TETCB", "ESTCB", "NGTCB", "CLTCB", "PATCB", "RETCB", "NUETB",
          "ESRCD", "ESCCD", "ESICD", "ESTCD", "ESTCV", "TETCV"]
UNITS = {"billion btu": ("TBtu", 0.001), "dollars per million btu": ("USD/MMBtu", 1.0), "million dollars": ("USD", 1e6)}


def unit_of(u):
    k = str(u).strip().lower()
    if k not in UNITS:
        raise RuntimeError(f"a unit not in the map: {u!r}")
    return UNITS[k]


def rows(data, url, retrieved):
    out = []
    for r in data:
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        unit, factor = unit_of(r.get("unit", ""))
        st = r["stateId"]
        out.append(dict(entity=f"eia_seds:{r['seriesId']}:{st}", variable="value", ts_utc=f"{int(r['period'])}-01-01T00:00:00Z",
                        value=float(v) * factor, unit=unit, freq="P1Y", geo="US" if st == "US" else f"US-{st}", market="",
                        node=r.get("seriesDescription", ""), source=SOURCE, source_url=url, retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA State Energy Data System: consumption, prices and expenditures by state")
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
    asked = [0]

    def get(params):
        for attempt in (1, 2):
            if asked[0] >= CEILING:
                raise RuntimeError(f"the ceiling of {CEILING} requests is reached")
            asked[0] += 1
            time.sleep(PAUSE)
            r = requests.get(API + "data/", params=params, timeout=120)
            if r.status_code < 500 and r.status_code != 429:
                r.raise_for_status()
                return r
            log(f"  {ip.redact(r.url)}: HTTP {r.status_code}; " + (f"asked once more in {RETRY_WAIT} s" if attempt == 1 else "not asked again"))
            time.sleep(RETRY_WAIT)
        raise RuntimeError(f"HTTP {r.status_code} twice for {ip.redact(r.url)}")

    try:
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is not set (.env or the environment)")
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        frames, offset = [], 0
        while True:
            r = get({"api_key": key, "frequency": "annual", "data[]": "value", "facets[seriesId][]": SERIES, "start": FIRST,
                     "length": 5000, "offset": offset})
            resp = r.json()["response"]
            frames.append(rows(resp["data"], ip.redact(r.url.split("&offset")[0]), retrieved))
            offset += len(resp["data"])
            if offset >= int(resp["total"]) or not resp["data"]:
                break
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        s = s[ip.SERIES_COLS]
        header = [
            "Energy Research Warehouse (ERW): EIA State Energy Data System, each state's consumption by source, electricity prices by sector and expenditures, a year (session 497)",
            f"Shape: series (docs/datastandard.md v0). entity eia_seds:<seriesId>:<state>; variable value; ts_utc the year's 1 January; freq P1Y; node the series' name. Series: {', '.join(SERIES)}. Billion Btu as TBtu, dollars per million Btu as USD/MMBtu, million dollars as USD.",
            f"EIA's estimates as SEDS publishes them (its technical notes); nothing is filled here; a withheld value has no row. Years {s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_seds.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, State Energy Data System (API v2, route seds), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=value&facets[seriesId][]=<id>&start={FIRST}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, State Energy Data System").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="State Energy Data System (API v2)", report_url=PAGE, document_list=API, license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['entity'].nunique():,} series by state, {s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}; {asked[0]} requests")
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
