#!/usr/bin/env python3
"""Estonia's electricity production by source, imports and exports, a month from January 2005, as Statistics Estonia
publishes it (table KE21) (session 2278, chain 103: a third source of the session's own choosing, Estonia beside chain
099's Norway and Sweden and session 2273's Finland; Elering's dashboard, the grid operator's own, disallows every path in
its robots file).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/statee_estonia_electricity_monthly.csv,
from Statistics Estonia's PxWeb API (no key): the table's metadata by GET and one JSON-stat 2.0 query by POST, to the
same address:

    https://andmed.stat.ee/api/v1/en/stat/majandus/energeetika/energia-tarbimine-ja-tootmine/luhiajastatistika/KE21.PX
    "KE21: ELECTRICITY PRODUCTION, IMPORTS, EXPORTS AND SALE (MONTHLY)"

    entity      statee:ee
    variable    the indicator's English name in snake case, its unit dropped (total_electricity_production,
                electricity_production_from_hydro_energy, electricity_production_from_wind_energy,
                electricity_production_from_solar_energy, imports_of_electricity, exports_of_electricity); node the name
                as Statistics Estonia writes it; x_code its code (PROD_E, PROD_E_HYDR, PROD_E_WIND, PROD_E_SOLAR,
                IMPORTS, EXPORTS)
    unit        MWh (the table's GWh times 1,000); ts_utc the month's first day; freq P1M; geo EE

Only the indicators in GWh are taken; the table's two shares of sold electricity (percent) are not. Totals are Statistics
Estonia's, never sums made here; a cell it leaves empty has no row; nothing is filled. A metadata without the two
variables, an indicator taken whose name does not end in ", GWh", a month not of the form YYYYMmm, a value array not the
size of the dimensions or an indicator and month given twice stops the run. The answer's "updated" is the vintage,
except that the API answers 9999-12-31T21:59:59Z, a placeholder, which is written as no vintage.

    python warehouse/connectors/statee_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests (the metadata and the query), saved together in warehouse/raw/statee_electricity/ (one address
serves both) and reused offline. andmed.stat.ee has no robots file (HTTP 404); www.stat.ee's disallows Drupal's own
paths only (session 2278). License: CC BY-SA 4.0, Statistics Estonia's principles for disseminating official statistics
("Statistics Estonia's open data can be shared under Creative Common (CC) licence BY-SA 4.0"); source: Statistics Estonia.
"""

import argparse
import datetime as dt
import itertools
import json
import os
import re
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "statee_estonia_electricity_monthly"
CONNECTOR = "statee_electricity"
SOURCE = "statee:KE21"
HOST = "andmed.stat.ee"
TABLE_URL = "https://andmed.stat.ee/api/v1/en/stat/majandus/energeetika/energia-tarbimine-ja-tootmine/luhiajastatistika/KE21.PX"
PAGE = "https://andmed.stat.ee/en/stat/majandus__energeetika__energia-tarbimine-ja-tootmine__luhiajastatistika/KE21"
TERMS = "https://www.stat.ee/en/statistics-estonia/about-us/strategy/principles-dissemination-official-statistics"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SAVED = "query_KE21.json"
IND, TIME = "Näitaja", "Vaatlusperiood"
X_COLS = ["x_code"]


def slug(label):
    s = re.sub(r",\s*GWh$", "", label.replace("\xa0", " ").strip())
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def gwh_codes(meta):
    v = {x["code"]: x for x in meta.get("variables", [])}
    if set(v) != {IND, TIME}:
        raise RuntimeError(f"the table's variables are not the two expected: {sorted(v)}")
    codes = [c for c, t in zip(v[IND]["values"], v[IND]["valueTexts"]) if t.replace("\xa0", " ").strip().endswith(", GWh")]
    if not codes:
        raise RuntimeError("no indicator in GWh in the table")
    return codes, v[TIME]["values"]


def query(meta):
    codes, months = gwh_codes(meta)
    sel = [(IND, codes), (TIME, months)]
    return {"query": [{"code": c, "selection": {"filter": "item", "values": vals}} for c, vals in sel], "response": {"format": "json-stat2"}}


def parse(js, base):
    dims = js.get("id")
    if sorted(dims or []) != sorted([IND, TIME]):
        raise RuntimeError(f"the answer's dimensions are not the two expected: {dims}")
    cats = []
    for d in dims:
        c = js["dimension"][d]["category"]
        idx = c["index"]
        codes = sorted(idx, key=idx.get) if isinstance(idx, dict) else list(idx)
        cats.append((d, codes, c.get("label", {})))
    n = 1
    for s in js["size"]:
        n *= s
    if len(js["value"]) != n:
        raise RuntimeError(f"{len(js['value'])} values for dimensions of size {js['size']}")
    labels = next(c[2] for c in cats if c[0] == IND)
    rows = []
    for k, combo in enumerate(itertools.product(*[c[1] for c in cats])):
        v = js["value"][k]
        if v is None:
            continue
        cell = dict(zip(dims, combo))
        code = cell[IND]
        label = labels[code].replace("\xa0", " ").strip()
        if not label.endswith(", GWh"):
            raise RuntimeError(f"an indicator not in GWh: {label!r}")
        m = re.fullmatch(r"(\d{4})M(\d\d)", cell[TIME])
        if not m:
            raise RuntimeError(f"a month not of the form YYYYMmm: {cell[TIME]!r}")
        rows.append(dict(entity="statee:ee", variable=slug(label), ts_utc=f"{m.group(1)}-{m.group(2)}-01T00:00:00Z", value=round(float(v) * 1000, 3),
                         unit="MWh", freq="P1M", geo="EE", market="", node=label, **base, x_code=code))
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no value in the answer")
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("an indicator and month given twice")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Estonia table KE21: Estonia's electricity production, imports and exports, a month")
    ap.add_argument("--offline", action="store_true", help="the saved metadata and answer only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host(HOST):
        print(f"{NAME}: the publisher is paused (warehouse/metadata/paused_sources.csv); nothing asked")
        return 0
    if args.out_dir:
        raw_dir = ip.RAW_DIR
        ip.set_out_dir(args.out_dir)
        ip.RAW_DIR = raw_dir
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{CONNECTOR}_{run_id}.log"))
    ip.RAW.open(CONNECTOR, run_id)
    results = []
    path = os.path.join(ip.RAW_DIR, CONNECTOR, SAVED)
    try:
        if args.offline:
            if not os.path.exists(path):
                raise RuntimeError(f"offline: no saved query at {path}")
            saved = json.load(open(path, encoding="utf-8"))
            meta, js, retrieved = saved["meta"], saved["answer"], saved["retrieved_at"]
            query(meta)
            log(f"  saved metadata and answer reused: {path} (retrieved {retrieved})")
        else:
            mcontent, _ = ip.fetch_raw(CONNECTOR, TABLE_URL, log, fresh=True, headers=UA, timeout=60, pause=1)
            meta = json.loads(mcontent.decode("utf-8-sig"))
            body = query(meta)
            r = requests.post(TABLE_URL, json=body, headers=UA, timeout=180)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code} for the query")
            js, retrieved = json.loads(r.content.decode("utf-8-sig")), ip.utc_iso(pd.Timestamp.now(tz="UTC"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            json.dump({"retrieved_at": retrieved, "query": body, "meta": meta, "answer": js}, open(path, "w", encoding="utf-8"))
            log(f"  POST {TABLE_URL}: {len(r.content)} bytes, saved with the metadata as {path}")
        upd = js.get("updated", "") or ""
        if upd.startswith("9999"):      # the API's placeholder, not a date (session 2278): no vintage
            upd = ""
        base = dict(source=SOURCE, source_url=TABLE_URL, retrieved_at=retrieved, vintage=upd)
        t = parse(js, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        g = t[t.variable == "total_electricity_production"].assign(y=lambda q: q.ts_utc.str[:4]).groupby("y").value.agg(["sum", "size"])
        g = g[g["size"] == 12]["sum"] / 1e6
        head = [
            "Energy Research Warehouse (ERW): Statistics Estonia, table KE21, Electricity production, imports, exports and sale, a month, "
            f"{t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]} (session 2278)",
            "Shape: series (docs/datastandard.md v0). entity statee:ee; variable the indicator in snake case, its unit dropped "
            "(total_electricity_production, electricity_production_from_hydro_energy, _wind_energy, _solar_energy, imports_of_electricity, "
            "exports_of_electricity); unit MWh (the table's GWh times 1,000); ts_utc the month's first day; freq P1M; geo EE; node the indicator "
            "as Statistics Estonia writes it; x_code its code.",
            f"{len(t)} rows, {t.variable.nunique()} indicators; total production TWh a full year: " + ", ".join(f"{k} {v:.2f}" for k, v in g.items() if k >= "2015")
            + ". Only the indicators in GWh are taken (the two shares of sold electricity are not). A cell left empty has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/statee_electricity.py; the query answered {retrieved}; updated {base['vintage'] or 'not given (the answer says 9999-12-31)'}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{SAVED} (the metadata and the answer; not in git)",
            f"Source: {SOURCE} Statistics Estonia, table KE21, {PAGE}",
            f"  access: {TABLE_URL} (the metadata by GET and one JSON-stat query by POST)",
            f"License: public (CC BY-SA 4.0, {TERMS}): a copy carries the same license. Source: Statistics Estonia.",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.variable.nunique()} indicators, {t.ts_utc.min()[:7]} to {t.ts_utc.max()[:7]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Estonia", report="Table KE21: Electricity production, imports, exports and sale (monthly)",
                                    report_url=PAGE, document_list=TABLE_URL, license="public", tables=[NAME])])  # CC BY-SA 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
