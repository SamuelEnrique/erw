#!/usr/bin/env python3
"""Burkina Faso's electricity a year, 2023 and 2024: production by producer and type (SONABEL's thermal, hydro and solar
plants, the independent producers' plants), imports by interconnection (Cote d'Ivoire, Ghana, Togo) and their totals,
as the Autorite de Regulation du Secteur de l'Energie (ARSE) gives them in table 15, "Donnees energetiques du secteur en
2023 et 2024", of its activity report for 2024 (session 2561, chain 126; the ERW held Burkina Faso only in EIA's
international table).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/arse_burkina_electricity_annual.csv, from one
PDF (no key):

    https://www.arse.bf/wp-content/uploads/2025/08/Rapport-dactivite-2024.pdf

The table runs over two pages. Its figures (kWh) print their thousands with spaces, so "688 243 400 750 144 848" cannot
be split from the text: the pages' words are read by their place. A line's words left of x 300 make its label; those
from x 300 to 390 its 2023 cell, from x 400 to 490 its 2024 cell; the percentage change beyond is not taken. A label's
second line (no figure) is passed over.

    entity      arse:bf:<item>: sonabel_thermal, sonabel_hydro, sonabel_solar, fiess_thermal, nagreongo_solar,
                kodeni_solar, pa_solar, zano_solar, faso_biogaz, essakane_solar (not on the grid), zina_solar,
                private_thermal, private_solar, sonabel_total, national_total (production); htb_cote_divoire,
                htb_ghana, hta_ghana, hta_togo, total (imports); total (supply: produced and imported)
    variable    production, imports, supply
    unit        MWh (ARSE's kWh divided by 1,000); ts_utc the year's first day; freq P1Y; geo BF
    node        ARSE's label

A row whose cells say "Non disponible" (COOPEL's) and the percentage rows (yield, distribution losses) are not taken.
The run stops on a page not found, a mapped row missing or given twice, a cell that is not a figure, or a total that
differs from its parts by more than 1 MWh (SONABEL's three types; the national total, SONABEL's and the private
totals; the private thermal total, FIESS's and Faso Biogaz's; the imports; the supply). The private solar total is not
checked: ARSE's differs from its listed plants (2024: 227.4 GWh against 246.1). Nothing is filled.

    python warehouse/connectors/arse_burkina_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/arse_bf/ and reused unless --fresh; --offline asks nothing.
www.arse.bf's robots file closes /wp-admin/ only (session 2561). License: internal. ARSE's conditions of use: "Toute
reproduction, diffusion ou reutilisation, meme partielle, est soumise a l'autorisation prealable ecrite de l'ARSE, sauf
mention contraire ou usage strictement personnel et non commercial."; internal until a ruling.
"""

import argparse
import datetime as dt
import io
import os
import re
import sys
import traceback

import pandas as pd
import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import iso_prices as ip  # noqa: E402

NAME = "arse_burkina_electricity_annual"
CONNECTOR = "arse_bf"
SOURCE = "arse_bf:rapport_activite_2024_tableau_15"
HOST = "www.arse.bf"
URL = "https://www.arse.bf/wp-content/uploads/2025/08/Rapport-dactivite-2024.pdf"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
CITATION = ("Autorite de Regulation du Secteur de l'Energie (ARSE), Burkina Faso, Rapport d'activites 2024, tableau 15: Donnees "
            "energetiques du secteur en 2023 et 2024")
PAGE1 = "Tableau 15"
PAGE2 = "Total imports (HTB+HTA)"
# a label's start (case as printed) and (variable, item); every one must be found once
ROWS = [("SONABEL Thermique", "production", "sonabel_thermal"), ("Hydro", "production", "sonabel_hydro"),
        ("Solaire Photovolta", "production", "sonabel_solar"), ("FIESS", "production", "fiess_thermal"),
        ("Nagr", "production", "nagreongo_solar"), ("Kod", "production", "kodeni_solar"), ("Pâ ", "production", "pa_solar"),
        ("Zano", "production", "zano_solar"), ("Faso Biogaz", "production", "faso_biogaz"), ("Essakane", "production", "essakane_solar"),
        ("Zina", "production", "zina_solar"), ("Thermique priv", "production", "private_thermal"),
        ("Solaire priv", "production", "private_solar"), ("HTB C", "imports", "htb_cote_divoire"), ("HTB Ghana", "imports", "htb_ghana"),
        ("HTA Ghana", "imports", "hta_ghana"), ("HTA Togo", "imports", "hta_togo"), ("Total SONABEL", "production", "sonabel_total"),
        ("Total production nationale", "production", "national_total"), ("Total imports", "imports", "total"),
        ("Total énergie produite et import", "supply", "total")]
SKIP = ("COOPEL", "Rendement", "Pertes")
SUMS = [("production", "sonabel_total", ["sonabel_thermal", "sonabel_hydro", "sonabel_solar"]),
        ("production", "private_thermal", ["fiess_thermal", "faso_biogaz"]),
        ("production", "national_total", ["sonabel_total", "private_thermal", "private_solar"]),
        ("imports", "total", ["htb_cote_divoire", "htb_ghana", "hta_ghana", "hta_togo"])]
ZONES = {"2023": (300, 390), "2024": (400, 490)}
X_COLS = ["x_label"]


def lines_of(words, tol=3):
    out = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if out and abs(w["top"] - out[-1][0]) <= tol:
            out[-1][1].append(w)
        else:
            out.append([w["top"], [w]])
    return [sorted(ws, key=lambda w: w["x0"]) for _, ws in out]


def kwh(cell):
    s = " ".join(cell)
    if not re.fullmatch(r"\d{1,3}(?: \d{3})*", s):
        raise RuntimeError(f"not a figure: {s!r}")
    return float(s.replace(" ", ""))


def parse_words(pages_words, base):
    rows, got, vals = [], {}, {}
    for words in pages_words:
        for ln in lines_of(words):
            label = " ".join(w["text"] for w in ln if w["x1"] < 300)
            if label.startswith("Source"):
                break  # the table's end; the page's text and chart follow
            cells = {y: [w["text"] for w in ln if lo <= w["x0"] < hi] for y, (lo, hi) in ZONES.items()}
            if not any(cells.values()) or label.startswith(SKIP):
                continue
            hit = [r for r in ROWS if label.startswith(r[0])]
            if not hit:
                if any(re.fullmatch(r"\d{1,3}", t) for c in cells.values() for t in c) and label and not label.startswith(("Source", "Production nationale")):
                    raise RuntimeError(f"a row not in the map: {label!r}")
                continue
            if len(hit) > 1:
                raise RuntimeError(f"{label!r} matches {len(hit)} rows of the map")
            start, var, item = hit[0]
            if start in got:
                raise RuntimeError(f"{label!r} given twice")
            got[start] = label
            for y, cell in cells.items():
                if not cell or cell == ["-"]:
                    continue
                v = kwh(cell)
                vals[(var, item, y)] = v
                rows.append(dict(entity=f"arse:bf:{item}", variable=var, ts_utc=f"{y}-01-01T00:00:00Z", value=round(v / 1000, 3), unit="MWh",
                                 freq="P1Y", geo="BF", market="", node=label, **base, x_label=label))
    missing = [r[0] for r in ROWS if r[0] not in got]
    if missing:
        raise RuntimeError(f"rows missing: {missing}")
    for y in ZONES:
        for var, tot, parts in SUMS:
            s = sum(vals.get((var, p, y), 0.0) for p in parts)
            if abs(s - vals[(var, tot, y)]) > 1000:
                raise RuntimeError(f"{y} {var} {tot}: {vals[(var, tot, y)]} is not the sum of its parts {s}")
        s = vals[("production", "national_total", y)] + vals[("imports", "total", y)]
        if abs(s - vals[("supply", "total", y)]) > 1000:
            raise RuntimeError(f"{y}: the supply is not production and imports")
    return pd.DataFrame(rows)


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        texts = [(i, pg.extract_text() or "") for i, pg in enumerate(pdf.pages)]
        first = [i for i, t in texts if PAGE1 + ":" in t and "Energie produite" in t]
        second = [i for i, t in texts if PAGE2 in t]
        if len(first) != 1 or len(second) != 1 or second[0] not in (first[0], first[0] + 1):
            raise RuntimeError(f"the table's pages not found (first {first}, second {second})")
        pages = sorted({first[0], second[0]})
        return parse_words([pdf.pages[i].extract_words() for i in pages], base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ARSE: Burkina Faso's production and imports of electricity, 2023 and 2024")
    ap.add_argument("--offline", action="store_true", help="the saved report only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the report again")
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
        content, rec = ip.fetch_raw(CONNECTOR, URL, log, offline=args.offline, fresh=args.fresh, headers=UA, timeout=300, pause=1)
        base = dict(source=SOURCE, source_url=URL, retrieved_at=rec.get("retrieved_at") or "", vintage=ip.vintage_of(rec))
        t = parse(content, base)
        cols = ip.SERIES_COLS + X_COLS
        t = t[cols].sort_values(["variable", "entity", "ts_utc"]).reset_index(drop=True)
        v = {(x, e.split(":")[-1], ts[:4]): val for x, e, ts, val in zip(t.variable, t.entity, t.ts_utc, t.value)}
        head = [
            "Energy Research Warehouse (ERW): Autorite de Regulation du Secteur de l'Energie (ARSE), Burkina Faso, Rapport d'activites 2024, "
            "table 15: production by producer and type, imports by interconnection, 2023 and 2024 (session 2561)",
            "Shape: series (docs/datastandard.md v0). entity arse:bf:<item>; variable production, imports, supply; unit MWh (ARSE's kWh "
            "divided by 1,000); ts_utc the year's first day; freq P1Y; geo BF; node ARSE's label.",
            f"{len(t)} rows; in 2024 national production {v[('production', 'national_total', '2024')] / 1e6:.3f} TWh, imports "
            f"{v[('imports', 'total', '2024')] / 1e6:.3f} TWh, supply {v[('supply', 'total', '2024')] / 1e6:.3f} TWh. COOPEL's rows (not "
            "available) and the percentages are not taken; ARSE's private solar total differs from its listed plants and is kept as given; "
            "nothing is filled.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/arse_burkina_electricity.py; the report retrieved {base['retrieved_at']}; last "
            f"modified {base['vintage']}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL}",
            "License: internal. ARSE's conditions of use make any reproduction, dissemination or reuse subject to its prior written "
            f"permission, except strictly personal and non-commercial use; internal until a ruling. Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Autorite de Regulation du Secteur de l'Energie (ARSE), Burkina Faso",
                                    report="Rapport d'activites 2024, tableau 15: donnees energetiques du secteur en 2023 et 2024", report_url=URL,
                                    document_list="https://www.arse.bf/documentation/rapport-dactivite/", license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
