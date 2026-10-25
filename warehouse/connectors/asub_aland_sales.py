#!/usr/bin/env python3
"""Aland's electricity sales a year by distributor and sector, with its exports, 1980 to 2025, as Statistics and Research Aland
(ASUB) publishes them in table MI010 ("Elforsaljningen efter ar, region, sald effekt och bransch") of its PxWeb database
(session 2670, chain 133, the session's third own choice; the ERW held ASUB's MI009, supply by origin, since session 2651, and
not its sales).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/asub_aland_electricity_sales_annual.csv, from
ASUB's PxWeb API (no key), one JSON-stat 2.0 query by POST, the GWh figures of every region, sector and year selected:

    https://pxweb.asub.ax/PXWeb/api/v1/sv/Statistik/MI/MI010.px

    entity      asub:ax:<region>:<sector>: region aland (all of Aland), mariehamns_energi (Mariehamn, Mariehamns Energi Ab),
                alands_elandelslag (the rural municipalities, Alands elandelslag) and export; sector total, households,
                agriculture, industry, services, public_sector
    variable    sales (exports for the region export)
    unit        MWh (the table's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo AX
    node        the region and the sector as ASUB names them (Swedish)

The years are 1980, 1985, 1990 and each year from 1994. A cell without a number has no row; nothing is filled. A table without
its year, region, statistic and sector dimensions, a region or sector not in the map, a year not of four digits, a value array
not the size of the dimensions, or a key given twice stops the run. The figures are whole GWh, so the checks allow their
rounding: a distributor's year whose five sectors miss its total by more than 3 GWh (the table's largest gap is 2), or whose two
distributors miss Aland's total by more than 1.5 GWh, stops the run. Exports, from 2018 (0 until 2021), are given as a total
only, and Mariehamn has no agriculture row. The per cent rows are not taken.

    python warehouse/connectors/asub_aland_sales.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/asub_ax/ (query_MI010.json, the answer with its time of retrieval) and read
from there with --offline. pxweb.asub.ax has no robots file (HTTP 404, sessions 2651 and 2670). License: CC BY 4.0, ASUB's terms
of use (www.asub.ax/sv/om-asub/om-asubax/anvandarvillkor, read in session 2651): public.
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

NAME = "asub_aland_electricity_sales_annual"
CONNECTOR = "asub_ax"
SOURCE = "asub_ax:MI010"
HOST = "pxweb.asub.ax"
URL = "https://pxweb.asub.ax/PXWeb/api/v1/sv/Statistik/MI/MI010.px"
TERMS = "https://www.asub.ax/sv/om-asub/om-asubax/anvandarvillkor"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEAR = "år"
STAT = "såld effekt"
REGIONS = {chr(0xC5) + "land, totalt": "aland", "Mariehamn (Mariehamns Energi Ab)": "mariehamns_energi",
           "Landskommunerna (" + chr(0xC5) + "lands elandelslag)": "alands_elandelslag", "Export": "export"}
SECTORS = {"Totalt": "total", "Hush" + chr(0xE5) + "ll": "households", "Jordbruk": "agriculture", "Industri": "industry",
           "Service": "services", "Offentlig sektor": "public_sector"}
X_COLS = []


def codes(cat):
    idx = cat["index"]
    return sorted(idx, key=idx.get) if isinstance(idx, dict) else list(idx)


def parse(js, base):
    dims = js.get("id") or []
    if sorted(dims) != sorted([YEAR, "region", STAT, "bransch"]):
        raise RuntimeError(f"the dimensions are {dims}")
    n = 1
    for s in js["size"]:
        n *= s
    if len(js["value"]) != n:
        raise RuntimeError(f"{len(js['value'])} values for dimensions of size {js['size']}")
    stat = js["dimension"][STAT]["category"]["label"]
    if list(stat.values()) != ["GWh (gigawattimmar)"]:
        raise RuntimeError(f"the statistic is not GWh alone: {stat}")
    lab = {d: js["dimension"][d]["category"]["label"] for d in dims}
    for d, m in (("region", REGIONS), ("bransch", SECTORS)):
        unknown = sorted(set(lab[d].values()) - set(m))
        if unknown:
            raise RuntimeError(f"a {d} not in the map: {unknown}")
    rows, gwh = [], {}
    for k, combo in enumerate(itertools.product(*[codes(js["dimension"][d]["category"]) for d in dims])):
        cell = dict(zip(dims, combo))
        v = js["value"][k]
        if v is None:
            continue
        y = lab[YEAR].get(cell[YEAR], cell[YEAR])
        if not re.fullmatch(r"\d{4}", str(y)):
            raise RuntimeError(f"a year not of four digits: {y!r}")
        rl, sl = lab["region"][cell["region"]], lab["bransch"][cell["bransch"]]
        region, sector = REGIONS[rl], SECTORS[sl]
        gwh[(int(y), region, sector)] = float(v)
        rows.append(dict(entity=f"asub:ax:{region}:{sector}", variable="exports" if region == "export" else "sales",
                         ts_utc=f"{y}-01-01T00:00:00Z", value=round(float(v) * 1000, 3), unit="MWh", freq="P1Y", geo="AX", market="",
                         node=f"{rl}: {sl}", **base))
    for y, region in sorted({(y, r) for y, r, _ in gwh}):
        if region == "export" or (y, region, "total") not in gwh:
            continue  # exports are given as a total only
        parts = [gwh[(y, region, s)] for s in SECTORS.values() if s != "total" and (y, region, s) in gwh]
        if parts and abs(sum(parts) - gwh[(y, region, "total")]) > 3:
            raise RuntimeError(f"{y} {region}: the sectors make {sum(parts):.2f} GWh, the total {gwh[(y, region, 'total')]}")
    for y in sorted({y for y, _, _ in gwh}):
        k = [(y, r, "total") for r in ("mariehamns_energi", "alands_elandelslag", "aland")]
        if all(x in gwh for x in k) and abs(gwh[k[0]] + gwh[k[1]] - gwh[k[2]]) > 1.5:
            raise RuntimeError(f"{y}: the two distributors make {gwh[k[0]] + gwh[k[1]]:.2f} GWh, Aland's total {gwh[k[2]]}")
    return rows


def get(offline, log):
    path = os.path.join(ip.RAW_DIR, CONNECTOR, "query_MI010.json")
    if offline:
        if not os.path.exists(path):
            raise RuntimeError(f"offline: no saved query at {path}")
        saved = json.load(open(path, encoding="utf-8"))
        log(f"  saved answer reused: {path} (retrieved {saved['retrieved_at']})")
        return saved["answer"], saved["retrieved_at"]
    body = {"query": [{"code": YEAR, "selection": {"filter": "all", "values": ["*"]}},
                      {"code": "region", "selection": {"filter": "all", "values": ["*"]}},
                      {"code": STAT, "selection": {"filter": "item", "values": ["GWh (gigawattimmar)"]}},
                      {"code": "bransch", "selection": {"filter": "all", "values": ["*"]}}],
            "response": {"format": "json-stat2"}}
    r = requests.post(URL, json=body, headers=UA, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} for MI010")
    at = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    js = json.loads(r.content.decode("utf-8-sig"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump({"retrieved_at": at, "url": URL, "query": body, "answer": js}, open(path, "w", encoding="utf-8"))
    log(f"  POST {URL}: {len(r.content)} bytes, saved as {path}")
    return js, at


def main(argv=None):
    ap = argparse.ArgumentParser(description="ASUB: Aland's electricity sales by distributor and sector a year")
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
        t = pd.DataFrame(parse(js, base))
        if t.empty:
            raise RuntimeError("no value in the answer")
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "ts_utc"]).reset_index(drop=True)
        tot = t[t.entity == "asub:ax:aland:total"].set_index("ts_utc").value
        head = [
            "Energy Research Warehouse (ERW): Statistics and Research Aland (ASUB), table MI010: Aland's electricity sales by "
            f"distributor and sector, with its exports, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2670)",
            "Shape: series (docs/datastandard.md v0). entity asub:ax:<region>:<sector>; variable sales (exports for the region "
            "export); unit MWh (the table's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo AX; node the region and "
            "the sector as ASUB names them.",
            f"{len(t)} rows; Aland's sales, GWh: " + ", ".join(f"{k[:4]} {v / 1e3:.1f}" for k, v in tot.items() if k[:4] in ("1980", "2000", "2025"))
            + ". Each region's sectors checked against its total; the years 1980, 1985, 1990 and from 1994; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/asub_aland_sales.py; the answer retrieved {at}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/query_MI010.json (not in git)",
            f"Source: {SOURCE} Statistics and Research Aland (ASUB), Elforsaljningen efter ar, region, sald effekt och bransch",
            f"  access: {URL} (one JSON-stat query by POST)",
            f"License: CC BY 4.0 (ASUB's terms of use, {TERMS}); credit: Statistics and Research Aland (ASUB).",
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
            ip.update_sources([dict(source=SOURCE, publisher="Statistics and Research Aland (ASUB)",
                                    report="Table MI010: Elforsaljningen (electricity sales by year, region, sector)", report_url=URL,
                                    document_list="https://pxweb.asub.ax/PXWeb/api/v1/sv/Statistik/MI", license="public",
                                    tables=[NAME])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
