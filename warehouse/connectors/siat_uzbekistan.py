#!/usr/bin/env python3
"""Uzbekistan's electricity production by region from 2010, its solar and wind production from 2015, and its gross
electricity consumption by region from 2016, a year, from the national statistics agency's open data portal SIAT
(siat.stat.uz; session 2451, chain 118: Uzbekistan's electricity).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/siat_uzbekistan_electricity_annual.csv,
from four indicator files (JSON), four requests:

    https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_440.json   1.02.02.0004 Volume of electricity production
    https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_446.json   1.02.02.0006 ... produced by solar power plants
    https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_458.json   1.02.02.0007 ... produced by wind power farms
    https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_2684.json  1.02.02.0019 Volume of electricity consumption by
                                                                     subscribers ("gross electricity consumption")
    (each listed on https://siat.stat.uz/data/<id>/?lang=en, whose download button names the file)

    entity    siat:UZ (the Republic of Uzbekistan) or siat:UZ:<SOATO code> (a region, Tashkent city among them)
    variable  generation (440), generation_solar (446, the republic only), generation_wind (458, the republic only),
              consumption (2684), all MWh (the files' "Million kWt hour", that is million kWh, times 1,000)
    ts_utc    the year's 1 January; freq P1Y; geo UZ or the region's ISO 3166-2 code; node the region's English name
    x_region_code the file's SOATO code

The files' notes: production 2010 to 2022 final, 2023 preliminary, the republic including data not allocated to a region;
solar and wind collected since 2015, 2023 preliminary; consumption collected since 2016, 2023 preliminary. Zeros are kept
as published (wind is 0.0 in most years to 2022). The wind file has a column keyed "2022.1" besides "2022" (0.0 in
both), which is not taken. Checks, each stopping the run: the indicator's code and unit are as read; a region not in the
map; a value that is not a number; the regions adding to more than the republic, beyond 1 GWh. The republic's excess
over its regions is data not allocated to a region (production: 34.1 GWh in 2017, 31.7 in 2019, 19.8 in 2016, 0.6 in 2022 to 2024); the
header names the largest.

    python warehouse/connectors/siat_uzbekistan.py [--offline] [--out-dir DIR]

Ceiling: four requests, reused from warehouse/raw/siat_uzbekistan/ with --offline. siat.stat.uz's and
api.siat.stat.uz's robots files allow every path, ClaudeBot, Claude-Web and anthropic-ai named among the allowed
(session 2451). License: public, CC BY 4.0 (indicator 440's page: "Litsenziya: CC BY 4.0", the source line naming the Statistics Agency;
the other three pages were not read, and the files carry no license field). Source: National Statistics
Committee of the Republic of Uzbekistan, SIAT.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "siat_uzbekistan_electricity_annual"
CONNECTOR = "siat_uzbekistan"
SOURCE = "siat:electricity"
PAGE = "https://siat.stat.uz/data/440/?lang=en"
BASE = "https://api.siat.stat.uz/media/uploads/sdmx/sdmx_data_{}.json"
INDICATORS = {440: ("1.02.02.0004", "generation"), 446: ("1.02.02.0006", "generation_solar"),
              458: ("1.02.02.0007", "generation_wind"), 2684: ("1.02.02.0019", "consumption")}
REGIONS = {"Republic of Uzbekistan": "UZ", "Republic of Karakalpakstan": "UZ-QR", "Andijan region": "UZ-AN",
           "Bukhara region": "UZ-BU", "Jizzakh region": "UZ-JI", "Kashkadarya region": "UZ-QA", "Navoi region": "UZ-NW",
           "Namangan region": "UZ-NG", "Samarkand region": "UZ-SA", "Surkhandarya region": "UZ-SU",
           "Syrdarya region": "UZ-SI", "Tashkent region": "UZ-TO", "Fergana region": "UZ-FA", "Khorezm region": "UZ-XO",
           "Tashkent city": "UZ-TK"}
TOL = 1.0   # GWh
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url",
        "retrieved_at", "vintage", "x_region_code"]


def meta(item, name):
    for m in item["metadata"]:
        if (m.get("name_en") or "").strip() == name:
            return str(m.get("value_en") or m.get("value") or "").strip()
    raise RuntimeError(f"metadata {name!r} not found")


def indicator(content, iid):
    data = json.loads(content)
    if not isinstance(data, list) or len(data) != 1:
        raise RuntimeError(f"{iid}: not one indicator")
    item = data[0]
    code, var = INDICATORS[iid]
    if meta(item, "Indicator identification number (code)") != code:
        raise RuntimeError(f"{iid}: the code is {meta(item, 'Indicator identification number (code)')!r}, not {code}")
    if meta(item, "Unit of measurement").lower() != "million kwt hour":
        raise RuntimeError(f"{iid}: the unit is {meta(item, 'Unit of measurement')!r}")
    out = {}
    for r in item["data"]:
        name = (r.get("Klassifikator_en") or "").strip()
        if name not in REGIONS:
            raise RuntimeError(f"{iid}: a region not in the map: {name!r}")
        for k, v in r.items():
            if not re.fullmatch(r"(19|20)\d\d", k):
                continue   # the wind file's "2022.1" and the names
            if v is None or v == "":
                continue
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise RuntimeError(f"{iid} {name} {k}: not a number: {v!r}")
            out[(name, str(r.get("Code")), int(k))] = float(v)
    years = {y for (_, _, y) in out}
    unallocated = 0.0
    for y in years:
        rep = out.get(("Republic of Uzbekistan", "1700", y))
        regs = [v for (n, _, yy), v in out.items() if yy == y and n != "Republic of Uzbekistan"]
        if rep is not None and regs:
            if sum(regs) - rep > TOL:
                raise RuntimeError(f"{iid} {y}: the regions add to {sum(regs)}, more than the republic's {rep}")
            unallocated = max(unallocated, rep - sum(regs))
    return var, out, meta(item, "Note"), unallocated


def finish(rows):
    t = pd.DataFrame(rows, columns=COLS)
    if t.duplicated(["entity", "variable", "ts_utc"]).any():
        raise RuntimeError("a key given twice")
    return t.sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="SIAT Uzbekistan: electricity production and consumption by region, a year")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
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
        if not args.offline and (ip.paused("siat") or ip.paused_host("api.siat.stat.uz")):
            raise RuntimeError("SIAT is paused (warehouse/metadata/paused_sources.csv): not requested")
        rows, notes, got = [], [], []
        for iid in INDICATORS:
            url = BASE.format(iid)
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, pause=2, headers=UA, timeout=120)
            var, vals, note, unalloc = indicator(content, iid)
            notes.append(f"{INDICATORS[iid][0]}: {note}" + (f" (the largest part not allocated to a region: {unalloc:.1f} million kWh)." if unalloc else ""))
            for (name, code, y), v in vals.items():
                rows.append(dict(entity="siat:UZ" if code == "1700" else f"siat:UZ:{code}", variable=var, ts_utc=f"{y}-01-01T00:00:00Z",
                                 value=round(v * 1000.0, 3), unit="MWh", freq="P1Y", geo=REGIONS[name], market="", node=name,
                                 source=SOURCE, source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec),
                                 x_region_code=code))
            got.append(rec.get("retrieved_at") or "")
        t = finish(rows)
        header = [
            f"Energy Research Warehouse (ERW): National Statistics Committee of the Republic of Uzbekistan, SIAT open data, electricity production by region, solar and wind production, and gross consumption by region, {t.ts_utc.min()[:4]} to {t.ts_utc.max()[:4]} (session 2451)",
            "Shape: series (docs/datastandard.md v0). entity siat:UZ or siat:UZ:<SOATO code>; variable generation (1.02.02.0004), generation_solar (1.02.02.0006, the republic only), generation_wind (1.02.02.0007, the republic only), "
            "consumption (1.02.02.0019, \"Volume of electricity consumption by subscribers\", which the file's note calls gross; undefined, and 19 to 24 per cent below production in most years), MWh (the files' million kWh times 1,000); ts_utc the year's 1 January; freq P1Y; geo UZ or ISO 3166-2; x_region_code SOATO. "
            "The regions are parts of the republic, which also holds data not allocated to a region: a sum takes one level.",
            f"{len(t)} rows. The regions never add to more than the republic (within 1 GWh); the republic's excess is data not allocated to a region. Zeros are kept as published; the wind file's column \"2022.1\" (0.0) is not taken. 2018's consumption (60,744.7 million kWh) is out of line with 2017 and 2019 in 13 of 14 areas, as published. The files' notes, which stop at 2023 (2024 and 2025 have no stated status): " + " ".join(notes),
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/siat_uzbekistan.py; the files retrieved {min(got)} to {max(got)}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} National Statistics Committee of the Republic of Uzbekistan, SIAT, indicators 1.02.02.0004, 0006, 0007 and 0019, {PAGE}",
            f"  access: {BASE.format(440)} and the three others (446, 458, 2684)",
            "License: public, CC BY 4.0 (indicator 440's page). Source: the Statistics Agency of the Republic of Uzbekistan (the page's source line), siat.stat.uz.",
        ]
        ip.write_csv(t, NAME, header, log, cols=COLS)
        if not args.out_dir:
            ip.update_sources([dict(source=SOURCE, publisher="National Statistics Committee of the Republic of Uzbekistan (SIAT)",
                                    report="SIAT open data: electricity production (1.02.02.0004), solar (0006), wind (0007), consumption by subscribers (0019)",
                                    report_url=PAGE, document_list=BASE.format(440), license="public", tables=[NAME])])
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} entities")
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
