#!/usr/bin/env python3
"""Norway's hydropower reservoirs, a week, from 1995: the filling share, the stored energy and the capacity, for the
country, its five price areas and its water regions, as the Norwegian Water Resources and Energy Directorate (NVE)
publishes them through its reservoir statistics API (session 2516, chain 122: a source of the session's own choosing;
the ERW held Statnett's production and consumption, not the reservoirs).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/nve_norway_reservoirs_weekly.csv, from one
JSON answer (no key):

    https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData

    entity      nve:no:<area>: `no` (the country), `no1` to `no5` (the price areas, NVE's omrType EL), `region_<n>` (the
                water regions, omrType VASS)
    variable    filling_share (pct, fyllingsgrad times 100), stored_energy (MWh, fylling_TWh times 1,000,000),
                capacity (MWh, kapasitet_TWh times 1,000,000)
    ts_utc      the date NVE gives the week (dato_Id, the week's last day, 00:00 UTC): a stock at that date; freq P1W;
                geo NO
    node        NVE's area type and number, ISO year and week

Not taken: last week's share and the change (fyllingsgrad_forrige_uke, endring_fyllingsgrad), which the table's own rows
give. A field without a number has no row. An answer that is not a list, an area type other than NO, EL and VASS, a
week given twice for an area, or a date not of the form YYYY-MM-DD stops the run. Nothing is filled.

    python warehouse/connectors/nve_norway_reservoirs.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/nve_reservoirs/answer.json and read from there with --offline.
biapi.nve.no has no robots file (session 2516); www.nve.no asks a crawl delay of 20 seconds. License: public. NVE's
API documentation (api.nve.no/doc/magasinstatistikk): the data are licensed under the Norwegian Licence for Open
Government Data (NLOD), compatible with CC BY 3.0 Norway; NVE is to be named as the source.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "nve_norway_reservoirs_weekly"
CONNECTOR = "nve_reservoirs"
SOURCE = "nve:magasinstatistikk"
HOST = "biapi.nve.no"
URL = "https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData"
DOC = "https://api.nve.no/doc/magasinstatistikk/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
FIELDS = {"fyllingsgrad": ("filling_share", "pct", 100.0), "fylling_TWh": ("stored_energy", "MWh", 1e6),
          "kapasitet_TWh": ("capacity", "MWh", 1e6)}
X_COLS = ["x_iso_week"]


def area(rec):
    kind, nr = rec["omrType"], int(rec["omrnr"])
    if kind == "NO":
        return "no"
    if kind == "EL":
        return f"no{nr}"
    if kind == "VASS":
        return f"region_{nr}"
    raise RuntimeError(f"an area type other than NO, EL and VASS: {kind!r}")


def parse(answer, base):
    if not isinstance(answer, list):
        raise RuntimeError("the answer is not a list")
    rows, seen = [], set()
    for rec in answer:
        day = str(rec.get("dato_Id", ""))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            raise RuntimeError(f"a date not of the form YYYY-MM-DD: {day!r}")
        a = area(rec)
        if (a, day) in seen:
            raise RuntimeError(f"{a} {day} given twice")
        seen.add((a, day))
        week = f"{rec['iso_aar']}-W{int(rec['iso_uke']):02d}"
        for field, (var, unit, f) in FIELDS.items():
            v = rec.get(field)
            if v is None:
                continue
            rows.append(dict(entity=f"nve:no:{a}", variable=var, ts_utc=f"{day}T00:00:00Z", value=round(float(v) * f, 6), unit=unit,
                             freq="P1W", geo="NO", market="", node=f"{rec['omrType']} {rec['omrnr']}, {week}", **base, x_iso_week=week))
    t = pd.DataFrame(rows)
    if t.empty:
        raise RuntimeError("no value in the answer")
    return t


def get(offline, log):
    path = os.path.join(ip.RAW_DIR, CONNECTOR, "answer.json")
    if offline:
        if not os.path.exists(path):
            raise RuntimeError(f"offline: no saved answer at {path}")
        saved = json.load(open(path, encoding="utf-8"))
        log(f"  saved answer reused: {path} (retrieved {saved['retrieved_at']})")
        return saved["answer"], saved["retrieved_at"]
    r = requests.get(URL, headers=UA, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}")
    at = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    js = json.loads(r.content.decode("utf-8-sig"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump({"retrieved_at": at, "url": URL, "answer": js}, open(path, "w", encoding="utf-8"))
    log(f"  GET {URL}: {len(r.content)} bytes, saved as {path}")
    return js, at


def main(argv=None):
    ap = argparse.ArgumentParser(description="NVE: Norway's hydropower reservoirs a week, from 1995")
    ap.add_argument("--offline", action="store_true", help="the saved answer only, no request")
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
    results = []
    try:
        js, at = get(args.offline, log)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=at, vintage="")
        t = parse(js, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        n = t[(t.entity == "nve:no:no") & (t.variable == "filling_share")].set_index("ts_utc").value
        newest = n.index.max()
        head = [
            "Energy Research Warehouse (ERW): Norwegian Water Resources and Energy Directorate (NVE), reservoir statistics (magasinstatistikk), "
            f"Norway's hydropower reservoirs a week, {t.ts_utc.min()[:10]} to {t.ts_utc.max()[:10]} (session 2516)",
            "Shape: series (docs/datastandard.md v0). entity nve:no:<area> (no, the country; no1 to no5, the price areas; region_<n>, the water regions); "
            "variable filling_share (pct), stored_energy and capacity (MWh, from TWh); ts_utc the date NVE gives the week (its last day): a stock at that date; "
            "freq P1W; geo NO; node NVE's area type and number with the ISO week; x_iso_week the ISO week.",
            f"{len(t)} rows; the country's filling share on {newest[:10]}: {n[newest]:.1f} pct. Not taken: last week's share and the change. "
            "A field without a number has no row; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/nve_norway_reservoirs.py; the answer retrieved {at}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/answer.json (not in git)",
            f"Source: {SOURCE} NVE, reservoir statistics (magasinstatistikk), {DOC}",
            f"  access: {URL}",
            "License: public. NVE's API documentation: the data are licensed under the Norwegian Licence for Open Government Data (NLOD), "
            "compatible with CC BY 3.0 Norway. Credit: Norwegian Water Resources and Energy Directorate (NVE).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Norwegian Water Resources and Energy Directorate (NVE)",
                                    report="Reservoir statistics (magasinstatistikk): filling share, stored energy and capacity a week",
                                    report_url=DOC, document_list=URL, license="public", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
