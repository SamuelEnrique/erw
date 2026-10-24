#!/usr/bin/env python3
"""EIA's U.S. net imports of crude oil and petroleum products by country of origin or destination, a month from 2010
(session 2412, chain 114: a source of the session's own choosing).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/eia_net_imports_monthly.csv, from the U.S.
Energy Information Administration's API v2, route petroleum/move/neti ("U.S. Net Imports by Country", Petroleum Supply
Monthly), three of its 43 products:

    https://api.eia.gov/v2/petroleum/move/neti/data/?frequency=monthly&data[]=value&facets[product][]=EP00&facets[product][]=EPC0&facets[product][]=EPP0&start=2010-01

    entity    eia_net_imports:<series>, EIA's series id (one a product and partner)
    variable  net_imports_crude_and_products (EP00), net_imports_crude (EPC0), net_imports_products (EPP0, total
              petroleum products), all kbbl/d (EIA's thousand barrels a day); imports less exports, so a negative value
              is a net export to that partner
    ts_utc    the month's first day at 00:00:00Z; freq P1M; geo US (the importer); node EIA's series description
    x_partner EIA's area: the partner's ISO 3166 alpha-3 code as EIA gives it, or EIA's area code (NUS-Z00 the world,
              NUS-ME0 OPEC, NUS-MN0 non-OPEC, NUS-MP0 the Persian Gulf, and 23 countries and
              territories EIA gives no three-letter code, such as Curacao, Sint Maarten and Serbia) where EIA gives
              none. Puerto Rico and the U.S. Virgin Islands are partners, so the importer is the U.S. without them.

The partners are EIA's own: each country, the world total and three groups, which overlap (a sum takes one level). EIA
gives no crude oil record where a partner has none (45 partners in May 2025), but a 0 for products and the total
(11,553 and 10,390 zeros from 2010; the products have 142 partners in May 2025); zeros are kept, nothing is filled. A product,
process, unit or month that does not read stops the run; so does a key given twice. Where a partner and month have all
three products, crude oil plus products is compared with the total: EIA rounds each to whole thousands, and a few
partner months differ by more than 1 kbbl/d as EIA publishes them (24 from 2010 to 2026: the first Egypt in January
2010, 16 kbbl/d; the largest the Bahamas in October 2017, 46 kbbl/d); they are kept as published, counted in the header and listed in the run log.

    python warehouse/connectors/eia_net_imports.py [--from 2010-01] [--offline | --fresh] [--out-dir DIR]

Ceiling: 20 requests a run (pages of 5,000, 3 seconds apart; a page an earlier run saved in warehouse/raw is reused
unless --fresh; --offline asks nothing). License: public (EIA, record 1 of license_reads.csv; cite "U.S. Energy
Information Administration, Petroleum Supply Monthly").
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

NAME = "eia_net_imports_monthly"
CONNECTOR = "eia_net_imports"
SOURCE = "eia:petroleum/move/neti"
API = "https://api.eia.gov/v2/petroleum/move/neti/"
PAGE = "https://www.eia.gov/dnav/pet/pet_move_neti_a_ep00_imn_mbblpd_m.htm"
CEILING, PAUSE, RETRY_WAIT = 20, 3, 60
FIRST = "2010-01"
PRODUCTS = {"EP00": "net_imports_crude_and_products", "EPC0": "net_imports_crude", "EPP0": "net_imports_products"}
TOL = 1.0
COLS = ip.SERIES_COLS + ["x_partner"]


def rows(data, url, retrieved):
    out = []
    for r in data:
        if r.get("process") != "IMN":
            raise RuntimeError(f"a process not asked for: {r.get('process')!r}")
        if r.get("product") not in PRODUCTS:
            raise RuntimeError(f"a product not asked for: {r.get('product')!r}")
        if str(r.get("units", "")).strip().upper() != "MBBL/D":
            raise RuntimeError(f"a unit not thousand barrels a day: {r.get('units')!r}")
        month = str(r["period"])
        if not re.fullmatch(r"\d{4}-\d{2}", month):
            raise RuntimeError(f"a period not a month: {month!r}")
        dt.date.fromisoformat(month + "-01")
        v = pd.to_numeric(r.get("value"), errors="coerce")
        if pd.isna(v):
            continue
        area = str(r.get("area-name") or "").strip()
        out.append(dict(entity=f"eia_net_imports:{str(r['series']).strip()}", variable=PRODUCTS[r["product"]],
                        ts_utc=f"{month}-01T00:00:00Z", value=float(v), unit="kbbl/d", freq="P1M", geo="US", market="",
                        node=str(r.get("series-description") or "").strip(), source=SOURCE, source_url=url,
                        retrieved_at=retrieved, vintage="",
                        x_partner=area if re.fullmatch(r"[A-Z]{3}", area) else str(r.get("duoarea") or "").strip(),
                        _duoarea=str(r.get("duoarea") or "").strip()))
    t = pd.DataFrame(out)
    if len(t) and t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an (entity, variable, ts_utc) is given twice")
    return t


def check_sum(s):
    """Crude oil plus products against the total, where a partner and month have all three: the count checked and the
    partner months that differ by more than TOL, largest first."""
    w = s.pivot_table(index=["_duoarea", "ts_utc"], columns="variable", values="value", aggfunc="first")
    full = w.dropna(subset=list(PRODUCTS.values()))
    gap = (full["net_imports_crude"] + full["net_imports_products"] - full["net_imports_crude_and_products"]).abs()
    bad = gap[gap > TOL].sort_values(ascending=False)
    return len(full), bad


def main(argv=None):
    ap = argparse.ArgumentParser(description="EIA's U.S. net imports of crude oil and petroleum products by country, a month")
    ap.add_argument("--from", dest="first", default=FIRST, help="the first month, YYYY-MM")
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
            return json.loads(hit[0]), ip.redact(url), (hit[1] or {}).get("retrieved_at") or retrieved
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
                return r.json(), ip.redact(r.url), dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
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
            params = {"api_key": key, "frequency": "monthly", "data[]": "value", "facets[product][]": list(PRODUCTS),
                      "start": args.first, "length": 5000, "offset": offset, "sort[0][column]": "period",
                      "sort[0][direction]": "asc", "sort[1][column]": "series", "sort[1][direction]": "asc"}
            body, url, served = get(params)
            resp = body["response"]
            total = int(resp["total"])
            frames.append(rows(resp["data"], url.split("&length")[0], served))
            offset += len(resp["data"])
            if offset >= total or len(resp["data"]) < 5000:
                break
        if offset != total:
            raise RuntimeError(f"{offset:,} rows read of the {total:,} EIA counts")
        s = pd.concat([f for f in frames if len(f)], ignore_index=True)
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a row on two pages")
        checked, bad = check_sum(s)
        for (area, ts), g in bad.items():
            log(f"  crude oil plus products differs from the total by {g:g} kbbl/d: {area} {ts[:7]}")
        worst = f"; the largest {bad.iloc[0]:g} kbbl/d ({bad.index[0][0]}, {bad.index[0][1][:7]})" if len(bad) else ""
        s = s[COLS]
        span = f"{s['ts_utc'].min()[:7]} to {s['ts_utc'].max()[:7]}"
        header = [
            "Energy Research Warehouse (ERW): EIA, U.S. net imports of crude oil and petroleum products by country, a month (session 2412)",
            "Shape: series (docs/datastandard.md v0). entity eia_net_imports:<series>; variable net_imports_crude_and_products, net_imports_crude, net_imports_products (kbbl/d, imports less exports: a negative value is a net export to that partner); "
            "ts_utc the month's first day; freq P1M; geo US; node EIA's series description; x_partner the partner's ISO 3166 alpha-3 code as EIA gives it, or EIA's area code for the world (NUS-Z00), the groups (NUS-ME0 OPEC, NUS-MN0 non-OPEC, NUS-MP0 Persian Gulf), which overlap the countries, "
            "and 23 countries and territories EIA gives no three-letter code. Puerto Rico and the U.S. Virgin Islands are partners, so the importer is the U.S. without them.",
            f"EIA gives no crude oil record where a partner has none, and a 0 (kept) for products and the total; nothing is filled. Crude oil plus products equals the total within {TOL:g} kbbl/d in {checked - len(bad):,} of the {checked:,} partner months that have the three; "
            f"the other {len(bad)} are kept as EIA publishes them and listed in the run log{worst}. Months {span}; {total:,} records of EIA's, {len(s):,} rows.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/eia_net_imports.py; {asked[0]} requests of {CEILING}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} U.S. Energy Information Administration, Petroleum Supply Monthly, U.S. net imports by country (API v2, route petroleum/move/neti), {PAGE}",
            f"  access: {API}data/?frequency=monthly&data[]=value&facets[product][]=EP00&facets[product][]=EPC0&facets[product][]=EPP0&start={args.first}",
            'License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly").',
        ]
        ip.write_snapshot(s, NAME, header, log, COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="U.S. Energy Information Administration (EIA)",
                                    report="Petroleum Supply Monthly, U.S. net imports by country (API v2)", report_url=PAGE, document_list=API,
                                    license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s):,} rows"))
        print(f"{NAME}: {len(s):,} rows, {s['entity'].nunique()} series, {span}; {checked:,} partner months summed, {len(bad)} differ{worst}; {asked[0]} requests")
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
