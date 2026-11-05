#!/usr/bin/env python3
"""Norway's electricity balance, a month from January 1993, as Statistics Norway publishes it (table 14091): generation
by source, imports, exports, losses and consumption by industry and households (session 2227, chain 099: Norway's
hydro-led grid, coupled to Europe's, beside Eurostat's figures in eurostat_electricity_monthly).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ssb_norway_electricity_monthly.csv, from
Statistics Norway's PxWeb API (no key): the table's metadata by GET and one JSON query by POST, to the same address:

    https://data.ssb.no/api/v0/en/table/14091   "Electricity balance (MWh), by production and consumption, contents and
                                                month": Produk2 (the 26 lines), ContentsCode Kraft, Tid (1993M01 on)

    entity      ssb:norway
    variable    the line's English name in snake case (total_electricity_generation, hydro_power_generation,
                wind_power_generation, solar_power_generation, thermal_power_generation, import, export,
                gross_electricity_consumption, pump_storage_consumption, grid_loss_and_statistical_difference,
                net_electricity_consumption and its industries and households, as SSB names them); node the name as SSB
                writes it; x_code SSB's code for the line (1, 1.1, ..., 7.42)
    unit        MWh, as SSB gives it; ts_utc the month's first day; freq P1M; geo NO

A cell SSB leaves empty ("." or "..") has no row; a 0 SSB gives is kept. Totals are SSB's lines, never sums made here.
A metadata without the three variables, a month not of the form YYYYMmm, a value that is not a number, a line given twice
or a query answer of another form stops the run. Nothing is filled.

    python warehouse/connectors/ssb_electricity.py [--offline] [--out-dir DIR]

Ceiling: two requests (the metadata and the query), saved together in warehouse/raw/ssb_electricity/ (one address serves
both) and reused offline. data.ssb.no's robots.txt redirects to www.ssb.no/api; www.ssb.no's robots file disallows
/a/kostra/stt only (session 2227). License: CC BY 4.0, as www.ssb.no/api states for SSB's APIs ("I likhet med resten av
ssb.no benytter API-ene lisensen CC BY 4.0", read in session 2227); cite Statistics Norway, table 14091.
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

NAME = "ssb_norway_electricity_monthly"
CONNECTOR = "ssb_electricity"
SOURCE = "ssb:14091"
TABLE_URL = "https://data.ssb.no/api/v0/en/table/14091"
PAGE = "https://www.ssb.no/en/statbank/table/14091"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
SAVED = "query_14091.json"
X_COLS = ["x_code"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def query(meta):
    """The JSON query of every line and month of the table."""
    codes = {v["code"]: v for v in meta.get("variables", [])}
    if set(codes) != {"Produk2", "ContentsCode", "Tid"}:
        raise RuntimeError(f"the table's variables are not the three expected: {sorted(codes)}")
    sel = [(c, codes[c]["values"]) for c in ("Produk2", "ContentsCode", "Tid")]
    return {"query": [{"code": c, "selection": {"filter": "item", "values": v}} for c, v in sel], "response": {"format": "json"}}


def parse(answer, meta, base):
    """The PxWeb json answer as rows; and the count of empty cells."""
    names = {c: t for v in meta["variables"] if v["code"] == "Produk2" for c, t in zip(v["values"], v["valueTexts"])}
    cols = [c["code"] for c in answer.get("columns", [])]
    if "Produk2" not in cols or "Tid" not in cols or "data" not in answer:
        raise RuntimeError(f"the answer is not of the form asked: columns {cols}")
    ip_, it = cols.index("Produk2"), cols.index("Tid")
    rows, empty = [], 0
    for d in answer["data"]:
        code, tid = d["key"][ip_], d["key"][it]
        m = re.fullmatch(r"(\d{4})M(\d\d)", tid)
        if not m:
            raise RuntimeError(f"a month not of the form YYYYMmm: {tid!r}")
        if code not in names:
            raise RuntimeError(f"a line not in the metadata: {code!r}")
        v = d["values"][0]
        if v in (".", "..", "...", ":", "-", ""):
            empty += 1
            continue
        try:
            value = float(v)
        except ValueError:
            raise RuntimeError(f"{code} {tid}: not a number: {v!r}")
        rows.append(dict(entity="ssb:norway", variable=slug(names[code]), ts_utc=f"{m.group(1)}-{m.group(2)}-01T00:00:00Z", value=value,
                         unit="MWh", freq="P1M", geo="NO", market="", node=names[code], **base, x_code=code))
    return pd.DataFrame(rows), empty


def saved_path():
    return os.path.join(ip.RAW_DIR, CONNECTOR, SAVED)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Statistics Norway table 14091: Norway's electricity balance, a month")
    ap.add_argument("--offline", action="store_true", help="the saved metadata and answer only, no request")
    ap.add_argument("--out-dir", help="a trial: the table under this folder, not warehouse/output")
    args = ap.parse_args(argv)
    if ip.paused(CONNECTOR) or ip.paused_host("data.ssb.no"):
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
    try:
        if args.offline:
            path = saved_path()
            if not os.path.exists(path):
                raise RuntimeError(f"offline: no saved query at {path}")
            saved = json.load(open(path, encoding="utf-8"))
            meta, answer, retrieved = saved["meta"], saved["answer"], saved["retrieved_at"]
            query(meta)
            log(f"  saved metadata and answer reused: {path} (retrieved {retrieved})")
        else:
            mcontent, _ = ip.fetch_raw(CONNECTOR, TABLE_URL, log, fresh=True, headers=UA, timeout=60, pause=1)
            meta = json.loads(mcontent.decode("utf-8"))
            body = query(meta)
            r = requests.post(TABLE_URL, json=body, headers=UA, timeout=180)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code} for the query")
            answer, retrieved = r.json(), ip.utc_iso(pd.Timestamp.now(tz="UTC"))
            os.makedirs(os.path.dirname(saved_path()), exist_ok=True)
            json.dump({"retrieved_at": retrieved, "query": body, "meta": meta, "answer": answer}, open(saved_path(), "w", encoding="utf-8"))
            log(f"  POST {TABLE_URL}: {len(r.content)} bytes, saved with the metadata as {saved_path()}")
        updated = ((answer.get("metadata") or [{}])[0] or {}).get("updated", "") or ""  # SSB's "updated", in the answer
        base = dict(source=SOURCE, source_url=TABLE_URL, retrieved_at=retrieved, vintage=updated)
        s, empty = parse(answer, meta, base)
        if s.empty:
            raise RuntimeError("no value in the answer")
        if s.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a line and month given twice")
        cols = ip.SERIES_COLS + X_COLS
        s = s[cols].sort_values(["variable", "ts_utc"]).reset_index(drop=True)
        gen = s[s.variable == "total_electricity_generation"]
        y = gen.groupby(gen.ts_utc.str[:4]).value.agg(["sum", "size"])
        y = y[y["size"] == 12]["sum"] / 1e6
        head = [
            f"Energy Research Warehouse (ERW): Statistics Norway (SSB), table 14091, Electricity balance (MWh), by production and consumption, a month, "
            f"{s.ts_utc.min()[:7]} to {s.ts_utc.max()[:7]} (session 2227)",
            "Shape: series (docs/datastandard.md v0). entity ssb:norway; variable the line's English name in snake case (generation by source, import, "
            "export, gross and net consumption, losses, consumption by industry and households); unit MWh as SSB gives it; ts_utc the month's first day; "
            "freq P1M; geo NO; node the name as SSB writes it; x_code SSB's code for the line.",
            f"{len(s)} rows, {s.variable.nunique()} lines; total generation TWh a full year: "
            + ", ".join(f"{k} {v:.1f}" for k, v in y.items() if k >= "2010") + f". {empty} empty cells have no row. Totals are SSB's lines, never "
            "sums made here; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ssb_electricity.py; the query answered {retrieved}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/{SAVED} (the metadata and the answer; not in git)",
            f"Source: {SOURCE} Statistics Norway, table 14091, {PAGE}",
            f"  access: {TABLE_URL} (the metadata by GET and one JSON query by POST)",
            "License: public (CC BY 4.0, as www.ssb.no/api states for SSB's APIs). Source: Statistics Norway, table 14091.",
        ]
        ip.write_snapshot(s, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(s)} rows"))
        print(f"{NAME}: {len(s)} rows, {s.variable.nunique()} lines, {empty} empty")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Statistics Norway (SSB)", report="Table 14091: Electricity balance (MWh)",
                                    report_url=PAGE, document_list=TABLE_URL, license="public", tables=[NAME])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
