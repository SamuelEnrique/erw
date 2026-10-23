#!/usr/bin/env python3
"""The World Bank's World Development Indicators for electricity: each country's access to electricity, and the IEA's
electric power consumption per person and renewable share of output as the World Bank republishes them, a year
(session 2150, chain 092: the world's electricity access, beside the U.S. tables).

Energy Research Warehouse (ERW) connector. Two series tables from the World Bank's Indicators API v2 (no key):

    https://api.worldbank.org/v2/country/all/indicator/<id>?format=json&date=2000:<year>&per_page=20000
    https://api.worldbank.org/v2/country?format=json&per_page=400      (the economies, to leave the aggregates out)

    wb_electricity_access_annual   EG.ELC.ACCS.ZS, access to electricity, percent of population (pct), the World Bank's
               own (its SDG 7.1.1 electrification dataset): public, CC BY 4.0
    wb_iea_electricity_annual      EG.USE.ELEC.KH.PC, electric power consumption (kWh/person) and EG.ELC.RNEW.ZS, renewable
               electricity output, percent of total output (pct), both sourced by the World Bank to the IEA's Energy
               Statistics: internal until the IEA's terms are read (the World Bank's licence holds "unless indicated
               otherwise in the data or indicator metadata", and the metadata names the IEA as the source)

    entity wb:<ISO3>; variable access_to_electricity, electricity_consumption_per_person, renewable_output_share; ts_utc
    1 January of the year; freq P1Y; geo the economy's ISO2 code (the World Bank's); node the economy's name;
    x_indicator the World Bank's id; x_region, x_income the World Bank's groups

Aggregates (regions, income groups, the world: the economies list's region "NA") have no row. A value the World Bank
leaves empty has no row. An answer whose page count is not one, or whose total differs from its rows, stops the run;
so does an economy given twice in a year. Nothing is filled.

    python warehouse/connectors/wb_wdi_electricity.py [--offline] [--out-dir DIR]

Ceiling: four requests (the economies and one an indicator), saved in warehouse/raw/wb_wdi_electricity/; asked again
unless --offline. api.worldbank.org has no robots file (HTTP 404). License: the World Bank's (read 141, CC BY 4.0 unless
the metadata says otherwise); the IEA's indicators held internal, as above.
"""

import argparse
import datetime as dt
import json
import os
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

CONNECTOR = "wb_wdi_electricity"
HOST = "api.worldbank.org"
API = "https://api.worldbank.org/v2/"
FIRST = 2000
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
X_COLS = ["x_indicator", "x_region", "x_income"]
# indicator: (table, variable, unit)
INDICATORS = {"EG.ELC.ACCS.ZS": ("wb_electricity_access_annual", "access_to_electricity", "pct"),
              "EG.USE.ELEC.KH.PC": ("wb_iea_electricity_annual", "electricity_consumption_per_person", "kWh/person"),
              "EG.ELC.RNEW.ZS": ("wb_iea_electricity_annual", "renewable_output_share", "pct")}
TABLES = {"wb_electricity_access_annual": ("worldbank:wdi_electricity_access", "public"),
          "wb_iea_electricity_annual": ("worldbank:wdi_iea_electricity", "internal")}


def economies(answer):
    meta, rows = answer
    if int(meta.get("pages", 0)) != 1 or int(meta["total"]) != len(rows):
        raise RuntimeError(f"the economies list is not one whole page: {meta}")
    return {r["id"]: r for r in rows if r["region"]["id"] != "NA"}


def parse(answer, ind, econ, base):
    meta, rows = answer
    if int(meta.get("pages", 0)) != 1 or int(meta["total"]) != len(rows):
        raise RuntimeError(f"{ind}: not one whole page: {meta}")
    table, var, unit = INDICATORS[ind]
    out, seen = [], set()
    for r in rows:
        if r["indicator"]["id"] != ind:
            raise RuntimeError(f"{ind}: a row of {r['indicator']['id']}")
        iso3 = r["countryiso3code"]
        if iso3 not in econ or r["value"] is None:
            continue
        key = (iso3, r["date"])
        if key in seen:
            raise RuntimeError(f"{ind}: {key} given twice")
        seen.add(key)
        e = econ[iso3]
        out.append(dict(base, entity=f"wb:{iso3}", variable=var, ts_utc=f"{int(r['date'])}-01-01T00:00:00Z", value=float(r["value"]),
                        unit=unit, freq="P1Y", geo=e["iso2Code"], market="", node=e["name"], x_indicator=ind,
                        x_region=e["region"]["value"].strip(), x_income=e["incomeLevel"]["value"].strip()))
    if not out:
        raise RuntimeError(f"{ind}: no economy with a value")
    return out, meta.get("lastupdated", "")


def main(argv=None):
    ap = argparse.ArgumentParser(description="The World Bank's electricity indicators by country")
    ap.add_argument("--offline", action="store_true", help="the saved files only, no request")
    ap.add_argument("--out-dir", help="a trial: the tables under this folder, not warehouse/output")
    ap.add_argument("--last", type=int, default=2025, help="the last year asked (default 2025)")
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
        if ip.paused(CONNECTOR) or ip.paused_host(HOST):
            raise RuntimeError(f"{HOST} is paused (warehouse/metadata/paused_sources.csv): no request made")
        ec, _ = ip.fetch_raw(CONNECTOR, f"{API}country?format=json&per_page=400", log, offline=args.offline, fresh=not args.offline,
                             headers=UA, timeout=120, pause=1)
        econ = economies(json.loads(ec))
        frames = {t: [] for t in TABLES}
        updated, urls = {}, {t: [] for t in TABLES}
        for ind, (table, _, _) in INDICATORS.items():
            url = f"{API}country/all/indicator/{ind}?format=json&date={FIRST}:{args.last}&per_page=20000"
            content, rec = ip.fetch_raw(CONNECTOR, url, log, offline=args.offline, fresh=not args.offline, headers=UA, timeout=180, pause=1)
            base = dict(source=TABLES[table][0], source_url=url, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
            got, last = parse(json.loads(content), ind, econ, base)
            log(f"  {ind}: {len(got):,} rows, the World Bank's last update {last}")
            frames[table] += got
            updated[ind] = last
            urls[table].append(url)
        cols = ip.SERIES_COLS + X_COLS
        for table, (source, lic) in TABLES.items():
            s = pd.DataFrame(frames[table])
            if s.duplicated(["entity", "variable", "ts_utc"]).any():
                raise RuntimeError(f"{table}: an (entity, variable, ts_utc) given twice")
            s = s[cols].sort_values(["entity", "variable", "ts_utc"]).reset_index(drop=True)
            inds = [i for i, v in INDICATORS.items() if v[0] == table]
            lic_line = ("License: public (the World Bank: CC BY 4.0; see license_verdicts.csv). Cite the World Bank, World Development "
                        "Indicators, and its SDG 7.1.1 electrification dataset." if lic == "public" else
                        "License: internal (the World Bank republishes these from the IEA's Energy Statistics, and its licence holds unless "
                        "the metadata says otherwise; held until the IEA's terms are read). Cite the IEA, via the World Bank.")
            head = [
                f"Energy Research Warehouse (ERW): the World Bank, World Development Indicators, {', '.join(inds)}, each economy a year, "
                f"{s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]} (session 2150)",
                "Shape: series (docs/datastandard.md v0). entity wb:<ISO3>; variables " + ", ".join(sorted(s.variable.unique())) +
                "; freq P1Y; ts_utc 1 January; geo the World Bank's ISO2 code; node the economy; x_indicator; x_region; x_income.",
                f"{s.entity.nunique()} economies; the World Bank's aggregates (regions, income groups, the world) have no row; an empty value has "
                f"no row. The World Bank's last updates: {', '.join(f'{i} {updated[i]}' for i in inds)}. Nothing is filled.",
                f"Retrieved: {run_id} (UTC) by warehouse/connectors/wb_wdi_electricity.py",
                f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
                f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
                f"Source: {source} The World Bank, World Development Indicators (Indicators API v2), {API}",
                f"  access: {', '.join(urls[table])}",
                lic_line,
            ]
            ip.write_snapshot(s, table, head, log, cols)
            results.append(dict(table=table, market="all", status="ok", detail=f"{len(s)} rows"))
            print(f"{table}: {len(s):,} rows, {s.entity.nunique()} economies, {s.ts_utc.min()[:4]} to {s.ts_utc.max()[:4]}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{CONNECTOR} FAILED, no output file written:\n{tb}")
        print(f"{CONNECTOR} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=CONNECTOR, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and all(r["status"] == "ok" for r in results):
            ip.update_sources([dict(source=src, publisher="World Bank", report="World Development Indicators (Indicators API v2): " +
                                    ", ".join(i for i, v in INDICATORS.items() if v[0] == t), report_url=API, document_list=API,
                                    license=lic, tables=[t]) for t, (src, lic) in TABLES.items()])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
