#!/usr/bin/env python3
"""The French island grids' electricity a year by source, 2018 to 2024: the net production EDF's island systems arm (EDF
Systemes Energetiques Insulaires, EDF SEI) records on each grid it runs (Corsica, Reunion, Guadeloupe, Martinique, French
Guiana, Saint-Pierre-et-Miquelon, Saint-Barthelemy and the other small islands), as EDF publishes it in the dataset
"Production annuelle d'electricite par filiere d'EDF SA en Corse & Outremer" of its open data portal (session 2656, chain
132, the session's third own choice; the ERW held none of these grids in a table).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/edf_sei_islands_electricity_annual.csv, from
the portal's data-fair API (no key), one GET of the dataset's lines:

    https://opendata.edf.fr/data-fair/api/v1/datasets/production-annuelle-delectricite-par-filiere/lines?size=1000

    entity      edf_sei:<territory>:<source>: bioenergy, coal, wind, geothermal, hydro, diesel, solar, oil_turbines
                (variable generation), links (net_imports, Corsica's links with Sardinia and Italy) and total (supply)
    unit        MWh (as published, rounded to the MWh); ts_utc the year's first day; freq P1Y; geo the territory's code
    node        the territory as EDF names it

A cell without a number has no row; the per cent columns are not taken; nothing is filled. EDF's notes: the figures are the
net energy injected into each territory's grid; the total adds every source and the storage balance; household waste
incineration counts at half in the renewable share (not taken); sources with fewer than ten installations under 36 kVA in a
territory are not published (hydro in Martinique, solar in Saint-Barthelemy); in the file of 2026 each year's published
sources add to its total within 0.02 per cent. A column or territory not in the map, a year not of four digits, a count of
lines not the dataset's total, a key given twice, a negative production, or a year whose sources miss its total by more than
1 per cent stops the run.

    python warehouse/connectors/edf_sei_islands_electricity.py [--offline] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/edf_sei/ (lines.json, the answer with its time of retrieval) and read
from there with --offline. opendata.edf.fr's robots file allows every path (its content signal: search yes, ai-train no,
ai-input yes; session 2656); the old portal, opendata-corse-outremer.edf.fr, sends every request to it. License: the Licence
Ouverte (Etalab), as the dataset's record on the portal and on data.gouv.fr states: public.
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

NAME = "edf_sei_islands_electricity_annual"
CONNECTOR = "edf_sei"
SOURCE = "edf_sei:production-annuelle-delectricite-par-filiere"
HOST = "opendata.edf.fr"
DATASET = "https://opendata.edf.fr/data-fair/api/v1/datasets/production-annuelle-delectricite-par-filiere"
URL = DATASET + "/lines?size=1000"
PAGE = "https://opendata.edf.fr/datasets/production-annuelle-delectricite-par-filiere"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
# the dataset's source columns: (ERW item, variable)
SOURCES = {"bioenergie": ("bioenergy", "generation"), "charbon": ("coal", "generation"), "eolien": ("wind", "generation"),
           "geothermie": ("geothermal", "generation"), "hydraulique": ("hydro", "generation"),
           "liaisons": ("links", "net_imports"), "moteurs_diesel": ("diesel", "generation"),
           "solaire_photovoltaique": ("solar", "generation"), "turbines_a_combustion_fioul": ("oil_turbines", "generation"),
           "total": ("total", "supply")}
NOT_TAKEN = {"tauxnonenr", "part_enr", "territoire_open_data", "annee_prod", "_id", "_i", "_rand", "_score"}
# the territory as EDF names it: (ERW key, geo); the Iles du Ponant, small islands off Brittany and Normandy, take France's code
TERRITORIES = {"Corse": ("corsica", "FR-20R"), "R" + chr(0xE9) + "union": ("reunion", "RE"), "Guadeloupe": ("guadeloupe", "GP"),
               "Martinique": ("martinique", "MQ"), "Guyane": ("french_guiana", "GF"),
               "St Pierre et Miquelon": ("saint_pierre_miquelon", "PM"), "St Barth" + chr(0xE9) + "lemy": ("saint_barthelemy", "BL"),
               "St Martin": ("saint_martin", "MF"), "Iles du Ponant": ("iles_du_ponant", "FR")}
X_COLS = []


def parse(js, base):
    lines = js.get("results")
    if not isinstance(lines, list) or js.get("total") != len(lines):
        raise RuntimeError(f"{len(lines or [])} lines for a dataset of {js.get('total')}")
    rows, mwh = [], {}
    for ln in lines:
        extra = sorted(set(ln) - set(SOURCES) - NOT_TAKEN)
        if extra:
            raise RuntimeError(f"a column not in the map: {extra}")
        name = ln["territoire_open_data"]
        if name not in TERRITORIES:
            raise RuntimeError(f"a territory not in the map: {name!r}")
        key, geo = TERRITORIES[name]
        y = str(ln["annee_prod"])
        if not re.fullmatch(r"\d{4}", y):
            raise RuntimeError(f"a year not of four digits: {y!r}")
        for col, (item, variable) in SOURCES.items():
            v = ln.get(col)
            if v is None or v == "":
                continue
            v = float(v)
            if v < 0 and variable == "generation":
                raise RuntimeError(f"{name} {y} {col}: a negative production {v}")
            mwh[(key, y, item)] = v
            rows.append(dict(entity=f"edf_sei:{key}:{item}", variable=variable, ts_utc=f"{y}-01-01T00:00:00Z", value=v,
                             unit="MWh", freq="P1Y", geo=geo, market="", node=name, **base))
    for key, y in sorted({(k, y) for k, y, _ in mwh}):
        if (key, y, "total") not in mwh:
            continue
        s = sum(v for (k, yy, it), v in mwh.items() if k == key and yy == y and it != "total")
        tot = mwh[(key, y, "total")]
        if abs(s - tot) > tot * 0.01 + 1:
            raise RuntimeError(f"{key} {y}: the sources make {s:.0f} MWh, the total {tot:.0f}")
    return rows


def get(offline, log):
    path = os.path.join(ip.RAW_DIR, CONNECTOR, "lines.json")
    if offline:
        if not os.path.exists(path):
            raise RuntimeError(f"offline: no saved answer at {path}")
        saved = json.load(open(path, encoding="utf-8"))
        log(f"  saved answer reused: {path} (retrieved {saved['retrieved_at']})")
        return saved["answer"], saved["retrieved_at"]
    r = requests.get(URL, headers=UA, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} for the dataset's lines")
    if not r.url.startswith("https://" + HOST + "/"):
        raise RuntimeError(f"sent to another host: {r.url}")
    at = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    js = json.loads(r.content.decode("utf-8-sig"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump({"retrieved_at": at, "url": URL, "answer": js}, open(path, "w", encoding="utf-8"))
    log(f"  GET {URL}: {len(r.content)} bytes, saved as {path}")
    return js, at


def main(argv=None):
    ap = argparse.ArgumentParser(description="EDF SEI: the French island grids' electricity by source a year")
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
        tot = t[t.entity.str.endswith(":total")]
        last = tot.ts_utc.max()
        head = [
            "Energy Research Warehouse (ERW): EDF Systemes Energetiques Insulaires (EDF SEI), the French island grids' net "
            f"electricity production by source, {t.ts_utc.min()[:4]} to {last[:4]} (session 2656)",
            "Shape: series (docs/datastandard.md v0). entity edf_sei:<territory>:<source>; variable generation, net_imports "
            "(Corsica's links) or supply (the total); unit MWh; ts_utc the year's first day; freq P1Y; geo the territory's "
            "code; node the territory as EDF names it.",
            f"{len(t)} rows, {tot.geo.nunique()} territories; the {last[:4]} totals, GWh: "
            + ", ".join(f"{n} {v / 1e3:.1f}" for n, v in zip(tot[tot.ts_utc == last].node, tot[tot.ts_utc == last].value))
            + ". Net energy injected into each grid; each year's sources checked against its total; sources of fewer than ten "
            "small installations are not published; nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/edf_sei_islands_electricity.py; the answer retrieved {at}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/lines.json (not in git)",
            f"Source: {SOURCE} EDF SA, Production annuelle d'electricite par filiere d'EDF SA en Corse & Outremer",
            f"  access: {URL} (the dataset's page: {PAGE})",
            "License: Licence Ouverte (Etalab), as the dataset's record states; credit: EDF SA (EDF Systemes Energetiques "
            "Insulaires).",
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
            ip.update_sources([dict(source=SOURCE, publisher="EDF SA (EDF Systemes Energetiques Insulaires)",
                                    report="Production annuelle d'electricite par filiere d'EDF SA en Corse & Outremer "
                                           "(annual net electricity production by source, the island grids)",
                                    report_url=PAGE, document_list="https://opendata.edf.fr/data-fair/api/v1/datasets",
                                    license="public", tables=[NAME])])  # Licence Ouverte (Etalab)
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
