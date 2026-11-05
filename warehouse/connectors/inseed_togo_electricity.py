#!/usr/bin/env python3
"""Togo's electricity a year, 2020 to 2024: CEET's purchases by supplier, the production of each producer on its grid,
and CEET's sales by voltage, as the Institut National de la Statistique et des Etudes Economiques et Demographiques
(INSEED) gives them in chapter 25 of its Annuaire Statistique National 2024, tables 25.2 ("Achat et production
d'energie") and 25.7 ("Ventes d'electricite"), both from CEET's annual activity reports (session 2535, chain 124; the ERW
held Togo only in EIA's and OWID's international tables).

Energy Research Warehouse (ERW) connector. One series table, warehouse/output/inseed_togo_electricity_annual.csv, from one
PDF (no key):

    https://inseed.tg/download/7668/

Each table is read from its page's words by their place: the year headings (2020 to 2024) give the columns; the words
of a figure, no more than 6 points apart, make one cell, and a cell belongs to the year whose heading's right edge is
nearest its own (the figures are right-aligned); the words left of the first year make the row's label. Reading by place splits cells such as "907,98 1 351 983,53", which the page's text
alone cannot.

    entity      inseed:tg:<item>: a supplier (vra_tcn_sbee_nangbeto, sbee_crossborder, ecg_crossborder, snpt) or total
                (purchases); a producer (ceet, contourglobal, kep, amea) (production); low_voltage, medium_voltage or
                total (sales)
    variable    purchases, gross_production (CEET, ContourGlobal Togo), net_production (KEP), production (AMEA), sales
    unit        MWh (INSEED's GWh times 1,000); ts_utc the year's first day; freq P1Y; geo TG
    node        INSEED's label

A cell of "-" is not written. The run stops on a table not found, a row label not in the map, a row missing, a figure
of another form, a year heading missing, or a total that differs from the sum of its parts by more than 0.2 GWh (table
25.2, whose 2023 purchase from VRA-TCN-SBEE-Nangbeto is printed as "1 351") or 1 GWh (table 25.7, in whole GWh). Nothing
is filled. Table 25.1's key figures are not taken: its purchases (2022 1,720 and 2023 1,975 GWh) and its energy sold
(2023 1,705 GWh) differ from tables 25.2 and 25.7 of the same chapter (916.26, 1,360.05 and 1,500 GWh).

    python warehouse/connectors/inseed_togo_electricity.py [--offline] [--fresh] [--out-dir DIR]

Ceiling: one request a run, saved in warehouse/raw/inseed_tg/ and reused unless --fresh; --offline asks nothing.
inseed.tg's robots file closes /wp-admin/ only (session 2535). License: internal. INSEED's site states "Copyright 2024
INSEED - Tous droits reserves" and links no terms of reuse; internal until a ruling.
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

NAME = "inseed_togo_electricity_annual"
CONNECTOR = "inseed_tg"
SOURCE = "inseed_tg:annuaire_2024_ch25"
HOST = "inseed.tg"
URL = "https://inseed.tg/download/7668/"
PAGE = "https://inseed.tg/"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)"}
YEARS = ["2020", "2021", "2022", "2023", "2024"]
CITATION = ("Institut National de la Statistique et des Etudes Economiques et Demographiques (INSEED), Togo, Annuaire Statistique "
            "National 2024, chapter 25, tables 25.2 (Achat et production d'energie) and 25.7 (Ventes d'electricite), from CEET's "
            "annual activity reports")
# table: {label: (variable, item)}; every label must be found
T252 = {"ACHATS VRA-TCN- SBEE-NANGBETO": ("purchases", "vra_tcn_sbee_nangbeto"),
        "SBEE Bénin (Transfrontalier)": ("purchases", "sbee_crossborder"),
        "ECG Ghana (Transfrontalier)": ("purchases", "ecg_crossborder"),
        "SNPT Togo": ("purchases", "snpt"),
        "TOTAL Achats (GWh)": ("purchases", "total"),
        "Production Brute CEET (GWh)": ("gross_production", "ceet"),
        "Production Brute CGT(GWh)": ("gross_production", "contourglobal"),
        "Production Nette KEP(GWh)": ("net_production", "kep"),
        "Production AMEA(GWh)": ("production", "amea")}
T257 = {"Ventes d’électricité BT": ("sales", "low_voltage"),
        "Ventes d’électricité MT": ("sales", "medium_voltage"),
        "TOTAL": ("sales", "total")}
TABLES = [("25.2", T252), ("25.7", T257)]
SUMS = [("purchases", ["vra_tcn_sbee_nangbeto", "sbee_crossborder", "ecg_crossborder", "snpt"], 200),
        ("sales", ["low_voltage", "medium_voltage"], 1000)]
X_COLS = ["x_label"]
GAP = 6  # points between two words of one figure ("1 351"); the gap between two cells is wider


def lines_of(words, tol=4):
    """Words grouped into lines by their top, each line's words left to right."""
    out = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if out and abs(w["top"] - out[-1][0]) <= tol:
            out[-1][1].append(w)
        else:
            out.append([w["top"], [w]])
    return [sorted(ws, key=lambda w: w["x0"]) for _, ws in out]


def gwh(cell):
    if cell == "-":
        return None
    if not re.fullmatch(r"\d{1,3}(?: \d{3})*(?:,\d+)?", cell):
        raise RuntimeError(f"not a figure: {cell!r}")
    return float(cell.replace(" ", "").replace(",", "."))


def read_table(words, no, labels):
    """{(variable, item, year): GWh} and {(variable, item): label} of one table, from its page's words."""
    ws = sorted(words, key=lambda w: (w["top"], w["x0"]))
    starts = [i for i, w in enumerate(ws[:-1]) if w["text"] == "Tableau" and ws[i + 1]["text"] == no]
    if len(starts) != 1:
        raise RuntimeError(f"table {no} found {len(starts)} times on its page")
    y0 = ws[starts[0]]["top"]
    after = [w["top"] for w in ws if w["text"] == "Tableau" and w["top"] > y0 + 2]
    y1 = min(after) if after else 1e9
    lines = lines_of([w for w in ws if y0 + 2 < w["top"] < y1])
    head = next((ln for ln in lines if [w["text"] for w in ln if w["text"] in YEARS] == YEARS), None)
    if head is None:
        raise RuntimeError(f"table {no}: the year headings {YEARS} not found")
    xs = {w["text"]: w["x1"] for w in head if w["text"] in YEARS}
    left = min(w["x0"] for w in head if w["text"] in YEARS) - 10
    out, names, seen = {}, {}, set()
    for ln in lines[lines.index(head) + 1:]:
        label = " ".join(w["text"] for w in ln if w["x1"] < left)
        if label.startswith("Source"):
            break
        # the figures' words joined into cells (a gap of GAP points or less inside one figure), each cell placed by its right edge
        groups = []
        for w in (w for w in ln if w["x1"] >= left):
            if groups and w["x0"] - groups[-1][-1]["x1"] <= GAP:
                groups[-1].append(w)
            else:
                groups.append([w])
        cells = {y: [] for y in YEARS}
        for g in groups:
            y = min(YEARS, key=lambda y: abs(xs[y] - g[-1]["x1"]))
            if cells[y]:
                raise RuntimeError(f"table {no}: {label!r} has two cells under {y}")
            cells[y] = [w["text"] for w in g]
        if label not in labels:
            raise RuntimeError(f"table {no}: a row not in the map: {label!r} {cells}")
        if label in seen:
            raise RuntimeError(f"table {no}: {label!r} given twice")
        seen.add(label)
        var, item = labels[label]
        names[(var, item)] = label
        for y in YEARS:
            if not cells[y]:
                raise RuntimeError(f"table {no}: {label!r} has no cell for {y}")
            v = gwh(" ".join(cells[y]))
            if v is not None:
                out[(var, item, y)] = v
    if seen != set(labels):
        raise RuntimeError(f"table {no}: rows missing: {sorted(set(labels) - seen)}")
    return out, names


def parse_pages(pages, base):
    """pages: [(text, words)] of the yearbook."""
    vals, names = {}, {}
    for no, labels in TABLES:
        title = f"Tableau {no} :"
        hits = [ws for text, ws in pages if title in text and "Source" in text and "RUBRIQUES" in text and "......" not in text]
        if len(hits) != 1:
            raise RuntimeError(f"the page of table {no} found {len(hits)} times")
        v, n = read_table(hits[0], no, labels)
        vals.update(v)
        names.update(n)
    for var, parts, tol in SUMS:
        for y in YEARS:
            if (var, "total", y) not in vals:
                continue
            s = sum(vals.get((var, p, y), 0.0) for p in parts)
            if abs(s - vals[(var, "total", y)]) * 1000 > tol:
                raise RuntimeError(f"{var} {y}: the total {vals[(var, 'total', y)]} is not the sum of its parts {s}")
    rows = [dict(entity=f"inseed:tg:{item}", variable=var, ts_utc=f"{y}-01-01T00:00:00Z", value=round(v * 1000, 3), unit="MWh",
                 freq="P1Y", geo="TG", market="", node=names[(var, item)], **base, x_label=names[(var, item)])
            for (var, item, y), v in vals.items()]
    return pd.DataFrame(rows)


def parse(content, base):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages = []
        for pg in pdf.pages:
            text = pg.extract_text() or ""
            if "Tableau 25." in text:
                pages.append((text, pg.extract_words()))
    return parse_pages(pages, base)


def main(argv=None):
    ap = argparse.ArgumentParser(description="INSEED Togo: CEET's purchases, production and sales a year")
    ap.add_argument("--offline", action="store_true", help="the saved yearbook only, no request")
    ap.add_argument("--fresh", action="store_true", help="ask for the yearbook again")
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
        v = {(x, e.split(":")[-1], y[:4]): val for x, e, y, val in zip(t.variable, t.entity, t.ts_utc, t.value)}
        head = [
            "Energy Research Warehouse (ERW): Institut National de la Statistique et des Etudes Economiques et Demographiques (INSEED), Togo, "
            "Annuaire Statistique National 2024, tables 25.2 and 25.7: CEET's purchases by supplier, production by producer and sales by "
            "voltage, 2020 to 2024 (session 2535)",
            "Shape: series (docs/datastandard.md v0). entity inseed:tg:<item>; variable purchases (by supplier), gross_production (CEET, "
            "ContourGlobal Togo), net_production (KEP), production (AMEA), sales (by voltage); unit MWh (INSEED's GWh times 1,000); ts_utc "
            "the year's first day; freq P1Y; geo TG; node INSEED's label.",
            f"{len(t)} rows; purchases {v[('purchases', 'total', '2024')] / 1e6:.3f} TWh in 2024; ContourGlobal Togo's gross production "
            f"{v[('gross_production', 'contourglobal', '2024')] / 1e6:.3f} TWh in 2024; sales {v[('sales', 'total', '2023')] / 1e6:.3f} TWh in "
            "2023 (none given for 2024). A cell of - is not written; nothing is filled. Table 25.1's key figures, which differ from these, "
            "are not taken.",
            f"Retrieved: {run_id} (UTC) by warehouse/connectors/inseed_togo_electricity.py; the yearbook retrieved {base['retrieved_at']}; "
            f"last modified {base['vintage'] or 'not stated'}",
            f"Run log: warehouse/output/logs/{CONNECTOR}_{run_id}.log",
            f"Raw files: warehouse/raw/{CONNECTOR}/ (not in git)",
            f"Source: {SOURCE} {CITATION}",
            f"  access: {URL} (listed on {PAGE})",
            "License: internal. INSEED's site states \"Copyright 2024 INSEED - Tous droits reserves\" and links no terms of reuse; internal "
            f"until a ruling. Cite: {CITATION}.",
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
            ip.update_sources([dict(source=SOURCE, publisher="Institut National de la Statistique et des Etudes Economiques et Demographiques (INSEED), Togo",
                                    report="Annuaire Statistique National 2024, chapter 25, tables 25.2 and 25.7", report_url=URL,
                                    document_list=PAGE, license="internal", tables=[NAME])])
        ip.write_status(CONNECTOR, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
