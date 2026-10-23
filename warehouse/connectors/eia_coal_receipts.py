#!/usr/bin/env python3
"""EIA's coal receipts at power plants: each mine to each plant by supplier, rank, contract type and transport mode, a year
(session 875, chain 047: coal's path from mine to plant; session 870 found the by-mine-by-plant route without a key).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_coal_receipts_annual.csv, from the U.S.
Energy Information Administration's API v2, route coal/shipments/receipts (Form EIA-923's fuel receipts):

    https://api.eia.gov/v2/coal/shipments/receipts/data/?frequency=annual&data[]=quantity&data[]=price
        &data[]=heat-content&data[]=sulfur-content&data[]=ash-content&start=2008

    entity    eia_coal_receipt:<mineMSHAId>:<plantId>:<supplier>:<coalRankId>:<contractType>:<transportationMode>, EIA's
              codes and the supplier's name as a slug; coalRankId TOT is EIA's sum of the ranks beside it (leave it out of
              a sum over ranks)
    variable  quantity (short_ton), price (USD/short_ton, EIA's average delivered price), heat_content (Btu/lb, Decision
              52), sulfur_content and ash_content (pct by weight)
    ts_utc    the year's 1 January at 00:00:00Z; freq P1Y; geo US-<plant state>; node mine, supplier and plant names
    x_*       EIA's own fields: MSHA id, mine state, county, basin and type, plant id and state, supplier, rank, contract
              type, transport mode

A value EIA leaves empty or withholds has no row; nothing is filled. A unit not in the map stops the run. A row EIA gives
twice with every field the same is kept once; records under one key with two values have no key and are left out whole,
counted in the header (chain 030's rule).

    python warehouse/connectors/eia_coal_receipts.py [--offline | --fresh]

Ceiling: 15 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused unless
--fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy Information
Administration, Form EIA-923").
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eia_coal_receipts_annual"
CONNECTOR = "eia_coal_receipts"
SOURCE = "eia:coal/shipments/receipts"
API = "https://api.eia.gov/v2/coal/shipments/receipts/"
PAGE = "https://www.eia.gov/coal/data/browser/"
CEILING, PAUSE, RETRY_WAIT = 15, 3, 60
FIRST = "2008"
DATA = {"quantity": ("quantity", {"tons": ("short_ton", 1.0)}),
        "price": ("price", {"average dollars per ton": ("USD/short_ton", 1.0)}),
        "heat-content": ("heat_content", {"btu per pound": ("Btu/lb", 1.0)}),
        "sulfur-content": ("sulfur_content", {"percent by weight": ("pct", 1.0)}),
        "ash-content": ("ash_content", {"percent by weight": ("pct", 1.0)})}
KEY = ["mineMSHAId", "plantId", "coalSupplier", "coalRankId", "contractType", "transportationMode"]
X_COLS = ["x_msha_id", "x_mine_state", "x_mine_county", "x_mine_basin", "x_mine_type", "x_plant_id", "x_plant_state",
          "x_supplier", "x_rank", "x_contract_type", "x_transport_mode"]
NO_KEY = set()


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def slug(v):
    return re.sub(r"[^A-Za-z0-9]+", "_", v).strip("_")


def rows(data, url, retrieved):
    out = []
    for r in data:
        k = [text(r.get(c)) for c in KEY]
        if not k[0] or not k[1]:
            raise RuntimeError(f"a record with no mine or plant: {r}")
        year, pstate = int(r["period"]), text(r.get("plantStateId"))
        base = dict(entity="eia_coal_receipt:" + ":".join(slug(x) or "none" for x in k), ts_utc=f"{year}-01-01T00:00:00Z",
                    freq="P1Y", geo=f"US-{pstate}" if len(pstate) == 2 else "US", market="",
                    node=f"{text(r.get('mineName'))} ({k[2]}) to {text(r.get('plantName'))}", source=SOURCE, source_url=url,
                    retrieved_at=retrieved, vintage="", x_msha_id=k[0], x_mine_state=text(r.get("mineStateId")),
                    x_mine_county=text(r.get("mineCountyName")), x_mine_basin=text(r.get("mineBasinDescription")),
                    x_mine_type=text(r.get("mineTypeDescription")), x_plant_id=k[1], x_plant_state=pstate, x_supplier=k[2],
                    x_rank=text(r.get("coalRankDescription")), x_contract_type=k[4], x_transport_mode=k[5])
        for col, (var, units) in DATA.items():
            v = pd.to_numeric(r.get(col), errors="coerce")
            if pd.isna(v):
                continue
            u = text(r.get(f"{col}-units")).lower()
            if u not in units:
                raise RuntimeError(f"a unit not in the map for {col}: {r.get(f'{col}-units')!r}")
            unit, factor = units[u]
            out.append(dict(base, variable=var, value=float(v) * factor, unit=unit))
    return pd.DataFrame(out)


def no_key(s):
    s = s.drop_duplicates()
    twice = s.duplicated(["entity", "variable", "ts_utc"], keep=False)
    if twice.any():
        bad = set(zip(s.loc[twice, "entity"], s.loc[twice, "ts_utc"]))
        NO_KEY.update(bad)
        s = s[[k not in bad for k in zip(s["entity"], s["ts_utc"])]]
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's coal receipts at power plants, a year")
    ap.add_argument("--offline", action="store_true", help="the pages from warehouse/raw only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask every page again, even one saved in warehouse/raw")
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
        url = requests.Request("GET", API + "data/", params=params).prepare().url
        hit = None if args.fresh else ip.raw_cached(CONNECTOR, url)
        if hit:
            log(f"  raw file reused: {ip.redact(url)}")
            return json.loads(hit[0]), ip.redact(url)
        if args.offline:
            raise RuntimeError(f"offline: {ip.redact(url)} is not in warehouse/raw/{CONNECTOR}/")
        for attempt in (1, 2):
            if asked[0] >= CEILING:
                raise RuntimeError(f"the ceiling of {CEILING} requests is reached")
            asked[0] += 1
            time.sleep(PAUSE)
            r = requests.get(url, timeout=180)
            if r.status_code < 500 and r.status_code != 429:
                r.raise_for_status()
                return r.json(), ip.redact(r.url)
            log(f"  {ip.redact(r.url)}: HTTP {r.status_code}; " + (f"asked once more in {RETRY_WAIT} s" if attempt == 1 else "not asked again"))
            time.sleep(RETRY_WAIT)
        raise RuntimeError(f"HTTP {r.status_code} twice for {ip.redact(r.url)}")

    try:
        key = ip.load_key("EIA_API_KEY", log)
        if not key:
            raise RuntimeError("EIA_API_KEY is not set (.env or the environment)")
        retrieved = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        frames, offset, total = [], 0, None
        while True:
            params = {"api_key": key, "frequency": "annual", "data[]": list(DATA), "start": FIRST, "length": 5000, "offset": offset,
                      "sort[0][column]": "period", "sort[0][direction]": "asc"}
            for i, c in enumerate(KEY, start=1):
                params[f"sort[{i}][column]"], params[f"sort[{i}][direction]"] = c, "asc"
            body, url = get(params)
            resp = body["response"]
            total = int(resp["total"])
            frames.append(rows(resp["data"], url.split("&length")[0], retrieved))
            offset += len(resp["data"])
            if offset >= total or len(resp["data"]) < 5000:
                break
        if offset != total:
            raise RuntimeError(f"{offset:,} rows read of the {total:,} EIA counts")
        s = no_key(pd.concat([f for f in frames if len(f)], ignore_index=True))
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols]
        span = f"{s['ts_utc'].min()[:4]} to {s['ts_utc'].max()[:4]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, coal receipts at power plants: each mine to each plant by supplier, rank, contract type and transport mode, a year (session 875)",
            "Shape: series (docs/datastandard.md v0). entity eia_coal_receipt:<mineMSHAId>:<plantId>:<supplier>:<coalRankId>:<contractType>:<transportationMode>; "
            "coalRankId TOT is EIA's sum of the ranks beside it; variables quantity (short_ton), price (USD/short_ton), heat_content (Btu/lb), sulfur_content and ash_content (pct by weight); ts_utc the year's 1 January; freq P1Y; geo US-<plant state>; x_* EIA's own fields.",
            f"A value EIA leaves empty or withholds has no row; nothing is filled. Records under one key with two values, left out whole (no key): {len(NO_KEY):,}. Years {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_coal_receipts.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, coal receipts at power plants (Form EIA-923; API v2, route coal/shipments/receipts), {PAGE}",
            f"  access: {API}data/?frequency=annual&data[]=quantity&data[]=price&data[]=heat-content&data[]=sulfur-content&data[]=ash-content&start={FIRST}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Form EIA-923").',
        ]
        ip.write_snapshot(s, NAME, header, log, cols)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Coal receipts at power plants (Form EIA-923, API v2)", report_url=PAGE, document_list=API,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['x_msha_id'].nunique():,} mines, {s['x_plant_id'].nunique():,} plants, {span}; {len(NO_KEY):,} records without a key; {asked[0]} requests")
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
