#!/usr/bin/env python3
"""Spain's dwellings by their intensity of use, measured by their electricity consumption, for the nation, its 19 autonomous
communities and cities, its 52 provinces and 3,185 municipalities, as Spain's National Statistics Institute (INE) gives them in
the 2021 Population and Housing Census, table "Viviendas según su intensidad de uso" (JAXI tpx 59531) (session 2765, chain 140:
INE, Spain's national statistics office, beside Red Electrica's national balance, held since chain 058).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/ine_es_dwellings_electricity_2021.csv, from one
file (no key), the table's CSV export (semicolon-separated, the thousands marked with points):

    https://www.ine.es/jaxi/files/tpx/es/csv_bdsc/59531.csv

    entity      ine_viv:es (Spain), ine_viv:ccaa_<code> (an autonomous community or city), ine_viv:prov_<code> (a province) or
                ine_viv:mun_<code> (a municipality), INE's codes
    variable    dwellings_total, dwellings_empty, dwellings_low_consumption, dwellings_occasional_use (with its two bands,
                dwellings_occasional_251_500_kwh and dwellings_occasional_501_750_kwh), the consumption bands
                dwellings_751_1000_kwh to dwellings_9001_10000_kwh and dwellings_over_10000_kwh (unit count), and
                median_annual_consumption (MWh per dwelling: INE's kWh divided by 1,000)
    ts_utc      2021-01-01T00:00:00Z, the 2021 census; freq P1Y; geo ES; node the area's code and name and the item as INE
                writes them; x_level nation, ccaa, province or municipality

The census classes each dwelling by its electricity consumption over a year: empty, low consumption, occasional use (251 to 750
kWh) and the bands above. The file states no year column; the table page names the 2021 census and says the data were updated
on 22 November 2024.

Checks that stop the run, exact, for every area: the dwellings total is the empty, low-consumption and occasional-use dwellings
and the eleven bands from 751 kWh; occasional use is its two bands; and each count of a nation, community and province is the
sum of its parts (communities, provinces, municipalities). A header not INE's, an item not in the eighteen, an area or item given
twice, or a value not a number stops the run. Nothing is filled.

    python warehouse/connectors/ine_es_dwellings_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/ine_es/ and reused unless --fresh; --offline asks nothing. www.ine.es's
robots file closes cgi-bin, search, test and admin paths and names no Claude agent (session 2765, read 1519). License: INE's
legal notice (read 1529): CC BY 4.0, commercial use included, cited as "Elaboracion propia con datos extraidos del sitio web del
INE: www.ine.es" with the date of the data's last update.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "ine_es_dwellings_electricity_2021"
CONNECTOR = "ine_es"
SOURCE = "ine_es:jaxi_tpx_59531"
HOST = "www.ine.es"
URL = "https://www.ine.es/jaxi/files/tpx/es/csv_bdsc/59531.csv"
PAGE = "https://www.ine.es/jaxi/Tabla.htm?tpx=59531"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("Instituto Nacional de Estadistica (INE), Censo de Poblacion y Viviendas 2021, Viviendas segun su intensidad de uso "
            "(viviendas por intensidad de uso a partir del consumo electrico), data updated 22 November 2024")
HEADER = ["Total Nacional", "Comunidades y Ciudades Autónomas", "Provincias", "Municipios", "Consumo eléctrico", "Total"]
ITEMS = {"Viviendas totales": "dwellings_total", "Viviendas vacías": "dwellings_empty",
         "Mediana consumo anual": "median_annual_consumption", "Viviendas con bajo consumo": "dwellings_low_consumption",
         "Viviendas de uso esporádico": "dwellings_occasional_use",
         "Viviendas de uso esporádico (entre 251 y 500 kwh)": "dwellings_occasional_251_500_kwh",
         "Viviendas de uso esporádico (entre 501 y 750 kwh)": "dwellings_occasional_501_750_kwh",
         "Viviendas con consumo entre 751 y 1.000 kwh": "dwellings_751_1000_kwh",
         "Viviendas con consumo entre 1.001 y 2.000 kwh": "dwellings_1001_2000_kwh",
         "Viviendas con consumo entre 2.001 y 3.000 kwh": "dwellings_2001_3000_kwh",
         "Viviendas con consumo entre 3.001 y 4.000 kwh": "dwellings_3001_4000_kwh",
         "Viviendas con consumo entre 4.001 y 5.000 kwh": "dwellings_4001_5000_kwh",
         "Viviendas con consumo entre 5.001 y 6.000 kwh": "dwellings_5001_6000_kwh",
         "Viviendas con consumo entre 6.001 y 7.000 kwh": "dwellings_6001_7000_kwh",
         "Viviendas con consumo entre 7.001 y 8.000 kwh": "dwellings_7001_8000_kwh",
         "Viviendas con consumo entre 8.001 y 9.000 kwh": "dwellings_8001_9000_kwh",
         "Viviendas con consumo entre 9.001 y 10.000 kwh": "dwellings_9001_10000_kwh",
         "Viviendas con consumo mayor de 10.000 kwh": "dwellings_over_10000_kwh"}
BANDS = [v for k, v in ITEMS.items() if k.startswith("Viviendas con consumo")]
PARTS = ["dwellings_empty", "dwellings_low_consumption", "dwellings_occasional_use"] + BANDS
COUNTS = [v for v in ITEMS.values() if v != "median_annual_consumption"]
TS = "2021-01-01T00:00:00Z"
X_COLS = ["x_level"]


def number(s, where):
    t = s.strip().replace(".", "").replace(",", ".")
    if not re.fullmatch(r"\d+(\.\d+)?", t):
        raise RuntimeError(f"{where}: not a number: {s!r}")
    return float(t)


def area(r):
    """(level, code, name) of a row from its four area cells, each "<code> <name>" or blank, the innermost filled."""
    for level, cell in (("municipality", r[3]), ("province", r[2]), ("ccaa", r[1])):
        if cell.strip():
            code, _, name = cell.strip().partition(" ")
            if not code.isdigit() or not name:
                raise RuntimeError(f"an area not '<code> <name>': {cell!r}")
            return level, code, name
    if r[0].strip() != "Total Nacional":
        raise RuntimeError(f"a row with no area: {r!r}")
    return "nation", "es", "Total Nacional"


def parse(content):
    d = pd.read_csv(io.BytesIO(content), sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False)
    if list(d.columns) != HEADER:
        raise RuntimeError(f"the header is not INE's: {list(d.columns)}")
    vals, names, parent = {}, {}, {}
    for r in d.itertuples(index=False):
        level, code, name = area(r)
        item = r[4].strip()
        if item not in ITEMS:
            raise RuntimeError(f"an item not expected: {item!r}")
        key = (level, code)
        if (key, ITEMS[item]) in vals:
            raise RuntimeError(f"{key} {item} given twice")
        vals[(key, ITEMS[item])] = number(r[5], f"{code} {item}")
        names[key] = name
        up = (("province", r[2].split(" ", 1)[0]) if level == "municipality" else
              ("ccaa", r[1].split(" ", 1)[0]) if level == "province" else ("nation", "es") if level == "ccaa" else None)
        if up and parent.setdefault(key, up) != up:
            raise RuntimeError(f"{key} has two parents")
    areas = sorted(names)
    for a in areas:
        if any((a, v) not in vals for v in ITEMS.values()):
            raise RuntimeError(f"{a} lacks an item")
        if vals[(a, "dwellings_total")] != sum(vals[(a, p)] for p in PARTS):
            raise RuntimeError(f"{a}: the dwellings total is not its classes")
        if vals[(a, "dwellings_occasional_use")] != vals[(a, "dwellings_occasional_251_500_kwh")] + vals[(a, "dwellings_occasional_501_750_kwh")]:
            raise RuntimeError(f"{a}: occasional use is not its two bands")
    kids = {}
    for k, p in parent.items():
        kids.setdefault(p, []).append(k)
    for p, ks in kids.items():
        for v in COUNTS:
            if vals[(p, v)] != sum(vals[(k, v)] for k in ks):
                raise RuntimeError(f"{p} {v}: its parts make {sum(vals[(k, v)] for k in ks):,.0f}, it {vals[(p, v)]:,.0f}")
    return vals, names, areas


def frame(vals, names, areas, base):
    pre = {"nation": "", "ccaa": "ccaa_", "province": "prov_", "municipality": "mun_"}
    inv = {v: k for k, v in ITEMS.items()}
    rows = []
    for a in areas:
        for v in ITEMS.values():
            x = vals[(a, v)]
            rows.append(dict(entity=f"ine_viv:{pre[a[0]]}{a[1]}", variable=v, ts_utc=TS,
                             value=round(x / 1000.0, 6) if v == "median_annual_consumption" else x,
                             unit="MWh" if v == "median_annual_consumption" else "count", freq="P1Y", geo="ES", market="",
                             node=f"{a[1]} {names[a]}: {inv[v]}", x_level=a[0], **base))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="INE: Spain's dwellings by electricity consumption, 2021 census")
    ap.add_argument("--offline", action="store_true", help="the saved file only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the file again")
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
    try:
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=180, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        vals, names, areas = parse(content)
        t = frame(vals, names, areas, base)
        if t.duplicated(["entity", "variable", "ts_utc"]).any():
            raise RuntimeError("a key given twice")
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["entity", "variable"]).reset_index(drop=True)
        lv = t.drop_duplicates("entity").x_level.value_counts().to_dict()
        nat = {v: vals[(("nation", "es"), v)] for v in ITEMS.values()}
        head = [
            "Energy Research Warehouse (ERW): INE, Censo de Poblacion y Viviendas 2021, dwellings by intensity of use from their "
            "electricity consumption (JAXI tpx 59531), for Spain, its autonomous communities, provinces and municipalities (session 2765)",
            "Shape: series (docs/datastandard.md v0). entity ine_viv:es, ine_viv:ccaa_<code>, ine_viv:prov_<code> or ine_viv:mun_<code>; "
            "variable dwellings_total, dwellings_empty, dwellings_low_consumption, dwellings_occasional_use and its two bands, the "
            "consumption bands from 751 kWh (unit count), median_annual_consumption (MWh per dwelling, INE's kWh / 1,000); ts_utc "
            "2021-01-01, the 2021 census; freq P1Y; geo ES; x_level the area's level.",
            f"{len(t)} rows, {lv.get('nation', 0)} nation, {lv.get('ccaa', 0)} communities, {lv.get('province', 0)} provinces, "
            f"{lv.get('municipality', 0)} municipalities. Spain: {nat['dwellings_total']:,.0f} dwellings, {nat['dwellings_empty']:,.0f} "
            f"empty, median annual consumption {nat['median_annual_consumption']:,.0f} kWh. Each total checked against its classes and "
            "each parent area's counts against its parts, exactly; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/ine_es_dwellings_electricity.py; the file retrieved "
            f"{base['retrieved_at']}; last modified {base['vintage']}; INE: data updated 22 November 2024",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (the table: {PAGE})",
            "License: CC BY 4.0 (INE's legal notice). Credit: Elaboracion propia con datos extraidos del sitio web del INE: www.ine.es "
            "(data updated 22 November 2024).",
        ]
        ip.write_snapshot(t, NAME, head, log, cols)
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(t)} rows"))
        print(f"{NAME}: {len(t)} rows, {t.entity.nunique()} areas")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"{NAME} FAILED, no output file written:\n{tb}")
        print(f"{NAME} FAILED, no output file written: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not args.out_dir:
        if results and results[0]["status"] == "ok":
            ip.update_sources([dict(source=SOURCE, publisher="Instituto Nacional de Estadistica (INE), Spain",
                                    report="Censo de Poblacion y Viviendas 2021: Viviendas segun su intensidad de uso",
                                    report_url=PAGE, document_list=PAGE, license="public", tables=[NAME])])  # CC BY 4.0
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
