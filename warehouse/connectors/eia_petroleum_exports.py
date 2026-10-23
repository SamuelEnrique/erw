#!/usr/bin/env python3
"""EIA's U.S. exports of crude oil and of petroleum products by country of destination, a month (session 860, chain 046:
a public source the ERW did not hold, beside its imports by country of origin; session 884, chain 048: seven products).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_petroleum_exports_by_destination.csv,
from the U.S. Energy Information Administration's API v2, route petroleum/move/expc ("Exports by Destination", the
Petroleum Supply Monthly):

    https://api.eia.gov/v2/petroleum/move/expc/data/?frequency=monthly&data[]=value&start=2015-01
        &facets[product][]=EPC0&facets[product][]=EPP0

    entity    eia_petroleum_exports:<destination code>:<product code>, EIA's codes (duoarea NUS-N<country>; product
              EPC0 crude oil, EPP0 total petroleum products, and from session 884 EPD0 distillate fuel oil, EPM0F
              finished motor gasoline, EPJK kerosene-type jet fuel, EPLLPA propane, EPPR residual fuel oil, EPLLEA
              ethane, EPPC petroleum coke)
    variable  exports (kbbl, EIA's MBBL: the month's barrels), exports_per_day (kbbl/d, EIA's MBBL/D, as eia_petroleum_snd_monthly names it)
    ts_utc    the month's first day at 00:00:00Z; freq P1M; geo the destination as EIA names it is in node; geo US
              (the exporting country)

Crude oil, total petroleum products and seven products, from January 2015: the route holds 407,028 monthly records
from 2015 for 42 products, more than a session's ceiling (session 860 counted them). The seven products are asked apart
from crude oil and the total (whose pages session 860 saved), sorted by product, so that a ceiling reached part way
leaves out whole products, named in the header, never part of one. A value EIA leaves empty has no row; nothing is
filled. A unit not in the map stops the run; so does a key given twice.

    python warehouse/connectors/eia_petroleum_exports.py [--offline | --fresh] [--ceiling N]

Ceiling: 30 requests a run unless --ceiling says fewer (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Petroleum Supply Monthly").
"""

import argparse
import datetime as dt
import json
import os
import sys
import time
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "eia_petroleum_exports_by_destination"
CONNECTOR = "eia_petroleum_exports"
SOURCE = "eia:petroleum/move/expc"
API = "https://api.eia.gov/v2/petroleum/move/expc/"
PAGE = "https://www.eia.gov/dnav/pet/pet_move_expc_a_EP00_EEX_mbblpd_m.htm"
CEILING, PAUSE, RETRY_WAIT = 30, 3, 60
FIRST = "2015-01"
PRODUCTS = ["EPC0", "EPP0"]
# session 884: the products session 860 left out, asked as a query of their own, sorted by product
MORE = ["EPD0", "EPM0F", "EPJK", "EPLLPA", "EPPR", "EPLLEA", "EPPC"]
UNITS = {"MBBL": ("exports", "kbbl"), "MBBL/D": ("exports_per_day", "kbbl/d")}


def text(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def rows(data, url, retrieved):
    out = []
    for r in data:
        area, product, u = text(r.get("duoarea")), text(r.get("product")), text(r.get("units"))
        if not area or not product:
            raise RuntimeError(f"a record with no destination or product: {r}")
        if u not in UNITS:
            raise RuntimeError(f"a unit not in the map: {u!r}")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        var, unit = UNITS[u]
        out.append(dict(entity=f"eia_petroleum_exports:{area}:{product}", variable=var, ts_utc=f"{r['period']}-01T00:00:00Z",
                        value=float(v), unit=unit, freq="P1M", geo="US", market="",
                        node=f"{text(r.get('area-name'))}, {text(r.get('product-name'))}", source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage=""))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's U.S. crude oil and petroleum product exports by destination, a month")
    ap.add_argument("--offline", action="store_true", help="the pages from warehouse/raw only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask every page again, even one saved in warehouse/raw")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    ap.add_argument("--ceiling", type=int, default=CEILING, help=f"at most this many requests (default {CEILING})")
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

    class Ceiling(RuntimeError):
        pass

    def get(params):
        url = requests.Request("GET", API + "data/", params=params).prepare().url
        hit = None if args.fresh else ip.raw_cached(CONNECTOR, url)
        if hit:
            log(f"  raw file reused: {ip.redact(url)}")
            return json.loads(hit[0]), ip.redact(url)
        if args.offline:
            raise Ceiling(f"offline: {ip.redact(url)} is not in warehouse/raw/{CONNECTOR}/")
        for attempt in (1, 2):
            if asked[0] >= args.ceiling:
                raise Ceiling(f"the ceiling of {args.ceiling} requests is reached")
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
            body, url = get({"api_key": key, "frequency": "monthly", "data[]": "value", "start": FIRST,
                             "facets[product][]": PRODUCTS, "length": 5000, "offset": offset,
                             "sort[0][column]": "period", "sort[0][direction]": "asc",
                             "sort[1][column]": "series", "sort[1][direction]": "asc"})
            resp = body["response"]
            total = int(resp["total"])
            frames.append(rows(resp["data"], url.split("&length")[0], retrieved))
            offset += len(resp["data"])
            if offset >= total or len(resp["data"]) < 5000:
                break
        if offset != total:
            raise RuntimeError(f"{offset:,} rows read of the {total:,} EIA counts")
        # the seven products, sorted by product: a ceiling reached part way leaves out the product it cut, whole
        more, offset2, total2, cut = [], 0, None, None
        while True:
            try:
                body, url = get({"api_key": key, "frequency": "monthly", "data[]": "value", "start": FIRST,
                                 "facets[product][]": MORE, "length": 5000, "offset": offset2,
                                 "sort[0][column]": "product", "sort[0][direction]": "asc",
                                 "sort[1][column]": "period", "sort[1][direction]": "asc",
                                 "sort[2][column]": "series", "sort[2][direction]": "asc"})
            except Ceiling as e:
                cut = str(e)
                break
            resp = body["response"]
            total2 = int(resp["total"])
            more.append(rows(resp["data"], url.split("&length")[0], retrieved))
            offset2 += len(resp["data"])
            if offset2 >= total2 or len(resp["data"]) < 5000:
                break
        m = pd.concat([f for f in more if len(f)], ignore_index=True) if any(len(f) for f in more) else pd.DataFrame(columns=ip.SERIES_COLS)
        product = m["entity"].str.split(":").str[-1] if len(m) else pd.Series(dtype=str)
        if cut:
            last = product.iloc[-1] if len(m) else None
            if last is not None:
                m, product = m[product != last], product[product != last]
            log(f"  {cut}: {offset2:,} of {total2 if total2 is not None else '?'} records of the seven products read; {last} left out whole")
        elif total2 is not None and offset2 != total2:
            raise RuntimeError(f"{offset2:,} rows of the seven products read of the {total2:,} EIA counts")
        taken = [p for p in MORE if p in set(product)]
        missed = [p for p in MORE if p not in taken] if cut else []       # cut by the ceiling
        empty = [] if cut else [p for p in MORE if p not in taken]        # read to the end: EIA gives them no record
        frames.append(m)
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        s = s[ip.SERIES_COLS]
        span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, U.S. exports of crude oil and of petroleum products by country of destination, a month (session 860)",
            "Shape: series (docs/datastandard.md v0). entity eia_petroleum_exports:<EIA destination code>:<product: EPC0 crude oil, EPP0 total petroleum products, "
            "EPD0 distillate fuel oil, EPM0F finished motor gasoline, EPJK kerosene-type jet fuel, EPLLPA propane, EPPR residual fuel oil, EPLLEA ethane, "
            "EPPC petroleum coke>; variables exports (kbbl) and exports_per_day (kbbl/d); the products are part of EPP0's total, a sum leaves EPP0 out; "
            "ts_utc the month's first day; freq P1M; geo US (the exporter); node the destination and product as EIA names them.",
            f"Crude oil, total products and {len(taken)} of the seven products ({', '.join(taken) or 'none'}) from {FIRST} (the route's 42 products since 2015 are 407,028 records)"
            + (f"; left out whole, the ceiling reached: {', '.join(missed)}" if missed else "")
            + (f"; no record from EIA: {', '.join(empty)}" if empty else "")
            + f". A value EIA leaves empty has no row; nothing is filled. Months {span}; {total + offset2:,} records of EIA's read, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_petroleum_exports.py; {asked[0]} requests of {args.ceiling}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Petroleum Supply Monthly, exports by destination (API v2, route petroleum/move/expc), {PAGE}",
            f"  access: {API}data/?frequency=monthly&data[]=value&start={FIRST}&facets[product][]=EPC0&facets[product][]=EPP0; and the same with facets[product][]= each of {', '.join(MORE)}, sorted by product",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly").',
        ]
        ip.write_snapshot(s, NAME, header, log, ip.SERIES_COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Petroleum Supply Monthly, exports by destination (API v2)", report_url=PAGE, document_list=API,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['entity'].nunique()} series, {span}; products taken {', '.join(taken) or 'none'}"
              + (f", left out {', '.join(missed)}" if missed else "") + f"; {asked[0]} requests")
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
